#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines an environment for market participants.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from scipy import array, zeros, mean, linspace, r_, polyval, polyder

#from pybrain.rl.environments import Environment
#from pybrain.rl.environments.graphical import GraphicalEnvironment

from pylon import PW_LINEAR, POLYNOMIAL
from pyreto.smart_market import Offer, Bid

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "DiscreteMarketEnvironment" class:
#------------------------------------------------------------------------------

class DiscreteMarketEnvironment(object):
    """ Defines the world in which an agent acts.  It receives an input with
        .performAction() and returns an output with .getSensors(). Each
        environment requires a reference to an asset (Generator) and the whole
        power system. The parameters of the asset are changed with the
        .performAction() method.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, asset, market, outdim=10, markups=None, n_offbids=1):
        """ Initialises the environment.
        """
        super(DiscreteMarketEnvironment, self).__init__()

        # Generator instance that the agent controls.
        self.asset = asset

        # Auction that clears offer and bids using OPF results.
        self.market = market

        # Number of offers/bids a participant submits.
        self.n_offbids = n_offbids

        # Discrete markups allowed on each offer/bid.
        self.markups = (0.0,0.1,0.2,0.3) if markups is None else markups

        # List of all markup combinations.
        self.all_actions = list(xselections(markups, n_offbids))

        # List of offers/bids from the previous action.
        self.last_action = []

        # Does a participant's offer/bid comprise quantity aswell as price.
#        self.offbid_qty = offbid_qty

        # A non-negative amount of money.
#        money = 1e6

#        assert asset.pcost_model == PW_LINEAR
        # Asset capacity limits.
        self._p_max = asset.p_max
        self._p_min = asset.p_min
        # Marginal cost function proportional to current capacity.
        self._p_cost = asset.p_cost
        self._pcost_model = asset.pcost_model

#        # Amortised fixed costs.
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

#        self.render = render
#        if self.render:
#            self.updateDone = True
#            self.updateLock=threading.Lock()

        #----------------------------------------------------------------------
        #  Set the number of action values that the environment accepts.
        #----------------------------------------------------------------------

        self.indim = len(self.all_actions)

        #----------------------------------------------------------------------
        #  Set the number of sensor values that the environment produces.
        #----------------------------------------------------------------------

        self.outdim = outdim

    #--------------------------------------------------------------------------
    #  "ParticipantEnvironment" interface:
    #--------------------------------------------------------------------------

    def setMarkups(self, markups):
        """ Sets the list of possible markups on marginal cost allowed
            with each offer/bid.
        """
        self.all_actions = list(xselections(markups, self.n_offbids))
        self.markups = markups


    def setNumOffbids(self, n_offbids):
        """ Set the number of offers/bids submitted to the market.
        """
        self.all_actions = list(xselections(self.markups, n_offbids))
        self.n_offbids = n_offbids

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
#        offbids = self.market.get_offbids(self.asset)

        if len(self.last_action):
            prc = mean([ob.cleared_price for ob in self.last_action])
        else:
            prc = 0.0

#        print "STATE:", [ob.cleared_price for ob in self.last_action]

        # Divide the range of market prices in to discrete bands.
        limit = self.market.price_cap
        states = linspace(0.0, limit, self.outdim)

        for i in range(len(states) - 1):
            if states[i] <= round(prc, 1) <= states[i + 1]:
                logger.info("%s in state %d." % (self.asset.name, i))
                return array([i])
        else:
            raise ValueError, "Cleared price mean: %f" % prc


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [int]
        """
        self.last_action = []

        asset = self.asset
        mkt = self.market
        n_offbids = self.n_offbids
        p_cost = self._p_cost

        markups = self.all_actions[action]

        # Divide available capacity equally among the offers/bids.
        if asset.is_load:
            qty = self._p_min / n_offbids
        else:
            qty = self._p_max / n_offbids

        c_noload = self._p_cost[-1] \
            if self._pcost_model == POLYNOMIAL else 0.0

        tot_qty = 0.0
        p0 = 0.0
        c0 = c_noload
        for i in range(n_offbids):
            tot_qty += qty

