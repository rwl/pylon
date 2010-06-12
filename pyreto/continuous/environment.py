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

from numpy import array, ones

from pybrain.rl.agents.logging import LoggingAgent

from pylon import PQ, POLYNOMIAL
from pyreto.smart_market import Offer, Bid

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ZeroAgent" class:
#------------------------------------------------------------------------------

class ZeroAgent(LoggingAgent):

    def getAction(self):
        self.lastaction = -1.0 * ones(self.outdim)
        return self.lastaction

    def learn(self):
        pass

#------------------------------------------------------------------------------
#  "MarketEnvironment" class:
#------------------------------------------------------------------------------

class MarketEnvironment(object):
    """ Defines a continuous representation of an electricity market
        participant's environment.
    """

    def __init__(self, generators, market, numOffbids=1, offbidQty=False):
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

        # A participant may submit any number of offers/bids for each of the
        # generators in its portfolio.
        self.numOffbids = numOffbids

        # A participant may offer/bid just a markup on its cost and the
        # quantity is the maximum rated capacity of the generator divided by
        # the number of offers/bids. Alternatively, it may also specify the
        # quantity that is offered/bid for.
        self.offbidQty = offbidQty

        # List of offers/bids from the previous action.
        self._lastAction = []

        # Initialise the environment.
        self.reset()

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        Pd = sum([b.p_demand for b in self.market.case.buses if b.type == PQ])
        logger.info("State: %s" % Pd)
        return array([Pd])


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ g1_qty, g1_prc, g2_qty, g2_prc, ... ]
        """
        if self.offbidQty:
            self._offbidQuantityAndMarkup(action)
        else:
            self._offbidMarkup(action)


    def reset(self):
        """ Re-initialises the participant's environment.
        """
        self.market.reset()


    @property
    def indim(self):
        """ The number of action values that the environment accepts.
        """
        indim = self.numOffbids * len(self.generators)

        if self.offbidQty:
            return indim * 2
        else:
            return indim

    @property
    def outdim(self):
        """ The number of sensor values that the environment produces.
        """
        return 1

    #--------------------------------------------------------------------------
    #  "MarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def _offbidMarkup(self, action):
        totQty = 0.0
        for i, g in enumerate(self.generators):
            ratedPMin = self._g0[g]["p_min"]
            ratedPMax = self._g0[g]["p_max"]
            marginalPCost = self._g0[g]["p_cost"]
            marginalPCostModel = self._g0[g]["pcost_model"]

            # Determine the cost at zero output.
            if marginalPCostModel == POLYNOMIAL:
                costNoLoad = marginalPCost[-1]
            else:
                costNoLoad = 0.0

            # Divide the rated capacity equally among the offers/bids.
            if g.is_load:
                qty = ratedPMin / self.numOffbids
            else:
                qty = ratedPMax / self.numOffbids

            # Track the total quantity offered/bid for by the generator.
            totQty += qty

            # Get the marginal cost of generating at this output.
            c = g.total_cost(totQty, marginalPCost, marginalPCostModel)

            for j in range(self.numOffbids):
                # Index of the first markup in 'action' for the current gen.
                k = i * (len(action) / len(self.generators))
                # The markups are cumulative to ensure cost function convexity.
                mk = sum(action[k:k + j + 1])

                # Markup the marginal cost of the generator.
                if not g.is_load:
                    prc = c * ((100.0 + mk) / 100.0)
                else:
                    prc = c * ((100.0 + mk) / 100.0)

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


    def _offbidQuantityAndMarkup(self, action):
        raise NotImplementedError


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
            g0[g]["p_max"] = g.p_max
            g0[g]["p_min"] = g.p_min
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

# EOF -------------------------------------------------------------------------
