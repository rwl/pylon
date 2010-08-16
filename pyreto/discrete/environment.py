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

""" Defines a discrete environment for electricity market participants.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from scipy import array, linspace, mean, polyval, polyder

from pylon import POLYNOMIAL, PW_LINEAR, PQ

from pyreto.smart_market import Offer, Bid
from pyreto.util import xselections

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "MarketEnvironment" class:
#------------------------------------------------------------------------------

class MarketEnvironment(object):
    """ Defines the world in which an agent acts.  It receives an input with
        .performAction() and returns an output with .getSensors(). Each
        environment requires a reference to an asset (Generator) and the whole
        power system. The parameters of the asset are changed with the
        .performAction() method.
    """

    # discrete state space
    discreteStates = True

    # discrete action space
    discreteActions = True

    # number of possible actions for discrete action space
    numActions = 1

    #: A discrete environment accepts one integer as an action.
    indim = 1

    #: A discrete environment provides one integer sensor.
    outdim = 1

    def __init__(self, generators, market, numStates=1, markups=None,
                 withholds=None, numOffbids=1, offbidQty=False,
                 Pd0=None, Pd_min=0.0):
        """ Initialises the environment.
        """
        super(MarketEnvironment, self).__init__()

        #: Save initial generator ratings and costs as these will be
        #: overwritten when offers/bids are submitted to the market. Set by
        #: "generators" property.
        self._g0 = {}

        #: Initial total system demand.
        if Pd0 is None:
#            self._Pd0 = sum([b.p_demand for b in market.case.buses if b.type ==PQ])
            self._Pd0 = sum([b.p_demand for b in market.case.buses])
        else:
            self._Pd0 = Pd0

        #: Minimum total system demand. Used to define states.
        self.Pd_min = Pd_min

        #: Portfolio of generators endowed to the agent.
        self._generators = None
        self.generators = generators

        #: Auction that clears offer and bids using OPF results.
        self.market = market

        #: The number of discrete states for the environment.
        self.numStates = numStates

        #: List of all markup combinations for all generators.
        self._allActions = []

        #: List of offers/bids from the previous action used by ProfitTask.
        self._lastAction = []

        self._numOffbids = 1
        self._markups = ()
        self._withholds = ()

        #: A participant may submit any number of offers/bids for each of the
        #: generators in its portfolio.
        self.numOffbids = numOffbids

        #: Discrete percentage markups allowed on each offer/bid price.
        self.markups = (0.0,) if markups is None else markups

        #: Discrete percentages for withholding capacity.
        self.withholds = (0.0,) if withholds is None else withholds

        #: A participant may offer/bid just a markup on its cost and the
        #: quantity is the maximum rated capacity of the generator divided by
        #: the number of offers/bids. Alternatively, it may also specify the
        #: quantity that is offered/bid for.
#        self.offbidQty = offbidQty

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        sensors = self._getDemandSensor()
#        sensors = self._getPriceSensor()

        return sensors


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [int]
        """
        self._lastAction = []

        # Markups chosen for each generator.
        a = self._allActions[action]

        self._offbid(a)

#        if max(sum(self.withholds)) > 0.0:
#            # Markups chosen for each generator.
#            actions = self._allActions[action]
#
#            self._offbidWithholdAndMarkup(actions)
#        else:
#            # Markups chosen for each generator.
#            markups = self._allActions[action]
#            self._offbidMarkup(markups)


    def reset(self):
        """ Reinitialises the environment.
        """
#        self.market.init()
        self._lastAction = []

    #--------------------------------------------------------------------------
    #  "DiscreteMarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def _offbid(self, actions):
        n = self.numOffbids * len(self.generators)
        markups = actions[:n]
        withholds = actions[n:]