#            if self._pcost_model == PW_LINEAR:
#                n_segments = len(p_cost) - 1
#                for j in range(n_segments):
#                    x1, y1 = p_cost[j]
#                    x2, y2 = p_cost[j + 1]
#                    if x1 <= tot_qty <= x2:
#                        m = (y2 - y1) / (x2 - x1)
#                        break
#                else:
#                    raise ValueError
#                c_noload = 0.0
#            elif self._pcost_model == POLYNOMIAL:
#                m = polyval(polyder(list(self._p_cost)), tot_qty)
#                c_noload = self._p_cost[-1]
#            else:
#                raise ValueError

            p1 = tot_qty
            c_marg = asset.total_cost(tot_qty, self._p_cost, self._pcost_model)

#            print "MARG:", c_marg

            # Cumulative markup/markdown to ensure convexity.
#            if not asset.is_load:
#                c1 = c_marg + (c_marg * sum(markups[:i + 1]))
#            else:
#                c1 = c_marg - (c_marg * sum(markups[:i + 1]))

            m = (c_marg - c0) / (p1 - p0)

            if not asset.is_load:
                prc = m + (m * sum(markups[:i + 1]))
            else:
                prc = m - (m * sum(markups[:i + 1]))

#            print "PRC:", prc

            if not asset.is_load:
                offer = Offer(asset, qty, prc, c_noload)
                mkt.offers.append(offer)
                self.last_action.append(offer)

                logger.info("%.2fMW offered at %.2f$/MWh for %s (%d%%)." %
                    (qty, prc, asset.name, sum(markups[:i + 1]) * 100))
            else:
                bid = Bid(asset, -qty, prc, c_noload)
                mkt.bids.append(bid)
                self.last_action.append(bid)

                logger.info("%.2f$/MWh bid for %.2fMW to supply %s (%d%%)." %
                    (prc, -qty, asset.name, sum(markups[:i + 1]) * 100))

            p0 = p1
            c0 = c_marg


    def reset(self):
        """ Reinitialises the environment.
        """
        self.market.init()

#------------------------------------------------------------------------------
#  "ContinuousMarketEnvironment" class:
#------------------------------------------------------------------------------

class ContinuousMarketEnvironment(object):
    """ Defines a continuous representation of an electricity market.
    """

    def __init__(self, asset, market, n_offbids=1, offbid_qty=False):
        """ Initialises a new environment.
        """
        super(ContinuousMarketEnvironment, self).__init__()

        # Generator instance that the agent controls.
        self.asset = asset

        # Auction that clears offer and bids using OPF results.
        self.market = market

        # Number of offers/bids a participant submits.
        self.n_offbids = n_offbids

        # Does a participant's offer/bid comprise quantity aswell as price.
        self.offbid_qty = offbid_qty

        # Asset properties.
        self._p_max = asset.p_max
        self._p_min = asset.p_min
        self._p_cost = asset.p_cost
        self._pcost_model = asset.pcost_model

        # List of offers/bids from the previous action.
        self.last_action = []

        #----------------------------------------------------------------------
        # Set the number of action values that the environment accepts.
        #----------------------------------------------------------------------

        self.indim = n_offbids * 2 if offbid_qty else n_offbids

        #----------------------------------------------------------------------
        # Set the number of sensor values that the environment produces.
        #----------------------------------------------------------------------

        outdim = 0
        outdim += 3                                 # f, tot_qty, mcp
        outdim += len(market.case.buses) * 1        # Va, Plam
        outdim += len(market.case.branches) * 1     # Pf, mu_f
        outdim += len(market.case.generators) * 1   # Pg, mu_pmax, mu_pmin
        self.outdim = outdim

    #--------------------------------------------------------------------------
    #  "ContinuousMarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def _get_marginal_cost(self, qty):
        """ Returns the asset's marginal cost at the given output.
        """
        if self._pcost_model == PW_LINEAR:
            n_segments = len(self._p_cost) - 1
            for j in range(n_segments):
                x1, y1 = self._p_cost[j]
                x2, y2 = self._p_cost[j + 1]
                if x1 <= qty <= x2:
                    m = (y2 - y1) / (x2 - x1)
                    break
            else:
                raise ValueError
        elif self._pcost_model == POLYNOMIAL:
            m = polyval(polyder(list(self._p_cost)), qty)
        else:
            raise ValueError

        return m

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        g = self.asset
        case = self.market.case

        if not g.is_load:
            offbids = [x for x in self.market.offers if x.generator == g]
        else:
            offbids = [x for x in self.market.bids if x.vload == g]

        # Market sensors.
        market_sensors = zeros(3)

        if self.market._solution.has_key("f"):
            market_sensors[0] = self.market._solution["f"]
        market_sensors[1] = sum([ob.cleared_quantity for ob in offbids])
        if offbids:
            market_sensors[2] = offbids[0].cleared_price

        # Case related sensors.
