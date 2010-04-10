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

""" Defines forums for trading electric energy.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging

from pylon import UDOPF, OPF #@UnusedImport

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DISCRIMINATIVE = "discriminative"
#LAO = "lao"
#FRO = "fro"
#LAB = "lab"
#FRB = "frb"
FIRST_PRICE = "first price"
#SECOND_PRICE = "second price"
#SPLIT = "split"
#DUAL_LAOB = "dual laob"

#------------------------------------------------------------------------------
#  "SmartMarket" class:
#------------------------------------------------------------------------------

class SmartMarket(object):
    """ Computes the new generation and price schedules based on the offers
        submitted [1].

        [1] R. D. Zimmerman, 'extras/smartmarket/smartmkt.m', MATPOWER,
            PSERC (Cornell), version 3.2, www.pserc.cornell.edu/matpower
    """

    def __init__(self, case, offers=None, bids=None, limits=None,
                 locationalAdjustment="dc", auctionType=FIRST_PRICE,
                 priceCap=100.0, period=1.0, decommit=False):
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
        self.locationalAdjustment = locationalAdjustment

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
        self.auctionType = auctionType

        # Price cap. Offers greater than this are eliminated.
        self.priceCap = priceCap

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


    def getOffbids(self, g):
        """ Returns the offers/bids for the given generator.
        """
        if not g.is_load:
            offbids = [x for x in self.offers if x.generator == g]
        else:
            offbids = [x for x in self.bids if x.vLoad == g]

        return offbids


    def run(self):
        """ Computes cleared offers and bids.
        """
        # Start the clock.
        t0 = time.time()

        # Manage reactive power offers/bids.
        haveQ = self._isReactiveMarket()

        # Withhold offers/bids outwith optional price limits.
        self._withholdOffbids()

        # Convert offers/bids to pwl functions and update limits.
        self._offbidToCase()

        # Compute dispatch points and LMPs using OPF.
        success = self._runOPF()

        if success:
            # Get nodal marginal prices from OPF.
            gteeOfferPrice, gteeBidPrice = self._nodalPrices(haveQ)
            # Determine quantity and price for each offer/bid.
            self._runAuction(gteeOfferPrice, gteeBidPrice, haveQ)

            logger.info("SmartMarket cleared in %.3fs" % (time.time() - t0))
        else:
            for offbid in self.offers + self.bids:
                offbid.clearedQuantity = 0.0
                offbid.clearedPrice = 0.0
                offbid.accepted = False

                offbid.generator.p = 0.0

            logger.error("Non-convergent market OPF. Blackout!")

        return self.offers, self.bids


    def _isReactiveMarket(self):
        """ Returns a flag indicating the existance of offers/bids for reactive
            power.
        """
        vLoads = [g for g in self.case.generators if g.is_load]

        if [offbid for offbid in self.offers + self.bids if offbid.reactive]:
            haveQ = True
            logger.warning("Combined active/reactive power " \
                "market not yet implemented.")
            raise NotImplementedError
        else:
            haveQ = False

        combinedTypes = [DISCRIMINATIVE, FIRST_PRICE]#, LAO]

        if haveQ and vLoads and self.auctionType not in combinedTypes:
            logger.error("Combined active/reactive power markets with "
                "constant power factor dispatchable loads are only "
                "implemented for 'discriminative', 'lao' and 'first price' "
                "auction types.")

        return haveQ


    def _withholdOffbids(self):
        """ Withholds offers/bids with invalid (<= 0.0) quantities or prices
            outwith the set limits.
        """
        limits = self.limits

        # Eliminate offers (but not bids) above 'price_cap'.
        if not limits.has_key('max_offer'):
            limits['max_offer'] = self.priceCap

        # Limit cleared offer prices after locational adjustments.
        if not self.limits.has_key('maxClearedOffer'):
            self.limits['maxClearedOffer'] = self.priceCap

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
        if limits.has_key("maxOffer"):
            for offer in self.offers:
                if offer.price > limits["maxOffer"]:
                    logger.info("Offer price [%.2f] above limit [%.3f], "
                        "withholding." % (offer.price, limits["maxOffer"]))
                    offer.withheld = True

        if limits.has_key("minBid"):
            for bid in self.bids:
                if bid.price < limits["minBid"]:
                    logger.info("Bid price [%.2f] below limit [%.2f], "
                        "withholding." % (bid.price, limits["minBid"]))
                    bid.withheld = True


    def _offbidToCase(self):
        """ Converts offers/bids to pwl functions and updates limits.
        """
        generators = [g for g in self.case.generators if not g.is_load]
        vLoads = [g for g in self.case.generators if g.is_load]

        # Convert offers into piecewise linear segments and update limits.
        for g in generators:
#            print "G: ", g.p_min, g.p_max, g.p_cost, g.pcost_model

            g.offers_to_pwl(self.offers)

#            print "GG:", g.p_min, g.p_max, g.p_cost, g.pcost_model

        for vl in vLoads:
#            print "L: ", vl.p_min, vl.p_max, vl.p_cost

            vl.bids_to_pwl(self.bids)

#            print "VL:", vl.p_min, vl.p_max, g.q_min, g.q_max, vl.p_cost

        # Move p_min and p_max limits out slightly to avoid problems with
        # lambdas caused by rounding errors when corner point of cost function
        # lies at exactly p_min or p_max.
        for g in generators: # Skip dispatchable loads.
            g.p_min -= 100 * self.violation
            g.p_max += 100 * self.violation


    def _runOPF(self):
        """ Computes dispatch points and LMPs using OPF.
        """
        if self.decommit:
            solver = UDOPF(self.case, dc=(self.locationalAdjustment == "dc"))
        elif self.locationalAdjustment == "dc":
            solver = OPF(self.case, dc=True, opt={"verbose": True})
        else:
            solver = OPF(self.case, dc=False, opt={"verbose": True})

        solution = self._solution = solver.solve()

#        for g in self.case.generators:
#            print "G:", g.online, g.p, g.q_min, g.q_max, g.bus.p_lmbda

        return solution["converged"]


    def _nodalPrices(self, haveQ):
        """ Sets the nodal prices associated with each offer/bid.
        """
        # Guarantee that cleared offer prices are >= offered prices.
        gteeOfferPrice = True
        gteeBidPrice = True

        for offer in self.offers:
            if not offer.reactive:
                # Get nodal marginal price from OPF results.
                offer.lmbda = offer.generator.bus.p_lmbda
                offer.totalQuantity = offer.generator.p
            else:
                offer.lmbda = offer.generator.bus.q_lmbda
                offer.totalQuantity = abs(offer.generator.q)
        for bid in self.bids:
            bus = bid.vLoad.bus

            if not bid.reactive:
                # Fudge factor to include price of bundled reactive power.
                if bid.vLoad.q_max == 0.0:
                    pf = bid.vLoad.q_min / bid.vLoad.p_min
                elif bid.vLoad.q_min == 0.0:
                    pf = bid.vLoad.q_max / bid.vLoad.p_min
                else:
                    pf = 0.0

                # Use bundled lambdas. For loads Q = pf * P.
                bid.lmbda = bus.p_lmbda + pf * bus.q_lmbda

                bid.totalQuantity = -bid.vLoad.p
                # Guarantee that cleared bids are <= bids.
                gteeBidPrice = True
            else:
                # Use unbundled lambdas.
                bid.lmbda = bus.q_lmbda

                bid.totalQuantity = abs(bid.vLoad.q)
                # Allow cleared bids to be above bid price.
                gteeBidPrice = False

        return gteeOfferPrice, gteeBidPrice


    def _runAuction(self, gteeOfferPrice, gteeBidPrice, haveQ):
        """ Clears an auction to determine the quantity and price for each
            offer/bid.
        """
        pOffers = [offer for offer in self.offers if not offer.reactive]
        pBids = [bid for bid in self.bids if not bid.reactive]

        # Clear offer/bid quantities and prices.
        auction = Auction(self.case, pOffers, pBids, self.auctionType,
                          gteeOfferPrice, gteeBidPrice, self.limits)
        auction.run()

        # Separate auction for reactive power.
        if haveQ:
            qOffers = [offer for offer in self.offers if offer.reactive]
            qBids = [bid for bid in self.bids if bid.reactive]

            qAuction = Auction(self.case, qOffers, qBids, self.auctionType,
                                gteeOfferPrice, gteeBidPrice, self.limits)
            qAuction.run()

#------------------------------------------------------------------------------
#  "Auction" class:
#------------------------------------------------------------------------------

class Auction(object):
    """ Defines a power auction for clearing offers/bids, where pricing is
        adjusted for network losses and binding constraints [2].

        [2] R. D. Zimmerman, 'extras/smartmarket/auction.m', MATPOWER,
            PSERC (Cornell), version 3.2, www.pserc.cornell.edu/matpower
    """

    def __init__(self, case, offers, bids, auctionType=FIRST_PRICE,
                 gteeOfferPrice=True, gteeBidPrice=True, limits=None):
        """ Initialises an new Auction instance.
        """
        self.case = case

        # Offers to produce a quantity of energy at a specified price.
        self.offers = offers

        # Bids to buy a quantity of energy at a specified price.
        self.bids = bids

        # Pricing option.
        self.auctionType = auctionType

        # Guarantee that cleared offers are >= offers.
        self.guaranteeOfferPrice = gteeOfferPrice

        # Guarantee that cleared bids are <= bids.
        self.guaranteeBidPrice = gteeBidPrice

        # Offer/bid price limits.
        self.limits = limits if limits is not None else {}


    def run(self):
        """ Clears a set of bids and offers.
        """
        # Compute cleared offer/bid quantities from total dispatched quantity.
        self._clearQuantities()

        # Compute shift values to add to lam to get desired pricing.
#        lao, fro, lab, frb = self._first_rejected_last_accepted()

        # Clear offer/bid prices according to auction type.
        self._clearPrices()
#        self._clear_prices(lao, fro, lab, frb)

        # Clip cleared prices according to guarantees and limits.
        self._clipPrices()

        self._logClearances()

        return self.offers, self.bids


    def _clearQuantities(self):
        """ Computes the cleared quantities for each offer/bid according to
            the dispatched output from the OPF solution.
        """
        generators = [g for g in self.case.generators if not g.is_load]
        vLoads = [g for g in self.case.generators if g.is_load]

        for g in generators:
            self._clearQuantity(self.offers, g)

        for vl in vLoads:
            self._clearQuantity(self.bids, vl)


    def _clearQuantity(self, offbids, gen):
        """ Computes the cleared bid quantity from total dispatched quantity.
        """
        # Filter out offers/bids not applicable to the generator in question.
        gOffbids = [offer for offer in offbids if offer.generator == gen]

        # Offers/bids within valid price limits (not withheld).
        valid = [ob for ob in gOffbids if not ob.withheld]

        # Sort offers by price in ascending order and bids in decending order.
        valid.sort(key=lambda ob: ob.price, reverse=[False, True][gen.is_load])

        acceptedQty = 0.0
        for ob in valid:
            # Compute the fraction of the block accepted.
            accepted = (ob.totalQuantity - acceptedQty) / ob.quantity

            # Clip to the range 0-1.
            if accepted > 1.0:
                accepted = 1.0
            elif accepted < 1.0e-05:
                accepted = 0.0

            ob.clearedQuantity = accepted * ob.quantity

            ob.accepted = (accepted > 0.0)

            # Log the event.
#            if ob.accepted:
#                logger.info("%s [%s, %.3f, %.3f] accepted at %.2f MW." %
#                    (ob.__class__.__name__, ob.generator.name, ob.quantity,
#                     ob.price, ob.clearedQuantity))
#            else:
#                logger.info("%s [%s, %.3f, %.3f] rejected." %
#                    (ob.__class__.__name__, ob.generator.name, ob.quantity,
#                     ob.price))

            # Increment the accepted quantity.
            acceptedQty += ob.quantity


#    def _first_rejected_last_accepted(self):
#        """ Compute shift values to add to lam to get desired pricing.
#        """
#        accepted = [of for of in self.offers if of.accepted]
#        rejected = [of for of in self.offers if not of.accepted]
#
#        # Sort according to the difference between the offer price and the
#        # reference nodal marginal price in ascending order.
#        accepted.sort(key=lambda x: x.difference)
#        rejected.sort(key=lambda x: x.difference)
#
#        # lao + lambda is equal to the last accepted offer.
#        lao = accepted[-1] if accepted else None
#        # fro + lambda is equal to the first rejected offer.
#        fro = rejected[0] if rejected else None
#
#        if lao is not None:
#            logger.info("LAO: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
#                        (lao.generator.name, lao.quantity,
#                         lao.clearedQuantity, lao.price))
#        elif self.offers:
#            logger.info("No accepted offers.")
#
#        if fro is not None:
#            logger.info("FRO: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
#                        (fro.generator.name, fro.quantity,
#                         fro.clearedQuantity, fro.price))
#        elif self.offers:
#            logger.info("No rejected offers.")
#
#
#        # Determine last accepted bid and first rejected bid.
#        acceptedBids = [bid for bid in self.bids if bid.accepted]
#        acceptedBids.sort(key=lambda bid: bid.difference, reverse=True)
#
#        rejectedBids = [bid for bid in self.bids if not bid.accepted]
#        rejectedBids.sort(key=lambda bid: bid.difference, reverse=True)
#
#        lab = self.lab = acceptedBids[-1] if accepted_bids else None
#        frb = self.frb = rejectedBids[0] if rejected_bids else None
#
#        if lab is not None:
#            logger.info("LAB: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
#                        (lab.generator.name, lab.quantity,
#                         lab.clearedQuantity, lab.price))
#        elif self.bids:
#            logger.info("No accepted bids.")
#
#        if frb is not None:
#            logger.info("FRB: %s, %.2fMW (%.2fMW), %.2f$/MWh" %
#                        (frb.generator.name, frb.quantity,
#                         frb.clearedQuantity, frb.price))
#        elif self.bids:
#            logger.info("No rejected bids.")
#
#        return lao, fro, lab, frb


    def _clearPrices(self):
        """ Clears prices according to auction type.
        """
        for offbid in self.offers + self.bids:
            if self.auctionType == DISCRIMINATIVE:
                offbid.clearedPrice = offbid.price
            elif self.auctionType == FIRST_PRICE:
                offbid.clearedPrice = offbid.lmbda
            else:
                raise ValueError


