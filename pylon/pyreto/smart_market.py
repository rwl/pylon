#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

from pylon import UDOPF, DCOPF, OPF #@UnusedImport

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DISCRIMINATIVE = "discriminative"
LAO = "lao"
FRO = "fro"
LAB = "lab"
FRB = "frb"
FIRST_PRICE = "first price"
SECOND_PRICE = "second price"
SPLIT = "split"
DUAL_LAOB = "dual laob"

#------------------------------------------------------------------------------
#  "SmartMarket" class:
#------------------------------------------------------------------------------

class SmartMarket(object):
    """ Computes the new generation and price schedules based on the offers
        submitted.

        References:
            R. D. Zimmerman, 'extras/smartmarket/smartmkt.m', MATPOWER,
            PSERC (Cornell), version 3.2, www.pserc.cornell.edu/matpower
    """

    def __init__(self, case, offers=None, bids=None, limits=None,
                 loc_adjust="dc", auction_type=FIRST_PRICE,
                 price_cap=100.0, period=1.0, decommit=False):
        """ Initialises a new SmartMarket instance.
        """
        self.case = case

        # Offers to sell a quantity of power at a particular price.
        self.offers = offers if offers is not None else []

        # Bids to buy power.
        self.bids = bids if bids is not None else []

        # Offer/bid limits.
        self.limits = limits if limits is not None else {}

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

        # A list of the commitment status of each generator from the
        # previous period (for computing startup/shutdown costs).
#        if g_online:
#            self.g_online = g_online
#        else:
#            self.g_online = [True] * len(case.generators)

        # Time duration of the dispatch period in hours.
        self.period = period

        # Constraint violation tolerance.
        self.violation = 5e-6

        # Guarantee that cleared offers are >= offers.
#        self.guarantee_offer_price = True

        # Guarantee that cleared bids are <= bids.
#        self.guarantee_bid_price = True

        # Should the unit decommitment algorithm be used?
        self.decommit = decommit

        # Solver solution dictionary.
        self._solution = {}


    def reset(self):
        """ Resets the market.
        """
        self.offers = []
        self.bids = []


    def run(self):
        """ Computes cleared offers and bids.
        """
        # Start the clock.
        t0 = time.time()

        # Manage reactive power offers/bids.
        haveQ = self._reactive_market()

        # Withhold offers/bids outwith optional price limits.
        self._withhold_offbids()

        # Convert offers/bids to pwl functions and update limits.
        self._offbids_to_case()

        # Compute dispatch points and LMPs using OPF.
        success = self._run_opf()

        if success:
            # Determine quantity and price for each offer/bid.
            self._run_auction(haveQ)
        else:
            for offbid in self.offers + self.bids:
                offbid.cleared_quantity = 0.0
                offbid.cleared_price = 0.0
                offbid.accepted = False

            logger.error("Non-convergent market OPF.")

        logger.info("SmartMarket cleared in %.3fs" % (time.time() - t0))

        return self.offers, self.bids


    def _reactive_market(self):
        """ Returns a flag indicating the existance of offers/bids for reactive
            power.
        """
        vloads = [g for g in self.case.generators if g.is_load]

        if [offbid for offbid in self.offers + self.bids if offbid.reactive]:
            haveQ = True
            logger.warning("Combined active/reactive power " \
                "market not yet implemented.")
        else:
            haveQ = False

        combined_types = [DISCRIMINATIVE, LAO, FIRST_PRICE]

        if haveQ and vloads and self.auction_type not in combined_types:
            logger.error("Combined active/reactive power markets with "
                "constant power factor dispatchable loads are only "
                "implemented for 'discriminative', 'lao' and 'first price' "
                "auction types.")

        return haveQ


    def _withhold_offbids(self):
        """ Withholds offers/bids with invalid (<= 0.0) quantities or prices
            outwith the set limits.
        """
        limits = self.limits

        # Eliminate offers (but not bids) above 'price_cap'.
        if not limits.has_key('max_offer'):
            limits['max_offer'] = self.price_cap

        # Limit cleared offer prices after locational adjustments.
        if not self.limits.has_key('max_cleared_offer'):
            self.limits['max_cleared_offer'] = self.price_cap

        # Withhold invalid offers/bids.
        for offer in self.offers:
            if round(offer.quantity, 4) <= 0.0:
                logger.info("Withholding non-posistive quantity [%.2f] "
                            "offer." % offer.quantity)
                offer.withheld = True

        for bid in self.bids:
            if round(bid.quantity, 4) <= 0.0:
                logger.info("Withholding non-posistive quantity [%.2f] "
                            "bid." % bid.quantity)
                bid.withheld = True

        # Optionally, withhold offers/bids beyond price limits.
        if limits.has_key("max_offer"):
            for offer in self.offers:
                if offer.price > limits["max_offer"]:
                    logger.info("Offer price [%.2f] above limit [%.3f], "
                        "withholding." % (offer.price, limits["max_offer"]))
                    offer.withheld = True

        if limits.has_key("min_bid"):
            for bid in self.bids:
                if bid.price < limits["min_bid"]:
                    logger.info("Bid price [%.2f] below limit [%.2f], "
                        "withholding." % (bid.price, limits["min_bid"]))
                    bid.withheld = True


    def _offbids_to_case(self):
        """ Converts offers/bids to pwl functions and updates limits.
        """
        generators = [g for g in self.case.generators if not g.is_load]
        vloads = [g for g in self.case.generators if g.is_load]

        # Convert offers into piecewise linear segments and update limits.
        for g in generators:
