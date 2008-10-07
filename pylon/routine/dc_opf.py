#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" DC Optimal Power Flow for routine

References:
    D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
    MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from os.path import join, dirname
from math import pi

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul
from cvxopt.umfpack import linsolve
from cvxopt.solvers import qp

from pylon.api import Network
from pylon.routine.y import SusceptanceMatrix
from pylon.traits import Matrix, SparseMatrix

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
#  "DCOPFRoutine" class:
#------------------------------------------------------------------------------

class DCOPFRoutine:
    """ A method class for solving the DC optimal power flow problem

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The network whose power flow is to be optimised:
    network = Network

    # Choice of solver (May be None or "mosek")
    solver = None

    # Branche susceptance matirx.  The bus real power injections are related
    # to bus voltage angles by P = Bbus * Va + Pbusinj
    _B = spmatrix

    # Branch source bus susceptance matrix. The real power flows at the from
    # end the lines are related to the bus voltage angles by
    # Pf = Bf * Va + Pfinj
    _B_source = spmatrix

    # The real power flows at the from end the lines are related to the bus
    # voltage angles by Pf = Bf * Va + Pfinj
    _theta_inj_source = matrix

    # The bus real power injections are related to bus voltage angles by
    # P = Bbus * Va + Pbusinj
    _theta_inj_bus = matrix

    # For polynomial cost models we use a quadratic solver:
    _solver_type = "linear" # or "quadratic"

    # Initial values for x:
    _x = matrix

    # Cost constraints:
    _aa_cost = spmatrix
    _bb_cost = matrix

    # Reference bus phase angle constraint:
    _aa_ref = spmatrix
    _bb_ref = matrix

    # Active power flow equations:
    _aa_mismatch = spmatrix
    _bb_mismatch = matrix

    # Generator limit constraints:
    _aa_generation = spmatrix
    _bb_generation = matrix

    # Branch flow limit constraints:
    _aa_flow = spmatrix
    _bb_flow = matrix

    # The equality and inequality problem constraints combined:
    _AA_eq = spmatrix
    _AA_ieq = spmatrix
    _bb_eq = matrix
    _bb_ieq = matrix

    # Objective function of the form 0.5 * x'*H*x + c'*x:
    _hh = spmatrix
    _cc = matrix

    # The solution:
    x = matrix

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network):
        """ Returns a new DCOPFRoutine instance """

        self.network = network

    #--------------------------------------------------------------------------
    #  Solve DC Optimal Power Flow problem:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves a DC OPF """

        logger.debug("Solving DC OPF [%s]" % self.network.name)

        solution = None

        sm = SusceptanceMatrix()
        self._B, self._B_source = sm.build(self.network)
        self._build_theta_inj_source()
        self._build_theta_inj_bus()
        self._check_cost_model_consistency()
        self._build_x()
        # Problem constraints
        self._build_cost_constraint()
        self._build_reference_angle_constraint()
        self._build_active_power_flow_equations()
        self._build_generation_limit_constraint()
        self._build_branch_flow_limit_constraint()

        self._build_AA_equality()
        self._build_AA_inequality()
        self._build_bb_equality()
        self._build_bb_inequality()

        # Objective function:
        self._build_h()
        self._build_c()

        # Solve the problem:
        solution = self._solve_qp()

        if solution["status"] == "optimal":
            self._update_solution_data(solution)

        return solution

    #--------------------------------------------------------------------------
    #  Phase shift injection vectors:
    #--------------------------------------------------------------------------

    def _build_theta_inj_source(self):
        """ Builds the phase shift "quiescent" injections

        | Pf |   | Bff  Bft |   | Vaf |   | Pfinj |
        |    | = |          | * |     | + |       |
        | Pt |   | Btf  Btt |   | Vat |   | Ptinj |

        """

        branches = self.network.in_service_branches

        b = matrix([1/e.x * e.in_service for e in branches])
        angle = matrix([-e.phase_shift*pi/180 for e in branches])

        # Element-wise multiply
        # http://abel.ee.ucla.edu/cvxopt/documentation/users-guide/node9.html
        source_inj = mul(b, angle)

        logger.debug(
            "Built source bus phase shift injection vector:\n%s" %
            source_inj
        )

        self._theta_inj_source = source_inj

        return source_inj


    def _build_theta_inj_bus(self):
        """ Pbusinj = dot(Cf, Pfinj) + dot(Ct, Ptinj) """

        buses = self.network.non_islanded_buses
        branches = self.network.in_service_branches
        n_buses = self.network.n_non_islanded_buses
        n_branches = self.network.n_in_service_branches

        # Build incidence matrices
        source_incd = matrix(0, (n_buses, n_branches), tc="i")
        target_incd = matrix(0, (n_buses, n_branches), tc="i")

        i = 0
        for e in branches:
            # Find the indexes of the buses at either end of the branch
            source_idx = buses.index(e.source_bus)
            target_idx = buses.index(e.target_bus)

            source_incd[source_idx, i] = 1
            target_incd[target_idx, i] = 1

            i += 1

        # matrix multiply
        source_inj = self._theta_inj_source
        bus_inj = source_incd * source_inj + target_incd * -source_inj

        logger.debug(
            "Built bus phase shift injection vector:\n%s" % bus_inj
        )

        self._theta_inj_bus = bus_inj

        return bus_inj

    #--------------------------------------------------------------------------
    #  Cost models:
    #--------------------------------------------------------------------------

    def _check_cost_model_consistency(self):
        """ Checks the generator cost models. If they are not all polynomial
        then those that are get converted to piecewise linear models.  The
        algorithm trait is then set accordingly.

        """

        buses = self.network.non_islanded_buses
        generators = self.network.in_service_generators

        models = [g.cost_model for g in generators]

        if "Polynomial" in models and "Piecewise Linear" in models:
            logger.info(
                "Not all generators use the same cost model, all will "
                "be converted to piece-wise linear"
            )

            # TODO: Implemented conversion of polynomial cost models
            # to piecewise linear models
            raise NotImplementedError, "Yet to implement polynomial to " \
                "piecewise linear conversion"

            logger.debug("Using linear solver for DC OPF")
            self._solver_type = "linear"

        elif "Polynomial" not in models:
            logger.debug("Using linear solver for DC OPF")
            self._solver_type = "linear"

        elif "Piecewise Linear" not in models:
            logger.debug("Using quadratic solver for DC OPF")
            self._solver_type = "quadratic"

        else:
            logger.info("No valid cost models specified")

    #--------------------------------------------------------------------------
    #  Form vector x:
    #--------------------------------------------------------------------------

    def _build_x(self):
        """ Builds the vector x where, AA * x <= bb.  Stack the initial voltage
        phases for each generator bus, the generator real power output and
        if using pw linear costs, the output cost.

        """

        buses = self.network.non_islanded_buses

        v_phase = matrix([v.v_phase_guess*pi/180 for v in buses])

