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

""" Defines an environment in which multiple agents compete.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pybrain.rl.environments.twoplayergames.twoplayergame \
    import CompetitiveEnvironment

from pylon.api import Network

#------------------------------------------------------------------------------
#  "MarketEnvironment" class:
#------------------------------------------------------------------------------

class MarketEnvironment(CompetitiveEnvironment):
    """ Defines an environment in which multiple agents compete.
    """

    # Power system on which the agents compete.
    network = None

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network):
        """ Initialises the market environment.
        """
        super(MarketEnvironment, self).__init__()
        assert isinstance(network, Network)
        self.network = network

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """

    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: tuple: (agentID, action value)
        """

    def reset(self):
        """ Reinitialises the environment.
        """
        pass

# EOF -------------------------------------------------------------------------
