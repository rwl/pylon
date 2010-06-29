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

from pyreto.discrete.task import ProfitTask as DiscreteProfitTask

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

class ProfitTask(DiscreteProfitTask):
    """ Defines a task for continuous sensor and action spaces.
    """

    def __init__(self, environment, maxSteps=24, discount=None,
                 maxMarkup=30.0):
        super(ProfitTask, self).__init__(environment, maxSteps, discount,
                                         maxMarkup)

#        #: Maximum number of time steps.
#        self.maxSteps = maxSteps
#
#        #: Current time step.
#        self.t = 0
#
#        #----------------------------------------------------------------------
#        #  "EpisodicTask" interface:
#        #----------------------------------------------------------------------
#
#        #: Discount factor.
#        self.discount = discount
#
#        #: Track cumulative reward.
#        self.cumulativeReward = 0
#
#        #: Track the number of samples.
#        self.samples = 0
#
#        #: Maximum markup/markdown.
#        self.maxMarkup = maxMarkup

        #----------------------------------------------------------------------
        #  "Task" interface:
        #----------------------------------------------------------------------

        #: Limits for scaling of sensors.
        self.sensor_limits = self.getSensorLimits()

        #: Limits for scaling of actors.
        self.actor_limits = self.getActorLimits()

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

#    def getObservation(self):
#        """ A filtered mapping to getSample of the underlying environment. """
#        sensors = super(ProfitTask, self).getObservation()
##        print "NORMALISED SENSORS:", sensors
#        return sensors


    def performAction(self, action):
        """ Execute one action.
        """
        print "ACTION:", action
        self.t += 1
        Task.performAction(self, action)
#        self.addReward()
        self.samples += 1

    #--------------------------------------------------------------------------
    #  "ProfitTask" interface:
    #--------------------------------------------------------------------------

    def getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        case = self.env.market.case

#        limits = []
#
#        # Market sensor limits.
#        limits.append((1e-6, BIGNUM)) # f
#        pLimit = 0.0
#        for g in self.env.generators:
#            if g.is_load:
#                pLimit += self.env._g0[g]["p_min"]
#            else:
#                pLimit += self.env._g0[g]["p_max"]
#        limits.append((0.0, pLimit)) # quantity
##        cost = max([g.total_cost(pLimit,
##                                 self.env._g0[g]["p_cost"],
##                                 self.env._g0[g]["pcost_model"]) \
##                                 for g in self.env.generators])
#        cost = self.env.generators[0].total_cost(pLimit,
#            self.env._g0[g]["p_cost"], self.env._g0[g]["pcost_model"])
#        limits.append((0.0, cost)) # mcp
#
#        # Case sensor limits.
##        limits.extend([(-180.0, 180.0) for _ in case.buses]) # Va
#        limits.extend([(0.0, BIGNUM) for _ in case.buses]) # P_lambda
#
#        limits.extend([(-b.rate_a, b.rate_a) for b in case.branches]) # Pf
##        limits.extend([(-BIGNUM, BIGNUM) for b in case.branches])     # mu_f
#
#        limits.extend([(g.p_min, g.p_max) for g in case.generators]) # Pg
##        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators])  # Pg_max
##        limits.extend([(-BIGNUM, BIGNUM) for g in case.generators])  # Pg_min

        Pdmax = sum([b.p_demand for b in case.buses])

        sensorLimits = [(0.0, Pdmax)]

        logger.debug("Sensor limits: %s" % sensorLimits)

        return sensorLimits


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
                    actorLimits.append((0.0, self.env._g0[g]["p_max"]))
                actorLimits.append((0.0, self.maxMarkup))

        logger.debug("Actor limits: %s" % actorLimits)

        return actorLimits

# EOF -------------------------------------------------------------------------
