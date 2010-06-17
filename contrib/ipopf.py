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

""" Defines an OPF solver for Pylon using IPOPT.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pyipopt

from numpy import \
    array, polyder, polyval, exp, conj, Inf, ones, r_, zeros, asarray

from scipy.sparse import lil_matrix, csr_matrix, hstack, vstack

from pylon import REFERENCE
from pylon.solver import Solver, SFLOW, IFLOW, PFLOW

#------------------------------------------------------------------------------
#  "IPOPFSolver" class:
#------------------------------------------------------------------------------

class IPOPFSolver(Solver):
    """ Solves AC optimal power flow using IPOPT.
    """

    def __init__(self, om, flow_lim=SFLOW, opt=None):
        """ Initialises a new IPOPFSolver instance.
        """
        super(IPOPFSolver, self).__init__(om)

        #: Quantity to limit for branch flow constraints ("S", "P" or "I").
        self.flow_lim = flow_lim

        #: Options for the PIPS.
        self.opt = {} if opt is None else opt


    def _ref_bus_angle_constraint(self, buses, Va, xmin, xmax):
        """ Adds a constraint on the reference bus angles.
        """
        refs = [bus._i for bus in buses if bus.type == REFERENCE]
        Varefs = array([b.v_angle for b in buses if b.type == REFERENCE])

        xmin[Va.i1 - 1 + refs] = Varefs
        xmax[Va.iN - 1 + refs] = Varefs

        return xmin, xmax


    def solve(self):
        """ Solves AC optimal power flow.
        """
        case = self.om.case
        base_mva = case.base_mva
        # TODO: Explain this value.
        self.opt["cost_mult"] = 1e-4

        # Unpack the OPF model.
        bs, ln, gn, _ = self._unpack_model(self.om)
        # Compute problem dimensions.
        ipol, _, nb, nl, _, ny, nxyz = self._dimension_data(bs, ln, gn)

        # Compute problem dimensions.
        ng = len(gn)
#        gpol = [g for g in gn if g.pcost_model == POLYNOMIAL]
        # Indexes of constrained lines.
        il = array([i for i,l in enumerate(ln) if 0.0 < l.rate_a < 1e10])
        nl2 = len(il)

        # Linear constraints (l <= A*x <= u).
        A, l, u = self.om.linear_constraints()
#        AA, bb = self._linear_constraints(self.om)

        _, xmin, xmax = self._var_bounds()

        # Select an interior initial point for interior point solver.
        x0 = self._initial_interior_point(bs, gn, xmin, xmax, ny)

        # Build admittance matrices.
        Ybus, Yf, Yt = case.Y

        # Optimisation variables.
        Va = self.om.get_var("Va")
        Vm = self.om.get_var("Vm")
        Pg = self.om.get_var("Pg")
        Qg = self.om.get_var("Qg")

        # Adds a constraint on the reference bus angles.
#        xmin, xmax = self._ref_bus_angle_constraint(bs, Va, xmin, xmax)

        def f_fcn(x, user_data=None):
            """ Evaluates the objective function.
            """
            p_gen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            q_gen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            # Polynomial cost of P and Q.
            xx = r_[p_gen, q_gen] * base_mva
            if len(ipol) > 0:
                f = sum([g.total_cost(xx[i]) for i,g in enumerate(gn)])
            else:
                f = 0

            # Piecewise linear cost of P and Q.
            if ny:
                y = self.om.get_var("y")
                ccost = csr_matrix((ones(ny),
                    (range(y.i1, y.iN + 1), zeros(ny))), shape=(nxyz, 1)).T
                f = f + ccost * x
            else:
                ccost = zeros((1, nxyz))
                # TODO: Generalised cost term.

            return f


        def df_fcn(x, usr_data=None):
            """ Calculates gradient of the objective function.
            """
            p_gen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            q_gen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            xx = r_[p_gen, q_gen] * base_mva

            if ny > 0:
                y = self.om.get_var("y")
                iy = range(y.i1, y.iN + 1)
                ccost = \
                    csr_matrix((ones(ny), (iy, zeros(ny))), shape=(nxyz, 1)).T
            else:
                ccost = zeros((1, nxyz))
                # TODO: Generalised cost term.

            iPg = range(Pg.i1, Pg.iN + 1)
            iQg = range(Qg.i1, Qg.iN + 1)

            # Polynomial cost of P and Q.
            df_dPgQg = zeros((2 * ng, 1))        # w.r.t p.u. Pg and Qg
#            df_dPgQg[ipol] = matrix([g.poly_cost(xx[i], 1) for g in gpol])
#            for i, g in enumerate(gn):
#                der = polyder(list(g.p_cost))
#                df_dPgQg[i] = polyval(der, xx[i]) * base_mva
            for i in ipol:
                df_dPgQg[i] = \
                    base_mva * polyval(polyder(list(gn[i].p_cost)), xx[i])

            df = zeros((nxyz, 1))
            df[iPg] = df_dPgQg[:ng]
            df[iQg] = df_dPgQg[ng:ng + ng]

            # Piecewise linear cost of P and Q.
            df = df + ccost.T
            # TODO: Generalised cost term.

            return asarray(df).flatten()


        def g_fcn(x, usr_data=None):
            """ Evaluates the non-linear constraint values.
            """
            Pgen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            Qgen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            for i, g in enumerate(gn):
                g.p = Pgen[i] * base_mva # active generation in MW
                g.q = Qgen[i] * base_mva # reactive generation in MVAr

            # Rebuild the net complex bus power injection vector in p.u.
            Sbus = case.getSbus(bs)

            Vang = x[Va.i1:Va.iN + 1]
            Vmag = x[Vm.i1:Vm.iN + 1]
            V = Vmag * exp(1j * Vang)

            # Evaluate the power flow equations.
            mis = V * conj(Ybus * V) - Sbus

            # Equality constraints (power flow).
            g = r_[mis.real,  # active power mismatch for all buses
                   mis.imag]  # reactive power mismatch for all buses

            # Inequality constraints (branch flow limits).
            # (line constraint is actually on square of limit)
            flow_max = array([(l.rate_a / base_mva)**2 for l in ln])
            # FIXME: There must be a more elegant method for this.
            for i, v in enumerate(flow_max):
                if v == 0.0:
                    flow_max[i] = Inf

            if self.flow_lim == IFLOW:
                If = Yf * V
                It = Yt * V
                # Branch current limits.
                h = r_[(If * conj(If)) - flow_max,
                       (If * conj(It)) - flow_max]
            else:
                i_fbus = [e.from_bus._i for e in ln]
                i_tbus = [e.to_bus._i for e in ln]
                # Complex power injected at "from" bus (p.u.).
                Sf = V[i_fbus] * conj(Yf * V)
                # Complex power injected at "to" bus (p.u.).
                St = V[i_tbus] * conj(Yt * V)
                if self.flow_lim == PFLOW: # active power limit, P (Pan Wei)
                    # Branch real power limits.
                    h = r_[Sf.real()**2 - flow_max,
                           St.real()**2 - flow_max]
                elif self.flow_lim == SFLOW: # apparent power limit, |S|
                    # Branch apparent power limits.
                    h = r_[(Sf * conj(Sf)) - flow_max,
                           (St * conj(St)) - flow_max].real
                else:
                    raise ValueError

            return r_[g, h]


        def dg_fcn(x, flag, usr_data=None):
            """ Calculates the Jacobian matrix. It takes two arguments, the
                first is the variable x and the second is a Boolean flag. If
                the flag is true, the function returns a tuple of arrays
                (row, col) to indicate the sparse structure of the Jacobian
                matrix. If the flag is false the function returns the values
                of the Jacobian matrix with length nnzj.
            """
            iVa = range(Va.i1, Va.iN + 1)
            iVm = range(Vm.i1, Vm.iN + 1)
            iPg = range(Pg.i1, Pg.iN + 1)
            iQg = range(Qg.i1, Qg.iN + 1)
            iVaVmPgQg = r_[iVa, iVm, iPg, iQg].T

            Vang = x[Va.i1:Va.iN + 1]
            Vmag = x[Vm.i1:Vm.iN + 1]
            V = Vmag * exp(1j * Vang)

            # Compute partials of injected bus powers.
            dSbus_dVm, dSbus_dVa = case.dSbus_dV(Ybus, V)

            i_gbus = [gen.bus._i for gen in gn]
            neg_Cg = csr_matrix((-ones(ng), (i_gbus, range(ng))), (nb, ng))

            # Transposed Jacobian of the power balance equality constraints.
            dg = lil_matrix((nxyz, 2 * nb))

            blank = csr_matrix((nb, ng))
            dg[iVaVmPgQg, :] = vstack([
                hstack([dSbus_dVa.real, dSbus_dVm.real, neg_Cg, blank]),
                hstack([dSbus_dVa.imag, dSbus_dVm.imag, blank, neg_Cg])
            ], "csr").T

            # Compute partials of flows w.r.t V.
            if self.flow_lim == IFLOW:
                dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    case.dIbr_dV(Yf, Yt, V)
            else:
                dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    case.dSbr_dV(Yf, Yt, V, bs, ln)
            if self.flow_lim == PFLOW:
                dFf_dVa = dFf_dVa.real
                dFf_dVm = dFf_dVm.real
                dFt_dVa = dFt_dVa.real
                dFt_dVm = dFt_dVm.real
                Ff = Ff.real
                Ft = Ft.real

            # Squared magnitude of flow (complex power, current or real power).
            df_dVa, df_dVm, dt_dVa, dt_dVm = \
                case.dAbr_dV(dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft)

            # Construct Jacobian of inequality constraints (branch limits) and
            # transpose it.
            dh = lil_matrix((nxyz, 2 * nl))
            dh[r_[iVa, iVm].T, :] = vstack([hstack([df_dVa, df_dVm]),
                                            hstack([dt_dVa, dt_dVm])], "csr").T

            J = vstack([dg, dh, A]).tocoo()

            if flag:
                return (J.row, J.col)
            else:
                return J.data


        def h_fcn(x, lagrange, obj_factor, flag, usr_data=None):
            """ Evaluates the Hessian of the Lagrangian.
            """
            neqnln = 2 * nb
            niqnln = 2 * len(il) # no. of lines with constraints

            Pgen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            Qgen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            for i, g in enumerate(gn):
                g.p = Pgen[i] * base_mva # active generation in MW
                g.q = Qgen[i] * base_mva # reactive generation in MVAr

            Vang = x[Va.i1:Va.iN + 1]
            Vmag = x[Vm.i1:Vm.iN + 1]
            V = Vmag * exp(1j * Vang)
            nxtra = nxyz - 2 * nb

            #------------------------------------------------------------------
            #  Evaluate d2f.
            #------------------------------------------------------------------

            d2f_dPg2 = lil_matrix((ng, 1)) # w.r.t p.u. Pg
            d2f_dQg2 = lil_matrix((ng, 1)) # w.r.t p.u. Qg]

            for i in ipol:
                d2f_dPg2[i, 0] = polyval(polyder(list(gn[i].p_cost), 2),
                                         Pg.v0[i] * base_mva) * base_mva**2
#            for i in ipol:
#                d2f_dQg2[i] = polyval(polyder(list(gn[i].p_cost), 2),
#                                      Qg.v0[i] * base_mva) * base_mva**2

            i = r_[range(Pg.i1, Pg.iN + 1), range(Qg.i1, Qg.iN + 1)]

            d2f = csr_matrix((vstack([d2f_dPg2, d2f_dQg2]).toarray().flatten(),
                              (i, i)), shape=(nxyz, nxyz))
            # TODO: Generalised cost model.
            d2f = d2f * self.opt["cost_mult"]

            #------------------------------------------------------------------
            #  Evaluate Hessian of power balance constraints.
            #------------------------------------------------------------------

            eqnonlin = lagrange[:neqnln]
#            nlam = len(lagrange["eqnonlin"]) / 2
            nlam = len(eqnonlin) / 2
            lamP = eqnonlin[:nlam]
            lamQ = eqnonlin[nlam:nlam + nlam]
            Gpaa, Gpav, Gpva, Gpvv = case.d2Sbus_dV2(Ybus, V, lamP)
            Gqaa, Gqav, Gqva, Gqvv = case.d2Sbus_dV2(Ybus, V, lamQ)

            d2G = vstack([
                hstack([
                    vstack([hstack([Gpaa, Gpav]),
                            hstack([Gpva, Gpvv])]).real +
                    vstack([hstack([Gqaa, Gqav]),
                            hstack([Gqva, Gqvv])]).imag,
                    csr_matrix((2 * nb, nxtra))]),
                hstack([
                    csr_matrix((nxtra, 2 * nb)),
                    csr_matrix((nxtra, nxtra))
                ])
            ], "csr")

            #------------------------------------------------------------------
            #  Evaluate Hessian of flow constraints.
            #------------------------------------------------------------------

            ineqnonlin = lagrange[neqnln:neqnln + niqnln]
            nmu = len(ineqnonlin) / 2
            muF = ineqnonlin[:nmu]
            muT = ineqnonlin[nmu:nmu + nmu]
            if self.flow_lim == "I":
                dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It = \
                    case.dIbr_dV(Yf, Yt, V)
                Hfaa, Hfav, Hfva, Hfvv = \
                    case.d2AIbr_dV2(dIf_dVa, dIf_dVm, If, Yf, V, muF)
                Htaa, Htav, Htva, Htvv = \
                    case.d2AIbr_dV2(dIt_dVa, dIt_dVm, It, Yt, V, muT)
            else:
                f = [e.from_bus._i for e in ln]
                t = [e.to_bus._i for e in ln]
                # Line-bus connection matrices.
                Cf = csr_matrix((ones(nl), (range(nl), f)), (nl, nb))
                Ct = csr_matrix((ones(nl), (range(nl), t)), (nl, nb))
                dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = \
                    case.dSbr_dV(Yf, Yt, V)
                if self.flow_lim == PFLOW:
                    Hfaa, Hfav, Hfva, Hfvv = \
                        case.d2ASbr_dV2(dSf_dVa.real(), dSf_dVm.real(),
                                        Sf.real(), Cf, Yf, V, muF)
                    Htaa, Htav, Htva, Htvv = \
                        case.d2ASbr_dV2(dSt_dVa.real(), dSt_dVm.real(),
                                        St.real(), Ct, Yt, V, muT)
                elif self.flow_lim == SFLOW:
                    Hfaa, Hfav, Hfva, Hfvv = \
                        case.d2ASbr_dV2(dSf_dVa, dSf_dVm, Sf, Cf, Yf, V, muF)
                    Htaa, Htav, Htva, Htvv = \
                        case.d2ASbr_dV2(dSt_dVa, dSt_dVm, St, Ct, Yt, V, muT)
                else:
                    raise ValueError

            d2H = vstack([
                hstack([
                    vstack([hstack([Hfaa, Hfav]),
                            hstack([Hfva, Hfvv])]) +
                    vstack([hstack([Htaa, Htav]),
                            hstack([Htva, Htvv])]),
                    csr_matrix((2 * nb, nxtra))
                ]),
                hstack([
                    csr_matrix((nxtra, 2 * nb)),
                    csr_matrix((nxtra, nxtra))
                ])
            ], "csr")

            H = d2f + d2G + d2H

            if flag:
                return (H.row, H.col)
            else:
                return H.data

        n = len(x0) # the number of variables
        gl = r_[zeros(2 * nb), -Inf * ones(2 * nl2), l]
        gu = r_[zeros(2 * nb),       zeros(2 * nl2), u]
        m = len(gl) # the number of constraints
        nnzj = 0 # the number of nonzeros in Jacobian matrix
        nnzh = 0 # the number of non-zeros in Hessian matrix

        nlp = pyipopt.create(n, xmin, xmax, m, gl, gu, nnzj, nnzh,
                             f_fcn, df_fcn, g_fcn, dg_fcn, h_fcn)

#        x, zl, zu, obj = nlp.solve(x0)
        success = nlp.solve(x0)
        nlp.close()

        print "Success:", success
        print "Solution of the primal variables, x"
#        print x
        print "Solution of the bound multipliers, z_L and z_U"
#        print zl, zu
        print "Objective value"
#        print "f(x*) =", obj


if __name__ == "__main__":
    import os
    import pylon
    c = pylon.Case.load(os.path.join(os.path.dirname(pylon.__file__),
                                     "test", "data", "case6ww.pkl"))
    s = pylon.OPF(c, dc=False).solve(IPOPFSolver)

# EOF -------------------------------------------------------------------------
