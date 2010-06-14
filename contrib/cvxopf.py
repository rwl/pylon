#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

""" Defines an OPF solver using CVXOPT [1].

    Note: This module is licensed under GNU GPL version 3 due to the
    CVXOPT import.

    [1] Ray Zimmerman, "mipsopf_solver.m", MATPOWER, PSERC Cornell,
        version 4.0b1, http://www.pserc.cornell.edu/matpower/, Dec 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import polyval, polyder, finfo, pi

from cvxopt import matrix, spmatrix, mul, sparse, exp, solvers, div, spdiag

from pylon.solver import Solver, DCOPFSolver, SFLOW, PFLOW, IFLOW

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

EPS = finfo(float).eps

#------------------------------------------------------------------------------
#  "DCCVXOPTSolver" class:
#------------------------------------------------------------------------------

class DCCVXOPTSolver(DCOPFSolver):
    """ Solves DC optimal power flow using CVXOPT.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, om, opt=None, solver=None):
        """ Initialises the new DCOPF instance.
        """
        super(DCOPFSolver, self).__init__(om, opt)

        # Choice of solver (May be None or "mosek" (or "glpk" for linear
        # formulation)). Specify None to use the Python solver from CVXOPT.
        self.solver = solver

        if opt.has_key("verbose"):
            solvers.options["show_progress"] = opt["verbose"]
        if opt.has_key("max_it"):
            solvers.options["maxiters"] = opt["max_it"]
        if opt.has_key("feastol"):
            solvers.options["feastol"] = opt["feastol"]
        if opt.has_key("gradtol"):
            raise NotImplementedError
        if opt.has_key("comptol"):
            raise NotImplementedError
        if opt.has_key("costtol"):
            raise NotImplementedError
        if opt.has_key("max_red"):
            raise NotImplementedError
        if opt.has_key("step_control"):
            raise NotImplementedError
        if opt.has_key("cost_mult"):
            raise NotImplementedError


    def _run_opf(self, P, q, AA, ll, uu, xmin, xmax, x0, opt):
        """ Solves the either quadratic or linear program.
        """
        AAcvx = tocvx(AA)
        nx = x0.shape[0] # number of variables
        # add var limits to linear constraints
        eyex = spmatrix(1.0, range(nx), range(nx))
        A = sparse([eyex, AAcvx])
        l = matrix([-xmin, ll])
        u = matrix([ xmax, uu])

        Ae, be, Ai, bi = split_linear_constraints(A, l, u)


        if len(P.V) > 0:
            cvx_sol = solvers.qp(P, q, Ai, bi, Ae, be, self.solver, {"x": x0})
        else:
            cvx_sol = solvers.lp(q, Ai, bi, Ae, be, self.solver, {"x": x0})

        return cvx_sol


    def _update_case(self, bs, ln, gn, base_mva, Bf, Pfinj, Va, Pg, lmbda):
        """ Calculates the result attribute values.
        """
        for i, bus in enumerate(bs):
            bus.v_angle = Va[i] * 180.0 / pi

#------------------------------------------------------------------------------
#  "CVXOPTSolver" class:
#------------------------------------------------------------------------------

