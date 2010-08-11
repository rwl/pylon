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

from pybrain.rl.environments import Task

from pyreto.discrete.task import ProfitTask as DiscreteProfitTask

from pylon import PQ

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ProfitTask" class:
#------------------------------------------------------------------------------

class ProfitTask(DiscreteProfitTask):
    """ Defines a task for continuous sensor and action spaces.
    """

    def __init__(self, environment, maxSteps=24, discount=None,
                 maxMarkup=30.0, fmax=2000.0):
        super(ProfitTask, self).__init__(environment, maxSteps, discount,
                                         maxMarkup)

        #: Maximum total system cost.
        self.fmax = fmax

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
        self.sensor_limits = self._getSensorLimits()

        #: Limits for scaling of actors.
        self.actor_limits = self._getActorLimits()

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

#    def getObservation(self):
#        """ A filtered mapping to getSample of the underlying environment. """
#        sensors = super(ProfitTask, self).getObservation()
#        print "NORMALISED SENSORS:", sensors
#        return sensors


    def performAction(self, action):
        """ Execute one action.
        """
#        print "ACTION:", action
        self.t += 1
        Task.performAction(self, action)
#        self.addReward()
        self.samples += 1

    #--------------------------------------------------------------------------
    #  "ProfitTask" interface:
    #--------------------------------------------------------------------------

    def _getSensorLimits(self):
        """ Returns a list of 2-tuples, e.g. [(-3.14, 3.14), (-0.001, 0.001)],
            one tuple per parameter, giving min and max for that parameter.
        """
        limits = []
        limits.extend(self._getTotalDemandLimits())
#        limits.extend(self._getDemandLimits())
#        limits.extend(self._getPriceLimits())
#        limits.extend(self._getVoltageMagnitudeLimits())
#        limits.extend(self._getVoltageAngleLimits())
        limits.extend(self._getVoltageLambdaLimits())
#        limits.extend(self._getFlowLimits())

        logger.debug("Sensor limits: %s" % limits)
        return limits

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


    def _getTotalDemandLimits(self):
        Pdmax = sum([b.p_demand for b in self.env.market.case.buses])
        return [(0.0, Pdmax)]


    def _getDemandLimits(self):
        limits = [(0.0, b.p_demand) for b in self.env.market.case.buses
                  if b.type == PQ]
        return limits


    def _getPriceLimits(self):
        mcpLimit = (0.0, self.env.market.priceCap)
        sysLimit = (0.0, self.fmax)
        return [mcpLimit, sysLimit]


    def _getVoltageMagnitudeLimits(self):
        limits = []
        Vmax = [b.v_max for b in self.env.market.case.connected_buses]
        Vmin = [b.v_min for b in self.env.market.case.connected_buses]
        limits.extend(zip(Vmax, Vmin))
#        nb = len(self.env.market.case.connected_buses)
#        limits.extend([(-180.0, 180.0)] * nb)
        return limits


    def _getVoltageAngleLimits(self):
        limits = []
        nb = len(self.env.market.case.connected_buses)
        limits.extend([(-180.0, 180.0)] * nb)
        return limits


    def _getVoltageLambdaLimits(self):
        nb = len(self.env.market.case.connected_buses)
        return [None] * nb


    def _getFlowLimits(self):
        rateA = [l.rate_a for l in self.env.market.case.online_branches]
        neg_rateA = [-1.0 * r for r in rateA]
        limits = zip(neg_rateA, rateA)
#        limits.extend(zip(neg_rateA, rateA))
        return limits


    def _getActorLimits(self):
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