#        print "ACTIONS:", markups, withholds

        for i, g in enumerate(self.generators):
            ratedPMin = self._g0[g]["p_min"]
            ratedPMax = self._g0[g]["p_max"]
            margPCost = self._g0[g]["p_cost"]
            margPCostModel = self._g0[g]["pcost_model"]

            # Index of the first markup in 'markups' for generator 'i'.
            k = i * (len(markups) / len(self.generators))

            # Determine the cost at zero output.
            if margPCostModel == POLYNOMIAL:
                costNoLoad = margPCost[-1]
            else:
                costNoLoad = 0.0

            # Divide available capacity equally among the offers/bids.
            if g.is_load:
                qty = ratedPMin / self.numOffbids
            else:
                qty = ratedPMax / self.numOffbids

            # Track the total quantity offered/bid for by the generator.
            totQty = 0.0

#            p0 = 0.0
#            c0 = costNoLoad
            for j in range(self.numOffbids):
                totQty += qty

                # The markups are cumulative to ensure cost function convexity.
                mk = sum(markups[k:k + j + 1])

                # Marginal cost (cost function gradient).
                if margPCostModel == POLYNOMIAL:
                    cmarg = polyval(polyder(margPCost), totQty)
                elif margPCostModel == PW_LINEAR:
                    n_segments = len(margPCost) - 1
                    for i in range(n_segments):
                        x1, y1 = margPCost[i]
                        x2, y2 = margPCost[i + 1]
                        if x1 <= totQty <= x2:
                            cmarg = (y2 - y1) / (x2 - x1)
                    else:
                        raise ValueError, "Invalid bid quantity [%f]." % totQty
                else:
                    raise ValueError

                # Markup the marginal cost of the generator.
                if not g.is_load:
                    prc = cmarg * ((100.0 + mk) / 100.0)
                else:
                    prc = cmarg * ((100.0 + mk) / 100.0)

                if not g.is_load:
                    offer = Offer(g, qty, prc, costNoLoad)
                    self.market.offers.append(offer)

                    self._lastAction.append(offer)

                    logger.info("%.2fMW offered at %.2f$/MWh for %s (%.1f%%)."
                        % (qty, prc, g.name, mk))
                else:
                    bid = Bid(g, -qty, prc, costNoLoad)
                    self.market.bids.append(bid)

                    self._lastAction.append(bid)

                    logger.info("%.2f$/MWh bid for %.2fMW for %s (%.1f%%)."
                        % (prc, -qty, g.name, mk))

        return self._lastAction


#                p1 = totQty
#                costMarginal = g.total_cost(totQty, pCost, pCostModel)
#
#                dCdP = (costMarginal - c0) / (p1 - p0)
#
#                m0 = i * nOffbids
#                mN = m0 + j + 1
#                m = sum(markups[m0:mN])
#
#                prc = dCdP + (dCdP * m) if not g.is_load else dCdP - (dCdP * m)
#
#                if not g.is_load:
#                    offer = Offer(g, qty, prc, costNoLoad)
#                    mkt.offers.append(offer)
#                    self.last_action.append(offer)
#
#                    logger.info("%.2fMW offered at %.2f$/MWh for %s (%d%%)."
#                        % (qty, prc, g.name, m * 100))
#                else:
#                    bid = Bid(g, -qty, prc, costNoLoad)
#                    mkt.bids.append(bid)
#                    self.last_action.append(bid)
#
#                    logger.info("%.2f$/MWh bid for %.2fMW to supply %s (%d%%)."
#                        % (prc, -qty, g.name, m * 100))
#
#                p0 = p1
#                c0 = costMarginal


    def _offbidQuantityAndMarkup(self, action):
        raise NotImplementedError

    #--------------------------------------------------------------------------
    #  Environment sensors:
    #--------------------------------------------------------------------------

    def _getDemandSensor(self):
        Pd = sum([b.p_demand for b in self.market.case.buses])

        # Divide the range of demand into discrete bands.
        states = linspace(self.Pd_min, self._Pd0, self.numStates + 1)

        print "STATES:", self._Pd0, states

        for i in range(len(states) - 1):
            if states[i] <= round(Pd, 1) <= states[i + 1]:
                logger.info("%s demand state: %d (%.2f)" %
                            (self.generators[0].name, i, Pd))
                return array([i])
        else:
            raise ValueError, "No state defined for system demand [%.3f]." % Pd


    def _getPriceSensor(self):