#    def _clearPrices(self, lao, fro, lab, frb):
#        """ Cleared offer/bid prices for different auction types.
#        """
#        for offbid in self.offers + self.bids:
#
#            if self.auctionType == DISCRIMINATIVE:
#                offbid.clearedPrice = offbid.price
#            elif self.auctionType == LAO:
#                offbid.clearedPrice = offbid.lmbda + lao.price
#            elif self.auctionType == FRO:
#                offbid.clearedPrice = offbid.lmbda + fro.price
#            elif self.auctionType == LAB:
#                offbid.clearedPrice = offbid.lmbda + lab.price
#            elif self.auctionType == FRB:
#                offbid.clearedPrice = offbid.lmbda + frb.price
#            elif self.auctionType == FIRST_PRICE:
#                offbid.clearedPrice = offbid.lmbda
#            elif self.auctionType == SECOND_PRICE:
#                if abs(lao.price) < 1e-5:
#                    clearedPrice = offbid.lmbda + min(fro.price, lab.price)
#                    offbid.clearedPrice = clearedPrice
#                else:
#                    clearedPrice = offbid.p_lmbda + max(lao.price, frb.price)
#                    offbid.clearedPrice = clearedPrice
#            elif self.auctionType == SPLIT:
#                splitPrice = (lao.price - lab.price) / 2.0
#                offbid.clearedPrice = offbid.lmbda + splitPrice
#            elif self.auctionType == DUAL_LAOB:
#                if isinstance(offbid, Offer):
#                    offbid.clearedPrice = offbid.lmbda + lao.price
#                else:
#                    offbid.clearedPrice = offbid.lmbda + lab.price


    def _clipPrices(self):
        """ Clip cleared prices according to guarantees and limits.
        """
        # Guarantee that cleared offer prices are >= offers.
        if self.guaranteeOfferPrice:
            for offer in self.offers:
                if offer.accepted and offer.clearedPrice < offer.price:
                    offer.clearedPrice = offer.price

        # Guarantee that cleared bid prices are <= bids.
        if self.guaranteeBidPrice:
            for bid in self.bids:
                if bid.accepted and bid.clearedPrice > bid.price:
                    bid.clearedPrice = bid.price

        # Clip cleared offer prices.
        if self.limits.has_key("maxClearedOffer"):
            maxClearedOffer = self.limits["maxClearedOffer"]

            for offer in self.offers:
                if offer.clearedPrice > maxClearedOffer:
                    offer.clearedPrice = maxClearedOffer

        # Clip cleared bid prices.
        if self.limits.has_key("minClearedBid"):
            minClearedBid = self.limits["minClearedBid"]

            for bid in self.bids:
                if bid.clearedPrice < minClearedBid:
                    bid.clearedPrice = minClearedBid

        # Make prices uniform across all offers/bids for each generator after
        # clipping (except for discrim auction) since clipping may only affect
        # a single block of a multi-block generator.
        if self.auctionType != DISCRIMINATIVE:
            for g in self.case.generators:
                gOffers = [of for of in self.offers if of.generator == g]
                if gOffers:
                    uniformPrice = max([of.clearedPrice for of in gOffers])
                    for of in gOffers:
                        of.clearedPrice = uniformPrice

                gBids = [bid for bid in self.bids if bid.vLoad == g]
                if gBids:
                    uniformPrice = min([bid.cleared_price for bid in gBids])
                    for bid in gBids:
                        bid.clearedPrice = uniformPrice


    def _logClearances(self):
        """ Logs offer/bid cleared values.
        """
        for offer in self.offers:
            logger.info("%.2fMW offer cleared at %.2f$/MWh for %s (%.2f)." %
                        (offer.clearedQuantity, offer.clearedPrice,
                         offer.generator.name, offer.revenue))
        for bid in self.bids:
            logger.info("%.2fMW bid cleared at %.2f$/MWh for %s (%.2f)." %
                        (bid.clearedQuantity, bid.clearedPrice,
                         bid.vLoad.name, bid.revenue))

