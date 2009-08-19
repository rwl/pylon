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
#  Constants:
#------------------------------------------------------------------------------

BIG_NUMBER = 1e6

#------------------------------------------------------------------------------
#  "Bid" class:
#------------------------------------------------------------------------------

class Bid(object):
    """ Defines a bid to buy a quantity of power at a defined price.
    """
    def __init__(self, generator, qty, prc):
        # Generating unit to which the bid applies.
        self.generator = generator
        # Quantity of power bidding to be bought.
        self.quantity = qty
        # Maximum price willing to be paid.
        self.price = prc
        # Is the bid valid?
        self.withheld = False
        # Has the bid been partially or fully accepted?
        self.accepted = False

        # Quantity of bid cleared by the market.
        self.cleared_quantity = 0.0
        # Price at which the bid was cleared.
        self.cleared_price = 0.0

    @property
    def total_quantity(self):
        """ Output at which the generator has been dispatched.
        """
        self.generator.p


    @property
    def difference(self):
        """ The gap between the marginal unit (setting lambda) and the
            offer/bid price.
        """
        return self.price - self.p_lambda

#------------------------------------------------------------------------------
#  "Offer" class:
#------------------------------------------------------------------------------

class Offer(object):
    """ Defines a offer to sell a quantity of power at a defined price.
    """
    def __init__(self, qty, prc):
        self.quantity = qty
        self.price = prc
        # Is the offer valid?
        self.withheld = False
        # Has the offer been partially or fully accepted?
        self.accepted = False

#------------------------------------------------------------------------------
#  "PriceLimit" class:
#------------------------------------------------------------------------------

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
    def __init__(self, network, bids, offers, loc_adjust="dc",
                 auction_type="first price", price_cap=500, g_online=None,
                 period=1.0):
        """ Initialises a new SmartMarket instance. A price cap can be set
            with max_p.
        """
        self.network = network

        # Bids to by quantities of power at a price.
        self.bids = bids
        # Offers to sell power.
        self.offers = offers

        # Compute locational adjustments ('ignore', 'ac', 'dc').
        self.loc_adjust = loc_adjust

        # 'discriminative' - discriminative pricing (price equal to offer/bid)
        # 'lao'            - last accepted offer auction
        # 'fro'            - first rejected offer auction
        # 'lab'            - last accepted bid auction
        # 'frb'            - first rejected bid auction
        # 'first price'    - first price auction (marginal unit, offer or bid,
        #                    sets the price)
        # 'second price'   - second price auction (if offer is marginal, then
        #                    price is set by min(FRO,LAB), if bid, then
        #                    max(FRB,LAO)
        # 'split'          - split the difference pricing (price set by last
        #                    accepted offer & bid)
        # 'dual laob'      - LAO sets seller price, LAB sets buyer price
        self.auction_type = auction_type

        # Price cap. Offers greater than this are eliminated.
        self.price_cap = price_cap

        # A vector containing the commitment status of each generator from the
        # previous period (for computing startup/shutdown costs)
        if g_online is None:
            self.g_online = matrix(1, (len(network.all_generators), 1))
        else:
            self.g_online = g_online

        # Time duration of the dispatch period in hours.
        self.period = period

        # Constraint violation tolerance.
        self.violation = 5e-6


    def run(self):
        """ Computes cleared offers and bids.
        """
        # Start the clock.
        t0 = time.time()

        buses = self.network.connected_buses
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
        success = DCOPF().solve(self.network)

        # Compute quantities, prices and costs.
        if success:
            # Get nodal marginal prices from OPF.
            p_lambda = spdiag([bus.p_lambda for bus in buses])
            q_lambda = spdiag([bus.q_lambda for bus in buses])

            # Compute fudge factor for p_lambda to include price of bundled
            # reactive power. For loads Q = pf * P.
            pass

            # Guarantee that cleared offers are >= offers.
            guarantee_offer_price = True

            for offer in offers:
                offer.p_lambda = bus.p_lambda
                offer.total_quantity = generator.p

            for bid in bids:
                if self.have_q:
                    # Use unbundled lambdas.
                    bid.p_lambda = bus.p_lambda
                    # Allow cleared bids to be above bid price.
                    guarantee_bid_price = False
                else:
                    # Use bundled lambdas.
                    bid.p_lambda = bus.p_lambda + spdiag(pf[l]) * bus.q_lambda
                    # Guarantee that cleared bids are <= bids.
                    guarantee_bid_price = True
                bid.total_quantity = dispatchable_load.p

            # Clear bids and offers.
            cleared_offers, cleared_bids = self.auction(offers, bids)

        else:
            logger.error("Non-convergent OPF.")

            quantity = 0.0
            price = limits["max_offer"]

            for offbid in offers + bids:
                offbid.quantity = 0.0
                offbid.price = 0.0

            # Compute costs in $ (not $/hr).
            for g in generators:
                fixed_cost = market_time * g.total_cost(0.0)
                variable_cost = g.total_cost(market_time * quantity)-fixed_cost
