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

""" Defines a solver for AC optimal power flow.

    References:
        Ray Zimmerman, "runopf.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging

from scipy import matrix, pi, polyder, polyval, multiply, exp
from scipy.sparse import lil_matrix, csc_matrix, csr_matrix

from pylon.util import conj

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ACOPF" class:
#------------------------------------------------------------------------------

class ACOPF(object):
    """ Solves AC optimal power flow.

        When specified, A, l, u represent additional linear constraints on the
        optimization variables, l <= A*[x; z] <= u. For an explanation of the
        formulation used and instructions for forming the A matrix, type
        'help genform'.

        A generalized cost on all variables can be applied if input arguments
        N, fparm, H and Cw are specified.  First, a linear transformation
        of the optimization variables is defined by means of r = N * [x; z].
        Then, to each element of r a function is applied as encoded in the
        fparm matrix (see MATPOWER manual).  If the resulting vector is now
        named w, then H and Cw define a quadratic cost on
        w: (1/2)*w'*H*w + Cw * w . H and N should be sparse matrices and H
        should also be symmetric.

        Rules for A matrix: If the user specifies an A matrix that has more
        columns than the number of "x" (OPF) variables, then there are extra
        linearly constrained "z" variables.

        References:
            R. Zimmerman, 'runopf.m', MATPOWER, PSERC (Cornell),
            version 3.2, http://www.pserc.cornell.edu/matpower/
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, show_progress=True, max_iterations=100,
                 absolute_tol=1e-7, relative_tol=1e-6, feasibility_tol=1e-7,
                 refinement=1):
        """ Initialises a new ACOPF instance.
        """
        # Turns the output to the screen on or off.
        self.show_progress = show_progress

        # Maximum number of iterations.
        self.max_iterations = max_iterations

        # Absolute accuracy.
        self.absolute_tol = absolute_tol

        # Relative accuracy.
        self.relative_tol = relative_tol

        # Tolerance for feasibility conditions.
        self.feasibility_tol = feasibility_tol

        # Number of iterative refinement steps when solving KKT equations.
        self.refinement = refinement

        # Solved case.
        self.case = case


    def solve(self, case=None):
        """ Solves AC OPF for the given case.
        """
        t0 = time.time()

        # Turn off output to screen.
#        solvers.options["show_progress"] = self.show_progress
#        solvers.options["maxiters"] = self.max_iterations
#        solvers.options["abstol"] = self.absolute_tol
#        solvers.options["reltol"] = self.relative_tol
#        solvers.options["feastol"] = self.feasibility_tol
#        solvers.options["refinement"] = self.refinement

        case = self.case if case is None else case
        assert case is not None

        logger.debug("Solving AC OPF [%s]." % case.name)

        j = 0 + 1j

        base_mva = case.base_mva
        buses = case.connected_buses
        branches = case.online_branches
        generators = case.online_generators
        n_buses = len(case.connected_buses)
        n_branches = len(case.online_branches)
        n_gen = len(case.online_generators)

        # FIXME: Implement piecewise linear cost constraints.
        assert "pwl" not in [g.pcost_model for g in generators]
        cost_model = "poly"

        # The number of non-linear equality constraints.
        n_equality = 2 * n_buses
        # The number of control variables.
        n_control = 2 * n_buses + 2 * n_gen

        # Definition of indexes for the optimisation variable vector.
        # Voltage phase angle.
        ph_base = 0
        ph_end  = ph_base + n_buses - 1;
        # Voltage amplitude.
        v_base  = ph_end + 1
        v_end   = v_base + n_buses - 1
        # Active generation.
        pg_base = v_end + 1
        pg_end  = pg_base + n_gen - 1
        # Reactive generation.
        qg_base = pg_end + 1
        qg_end  = qg_base + n_gen - 1

        # TODO: Definition of indexes for the constraint vector.

