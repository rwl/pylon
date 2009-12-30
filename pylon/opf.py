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

""" Defines a generalised OPF solver and an OPF model.

    References:
        Ray Zimmerman, "opf.m", MATPOWER, PSERC Cornell, version 4.0b1,
        http://www.pserc.cornell.edu/matpower/, December 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from math import pi

import numpy

from cvxopt import matrix, spmatrix, sparse, spdiag, div, mul
from cvxopt import solvers

from util import Named
from case import REFERENCE, POLYNOMIAL, PIECEWISE_LINEAR

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

INF = -1e10
EPS =  2**-52

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

    def __init__(self, case, dc=True, show_progress=True, max_iterations=100,
                 absolute_tol=1e-7, relative_tol=1e-6, feasibility_tol=1e-7,
                 ignore_ang_lim=True):
        """ Initialises a new OPF instance.
        """
        # Case under optimisation.
        self.case = case

        # Use DC power flow formulation.
        self.dc = dc

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

        # Ignore angle difference limits for branches even if specified.
        self.ignore_ang_lim = ignore_ang_lim


    def solve(self):
        """ Solves an optimal power flow and returns a results dictionary.
        """
        base_mva = self.case.base_mva
        # Set algorithm parameters.
        self.algorithm_parameters()
        # Check for one reference bus.
        refs = self.ref_check(self.case)
        # Remove isolated components.
        buses, branches, gens = self.remove_isolated(self.case)
        # Zero the case result attributes.
        self.case.reset()
        # Compute problem dimensions.
        nb, nl, ng = self.dimension_data(buses, branches, gens)
        # Convert single-block piecewise-linear costs into linear polynomial.
        generators = self.pwl1_to_poly(gens)
        # Set-up initial problem variables.
        Va, Vm, Pg, Qg = self.init_vars(buses, generators, base_mva)
        # Set-up initial problem bounds.
        Pmin, Pmax, Qmin, Qmax = self.init_bounds(generators, base_mva)

        if self.dc: # DC model.
            # Get the susceptance matrices and phase shift injection vectors.
            B, Bf, Pbusinj, Pfinj = self.case.B
            # Power mismatch constraints (B*Va + Pg = Pd).
            Amis, bmis = self.power_mismatch(buses, generators, nb, ng,
                                             B, Pbusinj, base_mva)
            # Branch flow limit constraints.
            lpf, upf, upt, il = self.branch_flow(branches, Pfinj, base_mva)
            # Reference, voltage angle constraint.
            Vau, Val = self.voltage_angle_reference(Va, nb, refs)
        else:
            raise NotImplementedError

        # Branch voltage angle difference limits.
        Aang, lang, uang, iang = self.voltage_angle_diff_limit(buses, branches)

        # Piece-wise linear gencost constraints.
        Ay, by, ny = self.pwl_gen_costs(generators, ng, base_mva)

        # Add variables and constraints to the OPF model object.
        om = self.construct_opf_model(Va, Val, Vau, nb, Pg, Pmin, Pmax, ng,
                                      Amis, bmis, lpf, upf, lpf, upt,
                                      Aang, lang, uang, Ay, by, ny,
                                      Bf, Pfinj, il)

        # Construct an OPF model object.
#        if self.dc:
#            om = OPFModel(
#                variables=[
#                    Variable("Va", nb, Va, Val, Vau),
#                    Variable("Pg", ng, Pg, Pmin, Pmax)],
#                constraints=[
#                    LinearConstraint("Pmis", Amis, bmis, bmis, ["Va", "Pg"]),
#                    LinearConstraint("Pf", Bf[il, :], lpf, upf, ["Va"]),
#                    LinearConstraint("Pt", -Bf[il, :], lpf, upt, ["Va"]),
#                    LinearConstraint("ang", Aang, lang, uang, ["Va"])]
#            )
#            if ny > 0:
#                om.add_var(Variable("y", ny))
#                om.add_constr(LinearConstraint("ycon", Ay, 0, by, ['Pg', 'y']))
#            om._Bf = Bf
#            om._Pfinj = Pfinj
#        else:
#            raise NotImplementedError
#            ycon_vars = ['Pg', 'Qg', 'y']

        # Call the specific solver.
        if self.dc:
            result = DCOPFSolver(om).solve()
#        else:
#            result = CVXOPTSolver(om).solve()


    def algorithm_parameters(self):
        """ Sets the parameters of the CVXOPT solver algorithm.
        """
        solvers.options["show_progress"] = self.show_progress
        solvers.options["maxiters"] = self.max_iterations
        solvers.options["abstol"] = self.absolute_tol
        solvers.options["reltol"] = self.relative_tol
        solvers.options["feastol"] = self.feasibility_tol


    def ref_check(self, case):
        """ Checks that there is only one reference bus.
        """
        refs = matrix([i for i, bus in enumerate(case.buses)
                      if bus.type == REFERENCE])

        if not (0 < len(refs) <= 1):
            logger.error("OPF requires a single reference bus.")

        return refs


    def remove_isolated(self, case):
        """ Returns non-isolated case components.
        """
        case.deactivate_isolated()
        buses = case.connected_buses
        branches = case.online_branches
        gens = case.online_generators

        return buses, branches, gens


    def dimension_data(self, buses, branches, generators):
        """ Returns the number of buses, branches and generators in the
            given case, respectively.
        """
        nb = len(buses)
        nl = len(branches)
        ng = len(generators)

        return nb, nl, ng


    def pwl1_to_poly(self, generators):
        """ Converts single-block piecewise-linear costs into linear
            polynomial.
        """
        for g in generators:
            if (g.cost_model == POLYNOMIAL) and (len(g.p_cost == 2)):
                g.pwl_to_poly()

        return generators


    def init_vars(self, buses, generators, base_mva):
        """ Sets-up the initial variables.
        """
        Va = matrix([b.v_angle_guess * (pi / 180.0) for b in buses])
        Vm = matrix([b.v_magnitude for b in self.buses])
        # For buses with generators initialise Vm from gen data.
        for g in generators:
            Vm[buses.index(g.bus)] = g.v_magnitude
        Pg = matrix([g.p / base_mva for g in generators])
        Qg = matrix([g.q / base_mva for g in generators])

        return Va, Vm, Pg, Qg


    def init_bounds(self, generators, base_mva):
        """ Sets-up the initial bounds.
        """
        Pmin = matrix([g.p_min / base_mva for g in generators])
        Pmax = matrix([g.p_max / base_mva for g in generators])
        Qmin = matrix([g.q_min / base_mva for g in generators])
        Qmax = matrix([g.q_max / base_mva for g in generators])

        return Pmin, Pmax, Qmin, Qmax


    def power_mismatch(self, buses, generators, nb, ng, B, Pbusinj, base_mva):
        """ Returns the power mismatch constraint (B*Va + Pg = Pd).
        """
        # Negative bus-generator incidence matrix.
        gen_bus = matrix([buses.index(g.bus) for g in generators])
        neg_Cg = spmatrix(-1.0, gen_bus, range(ng), (nb, ng))

        Amis = sparse([B, neg_Cg])

        Pd = matrix([bus.p_demand for bus in buses])
        Gs = matrix([bus.g_shunt for bus in buses])

        bmis = -(Pd - Gs) / base_mva - Pbusinj

        return Amis, bmis


    def branch_flow(self, branches, Pfinj, base_mva):
        """ Returns the branch flow limit constraint.  The real power flows
            at the from end the lines are related to the bus voltage angles
            by Pf = Bf * Va + Pfinj.
        """
        # Indexes of constrained lines.
        il = matrix([i for i,l in enumerate(branches) if 0.0 < l.s_max < 1e10])
        lpf = matrix(-INF, (len(il), 1))
        rate_a = matrix([l.s_max / base_mva for l in branches[il]])
        upf = rate_a - Pfinj[il]
        upt = rate_a + Pfinj[il]

        return lpf, upf, upt, il


    def voltage_angle_reference(self, Va, nb, refs):
        """ Returns the voltage angle reference constraint.
        """
        Vau = matrix(INF, (nb, 1))
        Val = -Vau
        Vau[refs] = Va[refs]
        Val[refs] = Va[refs]

        return Vau, Val


    def voltage_angle_diff_limit(self, buses, branches, nb):
        """ Returns the constraint on the branch voltage angle differences.
        """
        if not self.ignore_ang_lim:
            iang = matrix([i for i, b in enumerate(branches)
                           if (b.ang_min and (b.ang_min > -360.0))
                           or (b.ang_max and (b.ang_max < 360.0))])
            iangl = matrix([i for i, b in enumerate(branches[iang])
                            if b.ang_min is not None])
            iangh = matrix([i for i, b in enumerate(branches[iang])
                            if b.ang_max is not None])
            nang = len(iang)

            if nang > 0:
                ii = matrix([range(nang), range(nang)])
                jj = matrix([[buses.index(b.from_bus) for b in branches[iang]],
                             [buses.index(b.to_bus) for b in branches[iang]]])
                Aang = spmatrix(matrix([matrix(1.0, (nang, 1)),
                                        matrix(-1.0, (nang, 1))]),
                                        ii, jj, (nang, nb))
                uang = matrix(INF, (nang, 1))
                lang = -uang
                lang[iangl] = matrix([b.ang_min * (pi / 180.0)
                                      for b in branches[iangl]])
                uang[iangh] = matrix([b.ang_max * (pi / 180.0)
                                      for b in branches[iangh]])
            else:
                Aang = spmatrix([], [], [], (0, nb))
                lang = matrix()
                uang = matrix()
        else:
            Aang = spmatrix([], [], [], (0, nb))
            lang = matrix()
            uang = matrix()
            iang = matrix()

        return Aang, lang, uang, iang


    def pwl_gen_costs(self, generators, ng, base_mva):
        """ Returns the basin constraints for piece-wise linear gen cost
            variables.

            References:
                C. E. Murillo-Sanchez, "makeAy.m", MATPOWER, PSERC Cornell,
                version 4.0b1, http://www.pserc.cornell.edu/matpower/, Dec 09
        """
        if self.dc:
            pgbas = 0
#            qgbas = None
            ybas = ng + 1
        else:
            pgbas = 0
#            qgbas = ng + 1
            ybas = ng + 1 + ng # nq = ng

        gpwl = [g for g in generators if g.cost_model == PIECEWISE_LINEAR]
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
                m = div(numpy.diff(c), numpy.diff(p))
                if 0.0 in numpy.diff(p):
                    logger.error("Bad Pcost data: %s" % p)
                b = mul(m, p[:ns - 1] - c[:ns - 1])
                by = matrix([by, b.T])

                Ay[k:k + ns - 2, pgbas + i]
                Ay[k:k + ns - 2, ybas + i] = matrix(-1., (ns, 1))
                k += (ns - 1)
                # TODO: Repeat for Q cost.
        else:
            Ay = spmatrix([], [], [] (ybas + ny, 0))
            by = matrix()

        return Ay, by, ny


    def construct_opf_model(self, Va, Val, Vau, nb, Pg, Pmin, Pmax, ng,
                            Amis, bmis, lpf, upf, lpf, upt, Aang, lang, uang,
                            Ay, by, ny, Bf, Pfinj, il):
        """ Returns an OPF model with variables and constraints.
        """
        if self.dc:
            om = OPFModel()

            om._Bf = Bf
            om._Pfinj = Pfinj

            om.add_var(Variable("Va", nb, Va, Val, Vau))
            om.add_var(Variable("Pg", ng, Pg, Pmin, Pmax))

            om.add_constr(LinearConstraint("Pmis", Amis, bmis, bmis, ["Va", "Pg"]))
            om.add_constr(LinearConstraint("Pf", Bf[il, :], lpf, upf, ["Va"]))
            om.add_constr(LinearConstraint("Pt", -Bf[il, :], lpf, upt, ["Va"]))
            om.add_constr(LinearConstraint("ang", Aang, lang, uang, ["Va"]))
            ycon_vars = ['Pg', 'y']
        else:
            raise NotImplementedError
            ycon_vars = ['Pg', 'Qg', 'y']

        if ny > 0:
            om.add_var(Variable("y", ny))
            om.add_constr(LinearConstraint("ycon", Ay, 0, by, ycon_vars))

        return om

#------------------------------------------------------------------------------
#  "DCOPFSolver" class:
#------------------------------------------------------------------------------

class DCOPFSolver:
    """ Defines a solver for DC optimal power flow.

        References:
            Ray Zimmerman, "dcopf_solver.m", MATPOWER, PSERC Cornell, v4.0b1,
            http://www.pserc.cornell.edu/matpower/, December 2009
    """

    def __init__(self, om, solver=None):
        """ Initialises a new DCOPFSolver instance.
        """
        # Optimal power flow model.
        self.om = om

        # Specify an alternative solver ("mosek" (or "glpk" for linear
        # formulation)). Specify None to use the CVXOPT solver..
        self.solver = solver


    def solve(self):
        """ Solves DC optimal power flow and returns a results dict.
        """
        # Unpack the OPF model.
        buses, branches, generators = self.unpack_model(self.om)
        base_mva = self.om.case.base_mva
        # Compute problem dimensions.
        ipol, ipwl, nb, nl, nw, ny, nxyz = self.data_dims(buses, branches,
                                                          generators)
        # Split the constraints in equality and inequality.
        Aeq, beq, Aieq, bieq = self.split_constraints(self.om)
        # Piece-wise linear components of the objective function.
        Npwl, Hpwl, Cpwl, fparm_pwl = self.pwl_costs(nxyz)
        # Quadratic components of the objective function.
        Pg, Npol, Hpol, Cpol, fparm_pol = self.quadratic_costs(generators,
                                                               ipol, nxyz,
                                                               base_mva)
        # Combine pwl, poly and user costs.
        NN, HHw, CCw, ffparm = self.combine_costs(Npwl, Npol, N, Hpwl, Hpol, H,
                                                  Cpwl, Cpol, Cw,
                                                  fparm_pwl, fparm_pol, fparm,
                                                  any_pwl, npol, nw)
        # Transform quadratic coefficients for w into coefficients for X.
        HH, CC, C0 = self.transform_coefficients(NN, HHw, CCw, ffparm, polycf,
                                                 any_pwl, npol, nw)
        # Bounds on the optimisation variables..
#        self.var_bounds()

        # Call the quadratic/linear solver.
        solution = self.run_opf(HH, CC, Aieq, bieq, Aeq, beq)


    def unpack_model(self, om):
        """ Returns data from the OPF model.
        """
        buses = om.case.connected_buses
        branches = om.case.online_branches
        gens = om.case.online_generators

        cp = om.get_cost_params()

        Bf = om._Bf
        Pfinj = om._Pfinj

        return buses, branches, gens, cp, Bf, Pfinj


    def data_dims(self, buses, branches, generators):
        """ Returns the problem dimensions.
        """
        ipol = self.ipol = matrix([i for i, g in enumerate(generators)
                                   if g.cost_model == POLYNOMIAL])
        ipwl = self.ipwl = matrix([i for i, g in enumerate(generators)
                                   if g.cost_model == PIECEWISE_LINEAR])
        nb = len(buses)
        nl = len(branches)
        # Number of general cost vars, w.
        nw = self.N.size[0]
        # Number of piece-wise linear costs.
        ny = self.om.get_var_N("y")
        # Total number of control variables.
        nxyz = self.om.get_var_N()

        return ipol, ipwl, nb, nl, nw, ny, nxyz


    def split_constraints(self, om):
        """ Returns the linear problem constraints.
        """
        A, l, u = om.linear_constraints() # l <= A*x <= u
        assert len(l) == len(u)

        # Indexes for equality, greater than (unbounded above), less than
        # (unbounded below) and doubly-bounded constraints.
        ieq = matrix([i for i, v in enumerate(abs(u - l)) if v < EPS])
        igt = matrix([i for i in range(len(l)) if u[i] > 1e10 and l[i] > -1e10])
        ilt = matrix([i for i in range(len(l)) if u[i] < -1e10 and l[i] < 1e10])
        ibx = matrix([i for i in range(len(l))
                      if (abs(u[i] - l[i]) > EPS) and
                      (u[i] < 1e10) and (l[i] > -1e10)])

        Aeq = A[ieq, :]
        beq = u[ieq, :]
        Aieq = sparse([A[ilt, :], -A[igt, :], A[ibx, :], -A[ibx, :]])
        bieq = matrix([u[ilt], -l[igt], u[ibx], -l[ibx]])

        return Aeq, beq, Aieq, bieq


    def pwl_costs(self, nxyz):
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


    def quadratic_costs(self, generators, ipol, nxyz, base_mva):
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


    def combine_costs(self, Npwl, Npol, N, Hpwl, Hpol, H, Cpwl, Cpol, Cw,
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


    def transform_coefficients(self, NN, HHw, CCw, ffparm, polycf,
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


    def run_opf(self, P, q, G, h, A, b):
        if len(P) > 0:
#            initvals = {"x": self.x_init}
            solution = solvers.qp(P, q, G, h, A, b, self.solver)#, initvals)
        else:
#            primalstart = {"x": self.x_init}
            solution = solvers.lp(q, G, h, A, b, self.solver)#, primalstart)

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
    def __init__(self):
        self.A = None
        self.l = None
        self.u = None
        self.vs = None

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
