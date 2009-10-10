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

from pylon import UDOPF, DCOPF

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
            R. D. Zimmerman, 'extras/smartmarket/smartmkt.m', MATPOWER,
            PSERC (Cornell), version 3.2, www.pserc.cornell.edu/matpower
    """

    def __init__(self, case, offers=None, bids=None, limits=None,
            loc_adjust="dc", auction_type="first price", price_cap=500,
            g_online=None, period=1.0):
        """ Initialises a new SmartMarket instance.
        """
        self.case = case

        # Offers to sell a quantity of power at a particular price.
        if offers:
            self.offers = offers
        else:
            self.offers = []

        # Bids to buy power.
        if bids:
            self.bids = bids
        else:
            self.bids = []

        # Offer/bid limits.
        if limits:
            self.limits = limits
        else:
            self.limits = {}

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
        if g_online:
            self.g_online = g_online
        else:
            self.g_online = [True] * len(case.all_generators)

        # Time duration of the dispatch period in hours.
        self.period = period

        # Constraint violation tolerance.
        self.violation = 5e-6

        # Guarantee that cleared offers are >= offers.
#        self.guarantee_offer_price = True

        # Guarantee that cleared bids are <= bids.
#        self.guarantee_bid_price = True

        # Results of the settlement process. A list of Dispatch objects.
        self.settlement = {}


        # Finish initialising the market.
        self.init()


    def init(self):
        """ Initialises the market.
        """
        pass
#        generators = [g for g in self.case.all_generators if not g.is_load]
#        vloads     = [g for g in self.case.all_generators if g.is_load]
#
#        if not self.offers:
#            # Create offers from the generator cost functions.
#            self.offers = [off for g in generators for off in g.get_offers()]
#
#        if not self.bids:
#            self.bids = [bid for vl in vloads for bid in vl.get_bids()]


    def clear_offers_and_bids(self):
        """ Computes cleared offers and bids.
        """
        t0 = time.time()

        offers = self.offers
        bids = self.bids
        limits = self.limits
        all_generators = self.case.all_generators
        generators = [g for g in all_generators if not g.is_load]
        vloads     = [g for g in all_generators if g.is_load]

        # Manage reactive power offers/bids.
        self._reactive_power_market(offers, bids)

        # Withhold offers/bids outwith optional price limits.
        self._enforce_limits(offers, bids, limits)

        self._setup_opf(generators, vloads, offers, bids)

        self._run_opf(self.case)

        self._run_auction(self.case, offers, bids)

        self._compute_costs(self.case, offers, bids)

        elapsed = self.elapsed = time.time() - t0
        logger.info("SmartMarket cleared in %.3fs" % elapsed)


    def _reactive_power_market(self, offers, bids):
        """ Returns a flag indicating the existance of offers/bids for reactive
            power.
        """
#        offers, bids = self.offers, self.bids

        if [offbid for offbid in offers + bids if offbid.reactive]:
            have_q = self.have_q = True
            raise NotImplementedError, "Combined active/reactive power " \
                "market not yet implemented."
        else:
            have_q = self.have_q = False

#        if have_q and vloads and self.auction_type not in ["discriminative",
#                                                           "lao",
#                                                           "first price"]:
#            logger.error("Combined active/reactive power markets with "
#                "constant power factor dispatchable loads are only "
#                "implemented for 'discriminative', 'lao' and 'first price' "
#                "auction types.")

        return have_q


    def _enforce_limits(self, offers, bids, limits):
        """ Returns a tuple of lists of offers and bids with their withheld
            flags set if they represent invalid (<= 0.0) quantities or have
            prices outwith the set limits.
        """
        limits = self.limits

        if not limits.has_key('max_offer'):
            # Eliminates offers (but not bids) above 'price_cap'.
            limits['max_offer'] = self.price_cap
        if not limits.has_key('max_cleared_offer'):
            limits['max_cleared_offer'] = self.price_cap

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
                if offer.price > limits["max_offer"]:
                    logger.info("Offer price [%.2f] above limit [%.3f], "
                        "withholding." % (offer.price, limits["max_offer"]))
                    offer.withheld = True

        if limits.has_key("min_bid"):
            for bid in bids:
                if bid.price < limits["min_bid"]:
                    logger.info("Bid price [%.2f] below limit [%.2f], "
                        "withholding." % (bid.price, limits["min_bid"]))
                    bid.withheld = True

        return offers, bids


    def _setup_opf(self, generators, vloads, offers, bids):
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

        return generators, vloads


    def _run_opf(self, case):
        """ Solves the optimisation problem.
        """
#        routine = self.routine = UDOPF(dc=self.loc_adjust == "dc")
        routine = self.routine = DCOPF(show_progress=False)
        success = self.success = routine(case)

        return success


    def _run_auction(self, case, offers, bids):
        """ Clears an auction to determine the quantity and price for each
            offer/bid.
        """
        if self.success:
            # Guarantee that cleared offers are >= offers.
            guarantee_offer_price = True
            guarantee_bid_price = True

            for offer in offers:
                # Locate the bus to which the offer's generator is connected.
                for bus in case.buses:
                    if offer.generator in bus.generators:
                        break # Go with the first one found.
                else:
                    logger.error("Generator bus not found.")

                # Get nodal marginal price from OPF results.
                offer.p_lambda = bus.p_lambda
                offer.total_quantity = offer.generator.p

            for bid in bids:
                # Locate the bus to which the dispatchable load is connected.
                for bus in case.buses:
                    if bid.vload in bus.generators:
                        break
                else:
                    logger.error("Dispatchable load bus not found.")

                if self.have_q:
                    # Use unbundled lambdas.
                    bid.p_lambda = bus.p_lambda
                    # Allow cleared bids to be above bid price.
                    guarantee_bid_price = False
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


            # Clear offer/bid quantities and prices.
            Auction(case, offers, bids,
                guarantee_offer_price, guarantee_bid_price,
                self.limits).clear_offers_and_bids(self.auction_type)

        else:
            logger.error("Non-convergent UOPF.")

#            quantity = 0.0
#            if limits.has_key("max_offer"):
#                price = limits["max_offer"]
#            else:
#                price = 0.0

            for offbid in offers + bids:
                offbid.cleared_quantity = offbid.cleared_price = 0.0


    def _compute_costs(self, case, offers, bids):
        """ Returns a map of generators to their dispatch info, which details
            the units revenue and associated costs.
        """
        t = self.period
        settlement = self.settlement = {}

        for i, g in enumerate(case.all_generators):
            g_offbids = [ob for ob in offers + bids if ob.generator == g]

            if not g_offbids: continue

            quantity = g.p

            totclrqty = sum([offer.cleared_quantity for offer in g_offbids])
            if totclrqty == 0.0:
                price = totclrqty
            else:
                price = sum([of.cleared_quantity * of.cleared_price / totclrqty
                             for of in g_offbids])

            # Compute costs in $ (not $/hr).
            fixed_cost = t * g.total_cost(0.0)

            variable_cost = (t * g.p_cost) - fixed_cost

            if not self.g_online[i] and g.online:
                startup_cost = g.total_cost(g.c_startup)
                shutdown_cost = 0.0

            elif self.g_online[i] and not g.online:
                startup_cost = 0.0
                shutdown_cost = g.total_cost(g.c_shutdown)

            else:
                startup_cost = 0.0
                shutdown_cost = 0.0

            d = Dispatch(g, t, self.routine.f, quantity, price, fixed_cost,
                         variable_cost, startup_cost, shutdown_cost)

            settlement[g] = d

        return settlement

#------------------------------------------------------------------------------
#  "Auction" class:
#------------------------------------------------------------------------------

class Auction(object):
    """ Defines a power auction for clearing offers/bids, where the pricing is
        adjusted for network losses and binding constraints.

        References:
            R. D. Zimmerman, 'extras/smartmarket/auction.m', MATPOWER,
            PSERC (Cornell), version 3.2, www.pserc.cornell.edu/matpower
    """

    def __init__(self, case, offers, bids, guarantee_offer_price,
                 guarantee_bid_price, limits):
        """ Initialises an new Auction instance.
        """
        self.case = case

        # Offers to produce a quantity of energy at a specified price.
        self.offers = offers

        # Bids to buy a quantity of energy at a specified price.
        self.bids = bids

        # Guarantee that cleared offers are >= offers.
        self.guarantee_offer_price = True

        # Guarantee that cleared bids are <= bids.
        self.guarantee_bid_price = True

        # Offer/bid price limits.
        self.limits = limits


    def clear_offers_and_bids(self, auction_type):
        """ Clears a set of bids and offers.
        """
        offers, bids = self.offers, self.bids
        generators = [g for g in self.case.all_generators if not g.is_load]
        vloads     = [g for g in self.case.all_generators if g.is_load]

        self._clear_quantities(generators, vloads, offers, bids)
        self._compute_shift_values(offers, bids)
        self._clear_prices(offers, bids, auction_type)
        self._clip_prices(generators, vloads, offers, bids, auction_type)

        return offers, bids


    def _clear_quantities(self, generators, vloads, offers, bids):
        """ Computes the cleared quantities for each offer/bid according to
            the dispatched output from the OPF solution.
        """
        for g in generators:
            self._clear_quantity(offers, g)

        for vl in vloads:
            self._clear_quantity(bids, vl)


    def _compute_shift_values(self, offers, bids):
        """ Compute shift values to add to lam to get desired pricing.
        """
        accepted = [of for of in offers if of.accepted]
        rejected = [of for of in offers if not of.accepted]

        # Sort according to the difference between the offer price and the
        # reference nodal marginal price in ascending order.
        accepted.sort(key=lambda x: x.difference)
        rejected.sort(key=lambda x: x.difference)

        # lao + lambda is equal to the last accepted offer.
        lao = self.lao = accepted[-1] if accepted else None
        # fro + lambda is equal to the first rejected offer.
        fro = self.fro = rejected[0] if rejected else None

        if lao is not None:
            logger.info("LAO: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (lao.generator.name, lao.quantity,
                         lao.cleared_quantity, lao.price))
        elif offers:
            logger.info("No accepted offers.")

        if fro is not None:
            logger.info("FRO: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (fro.generator.name, fro.quantity,
                         fro.cleared_quantity, fro.price))
        elif offers:
            logger.info("No rejected offers.")


        # Determine last accepted bid and first rejected bid.
        accepted_bids = [bid for bid in bids if bid.accepted]
        accepted_bids.sort(key=lambda bid: bid.difference, reverse=True)

        rejected_bids = [bid for bid in bids if not bid.accepted]
        rejected_bids.sort(key=lambda bid: bid.difference, reverse=True)

        lab = self.lab = accepted_bids[-1] if accepted_bids else None
        frb = self.frb = rejected_bids[0] if rejected_bids else None

        if lab is not None:
            logger.info("LAB: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (lab.generator.name, lab.quantity,
                         lab.cleared_quantity, lab.price))
        elif bids:
            logger.info("No accepted bids.")

        if frb is not None:
            logger.info("FRB: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
                        (frb.generator.name, frb.quantity,
                         frb.cleared_quantity, frb.price))
        elif bids:
            logger.info("No rejected bids.")


    def _clear_prices(self, offers, bids, auction_type):
        """ Cleared offer/bid prices for different auction types.
        """
        lao, fro = self.lao, self.fro
        lab, frb = self.lab, self.frb

        for offbid in offers + bids:

            if auction_type == "discriminative":
                offbid.cleared_price = offbid.price
            elif auction_type == "lao":
                offbid.cleared_price = offbid.p_lambda + lao.price
            elif auction_type == "fro":
                offbid.cleared_price = offbid.p_lambda + fro.price
            elif auction_type == "lab":
                offbid.cleared_price = offbid.p_lambda + lab.price
            elif auction_type == "frb":
                offbid.cleared_price = offbid.p_lambda + frb.price
            elif auction_type == "first price":
                offbid.cleared_price = offbid.p_lambda
            elif auction_type == "second price":
                if abs(lao.price) < 1e-5:
                    clr_prc = offbid.p_lambda + min(fro.price, lab.price)
                    offbid.cleared_price = clr_prc
                else:
                    clr_prc = offbid.p_lambda + max(lao.price, frb.price)
                    offbid.cleared_price = clr_prc
            elif auction_type == "split":
                split_price = (lao.price - lab.price) / 2.0
                offbid.cleared_price = offbid.p_lambda + split_price
            elif auction_type == "dual laob":
                if isinstance(offbid, Offer):
                    offbid.cleared_price = offbid.p_lambda + lao.price
                else:
                    offbid.cleared_price = offbid.p_lambda + lab.price


    def _clip_prices(self, generators, vloads, offers, bids, auction_type):
        """ Clip cleared prices according to guarantees and limits.
        """
        # Guarantee that cleared offer prices are >= offers.
#        if self.guarantee_offer_price:
#            for offer in offers:
#                if offer.cleared_price < offer.price:
#                    offer.cleared_price = offer.price

        # Guarantee that cleared bid prices are <= bids.
#        if self.guarantee_bid_price:
#            for bid in bids:
#                if bid.cleared_price > bid.price:
#                    bid.cleared_price = bid.price

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

        # Make prices uniform across all offers/bids for each generator after
        # clipping (except for discrim auction) since clipping may only affect
        # a single block of a multi-block generator.
        if auction_type != "discriminative":
            for g in generators + vloads:
                g_offers = [of for of in offers if of.generator == g]
                if g_offers:
                    uniform_price = max([of.price for of in g_offers])
                    for of in g_offers:
                        of.price = uniform_price

                g_bids = [bid for bid in bids if bid.vload == g]
                if g_bids:
                    uniform_price = min([bid.price for bid in g_bids])
                    for bid in g_bids:
                        bid.price = uniform_price

        # Return offers and bids with cleared quantities and prices.
        return offers, bids


    def _clear_quantity(self, offbids, gen):
        """ Computes the cleared bid quantity from total dispatched quantity.
        """
        # Filter out offers/bids not applicable to the generator in question.
        if gen.is_load:
            offbids = [offer for offer in offbids if offer.vload == gen]
        else:
            offbids = [offer for offer in offbids if offer.generator == gen]

        # Offers/bids within valid price limits (not withheld).
        valid = [ob for ob in offbids if not ob.withheld]

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

            if accepted > 0.0:
                ob.accepted = True
            else:
                ob.accepted = False

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

#------------------------------------------------------------------------------
#  "Dispatch" class:
#------------------------------------------------------------------------------

class Dispatch(object):
    """ Defines a container for results from the SmartMarket.
    """

    def __init__(self, generator, period, f, quantity, price, fixed, variable,
                 startup, shutdown):
        """ Initialises a new Dispatch instance.
        """
        # Generator to which the dispatch applies.
        self.generator = generator

        # Time duration of the dispatch period in hours.
        self.period = period

        # Objective function value (total system cost).
        self.f = f

        # Output level at which the generator has been despatched.
        self.quantity = quantity

        # Value at which the generator's output has been priced.
        self.price = price

        # Cost for the generator at zero output.
        self.fixed = fixed

        # Cost for the generator at the dispatched output level minus any fixed
        # costs.
        self.variable = variable

        # Cost incurred due to starting up the generator.
        self.startup = startup

        # Cost incurred due to shutting down the generator.
        self.shutdown = shutdown

        # Penalty costs incurred. Not currently used.
        self.penalty = 0.0

    @property
    def revenue(self):
        """ Returns the value in dollars of producing the dispatched quantity
            at the cleared price over the period of the auction.
        """
        return self.quantity * self.price * self.period

    @property
    def total_cost(self):
        """ Returns the sum of the fixed, variable, startup and shutdown costs,
            plus any incurred penalties.
        """
        return sum([self.fixed, self.variable, self.startup, self.shutdown,
                    self.penalty])

    @property
    def earnings(self):
        """ Returns the revenue minus incurred costs.
        """
        return self.revenue - self.total_cost

# EOF -------------------------------------------------------------------------