#            print "G:", g.p_min, g.p_max, g.p_cost

            g.offers_to_pwl(self.offers)

#            print "GG:", g.p_min, g.p_max, g.p_cost

        for vl in vloads:
            vl.bids_to_pwl(self.bids)

        # Move p_min and p_max limits out slightly to avoid problems with
        # lambdas caused by rounding errors when corner point of cost function
        # lies at exactly p_min or p_max.
        for g in generators: # Skip dispatchable loads.
            g.p_min -= 100 * self.violation
            g.p_max += 100 * self.violation


    def _run_opf(self):
        """ Computes dispatch points and LMPs using OPF.
        """
        if self.decommit:
            solver = UDOPF(self.case, dc=(self.loc_adjust == "dc"))
        elif self.loc_adjust == "dc":
            solver = DCOPF(self.case, show_progress=False)
#            solver = OPF(case, dc=True, show_progress=False)
        else:
            solver = OPF(self.case, show_progress=False)

        solution = self._solution = solver.solve()

        import sys
        self.case.save_rst(sys.stdout)

        success = solution["status"] == "optimal" or \
                  solution["status"] == "unknown"

        return success


    def _run_auction(self, haveQ):
        """ Clears an auction to determine the quantity and price for each
            offer/bid.
        """
        # Guarantee that cleared offers are >= offers.
        gtee_offer_prc = True
        gtee_bid_prc = True

        for offer in self.offers:
            # Get nodal marginal price from OPF results.
            offer.p_lambda = offer.generator.bus.p_lambda
            offer.total_quantity = offer.generator.p
        for bid in self.bids:
            bus = bid.vload.bus
            if not haveQ:
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
                gtee_bid_prc = True
            else:
                # Use unbundled lambdas.
                bid.p_lambda = bus.p_lambda
                # Allow cleared bids to be above bid price.
                gtee_bid_prc = False

            bid.total_quantity = -bid.vload.p

        # Clear offer/bid quantities and prices.
        auction = Auction(self.case, self.offers, self.bids, self.auction_type,
                          gtee_offer_prc, gtee_bid_prc, self.limits)
        auction.run()

#------------------------------------------------------------------------------
#  "Auction" class:
#------------------------------------------------------------------------------