class CVXOPTSolver(Solver):
    """ Solves AC optimal power flow using convex optimization.
    """

    def __init__(self, om, opt=None, flow_lim=SFLOW):
        """ Initialises a new CVXOPTSolver instance.
        """
        super(CVXOPTSolver, self).__init__(om)

        # Quantity to limit for branch flow constraints ("S", "P" or "I").
        self.flow_lim = flow_lim

        self.opt = {} if opt is None else opt

        if self.opt.has_key("verbose"):
            solvers.options["show_progress"] = self.opt["verbose"]
        if self.opt.has_key("max_it"):
            solvers.options["maxiters"] = self.opt["max_it"]
        if self.opt.has_key("feastol"):
            solvers.options["feastol"] = self.opt["feastol"]
        if self.opt.has_key("gradtol"):
            raise NotImplementedError
        if self.opt.has_key("comptol"):
            raise NotImplementedError
        if self.opt.has_key("costtol"):
            raise NotImplementedError
        if self.opt.has_key("max_red"):
            raise NotImplementedError
        if self.opt.has_key("step_control"):
            raise NotImplementedError
        if self.opt.has_key("cost_mult"):
            raise NotImplementedError


    def solve(self):
        j = 0 + 1j
        case = self.om.case
        base_mva = case.base_mva
        self.opt["cost_mult"] = 1e-4
        # Unpack the OPF model.
        bs, ln, gn, cp = self._unpack_model(self.om)
        # Compute problem dimensions.
        ng = len(gn)
        ipol, ipwl, nb, nl, nw, ny, nxyz = self._dimension_data(bs, ln, gn)
        # The number of non-linear equality constraints.
        neq = 2 * nb
        # The number of control variables.
        nc = 2 * nb + 2 * ng
        # Indexes of constrained lines.
        il = matrix([i for i,l in enumerate(ln) if 0.0 < l.rate_a < 1e10])
        nl2 = len(il)

        # Linear constraints (l <= A*x <= u).
        A, l, u = self.om.linear_constraints()
        if A is None:
            AA = spmatrix([], [], [], (0, self.om.var_N))
        else:
            AA = tocvx(A)
        Ae, be, Ai, bi = split_linear_constraints(AA, matrix(l), matrix(u))

        _, xmin, xmax = self._var_bounds()

        # Select an interior initial point for interior point solver.
        x0 = matrix(self._initial_interior_point(bs, gn, xmin, xmax, ny))

        # Build admittance matrices.
        YYbus, YYf, YYt = case.Y
        Ybus = tocvx(YYbus)
        Yf = tocvx(YYf)
        Yt = tocvx(YYt)

        # Optimisation variables.
        Va = self.om.get_var("Va")
        Vm = self.om.get_var("Vm")
        Pg = self.om.get_var("Pg")
        Qg = self.om.get_var("Qg")

        def F(x=None, z=None):
            """ Evaluates the objective and nonlinear constraint functions.
            """
            if x is None:
                return neq, x0

            # Evaluate objective function -------------------------------------

            Pgen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            Qgen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            xx = matrix([Pgen, Qgen]) * base_mva

            # Evaluate the objective function value.
            if len(ipol) > 0:
                # FIXME: Implement reactive power costs.
                f = sum([g.total_cost(xx[i]) for i, g in enumerate(gn)])
            else:
                f = 0

            # Piecewise linear cost of P and Q.
            if ny:
                y = self.om.get_var("y")
                ccost = spmatrix(matrix(1.0, (ny, 1)),
                                 range(y.i1, y.iN + 1),
                                 matrix(0.0, (ny, 1)), size=(nxyz, 1)).T
                f = f + ccost * x
            else:
                ccost = matrix(0.0, (1, nxyz))
            # TODO: Generalised cost term.

            # Evaluate cost gradient ------------------------------------------

            iPg = range(Pg.i1, Pg.iN + 1)
            iQg = range(Qg.i1, Qg.iN + 1)

            # Polynomial cost of P and Q.
            df_dPgQg = matrix(0.0, (2 * ng, 1))        # w.r.t p.u. Pg and Qg
            for i in ipol:
                df_dPgQg[i] = \
                    base_mva * polyval(polyder(list(gn[i].p_cost)), xx[i])

            df0 = matrix(0.0, (nxyz, 1))
            df0[iPg] = df_dPgQg[:ng]
            df0[iQg] = df_dPgQg[ng:ng + ng]

            # Piecewise linear cost of P and Q.
            df0 = df0 + ccost.T
            # TODO: Generalised cost term.

            # Evaluate cost Hessian -------------------------------------------

            d2f = None

            # Evaluate nonlinear equality constraints -------------------------

            for i, g in enumerate(gn):
                g.p = Pgen[i] * base_mva # active generation in MW
                g.q = Qgen[i] * base_mva # reactive generation in MVAr

            # Rebuild the net complex bus power injection vector in p.u.
            Sbus = matrix(case.getSbus(bs))

            Vang = x[Va.i1:Va.iN + 1]
            Vmag = x[Vm.i1:Vm.iN + 1]
            V = mul(Vmag, exp(1j * Vang))

            # Evaluate the power flow equations.
            mis = mul(V, conj(Ybus * V)) - Sbus

            # Equality constraints (power flow).
            g = matrix([mis.real(),  # active power mismatch for all buses
                        mis.imag()]) # reactive power mismatch for all buses

            # Evaluate nonlinear inequality constraints -----------------------

            # Inequality constraints (branch flow limits).
            # (line constraint is actually on square of limit)
            flow_max = matrix([(l.rate_a / base_mva)**2 for l in ln])
            # FIXME: There must be a more elegant way to do this.
            for i, rate in enumerate(flow_max):
                if rate == 0.0:
                    flow_max[i] = 1e5

            if self.flow_lim == IFLOW:
                If = Yf * V
                It = Yt * V
                # Branch current limits.
                h = matrix([(If * conj(If)) - flow_max,
                            (If * conj(It)) - flow_max])
            else:
                i_fbus = [e.from_bus._i for e in ln]
                i_tbus = [e.to_bus._i for e in ln]
                # Complex power injected at "from" bus (p.u.).
                Sf = mul(V[i_fbus], conj(Yf * V))
                # Complex power injected at "to" bus (p.u.).
                St = mul(V[i_tbus], conj(Yt * V))
                if self.flow_lim == PFLOW: # active power limit, P (Pan Wei)
                    # Branch real power limits.
                    h = matrix([Sf.real()**2 - flow_max,
                                St.real()**2 - flow_max])
                elif self.flow_lim == SFLOW: # apparent power limit, |S|
                    # Branch apparent power limits.
                    h = matrix([mul(Sf, conj(Sf)) - flow_max,
                                mul(St, conj(St)) - flow_max]).real()
                else:
                    raise ValueError

            # Evaluate partial derivatives of constraints ---------------------

            iVa = matrix(range(Va.i1, Va.iN + 1))
            iVm = matrix(range(Vm.i1, Vm.iN + 1))
            iPg = matrix(range(Pg.i1, Pg.iN + 1))
            iQg = matrix(range(Qg.i1, Qg.iN + 1))
            iVaVmPgQg = matrix([iVa, iVm, iPg, iQg]).T

            # Compute partials of injected bus powers.
            dSbus_dVm, dSbus_dVa = dSbus_dV(Ybus, V)

            i_gbus = [gen.bus._i for gen in gn]
            neg_Cg = spmatrix(matrix(-1.0, (ng, 1)),
                                     i_gbus,
                                     range(ng), (nb, ng))

            # Transposed Jacobian of the power balance equality constraints.
            dg = spmatrix([], [], [], (nxyz, 2 * nb))

            blank = spmatrix([], [], [], (nb, ng))

            dg[iVaVmPgQg, :] = sparse([
                [dSbus_dVa.real(), dSbus_dVa.imag()],
                [dSbus_dVm.real(), dSbus_dVm.imag()],
                [neg_Cg, blank],
                [blank, neg_Cg]
            ]).T

            # Compute partials of flows w.r.t V.
            if self.flow_lim == IFLOW:
                dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    dIbr_dV(YYf, YYt, V)
            else:
                dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    dSbr_dV(Yf, Yt, V, bs, ln)
            if self.flow_lim == PFLOW:
                dFf_dVa = dFf_dVa.real
                dFf_dVm = dFf_dVm.real
                dFt_dVa = dFt_dVa.real
                dFt_dVm = dFt_dVm.real
                Ff = Ff.real
                Ft = Ft.real

            # Squared magnitude of flow (complex power, current or real power).
            df_dVa, df_dVm, dt_dVa, dt_dVm = \
                dAbr_dV(dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft)

            # Construct Jacobian of inequality constraints (branch limits) and
            # transpose it.
            dh = spmatrix([], [], [], (nxyz, 2 * nl))
            dh[matrix([iVa, iVm]).T, :] = sparse([[df_dVa, dt_dVa],
                                                  [df_dVm, dt_dVm]]).T

            f = matrix([f, g, h])
            df = sparse([[df0], [dg], [dh]]).T

            if z is None:
                return f, df

            # Evaluate cost Hessian -------------------------------------------

            nxtra = nxyz - 2 * nb

            # Evaluate d2f ----------------------------------------------------

            d2f_dPg2 = matrix(0.0, (ng, 1)) # w.r.t p.u. Pg
            d2f_dQg2 = matrix(0.0, (ng, 1)) # w.r.t p.u. Qg

            for i in ipol:
                d2f_dPg2[i, 0] = polyval(polyder(list(gn[i].p_cost), 2),
                                         Pg.v0[i] * base_mva) * base_mva**2
            # TODO: Reactive power costs.
