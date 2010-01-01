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

""" Defines a generalised OPF solver and an OPF model.

    References:
        Ray Zimmerman, "opf.m", MATPOWER, PSERC Cornell, version 4.0b1,
        http://www.pserc.cornell.edu/matpower/, December 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import pi, diff, polyder, polyval

from cvxopt import matrix, spmatrix, sparse, spdiag, div, mul
from cvxopt import solvers

from util import Named, conj
from case import REFERENCE, POLYNOMIAL, PW_LINEAR

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

INF = 1e10
EPS = 2**-52

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "OPF" class:
#------------------------------------------------------------------------------

class OPF:
    """ Defines a generalised OPF solver.

        References:
            Ray Zimmerman, "opf.m", MATPOWER, PSERC Cornell, version 4.0b1,
            http://www.pserc.cornell.edu/matpower/, December 2009
    """

    def __init__(self, case, dc=True, ignore_ang_lim=True, show_progress=True,
                 max_iterations=100, absolute_tol=1e-7, relative_tol=1e-6,
                 feasibility_tol=1e-7):
        """ Initialises a new OPF instance.
        """
        # Case under optimisation.
        self.case = case

        # Use DC power flow formulation.
        self.dc = dc

        # Ignore angle difference limits for branches even if specified.
        self.ignore_ang_lim = ignore_ang_lim

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


    def solve(self):
        """ Solves an optimal power flow and returns a results dictionary.
        """
        base_mva = self.case.base_mva

        # Set algorithm parameters.
        self._algorithm_parameters()

        # Check for one reference bus.
        oneref, refs = self._ref_check(self.case)
        if not oneref:
            return {"status": "error"}

        # Remove isolated components.
        buses, branches, generators = self._remove_isolated(self.case)

        # Zero the case result attributes.
        self.case.reset()

        # Convert single-block piecewise-linear costs into linear polynomial.
        generators = self._pwl1_to_poly(generators)

        # Set-up initial problem variables.
        Va = self._voltage_angle_var(refs, buses)
        Pg = self._p_gen_var(generators, base_mva)

        if self.dc: # DC model.
            # Get the susceptance matrices and phase shift injection vectors.
            B, Bf, Pbusinj, Pfinj = self.case.B

            # Power mismatch constraints (B*Va + Pg = Pd).
            Pmis = self._power_mismatch_dc(buses, generators, B, Pbusinj,
                                           base_mva)
            # Branch flow limit constraints.
            Pf, Pt = self._branch_flow_dc(branches, Bf, Pfinj, base_mva)
        else:
            Pmis, Qmis = self._power_mismatch_ac()

        # Branch voltage angle difference limits.
        ang = self._voltage_angle_diff_limit(buses, branches)

        # Piece-wise linear generator cost constraints.
        ycon = self._pwl_gen_costs(generators, base_mva)

        # Add variables and constraints to the OPF model object.
        if self.dc:
            om = self._construct_opf_model([Va, Pg], [Pmis, Pf, Pt, ang, ycon],
                                           Bf=Bf, Pfinj=Pfinj)
        else:
            om = self._construct_opf_model([Va, Vm, Pg, Qg],
                                           [Pmis, Qmis, Sf, St, vl, ang])

        # Call the specific solver.
        if self.dc:
            result = DCOPFSolver(om).solve()
        else:
            result = CVXOPTSolver(om).solve()

        return result


    def _algorithm_parameters(self):
        """ Sets the parameters of the CVXOPT solver algorithm.
        """
        solvers.options["show_progress"] = self.show_progress
        solvers.options["maxiters"] = self.max_iterations
        solvers.options["abstol"] = self.absolute_tol
        solvers.options["reltol"] = self.relative_tol
        solvers.options["feastol"] = self.feasibility_tol


    def _ref_check(self, case):
        """ Checks that there is only one reference bus.
        """
        refs = matrix([i for i, bus in enumerate(case.buses)
                      if bus.type == REFERENCE])

        if not len(refs) == 1:
            logger.error("OPF requires a single reference bus.")
            return False, refs
        else:
            return True, refs


    def _remove_isolated(self, case):
        """ Returns non-isolated case components.
        """
        case.deactivate_isolated()
        buses = case.connected_buses
        branches = case.online_branches
        gens = case.online_generators

        return buses, branches, gens


#    def _dimension_data(self, buses, branches, generators):
#        """ Returns the number of buses, branches and generators in the
#            given case, respectively.
#        """
#        nb = len(buses)
#        nl = len(branches)
#        ng = len(generators)
#
#        return nb, nl, ng


    def _pwl1_to_poly(self, generators):
        """ Converts single-block piecewise-linear costs into linear
            polynomial.
        """
        for g in generators:
            if (g.pcost_model == PW_LINEAR) and (len(g.p_cost) == 2):
                g.pwl_to_poly()

        return generators


    def _voltage_angle_var(self, refs, buses):
        """ Returns the voltage angle variable.
        """
        Va = matrix([b.v_angle_guess * (pi / 180.0) for b in buses])

        Vau = matrix(INF, (len(buses), 1))
        Val = -Vau
        Vau[refs] = Va[refs]
        Val[refs] = Va[refs]

        return Variable("Va", len(buses), Va, Val, Vau)


    def _p_gen_var(self, generators, base_mva):
        """ Returns the generator active power set-point variable.
        """
        Pg = matrix([g.p / base_mva for g in generators])

        Pmin = matrix([g.p_min / base_mva for g in generators])
        Pmax = matrix([g.p_max / base_mva for g in generators])

        return Variable("Pg", len(generators), Pg, Pmin, Pmax)