#        _g_buses = [v for v in buses if v.type == "PV" or v.type == "Slack"]
        _g_buses = [v for v in buses if len(v.generators) > 0]

        p_supply = matrix([v.p_supply for v in _g_buses])

        x = matrix([v_phase, p_supply])

        if self._solver_type == "linear":
            p_cost = []
            for v in _g_buses:
                for g in v.generators:
                    p_cost.append(g.p_cost)
            pw_cost = matrix(p_cost)
            x = matrix([x, pw_cost])

        logger.debug("Built DC OPF x vector:\n%s" % x)

        self._x = x

        return x

    #--------------------------------------------------------------------------
    #  Build cost constraint matrices:
    #--------------------------------------------------------------------------

    def _build_cost_constraint(self):
        """ Set up constraint matrix AA where, AA * x <= bb

        For pw linear cost models we must include a constraint for each
        segment of the function. For polynomial (quadratic) models we
        just add an appropriately sized empty matrix.

        """

        buses = self.network.non_islanded_buses
        generators = self.network.in_service_generators
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

        #----------------------------------------------------------------------
        #  Cost constraints ([Cp >= m*Pg + b] => [m*Pg - Cp <= -b]):
        #----------------------------------------------------------------------

        if self._solver_type == "linear": # pw cost constraints
            # A list of the number of cost constraints for each generator
            n_segments = [len(g.pwl_points)-1 for g in generators]
            # The total number of cost constraints (for matrix sizing)
            n_cc = sum(n_segments)
            # The total number of cost variables
            n_cost = len([g.p_cost for g in generators])

            a_cost_size = (n_cc, n_buses+n_generators+n_cost)
            a_cost = spmatrix([], [] ,[], size=a_cost_size)
            b_cost = matrix([0]*n_cost)

            i_segment = 0 # Counter of segments processed

            for g in generators:
                g_idx = generators.index(g)
                g_n_segments = len(g.pwl_points)-1

                for i in range(g_n_segments):
                    x1, y1 = g.pwl_points[i]
                    x2, y2 = g.pwl_points[i+1]

                    m = (y2-y1)/(x2-x1) # segment gradient
                    c = y1 - m*x1 # segment y-intercept

                    a_cost[i_segment+i, n_buses+g_idx] = m #* base_mva
                    a_cost[i_segment+i, n_buses+n_generators+i]
                    b_cost[i_segment+i] = -c

                i_segment += g_n_segments

            a_cost[:, n_buses+n_generators:] = -1

        elif self._solver_type == "quadratic":
            # The total number of cost variables
            n_cost = len([g.p_cost for g in generators])

            a_cost = spmatrix([], [], [], size=(0, n_buses+n_generators))
            b_cost = matrix([], size=(0,1))

        else:
            raise ValueError, "Invalid solver trait"

        logger.debug("Built cost constraint matrix Acc:\n%s" % a_cost)
        logger.debug("Built cost constraint vector bcc:\n%s" % b_cost)

        self._aa_cost = a_cost
        self._bb_cost = b_cost

    #--------------------------------------------------------------------------
    #  Reference bus constraint matrices:
    #--------------------------------------------------------------------------

    def _build_reference_angle_constraint(self):
        """ Use the slack bus angle for reference or buses[0] """

        buses = self.network.non_islanded_buses
        generators = self.network.in_service_generators
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

        # Indices of slack buses
        ref_idxs = [buses.index(v) for v in buses if v.slack]

        if len(ref_idxs) == 0:
            ref_idx = 0 # Use the first bus
        elif len(ref_idxs) == 1:
            ref_idx = ref_idxs[0]
        else:
            raise ValueError, "More than on slack/reference bus"

        # Append zeros for piecewise linear cost constraints
        if self._solver_type == "linear":
            n_cost = len([g.p_cost for g in generators])
        else:
            n_cost = 0

        a_ref = spmatrix([], [], [], size=(1, n_buses+n_generators+n_cost))
        a_ref[0, ref_idx] = 1

        b_ref = matrix([buses[ref_idx].v_phase_guess])

        logger.debug("Built reference constraint matrix Aref:\n%s" % a_ref)
        logger.debug("Built reference constraint vector bref:\n%s" % b_ref)

        self._aa_ref = a_ref
        self._bb_ref = b_ref

    #--------------------------------------------------------------------------
    #  Active power flow equations:
    #--------------------------------------------------------------------------

    def _build_active_power_flow_equations(self):
        """ P mismatch (B*Va + Pg = Pd) """

        buses = self.network.non_islanded_buses
        generators = self.network.in_service_generators
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