class Auction(object):
    """ Defines a power auction for clearing offers/bids, where pricing is
        adjusted for network losses and binding constraints.

        References:
            R. D. Zimmerman, 'extras/smartmarket/auction.m', MATPOWER,
            PSERC (Cornell), version 3.2, www.pserc.cornell.edu/matpower
    """

    def __init__(self, case, offers, bids, auction_type=FIRST_PRICE,
                 gtee_offer_prc=True, gtee_bid_prc=True, limits=None):
        """ Initialises an new Auction instance.
        """
        self.case = case

        # Offers to produce a quantity of energy at a specified price.
        self.offers = offers

        # Bids to buy a quantity of energy at a specified price.
        self.bids = bids

        # Pricing option.
        self.auction_type = auction_type

        # Guarantee that cleared offers are >= offers.
        self.guarantee_offer_price = gtee_offer_prc

        # Guarantee that cleared bids are <= bids.
        self.guarantee_bid_price = gtee_bid_prc

        # Offer/bid price limits.
        self.limits = limits if limits is not None else {}


    def run(self):
        """ Clears a set of bids and offers.
        """
        # Compute cleared offer/bid quantities from total dispatched quantity.
        self._clear_quantities()

        # Compute shift values to add to lam to get desired pricing.
        lao, fro, lab, frb = self._compute_shift_values()

        # Clear offer/bid prices according to auction type.
        self._clear_prices(lao, fro, lab, frb)

        # Clip cleared prices according to guarantees and limits.
        self._clip_prices()

        return self.offers, self.bids


    def _clear_quantities(self):
        """ Computes the cleared quantities for each offer/bid according to
            the dispatched output from the OPF solution.
        """
        generators = [g for g in self.case.generators if not g.is_load]
        vloads = [g for g in self.case.generators if g.is_load]

        for g in generators:
            self._clear_quantity(self.offers, g)

        for vl in vloads:
            self._clear_quantity(self.bids, vl)


    def _clear_quantity(self, offbids, gen):
        """ Computes the cleared bid quantity from total dispatched quantity.
        """
        # Filter out offers/bids not applicable to the generator in question.
        g_offbids = [offer for offer in offbids if offer.generator == gen]

        # Offers/bids within valid price limits (not withheld).
        valid = [ob for ob in g_offbids if not ob.withheld]

        # Sort offers by price in ascending order and bids in decending order.
        valid.sort(key=lambda ob: ob.price, reverse=[False, True][gen.is_load])

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

            ob.accepted = (accepted > 0.0)

            # Log the event.
            if ob.accepted:
                logger.info("%s [%s, %.3f, %.3f] accepted at %.2f MW." %
                    (ob.__class__.__name__, ob.generator.name, ob.quantity,
                     ob.price, ob.cleared_quantity))
            else:
                logger.info("%s [%s, %.3f, %.3f] rejected." %
                    (ob.__class__.__name__, ob.generator.name, ob.quantity,
                     ob.price))

            # Increment the accepted quantity.
            accepted_qty += ob.quantity


    def _compute_shift_values(self):
        """ Compute shift values to add to lam to get desired pricing.
        """
        accepted = [of for of in self.offers if of.accepted]
        rejected = [of for of in self.offers if not of.accepted]

        # Sort according to the difference between the offer price and the
        # reference nodal marginal price in ascending order.
        accepted.sort(key=lambda x: x.difference)
        rejected.sort(key=lambda x: x.difference)

        # lao + lambda is equal to the last accepted offer.
        lao = accepted[-1] if accepted else None
        # fro + lambda is equal to the first rejected offer.
        fro = rejected[0] if rejected else None

        if lao is not None:
            logger.info("LAO: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (lao.generator.name, lao.quantity,
                         lao.cleared_quantity, lao.price))
        elif self.offers:
            logger.info("No accepted offers.")

        if fro is not None:
            logger.info("FRO: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (fro.generator.name, fro.quantity,
                         fro.cleared_quantity, fro.price))
        elif self.offers:
            logger.info("No rejected offers.")


        # Determine last accepted bid and first rejected bid.
        accepted_bids = [bid for bid in self.bids if bid.accepted]
        accepted_bids.sort(key=lambda bid: bid.difference, reverse=True)

        rejected_bids = [bid for bid in self.bids if not bid.accepted]
        rejected_bids.sort(key=lambda bid: bid.difference, reverse=True)

        lab = self.lab = accepted_bids[-1] if accepted_bids else None
        frb = self.frb = rejected_bids[0] if rejected_bids else None

        if lab is not None:
            logger.info("LAB: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (lab.generator.name, lab.quantity,
                         lab.cleared_quantity, lab.price))
        elif self.bids:
            logger.info("No accepted bids.")

        if frb is not None:
            logger.info("FRB: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (frb.generator.name, frb.quantity,
                         frb.cleared_quantity, frb.price))
        elif self.bids:
            logger.info("No rejected bids.")

        return lao, fro, lab, frb


    def _clear_prices(self, lao, fro, lab, frb):
        """ Cleared offer/bid prices for different auction types.
        """
        for offbid in self.offers + self.bids:

            if self.auction_type == DISCRIMINATIVE:
                offbid.cleared_price = offbid.price
            elif self.auction_type == LAO:
                offbid.cleared_price = offbid.p_lambda + lao.price
            elif self.auction_type == FRO:
                offbid.cleared_price = offbid.p_lambda + fro.price
            elif self.auction_type == LAB:
                offbid.cleared_price = offbid.p_lambda + lab.price
            elif self.auction_type == FRB:
                offbid.cleared_price = offbid.p_lambda + frb.price
            elif self.auction_type == FIRST_PRICE:
                offbid.cleared_price = offbid.p_lambda
            elif self.auction_type == SECOND_PRICE:
                if abs(lao.price) < 1e-5:
                    clr_prc = offbid.p_lambda + min(fro.price, lab.price)
                    offbid.cleared_price = clr_prc
                else:
                    clr_prc = offbid.p_lambda + max(lao.price, frb.price)
                    offbid.cleared_price = clr_prc
            elif self.auction_type == SPLIT:
                split_price = (lao.price - lab.price) / 2.0
                offbid.cleared_price = offbid.p_lambda + split_price
            elif self.auction_type == DUAL_LAOB:
                if isinstance(offbid, Offer):
                    offbid.cleared_price = offbid.p_lambda + lao.price
                else:
                    offbid.cleared_price = offbid.p_lambda + lab.price


    def _clip_prices(self):
        """ Clip cleared prices according to guarantees and limits.
        """
        # Guarantee that cleared offer prices are >= offers.
        if self.guarantee_offer_price:
            for offer in self.offers:
                if offer.cleared_price < offer.price:
                    offer.cleared_price = offer.price

        # Guarantee that cleared bid prices are <= bids.
        if self.guarantee_bid_price:
            for bid in self.bids:
                if bid.cleared_price > bid.price:
                    bid.cleared_price = bid.price

        # Clip cleared offer prices.
        if self.limits.has_key("max_cleared_offer"):
            max_cleared_offer = self.limits["max_cleared_offer"]

            for offer in self.offers:
                if offer.cleared_price > max_cleared_offer:
                    offer.cleared_price = max_cleared_offer

        # Clip cleared bid prices.
        if self.limits.has_key("min_cleared_bid"):
            min_cleared_bid = self.limits["min_cleared_bid"]

            for bid in self.bids:
                if bid.cleared_price < min_cleared_bid:
                    bid.cleared_price = min_cleared_bid

        # Make prices uniform across all offers/bids for each generator after
        # clipping (except for discrim auction) since clipping may only affect
        # a single block of a multi-block generator.
        if self.auction_type != DISCRIMINATIVE:
            for g in self.case.generators:
                g_offers = [of for of in self.offers if of.generator == g]
                if g_offers:
                    uniform_price = max([of.price for of in g_offers])
                    for of in g_offers:
                        of.price = uniform_price

                g_bids = [bid for bid in self.bids if bid.vload == g]
                if g_bids:
                    uniform_price = min([bid.price for bid in g_bids])
                    for bid in g_bids:
                        bid.price = uniform_price

