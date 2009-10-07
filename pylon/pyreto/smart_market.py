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

import time
import logging

from cvxopt import matrix, spdiag

from pylon import UDOPF

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "SmartMarket" class:
#------------------------------------------------------------------------------

class SmartMarket(object):
    """ Computes the new generation and price schedules based on the offers
        submitted.

        References:
            R. Zimmerman, 'extras/smartmarket/smartmkt.m', MATPOWER,
            PSERC (Cornell), version 3.2, http://www.pserc.cornell.edu/matpower
    """

    def __init__(self, case, offers=None, bids=None, limits=None,
            loc_adjust="dc", auction_type="first price", price_cap=500,
            g_online=None, period=1.0):
        """ Initialises a new SmartMarket instance.
        """
        self.case = case

        # Offers to sell a quantity of power at a particular price.
        if offers is None:
            self.offers = []
        else:
            self.offers = offers

        # Bids to buy power.
        if bids is None:
            self.bids = []
        else:
            self.bids = bids

        # Offer/bid limits.
        if limits is None:
#            self.limits = PriceLimit()
#            self.limits = {"min_bid": None, "max_offer": None,
#                "min_cleared_bid": None, "max_cleared_offer": None}
            self.limits = {}
        else:
            self.limits = limits

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
        #                    price is set by min(fro, lab), if bid, then
        #                    max(frb, lao)
        # 'split'          - split the difference pricing (price set by last
        #                    accepted offer & bid)
        # 'dual laob'      - LAO sets seller price, LAB sets buyer price
        self.auction_type = auction_type

        # Price cap. Offers greater than this are eliminated.
        self.price_cap = price_cap

        # A vector containing the commitment status of each generator from the
        # previous period (for computing startup/shutdown costs)
        if g_online is None:
            # Assume all generators on-line unless otherwise specified.
            self.g_online = matrix(1, (len(case.all_generators), 1))
        else:
            self.g_online = g_online

        # Time duration of the dispatch period in hours.
        self.period = period

        # Constraint violation tolerance.
        self.violation = 5e-6

        # Guarantee that cleared offers are >= offers.
        self.guarantee_offer_price = True

        # Guarantee that cleared bids are <= bids.
        self.guarantee_bid_price = True


        # Finish initialising the market.
        self.init()


    def init(self):
        """ Initialises the market.
        """
        generators = [g for g in self.case.all_generators if not g.is_load]
        vloads     = [g for g in self.case.all_generators if g.is_load]

        if not self.offers:
            # Create offers from the generator cost functions.
            self.offers = [off for g in generators for off in g.get_offers()]

        if not self.bids:
            self.bids = [bid for vl in vloads for bid in vl.get_bids()]


    def clear(self):
        """ Computes cleared offers and bids.
        """
        t0 = time.time()

        offers = self.offers
        bids = self.bids
        limits = self.limits

        buses = self.case.connected_buses
        all_generators = self.case.all_generators
        generators = [g for g in all_generators if not g.is_load]
        vloads     = [g for g in all_generators if g.is_load]

        if [offbid for offbid in offers + bids if offbid.reactive]:
            have_q = True
            raise NotImplementedError, "Combined active/reactive power " \
                "market not yet implemented."
        else:
            have_q = False

#        if have_q and vloads and self.auction_type not in ["discriminative",
#                                                           "lao",
#                                                           "first price"]:
#            logger.error("Combined active/reactive power markets with "
#                "constant power factor dispatchable loads are only "
#                "implemented for 'discriminative', 'lao' and 'first price' "
#                "auction types.")


        # Eliminates offers (but not bids) above 'price_cap'.
        limits['max_offer'] = self.price_cap
        limits['max_cleared_offer'] = self.price_cap

        # Withhold offers/bids outwith optional price limits.
        self.enforce_limits(offers, bids, limits)

        # Convert power offers into piecewise linear segments and update
        # generator limits.
        for g in generators:
            g_offers = [offer for offer in offers if offer.generator == g]
            g.offers_to_pwl(g_offers)

            # Adjust generator limits.
            g.adjust_limits()

            p_offers = [of for of in g_offers if not of.reactive]
            q_offers = [of for of in g_offers if of.reactive]

            # Capacity offered for active power.
            if p_offers:
                pass
#                p_max = max([point[0] for point in g.pwl_points])
#                if not g.p_min <= p_max <= g.p_max:
#                    logger.error("Offer quantity (%.2f) must be between %.2f "
#                        "and %.2f." % (p_max, max([0, g.p_min]), g.p_max))
#                else:
#                    g.p_max = p_max
#                    g.online = True
            elif q_offers:
                # FIXME: Dispatch at zero real power without shutting down
                # if capacity offered for reactive power.
