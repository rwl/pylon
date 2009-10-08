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
#from pybrain.rl.environments import Environment
from pybrain.rl.environments.graphical import GraphicalEnvironment

#from pylon import Generator
from pylon.pyreto.smart_market import Offer, Bid

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
#    indim = 2

    # The number of sensor values the environment produces.
#    outdim = 1

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, asset, market, render=True):
        """ Initialises the environment.
        """
#        assert isinstance(asset, Generator)
#        assert isinstance(market, SmartMarket)

        super(ParticipantEnvironment, self).__init__()

        # Generator instance that the agent controls.
        self.asset = asset

        # Auction that clears offer and bids using OPF results.
        self.market = market

        # A nonnegative amount of money.
#        money = 100

        # Positive production capacity.
#        self.p_max = asset.p_max
#        self.p_min = asset.p_min
        # Total cost function proportional to current capacity.
#        self.cost_coeffs = asset.cost_coeffs
#        self.pwl_points  = asset.pwl_points
        # Amortised fixed costs.
#        self.c_startup = asset.c_startup
#        self.c_shutdown = asset.c_shutdown

#        if asset.is_load:
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

        # Set the number of action values that the environment accepts.
        self.indim = 2

        # Set the number of sensor values that the environment produces.
        case = market.case
        outdim = 0
        outdim += 1 # Total system cost.
        outdim += 1 # Previous bid quantity.
        outdim += len(case.branches)
        self.outdim = outdim

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        g = self.asset
        mkt = self.market
        case = mkt.case

        # Get sensor info from the previous settlement process.
        settlement = [d for d in mkt.settlement if d.generator == g]
        if settlement:
            dispatch = settlement[0]
            system_cost = dispatch.f
        else:
            system_cost = 0.0

        # Get sensor info from previous offers/bids.
        offerbids = [ob for ob in mkt.offers + mkt.bids if ob.generator == g]
        if offerbids:
            offbid = offerbids[0]
            previous_qty = offbid.quantity
        else:
            previous_qty = 0.0


        flows = [b.p_source for b in case.branches]

#        if self.hasRenderer():
#            data = (demand, None, None, None)
#            self.getRenderer().updateData(data, False)

        return array([system_cost, previous_qty] + flows)


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ qty, prc, qty, prc, ... ]
        """
        for i in len(action) / 2:
            asset = self.asset
            mkt = self.market

            qty = action[i * 2]
            prc = action[i * 2 + 1]

            if not asset.is_load:
                offer = Offer(asset, qty, prc)
                mkt.offers.append(offer)
            else:
                bid = Bid(asset, qty, prc)
                mkt.bids.append(bid)

        if self.hasRenderer():
            data = (None, action[0], None, None)
            self.getRenderer().updateData(data, False)


    def reset(self):
        """ Reinitialises the environment.
        """
        self.market.init()

# EOF -------------------------------------------------------------------------
