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

""" Defines a profit maximisation task.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from scipy import array, linspace
from pybrain.rl.environments import Task

logger = logging.getLogger(__name__)

BIGNUM = 1e06

#------------------------------------------------------------------------------
#  "BaseProfitTask" class:
#------------------------------------------------------------------------------

class BaseProfitTask(Task):
    """ Defines a base task where reward is profit (revenue - cost).
    """

#    def __init__(self, environment, num_actions=10):
#        """ The action space is divided into the given number of steps.
#        """
#        super(ProfitTask, self).__init__(environment)
#
#        # The number of steps that the action value should be divided into.
##        self.action_steps = num_actions
#        self.action_space = self.getDiscreteActions(num_actions)

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

#    def getObservation(self):
#        """ The vector of sensor values is replaced by a single integer since
#            there is only one state.
#        """
#        return 0
#
#
#    def performAction(self, action):
#        """ The action vector is stripped and the only element is cast to
#            integer and given to the super class.
#        """
##        Task.performAction(self, int(action[0]))
#        idx = int(action[0])
#        Task.performAction(self, array([self.action_space[idx]]))


    def getReward(self):
        """ Returns the reward corresponding to the last action performed.
        """
        g = self.env.asset
        if not g.is_load:
            offbids = [x for x in self.env.market.offers if x.generator == g]
        else:
            offbids = [x for x in self.env.market.bids if x.vload == g]
        t = self.env.market.period

        # Compute costs in $ (not $/hr).  Apply the marginal cost function for
        # calculating fixed and variable marginal costs.
        g.p_cost = self.env.marginal_cost
        fixed_cost = t * g.total_cost(0.0)
        variable_cost = (t * g.total_cost()) - fixed_cost

        revenue = t * sum([ob.revenue for ob in offbids])
        earnings = revenue - (fixed_cost + variable_cost)

        logger.debug("Profit task [%s] reward: %s" % (g.name, earnings))
        return earnings

#------------------------------------------------------------------------------
#  "DiscreteTask" class:
#------------------------------------------------------------------------------

class DiscreteTask(BaseProfitTask):
    """ Defines a task with discrete observations of the clearing price.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, environment, dim_state=100, num_actions=10):
        """ The sensor space is divided into the given number of steps.
        """
        super(DiscreteTask, self).__init__(environment, num_actions)

        # State dimensions.
        self.dim_state = dim_state

        # The number of steps that the action value should be divided into.
#        self.action_steps = num_actions
        self.action_space = self.getDiscreteActions(num_actions)

    #--------------------------------------------------------------------------
    #  "DiscreteTask" interface:
    #--------------------------------------------------------------------------

    def getDiscreteActions(self, num_actions):
        """ Returns an array of action values.
        """
        limit = self.env.market.price_cap
        return linspace(0.0, limit, num_actions)

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

    def getObservation(self):
        """ The agent receives a single non-negative integer indicating the
            band of market clearing prices in which the price from the last
            auction exists.
        """
        sensors = Task.getObservation(self)
        # Divide the range of market prices in to discrete bands.
        limit = self.env.market.price_cap
        states = linspace(0.0, limit, self.dim_state)
        mcp = abs(sensors[2]) # Discard all other sensor data.
        for i in range(len(states) - 1):
            if (states[i] <= round(mcp, 4) <= states[i + 1]):
                return array([i])
        else:
            raise ValueError, "MCP: %f" % mcp

#------------------------------------------------------------------------------
#  "ContinuousTask" class:
#------------------------------------------------------------------------------

class ContinuousTask(BaseProfitTask):
    """ Defines a task for continuous sensor and action spaces.
    """

    def __init__(self, environment):
        """ Initialises the task.
        """
        super(ContinuousTask, self).__init__(environment)

        # Limits for scaling of sensors.
        self.sensor_limits = self.getSensorLimits()

        # Limits for scaling of actors.
        self.actor_limits = self.getActorLimits()

    #--------------------------------------------------------------------------
    #  "ContinuousTask" interface:
    #--------------------------------------------------------------------------

    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        g = self.env.asset
        mkt = self.env.market
        case = mkt.case

        limits = []
        limits.append((0.0, BIGNUM)) # f
        limits.append((0.0, g.rated_pmax)) # quantity
        limits.append((0.0, BIGNUM)) # price
        limits.append((0.0, g.total_cost(g.rated_pmax))) # variable
#        c_startup = 2.0 if g.c_startup == 0.0 else g.c_startup
#        limits.append((0.0, c_startup)) # startup
#        c_shutdown = 2.0 if g.c_shutdown == 0.0 else g.c_shutdown
#        limits.append((0.0, c_shutdown)) # shutdown

        limits.extend([(0.0, b.rate_a) for b in case.branches])
        limits.extend([(-BIGNUM, BIGNUM) for b in case.branches]) # mu_flow

        limits.extend([(-180.0, 180.0) for b in case.buses]) # angle
        limits.extend([(0.0, BIGNUM) for b in case.buses]) # p_lambda
#        limits.extend([(b.v_min, b.v_max) for b in case.buses]) # mu_vmin
#        limits.extend([(b.v_min, b.v_max) for b in case.buses]) # mu_vmax

        limits.extend([(0., b.rated_pmax) for b in case.generators]) #pg
        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators]) #g_pmax
        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators]) #g_pmin

        return limits


    def getActorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        g = self.env.asset
        n_offbids = self.env.n_offbids
        offbid_qty = self.env.offbid_qty
        mkt = self.env.market

        actor_limits = []
        for _ in range(n_offbids):
            if offbid_qty:
                actor_limits.append((0.0, g.rated_pmax))
            actor_limits.append((0.0, mkt.price_cap))

        return actor_limits

# EOF -------------------------------------------------------------------------
