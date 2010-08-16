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

from numpy import array, mean, r_

from pylon import PQ
from pyreto.discrete import MarketEnvironment as DiscreteMarketEnvironment

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "MarketEnvironment" class:
#------------------------------------------------------------------------------

class MarketEnvironment(DiscreteMarketEnvironment):
    """ Defines a continuous representation of an electricity market
        participant's environment.
    """

    def __init__(self, generators, market, numOffbids=1, maxMarkup=0.0,
            maxWithhold=None):
        """ A market environment has a portfolios of generation and a market.
        """
        super(MarketEnvironment, self).__init__(generators, market,
            numStates=0, markups=None, withholds=None, numOffbids=numOffbids)

        #: Maximum price markup.
        self.maxMarkup = maxMarkup

        #: Maximum quantity withhold.
        self.maxWithhold = maxWithhold

    #--------------------------------------------------------------------------
    #  "Environment" interface:
    #--------------------------------------------------------------------------

    def getSensors(self):
        """ Returns the currently visible state of the world as a numpy array
            of doubles.
        """
        sensors = array([])
        sensors = r_[sensors, self._getTotalDemandSensor()]
#        sensors = r_[sensors, self._getDemandSensor()]
#        sensors = r_[sensors, self._getPriceSensor()]
#        sensors = r_[sensors, self._getBusVoltageMagnitudeSensor()]
#        sensors = r_[sensors, self._getBusVoltageLambdaSensor()]
#        sensors = r_[sensors, self._getBranchFlowSensor()]

#        logger.info("State: %s" % sensors)

        return sensors


    def performAction(self, action):
        """ Performs an action on the world that changes it's internal state.
            @param action: an action that should be executed in the Environment
            @type action: array: [ g1_prc, g2_prc, g1_qty, g2_qty, ... ]
        """
        self._lastAction = []

        print "ACT:", action

        n = self.numOffbids * len(self.generators)

        if self.maxWithhold is not None:
            markups = action[:n]
            withholds = action[n:]
        else:
            markups = action
            withholds = [0.0] * n

        self._offbid(markups, withholds)


    @property
    def indim(self):
        """ The number of action values that the environment accepts.
        """
        indim = self.numOffbids * len(self.generators)

        if self.maxWithhold is not None:
            return indim * 2
        else:
            return indim

    @property
    def outdim(self):
        """ The number of sensor values that the environment produces.
        """
        return len(self.getSensors())


#    def reset(self):
#        """ Re-initialises the market environment.
#        """
#        self._lastAction = []
#        self.market.reset()

    #--------------------------------------------------------------------------
    #  "MarketEnvironment" interface:
    #--------------------------------------------------------------------------

    def _getTotalDemandSensor(self):
        Pd = sum([b.p_demand for b in self.market.case.buses])

        return array([Pd])


    def _getDemandSensor(self):
        Pd = [b.p_demand for b in self.market.case.buses if b.type == PQ]

        return array(Pd)


    def _getPriceSensor(self):
        offers = [offer for offer in self._lastAction]

        if len(offers) > 0:
            avgPrice = mean([ob.clearedPrice for ob in offers])
        else:
            avgPrice = 0.0

        f = self.market._solution["f"]

        return array([avgPrice, f])


    def _getBusVoltageMagnitudeSensor(self):
        Vm = array([b.v_magnitude for b in self.market.case.connected_buses])
#        Va = array([b.v_angle for b in self.market.case.connected_buses])
        return Vm


    def _getBusVoltageAngleSensor(self):
        Va = array([b.v_angle for b in self.market.case.connected_buses])
        return Va


    def _getBusVoltageLambdaSensor(self):
        """ Returns an array of length nb where each value is the sum of the
        Lagrangian multipliers on the upper and the negative of the Lagrangian
        multipliers on the lower voltage limits. """
        muVmin = array([b.mu_vmin for b in self.market.case.connected_buses])
        muVmax = array([b.mu_vmax for b in self.market.case.connected_buses])
        muVmin = -1.0 * muVmin
        diff = muVmin + muVmax
        return diff


    def _getBranchFlowSensor(self):
        Pf = array([l.p_from for l in self.market.case.online_branches])
#        Qf = array([l.q_from for l in self.market.case.online_branches])
        return Pf


#    def _offbidMarkup(self, action):
#        for i, g in enumerate(self.generators):
#            ratedPMin = self._g0[g]["p_min"]
#            ratedPMax = self._g0[g]["p_max"]
#            margPCost = self._g0[g]["p_cost"]
#            margPCostModel = self._g0[g]["pcost_model"]
#
#            # Index of the first markup in 'action' for the current gen.
#            k = i * (len(action) / len(self.generators))
#
#            # Determine the cost at zero output.
#            if margPCostModel == POLYNOMIAL:
#                costNoLoad = margPCost[-1]
#            else:
#                costNoLoad = 0.0
#
#            # Divide the rated capacity equally among the offers/bids.
#            if g.is_load:
#                qty = ratedPMin / self.numOffbids
#            else:
#                qty = ratedPMax / self.numOffbids
#
#            # Get the marginal cost of generating at this output.
##            c = g.total_cost(totQty, marginalPCost, marginalPCostModel)
#
#            totQty = 0.0
#            for j in range(self.numOffbids):
#                # Track the total quantity offered/bid for by the generator.
#                totQty += qty
#
#                # The markups are cumulative to ensure cost function convexity.
#                mk = sum(action[k:k + j + 1])
#
#                # Marginal cost.
#                if margPCostModel == POLYNOMIAL:
#                    cmarg = polyval(polyder(margPCost), totQty)
#                elif margPCostModel == PW_LINEAR:
#                    n_segments = len(margPCost) - 1
#                    for i in range(n_segments):
#                        x1, y1 = margPCost[i]
#                        x2, y2 = margPCost[i + 1]
#                        if x1 <= totQty <= x2:
#                            cmarg = (y2 - y1) / (x2 - x1)
#                    else:
#                        raise ValueError, "Invalid bid quantity [%f]." % totQty
#                else:
#                    raise ValueError
#
#                # Markup the marginal cost of the generator.
#                if not g.is_load:
#                    prc = cmarg * ((100.0 + mk) / 100.0)
#                else:
#                    prc = cmarg * ((100.0 + mk) / 100.0)
#
#                if not g.is_load:
#                    offer = Offer(g, qty, prc, costNoLoad)
#                    self.market.offers.append(offer)
#
#                    self._lastAction.append(offer)
#
#                    logger.info("%.2fMW offered at %.2f$/MWh for %s (%.1f%%)."
#                        % (qty, prc, g.name, mk))
#                else:
#                    bid = Bid(g, -qty, prc, costNoLoad)
#                    self.market.bids.append(bid)
#
#                    self._lastAction.append(bid)
#
#                    logger.info("%.2f$/MWh bid for %.2fMW for %s (%.1f%%)."
#                        % (prc, -qty, g.name, mk))
#
#        return self._lastAction

# EOF -------------------------------------------------------------------------