#------------------------------------------------------------------------------
#  "_OfferBid" class:
#------------------------------------------------------------------------------

class _OfferBid(object):
    """ Defines a base class for bids to buy or offers to sell a quantity of
        power at a defined price.
    """

    def __init__(self, generator, qty, prc, noLoadCost=0.0, reactive=False):
        # Generating unit (dispatchable load) to which the offer (bid) applies.
        self.generator = generator

        # Quantity of power being offered for sale (or bid to be bought).
        self.quantity = qty

        # Minimum (maximum) price for sale (willing to be paid).
        self.price = prc

        # Cost for running.
        self.noLoadCost = noLoadCost

        # Does the offer/bid concern active or reactive power?
        self.reactive = reactive

        # Output at which the generator was dispatched.
        self.totalQuantity = 0.0

        # Nodal marginal active/reactive power price.
        self.lmbda = 0.0

        # Is the bid valid?
        self.withheld = False

        # Has the bid been partially or fully accepted?
        self.accepted = False

        # Has the offer/bid passed through the clearing process?
        self.cleared = False

        # Quantity of bid cleared by the market.
        self.clearedQuantity = 0.0

        # Price at which the bid was cleared.
        self.clearedQrice = 0.0


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
        return self.price - self.lmbda


    @property
    def revenue(self):
        """ Returns the value in dollars per unit time of producing the cleared
            quantity at the cleared price.
        """
        return self.clearedQuantity * self.clearedPrice

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

    def __init__(self, vLoad, qty, prc, reactive=False):
        """ Initialises a new Bid instance.
        """
        super(Bid, self).__init__(vLoad, qty, prc, reactive)

    @property
    def vLoad(self):
        """ Dispatchable load to which the bid applies. Synonym for the
            'generator' attribute.
        """
        return self.generator

# EOF -------------------------------------------------------------------------
