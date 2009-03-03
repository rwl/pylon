#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Defines an implementation of the unit commitment problem. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from cvxopt.base import matrix
from cvxopt.modeling import variable, op, dot, sum

from pylon.api import Network

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#  "UnitCommitmentRoutine" class:
#------------------------------------------------------------------------------

class UnitCommitmentRoutine:
    """ Defines an implementation of the unit commitment problem. """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The network passed to the routine
    network = Network

    # Selects one of three available LP solvers: the default solver written in
    # Python, the GLPK solver or the MOSEK LP solver.
    solver = None # "glpk" "mosek"

    # Time horizon
    n_periods = 1

    # Total demand vector
    demand = [0.0]

    # Total reserve for each period
    reserve = matrix

    # Maximum generation output limits.
    p_max = matrix

    # Minimum generation output limits.
    p_min = matrix

    # fixed generator costs.
    cost = matrix

    # Minimum up time limits.
    min_up = matrix

    # Minimum down time limits.
    min_down = matrix

    # Ramp up rate limits.
    rate_up = matrix

    # Ramp down limits.
    rate_down = matrix

    # Vector of the Market Clearing Prices for each period:
#    mcps = Array

    # A Result instance changes to which GenCos listen for:
#    result = None

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network):
        """ Returns a UnitCommitmentRoutine instance. """

        self.network = network

    #--------------------------------------------------------------------------
    #  Solve unit commitment:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves the unit commitment problem for the current network. """

        # Sanity checks -------------------------------------------------------

        # Time horizon sanity check
        p = self.n_periods
        if p < 1:
            logger.warn("Invalid time horizon [%d] using '1'." % p)
            self.n_periods = p = 1

        # Demand vector sanity check
        d = self.demand
        w, h = d.size
        if w != p:
            logger.warn("Demand vector length does not match time horizon.")
            if w > p:
                self.demand = d = self.demand[:p]
                logger.info("Slicing demand vector [%s]." % d)
            elif w < p:
                self.demand = d = self.demand.extend([0.0]*(p-w))
                logger.info("Extending demand vector [%s]." % d)

        # Reserve vector sanity check
#        r = self.reserve
#        w, h = r.size
#        if w != r:
#            logger.warn("Reserve vector length does not match time horizon.")
#            if w > r:
#                self.reserve = r = self.reserve[:p]
#                logger.info("Slicing reserve vector [%s]." % r)
#            elif w < p:
#                self.reserve = r = self.reserve.extend([0.0]*(p-w))
#                logger.info("Extending reserve vector [%s]." % r)

        # Generation ----------------------------------------------------------

        generators = self.network.online_generators

        # Generation output limits
        self.p_min = matrix( [ g.p_min_bid for g in generators ] )
        self.p_max = matrix( [ g.p_max_bid for g in generators ] )

        # fixed generation costs.
        self.cost = matrix( [ g.p_cost for g in generators ] )

        # Minimum up/down times
        self.min_up = matrix( [ g.min_up for g in generators ] )
        self.min_down = matrix( [ g.min_down for g in generators ] )

        # Ramp up/down rates
        self.rate_up = matrix( [ g.rate_up for g in generators ] )
        self.rate_down = matrix( [ g.rate_down for g in generators ] )

        # Solve LP ------------------------------------------------------------

        lp, p_gen = self.solve_lp()
#        logger.info("Solution status: %s", lp.status)

        # Process results -----------------------------------------------------

#        self._process_results(lp, alloc_vols)

    #--------------------------------------------------------------------------
    #  Solve Linear Programming problem:
    #--------------------------------------------------------------------------

    def solve_lp(self):
        """ Solves the linearised unit commitment problem.  Partitions problem
            creation from problem instantiation and solution.
        """

        n = self.network
        n_gen = len( n.online_generators )
        n_periods = self.n_periods

        # Problem variables declaration
#        period = variable()

#        unit_number = variable( n_gen )
#        commitment = matrix( 0.0, ( n_gen, n_periods ) )

#        demand = variable( n_periods, name = "Demand" )

        # Output of each generator at time t.
        p_gen = variable( size = n_gen, name = "Pg" )

#        p_min = variable( n_gen, "Pmin" )
#        p_max = variable( n_gen, "Pmax" )
#        min_up = variable(n_gen, "MinUp")
#        min_down = variable(n_gen, "MinDown")

#        c = self.cost[ :, period ]

        # Problem constraints
        gt_min = ( p_gen >= self.p_min ) # Lower output limits.
        print gt_min
        lt_max = ( p_gen <= self.p_max ) # Upper output limits.
        # Supply must balance with demand for each period.
#        balance = ( sum( p ) == demand[ period ] )


        # Specify variable values.
#        unit_number.value = range( n_gen )
#        p_min.value  = self.p_min
#        p_max.value  = self.p_max
#        demand.value = self.demand

        # Objective function.
#        objective = dot( c, p )

        lp = None#op( objective, [ lt_max, gt_min, balance ] )

#        logger.debug( "Solving the Unit Commitment problem [%s]." % n.name )
#        lp.solve( format = "dense", solver = self.solver )

        return lp, p_gen

    #--------------------------------------------------------------------------
    #  Process LP solution:
    #--------------------------------------------------------------------------

    def _process_results(self, lp, alloc_vols):
        """ Post valid results from the solution of the LP such that listening
            participants may learn.
        """

#        # Report a waring if non-optimal solution os found, but continue
#        if not lp.status == "optimal":
#            print "Period %d has solution status: %s", self.market.time,
#            lp.status
#
#            # Post non-optimal Result for all GenCos
#            for gco in self.market.gencos:
#                self.result = Result(solution_status="suboptimal",
#                                     genco=gco,
#                                     demand=self.demand[self.market.time],
#                                     volume=0.0,
#                                     mcp=0.0)
#
#            self.status = "Closed"
#
#        elif lp.status == "optimal":
#            print "Objective value: %f", float(str(lp.objective.value()))
#
#            # TODO: fix type coercion
#            mcp = float(str(lp.objective.value() / self.demand[self.time]))
#            print "Market clearing price: %f", mcp
#
#            for gco in self.market.gencos:
#                """store results for historical refernce"""
#                self.alloc_vol[:, self.market.time] = \
#                [float(str(g.value)) for g in p]
#
#                self.mcps[self.market.time] = mcp
#
#                gco_idx = self.market.gencos.index(gco)
#
#                self.result = Result(solution_status="optimal",
#                                     genco=gco,
#                                     demand=self.demand[self.market.time],
#                                     volume=float(str(p[gco_idx].value())),
#                                     mcp=mcp)
#
#            self.status = "Closed"

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.api import Bus, Generator

    network = Network(name="net1")
    bus1 = Bus(name="bus1")
    network.buses.append(bus1)

    gen1 = Generator(p_min=0.1, p_max=0.8, cost_coefs=(1.0, 0.0, 0.0))
    gen2 = Generator(p_min=0.2, p_max=0.6, cost_coefs=(2.0, 0.0, 0.0))
    bus1.generators.append(gen1)
    bus1.generators.append(gen2)

    routine = UnitCommitmentRoutine( network )
    routine.n_periods = 2
    routine.demand = matrix([1.0, 0.8])
    routine.solve()

# EOF -------------------------------------------------------------------------
