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

""" The standard OPF formulation has no mechanism for completely shutting down
    generators which are very expensive to operate. Instead they are simply
    dispatched at their minimum generation limits. PYLON includes the
    capability to run an optimal power flow combined with a unit decommitment
    for a single time period, which allows it to shut down these expensive
    units and find a least cost commitment and dispatch.

    References:
        Ray Zimmerman, "MATPOWER User's Manual", MATPOWER, PSERC Cornell,
        version 3.2, http://www.pserc.cornell.edu/matpower/, September, 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging
import random

from cvxopt import matrix

from pylon import DCOPF, ACOPF

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
        shutting something down.

        References:
            Ray Zimmerman, "uopf.m", MATPOWER, PSERC Cornell, version 3.2,
            http://www.pserc.cornell.edu/matpower/, March, 2006
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, dc=True):
        """ Initialises a new UDOPF instance.
        """
        # Use DC OPF routine?
        self.dc = dc
        # Optimised network.
        self.network = None


    def __call__(self, network):
        """ Calls the routine with the given network.
        """
        self.solve(network)


    def solve(self, network=None):
        """ Solves the combined unit decommitment / optimal power flow problem.
        """
        t0 = time.time()

        network = self.network if network is None else network
        generators = network.online_generators
        loads = network.online_loads

        logger.info("Solving OPF with unit decommitment [%s]." % network.name)

        # 1. Begin at stage zero (N = 0), assuming all generators are on-line
        # with all limits in place.


        # Check for sum(p_min) > total load, decommit as necessary.
        online       = [g for g in generators if not g.is_load]
        online_vload = [g for g in generators if g.is_load]

        # Total dispatchable load capacity.
        vload_capacity = sum([g.p_min for g in online_vload])
        # Total load capacity.
        load_capacity = sum([l.p for l in loads]) - vload_capacity

        # Minimum total online generation capacity.
        p_min_tot = sum([g.p_min for g in online])

        while p_min_tot > load_capacity:
            # Shut down most expensive unit.
            avg_pmin_cost = [g.total_cost(g.p_min) / g.p_min for g in online]

            # Find generator with the maximum average cost at Pmin.
            g_idx, value = fair_max(avg_pmin_cost)
            generator = online[g_idx]

            logger.info("Shutting down generator [%s] to satisfy all "
                        "p_min limits." % generator.name)

            # Set generation to zero.
#            generator.p = 0.0
#            generator.q = 0.0
            generator.online = False

            # Update minimum gen capacity.
            online = [g for g in network.online_generators if not g.is_load]
            p_min_tot = sum([g.p_min for g in online])

        # 2. Solve a normal OPF and save the solution as the current best.

        if self.dc:
            routine = DCOPF()
        else:
            routine = ACOPF()
        success = routine(network)

        if not success:
            logger.error("Non-convergent OPF [%s]." % routine)
            return False

        # 3. Go to the next stage, N = N + 1. Using the best solution from the
        # previous stage as the base case for this stage, ...

        # Best case so far.
        overall_online = [g.online for g in network.all_generators]
        overall_cost   = routine.f

        # Best case for this stage (ie. with n gens shut down, n=0,1,2 ...).
        stage_online = overall_online
        stage_cost   = overall_cost

        # Shutdown at most one generator per stage.
        while True:
            # 4. ...form a candidate list of generators with minimum
            # generation limits binding.

            # Activate generators according to the stage best.
            for i, generator in enumerate(network.all_generators):
                generator.online = stage_online[i]
            # Get candidates for shutdown.
            candidates = [g for g in network.online_generators if \
                          (g.mu_p_min > 0.0) and (g.p_min > 0.0)]

            if not candidates:
                break

            # No improvement during this stage.
            done = True

            for candidate in candidates:
                # 5. For each generator on the candidate list, solve an OPF to
                # find the total system cost with this generator shut down.

                # Start with best for this stage.
#                gen = gen0

                # Shutdown candidate generator.
#                candidate.p = 0.0
#                candidate.q = 0.0
                candidate.online = False

                # Run OPF.
                success = routine(network)

                # Something better?
                if success and (routine.f < overall_cost):
                    # 6. Replace the current best solution with this one if it
                    # has a lower cost.
                    overall_online = network.online_generators
                    overall_cost   = routine.f
                    # Make sure we check for further decommitment.
                    done = False

            if done:
                # Decommits at this stage did not help.
                break
            else:
                # 7. If any of the candidate solutions produced an improvement,
                # return to step 3.

                # Shutting something else down helps, so let's keep going.
                logger.info("Shutting down generator [%s].", candidate)

                stage_online = overall_online
                stage_cost   = overall_cost

        # Compute elapsed time.
        elapsed = self.elapsed = time.time() - t0

        logger.info("OPF with unit decommitment solved in %.3f." % elapsed)

        # 8. Return the current best solution as the final solution.
        return network


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