#    def _init_vars(self, buses, generators, base_mva):
#        """ Sets-up the initial variables.
#        """
#        Va = matrix([b.v_angle_guess * (pi / 180.0) for b in buses])
#        Vm = matrix([b.v_magnitude for b in buses])
#        # For buses with generators initialise Vm from gen data.
#        for g in generators:
#            Vm[buses.index(g.bus)] = g.v_magnitude
#        Pg = matrix([g.p / base_mva for g in generators])
#        Qg = matrix([g.q / base_mva for g in generators])
#
#        return Va, Vm, Pg, Qg
#
#
#    def _init_bounds(self, generators, base_mva):
#        """ Sets-up the bounds.
#        """
#        Pmin = matrix([g.p_min / base_mva for g in generators])
#        Pmax = matrix([g.p_max / base_mva for g in generators])
#        Qmin = matrix([g.q_min / base_mva for g in generators])
#        Qmax = matrix([g.q_max / base_mva for g in generators])
#
#        return Pmin, Pmax, Qmin, Qmax


    def _power_mismatch_dc(self, buses, generators, B, Pbusinj, base_mva):
        """ Returns the power mismatch constraint (B*Va + Pg = Pd).
        """
        nb, ng = len(buses), len(generators)
        # Negative bus-generator incidence matrix.
        gen_bus = matrix([buses.index(g.bus) for g in generators])
        neg_Cg = spmatrix(-1.0, gen_bus, range(ng), (nb, ng))

        Amis = sparse([B.T, neg_Cg.T]).T

        Pd = matrix([bus.p_demand for bus in buses])
        Gs = matrix([bus.g_shunt for bus in buses])

        bmis = -(Pd - Gs) / base_mva - Pbusinj

        return LinearConstraint("Pmis", Amis, bmis, bmis, ["Va", "Pg"])


    def _branch_flow_dc(self, branches, Bf, Pfinj, base_mva):
        """ Returns the branch flow limit constraint.  The real power flows
            at the from end the lines are related to the bus voltage angles
            by Pf = Bf * Va + Pfinj.
        """
        # Indexes of constrained lines.
        il = matrix([i for i,l in enumerate(branches) if 0.0 < l.s_max < 1e10])
        lpf = matrix(-INF, (len(il), 1))
        rate_a = matrix([l.s_max / base_mva for l in branches])
        upf = rate_a[il] - Pfinj[il]
        upt = rate_a[il] + Pfinj[il]

        Pf = LinearConstraint("Pf",  Bf[il, :], lpf, upf, ["Va"])
        Pt = LinearConstraint("Pt", -Bf[il, :], lpf, upt, ["Va"])

        return Pf, Pt


