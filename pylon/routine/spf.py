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

"""
Standard power flow routine with Newton-Raphson method implementation.

Reference:
    Power System Analysis Toolbox by Federico Milano

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

import math

from numpy import pi, zeros, ones, Inf, hstack, vstack, arange, conjugate

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul, exp

from cvxopt.umfpack import linsolve

from cvxopt.lapack import gesv

from pylon.routine.y import PSATAdmittanceMatrix

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Convenience function for computing the conjugate of cvxopt matrices:
#------------------------------------------------------------------------------

def conj(A): return A.ctrans().trans()

#------------------------------------------------------------------------------
#  "DifferantialAlgebraicEquation" class:
#------------------------------------------------------------------------------

class DifferantialAlgebraicEquation:
    """
    Differential and algebraic equations, functions and Jacobian
    matrices.

    """

    # Algebraic variables
    y = matrix

    # Variable for distributing losses among generators
#    kg = 0

    # State variables
    x = matrix

    # Number of state variables
    n = 0

    # Number of algebraic variables
    m = 0

    # Dynamic order during power flow
#    npf = 0

    # Differential equations
    f = matrix

    # Algebraic equations
    g = matrix

    # Jacobian matrix of differential equations Fx = grad_xf
    fx = spmatrix

    # Jacobian matrix of differential equations Fy = grad_yf
    fy = spmatrix

    # Jacobian matrix of algebraic equations Gx = grad_xg
    gx = spmatrix

    # Jacobian matrix of algebraic equations Gy = grad_yg
    gy = spmatrix

    # Jacobian matrix of algebraic equations Glamb = grad_lambg
#    gl = spmatrix
#
    # Jacobian matrix of algebraic equations Gk = grad_kg
#    gk = spmatrix
#
    # Complete DAE Jacobian matrix
#    ac = spmatrix
#
    # Vector of DAE for time domain simulations
#    tn = matrix
#
    # Current simulation time (-1 for static analysis)
#    t = -1

#------------------------------------------------------------------------------
#  "NewtonRaphsonRoutine" class:
#------------------------------------------------------------------------------

class SPFRoutine:
    """ Standard power flow routine with Newton-Raphson method implementation

    """

    # The maximum number of iterations
    max_iterations = 2

    # Error tolerance
    tolerance = 1e-05

    # Generator reactive power limit control
    q_limiting = False

    # Branch admittance matrix
    Y = spmatrix

    # Differential and algebraic equations, functions and
    # Jacobian matrices
    dae = DifferantialAlgebraicEquation()

    #--------------------------------------------------------------------------
    #  "SPFRoutine" interface:
    #--------------------------------------------------------------------------

    def solve(self, buses, branches):
        """ Solves the standard power flow """

        n_buses = len(buses)

        iteration = 1
        max_error = self.tolerance + 1
        alpha = Float(0.85)

        pam = PSATAdmittanceMatrix()
        self.Y = pam.build(self.network)

        dae = self.dae

        self.initialise_dae(dae, buses)

        while max_error > self.tolerance and \
            iteration < self.max_iterations and \
            alpha > 1e-05:

            # TODO: Distributed slack bus method
            # TODO: Robust method
            # Standard Newton-Raphson method

            # refresh Jacobian
            self.g = matrix(zeros((dae.m, 1)))

            self._build_algebraic_equations(dae, buses)

            self._build_jacobian_matrix(dae, buses)

            # Fxcall(PV)
            # Fxcall(SW)

            # No dynamic components
            dae.fx = spmatrix(1, [0], [0])

            # Increment
            # hstack using transpose and sparse()
            _top = sparse([dae.fx.T, dae.fy.T]).T
            _bot = sparse([dae.gx.T, dae.gy.T]).T
            a = sparse([_top, _bot])
            print "A:\n", a
            b = matrix([dae.f, dae.g])
            print "B:\n", b
            # Solves the sparse set of linear equations AX=B where A is
            # a sparse matrix and B is a dense matrix of the same type
            # ('d' or 'z') as A. On exit B contains the solution.
#            gesv(matrix(a), b)
            linsolve(-a, b)
            increment = b
            print "Increment:", increment

#            dae.x += increment[0:dae.n]
#            print "X:", dae.x

#            if dae.y.size != increment.size:
#                dae.y = matrix([dae.y, matrix([0])])
#                print "Y:", dae.y
            dae.y[n_buses:] += increment[n_buses]
            print "Y:", dae.y

            iteration += 1
            max_error = max(abs(increment))

    #--------------------------------------------------------------------------
    #  Initialise the differential and algebraic equations:
    #--------------------------------------------------------------------------

    def initialise_dae(self, dae, buses):
        """
        Initialises the differential and algebraic equations, allocating
        the necessary memory for the matrices.

        """

        n_buses = len(buses)

        # No dynamic elements!
        # number of state variables
        dae.n = 1 # Should perhaps be 0
        # number of algebraic variables
        dae.m = 2*n_buses
        # algebraic variables (See @BUclass/setup.m)
        ya = matrix([v.v_phase_guess for v in buses], tc='z')
        yv = matrix([v.v_amplitude_guess for v in buses], tc='z')
        dae.y = matrix([ya, yv])
        # Memory allocation:
        # algebraic equations
        dae.g = matrix(zeros((dae.m, 1)))
        # Jacobian of algebraic equations
        dae.gy = spmatrix([], [], [], size=(dae.m, dae.m))
        # differential equations
        dae.f = matrix(0) #matrix(ones((dae.n, 1)))
        # state variables
        dae.x = matrix(0) #matrix(ones((dae.n, 1)))
        # grad_fx
        dae.fx = spmatrix(1, [0], [0])
        # grad_fy
        dae.fy = spmatrix([], [], [], size=(1, dae.m))
        # grad_xg
        dae.gx = spmatrix([], [], [], size=(dae.m, 1))

    #--------------------------------------------------------------------------
    #  Builds the algebraic equations vector:
    #--------------------------------------------------------------------------

    def _build_algebraic_equations(self, dae, buses):
        """
        Builds the algebraic equations vector

        """

        n_buses = len(buses)

        a_idx = matrix(arange(0, n_buses))
        v_idx = matrix(a_idx+n_buses)

        # gcall(Line)
        vc = mul(dae.y[v_idx], exp(dae.y[a_idx])) # .*
        s = matrix(vc*conjugate(self.Y*vc)) # TODO: Implement cvxopt conjugate
        # FIXME: Powers of the order e-16 may be better rounded to zero
        dae.g[a_idx] = s.real()
        dae.g[v_idx] = s.imag()

        for i, v in enumerate(buses):
            # gcall(PQ)
            for l in v.loads:
                if l.in_service:
                    dae.g[i] += l.p
                    dae.g[n_buses+i] += l.q
                    # TODO: Conversion to impedance (See @PQclass/gcall.m)
        print "G (PQ):\n", dae.g

        for i, v in enumerate(buses):
            # gcall(PV)
            for g in v.generators:
                if v.type == "PV" and g.in_service:
                    #TODO: Distributed losses (See @PVclass/gcall.m)
                    if not self.q_limiting:
                        dae.g[n_buses+i] = 0
                    else:
                        raise NotImplementedError, "Conversion of "
                        "Q limited PV nodes to PQ is not yet implemented"
        print "G (PV):\n", dae.g

        for i, v in enumerate(buses):
                # gcall(SW)
                if v.type == "Slack":
                    dae.g[i] = 0
                    if not self.q_limiting:
                        dae.g[n_buses+i] = 0
                    else:
                        raise NotImplementedError, "Conversion of "
                        "Slack bus to theta-Q bus is not yet implemented"
        print "G (SW):\n", dae.g

    #--------------------------------------------------------------------------
    #  Builds the Jacobian matrix:
    #--------------------------------------------------------------------------

    def _build_jacobian_matrix(self, dae, buses):
        """
        Builds the Jacobian matrix

        """

        n_buses = len(buses)

        a_idx = matrix(arange(0, n_buses))
        v_idx = matrix(a_idx+n_buses)

        # Gycall(Line) - @LNclass/build_gy.m
        dae.gy = spmatrix(1e-06, range(dae.m), range(dae.m))

        u = exp(dae.y[a_idx])
        v = mul(dae.y[v_idx], u)
        i = self.Y*v
        diag_vn = spmatrix(u, a_idx, a_idx)
        diag_vc = spmatrix(v, a_idx, a_idx)
        diag_ic = spmatrix(i, a_idx, a_idx)

        ds = diag_vc * conj(self.Y*diag_vn) + conj(diag_ic) * diag_vn
        dr = conj(diag_vc) * (diag_ic - self.Y*diag_vc)

        # hstack using transpose and sparse()
        _top = sparse([dr.imag().T, ds.real().T]).T
        _bot = sparse([dr.real().T, ds.imag().T]).T
        dae.gy = sparse([_top, _bot])

        # Gycall(PQ)
        # TODO: Conversion to impedance

        # Gycall(PV)
        if not self.q_limiting:
            # FIXME: Buses have type PV even without generation
            pv_idx = [buses.index(v) for v in buses if v.type == "PV"]
            for i in pv_idx:
                idx = v_idx[i]
                self._set_gy(idx)
        else:
            raise NotImplementedError, "See @PVclass/Gycall.m"

        # Gycall(SW)
        slack_idx = [buses.index(v) for v in buses if v.type == "Slack"]
        for i in slack_idx:
            idx = a_idx[i]
            self._set_gy(idx)
            if not self.q_limiting:
                idx = v_idx[i]
                self._set_gy(idx)
            else:
                raise NotImplementedError, "See @SWclass/Gycall.m"

        # More Jacobian matrices
        n = dae.n
        m = dae.m
        dae.fx = spmatrix([], [], [], (n, n))
        dae.fy = spmatrix([], [], [], (n, m))
        dae.gx = spmatrix([], [], [], (m, n))


    def _set_gy(self, idx):
        """
        Zeros the dae.gy column and row of idx and sets the element
        [idx,  idx] to one.

        """

        dae = self.dae

        dae.gy[idx, :] = 0
        dae.gy[:, idx] = 0
        dae.gy[idx, idx] = 1

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    from pylon.filter.api import PSATImporter

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    filter = PSATImporter()
    data_file = "/home/rwl/python/aes/psat_20080214/src/rwl_003_opf_mdl.m"
    n = filter.parse_file(data_file)

    routine = SPFRoutine(network=n)

# EOF -------------------------------------------------------------------------
