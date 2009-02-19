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

""" Defines an environment for market participants.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from scipy import array
from pybrain.rl.environments import Environment

from pylon.api import Generator

#------------------------------------------------------------------------------
#  "ParticipantEnvironment" class:
#------------------------------------------------------------------------------

class ParticipantEnvironment(Environment):
    """ Defines an environment for market participant agents.
    """

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    # The number of action values the environment accepts.
    indim = 3

    # The number of sensor values the environment produces.
    outdim = 1

    #--------------------------------------------------------------------------
    #  "ParticipantEnvironment" interface:
    #--------------------------------------------------------------------------

    # Generator instance that the agent controls.
    asset = None

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, asset):
        """ Initialises the environment.
        """
#        super(ParticipantEnvironment, self).__init__()
        assert isinstance( asset, Generator )
        self.asset = asset

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        asset = self.asset
        if asset is not None:
            # Define actions (inputs to the network).
            min = asset.p_min_bid
            max = asset.p_max_bid
            half = min + ((max - min) / 2)

            return array( [ min, half, max ] )
        else:
            return []


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: tuple: (agentID, action value)
        """
        if self.asset is not None:
            self.asset.p_max_bid = action[0]
        else:
            raise ValueError, "Environment [%s] has no asset." % self


    def reset(self):
        """ Reinitialises the environment.
        """
        if self.asset is not None:
            self.asset.p_max_bid = self.asset.p_max

# EOF -------------------------------------------------------------------------