#        # Find "generators" that are actually dispatchable loads. Dispatchable
#        # loads are modeled as generators with an added constant power factor
#        # constraint. The power factor is derived from the original value of
#        # Pmin and either Qmin (for inductive loads) or Qmax (for capacitive
#        # loads). If both Qmin and Qmax are zero, this implies a unity power
#        # factor without the need for an additional constraint.
#        vloads = [g for g in generators if g.q_min != 0.0 or g.q_max != 0.0]
#
#        # At least one of the Q limits must be zero (corresponding to
#        # Pmax == 0)
#        if [vl for vl in vloads if vl.q_min != 0.0 and vl.q_max != 0.0]:
#            logger.error("Either q_min or q_max must be equal to zero for "
#                "each dispatchable load.")
#
#        # Initial values of PG and QG must be consistent with specified power
#        # factor.
#        q_lim = matrix(0.0, n_gen)
#
#        for i, g in enumerate(generators):
#            if g in vload:
#                if g.q_min == 0.0:
#                    q_lim[i] = g.q_max
#                if g.q_max == 0.0:
#                    q_lim[i] = g.q_min
#
#        if [l for l in vloads if (abs(l.q) - l.p * q_lim / l.p_min) > 1e-4]:
#            logger.error("For a dispatchable load, PG and QG must be "
#                "consistent with the power factor defined by PMIN and the "
#                "Q limits.")
#
#        # TODO: Implement P-Q capability curve constraints.
#
#        # Branch angle constraints.
#        if OPF_IGNORE_ANG_LIM:
#            n_angle = 0
#        else:
#            ang = [e for e in branches if \
#                   e.angle_min > -360.0 or e.angle_max < 360.0]
#            n_angle = len(ang)
#
#        n_ineq = 2 * n_buses
#        n_control = 2 * n_buses + 2 * n_gen
#
#        if not Au:
#            n_additional = 0
#            Au = spmatrix([], [], [], (n_control, 1))
#            if N:
#                if n.size()[1] != n_control:
#                    logger.error("N matrix must have %d columns." % n_control)
#        else:
#            # Additional linear variables.
#            n_additional = Au.size()[1] - n_control
#            if n_linear < 0:
#                logger.error("A matrix must have at least %d columns." %
#                             n_control)
#
#        n_pwl = len([e for e in branches if e.pcost_model == "pwl"])
#        # Total number of vars of all types.
#        n_var = n_control + n_pwl + n_additional


        def F(x=None, z=None):
            """ Evaluates the objective and nonlinear constraint functions.
            """
            if x is None:
                # Compute initial optimisation variable vector.
                x_va = matrix([bus.v_angle_guess * pi / 180 for bus in buses])
                # FIXME: Initialise V from any present generators.
                x_vm = matrix([bus.v_magnitude_guess for bus in buses])
                x_pg = matrix([g.p / base_mva for g in generators])
                x_qg = matrix([g.q / base_mva for g in generators])

                return n_equality, matrix([x_va, x_vm, x_pg, x_qg])

            # Evaluate objective function -------------------------------------

            p_gen = x[pg_base:pg_end + 1] # Active generation in p.u.
            q_gen = x[qg_base:qg_end + 1] # Reactive generation in p.u.

            for i, g in enumerate(generators):
                g.p = p_gen[i] * base_mva
                g.q = q_gen[i] * base_mva

            # Evaluate the objective function value.
            if cost_model == "poly":
                # FIXME: Implement reactive power costs.
                f0 = sum([g.total_cost(g.p) for g in generators])
            else:
                f0 = 0

            # Evaluate cost gradient ------------------------------------------

            # Partial derivative w.r.t. polynomial cost Pg and Qg.
#            df_dPgQg = [polyval(polyder(g.p_cost), g.p) * base_mva \
#                        for g in generators]
            df_dPgQg = matrix(0.0, (n_gen * 2, 1))

            for i, g in enumerate(generators):
                der = polyder( list(g.p_cost) )
                df_dPgQg[i] = polyval(der, g.p) * base_mva

            df0= matrix([matrix(0.0, (v_end, 1)), df_dPgQg])

            # Evaluate nonlinear equality constraints -------------------------

            # Net complex bus power injection vector in p.u.
            s = matrix([case.s_surplus(v) /base_mva for v in buses])

            # Bus voltage vector.
            v_angle = x[ph_base:ph_end + 1]
            v_magnitude = x[v_base:v_end]
