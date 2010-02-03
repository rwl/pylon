#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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
        Ray Zimmerman, "runpf.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 4.0b1, Dec 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from math import pi
from time import time

from numpy import angle, pi

from cvxopt import matrix, sparse, exp, mul, div, umfpack, cholmod
#from cvxopt.lapack import getrf
from cvxopt.umfpack import symbolic, numeric
#import cvxopt.blas

from pylon.util import conj
from pylon.case import PQ, PV, REFERENCE

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "_ACPF" class:
#------------------------------------------------------------------------------

class _ACPF(object):
    """ Defines a base class for AC power flow solvers.

        References:
            Ray Zimmerman, "runpf.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 4.0b1, Dec 2009
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, solver="UMFPACK", qlimit=False, tolerance=1e-08,
                 iter_max=10):
        """ Initialises a new ACPF instance.
        """
        # Solved case.
        self.case = case

        # Solver for sparse linear equations: 'UMFPACK' and 'CHOLMOD'
        self.solver = solver

        # Enforce Q limits on generators.
        self.qlimit = qlimit

        # Convergence tolerance.
        self.tolerance = tolerance

        # Maximum number of iterations.
        self.iter_max = iter_max

    #--------------------------------------------------------------------------
    #  "_ACPF" interface:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Override this method in subclasses.
        """
        # Zero result attributes.
        self.case.reset()

        # Retrieve the contents of the case.
        b, l, g, nb, nl, ng, base_mva = self._unpack_case(self.case)

        refs, pq, pv, pvpq = self._index_buses(b)

        if len(refs) != 1:
            logger.error("Swing bus required for DCPF.")
            return {"converged": False}

        # Start the clock.
        t0 = time()

        # Build the vector of initial complex bus voltages.
        V0 = self._initial_voltage(b, g)

        # Save index and angle of original reference bus.
#        if self.qlimit:
#            ref0 = ref
#            Varef0 = b[ref0].Va
#            # List of buses at Q limits.
#            limits = []
#            # Qg of generators at Q limits.
#            fixedQg = matrix(0.0, (g.size[0], 1))

        repeat = True
        while repeat:
            # Build admittance matrices.
            Ybus, Yf, Yt = self.case.Y

            # Compute complex bus power injections (generation - load).
            Sbus = self.case.Sbus

            # Run the power flow.
            V, success, iterations = self._run_power_flow(Ybus, Sbus, V0)

            # Update case with solution.
            self.case.pf_solution(Ybus, Yf, Yt, V)

            # Enforce generator Q limits.
            if self.qlimit:
                repeat = False
            else:
                repeat = False

        elapsed = time() - t0

        return {"success": success, "elapsed": elapsed,
                "iterations": iterations}


    def _unpack_case(self, case):
        """ Returns the contents of the case to be used in the OPF.
        """
        base_mva = self.case.base_mva
        b = self.case.connected_buses
        l = self.case.online_branches
        g = self.case.online_generators
        nb = len(b)
        nl = len(l)
        ng = len(g)

        return b, l, g, nb, nl, ng, base_mva


    def _index_buses(self, buses):
        """ Set up indexing for updating v.
        """
        refs = matrix([i for i,b in enumerate(buses) if b.type == REFERENCE])
        pv = matrix([i for i,b in enumerate(buses) if b.type == PV])
        pq = matrix([i for i,b in enumerate(buses) if b.type == PQ])
        pvpq = matrix([pv, pq])

        return refs, pq, pv, pvpq


    def _initial_voltage(self, buses, generators):
        """ Returns the initial vector of complex bus voltages.

            The bus voltage vector contains the set point for generator
            (including ref bus) buses, and the reference angle of the swing
            bus, as well as an initial guess for remaining magnitudes and
            angles.
        """
        Vm = matrix([bus.v_magnitude_guess for bus in buses])

        # Initial bus voltage angles in radians.
        Va = matrix([bus.v_angle_guess * (pi / 180.0) for bus in buses])

        V = mul(Vm, exp(1j * Va))

        # Get generator set points.
        for i, g in enumerate(generators):
            #   V0(gbus) = gen(on, VG) ./ abs(V0(gbus)).* V0(gbus);
            #            Vg
            #   V0 = ---------
            #        |V0| . V0
            V[buses.index(g.bus)] = g.v_magnitude / abs(V[i]) * V[i]
