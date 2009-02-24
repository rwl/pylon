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

from scipy import array
from pybrain.rl.tasks import EpisodicTask, Task

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

        self.sensor_limits = [None] * 3
        asset = environment.asset
        self.actor_limits = [(asset.p_min, asset.p_max)]


    def performAction(self, action):
        """ A filtered mapping the .performAction() method of the underlying
            environment.
        """
        print "ACTION:", action
#        self.env.performAction(action)
        Task.performAction(self, action)


    def getObservation(self):
        """ A filtered mapping to the .getSample() method of the underlying
            environment.
        """
        print "OBSERVATION:", self.env.getSensors()
#        return self.env.getSensors()
        return Task.getObservation(self)


    def getReward(self):
        """ Computes and returns the reward corresponding to the last action
            performed.
        """
        asset  = self.env.asset
#        profit = asset.p_despatch * asset.p_cost
        profit = asset.p_despatch

        print "REWARD:", profit
        return array( [ profit ] )

# EOF -------------------------------------------------------------------------