#            Va0r = Va0 * pi / 180 #convert to radians
            v = multiply(v_magnitude, exp(j * v_angle)) #element-wise product

            # Evaluate the power flow equations.
            Y, Yfrom, Yto = case.Y
            mismatch = multiply(v, conj(Y * v)) - s

            # Evaluate power balance equality constraint function values.
            fk_eq = matrix([mismatch.real(), mismatch.imag()])

            # Evaluate nonlinear inequality constraints -----------------------

            # Branch power flow limit inequality constraint function values.
            from_idxs = matrix([buses.index(e.from_bus) for e in branches])
            to_idxs = matrix([buses.index(e.to_bus) for e in branches])
            # Complex power in p.u. injected at the from bus.
            s_from = multiply(v[from_idxs], conj(Yfrom, v))
            # Complex power in p.u. injected at the to bus.
            s_to = multiply(v[to_idxs], conj(Yto, v))

            # Apparent power flow limit in MVA, |S|.
            rate_a = matrix([e.rate_a for e in branches])

            # FIXME: Implement active power and current magnitude limits.
            fk_ieq = matrix([abs(s_from) - rate_a, abs(s_to) - rate_a])

            # Evaluate partial derivatives of constraints ---------------------

            # Partial derivative of injected bus power
            dS_dVm, dS_dVa = case.dSbus_dV(Y, v) # w.r.t voltage
            pv_idxs = matrix([buses.index(bus) for bus in buses])
            dS_dPg = spmatrix(-1, pv_idxs, range(n_gen)) # w.r.t Pg
            dS_dQg = spmatrix(-j, pv_idxs, range(n_gen)) # w.r.t Qg

            # Transposed Jacobian of the power balance equality constraints.
            dfk_eq = sparse([
                sparse([
                    dS_dVa.real(), dS_dVm.real(), dS_dPg.real(), dS_dQg.real()
                ]),
                sparse([
                    dS_dVa.imag(), dS_dVm.imag(), dS_dPg.imag(), dS_dQg.imag()
                ])
            ]).T

            # Partial derivative of branch power flow w.r.t voltage.
            dSf_dVa, dSt_dVa, dSf_dVm, dSt_dVm, s_from, s_to = \
                case.dSbr_dV(branches, Yfrom, Yto, v)

            # Magnitude of complex power flow.
            df_dVa, dt_dVa, df_dVm, dt_dVm = \
                case.dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, s_from, s_to)

            # Transposed Jacobian of branch power flow inequality constraints.
            dfk_ieq = matrix([matrix([df_dVa, df_dVm]),
                              matrix([dt_dVa, dt_dVm])]).T

            f = matrix([f0, fk_eq, fk_ieq])
            df = matrix([df0, dfk_eq, dfk_ieq])

            if z is None:
                return f, df

            # Evaluate cost Hessian -------------------------------------------

            d2f_d2Pg = spmatrix([], [], [], (n_gen, 1))
            d2f_d2Qg = spmatrix([], [], [], (n_gen, 1))
            for i, g in enumerate(generators):
                der = polyder(list(g.p_cost))
                # TODO: Implement reactive power costs.
                d2f_d2Pg[i] = polyval(der, g.p) * base_mva

            i = matrix(range(pg_base, qg_end + 1)).T
            H = spmatrix(matrix([d2f_d2Pg, d2f_d2Qg]), i, i)

            return f, df, H


        # cp(F, G=None, h=None, dims=None, A=None, b=None, kktsolver=None)
        #
        #     minimize    f0(x)
        #     subject to  fk(x) <= 0, k = 1, ..., mnl
        #                 G*x   <= h
        #                 A*x   =  b.
        solution = solvers.cp(F)

        t_elapsed = time.time() - t0

        if solution['status'] == 'optimal':
            logger.info("AC OPF completed in %.3fs." % t_elapsed)
            return True
        else:
            logger.error("Non-convergent AC OPF.")
            return False


#    def _build_additional_linear_constraints(self):
#        """ A, l, u represent additional linear constraints on the
#            optimization variables.
#        """
#        if Au is None:
#            Au = sparse([], [], [], (0, 0))
#            l_bu = matrix([0])
#            u_bu = matrix([0])
#
#        # Piecewise linear convex costs
#        A_y = spmatrix([], [], [], (0, 0))
#        b_y = matrix([0])
#
#        # Branch angle difference limits
#        A_ang = spmatrix([], [], [], (0, 0))
#        l_ang = matrix([0])
#        u_ang = matrix([0])
#
#        # Despatchable loads
#        A_vl = spmatrix([], [], [], (0, 0))
#        l_vl = matrix([0])
#        u_vl = matrix([0])
#
#        # PQ capability curves
#        A_pqh = spmatrix([], [], [], (0, 0))
#        l_bpqh = matrix([0])
#        u_bpqh = matrix([0])
#
#        A_pql = spmatrix([], [], [], (0, 0))
#        l_bpql = matrix([0])
#        u_bpql = matrix([0])
#
#        # Build linear restriction matrix. Note the ordering.
#        # A, l, u represent additional linear constraints on
#        # the optimisation variables
#        A = sparse([Au, A_pqh, A_pql, A_vl, A_ang])
#        l = matrix([l_bu, l_bpqh, l_bpql, l_vl, l_ang])
#        u = matrix([u_bu, u_bpqh, u_bpql, u_vl, l_ang])

#------------------------------------------------------------------------------
#  "dS_dV" function:
#------------------------------------------------------------------------------

