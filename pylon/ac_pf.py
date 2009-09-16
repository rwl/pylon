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

""" Defines a base class for many AC power flow routines.

    References:
        Ray Zimmerman, "acpf.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import math
import cmath
import logging
from os import path

import numpy
from numpy import dot
from numpy import angle as numpy_angle

from cvxopt.base import matrix, spmatrix, sparse, spdiag, gemv, exp, mul, div
from cvxopt.lapack import getrf
from cvxopt.umfpack import symbolic, numeric, linsolve
import cvxopt.blas

from pylon.y import AdmittanceMatrix
from pylon.util import conj

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

j  = 0 + 1j
pi = math.pi

#------------------------------------------------------------------------------
#  "_ACPF" class:
#------------------------------------------------------------------------------

class _ACPF(object):
    """ Base class for many AC power flow routines.

        References:
            Ray Zimmerman, "acpf.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tolerance=1e-08, iter_max=10):
        """ Initialises a new ACPF instance.
        """
        self.case = None
        # Convergence tolerance.
        self.tolerance = tolerance
        # Maximum number of iterations.
        self.iter_max = iter_max

        # Vector of bus voltages.
        self.v = None
        # Sparse admittance matrix.
        self.Y = None
        # Complex bus power injections.
        self.s_surplus = matrix
        # Flag indicating if the solution converged:
        self.converged = False

        # Bus indexes for updating v.
        self.pv_idxs = []
        self.pq_idxs = []
        self.pvpq_idxs = []
        self.slack_idx = 0


    def __call__(self, case):
        """ Calls the routine with the given case.
        """
        self.solve(case)


    def solve(self):
        """ Override this method in subclasses.
        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    #  Make vector of initial node voltages:
    #--------------------------------------------------------------------------

    def _get_initial_voltage_vector(self):
        """ Makes the initial vector of complex bus voltages.  The bus voltage
            vector contains the set point for generator (including ref bus)
            buses, and the reference angle of the swing bus, as well as an
            initial guess for remaining magnitudes and angles.
        """
        buses = self.case.connected_buses

        v_magnitude = matrix([bus.v_magnitude_guess for bus in buses])

        # Initial bus voltage angles in radians.
        v_angle = matrix([bus.v_angle_guess * pi / 180.0 for bus in buses])

        v_guess = mul(v_magnitude, exp(j * v_angle)) #element-wise product

        # Get generator set points.
        for i, bus in enumerate(buses):
            if bus.generators:
                g = bus.generators[0]
                #   V0(gbus) = gen(on, VG) ./ abs(V0(gbus)).* V0(gbus);
                #            Vg
                #   V0 = ---------
                #        |V0| . V0
#                v = mul(abs(v_guess[i]), v_guess[i])
#                v_guess[i] = div(g.v_magnitude, v)
#                v = abs(v_guess[i]) * v_guess[i]
#                v_guess[i] = g.v_magnitude / v
                v_guess[i] = g.v_magnitude

        return v_guess

    #--------------------------------------------------------------------------
    #  Make vector of apparent power injected at each bus:
    #--------------------------------------------------------------------------

    def _get_power_injection_vector(self):
        """ Makes the vector of complex bus power injections (gen - load).
        """
        buses = self.case.connected_buses

        return matrix(
            [complex(bus.p_surplus, bus.q_surplus) for bus in buses], tc="z")

    #--------------------------------------------------------------------------
    #  Index buses for updating v:
    #--------------------------------------------------------------------------

    def _index_buses(self):
        """ Set up indexing for updating v.
        """
        buses = self.case.connected_buses

        # Indexing for updating v
        pv_idxs = [i for i, v in enumerate(buses) if v.mode is "pv"]
        pq_idxs = [i for i, v in enumerate(buses) if v.mode is "pq"]
        pvpq_idxs = pv_idxs + pq_idxs

        slack_idxs = [i for i, v in enumerate(buses) if v.mode is "slack"]
        if len(slack_idxs) > 0:
            slack_idx = slack_idxs[0]
        else:
            logger.error("No reference/swing/slack bus specified.")
            slack_idx = pv_idxs[0]

        self.slack_idx = slack_idx
        self.pv_idxs = pv_idxs
        self.pq_idxs = pq_idxs
        self.pvpq_idxs = pvpq_idxs

#------------------------------------------------------------------------------
#  "NewtonRaphson" class:
#------------------------------------------------------------------------------

class NewtonRaphson(_ACPF):
    """ Solves the power flow using full Newton's method.

        References:
            Ray Zimmerman, "newton.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
    """
    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tolerance=1e-08, iter_max=10):
        """ Initialises a new ACPF instance.
        """
        # Sparse Jacobian matrix (updated each iteration).
        self.J = None
        # Function of non-linear differential algebraic equations.
        self.f = None

        super(NewtonRaphson, self).__init__(tolerance, iter_max)

    #--------------------------------------------------------------------------
    #  Solve power flow using full Newton's method:
    #--------------------------------------------------------------------------

    def solve(self, case):
        """ Solves the AC power flow for the referenced case using full
            Newton's method.
        """
        self.case = case

        logger.info("Performing AC power flow using Newton-Raphson method.")

        t0 = time.time()

        admittance_matrix = AdmittanceMatrix()
        self.Y = admittance_matrix(case)

        self.v = self._get_initial_voltage_vector()
        self.s_surplus = self._get_power_injection_vector()

        self._index_buses()

        # Initial evaluation of f(x0) and convergency check.
        self.converged = False
        self.f = self._evaluate_function()
        self.converged = self._check_convergence()

        iter = 0
        while (not self.converged) and (iter < self.iter_max):
            self._iterate()
            self.f = self._evaluate_function()
            self.converged = self._check_convergence()
            iter += 1

        t_elapsed = time.time() - t0

        if self.converged:
            logger.info("AC power flow converged in %d iterations." % iter)
            logger.info("AC power flow completed in %.3fs" % t_elapsed)
        else:
            logger.info("Routine failed to converge in %d iterations." % iter)


    #--------------------------------------------------------------------------
    #  Newton iterations:
    #--------------------------------------------------------------------------

    def _iterate(self):
        """ Performs Newton iterations.
        """
        J = self._get_jacobian()
        F = self.f

        v_angle = matrix(numpy_angle(self.v))
        v_magnitude = abs(self.v)

        pv_idxs = self.pv_idxs
        pq_idxs = self.pq_idxs
        npv = len(pv_idxs)
        npq = len(pq_idxs)

        # Compute update step. Solves the sparse set of linear equations AX=B
        # where A is a sparse matrix and B is a dense matrix of the same type
        # ("d" or "z") as A. On exit B contains the solution.
        linsolve(J, F)

        dx = -1 * F # Update step.
        logger.debug("dx =\n%s" % dx)

        # Update voltage vector
        if pv_idxs:
            # Va(pv) = Va(pv) + dx(j1:j2);
            v_angle[pv_idxs] = v_angle[pv_idxs] + dx[range(npv)]

        if pq_idxs:
            v_angle[pq_idxs] = v_angle[pq_idxs] + dx[range(npv, npv+npq)]

            v_magnitude[pq_idxs] = v_magnitude[pq_idxs] + \
                dx[range(npv+npq, npv+npq+npq)]

        # V = Vm .* exp(j * Va);
        self.v = v = mul(v_magnitude, exp(j * v_angle))

        # Avoid wrapped round negative Vm
#        Vm = abs(voltage)
#        Va = angle(voltage)

        logger.debug("V: =\n%s" % v)

        return v

    #--------------------------------------------------------------------------
    #  Evaluate Jacobian:
    #--------------------------------------------------------------------------

    def _get_jacobian(self):
        """ Computes partial derivatives of power injection w.r.t. voltage.
            The following explains the expressions used to form the matrices:

            S = diag(V) * conj(Ibus) = diag(conj(Ibus)) * V

            Partials of V & Ibus w.r.t. voltage magnitudes
               dV/dVm = diag(V./abs(V))
               dI/dVm = Ybus * dV/dVm = Ybus * diag(V./abs(V))

            Partials of V & Ibus w.r.t. voltage angles
               dV/dVa = j * diag(V)
               dI/dVa = Ybus * dV/dVa = Ybus * j * diag(V)

            Partials of S w.r.t. voltage magnitudes
               dS/dVm = diag(V) * conj(dI/dVm) + diag(conj(Ibus)) * dV/dVm
                      = diag(V) * conj(Ybus * diag(V./abs(V)))
                                         + conj(diag(Ibus)) * diag(V./abs(V))

            Partials of S w.r.t. voltage angles
               dS/dVa = diag(V) * conj(dI/dVa) + diag(conj(Ibus)) * dV/dVa
                      = diag(V) * conj(Ybus * j * diag(V))
                                        + conj(diag(Ibus)) * j * diag(V)
                      = -j * diag(V) * conj(Ybus * diag(V))
                                        + conj(diag(Ibus)) * j * diag(V)
                      = j * diag(V) * conj(diag(Ibus) - Ybus * diag(V))

            References:
                Ray Zimmerman, "dSbus_dV.m", MATPOWER, version 3.2,
                PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
        """
        j = 0 + 1j
        y = self.Y
        v = self.v
        n = len(self.case.buses)

        pv_idxs = self.pv_idxs
        pq_idxs = self.pq_idxs
        pvpq_idxs = self.pvpq_idxs

#        Ibus = cvxopt.blas.dot(matrix(self.Y), v)
        i_bus = y * v
#        Ibus = self.Y.trans() * v
        logger.debug("i_bus =\n%s" % i_bus)

        diag_v = spmatrix(v, range(n), range(n), tc="z")
        logger.debug("diag_v =\n%s" % diag_v)

        diag_ibus = spmatrix(i_bus, range(n), range(n), tc="z")
        logger.debug("diag_ibus =\n%s" % diag_ibus)

        # diagVnorm = spdiags(V./abs(V), 0, n, n);
        diag_vnorm = spmatrix(div(v, abs(v)), range(n), range(n), tc="z")
        logger.debug("diag_vnorm =\n%s" % diag_vnorm)

        # From MATPOWER v3.2:
        # dSbus_dVm = diagV * conj(Y * diagVnorm) + conj(diagIbus) * diagVnorm;
        # dSbus_dVa = j * diagV * conj(diagIbus - Y * diagV);

        s_vm = diag_v * conj(y * diag_vnorm) + conj(diag_ibus) * diag_vnorm
#        dS_dVm = dot(
#            dot(diagV, conj(dot(Y, diagVnorm))) + conj(diagIbus), diagVnorm
#        )
        #dS_dVm = dot(diagV, conj(dot(Y, diagVnorm))) + dot(conj(diagIbus), diagVnorm)
        logger.debug("dS/dVm =\n%s" % s_vm)

        s_va = j * diag_v * conj(diag_ibus - y * diag_v)
#        dS_dVa = dot(dot(j, diagV), conj(dot(diagIbus - Y, diagV)))
        #dS_dVa = dot(dot(j, diagV), conj(diagIbus - dot(Y, diagV)))
        logger.debug("dS/dVa =\n%s" % s_va)


#        dP_dVm = spmatrix(map(lambda x: x.real, dS_dVm), dS_dVm.I, dS_dVa.J, tc="d")

#        dP_dVm = spmatrix(dS_dVm.real(), dS_dVm.I, dS_dVa.J, tc="d")
#        logger.debug("dP_dVm =\n%s" % dP_dVm)
#
#        dP_dVa = spmatrix(dS_dVa.real(), dS_dVa.I, dS_dVa.J, tc="d")
#        logger.debug("dP_dVa =\n%s" % dP_dVa)
#
#        dQ_dVm = spmatrix(dS_dVm.imag(), dS_dVm.I, dS_dVm.J, tc="d")
#        logger.debug("dQ_dVm =\n%s" % dQ_dVm)
#
#        dQ_dVa = spmatrix(dS_dVa.imag(), dS_dVa.I, dS_dVa.J, tc="d")
#        logger.debug("dQ_dVa" % dQ_dVa)

        # From MATPOWER v3.2:
        #    j11 = real(dSbus_dVa([pv; pq], [pv; pq]));
        #    j12 = real(dSbus_dVm([pv; pq], pq));
        #    j21 = imag(dSbus_dVa(pq, [pv; pq]));
        #    j22 = imag(dSbus_dVm(pq, pq));

#            J11 = dP_dVa[pvpq_idxs, pvpq_idxs]
#            J12 = dP_dVm[pvpq_idxs, pq_idxs]
#            J21 = dQ_dVa[pq_idxs, pvpq_idxs]
#            J22 = dQ_dVm[pq_idxs, pq_idxs]

        j11 = s_va[pvpq_idxs, pvpq_idxs].real()
        j12 = s_vm[pvpq_idxs, pq_idxs].real()
        j21 = s_va[pq_idxs, pvpq_idxs].imag()
        j22 = s_vm[pq_idxs, pq_idxs].imag()

        logger.debug("J12 =\n%s" % j12)
        logger.debug("J22 =\n%s" % j22)

        # The width and height of one quadrant of the Jacobian.
#        w, h = J11.size
#        print "w, h", J11.size, J12.size, J21.size, J22.size

        # A single-column dense matrix containing the numerical values of
        # the nonzero entries of the four quadrants of the Jacobian in
        # column-major order.
#        values = numpy.vstack((J11.V, J12.V, J21.V, J22.V))

        # A single-column integer matrix with the row indices of the entries
        # in "values" shifted appropriately by the width of one quadrant.
#        row_idxs = numpy.vstack((J11.I, J12.I, J21.I+h, J22.I+h))

        # A single-column integer matrix with the column indices of the
        # entries in "values" shifted appropriately by the width of one
        # quadrant.
#        col_idxs = numpy.vstack((J11.J, J12.J+w, J21.J, J22.J+w))

        # A deep copy of "values" is required for contiguity.
#        J = spmatrix(values.copy(), row_idxs, col_idxs)

        j1 = sparse([j11, j21])
        j2 = sparse([j12, j22])

        self.J = J = sparse([j1.T, j2.T]).T
        logger.debug("J =\n%s" % J)

        return J

    #--------------------------------------------------------------------------
    #  Evaluate F(x):
    #--------------------------------------------------------------------------

    def _evaluate_function(self):
        """ Evaluates F(x).
        """
        # mis = V .* conj(Ybus * V) - Sbus;
        mismatch = mul(self.v, conj(self.Y * self.v)) - self.s_surplus

        real = mismatch[self.pvpq_idxs].real()
        imag = mismatch[self.pq_idxs].imag()

        return matrix([real, imag])

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        f = self.f

        normf = max(abs(f))

        if normf < self.tolerance:
            converged = True
        else:
            converged = False
#            logger.info("Difference: %.3f" % normF-self.tolerance)

        return converged

#------------------------------------------------------------------------------
#  "FastDecoupled" class:
#------------------------------------------------------------------------------

class FastDecoupled(_ACPF):
    """ Solves the power flow using fast decoupled method.

        References:
            Ray Zimmerman, "fdpf.m", MATPOWER, PSERC Cornell, version 3.2,
            http://www.pserc.cornell.edu/matpower/, June 2007
    """
    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tolerance=1e-08, iter_max=10, method="XB"):
        """ Initialises a new ACPF instance.
        """
        # Use XB or BX method?
        self.method = method
        # Sparse FDPF matrix B prime.
        self.Bp = None
        # Sparse FDPF matrix B double prime.
        self.Bpp = None

        self.p = None
        self.q = None

        super(_ACPF, self).__init__(tolerance, iter_max)

    #--------------------------------------------------------------------------
    #  Solve power flow using Fast Decoupled method:
    #--------------------------------------------------------------------------

    def solve(self, case):
        """ Solves the AC power flow for the referenced case using fast
            decoupled method.  Returns the final complex voltages, a flag which
            indicates whether it converged or not, and the number of iterations
            performed.
        """
        self.case = case

        logger.info("Performing AC power flow using Fast Decoupled method.")

        t0 = time.time()

        self._make_B_prime()
        self._make_B_double_prime()

        self._make_admittance_matrix()
        self._initialise_voltage_vector()
        self._make_power_injection_vector()
        self._index_buses()

        # Initial mismatch evaluation and convergency check.
        self.converged = False
        self._evaluate_mismatch()
        self._check_convergence()

#        iter = 0
#        while (not self.converged) and (iter < self.iter_max):
#            self.iterate()
#            self._evaluate_mismatch()
#            self._check_convergence()
#            iter += 1

        if self.converged:
            logger.info("Routine converged in %d iterations." % iter)
        else:
            logger.info("Routine failed to converge in %d iterations." % iter)

        t_elapsed = time.time() - t0
        logger.info("AC power flow completed in %.3fs" % t_elapsed)

    #--------------------------------------------------------------------------
    #  P and Q iterations:
    #--------------------------------------------------------------------------

    def iterate(self):
        """ Performs P and Q iterations.
        """
        pass


    def _factor_B_matrices(self):
        """ Perform symbolic and numeric LU factorisation of Bp and Bpp.
        """
        Bp = self.Bp
        Bpp = self.Bpp

        # The numeric factorisation is returned as an opaque C object that
        # can be passed on to umfpack.solve().
        opaqueBp = numeric(Bp, symbolic(Bp))
        opaqueBpp = numeric(Bpp, symbolic(Bp))

    #--------------------------------------------------------------------------
    #  Evaluate mismatch:
    #--------------------------------------------------------------------------

    def _evaluate_mismatch(self):
        """ Evaluates the mismatch between.

          -4.0843 - 4.1177i
           1.0738 - 0.2847i
           0.2524 - 0.9024i
           4.6380 - 0.6955i
          -0.1939 + 0.6726i
          -0.2126 + 0.9608i

           4.0063 -11.7479i  -2.6642 + 3.5919i        0            -4.6636 + 1.3341i  -0.8299 + 3.1120i
          -1.2750 + 4.2865i   9.3283 -23.1955i  -0.7692 + 3.8462i  -4.0000 + 8.0000i  -1.0000 + 3.0000i
                0            -0.7692 + 3.8462i   4.1557 -16.5673i        0            -1.4634 + 3.1707i
           3.4872 + 3.3718i  -4.0000 + 8.0000i        0             6.1765 -14.6359i  -1.0000 + 2.0000i
          -0.8299 + 3.1120i  -1.0000 + 3.0000i  -1.4634 + 3.1707i  -1.0000 + 2.0000i   5.2933 -14.1378i
                0            -1.5590 + 4.4543i  -1.9231 + 9.6154i        0            -1.0000 + 3.0000i
        """
        j = 0 + 1j

        # MATPOWER:
        #   mis = (V .* conj(Ybus * V) - Sbus) ./ Vm;
        v = self.v
        Y = self.Y
        s = self.s_surplus

#        print "V:", v
#        print "Y:", Y
        print "S:", s

#        mismatch = div(mul(v, conj(self.Y * v) - self.s_surplus), abs(v))
        mismatch = div(mul(v, conj(Y * v)) - s, abs(v))

        print "MIS:", mismatch

        self.p = p = mismatch[self.pvpq_idxs].real()
        self.q = q = mismatch[self.pq_idxs].imag()

        print "P:", p
        print "Q:", q

        return p, q# + j*q

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        P = self.p
        Q = self.q
        tolerance = self.tolerance

        normP = max(abs(P))
        normQ = max(abs(Q))

        if (normP < tolerance) and (normQ < tolerance):
            self.converged = converged = True
        else:
            self.converged = converged = False
#            logger.info("Difference: %.3f" % normF-self.tolerance)

        return converged

    #--------------------------------------------------------------------------
    #  Make FDPF matrix B prime:
    #--------------------------------------------------------------------------

    def _make_B_prime(self):
        """ Builds the Fast Decoupled Power Flow matrix B prime.

            References:
            R. Zimmerman, "makeB.m", MATPOWER, PSERC (Cornell),
            version 1.5, http://www.pserc.cornell.edu/matpower/, July 8, 2005

        """
        if self.method is "XB":
            r_line = False
        else:
            r_line = True

        am = AdmittanceMatrix(bus_shunts=False, line_shunts=False,
                              taps=False, line_resistance=r_line)
        Y, Ysrc, Ytgt = am(self.case)

        self.Bp = Bp = -Y.imag()

        return Bp

    #--------------------------------------------------------------------------
    #  Make FDPF matrix B double prime:
    #--------------------------------------------------------------------------

    def _make_B_double_prime(self):
        """ Builds the Fast Decoupled Power Flow matrix B double prime.

            References:
            R. Zimmerman, "makeB.m", MATPOWER, PSERC (Cornell),
            version 1.5, http://www.pserc.cornell.edu/matpower/, July 8, 2005
        """
        if self.method is "BX":
            r_line = False
        else:
            r_line = True

        am = AdmittanceMatrix(line_resistance=r_line, phase_shift=False)

        Y = am(self.case)

        self.Bp = Bpp = -Y.imag()

        return Bpp


    def _reduce_B_matrices(self):
        """ Reduces the FDPF matrices Bp and Bpp.
        """
        # Reduce Bp matrix
        # Bp = Bp([pv; pq], [pv; pq]);
        self.Bp = self.Bp[self.pvpq_idxs]

        # Reduce Bpp matrix
        # Bpp = Bpp(pq, pq);
        self.Bpp = self.Bpp[self.pq_idxs]

# EOF -------------------------------------------------------------------------
