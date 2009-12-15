#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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

import logging
from scipy import array, zeros, r_, hstack

#from pybrain.rl.environments import Environment
from pybrain.rl.environments.graphical import GraphicalEnvironment

#from pylon import Generator
from pylon.pyreto.smart_market import Offer, Bid

logger = logging.getLogger(__name__)

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

    def __init__(self, asset, market, n_offbids=1, offbid_qty=False,
                 render=True):
        """ Initialises the environment.
        """
#        assert isinstance(asset, Generator)
#        assert isinstance(market, SmartMarket)

        super(ParticipantEnvironment, self).__init__()

        # Generator instance that the agent controls.
        self.asset = asset

        # Auction that clears offer and bids using OPF results.
        self.market = market

        # Number of offers/bids a participant submits.
        self.n_offbids = n_offbids

        # Does a participant's offer/bid comprise quantity aswell as price.
        self.offbid_qty = offbid_qty

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
        if offbid_qty:
            self.indim = n_offbids * 2
        else:
            self.indim = n_offbids

        # Set the number of sensor values that the environment produces.
        case = market.case
        outdim = 0
        outdim += 6 # Dispatch sensors.
        outdim += len(case.branches) * 2 # Branch sensors.
        outdim += len(case.buses) * 2 # Bus sensors.
        outdim += len(case.all_generators) * 3 # Generator sensors.
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

        # Dispatch related sensors.
        dispatch_sensors = zeros(6)
        if mkt.settlement.has_key(g):
            dispatch = mkt.settlement[g]
            dispatch_sensors[0] = dispatch.f
            dispatch_sensors[1] = dispatch.quantity
            dispatch_sensors[2] = dispatch.price
            dispatch_sensors[3] = dispatch.variable
            dispatch_sensors[4] = dispatch.startup
            dispatch_sensors[5] = dispatch.shutdown

        # Case related sensors.
        flows = array([branch.p_source for branch in case.branches])
        mu_flow = array([branch.mu_s_source for branch in case.branches])
        voltages = array([bus.v_magnitude for bus in case.buses])
        angles = array([bus.v_angle for bus in case.buses])
        nodal_prc = array([bus.p_lambda for bus in case.buses])
        v_max = array([bus.mu_vmax for bus in case.buses])
        v_min = array([bus.mu_vmin for bus in case.buses])
        pg = array([g.p for g in case.all_generators])
        g_max = array([g.mu_pmax for g in case.all_generators])
        g_min = array([g.mu_pmin for g in case.all_generators])

        case_sensors = r_[flows, mu_flow, angles, nodal_prc, pg, g_max, g_min]

#        if self.hasRenderer():
#            renderer = self.getRenderer()

        return r_[dispatch_sensors, case_sensors]


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ qty, prc, qty, prc, ... ]
        """
        asset = self.asset
        mkt = self.market
        n_offbids = self.n_offbids

        # Participants either submit prices, where the quantity is divided
        # equally among the offers/bids, or tuples of quantity and price.
        if not self.offbid_qty:
            # Divide the rated capacity equally among the offers/bids.
            qty = asset.rated_pmax / n_offbids
            for prc in action:
                if not asset.is_load:
                    mkt.offers.append(Offer(asset, qty, prc))
                    logger.info("%.2fMW offered at %.2f$/MWh for %s." %
                                (qty, prc, asset.name))
                else:
                    mkt.bids.append(Bid(asset, qty, prc))
                    logger.info("%.2f$/MWh bid for %.2fMW to supply %s." %
                                (prc, qty, asset.name))
        else:
            # Agent's actions comprise both quantities and prices.
            for i in range(0, len(action), 2):
                qty = action[i]
                prc = action[i + 1]
                if not asset.is_load:
                    mkt.offers.append(Offer(asset, qty, prc))
                    logger.info("%.2fMW offered at %.2f$/MWh for %s." %
                                (qty, prc, asset.name))
                else:
                    mkt.bids.append(Bid(asset, qty, prc))
                    logger.info("%.2f$/MWh bid for %.2fMW to supply %s." %
                                (prc, qty, asset.name))

#        if self.hasRenderer():
#            render = self.getRenderer()


    def reset(self):
        """ Reinitialises the environment.
        """
        self.market.init()

# EOF -------------------------------------------------------------------------