#            for i in ipol:
#                d2f_dQg2[i] = polyval(polyder(list(gn[i].q_cost), 2),
#                                      Qg.v0[i] * base_mva) * base_mva**2

            i = matrix([range(Pg.i1, Pg.iN + 1), range(Qg.i1, Qg.iN + 1)])

            d2f = spmatrix(matrix([d2f_dPg2, d2f_dQg2]), i, i, (nxyz, nxyz))

            # TODO: Generalised cost model.

            d2f = d2f * self.opt["cost_mult"]

            # Evaluate Hessian of power balance constraints -------------------

            neqnln = 2 * nb
            niqnln = 2 * len(il) # no. of lines with constraints

            eqnonlin = z[:neqnln]

            nlam = len(eqnonlin) / 2
            lamP = eqnonlin[:nlam]
            lamQ = eqnonlin[nlam:nlam + nlam]
            Gpaa, Gpav, Gpva, Gpvv = d2Sbus_dV2(Ybus, V, lamP)
            Gqaa, Gqav, Gqva, Gqvv = d2Sbus_dV2(Ybus, V, lamQ)

            d2G_1 = sparse([[sparse([[Gpaa, Gpva], [Gpav, Gpvv]]).real() +
                           sparse([[Gqaa, Gqva], [Gqav, Gqvv]]).imag()],
                           [spmatrix([], [], [], (2 * nb, nxtra))]])
            d2G_2 = spmatrix([], [], [], (nxtra, 2 * nb + nxtra))
            d2G = sparse([d2G_1, d2G_2])

            #  Evaluate Hessian of flow constraints ---------------------------

            ineqnonlin = z[neqnln:neqnln + niqnln]
            nmu = len(ineqnonlin) / 2
            muF = ineqnonlin[:nmu]
            muT = ineqnonlin[nmu:nmu + nmu]

            if self.flow_lim == IFLOW:
                dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It = \
                    dIbr_dV(Yf, Yt, V)
                Hfaa, Hfav, Hfva, Hfvv = \
                    d2AIbr_dV2(dIf_dVa, dIf_dVm, If, Yf, V, muF)
                Htaa, Htav, Htva, Htvv = \
                    d2AIbr_dV2(dIt_dVa, dIt_dVm, It, Yt, V, muT)
            else:
                f = [e.from_bus._i for e in ln]
                t = [e.to_bus._i for e in ln]
                # Line-bus connection matrices.
                Cf = spmatrix(1.0, range(nl), f, (nl, nb))
                Ct = spmatrix(1.0, range(nl), t, (nl, nb))
                dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = \
                    dSbr_dV(Yf, Yt, V, bs, ln)
                if self.flow_lim == PFLOW:
                    Hfaa, Hfav, Hfva, Hfvv = \
                        d2ASbr_dV2(dSf_dVa.real(), dSf_dVm.real(),
                                        Sf.real(), Cf, Yf, V, muF)
                    Htaa, Htav, Htva, Htvv = \
                        d2ASbr_dV2(dSt_dVa.real(), dSt_dVm.real(),
                                        St.real(), Ct, Yt, V, muT)
                elif self.flow_lim == SFLOW:
                    Hfaa, Hfav, Hfva, Hfvv = \
                        d2ASbr_dV2(dSf_dVa, dSf_dVm, Sf, Cf, Yf, V, muF)
                    Htaa, Htav, Htva, Htvv = \
                        d2ASbr_dV2(dSt_dVa, dSt_dVm, St, Ct, Yt, V, muT)
                else:
                    raise ValueError

            d2H_1 = sparse([[sparse([[Hfaa, Hfva], [Hfav, Hfvv]]) +
                             sparse([[Htaa, Htva], [Htav, Htvv]])],
                            [spmatrix([], [], [], (2 * nb, nxtra))]])
            d2H_2 = spmatrix([], [], [], (nxtra, 2 * nb + nxtra))
            d2H = sparse([d2H_1, d2H_2])

            H = d2f + d2G + d2H

            return f, df, H

        # cp(F, G=None, h=None, dims=None, A=None, b=None, kktsolver=None)
        #
        #     minimize    f0(x)
        #     subject to  fk(x) <= 0, k = 1, ..., mnl
        #                 G*x   <= h
        #                 A*x   =  b.
        solution = solvers.cp(F, G=Ai, h=bi, dims=None, A=Ae, b=be)

        return solution