#                g.p_min = g.p_max = 0.0
                g.online = True
            else:
                # Shutdown the unit if no capacity offered for active or
                # reactive power.
                g.online = False

            # FIXME: Update generator reactive power limits.

        # Convert power bids into piecewise linear segments and update
        # dispatchable load limits.
        for vl in vloads:
            vl_bids = [bid for bid in bids if bid.vload == vl]

            vl.bids_to_pwl(vl_bids)

            p_bids = [bid for bid in vl_bids if not bid.reactive]
            q_bids = [bid for bid in vl_bids if bid.reactive]

            # Capacity offered for active power.
            if p_bids:
                pass
#                p_min = min([point[0] for point in g.pwl_points])
#                if vl.p_min <= p_min <= vl.p_max:
#                    vl.q_min = vl.q_min * p_min / vl.p_min
#                    vl.q_max = vl.q_max * p_min / vl.p_min
#                    vl.p_min = p_min
#                    vl.online = True
#                else:
#                    logger.error("Bid quantity (%.2f) must be between %.2f "
#                        "and %.2f." % (-p_min, max([0, vl.p_max]), -vl.p_min))
            elif q_bids:
                # FIXME: Dispatch at zero real power without shutting down if
                # reactive power offered.
#                vl.q_min = vl.q_max = 0.0
                vl.online = True
            else:
                vl.online = False

            # FIXME: Update dispatchable load reactive power limits.

        # Move p_min and p_max limits out slightly to avoid problems with
        # lambdas caused by rounding errors when corner point of cost function
        # lies at exactly p_min or p_max.
        for g in generators: # Skip dispatchable loads.
            g.p_min -= 100 * self.violation
            g.p_max += 100 * self.violation


        # Solve the optimisation problem.
        success = UDOPF(dc=self.loc_adjust=="dc").solve(self.case)


        # Compute quantities, prices and costs.
        if success:
            # Guarantee that cleared offers are >= offers.
            self.guarantee_offer_price = True

            for offer in offers:
                # Locate the bus to which the offer's generator is connected.
                for bus in buses:
                    if offer.generator in bus.generators:
                        break # Go with the first one found.
                else:
                    logger.error("Generator bus not found.")

                # Get nodal marginal price from OPF results.
                offer.p_lambda = bus.p_lambda
                offer.total_quantity = offer.generator.p

            for bid in bids:
                # Locate the bus to which the dispatchable load is connected.
                for bus in buses:
                    if bid.vload in bus.generators:
                        break
                else:
                    logger.error("Dispatchable load bus not found.")

                if have_q:
                    # Use unbundled lambdas.
                    bid.p_lambda = bus.p_lambda
                    # Allow cleared bids to be above bid price.
                    self.guarantee_bid_price = False
                else:
                    # Compute fudge factor for p_lambda to include price of
                    # bundled reactive power. For loads Q = pf * P.
                    if bid.vload.q_max == 0.0:
                        pf = bid.vload.q_min / bid.vload.p_min
                    elif bid.vload.q_min == 0.0:
                        pf = bid.vload.q_max / bid.vload.p_min
                    else:
                        pf = 0.0

                    # Use bundled lambdas.
                    bid.p_lambda = bus.p_lambda + pf * bus.q_lambda

                    # Guarantee that cleared bids are <= bids.
                    self.guarantee_bid_price = True

                bid.total_quantity = -bid.vload.p

            # Clear bids and offers.
            cleared_offers, cleared_bids = self.auction(offers, bids)

        else:
            logger.error("Non-convergent UOPF.")

            quantity = 0.0
            price = limits.max_offer

            for offbid in offers + bids:
                offbid.quantity = 0.0
                offbid.price = 0.0

            # Compute costs in $ (not $/hr).
            for g in generators:
                fixed_cost = self.period * g.total_cost(0.0)
                variable_cost = g.total_cost(self.period * quantity)-fixed_cost