#------------------------------------------------------------------------------
#  "_OfferBid" class:
#------------------------------------------------------------------------------

class _OfferBid(object):
    """ Defines a base class for bids to buy or offers to sell a quantity of
        power at a defined price.
    """

    def __init__(self, generator, qty, prc, reactive=False):
        # Generating unit (dispatchable load) to which the offer (bid) applies.
        self.generator = generator

        # Quantity of power being offered for sale (or bid to be bought).
        self.quantity = qty

        # Minimum (maximum) price for sale (willing to be paid).
        self.price = prc

        # Does the offer/bid concern active or reactive power?
        self.reactive = reactive

        # Output at which the generator was dispatched.
        self.total_quantity = 0.0

        # Nodal marginal price from OPF.
        self.p_lambda = 0.0

        # Is the bid valid?
        self.withheld = False

        # Has the bid been partially or fully accepted?
        self.accepted = False

        # Has the offer/bid passed through the clearing process?
        self.cleared = False

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


    @property
    def revenue(self):
        """ Returns the value in dollars per unit time of producing the cleared
            quantity at the cleared price.
        """
        return self.cleared_quantity * self.cleared_price

#------------------------------------------------------------------------------
#  "Offer" class:
#------------------------------------------------------------------------------

class Offer(_OfferBid):
    """ Defines a offer to sell a quantity of power at a specified price.
    """

    def __init__(self, generator, qty, prc, reactive=False):
        """ Initialises a new Offer instance.
        """
        super(Offer, self).__init__(generator, qty, prc, reactive)

#------------------------------------------------------------------------------
#  "Bid" class:
#------------------------------------------------------------------------------

class Bid(_OfferBid):
    """ Defines a bid to buy a quantity of power at a specified price.
    """

    def __init__(self, vload, qty, prc, reactive=False):
        """ Initialises a new Bid instance.
        """
        super(Bid, self).__init__(vload, qty, prc, reactive)

    @property
    def vload(self):
        """ Dispatchable load to which the bid applies. Synonym for the
            'generator' attribute.
        """
        return self.generator

# EOF -------------------------------------------------------------------------