def split_linear_constraints(A, l, u):
    """ Returns the linear equality and inequality constraints.
    """
    ieq = []
    igt = []
    ilt = []
    ibx = []
    for i in range(len(l)):
        if abs(u[i] - l[i]) <= EPS:
            ieq.append(i)
        elif (u[i] > 1e10) and (l[i] > -1e10):
            igt.append(i)
        elif (l[i] <= -1e10) and (u[i] < 1e10):
            ilt.append(i)
        elif (abs(u[i] - l[i]) > EPS) and (u[i] < 1e10) and (l[i] > -1e10):
            ibx.append(i)
        else:
            raise ValueError

    Ae = A[ieq, :]
    Ai = sparse([A[ilt, :], -A[igt, :], A[ibx, :], -A[ibx, :]])
    be = u[ieq, :]
    bi = matrix([u[ilt], -l[igt], u[ibx], -l[ibx]])

    return Ae, be, Ai, bi

#--------------------------------------------------------------------------
#  Partial derivative of power injection w.r.t. voltage:
#--------------------------------------------------------------------------

def dSbus_dV(Y, V):
    """ Computes the partial derivative of power injection w.r.t. voltage.

        References:
            Ray Zimmerman, "dSbus_dV.m", MATPOWER, version 3.2,
            PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
    """
    I = Y * V

    diagV = spdiag(V)
    diagIbus = spdiag(I)
    diagVnorm = spdiag(div(V, abs(V))) # Element-wise division.

    dS_dVm = diagV * conj(Y * diagVnorm) + conj(diagIbus) * diagVnorm
    dS_dVa = 1j * diagV * conj(diagIbus - Y * diagV)

    return dS_dVm, dS_dVa

