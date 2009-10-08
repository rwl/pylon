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

""" Defines a profit maximisation task.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from scipy import array
from pybrain.rl.tasks import EpisodicTask, Task

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ProfitTask" class:
#------------------------------------------------------------------------------

class ProfitTask(Task):
    """ Defines the task of maximising profit.
    """

    def __init__(self, environment):
        """ Initialises the task.
        """
        Task.__init__(self, environment)

        # Limits for scaling of sensors.
        self.sensor_limits = None#[(0.000, sensor_max)]

        # Limits for scaling of actors.
#        mkt = environment.market
#        price_cap = mkt.price_cap
        self.actor_limits = None#[(asset.p_min, price_cap)]


    def performAction(self, action):
        """ A filtered mapping of the .performAction() method of the underlying
            environment.
        """
#        logger.debug("Profit task [%s] filtering action: %s" %
#                     (self.env.asset.name, action))
#        logger.debug("Profit task [%s] denormalised action: %s" %
#                     (self.env.asset.name, self.denormalize(action)))
        Task.performAction(self, action)


    def getObservation(self):
        """ A filtered mapping to the .getSample() method of the underlying
            environment.
        """
        sensors = Task.getObservation(self)
#        logger.debug("Profit task [%s] normalised sensors: %s" %
#                     (self.env.asset.name, sensors))
        return sensors


    def getReward(self):
        """ Computes and returns the reward corresponding to the last action
            performed.
        """
        g = self.env.asset
        mkt = self.env.market

        g_settlement = [d for d in mkt.settlement if d.generator == g]
        if g_settlement:
            dispatch = g_settlement[0]
        else:
            raise ValueError, "Dispatch not found."

        logger.debug("Profit task [%s] reward: %s" % (g.name, d.earnings))

        return array([d.earnings])

# EOF -------------------------------------------------------------------------