#                if g.online:
#                    startup_cost = g.total_cost(g.c_startup)
#                else:
#                    shutdown_cost = g.total_cost(g.c_shutdown)

        elapsed = time.time() - t0


    def auction(self):
        """ Clears a set of bids and offers, where the pricing is adjusted for
            network losses and binding constraints.
        """
        limits = self.limits

        # Enforce price limits.
        if limits.has_key("max_offer"):
            max_offer = limits["max_offer"]
            for offer in offers:
                if offer.price >= max_offer:
                    offer.withheld = True
        if limits.has_key("min_bid"):
            min_bid = limits["min_bid"]
            for bid in bids:
                if bid.price <= min_bid:
                    bid.withheld = True

        for g in generators:
            g_offers = [offer for offer in offers if offer.generator == g]
            self.clear_quantities(g_offers)

            g_bids   = [bid for bid in bids if bid.generator == g]
            self.clear_quantities(g_bids)

        # Initialise cleared prices.
        for offbid in offers + bids:
            offbid.cleared_price = 0.0

        # Compute shift values to add to lam to get desired pricing.

        # The locationally adjusted offer/bid price, when normalized to an
        # arbitrary reference location where lambda is equal to ref_lam, is:
        #     norm_prc = prc + (ref_lam - lam)
        # Then we can define the difference between the normalized offer/bid
        # prices and the ref_lam as:
        #     diff = norm_prc - ref_lam = prc - lam
        # This diff represents the gap between the marginal unit (setting
        # lambda) and the offer/bid price in question.
        accepted = []
        rejected = []
        for offer in offers:
            if offer.withheld:
                lao = offer.difference
                fro = BIG_NUMBER
            else:
                lao = -BIG_NUMBER
                fro = offer.difference
            accepted.append(lao)
            rejected.append(fro)

        lao = max(accepted)
        fro = min(rejected)

        # lao + lambda is equal to the last accepted offer.
        lao = max([offer.difference for offer in offers])
        # fro + lambda is equal to the first rejected offer.
        fro = min([offer.difference for offer in offers])

        if bids:
            # lab + lambda is equal to the last accepted bid.
            lab = min([bid.difference for bid in bids])
            # frb + lambda is equal to the first rejected bid.
            frb = max([bid.difference for bid in bids])
        else:
            lab = frb = BIG_NUMBER

        # Cleared offer/bid prices for different auction types.
        for offbid in offers + bids:
            if auction_type == "discriminative":
                offbid.cleared_price = offbid.price
            elif auction_type == "lao":
                offbid.cleared_price = offbid.p_lambda + lao
            elif auction_type == "fro":
                offbid.cleared_price = offbid.p_lambda + fro
            elif auction_type == "lab":
                offbid.cleared_price = offbid.p_lambda + lab
            elif auction_type == "frb":
                offbid.cleared_price = offbid.p_lambda + frb
            elif auction_type == "first price":
                offbid.cleared_price = offbid.p_lambda
            elif auction_type == "second price":
                if abs(lao) < self.zero_tol:
                    offbid.cleared_price = offbid.p_lambda + min(fro, lab)
                else:
                    offbid.cleared_price = offbid.p_lambda + max(lao, frb)
            elif auction_type == "split":
                offbid.cleared_price = offbid.p_lambda + (lao - lab) / 2.0
            elif auction_type == "dual laob":
                raise NotImplementedError

        # Guarantee that cleared offer prices are >= offers.
        if self.guarantee_offer_price:
            for offer in offers:
                if offer.price > offer.cleared_price:
                    offer.cleared_price = offer.price

        # Guarantee that cleared bid prices are <= bids.
        if self.guarantee_bid_price:
            for bid in bids:
                if bid.price <= bid.cleared_price:
                    bid.cleared_price = bid.price

        # Clip cleared offer prices.
        if limits.has_key("max_cleared_offer"):
            max_cleared_offer = limits["max_cleared_offer"]

            for offer in offers:
                if offer.cleared_price > max_cleared_offer:
                    offer.cleared_price = max_cleared_offer

        # Clip cleared bid prices.
        if limits.has_key("min_cleared_bid"):
            min_cleared_bid = limits["min_cleared_bid"]

            for bid in bids:
                if bid.cleared_price < min_cleared_bid:
                    bid.cleared_price = min_cleared_bid

        # Make prices uniform after clipping (except for discrim auction)
        # since clipping may only affect a single block of a multi-block
        # generator.
        if auction_type != "discriminatory":
            raise NotImplementedError


    def clear_quantity(self, offbids):
        """ Computes the cleared bid quantity from total cleared quantity.
        """
        # Get the total output that the generator has been dispatched at by
        # the OPF routine.
        total_quantity = offbids[0].generator.p

        ob_quantity = sum([ob.quantity for ob in offbids])

        # TODO: Sort offers/bids according to ascending price.

        for offbid in offbids:
            # Compute the fraction of the block accepted.
            accepted = (total_quantity - ob_quantity) / offbid.quantity
            # Clip to the range 0-1.
            if accepted > 1.0:
                accepted = 1.0
            elif accepted < 1.0e-05:
                accepted = 0.0

            offbid.cleared_quantity = accepted * offbid.quantity

            if accepted > 0.0:
                offbid.accepted = True
            else:
                offbid.accepted = False


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
