#------------------------------------------------------------------------------
# Copyright (C) 2007-2010 Richard Lincoln
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

""" Defines a test case for the Pyreto auction.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import unittest

from os.path import dirname, join

from pylon import Case, Bus, Branch, Generator, REFERENCE, PV, OPF
from pyreto import SmartMarket, Bid, Offer, FIRST_PRICE

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "t_auction_case.pkl")

#------------------------------------------------------------------------------
#  "TwoBusMarketTestCase" class:
#------------------------------------------------------------------------------

#class TwoBusMarketTestCase(unittest.TestCase):
#    """ Defines a simple test case for the Pyreto market.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        bus1 = Bus(type=REFERENCE, p_demand=10.0)
#        bus2 = Bus(type=PV, p_demand=70.0)
#        g2 = Generator(bus1, p_max=100.0, p_min=0.0)
#        g1 = Generator(bus2, p_max=60.0, p_min=0.0)
#        branch1 = Branch(bus1, bus2)
#        self.case = Case(buses=[bus1, bus2],
#                         branches=[branch1],
#                         generators=[g1, g2])
#        self.case.index_buses()
#
#
#    def testHaveQ(self):
#        """ Test reactive offers/bids.
#        """
#        mkt = SmartMarket(self.case)
#        self.assertFalse(mkt._reactiveMarket())
#
#
#    def testOffers(self):
#        """ Test market clearing of offers using results from DC OPF.
#        """
#        offers = [Offer(self.case.generators[0], 60.0, 20.0),
#                  Offer(self.case.generators[1], 100.0, 10.0)]
#
##        print "P:", self.case.generators[0].p
#
#        mkt = SmartMarket(self.case, offers)
#        mkt.run()
#
#        self.assertTrue(mkt._solution["converged"])
#        places = 2
#        self.assertAlmostEqual(mkt._solution["f"], 800.0, 1)
#
#        self.assertFalse(offers[0].accepted)
#        self.assertAlmostEqual(offers[0].clearedQuantity, 0.0, places)
#        self.assertAlmostEqual(offers[0].clearedPrice, 10.0, places)
#
#        self.assertTrue(offers[1].accepted)
#        self.assertAlmostEqual(offers[1].clearedQuantity, 80.0, places)
#        self.assertAlmostEqual(offers[1].clearedPrice, 10.0, places)
#
#
#    def testMultipleOffers(self):
#        """ Test market clearing of multiple offers per generator.
#        """
#        offers = [Offer(self.case.generators[0], 30.0, 5.0),
#                  Offer(self.case.generators[0], 30.0, 6.0),
#                  Offer(self.case.generators[1], 40.0, 10.0),
#                  Offer(self.case.generators[1], 40.0, 12.0),
#                  Offer(self.case.generators[1], 20.0, 20.0)]
#
#        mkt = SmartMarket(self.case, offers)
#        mkt.run()
#
#        self.assertAlmostEqual(mkt._solution["f"], 150. + 180. + 200., 1)
#
#        self.assertTrue(offers[0].accepted)
#        self.assertTrue(offers[1].accepted)
#        self.assertTrue(offers[2].accepted)
#        self.assertFalse(offers[3].accepted)
#        self.assertFalse(offers[4].accepted)
#
#        places = 2
#        self.assertAlmostEqual(offers[0].clearedQuantity, 30.0, places)
#        self.assertAlmostEqual(offers[1].clearedQuantity, 30.0, places)
#        self.assertAlmostEqual(offers[2].clearedQuantity, 20.0, places)
#        self.assertAlmostEqual(offers[0].clearedPrice, 10.0, places)
#        self.assertAlmostEqual(offers[1].clearedPrice, 10.0, places)
#        self.assertAlmostEqual(offers[2].clearedPrice, 10.0, places)
#
#
#    def testFirstPrice(self):
#        """ Test marginal offer/bid setting price.
#        """
#        offers = [Offer(self.case.generators[0], 60.0, 10.0),
#                  Offer(self.case.generators[1], 100.0, 20.0)]
#
#        SmartMarket(self.case, offers).run()
#
#        places = 2
#        self.assertTrue(offers[0].accepted)
#        self.assertAlmostEqual(offers[0].clearedQuantity, 60.0, places)
#        self.assertAlmostEqual(offers[0].clearedPrice, 20.0, places)
#        self.assertTrue(offers[1].accepted)
#        self.assertAlmostEqual(offers[1].clearedQuantity, 20.0, places)
#        self.assertAlmostEqual(offers[1].clearedPrice, 20.0, places)
#
#
#    def testPriceCap(self):
#        """ Test price cap.
#        """
#        offers = [Offer(self.case.generators[0], 60.0, 10.0),
#                  Offer(self.case.generators[1], 100.0, 20.0)]
#
#        mkt = SmartMarket(self.case, offers, priceCap=15.0)
#        mkt.run()
#
#        self.assertFalse(mkt._solution["converged"]) # Blackout.
#        self.assertFalse(self.case.generators[1].online)
#        self.assertFalse(offers[0].withheld)
#        self.assertTrue(offers[1].withheld)
#        self.assertFalse(offers[0].accepted)
#        self.assertFalse(offers[1].accepted)
#
#
#    def testBids(self):
#        """ Test clearing offers and bids.
#        """
#        vl = Generator(self.case.buses[0], p_max=0.0, p_min=-50.0)
#        self.case.generators.append(vl)
#
#        offers = [Offer(self.case.generators[0], 60.0, 10.0),
#                  Offer(self.case.generators[1], 60.0, 20.0)]
#
#        bids = [Bid(vl, 50.0, 30.0)] # Marginal bid.
#
#        SmartMarket(self.case, offers, bids).run()
#
#        places = 2
#        self.assertTrue(bids[0].accepted)
#        self.assertAlmostEqual(bids[0].clearedQuantity, 40.0, places)
#        self.assertAlmostEqual(bids[0].clearedPrice, 30.0, places)

