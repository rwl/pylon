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

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

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

        totalEarnings = 0.0
        for g in self.env.generators:
            # Compute costs in $ (not $/hr).
    #        fixedCost = t * g.total_cost(0.0)
    #        variableCost = (t * g.total_cost()) - fixedCost

            costs = g.total_cost(round(g.p, 4),
                                 self.env._g0[g]["p_cost"],
                                 self.env._g0[g]["pcost_model"])

    #        offbids = self.env.market.getOffbids(g)
            offbids = [ob for ob in self.env._lastAction if ob.generator == g]

#            print self.env._lastAction
#            print g.name
#            for ob in offbids:
#                print ob.cleared
#                print ob.accepted
#                print ob.withheld
#                print ob.clearedQuantity
#                print ob.clearedPrice

            revenue = t * sum([ob.revenue for ob in offbids])
            if offbids:
                revenue += offbids[0].noLoadCost

            if g.is_load:
                earnings = costs - revenue
            else:
                earnings = revenue - costs#(fixedCost + variableCost)

            logger.debug("Generator [%s] earnings: %.2f (%.2f, %.2f)" %
                         (g.name, earnings, revenue, costs))

            totalEarnings += earnings

        logger.debug("Task reward: %.2f" % totalEarnings)

        return earnings


    def performAction(self, action):
        """ The action vector is stripped and the only element is cast to
            integer and given to the super class.
        """
        super(ProfitTask, self).performAction(int(action[0]))

# EOF -------------------------------------------------------------------------
