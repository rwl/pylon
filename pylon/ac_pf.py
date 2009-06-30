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

from os import path
import math
import cmath
import logging

import numpy
from numpy import dot
from numpy import angle as numpy_angle

from cvxopt.base import matrix, spmatrix, sparse, spdiag, gemv, exp, mul, div
from cvxopt.lapack import getrf
from cvxopt.umfpack import symbolic, numeric, linsolve
import cvxopt.blas

from pylon.y import make_admittance_matrix, AdmittanceMatrix
from pylon.util import conj

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "_ACPFRoutine" class:
#------------------------------------------------------------------------------

class _ACPFRoutine(object):
    """ Base class for many AC power flow routines.

        References:
            Ray Zimmerman, "acpf.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
    """
    network = None

    # Convergence tolerance
    tolerance = 1e-08

    # Maximum number of iterations:
    iter_max = 10

    # Vector of bus voltages:
    v = None

    # Sparse admittance matrix:
    Y = None

    # Complex bus power injections.
    s_surplus = matrix

    # Flag indicating if the solution converged:
    converged = False

    # Bus indexes for updating v.
    pv_idxs = []
    pq_idxs = []
    pvpq_idxs = []
    slack_idx = 0

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, tolerance=1e-08, iter_max=10):
        """ Initialises a new ACPFRoutine instance.
        """
        self.tolerance = tolerance
        self.iter_max  = iter_max


    def __call__(self):
        """ Override this method in subclasses.
        """
        raise NotImplementedError


    def _make_admittance_matrix(self):
        """ Forms the admittance matrix for the referenced network.
        """
        self.Y = make_admittance_matrix(self.network)

    #--------------------------------------------------------------------------
    #  Form array of initial voltages at each node:
    #--------------------------------------------------------------------------

    def _initialise_voltage_vector(self):
        """ Makes the initial vector of complex bus voltages.  The bus voltage
            vector contains the set point for generator (including ref bus)
            buses, and the reference angle of the swing bus, as well as an
            initial guess for remaining magnitudes and angles.
        """
        j = 0+1j #cmath.sqrt(-1)
        pi = math.pi
        buses = self.network.connected_buses

        Vm0 = matrix([bus.v_amplitude_guess for bus in buses], tc='z')
        Va0 = matrix([bus.v_phase_guess for bus in buses]) #degrees

        Va0r = Va0 * pi / 180 #convert to radians

        v_initial = mul(Vm0, exp(j * Va0r)) #element-wise product

        # Incorporate generator set points.
        for i, bus in enumerate(buses):
            if len(bus.generators) > 0:
                # FIXME: Handle more than one generator at a bus
                g = bus.generators[0]
                # MATPOWER:
                #   V0(gbus) = gen(on, VG) ./ abs(V0(gbus)).* V0(gbus);
                #
                #            Vg
                #   V0 = ---------
                #        |V0| . V0
                #
#                v = mul(abs(v_initial[i]), v_initial[i])
#                v_initial[i] = div(g.v_amplitude, v)
#                v = abs(v_initial[i]) * v_initial[i]
#                v_initial[i] = g.v_amplitude / v
                v_initial[i] = g.v_amplitude

        self.v = v_initial

    #--------------------------------------------------------------------------
    #  Vector of apparent power injected at each bus:
    #--------------------------------------------------------------------------

    def _make_power_injection_vector(self):
        """ Makes the vector of complex bus power injections (gen - load).
        """
        buses = self.network.connected_buses

        self.s_surplus = matrix(
            [complex(v.p_surplus, v.q_surplus) for v in buses], tc="z")

    #--------------------------------------------------------------------------
    #  Index buses for updating v:
    #--------------------------------------------------------------------------

    def _index_buses(self):
        """ Set up indexing for updating v.
        """
        buses = self.network.connected_buses

        # Indexing for updating v
        pv_idxs = [i for i, v in enumerate(buses) if v.mode is "PV"]
        pq_idxs = [i for i, v in enumerate(buses) if v.mode is "PQ"]
        pvpq_idxs = pv_idxs + pq_idxs

        slack_idxs = [i for i, v in enumerate(buses) if v.mode is "Slack"]
        if len(slack_idxs) > 0:
            slack_idx = slack_idxs[0]
        else:
            logger.error    ("No reference/swing/slack bus specified.")
            slack_idx = 0

        self.slack_idx = slack_idx
        self.pv_idxs = pv_idxs
        self.pq_idxs = pq_idxs
        self.pvpq_idxs = pvpq_idxs

