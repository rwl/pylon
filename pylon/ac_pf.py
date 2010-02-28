#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

from numpy import matrix, array, angle, pi, exp, linalg, multiply, conj

from pylon.case import PQ, PV, REFERENCE

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

BX = "BX"
XB = "XB"

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
                 iter_max=10, verbose=True):
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

        # Print progress information.
        self.verbose = verbose

    #--------------------------------------------------------------------------
    #  "_ACPF" interface:
    #--------------------------------------------------------------------------

    def solve(self, **kw_args):
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
            V, success, i = self._run_power_flow(Ybus, Sbus, V0, **kw_args)

            # Update case with solution.
            self.case.pf_solution(Ybus, Yf, Yt, V)

            # Enforce generator Q limits.
            if self.qlimit:
                repeat = False
            else:
                repeat = False

        elapsed = time() - t0

        return {"success": success, "elapsed": elapsed, "iterations": i}


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
        refs = array([i for i,b in enumerate(buses) if b.type == REFERENCE])
        pv = array([i for i,b in enumerate(buses) if b.type == PV])
        pq = array([i for i,b in enumerate(buses) if b.type == PQ])
        pvpq = array([pv, pq])

        return refs, pq, pv, pvpq


    def _initial_voltage(self, buses, generators):
        """ Returns the initial vector of complex bus voltages.

            The bus voltage vector contains the set point for generator
            (including ref bus) buses, and the reference angle of the swing
            bus, as well as an initial guess for remaining magnitudes and
            angles.
        """
        Vm = array([bus.v_magnitude_guess for bus in buses])

        # Initial bus voltage angles in radians.
        Va = array([bus.v_angle_guess * (pi / 180.0) for bus in buses])

        V = Vm * exp(1j * Va)

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

    def _run_power_flow(self, Ybus, Sbus, V, pv, pq, pvpq, **kw_args):
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

#        if self.solver == "UMFPACK":
#            umfpack.linsolve(J, F)
#        elif self.solver == "CHOLMOD":
#            cholmod.linsolve(J, F)
#        else:
#            raise ValueError

        linalg.solve(J, F)

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

        V = multiply(Vm, exp(1j * Va))

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
        mis = multiply(V, conj(Ybus * V)) - Sbus

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

    def __init__(self, case, tolerance=1e-08, iter_max=10, method=XB):
        """ Initialises a new ACPF instance.
        """
        super(_ACPF, self).__init__(case, tolerance, iter_max)

        # Use XB or BX method?
        self.method = method


    def _run_power_flow(self, Ybus, Sbus, V, pv, pq, pvpq):
        """ Solves the power flow using a full Newton's method.
        """
        # FIXME: Do not repeat build for each Q limit loop.
        Bp, Bpp = self.case.makeB(self.method)

        i = 0
        Va = angle(V)
        Vm = abs(V)

        # Evaluate initial mismatch.
        P, Q = self._evaluate_mismatch(Ybus, V, Sbus, pq, pvpq)

        if self.verbose:
            logger.info("iteration     max mismatch (p.u.)  \n")
            logger.info("type   #        P            Q     \n")
            logger.info("---- ----  -----------  -----------\n")

        # Check tolerance.
        converged = self._check_convergence(self, i, P, Q)

        if converged and self.verbose:
            logger.info("Converged!")

        # Reduce B matrices.
        Bp = Bp[pvpq, pvpq]
        Bpp = Bpp[pq, pq]

        # Perform Newton iterations.
        while (not converged) and (i < self.iter_max):
            i += 1
            # Perform P iteration, update Va.
            V, Vm, Va = self._p_iteration(P, Q, Ybus, V, Vm, Va, pv, pq, pvpq)

            # Evalute mismatch.
            P, Q = self._evaluate_mismatch(Ybus, V, Sbus, pq, pvpq)
            # Check tolerance.
            converged = self._check_convergence(self, i, P, Q, "P")

            if self.verbose and converged:
                logger.info("Fast-decoupled power flow converged in %d "
                    "P-iterations and %d Q-iterations." % (i, i-1))
                break

            # Perform Q iteration, update Vm.
            V, Vm, Va = self._q_iteration(P, Q, Ybus, V, Vm, Va, pv, pq, pvpq)

            # Evalute mismatch.
            P, Q = self._evaluate_mismatch(Ybus, V, Sbus, pq, pvpq)
            # Check tolerance.
            converged = self._check_convergence(self, i, P, Q, "Q")

            if self.verbose and converged:
                logger.info("Fast-decoupled power flow converged in %d "
                    "P-iterations and %d Q-iterations." % (i, i))
                break

        if self.verbose and not converged:
            logger.info("FDPF did not converge in %d iterations." % i)

    #--------------------------------------------------------------------------
    #  P iterations:
    #--------------------------------------------------------------------------

    def _p_iteration(self, P, Ybus, Bp, Bpp, Sbus, Vm, Va, pq, pvpq):
        """ Performs a P iteration, updates Va.
        """
        # The numeric factorisation is returned as an opaque C object that
        # can be passed on to umfpack.solve().