#                if g.online:
#                    startup_cost = g.total_cost(g.c_startup)
#                else:
#                    shutdown_cost = g.total_cost(g.c_shutdown)

        elapsed = time.time() - t0
        logger.info("SmartMarket cleared in %.3fs" % elapsed)

        return True


    def auction(self, offers, bids):
        """ Clears a set of bids and offers, where the pricing is adjusted for
            network losses and binding constraints.

            References:
                R. Zimmerman, 'extras/smartmarket/auction.m', MATPOWER,
                Cornell, version 3.2, http://www.pserc.cornell.edu/matpower
        """
        generators = [g for g in self.case.all_generators if not g.is_load]
        vloads     = [g for g in self.case.all_generators if g.is_load]

        for g in generators:
            self.clear_quantity(offers, g)

        for vl in vloads:
            self.clear_quantity(bids, vl)

        # Compute shift values to add to lam to get desired pricing.
        #
        # The locationally adjusted offer/bid price, when normalized to an
        # arbitrary reference location where lambda is equal to ref_lam, is:
        #     norm_prc = prc + (ref_lam - lam)
        # Then we can define the difference between the normalized offer/bid
        # prices and the ref_lam as:
        #     diff = norm_prc - ref_lam = prc - lam
        # This diff represents the gap between the marginal unit (setting
        # lambda) and the offer/bid price in question.
        #
        # Rejected offers will have a positive diff and the lao has the least
        # negative diff.
        accepted = [of for of in offers if of.accepted]
        rejected = [of for of in offers if not of.accepted]

        # Sort according to the difference between the offer price and the
        # reference nodal marginal price in ascending order.
        accepted.sort(key=lambda x: x.difference)
        rejected.sort(key=lambda x: x.difference)

        # lao + lambda is equal to the last accepted offer.
        lao = accepted[-1] # Last Accepted Offer
        # fro + lambda is equal to the first rejected offer.
        fro = rejected[0]  # First Rejected Offer


        accepted_bids = [bid for bid in bids if bid.accepted]
        accepted_bids.sort(key=lambda bid: bid.difference)#, reverse=True)

        rejected_bids = [bid for bid in bids if not bid.accepted]
        rejected_bids.sort(key=lambda bid: bid.difference)#, reverse=True)

        lab = accepted_bids[-1] if accepted_bids else None # Last Accepted Bid
        frb = rejected_bids[0] if rejected_bids else None # First Rejected Bid

        # Cleared offer/bid prices for different auction types.
        for offbid in offers + bids:
            auction_type = self.auction_type

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
        if self.limits.has_key("max_cleared_offer"):
            max_cleared_offer = self.limits["max_cleared_offer"]

            for offer in offers:
                if offer.cleared_price > max_cleared_offer:
                    offer.cleared_price = max_cleared_offer

        # Clip cleared bid prices.
        if self.limits.has_key("min_cleared_bid"):
            min_cleared_bid = self.limits["min_cleared_bid"]

            for bid in bids:
                if bid.cleared_price < min_cleared_bid:
                    bid.cleared_price = min_cleared_bid

        # Make prices uniform after clipping (except for discrim auction)
        # since clipping may only affect a single block of a multi-block
        # generator.
        if auction_type != "discriminatory":
            raise NotImplementedError


    def clear_quantity(self, offbids, gen):
        """ Computes the cleared bid quantity from total cleared quantity.
        """
        # Filter out offers/bids not applicable to the generator in question.
        if gen.is_load:
            offbids = [offer for offer in offbids if offer.vload == gen]
        else:
            offbids = [offer for offer in offbids if offer.generator == gen]

        # Offers/bids within valid price limits (not withheld).
        valid = [ob for ob in offbids if not ob.withheld]
        # Sort offers/bids by price in ascending order.
        valid.sort(key=lambda ob: ob.price)

        accepted_qty = 0.0
        for ob in valid:
            # Compute the fraction of the block accepted.
            accepted = (ob.total_quantity - accepted_qty) / ob.quantity

            # Clip to the range 0-1.
            if accepted > 1.0:
                accepted = 1.0
            elif accepted < 1.0e-05:
                accepted = 0.0

            ob.cleared_quantity = accepted * ob.quantity

            if accepted > 0.0:
                ob.accepted = True
            else:
                ob.accepted = False

            # Log the event.
            if ob.accepted:
                logger.info("%s [%s, %.3f, %.3f] accepted at %.2fMW." %
                    (ob.__class__.__name__, ob.asset_name, ob.quantity,
                     ob.price, ob.cleared_quantity))
            else:
                logger.info("%s [%s, %.3f, %.3f] rejected." %
                    (ob.__class__.__name__, ob.asset_name, ob.quantity,
                     ob.price))

            # Increment the accepted quantity.
            accepted_qty += ob.quantity


    def enforce_limits(self, offers, bids, limits):
        """ Returns a tuple of lists of offers and bids with their withheld
            flags set if they represent invalid (<= 0.0) quantities or have
            prices outwith the set limits.
        """
        # Strip zero quantities (rounded to 4 decimal places).
#        if min([offbid.quantity for offbid in offers + bids]) < 0.0:
#            logger.info("Ignoring offers/bids with negative quantities.")
#
#        if 0.0 in [round(offer, 4) for offer in offers + bids]:
#            logger.info("Ignoring zero quantity offers/bids.")
#
#        offers = [offr for offr in offers if round(offr.quantity, 4) > 0.0]
#        bids = [bid for bid in bids if round(bid.quantity, 4) > 0.0]

        for offer in offers:
            if round(offer.quantity, 4) <= 0.0:
                logger.info("Withholding non-posistive quantity [%.2f] "
                            "offer." % offer.quantity)
                offer.withheld = True

        for bid in bids:
            if round(bid.quantity, 4) <= 0.0:
                logger.info("Withholding non-posistive quantity [%.2f] "
                            "bid." % bid.quantity)
                bid.withheld = True

        # Optionally strip prices beyond limits.