#------------------------------------------------------------------------------
#  "NewtonPFRoutine" class:
#------------------------------------------------------------------------------

class NewtonPFRoutine(_ACPFRoutine):
    """ Solves the power flow using full Newton's method.
    """
    # Sparse Jacobian matrix (updated each iteration).
    J = None

    # Vector of bus voltages.
    v = None

    # Function of non-linear differential algebraic equations.
    f = None

    #--------------------------------------------------------------------------
    #  Solve power flow using full Newton's method:
    #--------------------------------------------------------------------------

    def __call__(self, network):
        """ Solves the AC power flow for the referenced network using full
            Newton's method.
        """
        self.network = network

        self._make_admittance_matrix()
        self._initialise_voltage_vector()
        self._make_power_injection_vector()
        self._index_buses()

        # Initial evaluation of f(x0) and convergency check
        self.converged = False
        self._evaluate_function()
        self._check_convergence()

        iter = 0
        while (not self.converged) and (iter < self.iter_max):
            self.iterate()
            self._evaluate_function()
            self._check_convergence()
            iter += 1

        if self.converged:
            logger.info("Routine converged in %d iterations." % iter)
        else:
            logger.info("Routine failed to converge in %d iterations." % iter)

    #--------------------------------------------------------------------------
    #  Newton iterations:
    #--------------------------------------------------------------------------

    def iterate(self):
        """ Performs Newton iterations.
        """
        j = cmath.sqrt(-1)

        J = self._make_jacobian()
        F = self.f

        Va = matrix(numpy_angle(self.v))
        Vm = abs(self.v)

        pv_idxs = self.pv_idxs
        pq_idxs = self.pq_idxs
        npv = len(pv_idxs)
        npq = len(pq_idxs)

        # Compute update step.
        #
        # Solves the sparse set of linear equations AX=B where A is a sparse
        # matrix and B is a dense matrix of the same type ("d" or "z") as A. On
        # exit B contains the solution.
        linsolve(J, F)

        dx = -1 * F # Update step.
        logger.debug("dx =\n%s" % dx)

        # Update voltage vector
        if pv_idxs:
            # Va(pv) = Va(pv) + dx(j1:j2);
            Va[pv_idxs] = Va[pv_idxs] + dx[range(npv)]

        if pq_idxs:
            Va[pq_idxs] = Va[pq_idxs] + dx[range(npv, npv+npq)]
            Vm[pq_idxs] = Vm[pq_idxs] + dx[range(npv+npq, npv+npq+npq)]

        # V = Vm .* exp(j * Va);
#        v = j * Va
        self.v = v = mul(Vm, exp(j * Va))

        # Avoid wrapped round negative Vm
        # TODO: check necessity