#------------------------------------------------------------------------------
#  "DCMarketTestCase" class:
#------------------------------------------------------------------------------

class DCMarketTestCase(unittest.TestCase):
    """ Defines a test case for the Pyreto market using data from t_runmarket.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(DATA_FILE)

        generators = self.case.generators

        self.offers = [
            Offer(generators[0], 12.0, 20.0),
            Offer(generators[0], 24.0, 50.0),
            Offer(generators[0], 24.0, 60.0),

            Offer(generators[1], 12.0, 20.0),
            Offer(generators[1], 24.0, 40.0),
            Offer(generators[1], 24.0, 70.0),

            Offer(generators[2], 12.0, 20.0),
            Offer(generators[2], 24.0, 42.0),
            Offer(generators[2], 24.0, 80.0),

            Offer(generators[3], 12.0, 20.0),
            Offer(generators[3], 24.0, 44.0),
            Offer(generators[3], 24.0, 90.0),

            Offer(generators[4], 12.0, 20.0),
            Offer(generators[4], 24.0, 46.0),
            Offer(generators[4], 24.0, 75.0),

            Offer(generators[5], 12.0, 20.0),
            Offer(generators[5], 24.0, 48.0),
            Offer(generators[5], 24.0, 60.0)
        ]

        self.bids = [
            Bid(generators[6], 10.0, 100.0),
            Bid(generators[6], 10.0, 70.0),
            Bid(generators[6], 10.0, 60.0),

            Bid(generators[7], 10.0, 100.0),
            Bid(generators[7], 10.0, 50.0),
            Bid(generators[7], 10.0, 20.0),

            Bid(generators[8], 10.0, 100.0),
            Bid(generators[8], 10.0, 60.0),
            Bid(generators[8], 10.0, 50.0)
        ]

        self.mkt = SmartMarket(self.case, self.offers, self.bids,
            locationalAdjustment='dc', auctionType=FIRST_PRICE, priceCap=100.0)


    def testDcOpf(self):
        """ Test solving the auction case using DC OPF.
        """
        solver = OPF(self.case, True, opt={"verbose": False})
        solution = solver.solve()
        self.assertTrue(solution["converged"])
        self.assertAlmostEqual(solution["f"], -517.81, 2)


    def testReset(self):
        """ Test resetting the market.
        """
        self.assertEqual(len(self.mkt.offers), 18)
        self.assertEqual(len(self.mkt.bids), 9)
        self.mkt.reset()
        self.assertEqual(len(self.mkt.offers), 0)
        self.assertEqual(len(self.mkt.bids), 0)


    def testHaveQ(self):
        """ Test reactive offers/bids.
        """
        self.assertFalse(self.mkt._isReactiveMarket())


    def testWithhold(self):
        """ Test witholding of invalid and limited offers/bids.
        """
        invalidOffer = Offer(self.case.generators[0], -10.0, 20.0)
        self.mkt.offers.append(invalidOffer)
        self.mkt.priceCap = 80.0

        self.mkt._withhold_offbids()

        self.assertFalse(self.offers[0].withheld)
        self.assertFalse(self.offers[8].withheld)
        self.assertTrue(self.offers[11].withheld)
        self.assertTrue(invalidOffer.withheld)


    def testOffbidToCase(self):
        """ Test conversion of offers/bids to pwl functions and limit updates.
        """
        self.mkt._withholdOffbids()
        self.mkt._offbidToCase()

        places = 2
        generators = self.case.generators

        for g in generators:
            self.assertTrue(g.online)

        self.assertAlmostEqual(generators[0].p_min, 35.0, places)
        self.assertAlmostEqual(generators[0].p_max, 60.0, places)
        self.assertAlmostEqual(generators[1].p_min, 12.0, places)
        self.assertAlmostEqual(generators[1].p_max, 60.0, places)
        self.assertAlmostEqual(generators[6].p_min, -30.0, places)
        self.assertAlmostEqual(generators[6].p_max, 0.0, places)

        self.assertAlmostEqual(generators[0].p_cost[2][0], 36.0, places)
        self.assertAlmostEqual(generators[0].p_cost[2][1], 1440.0, places)
        self.assertAlmostEqual(generators[0].p_cost[3][0], 60.0, places)
        self.assertAlmostEqual(generators[0].p_cost[3][1], 2880.0, places)

        self.assertAlmostEqual(generators[2].p_cost[2][0], 36.0, places)
        self.assertAlmostEqual(generators[2].p_cost[2][1], 1248.0, places)
        self.assertAlmostEqual(generators[2].p_cost[3][0], 60.0, places)
        self.assertAlmostEqual(generators[2].p_cost[3][1], 3168.0, places)

        self.assertAlmostEqual(generators[6].p_cost[0][0], -30.0, places)
        self.assertAlmostEqual(generators[6].p_cost[0][1], -2300.0, places)
        self.assertAlmostEqual(generators[6].p_cost[1][0], -20.0, places)
        self.assertAlmostEqual(generators[6].p_cost[1][1], -1700.0, places)


        self.assertAlmostEqual(generators[2].q_min, -15.0, places)
        self.assertAlmostEqual(generators[2].q_max, 60.0, places)
        self.assertAlmostEqual(generators[5].q_min, -15.0, places)
        self.assertAlmostEqual(generators[5].q_max, 60.0, places)
        self.assertAlmostEqual(generators[7].q_min, -12.0, places)
        self.assertAlmostEqual(generators[7].q_max, 0.0, places)

#        self.assertAlmostEqual(generators[2].q_cost[0][0], -15.0, places)
#        self.assertAlmostEqual(generators[2].q_cost[0][1], 0.0, places)
#        self.assertAlmostEqual(generators[2].q_cost[2][0], 60.0, places)
#        self.assertAlmostEqual(generators[2].q_cost[2][1], 0.0, places)
#
#        self.assertAlmostEqual(generators[5].q_cost[0][0], -15.0, places)
#        self.assertAlmostEqual(generators[5].q_cost[0][1], 0.0, places)
#        self.assertAlmostEqual(generators[5].q_cost[2][0], 60.0, places)
#        self.assertAlmostEqual(generators[5].q_cost[2][1], 180.0, places)
#
#        self.assertAlmostEqual(generators[7].q_cost[0][0], -12.0, places)
#        self.assertAlmostEqual(generators[7].q_cost[0][1], -240.0, places)
#        self.assertAlmostEqual(generators[7].q_cost[2][0], 0.0, places)
#        self.assertAlmostEqual(generators[7].q_cost[2][1], 0.0, places)


    def testRunOPF(self):
        """ Test generator dispatch points.
        """
        mkt = self.mkt
        mkt._withholdOffbids()
        mkt._offbidToCase()
        success = mkt._runOPF()

        self.assertTrue(success)
        self.assertAlmostEqual(mkt._solution["f"], 2802.19, 2)


    def testNodalMarginalPrices(self):
        """ Test nodal marginal prices from OPF.
        """
        self.mkt._withholdOffbids()
        self.mkt._offbidToCase()
        _ = self.mkt._runOPF()
        gteeOfferPrice, gteeBidPrice = self.mkt._nodalPrices(haveQ=True)

        self.assertTrue(gteeOfferPrice)
        self.assertTrue(gteeBidPrice)

        # Nodal marginal prices.
        for offbid in self.offers + self.bids:
            self.assertAlmostEqual(offbid.lmbda, 50.0, 4)

        places = 0 # TODO: Repeat using PDIPM.
        # Total dispatched quantity for associated generator.
        self.assertAlmostEqual(self.offers[0].totalQuantity, 35.6103, places)
        self.assertAlmostEqual(self.offers[3].totalQuantity, 36.0000, places)
        self.assertAlmostEqual(self.offers[6].totalQuantity, 36.0000, places)

        self.assertAlmostEqual(self.bids[0].totalQuantity, 30.0000, places)
        self.assertAlmostEqual(self.bids[3].totalQuantity, 11.1779, places)
        self.assertAlmostEqual(self.bids[6].totalQuantity, 22.7885, places)


    def testActivePowerAuction(self):
        """ Test auction for clearing offer/bid quantities and prices.
        """
        self.mkt._withholdOffbids()
        self.mkt._offbidToCase()
        _ = self.mkt._runOPF()
        gteeOfferPrice, gteeBidPrice = self.mkt._nodalPrices(haveQ=True)
        self.mkt._runAuction(gteeOfferPrice, gteeBidPrice, haveQ=True)

        places = 4

        for offer in self.offers:
            self.assertAlmostEqual(offer.clearedPrice, 50.0, places)
        for bid in self.bids:
            self.assertAlmostEqual(bid.clearedPrice, 50.0, places)

        offers = self.offers
        self.assertAlmostEqual(offers[0].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[1].clearedQuantity, 23.6103, places=0)
        self.assertAlmostEqual(offers[2].clearedQuantity, 0.0, places)

        self.assertAlmostEqual(offers[3].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[4].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[5].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(offers[6].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[7].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[8].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(offers[9].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[10].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[11].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(offers[12].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[13].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[14].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(offers[15].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[16].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[17].clearedQuantity, 0.00, places)

        bids = self.bids
        self.assertAlmostEqual(bids[0].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[1].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[2].clearedQuantity, 10.0, places)

        self.assertAlmostEqual(bids[3].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[4].clearedQuantity, 1.1779, places)
        self.assertAlmostEqual(bids[5].clearedQuantity, 0.0, places)

        self.assertAlmostEqual(bids[6].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[7].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[8].clearedQuantity, 2.7885, places)


    def test_constrained_market(self):
        """ Test cleared prices & quantities in a constrained system.
        """
        mkt = self.mkt

        # Introduce a constraint on the 16th branch by lowering the rating.
        constrained = self.case.branches[15]
        constrained.rate_a = 30.0

        offers, bids = mkt.run()

        places = 4

        self.assertAlmostEqual(mkt._solution["f"], 2949.10, 2)

        # Cleared offer prices.
        for i in range(0, 3):
            self.assertAlmostEqual(offers[i].cleared_price, 50.0, places)
        for i in range(3, 6):
            self.assertAlmostEqual(offers[i].cleared_price, 41.0442, places)
        for i in range(6, 9):
            self.assertAlmostEqual(offers[i].cleared_price, 52.3954, places)
        for i in range(9, 12):
            self.assertAlmostEqual(offers[i].cleared_price, 50.0, places)
        for i in range(12, 15):
            self.assertAlmostEqual(offers[i].cleared_price, 75.0, places)
        for i in range(15, 18):
            self.assertAlmostEqual(offers[i].cleared_price, 48.0, places)

        # Cleared offer quantities.
        self.assertAlmostEqual(offers[0].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[1].clearedQuantity, 22.9995, places)
        self.assertAlmostEqual(offers[2].clearedQuantity, 0.0, places)

        self.assertAlmostEqual(offers[3].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[4].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[5].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(offers[6].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[7].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[8].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(offers[9].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[10].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[11].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(offers[12].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[13].clearedQuantity, 24.0, places)
        self.assertAlmostEqual(offers[14].clearedQuantity, 5.3963, places)

        self.assertAlmostEqual(offers[15].clearedQuantity, 12.0, places)
        self.assertAlmostEqual(offers[16].clearedQuantity, 18.0, places)
        self.assertAlmostEqual(offers[17].clearedQuantity, 0.00, places)

        # Cleared bid prices.
        for i in range(0, 3):
            self.assertAlmostEqual(bids[i].clearedPrice, 41.8831, places)
        for i in range(3, 6):
            self.assertAlmostEqual(bids[i].clearedPrice, 86.4585, places)
        for i in range(6, 9):
            self.assertAlmostEqual(bids[i].clearedPrice, 50.0000, places)

        # Cleared bid quantities.
        self.assertAlmostEqual(bids[0].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[1].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[2].clearedQuantity, 10.0, places)

        self.assertAlmostEqual(bids[3].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[4].clearedQuantity, 0.00, places)
        self.assertAlmostEqual(bids[5].clearedQuantity, 0.00, places)

        self.assertAlmostEqual(bids[6].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[7].clearedQuantity, 10.0, places)
        self.assertAlmostEqual(bids[8].clearedQuantity, 2.7519, places)

##------------------------------------------------------------------------------
##  "ACMarketTestCase" class:
##------------------------------------------------------------------------------
#
#class ACMarketTestCase(unittest.TestCase):
#    """ Defines a test case for the Pyreto market using data from t_runmarket.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.case = Case.load(DATA_FILE)
#
#        generators = self.case.generators
#
#        self.q_offers = [
#            Offer(generators[0], 60.0, 0.0, True),
#            Offer(generators[1], 60.0, 0.0, True),
#            Offer(generators[2], 60.0, 0.0, True),
#            Offer(generators[3], 60.0, 0.0, True),
#            Offer(generators[4], 60.0, 0.0, True),
#            Offer(generators[5], 60.0, 3.0, True),
#        ]
#
#        self.q_bids = [
#            Bid(generators[0], 15.0, 0.0, True),
#            Bid(generators[1], 15.0, 0.0, True),
#            Bid(generators[2], 15.0, 0.0, True),
#            Bid(generators[3], 15.0, 0.0, True),
#            Bid(generators[4], 15.0, 0.0, True),
#            Bid(generators[5], 15.0, 0.0, True),
#            Bid(generators[6], 15.0, 0.0, True),
##            Bid(generators[7], 12.0, 83.9056, True),
#            Bid(generators[7], 12.0, 20.0, True),
#            Bid(generators[8], 7.5, 0.0, True)
#        ]


if __name__ == "__main__":
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#        format="%(levelname)s: %(message)s")
#
#    logger = logging.getLogger()#"pylon")

    logger = logging.getLogger()#'pyreto.smart_market')
    logging.getLogger('pylon.opf').setLevel(logging.INFO)
    logging.getLogger('pylon.y').setLevel(logging.INFO)

    # Remove PyBrain handlers.
    for handler in logger.handlers: logger.removeHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
