#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" DC Optimal Power Flow for routine.

    References:
        Ray Zimmerman, "dcopf.m", MATPOWER, PSERC Cornell, version 3.2,
        http://www.pserc.cornell.edu/matpower/, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging

from os.path import join, dirname
from math import pi

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul
from cvxopt.umfpack import linsolve
from cvxopt import solvers
from cvxopt.solvers import qp

from pylon.y import SusceptanceMatrix

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
#  "DCOPF" class:
#------------------------------------------------------------------------------

class DCOPF(object):
    """ A method class for solving the DC optimal power flow problem

        References:
            Ray Zimmerman, "dcopf.m", MATPOWER, PSERC Cornell, version 3.2,
            http://www.pserc.cornell.edu/matpower/, June 2007
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, solver=None, show_progress=True, max_iterations=100,
            absolute_tol=1e-7, relative_tol=1e-6, feasibility_tol=1e-7,
            refinement=1):
        """ Initialises the new DCOPF instance.
        """
        # Choice of solver (May be None or "mosek"). Specify None to use the
        # native Python solver from CVXOPT.
        self.solver = solver
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

        # Network object to be optimised.
        self.network = None

        # Sparse branch susceptance matrix.  The bus real power injections are
        # related to bus voltage angles by P = Bbus * Va + Pbusinj
        self._B = None

        # Sparse branch source bus susceptance matrix. The real power flows at
        # the from end the lines are related to the bus voltage angles by
        # Pf = Bf * Va + Pfinj
        self._B_source = None

        # The real power flows at the from end the lines are related to the bus
        # voltage angles by Pf = Bf * Va + Pfinj
        self._theta_inj_source = None

        # The bus real power injections are related to bus voltage angles by
        # P = Bbus * Va + Pbusinj
        self._theta_inj_bus = None

        # For polynomial cost models we use a quadratic solver.
        self._solver_type = "linear" # or "quadratic"

        # Initial values for x.
        self._x = None

        # The equality and inequality problem constraints combined.
        self._AA_eq = None # sparse
        self._AA_ieq = None # sparse
        self._bb_eq = None
        self._bb_ieq = None

        # Objective function of the form 0.5 * x'*H*x + c'*x.
        self._hh = None # sparse
        self._cc = None

        # Solution.
        self.x = None

        # Objective function value.
        self.f = 0.0

        # Time taken to solve.
        self.t_elapsed = 0.0


    def __call__(self, network):
        """ Call the routine using routine(n).
        """
        return self.solve(network)


    def solve(self, network=None):
        """ Solves a DC OPF.
        """
        t0 = time.time()
        self.network = network if network is not None else self.network

        logger.debug("Solving DC OPF [%s]" % network.name)

        # Algorithm parameters.
        solvers.options["show_progress"] = self.show_progress
        solvers.options["maxiters"] = self.max_iterations
        solvers.options["abstol"] = self.absolute_tol
        solvers.options["reltol"] = self.relative_tol
        solvers.options["feastol"] = self.feasibility_tol
        solvers.options["refinement"] = self.refinement

        susceptance_matrix = SusceptanceMatrix()
        self._B, self._B_source = susceptance_matrix(self.network)

        self._theta_inj_source = self._get_theta_inj_source()
        self._theta_inj_bus = self._get_theta_inj_bus()

        # Use the same cost model for all generators.
        self._solver_type = self._get_solver_type()

        # Get the vector x where, AA * x <= bb.
        self._x = self._get_x()

        # Problem constraints.
        _aa_cost, _bb_cost = self._get_cost_constraint()

        _aa_ref, _bb_ref = self._get_reference_angle_constraint()

        _aa_mismatch, _bb_mismatch = self._get_active_power_flow_equations()

        _aa_gen, _bb_gen = self._get_generation_limit_constraint()

        _aa_flow, _bb_flow = self._get_branch_flow_limit_constraint()

        # Combine the equality constraints.
        self._AA_eq = sparse([_aa_cost, _aa_ref, _aa_mismatch])
        self._bb_eq = matrix([_bb_cost, _bb_ref, _bb_mismatch])

        # Combine the inequality constraints.
        self._AA_ieq = sparse([_aa_gen])#, _aa_flow])
        self._bb_ieq = matrix([_bb_gen])#, _bb_flow])

        # The objective function has the form 0.5 * x'*H*x + c'*x.
        self._hh = self._get_h()
        self._cc = self._get_c()

        # Solve the problem.
        solution = self._solve_qp()
        self.x = solution["x"]

        # Compute elapsed time.
        self.t_elapsed = t_elapsed = time.time() - t0

        if solution["status"] == "optimal":
            self._update_solution_data(solution)
            logger.info("DC OPF completed in %.3fs." % t_elapsed)
            return True
        else:
            logger.error("Non-convergent DC OPF.")
            return False

    #--------------------------------------------------------------------------
    #  Phase shift injection vectors:
    #--------------------------------------------------------------------------

    def _get_theta_inj_source(self):
        """ Returns the phase shift "quiescent" injections.

            | Pf |   | Bff  Bft |   | Vaf |   | Pfinj |
            |    | = |          | * |     | + |       |
            | Pt |   | Btf  Btt |   | Vat |   | Ptinj |
        """
        branches = self.network.online_branches

#        b = matrix([1/e.x * e.online for e in branches])
        susc = []
        for branch in branches:
            if branch.x != 0.0:
                susc.append(branch.x)
            else:
                susc.append(1e12)
        b = matrix(susc)
        angle = matrix([-e.phase_shift * pi / 180 for e in branches])

        # Element-wise multiply
        # http://abel.ee.ucla.edu/cvxopt/documentation/users-guide/node9.html
        source_inj = mul(b, angle)

        logger.debug("Built source bus phase shift injection vector:\n%s" %
            source_inj)

        return source_inj


    def _get_theta_inj_bus(self):
        """ Pbusinj = dot(Cf, Pfinj) + dot(Ct, Ptinj)
        """
        buses = self.network.connected_buses
        branches = self.network.online_branches
        n_buses = len(self.network.connected_buses)
        n_branches = len(self.network.online_branches)

        # Build incidence matrices
        source_incd = matrix(0, (n_buses, n_branches), tc="i")
        target_incd = matrix(0, (n_buses, n_branches), tc="i")
        for branch_idx, branch in enumerate(branches):
            # Find the indexes of the buses at either end of the branch
            source_idx = buses.index(branch.source_bus)
            target_idx = buses.index(branch.target_bus)

            source_incd[source_idx, branch_idx] = 1
            target_incd[target_idx, branch_idx] = 1

        # Matrix multiply
        source_inj = self._theta_inj_source
        bus_inj = source_incd * source_inj + target_incd * -source_inj

        logger.debug("Bus phase shift injection vector:\n%s" % bus_inj)

        return bus_inj

    #--------------------------------------------------------------------------
    #  Cost models:
    #--------------------------------------------------------------------------

    def _get_solver_type(self):
        """ Checks the generator cost models. If they are not all polynomial
            then those that are get converted to piecewise linear models. The
            algorithm attribute is then set accordingly.
        """
        buses = self.network.connected_buses
        generators = self.network.online_generators

        models = [g.cost_model for g in generators]

        if ("polynomial" in models) and ("piecewise linear" in models):
            logger.info("Not all generators use the same cost model, all will "
                "be converted to piece-wise linear.")

            for g in generators:
                g.poly_to_pwl()

            logger.debug("Using linear solver for DC OPF.")
            solver_type = "linear"

        elif "polynomial" not in models:
            logger.debug("Using linear solver for DC OPF.")
            solver_type = "linear"

        elif "piecewise linear" not in models:
            logger.debug("Using quadratic solver for DC OPF.")
            solver_type = "quadratic"

        else:
            logger.error("Invalid cost models specified.")

        return solver_type

    #--------------------------------------------------------------------------
    #  Form vector x:
    #--------------------------------------------------------------------------

    def _get_x(self):
        """ Returns the vector x where, AA * x <= bb.  Stack the initial
            voltage phases for each generator bus, the generator real power
            output and if using pw linear costs, the output cost.
        """
        base_mva = self.network.base_mva
        buses = self.network.connected_buses
        generators = self.network.online_generators

        v_angle = matrix([v.v_angle_guess * pi / 180 for v in buses])

#        _g_buses = [v for v in buses if v.type == "pv" or v.type == "slack"]
#        _g_buses = [v for v in buses if len(v.generators) > 0]

#        p_supply = matrix([v.p_supply / base_mva for v in _g_buses])
        p_supply = matrix([g.p / base_mva for g in generators])

        x = matrix([v_angle, p_supply])

        if self._solver_type == "linear":
            p_cost = []
#            for v in _g_buses:
#                for g in v.generators:
#                    p_cost.append(g.p_cost)
            for g in generators:
                p_cost.append(g.p_cost)

            pw_cost = matrix(p_cost)
            x = matrix([x, pw_cost])

        logger.debug("Built DC OPF x vector:\n%s" % x)

        return x

    #--------------------------------------------------------------------------
    #  Build cost constraint matrices:
    #--------------------------------------------------------------------------

    def _get_cost_constraint(self):
        """ Set up constraint matrix AA where, AA * x <= bb

            For pw linear cost models we must include a constraint for each
            segment of the function. For polynomial (quadratic) models we
            just add an appropriately sized empty matrix.
        """
        base_mva     = self.network.base_mva
        buses        = self.network.connected_buses
        generators   = self.network.online_generators
        n_buses      = len(buses)
        n_generators = len(generators)

        #----------------------------------------------------------------------
        #  Cost constraints ([Cp >= m*Pg + b] => [m*Pg - Cp <= -b]):
        #----------------------------------------------------------------------

        if self._solver_type == "linear": # pw cost constraints
            # A list of the number of cost constraints for each generator
            n_segments = [len(g.pwl_points) - 1 for g in generators]
            # The total number of cost constraints (for matrix sizing)
            n_cc = sum(n_segments)
            # The total number of cost variables.
            n_cost = len(generators)

            a_cost_size = (n_cc, n_buses + n_generators + n_cost)
            a_cost = spmatrix([], [], [], size=a_cost_size, tc='d')

            b_cost = matrix(0.0, size=(n_cc, 1))

            i_segment = 0 # Counter of total segments processed.

            for i, g in enumerate(generators):
#                g_idx = generators.index(g)

                for j in range(n_segments[i]):
                    x1, y1 = g.pwl_points[j]
                    x2, y2 = g.pwl_points[j + 1]

                    m = (y2 - y1) / (x2 - x1) # segment gradient
                    c = y1 - m * x1 # segment y-intercept

                    a_cost[i_segment + j, n_buses + i] = m * base_mva
                    a_cost[i_segment + j, n_buses + n_generators + i] = -1
                    b_cost[i_segment + j] = -c

                i_segment += n_segments[i]

            a_cost[:, n_buses + n_generators:] = -1

        elif self._solver_type == "quadratic":
            # The total number of cost variables
#            n_cost = len([g.p_cost for g in generators])

            a_cost = spmatrix([], [], [], size=(0, n_buses + n_generators))
            b_cost = matrix([], size=(0, 1))

        else:
            raise ValueError

        logger.debug("Cost constraint matrix (Acc):\n%s" % a_cost)
        logger.debug("Cost constraint vector (bcc):\n%s" % b_cost)

        return a_cost, b_cost

    #--------------------------------------------------------------------------
    #  Reference bus constraint matrices:
    #--------------------------------------------------------------------------

    def _get_reference_angle_constraint(self):
        """ Use the slack bus angle for reference or buses[0].
        """
        buses        = self.network.connected_buses
        generators   = self.network.online_generators
        n_buses      = len(buses)
        n_generators = len(generators)

        # Indices of slack buses
        ref_idxs = [buses.index(v) for v in buses if v.slack]

        if len(ref_idxs) == 0:
            ref_idx = 0 # Use the first bus
        elif len(ref_idxs) == 1:
            ref_idx = ref_idxs[0]
        else:
            raise ValueError, "More than one slack/reference bus"

        # Append zeros for piecewise linear cost constraints
        if self._solver_type == "linear":
            n_cost = len([g.p_cost for g in generators])
        else:
            n_cost = 0

        a_ref = spmatrix([], [], [], size=(1, n_buses + n_generators + n_cost))
        a_ref[0, ref_idx] = 1

        b_ref = matrix([buses[ref_idx].v_angle_guess])

        logger.debug("Built reference constraint matrix Aref:\n%s" % a_ref)
        logger.debug("Built reference constraint vector bref:\n%s" % b_ref)

        return a_ref, b_ref

    #--------------------------------------------------------------------------
    #  Active power flow equations:
    #--------------------------------------------------------------------------

    def _get_active_power_flow_equations(self):
        """ P mismatch (B*Va + Pg = Pd).
        """
        base_mva     = self.network.base_mva
        buses        = self.network.connected_buses
        generators   = self.network.online_generators
        n_buses      = len(buses)
        n_generators = len(generators)

#        g_buses = [v for v in buses if len(v.generators) > 0]
#        n_g_buses = len(g_buses)

        # Bus-(online)generator incidence matrix.
        i_bus_generator = spmatrix([],[],[], size=(n_buses, n_generators))

        j = 0
        for i, v in enumerate(buses):
            for g in v.generators:
                if g.online:
                    i_bus_generator[i, j] = 1
                    j += 1

        logger.debug("Built bus generator incidence matrix:\n%s" %
                     i_bus_generator)

        # Include zero matrix for pw linear cost constraints
        if self._solver_type == "linear":
            n_cost = len([g.p_cost for g in generators])
#            cost_mismatch = sparse([matrix(0.0, (n_buses, n_cost))])
            cost_mismatch = spmatrix([], [], [], size=(n_buses, n_cost))
        else:
            cost_mismatch = spmatrix([], [], [], size=(n_buses, 0))

        # sparse() does vstack, to hstack we transpose
        a_mismatch = sparse([self._B.T,
                             -i_bus_generator.T,
                             cost_mismatch.T]).T

        logger.debug("Built power balance constraint matrix Aflow:\n%s" %
                     a_mismatch)

        p_demand = matrix([v.p_demand for v in buses])
        g_shunt = matrix([v.g_shunt for v in buses])

        b_mismatch = -((p_demand + g_shunt) / base_mva) - self._theta_inj_bus

        logger.debug("Built power balance constraint vector bflow:\n%s" %
                     b_mismatch)

        return a_mismatch, b_mismatch

    #--------------------------------------------------------------------------
    #  Active power generation limit constraints:
    #--------------------------------------------------------------------------

    def _get_generation_limit_constraint(self):
        """ Returns the lower and upper limits on generator output. Note that
            bid values are used and represent the volume each generator is
            willing to produce and not the rated capacity of the machine.
        """
        base_mva     = self.network.base_mva
        buses        = self.network.connected_buses
        generators   = self.network.online_generators
        n_buses      = len(buses)
        n_generators = len(generators)

        # An all zero sparse matrix to exclude voltage angles from the
        # constraint.
        limit_zeros = spmatrix([], [], [], size=(n_generators, n_buses))

        # An identity matrix
        limit_eye = spdiag([1.0] * n_generators)

        if self._solver_type == "linear":
            # The total number of cost variables
            n_cost = n_generators
            a_limit_cost = spmatrix([], [], [], (n_generators, n_cost))
        else:
            a_limit_cost = spmatrix([], [], [], (n_generators, 0))

        # The identity matrix made negative to turn the inequality
        # contraint into >=. sparse() does vstack. To hstack we transpose
        a_lower = sparse([limit_zeros.T, -limit_eye.T, a_limit_cost.T]).T

        a_upper = sparse([limit_zeros.T, limit_eye.T, a_limit_cost.T]).T

        a_limit = sparse([a_lower, a_upper])

        logger.debug("Built generator limit constraint matrix:\n%s" % a_limit)


        b_lower = matrix([-g.p_min / base_mva for g in generators])

        b_upper = matrix([g.p_max / base_mva for g in generators])

        b_limit = matrix([b_lower, b_upper])

        logger.debug("Built generator limit constraint vector:\n%s" % b_limit)

        return a_limit, b_limit

    #--------------------------------------------------------------------------
    #  Active power flow limits:
    #--------------------------------------------------------------------------

    def _get_branch_flow_limit_constraint(self):
        """ The real power flows at the from end the lines are related to the
            bus voltage angles by Pf = Bf * Va + Pfinj

            FIXME: No solution when adding this constraint.
        """
        base_mva     = self.network.base_mva
        branches     = self.network.online_branches
        generators   = self.network.online_generators
        n_branches   = len(branches)
        n_generators = len(generators)

        # All zero sparse matrix to exclude power generation from the
        # constraint.
        flow_zeros = spmatrix([], [], [], size=(n_branches, n_generators))
        logger.debug("Built flow limit zeros:\n%s" % flow_zeros)

        if self._solver_type == "linear":
            # The total number of cost variables.
            n_cost = n_generators
            a_flow_cost = spmatrix([], [], [], (n_branches, n_cost))
        else:
            a_flow_cost = spmatrix([], [], [], (n_branches, 0))

        # Source flow limit.
        a_flow_source = sparse([self._B_source.T,
                                flow_zeros.T,
                                a_flow_cost.T]).T

        # Target flow limit.
        a_flow_target = sparse([-self._B_source.T,
                                flow_zeros.T,
                                a_flow_cost.T]).T

        a_flow = sparse([a_flow_source, a_flow_target])

        logger.debug("Built flow limit constraint matrix:\n%s" % a_flow)


        flow_s_max = matrix([e.s_max for e in branches])
        # Source and target limits are both the same.
        source_s_max = flow_s_max / base_mva - self._theta_inj_source
        target_s_max = flow_s_max / base_mva + self._theta_inj_source

        b_flow = matrix([source_s_max, target_s_max])

        logger.debug("Built flow limit constraint vector:\n%s" % b_flow)

        return a_flow, b_flow

    #--------------------------------------------------------------------------
    #  Objective function:
    #--------------------------------------------------------------------------

    def _get_h(self):
        """ H is a sparse square matrix.

            The objective function has the form 0.5 * x'*H*x + c'*x

            Quadratic cost function coefficients: a + bx + cx^2
        """
        base_mva     = self.network.base_mva
        buses        = self.network.connected_buses
        generators   = self.network.online_generators
        n_buses      = len(buses)
        n_generators = len(generators)

        if self._solver_type == "linear":
            dim = n_buses + n_generators + n_generators
            h = spmatrix([], [], [], (dim, dim))
        elif self._solver_type == "quadratic":
            coeffs = [g.cost_coeffs for g in generators]

            # Quadratic cost coefficients in p.u.
            c2_coeffs = matrix([c2 * base_mva**2 for c2, c1, c0 in coeffs])

    #        quad_coeffs = matrix([g.cost_function.c for g in generators])
            # TODO: Find explanation for multiplying by the square
            # of the system base (pu)
#            c_coeffs *= base_mva**2

            # TODO: Explain multiplication of the pu coefficients by 2
            h = spmatrix(2 * c2_coeffs,
                         matrix(range(n_generators)) + n_buses,
                         matrix(range(n_generators)) + n_buses,
                         size=(n_buses + n_generators, n_buses + n_generators))
        else:
            raise ValueError

        logger.debug("Built objective function matrix:\n%s" % h)

        return h


    def _get_c(self):
        """ Build c in the objective function of the form 0.5 * x'*H*x + c'*x

            Quadratic cost function coefficients: c0*x^2 + c1*x + c2
        """
        base_mva     = self.network.base_mva
        buses        = self.network.connected_buses
        generators   = self.network.online_generators
        n_buses      = len(buses)
        n_generators = len(generators)
        n_cost       = n_generators

        if self._solver_type == "linear":
            c = matrix([matrix(0.0, (n_buses + n_generators, 1)),
                        matrix(1.0, (n_cost, 1))])
        else:
            v_zeros = matrix([0] * n_buses)

            cost_coeffs = [g.cost_coeffs for g in generators]

            # Linear cost coefficients in p.u.
            c1_coeffs = matrix([c1 * base_mva for c2, c1, c0 in cost_coeffs])

            c = matrix([v_zeros, c1_coeffs])

        logger.debug("Built objective function vector:\n%s" % c)

        return c


    def _solve_qp(self):

        #Solves a quadratic program
        #    minimize    (1/2)*x'*P*x + q'*x
        #    subject to  G*x <= h
        #                A*x = b.
        #
        #initvals is a dictionary with optional primal and dual starting
        #points initvals['x'], initvals['s'], initvals['y'], initvals['z'].
        #- initvals['x'] is a dense 'd' matrix of size (n,1).
        #- initvals['s'] is a dense 'd' matrix of size (K,1), representing
        #  a vector that is strictly positive with respect to the cone C.
        #- initvals['y'] is a dense 'd' matrix of size (p,1).
        #- initvals['z'] is a dense 'd' matrix of size (K,1), representing
        #  a vector that is strictly positive with respect to the cone C.

        solution = qp(P=self._hh, q=self._cc,
                      G=self._AA_ieq, h=self._bb_ieq,
                      A=self._AA_eq, b=self._bb_eq,
                      solver=self.solver,
                      initvals={"x": self._x})

        #Returns a dictionary with keys 'status', 'x', 's', 'y', 'z'.
        #
        #The default solver returns with status 'optimal' or 'unknown'.
        #The MOSEK solver can also return with status 'primal infeasible'
        #or 'dual infeasible'.
        #
        #If status is 'optimal', x, s, y, z are the primal and dual
        #optimal solutions.
        #
        #If status is 'primal infeasible', x = s = None and z, y are
        #a proof of primal infeasibility:
        #
        #    G'*z + A'*y = 0,  h'*z + b'*y = -1,  z >= 0.
        #
        #If status is 'dual infeasible', z = y = None, and x, s are
        #a proof of dual infeasibility:
        #
        #    P*x = 0,  q'*x = -1,  G*x + s = 0,  A*x = 0,  s >=0
        #
        #If status is 'unknown', x, y, s, z are None.

        logger.debug("Quadratic solver returned:%s" % solution)

        return solution


    def _update_solution_data(self, solution):
        """ Sets bus voltages angles, generator output powers and branch
            power flows using the solution.
        """
        base_mva     = self.network.base_mva
        buses        = self.network.connected_buses
        branches     = self.network.online_branches
        generators   = self.network.online_generators
        n_buses      = len(buses)
        n_generators = len(generators)

        offline_branches = [
            e for e in self.network.branches if e not in branches]
        offline_generators = [
            g for g in self.network.all_generators if g not in generators]

        # Bus voltage angles.
        v_angle = solution["x"][:n_buses]
#        print "Vphase:", v_angle
        for i, bus in enumerate(buses):
            bus.v_magnitude = 1.0
            bus.v_angle = v_angle[i]

        # Generator real power output.
        p = solution["x"][n_buses:n_buses+n_generators]
        for i, generator in enumerate(generators):
            generator.p          = p[i] * base_mva
#            generator.p_despatch = p[i] * base_mva

        # Branch power flows.
        p_source = self._B_source * v_angle * base_mva
        p_target = -p_source
        for j, branch in enumerate(branches):
            branch.p_source = p_source[j]
            branch.p_target = p_target[j]
            branch.q_source = 0.0
            branch.q_target = 0.0

        # Update lambda and mu.
        # A Lagrange multiplier is the increase in the value of the objective
        # function due to the relaxation of a given constraint.
        eqlin   = solution["y"]
        ineqlin = solution["z"]

        for i, bus in enumerate(buses):
            bus.p_lambda = eqlin[i + 1] / base_mva
            bus.q_lambda = 0.0
            bus.mu_v_min = 0.0
            bus.mu_v_max = 0.0

        for j, branch in enumerate(branches):
            # TODO: Find multipliers for lower and upper bound constraints.
            branch.mu_s_source = 0.0
            branch.mu_s_target = 0.0

        for k, generator in enumerate(generators):
            generator.mu_p_min = ineqlin[k] / base_mva
            generator.mu_p_max = ineqlin[k + n_generators] / base_mva
            generator.mu_q_min = 0.0
            generator.mu_q_max = 0.0

        # Zero multipliers for all offline components.
        for branch in offline_branches:
            branch.mu_s_source = 0.0
            branch.mu_s_target = 0.0

        for generator in offline_generators:
            generator.mu_p_min = 0.0
            generator.mu_p_max = 0.0
            generator.mu_q_min = 0.0
            generator.mu_q_max = 0.0

        # Compute the objective function value.
        self.f = sum([g.total_cost(g.p) for g in generators])

# EOF -------------------------------------------------------------------------