#            V[buses.index(g.bus)] = g.v_magnitude

        return V


    def _run_power_flow(self, Ybus, Sbus, V0):
        """ Override this method in subclasses.
        """
        raise NotImplementedError

#------------------------------------------------------------------------------
#  "NewtonRaphson" class:
#------------------------------------------------------------------------------

class NewtonRaphson(_ACPF):
    """ Solves the power flow using full Newton's method.

        References:
            Ray Zimmerman, "newtonpf.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 4.0b1, Dec 2009
    """

    def _run_power_flow(self, Ybus, Sbus, V, pv, pq, pvpq):
        """ Solves the power flow using a full Newton's method.
        """
        Va = angle(V)
        Vm = abs(V)

        # Set up indexing for updating V.
#        npv = len(pv)
#        npq = len(pq)
#        j0, j1 = 0,  npv
#        j2, j3 = j1 + 1, j1 + npq
#        j4, j5 = j3 + 1, j3 + npq

        # Initial evaluation of F(x0)...
        F = self._evaluate_function(V)
        # ...and convergency check.
        converged = self._check_convergence(F)

        # Perform Newton iterations.
        i = 0
        while (not converged) and (i < self.iter_max):
            V, Vm, Va = self._one_iteration(F, Ybus, V, Vm, Va, pv, pq, pvpq)
            F = self._evaluate_function(V)
            converged = self._check_convergence(F)
            i += 1

        return V, converged, i


    def _one_iteration(self, F, Ybus, V, Vm, Va, pv, pq, pvpq):
        """ Performs one Newton iteration.
        """
        J = self._build_jacobian(Ybus, V, pv, pq, pvpq)

        if self.solver == "UMFPACK":
            umfpack.linsolve(J, F)
        elif self.solver == "CHOLMOD":
            cholmod.linsolve(J, F)
        else:
            raise ValueError

        # Update step.
        dx = -1 * F

        # Update voltage vector.
        npv = len(pv)
        npq = len(pq)
        if pv:
            Va[pv] = Va[pv] + dx[range(npv)]
        if pq:
            Va[pq] = Va[pq] + dx[range(npv, npv + npq)]
            Vm[pq] = Vm[pq] + dx[range(npv + npq, npv + npq + npq)]

        V = mul(Vm, exp(1j * Va))

        # Avoid wrapped round negative Vm.
        Vm = abs(V)
        Va = matrix(angle(Vm))

        return V, Vm, Va

    #--------------------------------------------------------------------------
    #  Evaluate Jacobian:
    #--------------------------------------------------------------------------

    def _build_jacobian(self, Ybus, V, pv, pq, pvpq):
        """ Returns the Jacobian matrix.
        """
        dS_dVm, dS_dVa = self.case.dSbus_dV(Ybus, V)

        J11 = dS_dVa[pvpq, pvpq].real()
        J12 = dS_dVm[pvpq, pq].real()
        J21 = dS_dVa[pq, pvpq].imag()
        J22 = dS_dVm[pq, pq].imag()
#        J1 = sparse([J11, J21])
#        J2 = sparse([J12, J22])
#        J = sparse([[J1], [J2]])
        J = sparse([[J11, J21], [J12, J22]])

        return J

    #--------------------------------------------------------------------------
    #  Evaluate F(x):
    #--------------------------------------------------------------------------

    def _evaluate_function(self, Ybus, V, Sbus, pv, pq):
        """ Evaluates F(x).
        """
        mis = mul(V, conj(Ybus * V)) - Sbus

        F = matrix([mis[pv].real(), mis[pq].real(), mis[pq].imag()])

        return F

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self, F):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        normF = max(abs(F))

        if normF < self.tolerance:
            converged = True
        else:
            converged = False
            logger.info("Difference: %.3f" % normF - self.tolerance)

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
