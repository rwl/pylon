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

from scipy import array, linspace

from pylon import POLYNOMIAL, PQ

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

    def __init__(self, generators, market, numStates=1, markups=None,
                 numOffbids=1, offbidQty=False):
        """ Initialises the environment.
        """
        super(MarketEnvironment, self).__init__()

        # Save initial generator ratings and costs as these will be overwritten
        # when offers/bids are submitted to the market. Set by "generators"
        # property.
        self._g0 = {}

        # Portfolio of generators endowed to the agent.
        self._generators = None
        self.generators = generators

        # Auction that clears offer and bids using OPF results.
        self.market = market

        # The number of discrete states for the environment.
        self.numStates = numStates

        # List of all markup combinations.
#        self._allActions = []

        # List of offers/bids from the previous action.
        self.lastAction = []

#        self._numOffbids = 0
        self._markups = ()

        # Number of offers/bids a participant submits.
        self.numOffbids = numOffbids

        # Discrete markups allowed on each offer/bid.
        self.markups = (0.0,) if markups is None else markups

        # Does a participant's offer/bid comprise quantity aswell as price.
        self.offbidQty = offbidQty

        # A discrete environment provides one integer sensor and accepts
        # one integer as an action.
        self.indim = self.outdim = 1

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        Pd = sum([b.p_demand for b in self.market.case.buses if b.type == PQ])

        # Divide the range of market prices in to discrete bands.
        states = linspace(0.0, self._Pd0, self.numStates + 1)

        for i in range(len(states) - 1):
            if states[i] <= round(Pd, 1) <= states[i + 1]:
                logger.info("%s in state %d." % (self.generators[0].name, i))
                return array([i])
        else:
            raise ValueError, "Demand greater than peak [%.3f]." % Pd


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
            pCost = self.gencost[g]["p_cost"]
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

    #--------------------------------------------------------------------------
    #  "DiscreteMarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def _getGenerators(self):
        """ Portfolio of generators endowed to the agent.
        """
        return self._generators


    def _setGenerators(self, generators):
        self._generators = generators

        # Update the record of initial ratings and costs.
        self._g0 = {}
        for g in generators:
            # Asset capacity limits.
            self._g0[g] = {}
            self._g0[g]["p_max"] = g.p_max
            self._g0[g]["p_min"] = g.p_min
            self._g0[g]["q_max"] = g.q_max
            self._g0[g]["q_min"] = g.q_min
            # Marginal cost function proportional to current capacity.
            self._g0[g]["p_cost"] = g.p_cost
            self._g0[g]["pcost_model"] = g.pcost_model
            self._g0[g]["q_cost"] = g.q_cost
            self._g0[g]["qcost_model"] = g.qcost_model
            # Amortised fixed costs.
            self._g0[g]["startup"] = g.c_startup
            self._g0[g]["shutdown"] = g.c_shutdown

    generators = property(_getGenerators, _setGenerators)


    def _getMarkups(self):
        """ Sets the list of possible markups on marginal cost allowed
            with each offer/bid.
        """
        return self._markups


    def _setMarkups(self, markups):
        n = self.numOffbids * len(self.generators)
        self._allActions = list(xselections(markups, n))
        self._markups = markups

        print "mup", n, list(xselections(markups, n))

    markups = property(_getMarkups, _setMarkups)


    def _getNumOffbids(self):
        """ Set the number of offers/bids submitted to the market.
        """
        return self._numOffbids


    def _setNumOffbids(self, numOffbids):
        n = numOffbids * len(self.generators)
        self._allActions = list(xselections(self.markups, n))
        self._numOffbids = numOffbids

        print "noff", n, list(xselections(self.markups, n))

    numOffbids = property(_getNumOffbids, _setNumOffbids)

# EOF -------------------------------------------------------------------------

