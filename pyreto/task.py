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
        t = self.env.market.period

        earnings = 0.0
        for g in self.env.generators:
            # Compute costs in $ (not $/hr).
    #        fixedCost = t * g.total_cost(0.0)
    #        variableCost = (t * g.total_cost()) - fixedCost
            costs = g.total_cost(round(g.p, 4),
                                 self.env.gencost[g]["pCost"],
                                 self.env.gencost[g]["pCostModel"])

    #        offbids = self.env.market.getOffbids(g)
            offbids = [ob for ob in self.env._lastAction if ob.generator == g]

            revenue = t * sum([ob.revenue for ob in offbids])

            if g.is_load:
                earnings += costs - revenue
            else:
                earnings += revenue - costs#(fixedCost + variableCost)

            logger.debug("Generator [%s] earnings: %.2f (%.2f, %.2f)" %
                         (g.name, earnings, revenue, costs))

        logger.debug("Task reward: %.2f" % earnings)

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

    def __init__(self, environment, maxSteps=24, discount=None):
        """ Initialises the task.
        """
        super(EpisodicProfitTask, self).__init__(environment)

        # Maximum number of time steps.
        self.maxSteps = maxSteps

        # Current time step.
        self.t = 0

        # Discount factor.
        self.discount = discount

        # Track cumulative reward.
        self.cumulativeReward = 0

        # Track the number of samples.
        self.samples = 0

        # Maximum markup/markdown.
        self.maxMarkup = 0.4

        #----------------------------------------------------------------------
        #  "Task" interface:
        #----------------------------------------------------------------------

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
        self.cumulativeReward = 0
        self.samples = 0
        self.t = 0

    #--------------------------------------------------------------------------
    #  "EpisodicTask" interface:
    #--------------------------------------------------------------------------

    def isFinished(self):
        """ Is the current episode over?
        """
        if self.t >= self.maxSteps:
            return True # maximal timesteps
        return False


    def addReward(self):
        """ A filtered mapping towards performAction of the underlying
            environment.
        """
        # by default, the cumulative reward is just the sum over the episode
        if self.discount:
            reward = self.getReward()
            self.cumulativeReward += power(self.discount, self.samples) *reward
        else:
            self.cumulativeReward += self.getReward()

    #--------------------------------------------------------------------------
    #  "EpisodicProfitTask" interface:
    #--------------------------------------------------------------------------

    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        case = self.env.market.case

        limits = []

        # Market sensor limits.
        limits.append((1e-6, BIGNUM)) # f
        pLimit = 0.0
        for g in self.env.generators:
            if g.is_load:
                pLimit += self.env.gencost[g]["pMin"]
            else:
                pLimit += self.env.gencost[g]["pMax"]
        limits.append((0.0, pLimit)) # quantity
#        cost = max([g.total_cost(pLimit,
#                                 self.env.gencost[g]["pCost"],
#                                 self.env.gencost[g]["pCostModel"]) \
#                                 for g in self.env.generators])
        cost = self.env.generators[0].total_cost(pLimit,
            self.env.gencost[g]["pCost"], self.env.gencost[g]["pCostModel"])
        limits.append((0.0, cost)) # mcp

        # Case sensor limits.
#        limits.extend([(-180.0, 180.0) for _ in case.buses]) # Va
        limits.extend([(0.0, BIGNUM) for _ in case.buses]) # P_lambda

        limits.extend([(-b.rate_a, b.rate_a) for b in case.branches]) # Pf
#        limits.extend([(-BIGNUM, BIGNUM) for b in case.branches])     # mu_f

        limits.extend([(g.p_min, g.p_max) for g in case.generators]) # Pg
#        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators])  # Pg_max
#        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators])  # Pg_min

        return limits


    def getActorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        numOffbids = self.env.numOffbids
        offbidQty = self.env.offbidQty

        actorLimits = []
        for _ in range(numOffbids):
            for g in self.env.generators:
                if offbidQty:
                    actorLimits.append((0.0, self.env.gencost[g]["pMax"]))
                actorLimits.append((0.0, self.maxMarkup))

        return actorLimits

# EOF -------------------------------------------------------------------------