#        if limits.has_key('max_offer'):
#            offers = [of for of in offers if of.price <= limits['max_offer']]
#        if limits.has_key('min_bid'):
#            bids = [bid for bid in bids if bid.price >= limits['min_bid']]

        if limits.has_key("max_offer"):
            for offer in offers:
                if offer.price >= limits["max_offer"]:
                    logger.info("Offer price [%.2f] above limit [%.3f], "
                        "withholding." % (offer.price, limits["max_offer"]))
                    offer.withheld = True

        if limits.has_key("min_bid"):
            for bid in bids:
                if bid.price <= limits["min_bid"]:
                    logger.info("Bid price [%.2f] below limit [%.2f], "
                        "withholding." % (bid.price, limits["min_bid"]))
                    bid.withheld = True

        return offers, bids

#------------------------------------------------------------------------------
#  "_OfferBid" class:
#------------------------------------------------------------------------------

class _OfferBid(object):
    """ Defines a base class for bids to buy or offers to sell a quantity of
        power at a defined price.
    """

    def __init__(self, qty, prc, reactive=False):
        # Quantity of power bidding to be bought.
        self.quantity = qty

        # Maximum price willing to be paid.
        self.price = prc

        # Does the bid concern active or reactive power?
        self.reactive = reactive

        # Output at which the generator was dispatched.
        self.total_quantity = 0.0

        # Nodal marginal price from OPF.
        self.p_lambda = 0.0

        # Is the bid valid?
        self.withheld = False

        # Has the bid been partially or fully accepted?
        self.accepted = False

        # Quantity of bid cleared by the market.
        self.cleared_quantity = 0.0

        # Price at which the bid was cleared.
        self.cleared_price = 0.0


    @property
    def difference(self):
        """ The locationally adjusted offer/bid price, when normalized to an
            arbitrary reference location where lambda is equal to ref_lam, is:

                norm_prc = prc + (ref_lam - lam)

            Then we can define the difference between the normalized offer/bid
            prices and the ref_lam as:

                diff = norm_prc - ref_lam = prc - lam

            This diff represents the gap between the marginal unit (setting
            lambda) and the offer/bid price in question.
        """
        return self.price - self.p_lambda

#------------------------------------------------------------------------------
#  "Offer" class:
#------------------------------------------------------------------------------

class Offer(_OfferBid):
    """ Defines a offer to sell a quantity of power at a defined price.
    """

    def __init__(self, generator, qty, prc, reactive=False):
        """ Initialises a new Offer instance.
        """
        super(Offer, self).__init__(qty, prc, reactive)

        # Generating unit to which the offer applies.
        self.generator = generator

    @property
    def asset_name(self):
        return self.generator.name


#    @property
#    def total_quantity(self):
#        """ Output at which the generator has been dispatched.
#        """
#        self.generator.p

#------------------------------------------------------------------------------
#  "Bid" class:
#------------------------------------------------------------------------------

class Bid(_OfferBid):
    """ Defines a bid to buy a quantity of power at a defined price.
    """

    def __init__(self, vload, qty, prc, reactive=False):
        """ Initialises a new Bid instance.
        """
        super(Bid, self).__init__(qty, prc, reactive)

        # Dispatchable load to which the bid applies.
        self.vload = vload

    @property
    def asset_name(self):
        return self.vload.name

#    @property
#    def total_quantity(self):
#        """ Output at which the generator has been dispatched.
#        """
#        self.vload.p

#------------------------------------------------------------------------------
#  "PriceLimit" class:
#------------------------------------------------------------------------------

#class PriceLimit(object):
#    """ Defines limits to offer/bid prices.
#    """
#
#    def __init__(self, min_bid=None, max_offer=None, min_cleared_bid=None,
#            max_cleared_offer=None):
#        """ Initialises a new PriceLimit instance.
#        """
#        # Offers above this are withheld.
#        self.max_offer = max_offer
#
#        # Bids below this are withheld.
#        self.min_bid = min_bid
#
#        # Cleared offer prices above this are clipped.
#        self.max_cleared_offer = max_cleared_offer
#
#        # Cleared bid prices below this are clipped.
#        self.min_cleared_bid = min_cleared_bid
#
#        self.q_max_offer = max_offer
#
#        self.q_min_bid = min_bid
#
#        self.q_max_cleared_offer = max_cleared_offer
#
#        self.q_min_cleared_bid = min_cleared_bid

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
