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

""" Defines an n-armed bandit problem.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import scipy

from pybrain.rl.environments import Environment, Task
from pybrain.utilities import drawIndex  #@UnusedImport

from pyreto.roth_erev import eventGenerator

#------------------------------------------------------------------------------
#  "BanditEnvironment" class:
#------------------------------------------------------------------------------

class BanditEnvironment(Environment):
    """ Defines an n-armed bandit environment.
    """

    #: The number of action values the environment accepts.
    indim = 1

    #: The number of sensor values the environment produces.
    outdim = 0

    #: Payout from the last arm pull.
    lastPayout = 0.0

    def __init__(self, payouts, distrib):
        super(BanditEnvironment, self).__init__()

        #: Matrix of possible payouts from each arm.
        self.payouts = payouts

        #: Discrete probability distribution matrix each arm's payouts.
        self.distrib = distrib


    def getSensors(self):
        """ the currently visible state of the world (the observation may be
            stochastic - repeated calls returning different values)
        """
        return scipy.array([0])


    def performAction(self, action):
        """ perform an action on the world that changes it's internal state
            (maybe stochastically).

            All you have to do is pull one of the arm and receive a payout.
            Each arm has a distribution of different payouts that are delivered
            with different probabilities.
        """
        distrib = self.distrib[action[0], :]
        payoutIdx = eventGenerator(distrib)
#        payoutIdx = drawIndex(distrib)

        self.lastPayout = self.payouts[action[0], payoutIdx]

        print "Payout [Arm: %d]: %.1f" % (action[0] + 1, self.lastPayout)

#------------------------------------------------------------------------------
#  "BanditTask" class:
#------------------------------------------------------------------------------

class BanditTask(Task):
    """ Defines the task of maximising payouts.
    """

    def getReward(self):
        return self.env.lastPayout

# EOF -------------------------------------------------------------------------
