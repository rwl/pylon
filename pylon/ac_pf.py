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

""" Defines solvers for AC power flow [1].

    [1] Ray Zimmerman, "runpf.m", MATPOWER, PSERC Cornell,
    http://www.pserc.cornell.edu/matpower/, version 4.0b1, Dec 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from time import time

from numpy import array, angle, pi, exp, linalg, multiply, conj, r_, Inf

from scipy.sparse import hstack, vstack
from scipy.sparse.linalg import spsolve, splu

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
#  Exceptions:
#------------------------------------------------------------------------------

class SlackBusError(Exception):
    """ No single slack bus error. """

#------------------------------------------------------------------------------
#  "_ACPF" class:
#------------------------------------------------------------------------------

class _ACPF(object):
    """ Defines a base class for AC power flow solvers [1].

        [1] Ray Zimmerman, "runpf.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 4.0b1, Dec 2009
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, qlimit=False, tolerance=1e-08,
                 iter_max=10, verbose=True):
        """ Initialises a new ACPF instance.
        """
        # Solved case.
        self.case = case

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

    def solve(self):
        """ Override this method in subclasses.
        """
        # Zero result attributes.
        self.case.reset()

        # Retrieve the contents of the case.
        b, l, g, _, _, _, _ = self._unpack_case(self.case)

        # Update bus indexes.
        self.case.index_buses(b)

        # Index buses accoding to type.
        try:
            _, pq, pv, pvpq = self._index_buses(b)
        except SlackBusError:
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
            Ybus, Yf, Yt = self.case.getYbus(b, l)

            # Compute complex bus power injections (generation - load).
            Sbus = self.case.getSbus(b)

            # Run the power flow.
            V, success, i = self._run_power_flow(Ybus, Sbus, V0, pv, pq, pvpq)

            # Update case with solution.
            self.case.pf_solution(Ybus, Yf, Yt, V)

            # Enforce generator Q limits.
            if self.qlimit:
                raise NotImplementedError
            else:
                repeat = False

        elapsed = time() - t0

        return {"success": success, "elapsed": elapsed, "iterations": i, "V":V}


    def _unpack_case(self, case):
        """ Returns the contents of the case to be used in the OPF.
        """
        base_mva = case.base_mva
        b = case.connected_buses
        l = case.online_branches
        g = case.online_generators
        nb = len(b)
        nl = len(l)
        ng = len(g)

        return b, l, g, nb, nl, ng, base_mva


    def _index_buses(self, buses):
        """ Set up indexing for updating v.
        """
        refs = [bus._i for bus in buses if bus.type == REFERENCE]
        if len(refs) != 1:
            raise SlackBusError
        pv = [bus._i for bus in buses if bus.type == PV]
        pq = [bus._i for bus in buses if bus.type == PQ]
        pvpq = pv + pq

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
            #            Vg
            #   V0 = ---------
            #        |V0| . V0
            V[g.bus._i] = g.v_magnitude / abs(V[i]) * V[i]

        return V


    def _run_power_flow(self, Ybus, Sbus, V0):
        """ Override this method in subclasses.
        """
        raise NotImplementedError

#------------------------------------------------------------------------------
#  "NewtonPF" class:
#------------------------------------------------------------------------------

class NewtonPF(_ACPF):
    """ Solves the power flow using full Newton's method [2].

        [2] Ray Zimmerman, "newtonpf.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 4.0b1, Dec 2009
    """

    def _run_power_flow(self, Ybus, Sbus, V, pv, pq, pvpq, **kw_args):
        """ Solves the power flow using a full Newton's method.
        """
        Va = angle(V)
        Vm = abs(V)

        # Initial evaluation of F(x0)...
        F = self._evaluate_function(Ybus, V, Sbus, pv, pq)
        # ...and convergency check.
        converged = self._check_convergence(F)

        # Perform Newton iterations.
        i = 0
        while (not converged) and (i < self.iter_max):
            V, Vm, Va = self._one_iteration(F, Ybus, V, Vm, Va, pv, pq, pvpq)
            F = self._evaluate_function(Ybus, V, Sbus, pv, pq)
            converged = self._check_convergence(F)
            i += 1

        return V, converged, i


    def _one_iteration(self, F, Ybus, V, Vm, Va, pv, pq, pvpq):
        """ Performs one Newton iteration.
        """
        J = self._build_jacobian(Ybus, V, pv, pq, pvpq)

        # Update step.
        dx = -1 * spsolve(J, F)
#        dx = -1 * linalg.lstsq(J.todense(), F)[0]

        # Update voltage vector.
        npv = len(pv)
        npq = len(pq)
        if npv > 0:
            Va[pv] = Va[pv] + dx[range(npv)]
        if npq > 0:
            Va[pq] = Va[pq] + dx[range(npv, npv + npq)]
            Vm[pq] = Vm[pq] + dx[range(npv + npq, npv + npq + npq)]

        V = Vm * exp(1j * Va)
        Vm = abs(V) # Avoid wrapped round negative Vm.
        Va = angle(V)

        return V, Vm, Va

    #--------------------------------------------------------------------------
    #  Evaluate F(x):
    #--------------------------------------------------------------------------

    def _evaluate_function(self, Ybus, V, Sbus, pv, pq):
        """ Evaluates F(x).
        """
        mis = multiply(V, conj(Ybus * V)) - Sbus

        F = r_[mis[pv].real, mis[pq].real, mis[pq].imag]

        return F

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self, F):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        normF = linalg.norm(F, Inf)

        if normF < self.tolerance:
            converged = True
        else:
            converged = False
            if self.verbose:
                logger.info("Difference: %.3f" % (normF - self.tolerance))

        return converged

    #--------------------------------------------------------------------------
    #  Evaluate Jacobian:
    #--------------------------------------------------------------------------

    def _build_jacobian(self, Ybus, V, pv, pq, pvpq):
        """ Returns the Jacobian matrix.
        """
        pq_col = [[i] for i in pq]
        pvpq_col = [[i] for i in pvpq]

        dS_dVm, dS_dVa = self.case.dSbus_dV(Ybus, V)

        J11 = dS_dVa[pvpq_col, pvpq].real

        J12 = dS_dVm[pvpq_col, pq].real
        J21 = dS_dVa[pq_col, pvpq].imag
        J22 = dS_dVm[pq_col, pq].imag

        J = vstack([
            hstack([J11, J12]),
            hstack([J21, J22])
        ], format="csr")

        return J

