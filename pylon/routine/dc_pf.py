#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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
    D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
    MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from os.path import join, dirname
from math import pi

from cvxopt.base import matrix, spmatrix, sparse
from cvxopt.umfpack import linsolve

from pylon.routine.y import make_susceptance
from pylon.network import Network
#from pylon.pypylon import Network

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "DCPFRoutine" class:
#------------------------------------------------------------------------------

class DCPFRoutine:
    """ Solves DC power flow.

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    # The network on which the routine is performed
    network = Network

    # Branch susceptance matrix
    B = spmatrix([], [], [])

    # Branch source bus susceptance matrix
    B_source = spmatrix([], [], [])

    # Vector of voltage angle guesses
    v_phase_guess = matrix

    # Vector of voltage phase angles
    v_phase = matrix

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network):
        """ Returns a DCPFRoutine instance """

        self.network = network
        self.solve()

    #--------------------------------------------------------------------------
    #  Solve power flow:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves DC power flow for the current network """

        # FIXME: Should this be here? Validation
        if self.network is None:
            logger.error("Network unspecified")
        elif not self.network.slack_model == "Single":
            logger.error("DC power flow requires a single slack bus")
        else:
            self.B, self.B_source = make_susceptance(self.network)
            self._make_v_phase_guess_vector()
            self._make_v_phase_vector()
            self._update_model()

    #--------------------------------------------------------------------------
    #  Build voltage phase angle guess vector:
    #--------------------------------------------------------------------------

    def _make_v_phase_guess_vector(self):
        """ Make the vector of voltage phase guesses """

        if self.network is not None:
            buses = self.network.non_islanded_buses
            guesses = [v.v_phase_guess for v in buses]
            self.v_phase_guess = matrix(guesses)
            logger.debug("Vector of voltage phase guesses:\n%s" % guesses)

    #--------------------------------------------------------------------------
    #  Calculate voltage angles:
    #--------------------------------------------------------------------------

    def _make_v_phase_vector(self):
        """ Caluclates the voltage phase angles """

        buses = self.network.non_islanded_buses

        # Remove the column and row from the susceptance matrix that
        # correspond to the slack bus
        slack_idxs = [buses.index(v) for v in buses if v.slack]
        slack_idx = slack_idxs[0]

        pv_idxs = [buses.index(v) for v in buses if v.mode == "PV"]
        pq_idxs = [buses.index(v) for v in buses if v.mode == "PQ"]
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

        v_phase_slack = self.v_phase_guess[slack_idx]
        logger.debug("Slack bus voltage angle:\n%s" % v_phase_slack)

        # Solves the sparse set of linear equations Ax=b where A is a
        # sparse matrix and B is a dense matrix of the same type ('d'
        # or 'z') as A. On exit B contains the solution.
        A = B_pvpq
        b = p_pvpq-p_slack*v_phase_slack
        linsolve(A, b)
        logger.debug("UMFPACK linsolve solution:\n%s" % b)

#        v_phase = matrix([b[:slack_idx], [v_phase_slack], b[slack_idx:]])
        import numpy # FIXME: remove numpy dependency
        # Insert the reference voltage angle of the slack bus
        v_phase = matrix(numpy.insert(b, slack_idx, v_phase_slack))
        logger.debug("Bus voltage phase angles:\n%s" % v_phase)

        self.v_phase = v_phase

        return v_phase

    #--------------------------------------------------------------------------
    #  Set model attributes:
    #--------------------------------------------------------------------------

    def _update_model(self):
        """ Updates the network model with values computed from the voltage
        phase angle solution

        """

        base_mva = self.network.mva_base
        buses = self.network.non_islanded_buses
        branches = self.network.in_service_branches

        p_source = self.B_source * self.v_phase * base_mva
        p_target = -p_source

        for i in range(len(branches)):
            branches[i].p_source = p_source[i]
            branches[i].p_target = p_target[i]
            branches[i].q_source = 0.0
            branches[i].q_target = 0.0

        for i in range(len(buses)):
            v_phase = self.v_phase[i]
            buses[i].v_phase = v_phase*(180/pi)
            buses[i].v_amplitude = 1.0

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    from pylon.filter.api import read_matpower
    data_file = "/home/rwl/python/aes/matpower_3.2/case6ww.m"

    dc_pf = DCPFRoutine(read_matpower(data_file))

# EOF -------------------------------------------------------------------------
