#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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
import math

from cvxopt import matrix, umfpack, cholmod

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
        # linear equations: 'UMFPACK' and 'CHOLMOD'.(default: 'UMFPACK')
        self.library = library

        # The case on which the routine is performed.
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
        return self.solve(case)


    def solve(self, case):
        """ Solves DC power flow for the case.
        """
        self.case = case

        logger.info("Performing DC power flow [%s]." % case.name)

        t0 = time.time()

        if not [bus for bus in self.case.buses if bus.type == "ref"]:
            logger.error("DC power flow requires a single slack bus")
            return False

        self.B, self.B_source = case.B
        self._make_v_angle_guess_vector(case)

        # Calculate the voltage phase angles.
        self._make_v_angle_vector()

        self._update_model()

        t_elapsed = time.time() - t0
        logger.info("DC power flow completed in %.3fs." % t_elapsed)

        return True

    #--------------------------------------------------------------------------
    #  Build voltage phase angle guess vector:
    #--------------------------------------------------------------------------

    def _make_v_angle_guess_vector(self, case):
        """ Make the vector of voltage phase guesses.
        """
        buses = case.connected_buses
        self.v_angle_guess = matrix([bus.v_angle_guess for bus in buses])

        logger.debug("Voltage phase guesses:\n%s" % self.v_angle_guess)

        return self.v_angle_guess

    #--------------------------------------------------------------------------
    #  Calculate voltage angles:
    #--------------------------------------------------------------------------

    def _make_v_angle_vector(self):
        """ Calculates the voltage phase angles.
        """
        buses = self.case.connected_buses

        # Remove the column and row from the susceptance matrix that
        # corresponds to the slack bus.
        self.refidx = [buses.index(v) for v in buses if v.type == "ref"][0]

        pv_idxs = matrix([buses.index(v) for v in buses if v.type == "PV"])
        pq_idxs = matrix([buses.index(v) for v in buses if v.type == "PQ"])
        pvpq_idxs = matrix([pv_idxs, pq_idxs])

        Bpvpq = self.B[pvpq_idxs, pvpq_idxs]

        logger.debug("Susceptance matrix with the row and column "
            "corresponding to the slack bus removed:\n%s" % Bpvpq)

        Bref = self.B[pvpq_idxs, self.refidx]

        logger.debug("Susceptance matrix column corresponding to the slack "
            "bus:\n%s" % Bref)

        # Bus active power injections (generation - load)
        # FIXME: Adjust for phase shifters and real shunts.
        # Pbus = real(makeSbus(baseMVA, bus, gen)) - Pbusinj - bus(:, GS) / baseMVA;
        p = matrix([self.case.p_surplus(v) / self.case.base_mva for v in buses])
        self.p_ref = p[self.refidx]
        p_pvpq = p[pvpq_idxs]

        logger.debug("Active power injections:\n%s" % p_pvpq)

        v_angle_ref = self.v_angle_guess[self.refidx]

        logger.debug("Slack bus voltage angle:\n%s" % v_angle_ref)

        # Solves the sparse set of linear equations Ax=b where A is a
        # sparse matrix and B is a dense matrix of the same type ('d'
        # or 'z') as A. On exit b contains the solution.
        A = Bpvpq
        b = p_pvpq - self.p_ref * v_angle_ref

        if self.library == "UMFPACK":
            umfpack.linsolve(A, b)
        elif self.library == "CHOLMOD":
            cholmod.splinsolve(A, b)
        else:
            raise ValueError

        logger.debug("Solution to linear equations:\n%s" % b)

        # Insert the reference voltage angle of the slack bus
        v_angle = matrix([b[:self.refidx], v_angle_ref, b[self.refidx:]])

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

        p_source = (self.B_source * self.v_angle) * base_mva
        p_target = -p_source

        for i in range(len(branches)):
            branches[i].p_source = p_source[i]
            branches[i].p_target = p_target[i]
            branches[i].q_source = 0.0
            branches[i].q_target = 0.0

        for i in range(len(buses)):
            buses[i].v_angle = self.v_angle[i] * (180 / math.pi)
            buses[i].v_magnitude = 1.0

        # Update Pg for swing generator.
        refbus = buses[self.refidx]
        refgen = [gen for gen in self.case.generators if gen.bus == refbus][0]
        refgen.p += (self.B[self.refidx] * self.v_angle - self.p_ref) * base_mva

# EOF -------------------------------------------------------------------------