#    def _voltage_angle_reference(self, Va, nb, refs):
#        """ Returns the voltage angle reference constraint.
#        """
#        Vau = matrix(INF, (nb, 1))
#        Val = -Vau
#        Vau[refs] = Va[refs]
#        Val[refs] = Va[refs]
#
#        return Vau, Val


    def _voltage_angle_diff_limit(self, buses, branches):
        """ Returns the constraint on the branch voltage angle differences.
        """
        nb = len(buses)

        if not self.ignore_ang_lim:
            iang = matrix([i for i, b in enumerate(branches)
                           if (b.ang_min and (b.ang_min > -360.0))
                           or (b.ang_max and (b.ang_max < 360.0))])
            iangl = matrix([i for i, b in enumerate(branches)
                            if b.ang_min is not None])[iang]
            iangh = matrix([i for i, b in enumerate(branches)
                            if b.ang_max is not None])[iang]
            nang = len(iang)

            if nang > 0:
                ii = matrix([range(nang), range(nang)])
                jjf = matrix([buses.index(b.from_bus) for b in branches])[iang]
                jjt = matrix([buses.index(b.to_bus) for b in branches])[iang]
                jj = matrix([jjf, jjt])
                Aang = spmatrix(matrix([matrix(1.0, (nang, 1)),
                                        matrix(-1.0, (nang, 1))]),
                                        ii, jj, (nang, nb))
                uang = matrix(INF, (nang, 1))
                lang = -uang
                lang[iangl] = matrix([b.ang_min * (pi / 180.0)
                                      for b in branches])[iangl]
                uang[iangh] = matrix([b.ang_max * (pi / 180.0)
                                      for b in branches])[iangh]
            else:
                Aang = spmatrix([], [], [], (0, nb))
                lang = matrix()
                uang = matrix()
        else:
            Aang = spmatrix([], [], [], (0, nb))
            lang = matrix()
            uang = matrix()
            iang = matrix()

        return LinearConstraint("ang", Aang, lang, uang, ["Va"])


    def _pwl_gen_costs(self, generators, base_mva):
        """ Returns the basin constraints for piece-wise linear gen cost
            variables.

            References:
                C. E. Murillo-Sanchez, "makeAy.m", MATPOWER, PSERC Cornell,
                version 4.0b1, http://www.pserc.cornell.edu/matpower/, Dec 09
        """
        ng = len(generators)
        if self.dc:
            pgbas = 0
#            qgbas = None
            ybas = ng
        else:
            pgbas = 0
#            qgbas = ng + 1
            ybas = ng + ng # nq = ng

        gpwl = [g for g in generators if g.pcost_model == PW_LINEAR]
        ny = len(gpwl) # number of extra y variables.
        if ny > 0:
            # Total number of cost points.
            nc = len([p for g in gpwl for p in g.p_cost])
            Ay = spmatrix([], [], [], (nc - ny, ybas + ny -1))
            by = matrix()

            k = 0
            for i, g in enumerate(gpwl):
                ns = len(g.p_cost)
                p = matrix([p / base_mva for p, c in g.p_cost])
                c = matrix([c for p, c in g.p_cost])
                m = div(diff(c), diff(p))
                if 0.0 in diff(p):
                    logger.error("Bad Pcost data: %s" % p)
                b = mul(m, p[:ns - 1] - c[:ns - 1])
                by = matrix([by, b.T])

                Ay[k:k + ns - 2, pgbas + i]
                Ay[k:k + ns - 2, ybas + i] = matrix(-1., (ns, 1))
                k += (ns - 1)
                # TODO: Repeat for Q cost.
        else:
            Ay = spmatrix([], [], [], (ybas + ny, 0))
            by = matrix()

        if self.dc:
            return LinearConstraint("ycon", Ay, 0, by, ["Pg", "y"])
        else:
            return LinearConstraint("ycon", Ay, 0, by, ["Pg", "Qg", "y"])


    def _construct_opf_model(self, vars, constraints, *kw_args):
        """ Returns an OPF model with the given variables, constraints and
            user data.
        """
        opf = OPFModel()

        for var in vars:
            opf.add_var(var)

        for constr in constraints:
            opf.add_constr(constr)

        for k, v in kw_args.iteritems():
            setattr(opf, "_" + k, v)

        return opf


