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

""" Defines solvers for AC power flow.

    References:
        Ray Zimmerman, "acpf.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import math
import logging
import numpy
from time import time

from cvxopt import matrix, spmatrix, sparse, exp, mul, div, umfpack, cholmod
#from cvxopt.lapack import getrf
from cvxopt.umfpack import symbolic, numeric
#import cvxopt.blas

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
    """ Defines a base class for AC power flow solvers.

        References:
            Ray Zimmerman, "acpf.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, solver="UMFPACK", tolerance=1e-08, iter_max=10):
        """ Initialises a new ACPF instance.
        """
        # CVXOPT offers interfaces to two libraries for solving sets of sparse
        # linear equations: 'UMFPACK' and 'CHOLMOD' (default: 'UMFPACK')
        self.solver = solver

        # Convergence tolerance.
        self.tolerance = tolerance

        # Maximum number of iterations.
        self.iter_max = iter_max

        # Solved case.
        self.case = case

        # Vector of bus voltages.
        self.v = None

        # Complex bus power injections.
        self.s_surplus = None

        # Flag indicating if the solution converged:
        self.converged = False

        # Bus indexes for updating v.
        self.pv_idx = None
        self.pq_idx = None
        self.pvpq_idx = None
        self.ref_idx = -1

    #--------------------------------------------------------------------------
    #  "_ACPF" interface:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Override this method in subclasses.
        """
        # Build the vector of initial complex bus voltages.
        self._build_initial_voltage_vector()

        # Build the vector of complex bus power injections.
        self._build_power_injection_vector()

        # Index the buses for updating the voltage vector.
        self._index_buses()

    #--------------------------------------------------------------------------
    #  Make vector of initial node voltages:
    #--------------------------------------------------------------------------

    def _build_initial_voltage_vector(self):
        """ Returns the initial vector of complex bus voltages.

            The bus voltage vector contains the set point for generator
            (including ref bus) buses, and the reference angle of the swing
            bus, as well as an initial guess for remaining magnitudes and
            angles.
        """
        buses = self.case.connected_buses

        v_magnitude = matrix([bus.v_magnitude_guess for bus in buses])

        # Initial bus voltage angles in radians.
        v_angle = matrix([bus.v_angle_guess * (pi / 180.0) for bus in buses])

        v_guess = self.v = mul(v_magnitude, exp(j * v_angle))

        # Get generator set points.
        for g in self.case.generators:
            #   V0(gbus) = gen(on, VG) ./ abs(V0(gbus)).* V0(gbus);
            #            Vg
            #   V0 = ---------
            #        |V0| . V0
#            v = mul(abs(v_guess[i]), v_guess[i])
#            v_guess[i] = div(g.v_magnitude, v)
#            v = abs(v_guess[i]) * v_guess[i]
#            v_guess[i] = g.v_magnitude / v
            v_guess[buses.index(g.bus)] = g.v_magnitude

        return v_guess

    #--------------------------------------------------------------------------
    #  Make vector of apparent power injected at each bus:
    #--------------------------------------------------------------------------

    def _build_power_injection_vector(self):
        """ Returns the vector of complex bus power injections (gen - load).
        """
        case = self.case
        buses = self.case.connected_buses

        self.s_surplus = matrix([complex(case.p_surplus(b) / case.base_mva,
                                         case.q_surplus(b) / case.base_mva)
                                 for b in buses], tc="z")
        return self.s_surplus

    #--------------------------------------------------------------------------
    #  Index buses for updating v:
    #--------------------------------------------------------------------------

    def _index_buses(self):
        """ Set up indexing for updating v.
        """
        buses = self.case.connected_buses

        pv_idx = self.pv_idx = matrix([i for i,b in enumerate(buses)
                                       if b.type == "PV"])
        pq_idx = self.pq_idx = matrix([i for i,b in enumerate(buses)
                                       if b.type == "PQ"])

        pvpq_idx = self.pvpq_idx = matrix([self.pv_idx, self.pq_idx])

        for ref_idx, bus in enumerate(buses):
            if bus.type == "ref":
                self.ref_idx = ref_idx
                break
        else:
            logger.error("Swing bus required for DCPF.")
            ref_idx = self.ref_idx = -1

        return ref_idx, pv_idx, pq_idx, pvpq_idx

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

    def __init__(self, case, solver="UMFPACK", tolerance=1e-08, iter_max=10):
        """ Initialises a new ACPF instance.
        """
        super(NewtonRaphson, self).__init__(case, solver, tolerance, iter_max)

        # Sparse admittance matrix.
        self.Y = None

        # Sparse Jacobian matrix (updated each iteration).
        self.J = None

        # Function of non-linear differential algebraic equations.
        self.f = None

    #--------------------------------------------------------------------------
    #  Solve power flow using full Newton's method:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves the AC power flow using full Newton's method.
        """
        t0 = time()
        super(NewtonRaphson, self).solve()

        logger.info("Performing AC power flow using Newton-Raphson method.")

        self._build_admittance_matrix()

        self.converged = False
        # Initial evaluation of f(x0)...
        f0 = self._evaluate_function(self.v)
        # ...and convergency check.
        self.converged = self._check_convergence(f0)

        # Perform Newton iterations.
        iter = self._iterate()

        if self.converged:
            logger.info("AC power flow converged in %d iteration(s)." % iter)
            logger.info("AC power flow completed in %.3fs" % (time() - t0))
        else:
            logger.info("ACPF failed to converge in %d iteration(s)." % iter)

    #--------------------------------------------------------------------------
    #  Build admittance matrix:
    #--------------------------------------------------------------------------

    def _build_admittance_matrix(self):
        """ Returns the admittance matrix for the given case.
        """
        self.Y, _, _ = self.case.Y

        return self.Y

    #--------------------------------------------------------------------------
    #  Newton iterations:
    #--------------------------------------------------------------------------

    def _iterate(self):
        """ Performs Newton iterations.
        """
        iter = 0
        while (not self.converged) and (iter < self.iter_max):
            self._one_iteration()
            f = self._evaluate_function(self.v)
            self._check_convergence(f)
            iter += 1
        return iter


    def _one_iteration(self):
        """ Performs one Newton iteration.
        """
        J = self._build_jacobian()
        f = self.f

        if self.solver == "UMFPACK":
            umfpack.linsolve(J, f)
        elif self.solver == "CHOLMOD":
            cholmod.linsolve(J, f)
        else:
            raise ValueError

        v_angle = matrix(numpy.angle(self.v))
        v_magnitude = abs(self.v)

        npv = len(self.pv_idx)
        npq = len(self.pq_idx)

        dx = -1 * f # Update step.

        # Update voltage vector.
        if self.pv_idx:
            v_angle[self.pv_idx] += dx[range(npv)]

        if self.pq_idx:
            v_angle[self.pq_idx] += dx[range(npv, npv + npq)]
            v_magnitude[self.pq_idx] += dx[range(npv + npq, npv + npq + npq)]

        v = self.v = mul(v_magnitude, exp(j * v_angle))

        # Avoid wrapped round negative Vm
