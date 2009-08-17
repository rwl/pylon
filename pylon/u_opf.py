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

""" Defines a routine for solving the combined unit decommitment and optimal
    power flow problem.

    References:
        Ray Zimmerman, "uopf.m", MATPOWER, PSERC Cornell, version 3.2,
        http://www.pserc.cornell.edu/matpower/, March, 2006
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging
import random

from cvxopt import matrix

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "UOPFRoutine" class:
#------------------------------------------------------------------------------

class UOPFRoutine(object):
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
        """ Initialises a new UOPFRoutine instance.
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

        # Check for sum(Pmin) > total load, decommit as necessary.
        on = [g for g in generators if g.mode == "generator"]
        onld = [g for g in generators if g.mode == "despatchable load"]
        load_capacity = sum([l.p for l in loads])
        p_min_tot = sum([g.p_min for g in generators])

        while p_min_tot > load_capacity:
            # Shut down most expensive unit.
            avg_cost = [g.total_cost(g.p_min) / g.p_min for g in generators]
            # Pick one with max avg cost at Pmin.
#            g_idx = avg_cost.index(max(avg_cost))
            g_idx, value = fair_max(avg_cost)
            generator = generators[g_idx]

            logger.info("Shutting down generator [%s].", generator)

            # Set generation to zero.
            generator.p = 0.0
            generator.q = 0.0
            generator.online = False

            # Update minimum gen capacity.
            p_min_tot = sum([g.p_min for g in generators])

        # Run initial opf.
        if self.dc:
            routine = DCOPFRoutine()
        else:
            routine = ACOPFRoutine()

        solution = routine(network)

        # Best case so far.

        # Best case for this stage (ie. with n gens shut down, n=0,1,2 ...).

        while True:
            # Get candidates for shutdown.
            candidates = [g for g in gen0 if g.p_min > 0.0]

            if not candidates:
                break

            # Do not check for further decommitment unless we see something
            # better during this stage.
            done = True

            for candidate in candidates:
                # Start with best for this stage.
                gen = gen0

                candidate.p = 0.0
                candidate.q = 0.0
                candidate.online = False

                # Run opf.
                solution = routine(network)

                # Something better?
                if (solution['optimal'] == True) and (f < f1):

                    # Make sure we check for further decommitment.
                    done = False

            if done:
                # Decommits at this stage did not help.
                break
            else:
                # Shutting something else down helps, so let's keep going.
                logger.info("Shutting down generator [%s].", candidate)

        # Compute elapsed time.
        self.elapsed = t0 - time.time()

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