#------------------------------------------------------------------------------
#  "FastDecoupledPF" class:
#------------------------------------------------------------------------------

class FastDecoupledPF(_ACPF):
    """ Solves the power flow using fast decoupled method [3].

        [3] Ray Zimmerman, "fdpf.m", MATPOWER, PSERC Cornell, version 4.0b1,
        http://www.pserc.cornell.edu/matpower/, December 2009
    """
    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, qlimit=False, tolerance=1e-08, iter_max=20,
                 verbose=True, method=XB):
        """ Initialises a new ACPF instance.
        """
        super(FastDecoupledPF, self).__init__(case, qlimit, tolerance,
                                              iter_max, verbose)
        # Use XB or BX method?
        self.method = method


    def _run_power_flow(self, Ybus, Sbus, V, pv, pq, pvpq):
        """ Solves the power flow using a full Newton's method.
        """
        i = 0
        Va = angle(V)
        Vm = abs(V)

        # FIXME: Do not repeat build for each Q limit loop.
        Bp, Bpp = self.case.makeB(method=self.method)

        # Evaluate initial mismatch.
        P, Q = self._evaluate_mismatch(Ybus, V, Sbus, pq, pvpq)

        if self.verbose:
            logger.info("iteration     max mismatch (p.u.)  \n")
            logger.info("type   #        P            Q     \n")
            logger.info("---- ----  -----------  -----------\n")

        # Check tolerance.
        converged = self._check_convergence(P, Q, i, "P")

        if converged and self.verbose:
            logger.info("Converged!")

        # Reduce B matrices.
        pq_col = [[k] for k in pq]
        pvpq_col = [[k] for k in pvpq]
        Bp = Bp[pvpq_col, pvpq].tocsc() # splu requires a CSC matrix
        Bpp = Bpp[pq_col, pq].tocsc()

        # Factor B matrices.
        Bp_solver = splu(Bp)
        Bpp_solver = splu(Bpp)
#        L = decomp.lu(Bp.todense())
#        LU, P = decomp.lu_factor(Bp.todense())

        # Perform Newton iterations.
        while (not converged) and (i < self.iter_max):
            i += 1
            # Perform P iteration, update Va.
            V, Vm, Va = self._p_iteration(P, Bp_solver, Vm, Va, pvpq)

            # Evalute mismatch.
            P, Q = self._evaluate_mismatch(Ybus, V, Sbus, pq, pvpq)
            # Check tolerance.
            converged = self._check_convergence(P, Q, i, "P")

            if self.verbose and converged:
                logger.info("Fast-decoupled power flow converged in %d "
                    "P-iterations and %d Q-iterations." % (i, i - 1))
                break

            # Perform Q iteration, update Vm.
            V, Vm, Va = self._q_iteration(Q, Bpp_solver, Vm, Va, pq)

            # Evalute mismatch.
            P, Q = self._evaluate_mismatch(Ybus, V, Sbus, pq, pvpq)
            # Check tolerance.
            converged = self._check_convergence(P, Q, i, "Q")

            if self.verbose and converged:
                logger.info("Fast-decoupled power flow converged in %d "
                    "P-iterations and %d Q-iterations." % (i, i))
                break

        if self.verbose and not converged:
            logger.info("FDPF did not converge in %d iterations." % i)

        return V, converged, i

    #--------------------------------------------------------------------------
    #  Evaluate mismatch:
    #--------------------------------------------------------------------------

    def _evaluate_mismatch(self, Ybus, V, Sbus, pq, pvpq):
        """ Evaluates the mismatch.
        """
        mis = (multiply(V, conj(Ybus * V)) - Sbus) / abs(V)

        P = mis[pvpq].real
        Q = mis[pq].imag

        return P, Q

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self, P, Q, i, type):
        """ Checks if the solution has converged to within the specified
            tolerance.
        """
        normP = linalg.norm(P, Inf)
        normQ = linalg.norm(Q, Inf)

        if self.verbose:
            logger.info("  %s  %3d   %10.3e   %10.3e" % (type,i, normP, normQ))

        if (normP < self.tolerance) and (normQ < self.tolerance):
            converged = True
        else:
            converged = False

        return converged

    #--------------------------------------------------------------------------
    #  P iterations:
    #--------------------------------------------------------------------------

    def _p_iteration(self, P, Bp_solver, Vm, Va, pvpq):
        """ Performs a P iteration, updates Va.
        """
        dVa = -Bp_solver.solve(P)

        # Update voltage.
        Va[pvpq] = Va[pvpq] + dVa
        V = Vm * exp(1j * Va)

        return V, Vm, Va

    #--------------------------------------------------------------------------
    #  Q iterations:
    #--------------------------------------------------------------------------

    def _q_iteration(self, Q, Bpp_solver, Vm, Va, pq):
        """ Performs a Q iteration, updates Vm.
        """
        dVm = -Bpp_solver.solve(Q)

        # Update voltage.
        Vm[pq] = Vm[pq] + dVm
        V = Vm * exp(1j * Va)

        return V, Vm, Va

# EOF -------------------------------------------------------------------------
