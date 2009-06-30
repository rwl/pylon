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

    #--------------------------------------------------------------------------
    #  "Task" interface:
    #--------------------------------------------------------------------------

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
        self.actor_limits = [(asset.p_min, asset.p_max)]


    def performAction(self, action):
        """ A filtered mapping of the .performAction() method of the underlying
            environment.
        """
        logger.debug("Profit task [%s] filtering action: %s" %
                     (self.env.asset.name, action))
        logger.debug("Profit task [%s] denormalised action: %s" %
                     (self.env.asset.name, self.denormalize(action)))
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
        base_mva = self.env.power_system.base_mva
        asset  = self.env.asset
        # Define the market clearing price as the maximum of the Lagrangian
        # multipliers (lambda, $/MWh) for all buses.
        mcp = max( [bus.p_lambda for bus in self.env.power_system.buses] )
#        profit = asset.p_despatch * asset.p_cost
        profit = (asset.p_despatch * base_mva) * mcp

        logger.debug("Profit task [%s] reward: %s" % (asset.name, profit))
        return array( [ profit ] )

# EOF -------------------------------------------------------------------------
