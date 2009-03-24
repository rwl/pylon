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

from pylon.api import Network, Generator

#------------------------------------------------------------------------------
#  "ParticipantEnvironment" class:
#------------------------------------------------------------------------------

class ParticipantEnvironment(Environment):
    """ Defines the world in which an agent acts.  It receives an input with
        .performAction() and returns an output with .getSensors(). Each
        environment requires a reference to an asset (Generator) and the whole
        power system. The parameters of the asset are changed with the
        .performAction() method.
    """

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    # The number of action values the environment accepts.
    indim = 1

    # The number of sensor values the environment produces.
    outdim = 1

    #--------------------------------------------------------------------------
    #  "ParticipantEnvironment" interface:
    #--------------------------------------------------------------------------

    # Energy network in which the asset operates.
    power_system = None

    # Generator instance that the agent controls.
    asset = None

    @property
    def demand(self):
        """ Total system demand.
        """
        base = self.power_system.base_mva
        return sum([l.p for l in self.power_system.online_loads])

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, power_system, asset):
        """ Initialises the environment.
        """
        assert isinstance( power_system, Network )
        assert isinstance( asset, Generator )

        self.power_system = power_system
        self.asset = asset

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
            The state consists of 'total demand', 'market clearing price' and
            'forecast demand'.
        """
        return array( [self.demand] )


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ p_max_bid, proportional_cost ]
        """
        if self.asset is not None:
            base_mva = self.power_system.base_mva
            self.asset.p_max_bid = action[0]# / base_mva
#            self.asset.cost_coeffs = (0.0, action[1], 0.0)
        else:
            raise ValueError, "Environment [%s] has no asset." % self


    def reset(self):
        """ Reinitialises the environment.
        """
        if self.asset is not None:
            self.asset.p_max_bid = self.asset.p_max
        else:
            raise ValueError, "Environment [%s] has no asset." % self

        # Reset the load profile for each online load.
        for load in self.power_system.online_loads:
            load.reset_profile()

# EOF -------------------------------------------------------------------------