#        g_buses = [v for v in buses if len(v.generators) > 0]
#        n_g_buses = len(g_buses)

        i_bus_generator = spmatrix([], [], [], size=(n_buses, n_generators))

        # TODO: Beautify
        j = 0
        for v in buses:
            i = buses.index(v)
            for g in v.generators:
                i_bus_generator[i,j] = 1
                j += 1

        logger.debug(
            "Built bus generator incidence matrix:\n%s" % i_bus_generator
        )

        # Include zero matrix for pw linear cost constraints
        if self._solver_type == "linear":
            n_cost = len([g.p_cost for g in generators])
            cost_mismatch = sparse([matrix(zeros((n_buses, n_cost)))])
        else:
            cost_mismatch = spmatrix([], [], [], size=(n_buses, 0))

        # sparse() does vstack, to hstack we transpose
        a_mismatch = sparse(
            [self._B.T, -i_bus_generator.T, cost_mismatch.T]
        ).T

        logger.debug(
            "Built power balance constraint matrix Aflow:\n%s" % a_mismatch
        )

        self._aa_mismatch = a_mismatch

        p_demand = matrix([v.p_demand for v in buses])
        g_shunt = matrix([v.g_shunt for v in buses])

        b_mismatch = -(p_demand+g_shunt)-self._theta_inj_bus

        logger.debug(
            "Built power balance constraint vector bflow:\n%s" % b_mismatch
        )

        self._bb_mismatch = b_mismatch

    #--------------------------------------------------------------------------
    #  Active power generation limit constraints:
    #--------------------------------------------------------------------------

    def _build_generation_limit_constraint(self):

        buses = self.network.n_non_islanded_buses
        generators = self.network.in_service_generators
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

        # An all zero sparse matrix to exclude voltage angles from the
        # constraint.
        limit_zeros = spmatrix([], [], [], size=(n_generators, n_buses))

        # An identity matrix
        limit_eye = spdiag([1.0]*n_generators)

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

        self._aa_generation = a_limit


        b_lower = matrix([g.p_min for g in generators])

        b_upper = matrix([g.p_max for g in generators])

        b_limit = matrix([b_lower, b_upper])

        logger.debug("Built generator limit constraint vector:\n%s" % b_limit)

        self._bb_generation = b_limit

    #--------------------------------------------------------------------------
    #  Active power flow limits:
    #--------------------------------------------------------------------------

    def _build_branch_flow_limit_constraint(self):
        """ The real power flows at the from end the lines are related to the
        bus voltage angles by Pf = Bf * Va + Pfinj

        FIXME!

        """

        branches = self.network.in_service_branches
        generators = self.network.in_service_generators
        n_branches = self.network.n_in_service_branches
        n_generators = self.network.n_in_service_generators

        # All zero sparse matrix to exclude power generation from the
        # constraint.
        flow_zeros = spmatrix([], [], [], size=(n_branches, n_generators))
        logger.debug("Built flow limit zeros:\n%s" % flow_zeros)

        if self._solver_type == "linear":
            # The total number of cost variables
            n_cost = n_generators
            a_flow_cost = spmatrix([], [], [], (n_branches, n_cost))
        else:
            a_flow_cost = spmatrix([], [], [], (n_branches, 0))

        # Source flow limit
        a_flow_source = sparse([
            self._B_source.T, flow_zeros.T, a_flow_cost.T
        ]).T

        # Target flow limit
        a_flow_target = sparse([
            -self._B_source.T, flow_zeros.T, a_flow_cost.T
        ]).T

        a_flow = sparse([a_flow_source, a_flow_target])

        logger.debug("Built flow limit constraint matrix:\n%s" % a_flow)

        self._aa_flow = a_flow


        flow_s_max = matrix([e.s_max for e in branches])
        # Source and target limits are both the same
        source_s_max = flow_s_max - self._theta_inj_source
        target_s_max = flow_s_max + self._theta_inj_source

        b_flow = matrix([source_s_max, target_s_max])

        logger.debug("Built flow limit constraint vector:\n%s" % b_flow)

        self._bb_flow = b_flow

    #--------------------------------------------------------------------------
    #  Constraints combined:
    #--------------------------------------------------------------------------

    def _build_AA_equality(self):

        AA_eq = sparse([
            self._aa_cost,
            self._aa_ref,
            self._aa_mismatch
        ])

        logger.debug("Built equality constraint matrix AA:\n%s" % AA_eq)

        self._AA_eq = AA_eq


    def _build_bb_equality(self):

        bb_eq = matrix([
            self._bb_cost,
            self._bb_ref,
            self._bb_mismatch
        ])

        logger.debug("Build equality constraint vector bb:\n%s" % bb_eq)

        self._bb_eq = bb_eq


    def _build_AA_inequality(self):

        AA_ieq = sparse([
            self._aa_generation,
            # FIXME: Branch flow limit constraint
#            self._aa_flow,
        ])

        logger.debug("Built inequality constraint matrix AAieq:\n%s" % AA_ieq)

        self._AA_ieq = AA_ieq


    def _build_bb_inequality(self):

        bb_ieq = matrix([
            self._bb_generation,
            # FIXME: Branch flow limit constraint
#            self._bb_flow
        ])

        logger.debug("Build inequality constraint vector bb:\n%s" % bb_ieq)

        self._bb_ieq = bb_ieq

    #--------------------------------------------------------------------------
    #  Objective function:
    #--------------------------------------------------------------------------

    def _build_h(self):
        """ H is a sparse square matrix.

        The objective function has the form 0.5 * x'*H*x + c'*x

        Quadratic cost function coefficients: a + bx + cx^2

        """

        base_mva = self.network.mva_base
        buses = self.network.non_islanded_buses
        generators = self.network.in_service_generators
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

        if self._solver_type == "linear":
            raise NotImplementedError
        else:
            cost_coeffs = [g.cost_coeffs for g in generators]

            # Quadratic cost coefficients in p.u.
            c0_coeffs = matrix([c0*base_mva**2 for c0, c1, c2 in cost_coeffs])

    #        quad_coeffs = matrix([g.cost_function.c for g in generators])
            # TODO: Find explanation for multiplying by the square
            # of the system base (pu)
