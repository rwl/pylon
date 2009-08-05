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

""" Defines forums for trading electric energy.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from cvxopt import matrix

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Bid" class:
#------------------------------------------------------------------------------

class Bid(object):
    """ Defines a bid to buy a quantity of power at a defined price.
    """
    def __init__(self, qty, prc):
        self.quantity = qty
        self.price = prc

#------------------------------------------------------------------------------
#  "Offer" class:
#------------------------------------------------------------------------------

class Offer(object):
    """ Defines a offer to sell a quantity of power at a defined price.
    """
    def __init__(self, qty, prc):
        self.quantity = qty
        self.price = prc


class PriceLimit(object):
    """ Defines limits to offer/bid prices.
    """
    def __init__(self, min_bid, max_offer, min_cleared_bid, max_cleared_offer):
        """ Initialises a new PriceLimit instance.
        """
        self.p_min_bid = min_bid
        self.p_max_offer = max_offer
        self.p_min_cleared_bid = min_cleared_bid
        self.p_max_cleared_offer = max_cleared_offer

#------------------------------------------------------------------------------
#  "SmartMarket" class:
#------------------------------------------------------------------------------

class SmartMarket(object):
    """ Computes the new generation and price schedules based on the offers
        submitted.
    """
    def __init__(self, network, bids, offers, price_cap=500):
        """ Initialises a new SmartMarket instance. A price cap can be set
            with max_p.
        """
        self.network = network
        # Bids to by quantities of power at a price.
        self.bids = bids
        # Offers to sell power.
        self.offers = offers
        # Price cap. Offers greater than this are eliminated.
        self.price_cap = price_cap

        # Constraint violation tolerance.
        self.violation = 5e-6


    def run(self):
        """ Computes cleared offers and bids.
        """
        # Start the clock.
        t0 = time.time()

        generators = self.network.all_generators

        limits = {"max_offer": self.price_cap,
                  "max_cleared_offer": self.price_cap}

        # Create offers from the generator cost function.
        if not self.offers:
            self.offers = [g.get_offer for g in generators]

        # Number of points to define piece-wise linear cost.
        n_points = len(self.offers) + len(self.bids) + 1
        n_points = max([len(self.offers), len(self.bids)]) + 1

        # Convert active power bids & offers into piecewise linear segments.
        for g in generators:
            g_offers = [off for off in offers if off.generator == g]
            g.offers_to_pwl(g_offers)

            g_bids = [bid for bid in bids if bid.generator == g]
            g.offers_to_pwl(g_bids, is_bid=True)

        # Update generator limits.
        for g in generators:
            if g.p_max > 0.0:
                p_max = max([point[0] for point in points])
                if not g.p_min <= p_max <= g.p_max:
                    logger.error("Offer quantity outwith range.")
            if g.p_min < 0.0:
                p_min = min([point[0] for point in points])
                if g.p_min <= p_min <= g.p_max:
                    if g.mode == "dispatchable load":
                        q_min = g.q_min * p_min / g.p_min
                        q_max = g.q_max * p_min / g.p_min
                    else:
                        logger.error("Bid quantity outwith range.")

            g.p_min = p_min
            g.p_max = p_max

        # No capacity bid/offered for active power.
        participating = [offbid.generator for offbid in offers + bids]
        for g in generators:
            if g not in participating:
                g.online = False

        # Move p_min and p_max limits out slightly to avoid problems with
        # lambdas caused by rounding errors when corner point of cost function
        # lies at exactly p_min or p_max.
        for g in generators:
            if g.mode == "generator": # Skip dispatchable loads.
                g.p_min -= 100 * self.violation
                g.p_max += 100 * self.violation

        # Solve the optimisation problem.
        solution = DCOPFRoutine().solve(self.network)

        # Compute quantities, prices and costs.
        if solution["status"] == "optimal":
            pass
        else:
            logger.error("Non-convergent OPF.")

        elapsed = time.time() - t0


#    def _price_limit_default(self, limits=None, have_q=False):
#        """ Returns a dictionary with default values for offer/bid limits.
#        """
#        if not limits:
#            if have_q:
#                p_limits = {}

#------------------------------------------------------------------------------
#  "ContractsMarket" class:
#------------------------------------------------------------------------------

#class ContractsMarket(object):
#    """ Defines a market for the formation of long-term bilateral contracts.
#    """
#    def __init__(self, buyers, sellers):
#        """ Initialises a new ContractsMarket instance.
#        """
#        # Agents associated with Generator instances operating as dispatchable
#        # loads and wishing to buy of electric energy.
#        self.buyers = buyers
#
#        self.bids = {}
#
#        # Agents associated with generators that may contract to sell electric
#        # energy to buyers.
#        self.sellers = sellers
#
#        self.offers = {}
#
#
#    def get_bids(self, agent):
#        """ Returns proposals from buyers bidding to buy electric energy from
#            the given seller 'agent'.
#        """
#        if self.bids.has_key(agent):
#            return self.bids[agent]
#        else:
#            return matrix()

# EOF -------------------------------------------------------------------------
