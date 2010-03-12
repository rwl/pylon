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

""" Defines a profit maximisation task.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from scipy import power

from pybrain.rl.environments import Task

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

BIGNUM = 1e04

#------------------------------------------------------------------------------
#  "ProfitTask" class:
#------------------------------------------------------------------------------

class ProfitTask(Task):
    """ Defines a task with discrete observations of the clearing price.
    """

    def getReward(self):
        """ Returns the reward corresponding to the last action performed.
        """
        g = self.env.asset
        t = self.env.market.period

#        offbids = self.env.market.get_offbids(g)
        offbids = self.env.last_action

        # Compute costs in $ (not $/hr).
#        g.p_cost = self.env.marginal_cost

#        fixed_cost = t * g.total_cost(0.0)
#        variable_cost = (t * g.total_cost()) - fixed_cost
        costs = g.total_cost(round(g.p, 2),
                             self.env._p_cost,
                             self.env._pcost_model)

        revenue = t * sum([ob.revenue for ob in offbids])

        if g.is_load:
            earnings = costs - revenue
        else:
            earnings = revenue - costs#(fixed_cost + variable_cost)

        logger.debug("Profit task [%s] reward: %.2f (%.2f, %.2f)" %
                     (g.name, earnings, revenue, costs))

        return earnings


    def performAction(self, action):
        """ The action vector is stripped and the only element is cast to
            integer and given to the super class.
        """
        super(ProfitTask, self).performAction(int(action[0]))

#------------------------------------------------------------------------------
#  "EpisodicProfitTask" class:
#------------------------------------------------------------------------------

class EpisodicProfitTask(ProfitTask):
    """ Defines a task for continuous sensor and action spaces.
    """

    def __init__(self, environment, maxsteps=24, discount=None):
        """ Initialises the task.
        """
        super(EpisodicProfitTask, self).__init__(environment)

        # Maximum number of time steps.
        self.maxsteps = maxsteps

        # Current time step.
        self.t = 0

        # Discount factor.
        self.discount = discount

        # Track cumulative reward.
        self.cumreward = 0

        # Track the number of samples.
        self.samples = 0

        # Maximum markup/markdown.
        self.mark_max = 0.4

        # Limits for scaling of sensors.
        self.sensor_limits = self.getSensorLimits()

        # Limits for scaling of actors.
        self.actor_limits = self.getActorLimits()

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

    def getObservation(self):
        """ A filtered mapping to getSample of the underlying environment. """
        sensors = super(EpisodicProfitTask, self).getObservation()
#        print "SENSORS:", sensors
        return sensors


    def performAction(self, action):
        """ Execute one action.
        """
        self.t += 1
        Task.performAction(self, action)
        self.addReward()
        self.samples += 1


    def reset(self):
#        super(EpisodicProfitTask, self).reset()
#        self.env.reset()
        self.cumreward = 0
        self.samples = 0
        self.t = 0

    #--------------------------------------------------------------------------
    #  "EpisodicTask" interface:
    #--------------------------------------------------------------------------

    def isFinished(self):
        """ Is the current episode over?
        """
        if self.t >= self.maxsteps:
            return True # maximal timesteps
        return False


    def addReward(self):
        """ A filtered mapping towards performAction of the underlying
            environment.
        """
        # by default, the cumulative reward is just the sum over the episode
        if self.discount:
            reward = self.getReward()
            self.cumreward += power(self.discount, self.samples) * reward
        else:
            self.cumreward += self.getReward()

    #--------------------------------------------------------------------------
    #  "EpisodicProfitTask" interface:
    #--------------------------------------------------------------------------

    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        g = self.env.asset
        case = self.env.market.case

        limits = []

        # Market sensor limits.
        limits.append((1e-6, BIGNUM)) # f
        p_lim = self.env._p_min if g.is_load else self.env._p_max
        limits.append((0.0, p_lim)) # quantity
        limits.append((0.0, g.total_cost(p_lim, self.env._p_cost,
                                         self.env._pcost_model)))

        # Case sensor limits.
#        limits.extend([(-180.0, 180.0) for _ in case.buses]) # Va
        limits.extend([(0.0, BIGNUM) for _ in case.buses]) # Plam

        limits.extend([(-b.rate_a, b.rate_a) for b in case.branches]) # Pf
#        limits.extend([(-BIGNUM, BIGNUM) for b in case.branches]) # mu_f

        limits.extend([(g.p_min, g.p_max) for g in case.generators]) # Pg
#        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators]) # Pg_max
#        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators]) # Pg_min

        return limits


    def getActorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        n_offbids = self.env.n_offbids
        offbid_qty = self.env.offbid_qty

        actor_limits = []
        for _ in range(n_offbids):
            if offbid_qty:
                actor_limits.append((0.0, self.env._p_max))
            actor_limits.append((0.0, self.mark_max))

        return actor_limits

# EOF -------------------------------------------------------------------------
