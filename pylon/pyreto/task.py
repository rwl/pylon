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
        power_sys = environment.power_system
        base_mva = power_sys.base_mva
        sensor_max = [l.p_max for l in power_sys.online_loads]
        self.sensor_limits = None#[(0.000, sensor_max)]

        # Limits for scaling of actors.
        asset = environment.asset
        self.actor_limits = None#[(asset.p_min, asset.p_max)]


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
        logger.debug("Profit task [%s] normalised sensors: %s" %
                     (self.env.asset.name, sensors))
        return sensors


    def getReward(self):
        """ Computes and returns the reward corresponding to the last action
            performed.
        """
        g = self.env.asset
        t = self.env.market.period
        g_online = self.env.market.g_online

        offerbids = [ob for ob in mkt.offers + mkt.bids if ob.generator == g]

        pay = sum( [ob.cleared_quantity * ob.cleared_price * t \
                    for ob in offerbids] )

        # Costs for the period (not per hour).
        c_fixed = g.total_cost(0.0) * t
        c_variable = (g.total_cost(ob.cleared_quantity) - c_fixed) * t
        # Startup and shutdown costs.
        g_idx = self.env.market.case.all_generators.index(g)
        if not bool(g_online[g_idx]) and g.online:
            # The generator has been started up.
            c_updown = g.c_startup
        elif bool(g_online[g_idx]) and not g.online:
            # The generator has been turned off.
            c_updown = g.c_shutdown
        else:
            c_updown = 0.0

        cost = c_fixed + c_variable + c_updown

        earnings = pay - cost

        logger.debug("Profit task [%s] reward: %s" % (g.name, earnings))

        return array([earnings])

# EOF -------------------------------------------------------------------------