#        Vm = abs(voltage)
#        Va = numpy.angle(voltage)

        return v

    #--------------------------------------------------------------------------
    #  Evaluate Jacobian:
    #--------------------------------------------------------------------------

    def _build_jacobian(self):
        """ Returns the Jacobian matrix.
        """
        dS_dVm, dS_dVa = self.case.dSbus_dV(self.Y, self.v)

        J11 = dS_dVa[self.pvpq_idx, self.pvpq_idx].real()
        J12 = dS_dVm[self.pvpq_idx, self.pq_idx].real()
        J21 = dS_dVa[self.pq_idx, self.pvpq_idx].imag()
        J22 = dS_dVm[self.pq_idx, self.pq_idx].imag()

        J1 = sparse([J11, J21])
        J2 = sparse([J12, J22])

        J = self.J = sparse([J1.T, J2.T]).T

        return J

    #--------------------------------------------------------------------------
    #  Evaluate F(x):
    #--------------------------------------------------------------------------

    def _evaluate_function(self, v):
        """ Evaluates F(x).
        """
        mismatch = mul(v, conj(self.Y * v)) - self.s_surplus

        real = mismatch[self.pvpq_idx].real()
        imag = mismatch[self.pq_idx].imag()

        f = self.f = matrix([real, imag])

        return f

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self, f):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        normf = max(abs(f))

        if normf < self.tolerance:
            converged = self.converged = True
        else:
            converged = self.converged = False
#            logger.info("Difference: %.3f" % normf - self.tolerance)

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

    def __init__(self, case, tolerance=1e-08, iter_max=10, method="XB"):
        """ Initialises a new ACPF instance.
        """
        super(_ACPF, self).__init__(case, tolerance, iter_max)

        # Use XB or BX method?
        self.method = method
        # Sparse FDPF matrix B prime.
        self.Bp = None
        # Sparse FDPF matrix B double prime.
        self.Bpp = None

        self.p = None
        self.q = None

    #--------------------------------------------------------------------------
    #  Solve power flow using Fast Decoupled method:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves the AC power flow for the referenced case using fast
            decoupled method.  Returns the final complex voltages, a flag which
            indicates whether it converged or not, and the number of iterations
            performed.
        """
        logger.info("Performing Fast Decoupled AC power flow.")

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

        Y, _, _ = self.case.get_admittance_matrix(bus_shunts=False,
            line_shunts=False, tap_positions=False, line_resistance=r_line)

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

        Y, _, _ = self.case.get_admittance_matrix(line_resistance=r_line,
                                                  phase_shift=False)

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