#        Vm = abs(voltage)
#        Va = angle(voltage)

        logger.debug("V: =\n%s" % v)

        return v

    #--------------------------------------------------------------------------
    #  Evaluate Jacobian:
    #--------------------------------------------------------------------------

    def _make_jacobian(self):
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
                D. Zimmerman, C. E. Murillo-Sanchez and D. Gan, MATPOWER,
                dSbus_dV.m, version 3.2, http://www.pserc.cornell.edu/matpower/
        """
        j = cmath.sqrt(-1)
        Y = self.Y
        v = self.v
        n = len(self.network.buses)

        pv_idxs = self.pv_idxs
        pq_idxs = self.pq_idxs
        pvpq_idxs = self.pvpq_idxs

#        Ibus = cvxopt.blas.dot(matrix(self.Y), v)
        Ibus = Y * v
#        Ibus = self.Y.trans() * v
        logger.debug("Ibus =\n%s" % Ibus)

        diagV = spmatrix(v, range(n), range(n), tc="z")
        logger.debug("diagV =\n%s" % diagV)

        diagIbus = spmatrix(Ibus, range(n), range(n), tc="z")
        logger.debug("diagIbus =\n%s" % diagIbus)

        # diagVnorm = spdiags(V./abs(V), 0, n, n);
        diagVnorm = spmatrix(div(v, abs(v)), range(n), range(n), tc="z")
        logger.debug("diagVnorm =\n%s" % diagVnorm)

        # From MATPOWER v3.2:
        # dSbus_dVm = diagV * conj(Y * diagVnorm) + conj(diagIbus) * diagVnorm;
        # dSbus_dVa = j * diagV * conj(diagIbus - Y * diagV);

        dS_dVm = diagV * conj(Y * diagVnorm) + conj(diagIbus) * diagVnorm
#        dS_dVm = dot(
#            dot(diagV, conj(dot(Y, diagVnorm))) + conj(diagIbus), diagVnorm
#        )
        #dS_dVm = dot(diagV, conj(dot(Y, diagVnorm))) + dot(conj(diagIbus), diagVnorm)
        logger.debug("dS_dVm =\n%s" % dS_dVm)

        dS_dVa = j * diagV * conj(diagIbus - Y * diagV)
#        dS_dVa = dot(dot(j, diagV), conj(dot(diagIbus - Y, diagV)))
        #dS_dVa = dot(dot(j, diagV), conj(diagIbus - dot(Y, diagV)))
        logger.debug("dS_dVa =\n%s" % dS_dVa)


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

        J11 = dS_dVa[pvpq_idxs, pvpq_idxs].real()
        J12 = dS_dVm[pvpq_idxs, pq_idxs].real()
        J21 = dS_dVa[pq_idxs, pvpq_idxs].imag()
        J22 = dS_dVm[pq_idxs, pq_idxs].imag()

        logger.debug("J12 =\n%s" % J12)
        logger.debug("J22 =\n%s" % J22)

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

        JX1 = sparse([J11, J21])
        JX2 = sparse([J12, J22])
        J = sparse([JX1.T, JX2.T]).T
        logger.debug("J =\n%s" % J)

        return J

    #--------------------------------------------------------------------------
    #  Evaluate F(x):
    #--------------------------------------------------------------------------

    def _evaluate_function(self):
        """ Evaluates F(x).
        """
        # MATPOWER:
        #   mis = V .* conj(Ybus * V) - Sbus;
        v = self.v
        mismatch = mul(v, conj(self.Y * v)) - self.s_surplus

        real = mismatch[self.pvpq_idxs].real()
        imag = mismatch[self.pq_idxs].imag()

        self.f = f = matrix([real, imag])

        return f

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        F = self.f

        normF = max(abs(F))

        if normF < self.tolerance:
            self.converged = converged = True
        else:
            self.converged = converged = False
#            logger.info("Difference: %.3f" % normF-self.tolerance)

        return converged

#------------------------------------------------------------------------------
#  "FastDecoupledPFRoutine" class:
#------------------------------------------------------------------------------

class FastDecoupledPFRoutine(_ACPFRoutine):
    """ Solves the power flow using fast decoupled method.
    """
    # Sparse FDPF matrix B prime.
    Bp = None

    # Sparse FDPF matrix B double prime.
    Bpp = None

    # Use XB or BX method?
    method = "XB"

    p = None

    q = None

    #--------------------------------------------------------------------------
    #  Solve power flow using Fast Decoupled method:
    #--------------------------------------------------------------------------

    def __call__(self, network):
        """ Solves the AC power flow for the referenced network using fast
            decoupled method.  Returns the final complex voltages, a flag which
            indicates whether it converged or not, and the number of iterations
            performed.
        """
        self.network = network

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

        am = AdmittanceMatrix(self.network, bus_shunts=False,
            line_shunts=False, taps=False, line_resistance=r_line)

        self.Bp = Bp = -am.Y.imag()

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

        am = AdmittanceMatrix(self.network, line_resistance=r_line,
            phase_shift=False)

        self.Bp = Bpp = -am.Y.imag()

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