#--------------------------------------------------------------------------
#  Partial derivatives of branch currents w.r.t. voltage.
#--------------------------------------------------------------------------

def dIbr_dV(Yf, Yt, V):
    """ Computes partial derivatives of branch currents w.r.t. voltage.

        Ray Zimmerman, "dIbr_dV.m", MATPOWER, version 4.0b1,
        PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
    """
#        nb = len(V)

    Vnorm = div(V, abs(V))
    diagV = spdiag(V)
    diagVnorm = spdiag(Vnorm)
    dIf_dVa = Yf * 1j * diagV
    dIf_dVm = Yf * diagVnorm
    dIt_dVa = Yt * 1j * diagV
    dIt_dVm = Yt * diagVnorm

    # Compute currents.
    If = Yf * V
    It = Yt * V

    return dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It

#--------------------------------------------------------------------------
#  Partial derivative of branch power flow w.r.t voltage:
#--------------------------------------------------------------------------

def dSbr_dV(Yf, Yt, V, buses, branches):
    """ Computes the branch power flow vector and the partial derivative of
        branch power flow w.r.t voltage.
    """
    nl = len(branches)
    nb = len(V)

    f = matrix([l.from_bus._i for l in branches])
    t = matrix([l.to_bus._i for l in branches])

    # Compute currents.
    If = Yf * V
    It = Yt * V

    Vnorm = div(V, abs(V))

    diagVf = spdiag(V[f])
    diagIf = spdiag(If)
    diagVt = spdiag(V[t])
    diagIt = spdiag(It)
    diagV = spdiag(V)
    diagVnorm = spdiag(Vnorm)

    ibr = range(nl)
    size = (nl, nb)
    # Partial derivative of S w.r.t voltage phase angle.
    dSf_dVa = 1j * (conj(diagIf) *
        spmatrix(V[f], ibr, f, size) - diagVf * conj(Yf * diagV))

    dSt_dVa = 1j * (conj(diagIt) *
        spmatrix(V[t], ibr, t, size) - diagVt * conj(Yt * diagV))

    # Partial derivative of S w.r.t. voltage amplitude.
    dSf_dVm = diagVf * conj(Yf * diagVnorm) + conj(diagIf) * \
        spmatrix(Vnorm[f], ibr, f, size)

    dSt_dVm = diagVt * conj(Yt * diagVnorm) + conj(diagIt) * \
        spmatrix(Vnorm[t], ibr, t, size)

    # Compute power flow vectors.
    Sf = mul(V[f], conj(If))
    St = mul(V[t], conj(It))

    return dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St