#    def _construct_opf_model(self, Va, Val, Vau, nb, Pg, Pmin, Pmax, ng,
#                             Amis, bmis, lpf, upf, upt, Aang, lang, uang,
#                             Ay, by, ny, Bf, Pfinj, il):
#        """ Returns an OPF model with variables and constraints.
#        """
#        if self.dc:
#            om = OPFModel()
#
#            om._Bf = Bf
#            om._Pfinj = Pfinj
#
#            om.add_var(Variable("Va", nb, Va, Val, Vau))
#            om.add_var(Variable("Pg", ng, Pg, Pmin, Pmax))
#
#            om.add_constr(LinearConstraint("Pmis", Amis, bmis, bmis,
#                                           ["Va", "Pg"]))
#            om.add_constr(LinearConstraint("Pf", Bf[il, :], lpf, upf, ["Va"]))
#            om.add_constr(LinearConstraint("Pt", -Bf[il, :], lpf, upt, ["Va"]))
#            om.add_constr(LinearConstraint("ang", Aang, lang, uang, ["Va"]))
#            ycon_vars = ['Pg', 'y']
#        else:
#            raise NotImplementedError
#            ycon_vars = ['Pg', 'Qg', 'y']
#
#        if ny > 0:
#            om.add_var(Variable("y", ny))
#            om.add_constr(LinearConstraint("ycon", Ay, 0, by, ycon_vars))
#
#        return om

#------------------------------------------------------------------------------
#  "Solver" class:
#------------------------------------------------------------------------------

class Solver:
    """ Defines a base class for many solvers.
    """

    def __init__(self, om):
        # Optimal power flow model.
        self.om = om


    def solve(self):
        """ Solves optimal power flow and returns a results dict.
        """
        raise NotImplementedError


    def _unpack_model(self, om):
        """ Returns data from the OPF model.
        """
        buses = om.case.connected_buses
        branches = om.case.online_branches
        gens = om.case.online_generators

        cp = om.get_cost_params()

        Bf = om._Bf
        Pfinj = om._Pfinj

        return buses, branches, gens, cp, Bf, Pfinj


    def _dimension_data(self, buses, branches, generators):
        """ Returns the problem dimensions.
        """
        ipol = self.ipol = matrix([i for i, g in enumerate(generators)
                                   if g.pcost_model == POLYNOMIAL])
        ipwl = self.ipwl = matrix([i for i, g in enumerate(generators)
                                   if g.pcost_model == PW_LINEAR])
        nb = len(buses)
        nl = len(branches)
        # Number of general cost vars, w.
        nw = self.N.size[0]
        # Number of piece-wise linear costs.
        ny = self.om.get_var_N("y")
        # Total number of control variables.
        nxyz = self.om.get_var_N()

        return ipol, ipwl, nb, nl, nw, ny, nxyz


    def _split_constraints(self, om):
        """ Returns the linear problem constraints.
        """
        A, l, u = om.linear_constraints() # l <= A*x <= u
        assert len(l) == len(u)

        # Indexes for equality, greater than (unbounded above), less than
        # (unbounded below) and doubly-bounded constraints.
        ieq = matrix([i for i, v in enumerate(abs(u - l)) if v < EPS])
        igt = matrix([i for i in range(len(l)) if u[i] > 1e10 and l[i] >-1e10])
        ilt = matrix([i for i in range(len(l)) if u[i] < -1e10 and l[i] <1e10])
        ibx = matrix([i for i in range(len(l))
                      if (abs(u[i] - l[i]) > EPS) and
                      (u[i] < 1e10) and (l[i] > -1e10)])

        Aeq = A[ieq, :]
        beq = u[ieq, :]
        Aieq = sparse([A[ilt, :], -A[igt, :], A[ibx, :], -A[ibx, :]])
        bieq = matrix([u[ilt], -l[igt], u[ibx], -l[ibx]])

        return Aeq, beq, Aieq, bieq

#------------------------------------------------------------------------------
#  "DCOPFSolver" class:
#------------------------------------------------------------------------------

