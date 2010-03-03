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

""" The standard OPF formulation has no mechanism for completely shutting down
    generators which are very expensive to operate. Instead they are simply
    dispatched at their minimum generation limits. PYLON includes the
    capability to run an optimal power flow combined with a unit decommitment
    for a single time period, which allows it to shut down these expensive
    units and find a least cost commitment and dispatch [1].

    [1] Ray Zimmerman, "MATPOWER User's Manual", MATPOWER, PSERC Cornell,
        version 3.2, http://www.pserc.cornell.edu/matpower/, September, 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging
import random

from numpy import matrix

from pylon import OPF

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "UDOPF" class:
#------------------------------------------------------------------------------

class UDOPF(object):
    """ Solves a combined unit decommitment and optimal power flow for a
        single time period. Uses an algorithm similar to dynamic programming.
        It proceeds through a sequence of stages, where stage N has N
        generators shut down, starting with N=0. In each stage, it forms a list
        of candidates (gens at their Pmin limits) and computes the cost with
        each one of them shut down. It selects the least cost case as the
        starting point for the next stage, continuing until there are no more
        candidates to be shut down or no more improvement can be gained by
        shutting something down [2].

        [2] Ray Zimmerman, "uopf.m", MATPOWER, PSERC Cornell, version 3.2,
            http://www.pserc.cornell.edu/matpower/, March, 2006
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, dc=True, solver=None, show_progress=False,
            max_iterations=100, absolute_tol=1e-7, relative_tol=1e-6,
            feasibility_tol=1e-7):
        """ Initialises a new UDOPF instance.
        """
        # Use DC OPF solver?
        self.dc = dc
        self.solver = None

        # Optimised case.
        self.case = case

        # Choice of solver (May be None or "mosek" (or "glpk" for linear
        # formulation)). Specify None to use the Python solver from CVXOPT.
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


#    @property
#    def f(self):
#        """ Objective function value. Delegates to the solver used.
#        """
#        return self.solver.f


    def solve(self):
        """ Solves the combined unit decommitment / optimal power flow problem.
        """
        t0 = time.time()

        case = self.case

        generators = case.online_generators

        logger.info("Solving OPF with unit decommitment [%s]." % case.name)

        # 1. Begin at stage zero (N = 0), assuming all generators are on-line
        # with all limits in place. At most one generator shutdown per stage.
        i_stage = 0

        # Check for sum(p_min) > total load, decommit as necessary.
        online       = [g for g in generators if not g.is_load]
        online_vload = [g for g in generators if g.is_load]

        # Total dispatchable load capacity.
        vload_capacity = sum([g.p_min for g in online_vload])
        # Total load capacity.
        load_capacity = sum([b.p_demand for b in case.buses]) - vload_capacity

        # Minimum total online generation capacity.
        p_min_tot = sum([g.p_min for g in online])

        # Shutdown the most expensive units until the minimum generation
        # capacity is less than the total load capacity.
        while p_min_tot > load_capacity:
            i_stage += 1
            logger.debug("Entered decommitment stage %d." % i_stage)

            # Find generator with the maximum average cost at Pmin.
            avg_pmin_cost = [g.total_cost(g.p_min) / g.p_min for g in online]
            # Select at random from maximal generators with equal cost.
            g_idx, _ = fair_max(avg_pmin_cost)
            generator = online[g_idx]

            logger.info("Shutting down generator [%s] to satisfy all "
                        "p_min limits." % generator.name)

            # Shut down most expensive unit.
            generator.online = False

            # Update minimum generation capacity for while loop.
            online = [g for g in case.online_generators if not g.is_load]
            p_min_tot = sum([g.p_min for g in online])

        # 2. Solve a normal OPF and save the solution as the current best.
        cvxopt   = True
        solver   = self.solver
        progress = self.show_progress
        itermax  = self.max_iterations
        abstol  = self.absolute_tol
        reltol  = self.relative_tol
        feastol = self.feasibility_tol

        solver = self.solver = OPF(case, self.dc, solver, progress, itermax,
                                   abstol, reltol, feastol)

        # Initial solve fo the OPF problem.
        solution = solver.solve()

        status = solution["status"]
        if not status == "optimal" or status == "unknown":
            logger.error("Non-convergent OPF [%s]." % solution["status"])
            return solution

        # 3. Go to the next stage, N = N + 1. Using the best solution from the
        # previous stage as the base case for this stage, ...

        # Best case so far. A list of the on-line status of all generators.
        overall_online = [g.online for g in case.generators]
        # The objective function value is the total system cost.
        overall_cost = solution["primal objective"]

        # Best case for this stage.
        stage_online = overall_online
        stage_cost   = overall_cost

        # Shutdown at most one generator per stage.
        while True:
            # 4. ...form a candidate list of generators with minimum
            # generation limits binding.

            # Activate generators according to the stage best.
            for i, generator in enumerate(case.generators):
                generator.online = stage_online[i]

            # Get candidates for shutdown. Lagrangian multipliers are often
            # very small so we round to four decimal places.
            candidates = [g for g in case.online_generators if \
                          (g.mu_pmin > 0.0) and (g.p_min > 0.0)]

            if not candidates: break

            # Assume no improvement during this stage.
            done = True

            i_stage += 1
            logger.debug("Entered decommitment stage %d." % i_stage)

            for candidate in candidates:
                # 5. For each generator on the candidate list, solve an OPF to
                # find the total system cost with this generator shut down.

                # Activate generators according to the stage best.
                for i, generator in enumerate(case.generators):
                    generator.online = stage_online[i]

                # Shutdown candidate generator.
                candidate.online = False

                logger.info("Attempting OPF with generator '%s' shutdown." %
                    candidate.name)

                # Run OPF.
                solution = solver(case)

                # Compare total system costs for improvement.
                if solution["status"]=="optimal" and (solver.f < overall_cost):
                    # 6. Replace the current best solution with this one if it
                    # has a lower cost.
                    overall_online = [g.online for g in case.generators]
                    overall_cost   = solver.f
                    # Check for further decommitment.
                    done = False

            if done:
                # Decommits at this stage did not help.
                break
            else:
                # 7. If any of the candidate solutions produced an improvement,
                # return to step 3.

                # Shutting something else down helps, so let's keep going.
                logger.info("Shutting down generator '%s'.", candidate.name)

                stage_online = overall_online
                stage_cost   = overall_cost

        # 8. Use the best overall solution as the final solution.
        for i, generator in enumerate(case.generators):
            generator.online = overall_online[i]

        # One final solve using the best case to ensure all results are
        # up-to-date.
        solution = solver.solve()

        # Compute elapsed time and log it.
        elapsed = self.elapsed = time.time() - t0
        plural = "" if i_stage == 1 else "s"
        logger.info("Unit decommitment OPF solved in %.3fs (%d decommitment "
                    "stage%s)." % (elapsed, i_stage, plural))

        return solution

#------------------------------------------------------------------------------
#  "fair_max" function:
#------------------------------------------------------------------------------

def fair_max(x):
    """ Takes a single iterable as an argument and returns the same output as
        the built-in function max with two output parameters, except that where
        the maximum value occurs at more than one position in the  vector, the
        index is chosen randomly from these positions as opposed to just
        choosing the first occurance.
    """
    value = max(x)
    # List indexes of max value.
    i = [x.index(v) for v in x if v == value]
    # Select index randomly among occurances.
    idx = random.choice(i)

    return idx, value

# EOF -------------------------------------------------------------------------
