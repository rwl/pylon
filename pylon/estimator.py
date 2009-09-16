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
        Ray Zimmerman, "state_est.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul
from cvxopt.umfpack import linsolve

from ac_opf import dSbus_dV, dSbr_dV
from ac_pf import ACPF
from dc_pf import DCPF

j = 0.0+1.0j

#------------------------------------------------------------------------------
#  "StateEsimationRoutine" class:
#------------------------------------------------------------------------------

class StateEsimationRoutine(object):
    """ State estimation based on code from James S. Thorp.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, dc=False, max_iter=100, tolerance=1e-7):
        """ Initialises a new StateEstimationRoutine instance.
        """
        # Maximum number of iterations.
        self.max_iter = max_iter
        # Convergence tolerance.
        self.tolerance = tolerance

        # Use DC power flow formulation?
        self.dc = dc

        if dc:
            self.pf_routine = DCPF()
        else:
            self.pf_routine = ACPF()

        self.case = None
        # Has the routine converged?
        self.converged = False

    #--------------------------------------------------------------------------
    #  Solves a state estimation problem:
    #--------------------------------------------------------------------------

    def __call__(self, case):
        """ Solves a state estimation problem.
        """
        self.case = case
        branches = case.online_branches

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

        H = spmatrix([
            dSf_dVa.real(),   dSf_dVm.real(),
            dSt_dVa.real(),   dSt_dVm.real(),
            dSbus_dVa.real(), dSbus_dVm.real(),
            spdiag(1.0, range(nb)), spmatrix(0.0, (nb,nb)),
            dSf_dVa.imag(),   dSf_dVm.imag(),
            dSt_dVa.imag(),   dSt_dVm.imag(),
            dSbus_dVa.imag(), dSbus_dVm.imag(),
            spmatrix(0.0, (nb,nb)), spdiag(1.0, range(nb))
        ])

        # True measurement.
        z = matrix([
            Sf.real(),
            St.real(),
            Sbus.real(),
            angle(V0),
            Sf.imag(),
            St.imag(),
            Sbus.imag(),
            abs(V0)
        ])

        # Create inverse of covariance matrix with all measurements.
        full_scale = 30
#        sigma = [
#            0.02 * abs(Sf)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(St)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(Sbus)    + 0.0052 * full_scale * ones(nb,1),
#            0.2 * pi/180 * 3*ones(nb,1),
#            0.02 * abs(Sf)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(St)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(Sbus)    + 0.0052 * full_scale * ones(nb,1),
#            0.02 * abs(V0)      + 0.0052 * 1.1 * ones(nb,1),
#        ] ./ 3

# EOF -------------------------------------------------------------------------