class DCOPFSolver(Solver):
    """ Defines a solver for DC optimal power flow.

        References:
            Ray Zimmerman, "dcopf_solver.m", MATPOWER, PSERC Cornell, v4.0b1,
            http://www.pserc.cornell.edu/matpower/, December 2009
    """

    def __init__(self, om, solver=None):
        """ Initialises a new DCOPFSolver instance.
        """
        super(DCOPFSolver, self).__init__(om)

        # Specify an alternative solver ("mosek" (or "glpk" for linear
        # formulation)). Specify None to use the CVXOPT solver..
        self.solver = solver


    def solve(self):
        """ Solves DC optimal power flow and returns a results dict.
        """
        base_mva = self.om.case.base_mva
        # Unpack the OPF model.
        buses, branches, generators = self._unpack_model(self.om)
        # Compute problem dimensions.
        ipol, ipwl, nb, nl, nw, ny, nxyz = self._dimension_data(buses,
                                                                branches,
                                                                generators)
        # Split the constraints in equality and inequality.
        Aeq, beq, Aieq, bieq = self._split_constraints(self.om)
        # Piece-wise linear components of the objective function.
        Npwl, Hpwl, Cpwl, fparm_pwl = self._pwl_costs(nxyz)
        # Quadratic components of the objective function.
        Pg, Npol, Hpol, Cpol, fparm_pol = self._quadratic_costs(generators,
                                                                ipol, nxyz,
                                                                base_mva)
        # Combine pwl, poly and user costs.
        NN, HHw, CCw, ffparm = self._combine_costs(Npwl, Npol, N,
                                                   Hpwl, Hpol, H,
                                                   Cpwl, Cpol, Cw,
                                                   fparm_pwl, fparm_pol, fparm,
                                                   any_pwl, npol, nw)
        # Transform quadratic coefficients for w into coefficients for X.
        HH, CC, C0 = self._transform_coefficients(NN, HHw, CCw, ffparm, polycf,
                                                  any_pwl, npol, nw)
        # Bounds on the optimisation variables..
#        self.var_bounds()

        # Select an interior initial point for interior point solver.
        x0 = self._initial_interior_point(self.om)

        # Call the quadratic/linear solver.
        solution = self._run_opf(HH, CC, Aieq, bieq, Aeq, beq, x0)


    def _pwl_costs(self, nxyz):
        """ Returns the piece-wise linear components of the objective function.
        """
        if self.ny > 0:
            Npwl = spmatrix(1.0, )
            Hpwl = 0
            Cpwl = 1
            fparm_pwl = matrix([1, 0, 0, 1])
        else:
            Npwl = spmatrix([], [], [], (0, nxyz))
            Hpwl = matrix()
            Cpwl = matrix()
            fparm_pwl = matrix()

        return Npwl, Hpwl, Cpwl, fparm_pwl


    def _quadratic_costs(self, generators, ipol, nxyz, base_mva):
        """ Returns the quadratic cost components of the objective function.
        """
        npol = len(ipol)

        if [g for g in generators[ipol] if len(g.p_cost) > 3]:
            logger.error("Order of polynomial cost greater than quadratic.")

        iqdr = matrix([i for i, g in enumerate(generators[ipol])
                       if len(g.p_cost) == 3])
        ilin = matrix([i for i, g in enumerate(generators[ipol])
                       if len(g.p_cost) == 2])

        polycf = matrix(0.0, (npol, 3))
        if len(iqdr) > 0:
            polycf[iqdr, :] = matrix([g.p_cost for g in
                                   generators[ipol[iqdr]]])

        polycf[ilin, 1:2] = matrix([g.p_cost[:2] for g in
                                   generators[ipol[iqdr]]])

        # Convert to per-unit.
        polycf *= spdiag([base_mva**2, base_mva, 1])

        Pg = self.om.get_var("Pg")
        Npol = spmatrix(1.0, range(npol), Pg - 1 + ipol, (npol, nxyz))
        Hpol = spmatrix(2 * polycf[:, 1], range(npol), range(npol))
        Cpol = polycf[:, 2]
        fparm_pol = matrix(1., (npol, 1)) * matrix([1, 0, 0, 1])

        return Pg, Npol, Hpol, Cpol, fparm_pol


    def _combine_costs(self, Npwl, Npol, N, Hpwl, Hpol, H, Cpwl, Cpol, Cw,
                      fparm_pwl, fparm_pol, fparm, any_pwl, npol, nw):
        NN = sparse([Npwl, Npol, N])
        HHw = sparse([Hpwl,
                      spmatrix([], [], [], (any_pwl, npol + nw)),
                      spmatrix([], [], [], (npol, any_pwl)),
                      Hpol,
                      spmatrix([], [], [], (npol, nw)),
                      spmatrix([], [], [], (nw, any_pwl + npol)),
                      H])
        CCw = matrix([Cpwl, Cpol, Cw])
        ffparm = matrix([fparm_pwl, fparm_pol, fparm])

        return NN, HHw, CCw, ffparm


    def _transform_coefficients(self, NN, HHw, CCw, ffparm, polycf,
                               any_pwl, npol, nw):
        """ Transforms quadratic coefficients for w into coefficients for X.
        """
        nnw = any_pwl + npol + nw
        M = spmatrix(ffparm[:, 3], range(nnw), range(nnw))
        MR = M * ffparm[:, 2]
        HMR = HHw * MR
        MN = M * NN
        HH = MN.T * HHw, MN
        CC = MN.T * (CCw - HMR)
        # Constant term of cost.
        C0 = 1./2. * MR.T * HMR + sum(polycf[:, 3])

        return HH, CC, C0