#        Bps = symbolic(Bp)
#        Bpps = symbolic(Bp)
#        FBp = numeric(Bp, Bps)
#        FBpp = numeric(Bpp, Bpps)

        Pp, Lp, Up = linalg.lu(Bp)
#        LU, P = linalg.lu_factor(Bp)

        # P iteration, update Va.
        # dVa = -( Up \  (Lp \ (Pp * P)));
        # L, U = Sci.linalg.lu(a)
        # LU, P = Sci.linalg.lu_factor(a)
        dVa = linalg.solve(Lp, (Pp * P))

        # Update voltage.
        Va[pvpq] = Va[pvpq] + dVa
        V = multiply(Vm, exp(1j * Va))

        return V, Vm, Va

    #--------------------------------------------------------------------------
    #  Q iterations:
    #--------------------------------------------------------------------------

    def _q_iteration(self, Lpp, Upp, Ppp, Ybus, Bp, Bpp, Sbus, Vm, Va, pq, pvpq):
        """ Performs a Q iteration, updates Vm.
        """
        dVm = None

        # Update voltage.
        Vm[pq] = Vm[pq] + dVm
        V = multiply(Vm, exp(1j * Va))

        return V, Vm


#    def _factor_B_matrices(self):
#        """ Perform symbolic and numeric LU factorisation of Bp and Bpp.
#        """
#        Bp = self.Bp
#        Bpp = self.Bpp
#
#        # The numeric factorisation is returned as an opaque C object that
#        # can be passed on to umfpack.solve().
#        opaqueBp = numeric(Bp, symbolic(Bp))
#        opaqueBpp = numeric(Bpp, symbolic(Bp))

    #--------------------------------------------------------------------------
    #  Evaluate mismatch:
    #--------------------------------------------------------------------------

    def _evaluate_mismatch(self, Ybus, V, Sbus, pq, pvpq):
        """ Evaluates the mismatch.
        """
        mis = multiply(V, conj(Ybus * V)) - Sbus / abs(V)

        P = mis[pvpq].real()
        Q = mis[pq].imag()

        return P, Q

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self, i, P, Q, type):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        normP = max(abs(P))
        normQ = max(abs(Q))

        if self.verbose:
            logger.info("  -  %3d   %10.3e   %10.3e" % (i, normP, normQ))

        if (normP < self.tolerance) and (normQ < self.tolerance):
            converged = True
        else:
            converged = False

        return converged

    #--------------------------------------------------------------------------
    #  Make FDPF matrix B prime:
    #--------------------------------------------------------------------------

#    def _make_B_prime(self):
#        """ Builds the Fast Decoupled Power Flow matrix B prime.
#
#            References:
#            R. Zimmerman, "makeB.m", MATPOWER, PSERC (Cornell),
#            version 1.5, http://www.pserc.cornell.edu/matpower/, July 8, 2005
#
#        """
#        if self.method is "XB":
#            r_line = False
#        else:
#            r_line = True
#
#        Y, _, _ = self.case.get_admittance_matrix(bus_shunts=False,
#            line_shunts=False, tap_positions=False, line_resistance=r_line)
#
#        self.Bp = Bp = -Y.imag()
#
#        return Bp

    #--------------------------------------------------------------------------
    #  Make FDPF matrix B double prime:
    #--------------------------------------------------------------------------

#    def _make_B_double_prime(self):
#        """ Builds the Fast Decoupled Power Flow matrix B double prime.
#
#            References:
#            R. Zimmerman, "makeB.m", MATPOWER, PSERC (Cornell),
#            version 1.5, http://www.pserc.cornell.edu/matpower/, July 8, 2005
#        """
#        if self.method is "BX":
#            r_line = False
#        else:
#            r_line = True
#
#        Y, _, _ = self.case.get_admittance_matrix(line_resistance=r_line,
#                                                  phase_shift=False)
#
#        self.Bp = Bpp = -Y.imag()
#
#        return Bpp

# EOF -------------------------------------------------------------------------
