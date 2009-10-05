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
from pybrain.rl.environments.graphical import GraphicalEnvironment

from pylon import Generator
from pylon.pyreto.market import SmartMarket, Offer, Bid

#------------------------------------------------------------------------------
#  "ParticipantEnvironment" class:
#------------------------------------------------------------------------------

class ParticipantEnvironment(GraphicalEnvironment):
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
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, asset, market, render=True):
        """ Initialises the environment.
        """
        assert isinstance(asset, Generator)
        assert isinstance(market, SmartMarket)

        super(ParticipantEnvironment, self).__init__()

        # Energy network in which the asset operates.
#        self.power_system = power_system
        # Generator instance that the agent controls.
        self.asset = asset
        # Auction that clears offer and bids using OPF results.
        self.market = market
        # A nonnegative amount of money.
#        money = 100

        # Store on initialisation as they are set in perfromAction().
        # Positive production capacity.
#        self.p_max = asset.p_max
#        self.p_min = asset.p_min
        # Total cost function proportional to current capacity.
#        self.cost_coeffs = asset.cost_coeffs
#        self.pwl_points  = asset.pwl_points
        # Amortised fixed costs.
#        self.c_startup = asset.c_startup
#        self.c_shutdown = asset.c_shutdown
        # Total number of agents.
#        self.n_agents = n_agents

#        if asset.mode == "":
#            # Income received each periods.
#            self.endowment_profile = 10
#            # Needs and preferences for power consumption each period.
#            self.utility_function = [1.0]
#            # Savings from previous periods.
#            self.savings = 100
#            # Each participant is a shareholder who owns shares in generating
#            # companies and receives an according dividend each period.
#            self.shares = {}

        self.render = render
#        if self.render:
#            self.updateDone = True
#            self.updateLock=threading.Lock()

    def get_demand(self):
        """ Returns the total system demand including dispatchable loads.
        """
        n = self.market.case
        l  = sum( [load.p for load in case.online_loads] )
        vl = sum( [g.p for g in case.online_generators if g.is_load()] )

        return l + vl

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        g = self.asset
        mkt = self.market

        offerbids = [ob for ob in mkt.offers + mkt.bids if ob.generator == g]

        demand = self.get_demand()

        c_system = self.market.c_system

        if self.hasRenderer():
            data = (demand, None, None, None)
            self.getRenderer().updateData(data, False)

        return array([demand])


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ qty, prc, qty, prc, ... ]
        """
        for i in len(action) / 2:
            ob = OfferBid(self.asset, qty=action[i * 2], prc=action[i * 2 + 1])
            self.market.submit(ob)

        if self.hasRenderer():
            data = (None, action[0], None, None)
            self.getRenderer().updateData(data, False)


    def reset(self):
        """ Reinitialises the environment.
        """
        # Rest the asset parameters.
#        self.asset.p_max = self.p_max
#        self.asset.p_min = self.p_min
#        self.asset.cost_coeffs = self.cost_coeffs

        # Reset the load profile for each online load.
#        for load in self.power_system.online_loads:
#            load.reset_profile()

        self.market.init()

# EOF -------------------------------------------------------------------------
