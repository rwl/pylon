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

from numpy import pi, diff, polyder, polyval, array, nonzero

from cvxopt import matrix, spmatrix, sparse, spdiag, div, mul, exp
from cvxopt.solvers import qp, lp
from cvxopt import solvers

from util import Named, conj
from case import REFERENCE
from generator import POLYNOMIAL, PW_LINEAR
from pdipm import pdipm, pdipm_qp

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

class OPF(object):
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

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves an optimal power flow and returns a results dictionary.
        """
        # Set algorithm parameters.
        opts = self._algorithm_parameters()

        # Build an OPF model with variables and constraints.
        om = self._construct_opf_model(self.case)

        # Call the specific solver.
        if self.dc:
            result = DCOPFSolver(om).solve()
        else:
#            result = CVXOPTSolver(om).solve()
            result = PDIPMSolver(om, opts).solve()

        return result

    #--------------------------------------------------------------------------
    #  Private interface:
    #--------------------------------------------------------------------------

    def _construct_opf_model(self, case):
        base_mva = case.base_mva

        # Check for one reference bus.
        oneref, refs = self._ref_check(case)
        if not oneref:
            return {"status": "error"}

        # Remove isolated components.
        bs, ln, gn = self._remove_isolated(case)

        # Zero the case result attributes.
        self.case.reset()

        # Convert single-block piecewise-linear costs into linear polynomial.
        gn = self._pwl1_to_poly(gn)

        # Set-up initial problem variables.
        Va = self._voltage_angle_var(refs, bs)
        Pg = self._p_gen_var(gn, base_mva)

        if self.dc: # DC model.
            # Get the susceptance matrices and phase shift injection vectors.
            B, Bf, Pbusinj, Pfinj = self.case.makeBdc(bs, ln)

            # Power mismatch constraints (B*Va + Pg = Pd).
            Pmis = self._power_mismatch_dc(bs, gn, B, Pbusinj, base_mva)

            # Branch flow limit constraints.
            Pf, Pt = self._branch_flow_dc(ln, Bf, Pfinj, base_mva)
        else:
            # Set-up additional AC-OPF problem variables.
            Vm = self._voltage_magnitude_var(bs, gn)
            Qg = self._q_gen_var(gn, base_mva)

            Pmis, Qmis, Sf, St = self._nln_constraints(len(bs), len(ln))

            # TODO: Dispatchable load, constant power factor constraints.
#            vl = self._dispatchable_load_constraints(gn)

            # TODO: Generator PQ capability curve constraints.
#            PQh, PQl = self._pq_capability_curve_constraints(gn)

        # Branch voltage angle difference limits.
        ang = self._voltage_angle_diff_limit(bs, ln)

        if self.dc:
            vars = [Va, Pg]
            constraints = [Pmis, Pf, Pt, ang]
        else:
            vars = [Va, Vm, Pg, Qg]
            constraints = [Pmis, Qmis, Sf, St, #PQh, PQL, vl,
                           ang]

        # Piece-wise linear generator cost constraints.
        y, ycon = self._pwl_gen_costs(gn, base_mva)
        if ycon is not None:
            vars.append(y)
            constraints.append(ycon)

        # Add variables and constraints to the OPF model object.
        opf = OPFModel(case)
        opf.add_vars(vars)
        opf.add_constraints(constraints)

        if self.dc: # user data
            opf._Bf = Bf
            opf._Pfinj = Pfinj

        return opf


    def _algorithm_parameters(self):
        """ Sets the parameters of the CVXOPT solver algorithm.
        """
        solvers.options["show_progress"] = self.show_progress
        solvers.options["maxiters"] = self.max_iterations
        solvers.options["abstol"] = self.absolute_tol
        solvers.options["reltol"] = self.relative_tol
        solvers.options["feastol"] = self.feasibility_tol

        opts = {"verbose": self.show_progress,
                "feastol": self.feasibility_tol,
                "gradtol": 1e-6,
                "comptol": 1e-6,
                "costtol": 1e-6,
                "max_it": self.max_iterations,
                "max_red": 20,
                "step_contol": False,
                "cost_mult": 1e-4}

        return opts


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


    def _pwl1_to_poly(self, generators):
        """ Converts single-block piecewise-linear costs into linear
            polynomial.
        """
        for g in generators:
            if (g.pcost_model == PW_LINEAR) and (len(g.p_cost) == 2):
                g.pwl_to_poly()

        return generators

    #--------------------------------------------------------------------------
    #  Optimisation variables:
    #--------------------------------------------------------------------------

    def _voltage_angle_var(self, refs, buses):
        """ Returns the voltage angle variable set.
        """
        Va = matrix([b.v_angle_guess * (pi / 180.0) for b in buses])

        Vau = matrix(INF, (len(buses), 1))
        Val = -Vau
        Vau[refs] = Va[refs]
        Val[refs] = Va[refs]

        return Variable("Va", len(buses), Va, Val, Vau)


    def _voltage_magnitude_var(self, buses, generators):
        """ Returns the voltage magnitude variable set.
        """
        Vm = matrix([b.v_magnitude_guess for b in buses])

        # For buses with generators initialise Vm from gen data.
        for g in generators:
            Vm[buses.index(g.bus)] = g.v_magnitude

        Vmin = matrix([b.v_min for b in buses])
        Vmax = matrix([b.v_max for b in buses])

        return Variable("Vm", len(buses), Vm, Vmin, Vmax)


    def _p_gen_var(self, generators, base_mva):
        """ Returns the generator active power set-point variable.
        """
        Pg = matrix([g.p / base_mva for g in generators])

        Pmin = matrix([g.p_min / base_mva for g in generators])
        Pmax = matrix([g.p_max / base_mva for g in generators])

        return Variable("Pg", len(generators), Pg, Pmin, Pmax)


    def _q_gen_var(self, generators, base_mva):
        """ Returns the generator reactive power variable set.
        """
        Qg = matrix([g.q / base_mva for g in generators])

        Qmin = matrix([g.q_min / base_mva for g in generators])
        Qmax = matrix([g.q_max / base_mva for g in generators])

        return Variable("Qg", len(generators), Qg, Qmin, Qmax)

    #--------------------------------------------------------------------------
    #  Constraints:
    #--------------------------------------------------------------------------

    def _nln_constraints(self, nb, nl):
        """ Returns non-linear constraints for OPF.
        """
        Pmis = NonLinearConstraint("Pmis", nb)
        Qmis = NonLinearConstraint("Qmis", nb)
        Sf = NonLinearConstraint("Sf", nl)
        St = NonLinearConstraint("St", nl)

        return Pmis, Qmis, Sf, St


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
        il = matrix([i for i,l in enumerate(branches) if 0.0 < l.rate_a < 1e10])
        lpf = matrix(-INF, (len(il), 1))
        rate_a = matrix([l.rate_a / base_mva for l in branches])
        upf = rate_a[il] - Pfinj[il]
        upt = rate_a[il] + Pfinj[il]

        Pf = LinearConstraint("Pf",  Bf[il, :], lpf, upf, ["Va"])
        Pt = LinearConstraint("Pt", -Bf[il, :], lpf, upt, ["Va"])

        return Pf, Pt


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
                by = matrix([by, b.H])

                Ay[k:k + ns - 2, pgbas + i]
                Ay[k:k + ns - 2, ybas + i] = matrix(-1., (ns, 1))
                k += (ns - 1)
                # TODO: Repeat for Q cost.

            y = Variable("y", ny)

            if self.dc:
                ycon = LinearConstraint("ycon", Ay, None, by, ["Pg", "y"])
            else:
                ycon = LinearConstraint("ycon", Ay, None, by, ["Pg", "Qg","y"])
        else:
#            Ay = spmatrix([], [], [], (ybas + ny, 0))
#            by = matrix()
            y = ycon = None

        return y, ycon

#------------------------------------------------------------------------------
#  "Solver" class:
#------------------------------------------------------------------------------

class Solver(object):
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

#        Bf = om._Bf
#        Pfinj = om._Pfinj

        return buses, branches, gens, cp


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
        nw = self.om.cost_N
        # Number of piece-wise linear costs.
        if "y" in [v.name for v in self.om.vars]:
            ny = self.om.get_var_N("y")
        else:
            ny = 0
        # Total number of control variables of all types.
        nxyz = self.om.var_N

        return ipol, ipwl, nb, nl, nw, ny, nxyz


    def _split_constraints(self, om):
        """ Returns the linear problem constraints.
        """
        A, l, u = om.linear_constraints() # l <= A*x <= u

        # Indexes for equality, greater than (unbounded above), less than
        # (unbounded below) and doubly-bounded constraints.
        ieq = matrix([i for i, v in enumerate(abs(u - l)) if v < EPS])
        igt = matrix([i for i in range(len(l)) if u[i] >=  1e10 and l[i] > -1e10])
        ilt = matrix([i for i in range(len(l)) if l[i] <= -1e10 and u[i] <  1e10])
        ibx = matrix([i for i in range(len(l))
                      if (abs(u[i] - l[i]) > EPS) and
                      (u[i] < 1e10) and (l[i] > -1e10)])

        Aeq = A[ieq, :]
        beq = u[ieq, :]
        Aieq = sparse([A[ilt, :], -A[igt, :], A[ibx, :], -A[ibx, :]])
        bieq = matrix([u[ilt], -l[igt], u[ibx], -l[ibx]])

        return Aeq, beq, Aieq, bieq


    def _var_bounds(self):
        """ Returns bounds on the optimisation variables.
        """
        x0 = matrix(0.0, (0, 1))
        LB = matrix(0.0, (0, 1))
        UB = matrix(0.0, (0, 1))

        for var in self.om.vars:
            x0 = matrix([x0, var.v0])
            LB = matrix([LB, var.vl])
            UB = matrix([UB, var.vu])

        return x0, LB, UB


    def _initial_interior_point(self, buses, LB, UB):
        """ Selects an interior initial point for interior point solver.
        """
        Va = self.om.get_var("Va")
        va_refs = [b.v_angle_guess * pi / 180.0 for b in buses
                   if b.type == REFERENCE]
        x0 = matrix((LB + UB) / 2.0)
        x0[Va.i1:Va.iN + 1] = va_refs[0] # Angles set to first reference angle.
        # TODO: PWL initial points.
        return x0

#------------------------------------------------------------------------------
#  "DCOPFSolver" class:
#------------------------------------------------------------------------------

class DCOPFSolver(Solver):
    """ Defines a solver for DC optimal power flow.

        References:
            Ray Zimmerman, "dcopf_solver.m", MATPOWER, PSERC Cornell, v4.0b1,
            http://www.pserc.cornell.edu/matpower/, December 2009
    """

    def __init__(self, om, cvxopt=True, solver=None):
        """ Initialises a new DCOPFSolver instance.
        """
        super(DCOPFSolver, self).__init__(om)

        # Use a solver from CVXOPT.
        self.cvxopt = cvxopt

        # Specify an alternative solver ("mosek" (or "glpk" for linear
        # formulation)). Specify None to use the CVXOPT solver.
        self.solver = solver

        # User-defined costs.
        self.N = spmatrix([], [], [], (0, self.om.var_N))
        self.H = spmatrix([], [], [], (0, 0))
        self.Cw = matrix(0.0, (0, 0))
        self.fparm = matrix(0.0, (0, 0))


    def solve(self):
        """ Solves DC optimal power flow and returns a results dict.
        """
        base_mva = self.om.case.base_mva
        # Unpack the OPF model.
        buses, branches, generators, cp = self._unpack_model(self.om)
        # Compute problem dimensions.
        ipol, ipwl, nb, nl, nw, ny, nxyz = self._dimension_data(buses,
                                                                branches,
                                                                generators)
        # Split the constraints in equality and inequality.
        Aeq, beq, Aieq, bieq = self._split_constraints(self.om)
        # Piece-wise linear components of the objective function.
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self._pwl_costs(ny, nxyz)
        # Quadratic components of the objective function.
        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
            self._quadratic_costs(generators, ipol, nxyz, base_mva)
        # Combine pwl, poly and user costs.
        NN, HHw, CCw, ffparm = \
            self._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
                                Npol, Hpol, Cpol, fparm_pol, npol,
                                self.N, self.H, self.Cw, self.fparm, nw)
        # Transform quadratic coefficients for w into coefficients for X.
        HH, CC, C0 = self._transform_coefficients(NN, HHw, CCw, ffparm, polycf,
                                                  any_pwl, npol, nw)
        # Bounds on the optimisation variables.
        _, LB, UB = self._var_bounds()

        # Select an interior initial point for interior point solver.
        x0 = self._initial_interior_point(buses, LB, UB)

        # Call the quadratic/linear solver.
        solution = self._run_opf(HH, CC, Aieq, bieq, Aeq, beq, LB, UB, x0)

        return solution


    def _pwl_costs(self, ny, nxyz):
        """ Returns the piece-wise linear components of the objective function.
        """
        any_pwl = int(ny > 0)
        if any_pwl:
            Npwl = spmatrix(1.0, )
            Hpwl = 0
            Cpwl = 1
            fparm_pwl = matrix([1, 0, 0, 1])
        else:
            Npwl = spmatrix([], [], [], (0, nxyz))
            Hpwl = spmatrix([], [], [], (0, 0))
            Cpwl = matrix(0.0, (0, 1))
            fparm_pwl = matrix(0.0, (0, 4))

        return Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl


    def _quadratic_costs(self, generators, ipol, nxyz, base_mva):
        """ Returns the quadratic cost components of the objective function.
        """
        npol = len(ipol)
        gpol = [g for g in generators if g.pcost_model == POLYNOMIAL]

        if [g for g in gpol if len(g.p_cost) > 3]:
            logger.error("Order of polynomial cost greater than quadratic.")

        iqdr = matrix([i for i, g in enumerate(generators)
                       if g.pcost_model == POLYNOMIAL and len(g.p_cost) == 3])
        ilin = matrix([i for i, g in enumerate(generators)
                       if g.pcost_model == POLYNOMIAL and len(g.p_cost) == 2])

        polycf = matrix(0.0, (npol, 3))
        if len(iqdr) > 0:
            polycf[iqdr, :] = matrix([list(g.p_cost)
                                      for g in generators]).T[iqdr, :]

        polycf[ilin, 1:] = matrix([list(g.p_cost[:2])
                                    for g in generators]).T[ilin, :]

        # Convert to per-unit.
        polycf *= spdiag([base_mva**2, base_mva, 1])
        Pg = self.om.get_var("Pg")
        Npol = spmatrix(1.0, range(npol), Pg.i1 + ipol, (npol, nxyz))
        Hpol = spmatrix(2 * polycf[:, 0], range(npol), range(npol))
        Cpol = polycf[:, 1]
        fparm_pol = matrix(1.0, (npol, 1)) * matrix([1, 0, 0, 1]).T

        return Npol, Hpol, Cpol, fparm_pol, polycf, npol


    def _combine_costs(self, Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
                       Npol, Hpol, Cpol, fparm_pol, npol,
                       N=None, H=None, Cw=None, fparm=None, nw=0):
        NN = sparse([Npwl, Npol])#, N])

        HHw = sparse([
            sparse([Hpwl, spmatrix([], [], [], (npol, any_pwl))]).T,
            sparse([spmatrix([], [], [], (any_pwl, npol)), Hpol]).T
        ]).T

#        HHw = sparse([
#            sparse([Hpwl, spmatrix([], [], [], (any_pwl, npol + nw))]).T,
#            sparse([spmatrix([], [], [], (npol, any_pwl)),
#                    Hpol,
#                    spmatrix([], [], [], (npol, nw))]).T,
#            sparse([spmatrix([], [], [], (nw, any_pwl + npol)), H]).T
#        ]).T

        CCw = matrix([Cpwl, Cpol])#, Cw])
        ffparm = matrix([fparm_pwl, fparm_pol])#, fparm])

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
        HH = MN.H * HHw * MN
        CC = MN.H * (CCw - HMR)
        # Constant term of cost.
        C0 = 1./2. * MR.H * HMR + sum(polycf[:, 2])

        return HH, CC, C0


    def _run_opf(self, P, q, G, h, A, b, LB, UB, x0):
        """ Solves the either quadratic or linear program.
        """
        if not self.cvxopt:
            AA = sparse([A, G]) # Combined equality and inequality constraints.
            bb = matrix([b, h])
            N = A.size[0]
            if solvers.options.has_key("show_progress"):
                opt = {"verbose": solvers.options["show_progress"]}
            else:
                opt = {"verbose": False}

        if len(P) > 0:
            if self.cvxopt:
                solution = qp(P, q, G, h, A, b, self.solver, {"x": x0})
            else:
                retval = pdipm_qp(P, q, AA, bb, LB, UB, x0, N, opt)
        else:
            if self.cvxopt:
                solution = lp(q, G, h, A, b, self.solver, {"x": x0})
            else:
                retval = pdipm_qp(None, q, AA, bb, LB, UB, x0, N)

        if not self.cvxopt:
            solution = {"xout": retval[0], "lmbdaout": retval[1],
                        "howout": retval[2], "success": retval[3]}

        return solution

#------------------------------------------------------------------------------
#  "PDIPMSolver" class:
#------------------------------------------------------------------------------

class PDIPMSolver(Solver):
    """ Solves AC optimal power flow using a primal-dual interior point method.
    """

    def __init__(self, om, flow_lim="S", opt=None):
        """ Initialises a new PDIPMSolver instance.
        """
        super(PDIPMSolver, self).__init__(om)

        # Quantity to limit for branch flow constraints ("S", "P" or "I").
        self.flow_lim = flow_lim

        # Options for the PDIPM.
        self.opt = {} if opt is None else opt


    def _ref_bus_angle_constraint(self, buses, Va, xmin, xmax):
        """ Adds a constraint on the reference bus angles.
        """
        refs = matrix([i for i, v in enumerate(buses) if v.type == REFERENCE])
        Varefs = matrix([b.v_angle_guess for b in buses if b.type ==REFERENCE])

        xmin[Va.i1 - 1 + refs] = Varefs
        xmax[Va.iN - 1 + refs] = Varefs

        return xmin, xmax


    def solve(self):
        j = 0 + 1j
        case = self.om.case
        base_mva = case.base_mva

        # TODO: Find explanation for this value.
        self.opt["cost_mult"] = 1e-4

        # Unpack the OPF model.
        bs, ln, gn, cp = self._unpack_model(self.om)

        # Compute problem dimensions.
        ng = len(gn)
        gpol = [g for g in gn if g.pcost_model == POLYNOMIAL]
        ipol, ipwl, nb, nl, nw, ny, nxyz = self._dimension_data(bs, ln, gn)

        # Linear constraints (l <= A*x <= u).
        A, l, u = self.om.linear_constraints()

        _, xmin, xmax = self._var_bounds()

        # Select an interior initial point for interior point solver.
        x0 = self._initial_interior_point(bs, xmin, xmax)

        # Build admittance matrices.
        Ybus, Yf, Yt = case.Y

        # Optimisation variables.
        Va = self.om.get_var("Va")
        Vm = self.om.get_var("Vm")
        Pg = self.om.get_var("Pg")
        Qg = self.om.get_var("Qg")

        # Adds a constraint on the reference bus angles.
#        xmin, xmax = self._ref_bus_angle_constraint(bs, Va, xmin, xmax)

        def ipm_f(x):
            """ Evaluates the objective function, gradient and Hessian for OPF.
            """
            p_gen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            q_gen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            #------------------------------------------------------------------
            #  Evaluate the objective function.
            #------------------------------------------------------------------

            # Polynomial cost of P and Q.
            xx = matrix([p_gen, q_gen]) * base_mva
            if len(ipol) > 0:
                f = sum([g.total_cost(xx[i]) for i,g in enumerate(gn)])
            else:
                f = 0

            # Piecewise linear cost of P and Q.
            if ny:
                y = self.om.get_var("y")
                ccost = spmatrix(matrix(1.0, (1, ny)), range(y.i1, i.iN + 1),
                                 matrix(1.0, (1, ny)), (1, nxyz))
                f += ccost * x
            else:
                ccost = matrix(0.0, (1, nxyz))

            # TODO: Generalised cost term.

            #------------------------------------------------------------------
            #  Evaluate cost gradient.
            #------------------------------------------------------------------

            iPg = matrix(range(Pg.i1, Pg.iN + 1))
            iQg = matrix(range(Qg.i1, Qg.iN + 1))

            # Polynomial cost of P and Q.
            df_dPgQg = matrix(0.0, (2 * ng, 1))        # w.r.t p.u. Pg and Qg
#            df_dPgQg[ipol] = matrix([g.poly_cost(xx[i], 1) for g in gpol])
            for i, g in enumerate(gn):
                der = polyder(list(g.p_cost))
                df_dPgQg[i] = polyval(der, xx[i]) * base_mva

            df = matrix(0.0, (nxyz, 1))
            df[iPg] = df_dPgQg[:ng]
            df[iQg] = df_dPgQg[ng:ng + ng]

            # Piecewise linear cost of P and Q.
            df += ccost.T # linear cost row is additive wrt any nonlinear cost

            # TODO: Generalised cost term.

            #------------------------------------------------------------------
            #  Evaluate cost Hessian.
            #------------------------------------------------------------------

            d2f = None

            return f, df, d2f


        def ipm_gh(x):
            """ Evaluates nonlinear constraints and their Jacobian for OPF.
            """
            Pgen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            Qgen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            for i, g in enumerate(gn):
                g.p = Pgen[i] * base_mva # active generation in MW
                g.q = Qgen[i] * base_mva # reactive generation in MVAr

            # Rebuild the net complex bus power injection vector in p.u.
            Sbus = case.Sbus

            Vang = x[Va.i1:Va.iN + 1]
            Vmag = x[Vm.i1:Vm.iN + 1]
            V = mul(Vmag, exp(j * Vang))

            # Evaluate the power flow equations.
            mis = mul(V, conj(Ybus * V)) - Sbus

            #------------------------------------------------------------------
            #  Evaluate constraint function values.
            #------------------------------------------------------------------

            # Equality constraints (power flow).
            h = matrix([mis.real(),  # active power mismatch for all buses
                        mis.imag()]) # reactive power mismatch for all buses

            # Inequality constraints (branch flow limits).
            flow_max = matrix([(l.rate_a / base_mva)**2 for l in ln])
            # FIXME: There must be a more elegant method for this.
            for i, v in enumerate(flow_max):
                if v == 0.0:
                    flow_max[i] = INF

            if self.flow_lim == "I":
                If = Yf * V
                It = Yt * V
                # Branch current limits.
                g = matrix([(mul(If, conj(If)) - flow_max),
                            (mul(If, conj(It)) - flow_max)])
            else:
                i_fbus = matrix([bs.index(e.from_bus) for e in ln])
                i_tbus = matrix([bs.index(e.to_bus) for e in ln])
                # Complex power injected at "from" bus (p.u.).
                Sf = mul(V[i_fbus], conj(Yf * V))
                # Complex power injected at "to" bus (p.u.).
                St = mul(V[i_tbus], conj(Yt * V))
                if self.flow_lim == "P": # active power limit, P (Pan Wei)
                    # Branch real power limits.
                    g = matrix([Sf.real()**2 - flow_max,
                                St.real()**2 - flow_max])
                elif self.flow_lim == "S": # apparent power limit, |S|
                    # Branch apparent power limits.
                    g = matrix([mul(Sf, conj(Sf)) - flow_max,
                                mul(St, conj(St)) - flow_max]).real()
                else:
                    raise ValueError

            #------------------------------------------------------------------
            #  Evaluate partials of constraints.
            #------------------------------------------------------------------

            iVa = matrix(range(Va.i1, Va.iN + 1))
            iVm = matrix(range(Vm.i1, Vm.iN + 1))
            iPg = matrix(range(Pg.i1, Pg.iN + 1))
            iQg = matrix(range(Qg.i1, Qg.iN + 1))
            iVaVmPgQg = matrix([iVa, iVm, iPg, iQg]).T

            # Compute partials of injected bus powers.
            dSbus_dVm, dSbus_dVa = case.dSbus_dV(Ybus, V)

            i_gbus = matrix([bs.index(gen.bus) for gen in gn])
            neg_Cg = spmatrix(-1.0, i_gbus, range(ng), (nb, ng))

            # Transposed Jacobian of the power balance equality constraints.
            dh = spmatrix([], [], [], (nxyz, 2 * nb))

            dh[iVaVmPgQg, :] = sparse([
                [dSbus_dVa.real(), dSbus_dVa.imag()],
                [dSbus_dVm.real(), dSbus_dVm.imag()],
                [neg_Cg, spmatrix([], [], [], (nb, ng))],
                [spmatrix([], [], [], (nb, ng)), neg_Cg]
            ]).T

            # Compute partials of flows w.r.t V.
            if self.flow_lim == "I":
                dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    case.dIbr_dV(Yf, Yt, V)
            else:
                dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft = \
                    case.dSbr_dV(Yf, Yt, V, bs, ln)
            if self.flow_lim == "P":
                dFf_dVa = dFf_dVa.real()
                dFf_dVm = dFf_dVm.real()
                dFt_dVa = dFt_dVa.real()
                dFt_dVm = dFt_dVm.real()
                Ff = Ff.real()
                Ft = Ft.real()

            # Squared magnitude of flow (complex power, current or real power).
            df_dVa, df_dVm, dt_dVa, dt_dVm = \
                case.dAbr_dV(dFf_dVa, dFf_dVm, dFt_dVa, dFt_dVm, Ff, Ft)

            # Construct Jacobian of inequality constraints (branch limits) and
            # transpose it.
            dg = spmatrix([], [], [], (nxyz, 2 * nl))
            dg[matrix([iVa, iVm]).T, :] = sparse([[df_dVa, dt_dVa],
                                                  [df_dVm, dt_dVm]]).T

            return g, h, dg, dh


        def ipm_hess(x, lmbda):
            """ Evaluates Hessian of Lagrangian for AC OPF.
            """
            Pgen = x[Pg.i1:Pg.iN + 1] # Active generation in p.u.
            Qgen = x[Qg.i1:Qg.iN + 1] # Reactive generation in p.u.

            for i, g in enumerate(gn):
                g.p = Pgen[i] * base_mva # active generation in MW
                g.q = Qgen[i] * base_mva # reactive generation in MVAr

            Vang = x[Va.i1:Va.iN + 1]
            Vmag = x[Vm.i1:Vm.iN + 1]
            V = mul(Vmag, exp(j * Vang))
            nxtra = nxyz - 2 * nb

            #------------------------------------------------------------------
            #  Evaluate d2f.
            #------------------------------------------------------------------

            d2f_dPg2 = spmatrix([], [], [], (ng, 1)) # w.r.t p.u. Pg
            d2f_dQg2 = spmatrix([], [], [], (ng, 1)) # w.r.t p.u. Qg
#            d2f_dPg2[ipol] = matrix([g.poly_cost(Pg[i] * base_mva, 2)
#                                     for i, g in enumerate(gpol)])
            for i, g in enumerate(gn):
                der = polyder(list(g.p_cost), 2)
                d2f_dPg2[i] = polyval(der, Pgen[i]) * base_mva
#            d2f_dQg2[ipol] = matrix([g.poly_cost(Qg[i] * base_mva, 2)
#                                     for i, g in enumerate(gpol)
#                                     if g.qcost_model is not None])
            for i, g in enumerate(gn):
                if g.qcost_model == POLYNOMIAL:
                    der = polyder(list(g.q_cost), 2)
                    d2f_dQg2[i] = polyval(der, Qgen[i]) * base_mva

            i = matrix([matrix(range(Pg.i1, Pg.iN + 1)),
                        matrix(range(Qg.i1, Qg.iN + 1))])
            d2f = spmatrix(matrix([d2f_dPg2, d2f_dQg2]), i, i, (nxyz, nxyz))

            # TODO: Generalised cost model.

            d2f *= self.opt["cost_mult"]

            #------------------------------------------------------------------
            #  Evaluate Hessian of power balance constraints.
            #------------------------------------------------------------------

            nlam = len(lmbda["eqnonlin"]) / 2
            lamP = lmbda["eqnonlin"][:nlam]
            lamQ = lmbda["eqnonlin"][nlam:nlam + nlam]
            Hpaa, Hpav, Hpva, Hpvv = case.d2Sbus_dV2(Ybus, V, lamP)
            Hqaa, Hqav, Hqva, Hqvv = case.d2Sbus_dV2(Ybus, V, lamQ)

            d2H = sparse([
                [sparse([[Hpaa.real(), Hpva.real()],
                         [Hpav.real(), Hpvv.real()]]) + \
                 sparse([[Hqaa.imag(), Hqva.imag()],
                         [Hqav.imag(), Hqvv.imag()]]),
                 spmatrix([], [], [], (nxtra, 2 * nb))],
                [spmatrix([], [], [], (2 * nb, nxtra)),
                 spmatrix([], [], [], (nxtra, nxtra))]
            ])

            #------------------------------------------------------------------
            #  Evaluate Hessian of flow constraints.
            #------------------------------------------------------------------

            nmu = len(lmbda["ineqnonlin"]) / 2
            muF = lmbda["ineqnonlin"][:nmu]
            muT = lmbda["ineqnonlin"][nmu:nmu + nmu]
            if self.flow_lim == "I":
                dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It = \
                    case.dIbr_dV(Yf, Yt, V)
                Gfaa, Gfav, Gfva, Gfvv = \
                    case.d2AIbr_dV2(dIf_dVa, dIf_dVm, If, Yf, V, muF)
                Gtaa, Gtav, Gtva, Gtvv = \
                    case.d2AIbr_dV2(dIt_dVa, dIt_dVm, It, Yt, V, muT)
            else:
                f = matrix([bs.index(e.from_bus) for e in ln])
                t = matrix([bs.index(e.to_bus) for e in ln])
                # Line-bus connection matrices.
                Cf = spmatrix(matrix(1.0, (nl, 1)), range(nl), f, (nl, nb))
                Ct = spmatrix(matrix(1.0, (nl, 1)), range(nl), t, (nl, nb))
                dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St = \
                    case.dSbr_dV(Yf, Yt, V)
                if self.flow_lim == "P":
                    Gfaa, Gfav, Gfva, Gfvv = \
                        case.d2ASbr_dV2(dSf_dVa.real(), dSf_dVm.real(),
                                        Sf.real(), Cf, Yf, V, muF)
                    Gtaa, Gtav, Gtva, Gtvv = \
                        case.d2ASbr_dV2(dSt_dVa.real(), dSt_dVm.real(),
                                        St.real(), Ct, Yt, V, muT)
                elif self.flow_lim == "S":
                    Gfaa, Gfav, Gfva, Gfvv = \
                        case.d2ASbr_dV2(dSf_dVa, dSf_dVm, Sf, Cf, Yf, V, muF)
                    Gtaa, Gtav, Gtva, Gtvv = \
                        case.d2ASbr_dV2(dSt_dVa, dSt_dVm, St, Ct, Yt, V, muT)
                else:
                    raise ValueError

#            Gf = sparse([[Gfaa, Gfva], [Gfav, Gfvv]])
#            Gt = sparse([[Gtaa, Gtva], [Gtav, Gtvv]])
#            d2G1 = sparse([[Gf + Gt],
#                           [spmatrix([], [], [], (2 * nb, nxtra))]])
#            d2G2 = spmatrix([], [], [], (nxtra, 2 * nb + nxtra))
#            d2G = sparse([d2G1, d2G2])

            d2G = sparse([
                [sparse([[Gfaa, Gfva], [Gfav, Gfvv]]) + \
                 sparse([[Gtaa, Gtva], [Gtav, Gtvv]]),
                 spmatrix([], [], [], (nxtra, 2 * nb))],
                [spmatrix([], [], [], (2 * nb, nxtra)),
                 spmatrix([], [], [], (nxtra, nxtra))]
            ])

            return d2f + d2H + d2G

        # Solve using primal-dual interior point method.
        x, _, info, output, lmbda = \
            pdipm(ipm_f, ipm_gh, ipm_hess, x0, xmin, xmax, A, l, u, self.opt)

        success = (info > 0)
        if success:
            howout = 'success'
        else:
            howout = 'failure'

        lmbdaout = matrix([-lmbda["mu_l"] + lmbda["mu_u"],
                            lmbda["lower"], lmbda["upper"]])

        solution = {"xout": x, "lmbdaout": lmbdaout,
                    "howout": howout, "success": success}

        solution.update(output)

        return solution

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
        Aeq, beq, Aieq, bieq = self._split_constraints(self.om)

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
            from_idxs = matrix([buses.index(e.from_bus) for e in branches])
            to_idxs = matrix([buses.index(e.to_bus) for e in branches])
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
#  "OPFModel" class:
#------------------------------------------------------------------------------

class OPFModel(object):
    """ Defines a model for optimal power flow.
    """

    def __init__(self, case):
        self.case = case
        self.vars = []
        self.lin_constraints = []
        self.nln_constraints = []
        self.costs = []


    @property
    def var_N(self):
        return sum([v.N for v in self.vars])


    def add_var(self, var):
        """ Adds a variable to the model.
        """
        if var.name in [v.name for v in self.vars]:
            logger.error("Variable set named '%s' already exists." % var.name)
            return

        var.i1 = self.var_N
        var.iN = self.var_N + var.N - 1
        self.vars.append(var)


    def add_vars(self, vars):
        """ Adds a set of variables to the model.
        """
        for var in vars:
            self.add_var(var)


    def get_var(self, name):
        """ Returns the variable set with the given name.
        """
        for var in self.vars:
            if var.name == name:
                return var
        else:
            raise ValueError



    def get_var_N(self, name):
        """ Return the number of variables in the named set.
        """
        return self.get_var(name).N


    @property
    def nln_N(self):
        return sum([c.N for c in self.nln_constraints])


    @property
    def lin_N(self):
        return sum([c.N for c in self.lin_constraints])


    @property
    def lin_NS(self):
        return len(self.lin_constraints)


    def linear_constraints(self):
        """ Returns the linear constraints.
        """
        A = spmatrix([], [], [], (self.lin_N, self.var_N), tc='d')
        l = matrix(-INF, (self.lin_N, 1))
        u = -l

        for lin in self.lin_constraints:
            if lin.N:                   # non-zero number of rows to add
                Ak = lin.A              # A for kth linear constrain set
                i1 = lin.i1             # starting row index
                iN = lin.iN             # ending row index
                vsl = lin.vs            # var set list
                kN = -1                 # initialize last col of Ak used
                Ai = spmatrix([], [], [], (lin.N, self.var_N))
                for v in vsl:
                    var = self.get_var(v)
                    j1 = var.i1         # starting column in A
                    jN = var.iN         # ending column in A
                    k1 = kN + 1         # starting column in Ak
                    kN = kN + var.N     # ending column in Ak
                    Ai[:, j1:jN + 1] = Ak[:, k1:kN + 1]

                A[i1:iN + 1, :] = Ai
                l[i1:iN + 1] = lin.l
                u[i1:iN + 1] = lin.u

        return A, l, u


    def add_constraint(self, con):
        """ Adds a constraint to the model.
        """
        if isinstance(con, LinearConstraint):
            N, M = con.A.size
            if con.name in [c.name for c in self.lin_constraints]:
                logger.error("Constraint set named '%s' already exists."
                             % con.name)
                return False
            else:
                con.i1 = self.lin_N# + 1
                con.iN = self.lin_N + N - 1

                nv = 0
                for vs in con.vs:
                    nv = nv + self.get_var_N(vs)
                if M != nv:
                    logger.error("Number of columns of A does not match number"
                        " of variables, A is %d x %d, nv = %d", N, M, nv)
                self.lin_constraints.append(con)
        elif isinstance(con, NonLinearConstraint):
            N = con.N
            if con.name in [c.name for c in self.nln_constraints]:
                logger.error("Constraint set named '%s' already exists."
                             % con.name)
                return False
            else:
                con.i1 = self.nln_N# + 1
                con.iN = self.nln_N + N
                self.nln_constraints.append(con)
        else:
            raise ValueError

        return True


    def add_constraints(self, constraints):
        """ Adds constraints to the model.
        """
        for con in constraints:
            self.add_constraint(con)


    @property
    def cost_N(self):
        return sum([c.N for c in self.costs])


    def get_cost_params(self):
        """ Returns the cost parameters.
        """
        return [c.params for c in self.costs]

#------------------------------------------------------------------------------
#  "Indexed" class:
#------------------------------------------------------------------------------

class Set(Named):

    def __init__(self, name, N):

        self.name = name

        # Starting index.
        self.i0 = 0

        # Ending index.
        self.iN = 0

        # Number in set.
        self.N = N

        # Number of sets.
        self.NS = 0

        # Ordered list of sets.
        self.order = []

#------------------------------------------------------------------------------
#  "Variable" class:
#------------------------------------------------------------------------------

class Variable(Set):
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
#  "LinearConstraint" class:
#------------------------------------------------------------------------------

class LinearConstraint(Set):
    """ Defines a set of linear constraints.
    """

    def __init__(self, name, AorN, l=None, u=None, vs=None):
        N, _ = AorN.size

        super(LinearConstraint, self).__init__(name, N)

        self.A = AorN
        self.l = matrix(-INF, (N, 1)) if l is None else l
        self.u = matrix( INF, (N, 1)) if u is None else u

        # Varsets.
        self.vs = [] if vs is None else vs

        if (self.l.size[0] != N) or (self.u.size[0] != N):
            logger.error("Sizes of A, l and u must match.")

#------------------------------------------------------------------------------
#  "NonLinearConstraint" class:
#------------------------------------------------------------------------------

class NonLinearConstraint(Set):
    """ Defines a set of non-linear constraints.
    """
    pass

#------------------------------------------------------------------------------
#  "Cost" class:
#------------------------------------------------------------------------------

class Cost(Set):
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

# EOF -------------------------------------------------------------------------
