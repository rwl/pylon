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

""" State estimation (under construction) based on code from James S. Thorp.

    References:
        R. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, "state_est.m",
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul
from cvxopt.umfpack import linsolve

from ac_opf import dSbus_dV, dSbr_dV
from ac_pf import ACPFRoutine
from dc_pf import DCPFRoutine

j = 0.0+1.0j

#------------------------------------------------------------------------------
#  "StateEsimationRoutine" class:
#------------------------------------------------------------------------------

class StateEsimationRoutine(object):
    """ State estimation based on code from James S. Thorp.
    """
    # Bus-branch network linking loads and generators.
    network = None

    pf_routine = None

    # Use DC power flow formulation?
    dc = False

    # Maximum number of iterations.
    max_iter = 100

    # Absolute accuracy.
    tolerance = 1e-7

    converged = False

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network, dc=False, max_iter=100, tolerance=1e-7):
        """ Initialises a new StateEstimationRoutine instance.
        """
        self.network = network

        if dc:
            self.pf_routine = DCPFRoutine()
        else:
            self.pf_routine = ACPFRoutine()

        self.max_iter = max_iter
        self.tolerance = tolerance

    #--------------------------------------------------------------------------
    #  Solves a state estimation problem:
    #--------------------------------------------------------------------------

    def solve(self, network=None):
        """ Solves a state estimation problem.
        """
        network = self.network
        branches = network.online_branches

        # Run the power flow.
        self.pf_routine.solve()

        # Save some values from the load flow solution.
        plf_source = [branch.p_source for branch in branches]
        qlf_source = [branch.q_source for branch in branches]
        plf_target = [branch.p_target for branch in branches]
        qlf_target = [branch.q_target for branch in branches]

        # Begin state estimation.
        Y = self.pf_routine.Y # Sparse admittance matrix.
        v = self.pf_routine.v # Vector of bus voltages.

        # Evaluate the Hessian.
        dSbus_dVm, dSbus_dVa = dSbus_dV(Y, v)
        dSbr_dVm, dSbr_dVa = dSbr_dV(branches, Ysource, Ytarget, v)



# EOF -------------------------------------------------------------------------