#        print self._lastAction

        offers = [offer for offer in self._lastAction if offer.accepted]
#        bids = [bid for bid in self.market.bids if bid.accepted]

        if len(offers) > 0:
            avgPrice = mean([ob.clearedPrice for ob in offers])
            print "avgPrice:", avgPrice
        else:
            avgPrice = 0.0

        states = linspace(0.0, self.market.priceCap, self.numStates + 1)

        print "avgPrice:", avgPrice, states

        for i in range(len(states) - 1):
            if states[i] <= avgPrice <= states[i + 1]:
                logger.info("%s price state: %d" %
                            (self.generators[0].name, i))
                return array([i])
        else:
            raise ValueError, ("Average price [%.3f] above price cap [%.3f]." %
                (avgPrice, self.market.priceCap))

    #--------------------------------------------------------------------------
    #  "markups" property:
    #--------------------------------------------------------------------------

    def _getMarkups(self):
        """ Sets the list of possible percentage markups on marginal cost
        allowed with each offer/bid.
        """
        return self._markups


    def _setMarkups(self, markups):
        self._markups = markups
        self._allActions = self._getAllActions(markups, self.withholds)

    markups = property(_getMarkups, _setMarkups)

    #--------------------------------------------------------------------------
    #  "withholds" property:
    #--------------------------------------------------------------------------

    def _getWithholds(self):
        """ Sets the list of possible percentage withholds of capacity allowed
        with each offer/bid.
        """
        return self._withholds


    def _setWithholds(self, withholds):
        self._withholds = withholds
        self._allActions = self._getAllActions(self.markups, withholds)

    withholds = property(_getWithholds, _setWithholds)

    #--------------------------------------------------------------------------
    #  "numOffbids" property:
    #--------------------------------------------------------------------------

    def _getNumOffbids(self):
        """ Set the number of offers/bids submitted to the market.
        """
        return self._numOffbids


    def _setNumOffbids(self, numOffbids):
        self._numOffbids = numOffbids
        self._allActions = self._getAllActions(self.markups, self.withholds)

    numOffbids = property(_getNumOffbids, _setNumOffbids)

    #--------------------------------------------------------------------------
    #  "generators" property:
    #--------------------------------------------------------------------------

    def _getGenerators(self):
        """ Portfolio of generators endowed to the agent.
        """
        return self._generators


    def _setGenerators(self, generators):
        # Update the record of initial ratings and costs.
        g0 = {}
        for g in generators:
            # Asset capacity limits.
            g0[g] = {}
            g0[g]["p"] = g.p
            g0[g]["p_max"] = g.p_max
            g0[g]["p_min"] = g.p_min
            g0[g]["q"] = g.q
            g0[g]["q_max"] = g.q_max
            g0[g]["q_min"] = g.q_min
            # Marginal cost function proportional to current capacity.
            g0[g]["p_cost"] = g.p_cost
            g0[g]["pcost_model"] = g.pcost_model
            g0[g]["q_cost"] = g.q_cost
            g0[g]["qcost_model"] = g.qcost_model
            # Amortised fixed costs.
            g0[g]["startup"] = g.c_startup
            g0[g]["shutdown"] = g.c_shutdown
        self._g0 = g0
        self._generators = generators

    generators = property(_getGenerators, _setGenerators)

    #--------------------------------------------------------------------------
    #  Returns all possible actions:
    #--------------------------------------------------------------------------

    def _getAllActions(self, markups, withholds):
        n = self.numOffbids * len(self.generators)
        a = []
        for w in xselections(withholds, n):
            for m in xselections(markups, n):
                m.extend(w)
                a.append(m)

        return a

# EOF -------------------------------------------------------------------------