#    def var_bounds(self):
#        """ Returns bounds on the optimisation variables.
#        """
#        x0, LB, UB = self.om.getv()
#        return x0, LB, UB


    def _initial_interior_point(self, om, buses, generators, base_mva):
        """ Selects an interior initial point for interior point solver.
        """
#        x0 = matrix(0., (om.get_var_N(), 1))

        xva = matrix([bus.v_angle_guess * pi / 180 for bus in buses])
        # FIXME: Initialise V from any present generators.
        xvm = matrix([bus.v_magnitude_guess for bus in buses])
        xpg = matrix([g.p / base_mva for g in generators])
        xqg = matrix([g.q / base_mva for g in generators])
        x0 = matrix([xva, xvm, xpg, xqg])

        return x0


    def _run_opf(self, P, q, G, h, A, b, x0):
        """ Solves the either quadratic or linear program.
        """
        if len(P) > 0:
            solution = solvers.qp(P, q, G, h, A, b, self.solver, {"x": x0})
        else:
            solution = solvers.lp(q, G, h, A, b, self.solver, {"x": x0})

        return solution

#------------------------------------------------------------------------------
#  "CVXOPTSolver" class:
#------------------------------------------------------------------------------

class CVXOPTSolver(Solver):
    """ Solves AC optimal power flow using convex optimization.
    """

    def solve(self):
        # Unpack the OPF model.
        buses, branches, generators = self._unpack_model(self.om)
        # Compute problem dimensions.
        ipol, ipwl, nb, nl, nw, ny, nxyz = self._dimension_data(buses,
                                                                branches,
                                                                generators)
        # Split the constraints in equality and inequality.
        Aeq, beq, Aieq, bieq = self._split_constraints(self.om)

        # Get the function that evaluates the objective and nonlinear
        # constraint functions.
        F = self._objective_and_nonlinear_constraint_function()

        # Solve the convex optimization problem.
        result = self._run_opf(F, Aieq, bieq, Aeq, beq)


    def _objective_and_nonlinear_constraint_function(self, om, buses, branches,
                                                     generators, nb, nl, ng,
                                                     base_mva):
        """ Returns a function that evaluates the objective and nonlinear
            constraint functions.
        """
        j = 0 + 1j

        # Optimisation variables.
        Va = om.get_var("Va")
        Vm = om.get_var("Vm")
        Pg = om.get_var("Pg")
        Qg = om.get_var("Qg")

        # The number of non-linear equality constraints.
        neq = 2 * nb
        # The number of control variables.
        nc = 2 * nb + 2 * ng

        # Definition of indexes for the optimisation variable vector.
        # Voltage phase angle.
#        ph_base = 0
#        ph_end  = ph_base + nb - 1;
#        # Voltage amplitude.
#        v_base  = ph_end + 1
#        v_end   = v_base + nb - 1
#        # Active generation.
#        pg_base = v_end + 1
#        pg_end  = pg_base + ng - 1
#        # Reactive generation.
#        qg_base = pg_end + 1
#        qg_end  = qg_base + ng - 1


        def F(x=None, z=None):
            """ Evaluates the objective and nonlinear constraint functions.
            """
            if x is None:
                # Number of non-linear constraints.
                m = neq

                x0 = matrix(0., (om.get_var_N(), 1))
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

            df0= matrix([matrix(0.0, (v_end, 1)), df_dPgQg])

            # Evaluate nonlinear equality constraints -------------------------

            # Net complex bus power injection vector in p.u.
            s = matrix([complex(case.p_surplus(v), case.q_surplus(v)) /base_mva
                        for v in buses])

            # Bus voltage vector.
            v_angle = x[ph_base:ph_end + 1]
            v_magnitude = x[v_base:v_end]