#        angles = array([bus.v_angle for bus in case.buses])
        nodal_prc = array([bus.p_lmbda for bus in case.buses])

        flows = array([branch.p_from for branch in case.branches])
#        mu_flow = array([branch.mu_s_from for branch in case.branches])

        pg = array([g.p for g in case.generators])
#        g_max = array([g.mu_pmax for g in case.generators])
#        g_min = array([g.mu_pmin for g in case.generators])

#        case_sensors = r_[flows, mu_flow, angles, nodal_prc, pg, g_max, g_min]
        case_sensors = r_[flows, nodal_prc, pg]

#        print "SENSORS:", r_[market_sensors, case_sensors]

        return r_[market_sensors, case_sensors]


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ qty, prc, qty, prc, ... ]
        """
        self.last_action = []

        asset = self.asset

#        print "ACTION:", action

        # Participants either submit prices, where the quantity is divided
        # equally among the offers/bids, or tuples of quantity and price.
        if not self.offbid_qty:
            # Divide the rated capacity equally among the offers/bids.
            if asset.is_load:
                qty = self._p_min / self.n_offbids
            else:
                qty = self._p_max / self.n_offbids

            tot_qty = 0.0

            for i in range(self.indim):
                tot_qty += qty

                marginal = self._get_marginal_cost(tot_qty)

                if asset.is_load:
                    prc = marginal * (1.0 - sum(action[:i + 1])) # markdown
                else:
                    prc = marginal * (1.0 + sum(action[:i + 1]))

                if not asset.is_load:
                    offer = Offer(asset, qty, prc)
                    self.market.offers.append(offer)
                    self.last_action.append(offer)
                    logger.info("%.2fMW offered at %.2f$/MWh for %s (%.1f%%)." %
                        (qty, prc, asset.name, sum(action[:i + 1]) * 100))
                else:
                    bid = Bid(asset, -qty, prc)
                    self.market.bids.append(bid)
                    self.last_action.append(bid)
                    logger.info("%.2f$/MWh bid for %.2fMW to supply %s (%.1f%%)." %
                        (prc, -qty, asset.name, sum(action[:i + 1]) * 100))
        else:
            raise NotImplementedError

            # Agent's actions comprise both quantities and prices.
#            for i in range(0, len(action), 2):
#                qty = action[i]
#                prc = action[i + 1]
#                if not asset.is_load:
#                    self.market.offers.append(Offer(asset, qty, prc))
#                    logger.info("%.2fMW offered at %.2f$/MWh for %s." %
#                                (qty, prc, asset.name))
#                else:
#                    self.market.bids.append(Bid(asset, qty, prc))
#                    logger.info("%.2f$/MWh bid for %.2fMW to supply %s." %
#                                (prc, qty, asset.name))


    def reset(self):
        """ Reinitialises the environment.
        """
        self.market.reset()

#------------------------------------------------------------------------------
#  "xselections" function:
#------------------------------------------------------------------------------

def xselections(items, n):
    """ Takes n elements (not necessarily distinct) from the sequence, order
        matters.

        @see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/190465
    """
    if n==0:
        yield []
    else:
        for i in xrange(len(items)):
            for ss in xselections(items, n-1):
                yield [items[i]]+ss

# EOF -------------------------------------------------------------------------