#--------------------------------------------------------------------------
#  Partial derivative of apparent power flow w.r.t voltage:
#--------------------------------------------------------------------------

def dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St):
    """ Partial derivatives of squared flow magnitudes w.r.t voltage.

        Computes partial derivatives of apparent power w.r.t active and
        reactive power flows.  Partial derivative must equal 1 for lines
        with zero flow to avoid division by zero errors (1 comes from
        L'Hopital).
    """
    dAf_dPf = spdiag(2 * Sf.real())
    dAf_dQf = spdiag(2 * Sf.imag())
    dAt_dPt = spdiag(2 * St.real())
    dAt_dQt = spdiag(2 * St.imag())

    # Partial derivative of apparent power magnitude w.r.t voltage
    # phase angle.
    dAf_dVa = dAf_dPf * dSf_dVa.real() + dAf_dQf * dSf_dVa.imag()
    dAt_dVa = dAt_dPt * dSt_dVa.real() + dAt_dQt * dSt_dVa.imag()
    # Partial derivative of apparent power magnitude w.r.t. voltage
    # amplitude.
    dAf_dVm = dAf_dPf * dSf_dVm.real() + dAf_dQf * dSf_dVm.imag()
    dAt_dVm = dAt_dPt * dSt_dVm.real() + dAt_dQt * dSt_dVm.imag()

    return dAf_dVa, dAf_dVm, dAt_dVa, dAt_dVm

#--------------------------------------------------------------------------
#  Second derivative of power injection w.r.t voltage:
#--------------------------------------------------------------------------

def d2Sbus_dV2(Ybus, V, lam):
    """ Computes 2nd derivatives of power injection w.r.t. voltage.
    """
    n = len(V)
    Ibus = Ybus * V
    diaglam = spdiag(lam)
    diagV = spdiag(V)

    A = spmatrix(mul(lam, V), range(n), range(n))
    B = Ybus * diagV
    C = A * conj(B)
    D = Ybus.H * diagV
    E = conj(diagV) * (D * diaglam - spmatrix(D*lam, range(n), range(n)))
    F = C - A * spmatrix(conj(Ibus), range(n), range(n))
    G = spmatrix(div(matrix(1.0, (n, 1)), abs(V)), range(n), range(n))

    Gaa = E + F
    Gva = 1j * G * (E - F)
    Gav = Gva.T
    Gvv = G * (C + C.T) * G

    return Gaa, Gav, Gva, Gvv

#--------------------------------------------------------------------------
#  Second derivative of complex branch current w.r.t. voltage:
#--------------------------------------------------------------------------

