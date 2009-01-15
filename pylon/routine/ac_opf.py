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

""" Optimal power flow routine, translated from MATPOWER.

References:
    D. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, MATPOWER, version 3.2,
    http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
import numpy

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul, exp
from cvxopt import solvers

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "OptimalPowerFlow" class:
#------------------------------------------------------------------------------

class ACOPFRoutine:
    """ Optimal power flow routine, translated from MATPOWER.

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, MATPOWER,
        version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    # Network instance to be optimised.
    network = None

    #--------------------------------------------------------------------------
    #  Algorithm parameters:
    #--------------------------------------------------------------------------

    # Turns the output to the screen on or off.
    show_progress = True

    # Maximum number of iterations.
    max_iterations = 100

    # Absolute accuracy.
    absolute_tol = 1e-7

    # Relative accuracy.
    relative_tol = 1e-6

    # Tolerance for feasibility conditions.
    feasibility_tol = 1e-7

    # Number of iterative refinement steps when solving KKT equations.
    refinement = 1

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network, show_progress=True, max_iterations=100,
            absolute_tol=1e-7, relative_tol=1e-6, feasibility_tol=1e-7,
            refinement=1):
        """ Initialises a new ACOPFRoutine instance. """

        self.network = network
        self.show_progress = show_progress
        self.max_iterations = max_iterations
        self.absolute_tol = absolute_tol
        self.relative_tol = relative_tol
        self.feasibility_tol = feasibility_tol
        self.refinement = refinement

    #--------------------------------------------------------------------------
    #  Solve AC Optimal Power Flow problem:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves AC OPF. """

        # Turn off output to screen.
        solvers.options["show_progress"] = self.show_progress
        solvers.options["maxiters"] = self.max_iterations
        solvers.options["abstol"] = self.absolute_tol
        solvers.options["reltol"] = self.relative_tol
        solvers.options["feastol"] = self.feasibility_tol
        solvers.options["refinement"] = self.refinement

        network = self.network
        logger.debug("Solving AC OPF [%s]" % network.name)

        buses = network.non_islanded_buses
        generators = network.in_service_generators
        n_buses = len(network.non_islanded_buses)
        n_branches = len(network.in_service_branches)
        n_generators = len(network.in_service_generators)

        # The number of non-linear equality constraints.
        n_equality = 2*n_buses
        # The number of control variables.
        n_control = 2*n_buses + 2*n_generators

        # Definition of indexes for the optimisation variable vector.
        ph_base = 0 # Voltage phase angle.
        ph_end = ph_base + n_buses-1;
        v_base = ph_end + 1
        v_end = v_base + n_buses-1
        pg_base = v_end + 1
        pg_end = pg_base + n_generators-1
        qg_base = pg_end + 1
        qg_end = qg_base + n_generators-1

        # Definition of indexes for the constraint vector

        def F(x=None, z=None):
            """ Evaluates the objective and nonlinear constraint functions. """

            if x is None:
                # Compute initial vector.
                x_ph = matrix([bus.v_phase_guess for bus in buses])
                # TODO: Initialise V from any present generators.
                x_v = matrix([bus.v_amplitude_guess for bus in buses])
                x_pg = matrix([g.p for g in generators])
                x_qg = matrix([g.q for g in generators])
                
                return n_equality, matrix([x_ph, x_v, x_pg, x_qg])

            # Evaluate objective function -------------------------------------

            print "X:", x

            p_gen = x[pg_base:pg_end+1] # Active generation in p.u.
            q_gen = x[qg_base:qg_end+1] # Reactive generation in p.u.

            # Setting P and Q for each generator triggers re-evaluation of the
            # generator cost.
            for i, g in enumerate(generators):
                g.p = p_gen[i]# * network.mva_base
                g.q = q_gen[i]# * network.mva_base

            costs = matrix([g.p_cost for g in generators])
            f = sum(costs)
            # TODO: Generalised cost term.

            # Evaluate cost gradient ------------------------------------------

            # Partial derivative w.r.t. polynomial cost Pg and Qg.
            df = spmatrix([], [], [], (n_generators*2, 1))
            for i, g in enumerate(generators):
                derivative = numpy.polyder(list(g.cost_coeffs))
                df[i] = numpy.polyval(derivative, g.p) * network.mva_base
            print "dF_dPgQg:", df

            if z is None:
                return f, df

            # Evaluate cost Hessian -------------------------------------------

            d2f_d2pg = spmatrix([], [], [], (n_generators, 1))
            d2f_d2qg = spmatrix([], [], [], (n_generators, 1))
            for i, g in enumerate(generators):
                der = numpy.polyder(list(g.cost_coeffs))
                d2f_d2pg[i] = numpy.polyval(der, g.p) * network.mva_base
                # TODO: Implement reactive power costs.

            i = matrix(range(pg_base, qg_end+1)).T
            H = spmatrix(matrix([d2f_d2pg, d2f_d2qg]), i, i)

            return f, df, H


        # cp(F, G=None, h=None, dims=None, A=None, b=None, kktsolver=None)
        #
        #     minimize    f0(x)
        #     subject to  fk(x) <= 0, k = 1, ..., mnl
        #                 G*x   <= h
        #                 A*x   =  b.
        solution = solvers.cp(F)


    def _build_additional_linear_constraints(self):
        """ A, l, u represent additional linear constraints on the
        optimization variables. """

        if Au is None:
            Au = sparse([], [], [], (0, 0))
            l_bu = matrix([0])
            u_bu = matrix([0])

        # Piecewise linear convex costs
        A_y = spmatrix([], [], [], (0, 0))
        b_y = matrix([0])

        # Branch angle difference limits
        A_ang = spmatrix([], [], [], (0, 0))
        l_ang = matrix([0])
        u_ang = matrix([0])

        # Despatchable loads
        A_vl = spmatrix([], [], [], (0, 0))
        l_vl = matrix([0])
        u_vl = matrix([0])

        # PQ capability curves
        A_pqh = spmatrix([], [], [], (0, 0))
        l_bpqh = matrix([0])
        u_bpqh = matrix([0])

        A_pql = spmatrix([], [], [], (0, 0))
        l_bpql = matrix([0])
        u_bpql = matrix([0])

        # Build linear restriction matrix. Note the ordering.
        # A, l, u represent additional linear constraints on
        # the optimisation variables
        A = sparse([Au, A_pqh, A_pql, A_vl, A_ang])
        l = matrix([l_bu, l_bpqh, l_bpql, l_vl, l_ang])
        u = matrix([u_bu, u_bpqh, u_bpql, u_vl, l_ang])

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from os.path import join, dirname
    from pylon.readwrite.api import read_matpower

    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    data_file = join(dirname(__file__), "../test/data/case6ww.m")
    n = read_matpower(data_file)

    ac_opf = ACOPFRoutine(network=n)
    ac_opf.solve()

# EOF -------------------------------------------------------------------------
