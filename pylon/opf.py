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
        Ray Zimmerman, "opf.m", MATPOWER, PSERC Cornell, version 4.0b2,
        http://www.pserc.cornell.edu/matpower/, December 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from math import pi

from cvxopt import matrix, spmatrix, sparse

from util import Named
from case import REFERENCE, POLYNOMIAL, PIECEWISE_LINEAR

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

INF = -1e10

#------------------------------------------------------------------------------
#  "OPF" class:
#------------------------------------------------------------------------------

class OPF:
    """ Defines a generalised OPF solver.

        References:
            Ray Zimmerman, "opf.m", MATPOWER, PSERC Cornell, version 4.0b2,
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
        self.ref_check()
        self.remove_isolated()
        self.case.reset()
        self.dimension_data()
        self.pwl1_to_poly()
        self.init_vars()
        self.init_bounds()
        if self.dc:
            self.B, _, self.Pbusinj, self.Pfinj = self.case.B
            self.power_mismatch()
            self.voltage_angle_reference()
        self.branch_voltage_angle_difference_limit()
        self.construct_opf_model()


    def ref_check(self):
        """ Checks that there is only one reference bus.
        """
        self.refs = matrix([i for i, bus in enumerate(self.case.buses)
                     if bus.type == REFERENCE])

        return 0 < len(self.refs) <= 1


    def remove_isolated(self):
        """ Returns non-isolated case components.
        """
        self.case.deactivate_isolated()
        buses = self.buses = self.case.connected_buses
        branches = self.branches = self.case.online_branches
        gens = self.generators = self.case.online_generators

        return buses, branches, gens


    def dimension_data(self):
        """ Returns the number of buses, branches and generators in the
            given case, respectively.
        """
        self.nb = nb = len(self.buses)
        self.nl = nl = len(self.branches)
        self.ng = ng = len(self.generators)

        return nb, nl, ng


    def pwl1_to_poly(self):
        """ Converts single-block piecewise-linear costs into linear
            polynomial.
        """
        for g in self.generators:
            if (g.cost_model == POLYNOMIAL) and (len(g.p_cost == 2)):
                g.pwl_to_poly()


    def init_vars(self):
        """ Sets-up the initial variables.
        """
        self.Va = matrix([b.v_angle_guess * (pi / 180.0) for b in self.buses])
        self.Vm = matrix([b.v_magnitude for b in self.buses])
        # For buses with generators initialise Vm from gen data.
        for g in self.generators:
            busidx = self.buses.index(g.bus)
            self.Vm[busidx] = g.v_magnitude
        self.Pg = matrix([g.p / self.case.base_mva for g in self.generators])
        self.Qg = matrix([g.q / self.case.base_mva for g in self.generators])


    def init_bounds(self):
        """ Sets-up the initial bounds.
        """
        self.Pmin = matrix([g.p_min / self.case.base_mva
                            for g in self.generators])
        self.Pmax = matrix([g.p_max / self.case.base_mva
                            for g in self.generators])
        self.Qmin = matrix([g.q_min / self.case.base_mva
                            for g in self.generators])
        self.Qmax = matrix([g.q_max / self.case.base_mva
                            for g in self.generators])


    def power_mismatch(self):
        """ Returns the power mismatch constraint (B*Va + Pg = Pd).
        """
        # Negative bus-generator incidence matrix.
        gen_bus = matrix([self.buses.index(g.bus) for g in self.generators])
        neg_Cg = spmatrix(-1.0, gen_bus, range(self.ng), (self.nb, self.ng))

        Amis = self.Amis = sparse([self.B, neg_Cg])

        Pd = matrix([bus.p_demand for bus in self.buses])
        Gs = matrix([bus.g_shunt for bus in self.buses])

        bmis = -(Pd - Gs) / self.case.base_mva - self.Pbusinj

        return Amis, bmis


    def branch_flow(self):
        """ Returns the branch flow limit constraint.  The real power flows
            at the from end the lines are related to the bus voltage angles
            by Pf = Bf * Va + Pfinj.
        """
        # Indexes of constrained lines.
        il = matrix([i for i, l in enumerate(self.branches)
                     if 0.0 < l.s_max < 1e10])
        lpf = matrix(-INF, (len(il), 1))
        rate_a = matrix([l.s_max / self.base_mva for l in self.branches[il]])
        upf = rate_a - self.Pfinj[il]
        upt = rate_a + self.Pfinj[il]

        return lpf, upf, upt


    def voltage_angle_reference(self):
        """ Returns the voltage angle reference constraint.
        """
        Vau = self.Vau = matrix(INF, (self.nb, 1))
        Val = self.Val = -Vau
        Vau[self.refs] = self.Va[self.refs]
        Val[self.refs] = self.Va[self.refs]

        return Vau, Val


    def branch_voltage_angle_difference_limit(self):
        """ Returns the constraint on the branch voltage angle differences.
        """
        if not self.ignore_ang_lim:
            iang = matrix([i for i, b in enumerate(self.branches)
                           if (b.ang_min and (b.ang_min > -360.0))
                           or (b.ang_max and (b.ang_max < 360.0))])
            iangl = matrix([i for i, b in enumerate(self.branches[iang])
                            if b.ang_min is not None])
            iangh = matrix([i for i, b in enumerate(self.branches[iang])
                            if b.ang_max is not None])
            nang = len(iang)

            if nang > 0:
                ii = matrix([range(nang), range(nang)])
                jj = matrix([[self.buses.index(b.from_bus)
                              for b in self.branches[iang]],
                             [self.buses.index(b.to_bus)
                              for b in self.branches[iang]]])
                Aang = spmatrix(matrix([matrix(1.0, (nang, 1)),
                                        matrix(-1.0, (nang, 1))]),
                                        ii, jj, (nang, self.nb))
                uang = matrix(INF, (nang, 1))
                lang = -uang
                lang[iangl] = matrix([b.ang_min * (pi / 180.0)
                                      for b in self.branches[iangl]])
                uang[iangh] = matrix([b.ang_max * (pi / 180.0)
                                      for b in self.branches[iangh]])
            else:
                Aang = spmatrix([], [], [], (0, self.nb))
                lang = matrix()
                uang = matrix()
        else:
            Aang = spmatrix([], [], [], (0, self.nb))
            lang = matrix()
            uang = matrix()
            iang = matrix()

        return Aang, lang, uang, iang


    def pwl_gen_costs(self):
        """ Returns the basin constraints for piece-wise linear gen cost
            variables.

            References:
                C. E. Murillo-Sanchez, "makeAy.m", MATPOWER, PSERC Cornell,
                version 4.0b2, http://www.pserc.cornell.edu/matpower/, Dec 09
        """
        gpwl = [g for g in self.generators if g.cost_model == PIECEWISE_LINEAR]
        ny = len(gpwl) # number of extra y variables.
        if ny > 0:
            # Total number of cost points.
            m = len([p for g in gpwl for p in g.p_cost])
            Ay = spmatrix([], [], [], (m - ny, ybas + ny -1))
            by = matrix()
        else:
            Ay = spmatrix([], [], [] (ybas + ny, 0))
            by = matrix()

        return Ay, by


    def construct_opf_model(self):
        """ Returns an OPF model with variables and constraints.
        """
        if self.dc:
            om = OPFModel()
            om.add_var(Variable("Va", self.nb, self.Va, self.Val, self.Vau))
            om.add_var(Variable("Pg", self.ng, self.Pg, self.Pmin, self.Pmax))

            om.add_constr(LinearConstraint("Pmis", self.Amis,
                                           self.bmis, self.bmis, ["Va", "Pg"]))
            om.add_constr(LinearConstraint("Pf", self.Bf[self.il, :],
                                           self.lpf, self.upf, ["Va"]))
            om.add_constr(LinearConstraint("Pt", -self.Bf[self.il, :],
                                           self.lpf, self.upt, ["Va"]))
            om.add_constr(LinearConstraint("ang", self.Aang,
                                           self.lang, self.uang, ["Va"]))
        else:
            raise NotImplementedError

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