#            Va0r = Va0 * pi / 180 #convert to radians
            v = mul(v_magnitude, exp(j * v_angle)) #element-wise product

            # Evaluate the power flow equations.
            Y, Yfrom, Yto = case.Y
            mismatch = mul(v, conj(Y * v)) - s

            # Evaluate power balance equality constraint function values.
            fk_eq = matrix([mismatch.real(), mismatch.imag()])

            # Evaluate nonlinear inequality constraints -----------------------

            # Branch power flow limit inequality constraint function values.
            from_idxs = matrix([buses.index(e.from_bus) for e in branches])
            to_idxs = matrix([buses.index(e.to_bus) for e in branches])
            # Complex power in p.u. injected at the from bus.
            s_from = mul(v[from_idxs], conj(Yfrom, v))
            # Complex power in p.u. injected at the to bus.
            s_to = mul(v[to_idxs], conj(Yto, v))

            # Apparent power flow limit in MVA, |S|.
            s_max = matrix([e.s_max for e in branches])

            # FIXME: Implement active power and current magnitude limits.
            fk_ieq = matrix([abs(s_from) - s_max, abs(s_to) - s_max])

            # Evaluate partial derivatives of constraints ---------------------

            # Partial derivative of injected bus power
            dS_dVm, dS_dVa = dSbus_dV(Y, v) # w.r.t voltage
            pv_idxs = matrix([buses.index(bus) for bus in buses])
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
                dSbr_dV(branches, Yfrom, Yto, v)

            # Magnitude of complex power flow.
            df_dVa, dt_dVa, df_dVm, dt_dVm = \
                dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, s_from, s_to)

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

            i = matrix(range(pg_base, qg_end + 1)).T
            H = spmatrix(matrix([d2f_d2Pg, d2f_d2Qg]), i, i)

            return f, df, H

        return F


    def _run_opf(self, F, G, h, A, b):
        """ Solves the convex optimal power flow problem.
        """
        # cp(F, G=None, h=None, dims=None, A=None, b=None, kktsolver=None)
        #
        #     minimize    f0(x)
        #     subject to  fk(x) <= 0, k = 1, ..., mnl
        #                 G*x   <= h
        #                 A*x   =  b.
        dims = None
        solution = solvers.cp(F, G, h, dims, A, b)

        return solution

#------------------------------------------------------------------------------
#  "Indexed" class:
#------------------------------------------------------------------------------

class Indexed(Named):
    def __init__(self, name, N):
        self.name = name

        # Starting index.
        self.i0 = 0

        # Ending index.
        self.iN = 0

        # Number of variables.
        self.N = 0

        # Number of variable sets.
        self.NS = 0

        # Ordered list of variable sets.
        self.order = {}

#------------------------------------------------------------------------------
#  "Variable" class:
#------------------------------------------------------------------------------

class Variable(Indexed):
    """ Defines a set of variables.
    """

    def __init__(self, name, N, v0=None, vl=None , vu=None):
        """ Initialises a new Variable instance.
        """
        super(Variable, self).__init__(name, N)

        # Initial value of the variables. Zero by default.
        if v0 is None:
            self.v0 = matrix(0.0, (N, 1))
        else:
            self.v0 = v0

        # Lower bound on the variables. Unbounded below be default.
        if vl is None:
            self.vl = matrix(-INF, (N, 1))
        else:
            self.vl = vl

        # Upper bound on the variables. Unbounded above by default.
        if vu is None:
            self.vu = matrix(INF, (N, 1))
        else:
            self.vu = vu

#------------------------------------------------------------------------------
#  "NonLinearConstraint" class:
#------------------------------------------------------------------------------

class NonLinearConstraint(Indexed):
    pass

#------------------------------------------------------------------------------
#  "LinearConstraint" class:
#------------------------------------------------------------------------------

class LinearConstraint(Indexed):
    def __init__(self, name, A, l, u, vs):
        super(LinearConstraint, self).__init__(name, 0)
        self.A = A
        self.l = l
        self.u = u
        self.vs = vs

#------------------------------------------------------------------------------
#  "Cost" class:
#------------------------------------------------------------------------------

class Cost(Indexed):
    def __init__(self):
        self.N = None
        self.H = None
        self.Cw = None
        self.dd = None
        self.rh = None
        self.kk = None
        self.mm = None
        self.vs = None
        self.params = None

#------------------------------------------------------------------------------
#  "OPFModel" class:
#------------------------------------------------------------------------------

class OPFModel:
    def __init__(self, case):
        self.case = case
        self.vars = []
        self.nln_constraints = []
        self.lin_constraints = []
        self.costs = []

# EOF -------------------------------------------------------------------------
