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

    [1] Ray Zimmerman, "fmincon.m", MATPOWER, PSERC Cornell, version 4.0b1,
        http://www.pserc.cornell.edu/matpower/, December 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import polyval, polyder

from cvxopt import matrix, spmatrix, mul, sparse, exp, solvers

from pylon.opf import Solver

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "CVXOPTSolver" class:
#------------------------------------------------------------------------------

class CVXOPTSolver(Solver):
    """ Solves AC optimal power flow using convex optimization.
    """

    def __init__(self, om, flow_lim="S"):
        """ Initialises a new CVXOPTSolver instance.
        """
        super(CVXOPTSolver, self).__init__(om)

        # Quantity to limit for branch flow constraints ("S", "P" or "I").
        self.flow_lim = flow_lim


    def solve(self):
        j = 0 + 1j
        case = self.om.case
        base_mva = case.base_mva
        # Unpack the OPF model.
        buses, branches, generators = self._unpack_model(self.om)
        # Compute problem dimensions.
        ng = len(generators)
        ipol, ipwl, nb, nl, nw, ny, nxyz = self._dimension_data(buses,
                                                                branches,
                                                                generators)
        # The number of non-linear equality constraints.
        neq = 2 * nb
        # The number of control variables.
        nc = 2 * nb + 2 * ng

        # Split the constraints in equality and inequality.
        Aeq, beq, Aieq, bieq = self._linear_constraints(self.om)

        # Optimisation variables.
        Va = self.om.get_var("Va")
        Vm = self.om.get_var("Vm")
        Pg = self.om.get_var("Pg")
        Qg = self.om.get_var("Qg")


        def F(x=None, z=None):
            """ Evaluates the objective and nonlinear constraint functions.
            """
            if x is None:
                # Number of non-linear constraints.
                m = neq

                x0 = matrix(0., (nxyz, 1))
                x0[Va.i1:Va.iN] = 0.0
                x0[Vm.i1:Vm.iN] = 1.0
                x0[Pg.i1:Pg.iN] = [g.p_min + g.p_max / 2 / base_mva
                                   for g in generators]
                x0[Qg.i1:Qg.iN] = [g.q_min + g.q_max / 2 / base_mva
                                   for g in generators]
                return m, x0

            # Evaluate objective function -------------------------------------

            p_gen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            q_gen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            xx = matrix([p_gen, q_gen]) * base_mva

            # Evaluate the objective function value.
            if len(ipol) > 0:
                # FIXME: Implement reactive power costs.
                f0 = sum([g.total_cost(xx[i]) for i, g in
                          enumerate(generators)])
            else:
                f0 = 0

            # Evaluate cost gradient ------------------------------------------

            # Partial derivative w.r.t. polynomial cost Pg and Qg.
#            df_dPgQg = [polyval(polyder(g.p_cost), g.p) * base_mva \
#                        for g in generators]
            df_dPgQg = matrix(0.0, (ng * 2, 1))

            for i, g in enumerate(generators):
                der = polyder( list(g.p_cost) )
                df_dPgQg[i] = polyval(der, g.p) * base_mva

            df0= matrix([matrix(0.0, (Vm.iN, 1)), df_dPgQg])

            # Evaluate nonlinear equality constraints -------------------------

            # Net complex bus power injection vector in p.u.
            s = matrix([case.s_surplus(v) / base_mva for v in buses])

            # Bus voltage vector.
            v_angle = x[Va.i1:Va.iN + 1]
            v_magnitude = x[Vm.i1:Vm.iN + 1]
#            Va0r = Va0 * pi / 180 #convert to radians
            v = mul(v_magnitude, exp(j * v_angle)) #element-wise product

            # Evaluate the power flow equations.
            Y, Yfrom, Yto = case.Y
            mismatch = mul(v, conj(Y * v)) - s

            # Evaluate power balance equality constraint function values.
            fk_eq = matrix([mismatch.real(), mismatch.imag()])

            # Evaluate nonlinear inequality constraints -----------------------

            # Branch power flow limit inequality constraint function values.
            from_idxs = matrix([e.from_bus._i for e in branches])
            to_idxs = matrix([e.to_bus._i for e in branches])
            # Complex power in p.u. injected at the from bus.
            s_from = mul(v[from_idxs], conj(Yfrom, v))
            # Complex power in p.u. injected at the to bus.
            s_to = mul(v[to_idxs], conj(Yto, v))

            # Apparent power flow limit in MVA, |S|.
            rate_a = matrix([e.rate_a for e in branches])

            # FIXME: Implement active power and current magnitude limits.
            fk_ieq = matrix([abs(s_from) - rate_a, abs(s_to) - rate_a])

            # Evaluate partial derivatives of constraints ---------------------

            # Partial derivative of injected bus power
            dS_dVm, dS_dVa = case.dSbus_dV(Y, v) # w.r.t voltage
            pv_idxs = matrix([bus._i for bus in buses])
            dS_dPg = spmatrix(-1, pv_idxs, range(ng)) # w.r.t Pg
            dS_dQg = spmatrix(-j, pv_idxs, range(ng)) # w.r.t Qg

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
                case.dSbr_dV(Yfrom, Yto, v)

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

            d2f_d2Pg = spmatrix([], [], [], (ng, 1))
            d2f_d2Qg = spmatrix([], [], [], (ng, 1))
            for i, g in enumerate(generators):
                der = polyder(list(g.p_cost))
                # TODO: Implement reactive power costs.
                d2f_d2Pg[i] = polyval(der, g.p) * base_mva

            i = matrix(range(Pg.i1, Qg.iN + 1)).T
            H = spmatrix(matrix([d2f_d2Pg, d2f_d2Qg]), i, i)

            return f, df, H

        # cp(F, G=None, h=None, dims=None, A=None, b=None, kktsolver=None)
        #
        #     minimize    f0(x)
        #     subject to  fk(x) <= 0, k = 1, ..., mnl
        #                 G*x   <= h
        #                 A*x   =  b.
        solution = solvers.cp(F, G=Aieq, h=bieq, dims=None, A=Aeq, b=beq)

        return solution

#------------------------------------------------------------------------------
# Complex conjugate:
#------------------------------------------------------------------------------

def conj(A):
    """ Returns the complex conjugate of A as a new matrix.
    """
    return A.ctrans().trans()

# EOF -------------------------------------------------------------------------
