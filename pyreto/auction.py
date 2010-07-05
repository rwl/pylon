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

""" Defines a power auction for clearing offers/bids, where pricing is
adjusted for network losses and binding constraints
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

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
#  "Auction" class:
#------------------------------------------------------------------------------

class Auction(object):
    """ Defines a power auction for clearing offers/bids, where pricing is
    adjusted for network losses and binding constraints.

    Based on auction.m from MATPOWER by Ray Zimmerman, developed at PSERC
    Cornell. See U{http://www.pserc.cornell.edu/matpower/} for more info.
    """

    def __init__(self, case, offers, bids, auctionType,
                 gteeOfferPrice=True, gteeBidPrice=True, limits=None):
        """ Initialises an new Auction instance.
        """
        #: Power system case.
        self.case = case

        #: Offers to produce a quantity of energy at a specified price.
        self.offers = offers

        #: Bids to buy a quantity of energy at a specified price.
        self.bids = bids

        #: Pricing option.
        self.auctionType = auctionType

        #: Guarantee that cleared offers are >= offers.
        self.guaranteeOfferPrice = gteeOfferPrice

        #: Guarantee that cleared bids are <= bids.
        self.guaranteeBidPrice = gteeBidPrice

        #: Offer/bid price limits.
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
        """ Computes the cleared quantities for each offer/bid according
        to the dispatched output from the OPF solution.
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

# EOF -------------------------------------------------------------------------
