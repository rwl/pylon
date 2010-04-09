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

    def __init__(self, generators, market, outdim=10, markups=None,
                 numOffbids=1):
        """ Initialises the environment.
        """
        super(DiscreteMarketEnvironment, self).__init__()

        # Generator ratings and marginal costs.  Set by 'generators' property.
        self._gencost = {}

        self.generators = generators

        # Auction that clears offer and bids using OPF results.
        self.market = market

        self._numOffbids = 0
        self._markups = ()

        # Number of offers/bids a participant submits.
        self.numOffbids = numOffbids

        # Discrete markups allowed on each offer/bid.
        self.markups = (0.0,0.1,0.2,0.3) if markups is None else markups

        # List of all markup combinations.
        self._allActions = []#list(xselections(markups, n_offbids))

        # List of offers/bids from the previous action.
        self._lastAction = []

        # Does a participant's offer/bid comprise quantity aswell as price.
#        self.offbidQty = offbidQty

        # A non-negative amount of money.
#        self.money = 1e6

#        if asset.is_load:
#            # Income received each periods.
#            self.endowmentProfile = 10
#            # Needs and preferences for power consumption each period.
#            self.utilityFunction = [1.0]
#            # Savings from previous periods.
#            self.savings = 100
#            # Each participant is a shareholder who owns shares in generating
#            # companies and receives an according dividend each period.
#            self.shares = {}

        #----------------------------------------------------------------------
        #  "Environment" interface:
        #----------------------------------------------------------------------

        # Set the number of action values that the environment accepts.
        self.indim = len(self._all_actions) * len(self.generators)

        # Set the number of sensor values that the environment produces.
        self.outdim = outdim

    #--------------------------------------------------------------------------
    #  "DiscreteMarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def getGenerators(self):
        return self._generators


    def setGenerators(self, generators):
        gencost = {}
        for g in generators:
            # Asset capacity limits.
            gencost[g] = {}
            gencost[g]["pMax"] = g.p_max
            gencost[g]["pMin"] = g.p_min
            gencost[g]["qMax"] = g.q_max
            gencost[g]["qMin"] = g.q_min
            # Marginal cost function proportional to current capacity.
            gencost[g]["pCost"] = g.p_cost
            gencost[g]["pCostModel"] = g.pcost_model
            gencost[g]["qCost"] = g.q_cost
            gencost[g]["qCostModel"] = g.qcost_model
            # Amortised fixed costs.
            gencost[g]["startup"] = g.startup
            gencost[g]["shutdown"] = g.shutdown
        self._gencost = gencost

        self._generators = generators

    # Portfolio of generators endowed to the agent.
    generators = property(getGenerators, setGenerators)


    def getMarkups(self):
        """ Sets the list of possible markups on marginal cost allowed
            with each offer/bid.
        """
        return self._markups


    def setMarkups(self, markups):
        n = self.numOffbids * len(self.generators)
        self._all_actions = list(xselections(markups, n))
        self._markups = markups

    markups = property(getMarkups, setMarkups)


    def getNumOffbids(self):
        """ Set the number of offers/bids submitted to the market.
        """
        return self._numOffbids


    def setNumOffbids(self, numOffbids):
        n = numOffbids * len(self.generators)
        self._allActions = list(xselections(self.markups, n))
        self._numOffbids = numOffbids

    numOffbids = property(getNumOffbids, setNumOffbids)

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        # TODO: Load forecast as state.
        if len(self.last_action):
            prc = mean([ob.cleared_price for ob in self.last_action])
        else:
            prc = 0.0

        # Divide the range of market prices in to discrete bands.
        limit = self.market.price_cap
        states = linspace(0.0, limit, self.outdim)

        for i in range(len(states) - 1):
            if states[i] <= round(prc, 1) <= states[i + 1]:
                logger.info("%s in state %d." % (self.name, i))
                return array([i])
        else:
            raise ValueError, "Cleared price mean: %f" % prc


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [int]
        """
        self.last_action = []

        markups = self._allActions[action]

        for i, g in enumerate(self.generators):
            mkt = self.market
            nOffbids = self.numOffbids
            pCost = self.gencost[g]["pCost"]
            pCostModel = self.gencost[g]["pCostModel"]

            # Divide available capacity equally among the offers/bids.
            if g.is_load:
                qty = self.gencost[g]["pMin"] / nOffbids
            else:
                qty = self.gencost[g]["pMax"] / nOffbids

            costNoLoad = pCost[-1] if pCostModel == POLYNOMIAL else 0.0

            totQty = 0.0
            p0 = 0.0
            c0 = costNoLoad
            for j in range(nOffbids):
                totQty += qty

                p1 = totQty
                costMarginal = g.total_cost(totQty, pCost, pCostModel)

                dCdP = (costMarginal - c0) / (p1 - p0)

                m0 = i * nOffbids
                mN = m0 + j + 1
                m = sum(markups[m0:mN])

                prc = dCdP + (dCdP * m) if not g.is_load else dCdP - (dCdP * m)

                if not g.is_load:
                    offer = Offer(g, qty, prc, costNoLoad)
                    mkt.offers.append(offer)
                    self.last_action.append(offer)

                    logger.info("%.2fMW offered at %.2f$/MWh for %s (%d%%)."
                        % (qty, prc, g.name, m * 100))
                else:
                    bid = Bid(g, -qty, prc, costNoLoad)
                    mkt.bids.append(bid)
                    self.last_action.append(bid)

                    logger.info("%.2f$/MWh bid for %.2fMW to supply %s (%d%%)."
                        % (prc, -qty, g.name, m * 100))

                p0 = p1
                c0 = costMarginal


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

    def __init__(self, generators, market, numOffbids=1, offbidQty=False):
        """ Initialises a new environment.
        """
        super(ContinuousMarketEnvironment, self).__init__()

        self._generators = None
        # Generator instance that the agent controls.
        self.generators = generators

        # Auction that clears offer and bids using OPF results.
        self.market = market

        # Number of offers/bids a participant submits.
        self.numOffbids = numOffbids

        # Does a participant's offer/bid comprise quantity aswell as price.
        self.offbidQty = offbidQty

        # List of offers/bids from the previous action.
        self.lastAction = []

        #----------------------------------------------------------------------
        #  "Environment" interface:
        #----------------------------------------------------------------------

        # Set the number of action values that the environment accepts.
        indim = numOffbids * 2 if offbidQty else numOffbids
        self.indim = indim * len(self.generators)

        # Set the number of sensor values that the environment produces.
        outdim = 0
        outdim += 3                                 # f, tot_qty, mcp
        outdim += len(market.case.buses) * 1        # Va, Plam
        outdim += len(market.case.branches) * 1     # Pf, mu_f
        outdim += len(market.case.generators) * 1   # Pg, mu_pmax, mu_pmin
        self.outdim = outdim

    #--------------------------------------------------------------------------
    #  "ContinuousMarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def getGenerators(self):
        return self._generators


    def setGenerators(self, generators):
        gencost = {}
        for g in generators:
            # Asset capacity limits.
            gencost[g] = {}
            gencost[g]["pMax"] = g.p_max
            gencost[g]["pMin"] = g.p_min
            gencost[g]["qMax"] = g.q_max
            gencost[g]["qMin"] = g.q_min
            # Marginal cost function proportional to current capacity.
            gencost[g]["pCost"] = g.p_cost
            gencost[g]["pCostModel"] = g.pcost_model
            gencost[g]["qCost"] = g.q_cost
            gencost[g]["qCostModel"] = g.qcost_model
            # Amortised fixed costs.
            gencost[g]["startup"] = g.startup
            gencost[g]["shutdown"] = g.shutdown
        self._gencost = gencost

        self._generators = generators

    # Portfolio of generators endowed to the agent.
    generators = property(getGenerators, setGenerators)

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
            offbids = [x for x in self.market.bids if x.vLoad == g]

        # Market sensors.
        marketSensors = zeros(3)

        if self.market._solution.has_key("f"):
            marketSensors[0] = self.market._solution["f"]
        marketSensors[1] = sum([ob.cleared_quantity for ob in offbids])
        if offbids:
            marketSensors[2] = offbids[0].cleared_price

        # Case related sensors.
#        angles = array([bus.v_angle for bus in case.buses])
        nodalPrice = array([bus.p_lmbda for bus in case.buses])

        flows = array([branch.p_from for branch in case.branches])
#        muFlow = array([branch.mu_s_from for branch in case.branches])

        pg = array([g.p for g in case.generators])
#        gMax = array([g.mu_pmax for g in case.generators])
#        gMin = array([g.mu_pmin for g in case.generators])

#        caseSensors = r_[flows, muFlow, angles, nodalPrice, pg, gMax, gMin]
        caseSensors = r_[flows, nodalPrice, pg]

        return r_[marketSensors, caseSensors]


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ qty, prc, qty, prc, ... ]
        """
        self.last_action = []

        numOffbids = self.numOffbids

        # Participants either submit prices, where the quantity is divided
        # equally among the offers/bids, or tuples of quantity and price.
        if not self.offbidQty:
            totQty = 0.0
            for i, g in enumerate(self.generators):
                pMin = self.gencost[g]["pMin"]
                pMax = self.gencost[g]["pMax"]
                pCost = self.gencost[g]["pCost"]
                pCostModel = self.gencost[g]["pCostModel"]

                costNoLoad = pCost[-1] if pCostModel == POLYNOMIAL else 0.0

                # Divide the rated capacity equally among the offers/bids.
                qty = pMin / numOffbids if g.is_load else pMax / numOffbids

                totQty += qty

#                marginal = self._get_marginal_cost(tot_qty)
                c = g.total_cost(totQty, pCost, pCostModel)

                mk = sum(action[:i + 1])

                prc = c * (1.0 - mk) if g.is_load else g * (1.0 + mk)

                if not g.is_load:
                    offer = Offer(g, qty, prc, costNoLoad)
                    self.market.offers.append(offer)
                    self.last_action.append(offer)
                    logger.info("%.2fMW offered at %.2f$/MWh for %s (%.1f%%)."
                        % (qty, prc, g.name, mk * 100))
                else:
                    bid = Bid(g, -qty, prc, costNoLoad)
                    self.market.bids.append(bid)
                    self.last_action.append(bid)
                    logger.info("%.2f$/MWh bid for %.2fMW for %s (%.1f%%)."
                        % (prc, -qty, g.name, mk * 100))
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