def d2Ibr_dV2(Ybr, V, lam):
    """ Computes 2nd derivatives of complex branch current w.r.t. voltage.
    """
    nb = len(V)
    diaginvVm = spdiag(div(matrix(1.0, (nb, 1)), abs(V)))

    Haa = spdiag(mul(-(Ybr.T * lam), V))
    Hva = -1j * Haa * diaginvVm
    Hav = Hva
    Hvv = spmatrix([], [], [], (nb, nb))

    return Haa, Hav, Hva, Hvv

#--------------------------------------------------------------------------
#  Second derivative of complex power flow w.r.t. voltage:
#--------------------------------------------------------------------------

def d2Sbr_dV2(Cbr, Ybr, V, lam):
    """ Computes 2nd derivatives of complex power flow w.r.t. voltage.
    """
    nb = len(V)

    diaglam = spdiag(lam)
    diagV = spdiag(V)

    A = Ybr.H * diaglam * Cbr
    B = conj(diagV) * A * diagV
    D = spdiag(mul((A*V), conj(V)))
    E = spdiag(mul((A.T * conj(V)), V))
    F = B + B.T
    G = spdiag(div(matrix(1.0, (nb, 1)), abs(V)))

    Haa = F - D - E
    Hva = 1j * G * (B - B.T - D + E)
    Hav = Hva.T
    Hvv = G * F * G

    return Haa, Hav, Hva, Hvv

#--------------------------------------------------------------------------
#  Second derivative of |complex power flow|**2 w.r.t. voltage:
#--------------------------------------------------------------------------

def d2ASbr_dV2(dSbr_dVa, dSbr_dVm, Sbr, Cbr, Ybr, V, lam):
    """ Computes 2nd derivatives of |complex power flow|**2 w.r.t. V.
    """
    diaglam = spdiag(lam)
    diagSbr_conj = spdiag(conj(Sbr))

    Saa, Sav, Sva, Svv = d2Sbr_dV2(Cbr, Ybr, V, diagSbr_conj * lam)

    Haa = 2 * ( Saa + dSbr_dVa.T * diaglam * conj(dSbr_dVa) ).real()
    Hva = 2 * ( Sva + dSbr_dVm.T * diaglam * conj(dSbr_dVa) ).real()
    Hav = 2 * ( Sav + dSbr_dVa.T * diaglam * conj(dSbr_dVm) ).real()
    Hvv = 2 * ( Svv + dSbr_dVm.T * diaglam * conj(dSbr_dVm) ).real()

    return Haa, Hav, Hva, Hvv

#--------------------------------------------------------------------------
#  Second derivative of |complex current|**2 w.r.t. voltage:
#--------------------------------------------------------------------------

def d2AIbr_dV2(dIbr_dVa, dIbr_dVm, Ibr, Ybr, V, lam):
    """ Computes 2nd derivatives of |complex current|**2 w.r.t. V.
    """
    diaglam = spdiag(lam)
    diagIbr_conj = spdiag(conj(Ibr))

    Iaa, Iav, Iva, Ivv = d2Ibr_dV2(Ybr, V, diagIbr_conj * lam)

    Haa = 2 * ( Iaa + dIbr_dVa.T * diaglam * conj(dIbr_dVa) ).real()
    Hva = 2 * ( Iva + dIbr_dVm.T * diaglam * conj(dIbr_dVa) ).real()
    Hav = 2 * ( Iav + dIbr_dVa.T * diaglam * conj(dIbr_dVm) ).real()
    Hvv = 2 * ( Ivv + dIbr_dVm.T * diaglam * conj(dIbr_dVm) ).real()

    return Haa, Hav, Hva, Hvv

#------------------------------------------------------------------------------
# Complex conjugate:
#------------------------------------------------------------------------------

def conj(A):
    """ Returns the complex conjugate of A as a new matrix.
    """
    return A.ctrans().trans()


def tocvx(B):
    """ Converts a sparse SciPy matrix into a sparse CVXOPT matrix.
    """
    Bcoo = B.tocoo()
    return spmatrix(Bcoo.data, Bcoo.row.tolist(), Bcoo.col.tolist())

# EOF -------------------------------------------------------------------------
