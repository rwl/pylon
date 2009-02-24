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
    """ Defines the world in which an agent acts.  It receives an input with
        .performAction() and returns an output with .getSensors(). The
        ParticipantEnviroment has no notion of the whole network and
        attributes used to represent the state of the power system must be
        set by the Experiment. Each environment requires an asset component
        (Generator), the parameters of which are changed with the
        .performAction() method.
    """

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    # The number of action values the environment accepts.
    indim = 1

    # The number of sensor values the environment produces.
    outdim = 3

    #--------------------------------------------------------------------------
    #  "ParticipantEnvironment" interface:
    #--------------------------------------------------------------------------

    # Generator instance that the agent controls.
    asset = None

    # Sum of demand for each Load for the current period.
    demand = 0.0

    # Market Clearing Price for the current period.
    mcp = 0.0

    # Forecast demand for the successive period.
    forecast = 0.0

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, asset):
        """ Initialises the environment.
        """
        assert isinstance( asset, Generator )
        self.asset    = asset
        self.demand   = 0.0
        self.mcp      = 0.0
        self.forecast = 0.0

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
            The state consists of 'total demand', 'market clearing price' and
            'forecast demand'.
        """
        return array( [ self.demand, self.mcp, self.forecast ] )


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ p_max_bid ]
        """
        if self.asset is not None:
            self.asset.p_max_bid = action[0]
        else:
            raise ValueError, "Environment [%s] has no asset." % self


    def reset(self):
        """ Reinitialises the environment.
        """
        self.demand   = 0.0
        self.mcp      = 0.0
        self.forecast = 0.0
        if self.asset is not None:
            self.asset.p_max_bid = self.asset.p_max

# EOF -------------------------------------------------------------------------