#def dSbus_dV(Y, v):
#    """ Computes the partial derivative of power injection w.r.t. voltage.
#
#        References:
#            Ray Zimmerman, "dSbus_dV.m", MATPOWER, version 3.2,
#            PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
#    """
#    j = 0 + 1j
#    n = len(v)
#    i = Y * v
#
#    diag_v = spdiag(v)
#    diag_i = spdiag(i)
#    diag_vnorm = spdiag(div(v, abs(v))) # Element-wise division.
#
#    ds_dvm = diag_v * conj(Y * diag_vnorm) + conj(diag_i) * diag_vnorm
#    ds_dva = j * diag_v * conj(diag_i - Y * diag_v)
#
#    return ds_dvm, ds_dva
#
##------------------------------------------------------------------------------
##  "dSbr_dV" function:
##------------------------------------------------------------------------------
#
#def dSbr_dV(buses, branches, Y_from, Y_to, v):
#    """ Computes the branch power flow vector and the partial derivative of
#        branch power flow w.r.t voltage.
#
#        References:
#            Ray Zimmerman, "dSbr_dV.m", MATPOWER, version 3.2,
#            PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
#    """
#    j = 0 + 1j
#    n_branches = len(branches)
#    n_buses = len(v)
#
#    from_idxs = matrix([buses.index(e.from_bus) for e in branches])
#    to_idxs = matrix([buses.index(e.to_bus) for e in branches])
#
#    # Compute currents.
#    i_from = Y_from * v
#    i_to = Y_to * v
#
#    # dV/dVm = diag(V./abs(V))
#    v_norm = div(v, abs(v))
#
#    diagVfrom = spdiag(v[from_idxs])
#    diagIfrom = spdiag(i_from)
#    diagVto = spdiag(v[to_idxs])
#    diagIto = spdiag(i_to)
#    diagV = spdiag(v)
#    diagVnorm = spdiag(v_norm)
#
#    # Partial derivative of S w.r.t voltage phase angle.
#    dSf_dVa = j * (conj(diagIfrom) * spmatrix(v[from_idx],
#                                                range(n_branches),
#                                                from_idxs,
#                                                (n_branches, n_buses)) - \
#        diagVfrom * conj(Y_from * diagV))
#
#    dSt_dVa = j * (conj(diagIto) * spmatrix(v[to_idx],
#                                                range(n_branches),
#                                                to_idxs,
#                                                (n_branches, n_buses)) - \
#        diagVto * conj(Y_to * diagV))
#
#    # Partial derivative of S w.r.t. voltage amplitude.
#    dSf_dVm = diagVfrom * conj(Y_from * diagVnorm) + conj(diagIfrom) * \
#        spmatrix(v_norm[from_idxs], range(n_branches),
#            from_idxs, (n_branches, n_buses))
#
#    dSt_dVm = diagVto * conj(Y_to * diagVnorm) + conj(diagIto) * \
#        spmatrix(v_norm[to_idxs], range(n_branches),
#            to_idxs, (n_branches, n_buses))
#
#    # Compute power flow vectors.
#    s_from = mul(v[from_idxs], conj(i_from))
#    s_to = mul(v[to_idxs], conj(i_to))
#
#    return dSf_dVa, dSt_dVa, dSf_dVm, dSt_dVm, s_from, s_to
#
##------------------------------------------------------------------------------
##  "dAbr_dV" function:
##------------------------------------------------------------------------------
#
#def dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, s_from, s_to):
#    """ Computes the partial derivatives of apparent power flow w.r.t voltage.
#
#        References:
#            Ray Zimmerman, "dAbr_dV.m", MATPOWER, version 3.2,
#            PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
#    """
##    n_branches = len(s_from)
#
#    # Compute apparent powers.
#    a_from = abs(s_from)
#    a_to = abs(s_to)
#
#    # Compute partial derivative of apparent power w.r.t active and
#    # reactive power flows.  Partial derivative must equal 1 for lines with
#    # zero flow to avoid division by zero errors (1 comes from L'Hopital).
#    def zero2one(x):
#        if x != 0: return x
#        else: return 1.0
#
#    p_from = div(s_from.real(), map(zero2one, a_from))
#    q_from = div(s_to.imag(), map(zero2one, a_from))
#    p_to = div(s_to.real(), map(zero2one, a_to))
#    q_to = div(s_to.imag(), map(zero2one, a_to))
#
#    dAf_dPf = spdiag(p_from)
#    dAf_dQf = spdiag(q_from)
#    dAt_dPt = spdiag(p_to)
#    dAt_dQt = spdiag(q_to)
#
#    # Partial derivative of apparent power magnitude w.r.t voltage phase angle.
#    dAf_dVa = dAf_dPf * dSf_dVa.real() + dAf_dQf * dSf_dVa.imag()
#    dAt_dVa = dAt_dPt * dSt_dVa.real() + dAt_dQt * dSt_dVa.imag()
#    # Partial derivative of apparent power magnitude w.r.t. voltage amplitude.
#    dAf_dVm = dAf_dPf * dSf_dVm.real() + dAf_dQf * dSf_dVm.imag()
#    dAt_dVm = dAt_dPt * dSt_dVm.real() + dAt_dQt * dSt_dVm.imag()
#
#    return dAf_dVa, dAt_dVa, dAf_dVm, dAt_dVm

# EOF -------------------------------------------------------------------------
