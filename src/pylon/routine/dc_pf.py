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

from pylon.routine.y import SusceptanceMatrix
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

    # Vector of voltage angle guesses
    v_phase_guess = matrix

    # Branch susceptance matrix
    B = spmatrix([], [], [])

    # Branch source bus susceptance matrix
    B_source = spmatrix([], [], [])

    # Vector of voltage phase angles
    v_phase = matrix

    #--------------------------------------------------------------------------
    #  Solve power flow:
    #--------------------------------------------------------------------------

    def solve(self):

        if not self.network.slack_model == "Single":
            logger.error(
                "Performing a DC power flow requires a single slack bus"
            )
            return

        self._build_v_phase_guess_vector()

        sm = SusceptanceMatrix()
        self.B, self.B_source = sm.build(self.network)
        del sm

        self._build_v_phase_vector()

        self._update_model()

    #--------------------------------------------------------------------------
    #  Build voltage phase angle guess vector:
    #--------------------------------------------------------------------------

    def _build_v_phase_guess_vector(self):
        """ Build the vector of voltage phase guesses """

        vpg = matrix([v.v_phase_guess for v in self.network.buses])
        logger.debug("Built vector of voltage phase guesses:\n%s" % vpg)

        self.v_phase_guess = vpg
        return vpg

    #--------------------------------------------------------------------------
    #  Calculate voltage angles:
    #--------------------------------------------------------------------------

    def _build_v_phase_vector(self):
        """ Caluclates the voltage phase angles """

        buses = self.network.buses

        # Remove the column and row from the susceptance matrix that
        # correspond to the slack bus
        slack_idxs = [buses.index(v) for v in buses if v.slack]
        # Assume a single slack bus model
        slack_idx = slack_idxs[0]

        tight_idxs = [buses.index(v) for v in buses if not v.slack]

        B_tight = self.B[tight_idxs, tight_idxs]
        B_slack = self.B[tight_idxs, slack_idx]

        logger.debug(
            "Susceptance matrix with the row and column corresponding to "
            "the slack bus removed:\n%s" % B_tight
        )
        logger.debug(
            "Susceptance matrix column corresponding to the slack bus:\n%s"
            % B_slack
        )

        # Bus active power injections (generation - load)
        # FIXME: Adjust for phase shifters and real shunts
        p = matrix([v.p_supply for v in buses])
        p_slack = p[slack_idx]
        p_tight = p[tight_idxs]
        logger.debug("Active power injections:\n%s" % p_tight)

        v_phase_slack = self.v_phase_guess[slack_idx]
        logger.debug("Slack bus voltage angle:\n%s" % v_phase_slack)

        # Solves the sparse set of linear equations Ax=b where A is a
        # sparse matrix and B is a dense matrix of the same type ('d'
        # or 'z') as A. On exit B contains the solution.
        A = B_tight
        b = p_tight-p_slack*v_phase_slack
        linsolve(A, b)
        logger.debug("UMFPACK linsolve solution:\n%s" % b)

        import numpy
        # Insert the reference voltage angle of the slack bus
        v_phase = matrix(numpy.insert(b, slack_idx, 0.0))
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

        buses = self.network.buses
        branches = self.network.branches

        p_source = self.B_source * self.v_phase
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

    from pylon.filter.api import MATPOWERImporter
    filter = MATPOWERImporter()
    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
    n = filter.parse_file(data_file)

    dc_pf = DCPFRoutine(network=n)
    dc_pf.configure_traits()
#   dc_pf.solve()

# EOF -------------------------------------------------------------------------
