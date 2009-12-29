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
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from math import pi

from cvxopt import matrix, spmatrix, sparse

from case import REFERENCE, POLYNOMIAL

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

INF = -1e10

#------------------------------------------------------------------------------
#  "OPF" class:
#------------------------------------------------------------------------------

class OPF:
    """ Defines a generalised OPF solver.
    """

    def __init__(self, case, dc=True, show_progress=True, max_iterations=100,
                 absolute_tol=1e-7, relative_tol=1e-6, feasibility_tol=1e-7):
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


    def init_bounds(self):
        """ Sets-up the initial bounds.
        """
        self.Pg = matrix([g.p / self.case.base_mva for g in self.generators])
        self.Qg = matrix([g.q / self.case.base_mva for g in self.generators])
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
        raise NotImplementedError

#------------------------------------------------------------------------------
#  "Indexed" class:
#------------------------------------------------------------------------------

class Indexed:
    def __init__(self):
        self.i0 = 0
        self.iN = 0
        self.N = 0
        self.NS = 0
        self.order = {}

#------------------------------------------------------------------------------
#  "Variable" class:
#------------------------------------------------------------------------------

class Variable(Indexed):
    def __init__(self):
        self.v0 = 0.0
        self.vl = 0.0
        self.vu = 0.0

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
