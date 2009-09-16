#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

""" Solves DC power flow.

    References:
        Ray Zimmerman, "dcpf.m", MATPOWER, PSERC Cornell, version 3.2,
        http://www.pserc.cornell.edu/matpower/, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging

from math import pi
from cvxopt import matrix, spmatrix, sparse, umfpack, cholmod

from pylon.y import SusceptanceMatrix

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "DCPF" class:
#------------------------------------------------------------------------------

class DCPF(object):
    """ Solves DC power flow.

        References:
            Ray Zimmerman, "dcpf.m", MATPOWER, PSERC Cornell, version 3.2,
            http://www.pserc.cornell.edu/matpower/, June 2007
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, library="UMFPACK"):
        """ Initialises a DCPF instance.
        """
        # CVXOPT offers interfaces to two routines for solving sets of sparse
        # linear equations.  Possible values are 'UMFPACK' and 'CHOLMOD'.
        self.library = library
        # The case on which the routine is performed
        self.case = None
        # Branch susceptance matrix
        self.B = None
        # Branch source bus susceptance matrix
        self.B_source = None
        # Vector of voltage angle guesses
        self.v_angle_guess = None
        # Vector of voltage phase angles
        self.v_angle = None


    def __call__(self, case):
        """ Calls the routine with the given case.
        """
        self.solve(case)


    def solve(self, case):
        """ Solves DC power flow for the case.
        """
        self.case = case

        logger.info("Performing DC power flow [%s]." % case.name)

        t0 = time.time()

        if not self.case.slack_model == "single":
            logger.error("DC power flow requires a single slack bus")
            return False

        susceptance = SusceptanceMatrix()
        self.B, self.B_source = susceptance(case)
        self._make_v_angle_guess_vector()

        # Calculate the voltage phase angles.
        self._make_v_angle_vector()

        self._update_model()

        t_elapsed = time.time() - t0
        logger.info("DC power flow completed in %.3fs." % t_elapsed)

        return True

    #--------------------------------------------------------------------------
    #  Build voltage phase angle guess vector:
    #--------------------------------------------------------------------------

    def _make_v_angle_guess_vector(self):
        """ Make the vector of voltage phase guesses """

        if self.case is not None:
            buses = self.case.connected_buses
            guesses = [v.v_angle_guess for v in buses]
            self.v_angle_guess = matrix(guesses)
            logger.debug("Vector of voltage phase guesses:\n%s" % guesses)

    #--------------------------------------------------------------------------
    #  Calculate voltage angles:
    #--------------------------------------------------------------------------

    def _make_v_angle_vector(self):
        """ Caluclates the voltage phase angles.
        """
        buses = self.case.connected_buses

        # Remove the column and row from the susceptance matrix that
        # correspond to the slack bus
        slack_idxs = [buses.index(v) for v in buses if v.slack]
        slack_idx = slack_idxs[0]

        pv_idxs = [buses.index(v) for v in buses if v.mode == "pv"]
        pq_idxs = [buses.index(v) for v in buses if v.mode == "pq"]
        pvpq_idxs = pv_idxs + pq_idxs

        B_pvpq = self.B[pvpq_idxs, pvpq_idxs]
        logger.debug("Susceptance matrix with the row and column "
            "corresponding to the slack bus removed:\n%s" % B_pvpq)

        B_slack = self.B[pvpq_idxs, slack_idx]
        logger.debug("Susceptance matrix column corresponding to the slack "
            "bus:\n%s" % B_slack)

        # Bus active power injections (generation - load)
        # FIXME: Adjust for phase shifters and real shunts
        p = matrix([v.p_surplus for v in buses])
        p_slack = p[slack_idx]
        p_pvpq = p[pvpq_idxs]
        logger.debug("Active power injections:\n%s" % p_pvpq)

        v_angle_slack = self.v_angle_guess[slack_idx]
        logger.debug("Slack bus voltage angle:\n%s" % v_angle_slack)

        # Solves the sparse set of linear equations Ax=b where A is a
        # sparse matrix and B is a dense matrix of the same type ('d'
        # or 'z') as A. On exit B contains the solution.
        A = B_pvpq
        b = p_pvpq - p_slack * v_angle_slack

        if self.library == "UMFPACK":
            umfpack.linsolve(A, b)
        elif self.library == "CHOLMOD":
            cholmod.splinsolve(A, b)
        else:
            raise ValueError, "'library' must be either 'UMFPACK' of 'CHOLMOD'"

        logger.debug("Solution to linear equations:\n%s" % b)

#        v_angle = matrix([b[:slack_idx], [v_angle_slack], b[slack_idx:]])
        import numpy # FIXME: remove numpy dependency
        # Insert the reference voltage angle of the slack bus
        v_angle = matrix(numpy.insert(b, slack_idx, v_angle_slack))
        logger.debug("Bus voltage phase angles:\n%s" % v_angle)

        self.v_angle = v_angle

        return v_angle

    #--------------------------------------------------------------------------
    #  Update model with solution:
    #--------------------------------------------------------------------------

    def _update_model(self):
        """ Updates the network model with values computed from the voltage
            phase angle solution.
        """
        base_mva = self.case.base_mva
        buses    = self.case.connected_buses
        branches = self.case.online_branches

        p_source = self.B_source * self.v_angle * base_mva
        p_target = -p_source

        for i in range(len(branches)):
            branches[i].p_source = p_source[i]
            branches[i].p_target = p_target[i]
            branches[i].q_source = 0.0
            branches[i].q_target = 0.0

        for i in range(len(buses)):
            v_angle = self.v_angle[i]
            buses[i].v_angle = v_angle*(180/pi)
            buses[i].v_magnitude = 1.0

# EOF -------------------------------------------------------------------------