#            c_coeffs *= base_mva**2

            # TODO: Find explanation for multiplying by the pu coefficients by 2
            h = spmatrix(
                2*c0_coeffs,
                matrix(range(n_generators))+n_buses,
                matrix(range(n_generators))+n_buses,
                size=(n_buses+n_generators, n_buses+n_generators)
            )

        logger.debug("Built objective function matrix:\n%s" % h)

        self._hh = h


    def _build_c(self):
        """ Build c in the objective function of the form 0.5 * x'*H*x + c'*x

        Quadratic cost function coefficients: c0*x^2 + c1*x + c2

        """

        base_mva = self.network.mva_base
        buses = self.network.non_islanded_buses
        generators = self.network.in_service_generators
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

        if self._solver_type == "linear":
            raise NotImplementedError
        else:
            v_zeros = matrix([0]*n_buses)

            cost_coeffs = [g.cost_coeffs for g in generators]

            # Linear cost coefficients in p.u.
            c1_coeffs = matrix([c1*base_mva for c0, c1, c2 in cost_coeffs])

            c = matrix([v_zeros, c1_coeffs])

        logger.debug("Built objective function vector:\n%s" % c)

        self._cc = c


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

        solution = qp(
            P=self._hh, q=self._cc,
            G=self._AA_ieq, h=self._bb_ieq,
            A=self._AA_eq, b=self._bb_eq,
            solver=self.solver,
            initvals={"x": self._x}
        )

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

        self.x = solution["x"]

        return solution


    def _update_solution_data(self, solution):

        buses = self.network.non_islanded_buses
        generators = self.network.in_service_generators
        n_buses = self.network.n_non_islanded_buses
        n_generators = self.network.n_in_service_generators

#        print "Solution x:\n", solution["x"]
#        print "Solution s:\n", solution["s"]
#        print "Solution y:\n", solution["y"]
#        print "Solution z:\n", solution["z"]

        v_phase = solution["x"][:n_buses]

#        print "Vphase:", v_phase

        for i, bus in enumerate(buses):
            bus.v_amplitude = 1.0
            bus.v_phase = v_phase[i]

        p = solution["x"][n_buses:n_buses+n_generators]

#        print "Pg:", p

        for i, generator in enumerate(generators):
            generator.p = p[i]

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from pylon.filter.api import MATPOWERImporter

    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    filter = MATPOWERImporter()
#    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
    data_file = "/home/rwl/python/aes/matpower_3.2/case30.m"
    n = filter.parse_file(data_file)

    dc_opf = DCOPFRoutine(network=n)
    dc_opf.configure_traits()
#    dc_opf.solve()


# EOF -------------------------------------------------------------------------
