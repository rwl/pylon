#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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

""" Defines a test case for the Pyreto auction.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import unittest

from os.path import dirname, join

from pylon import Case, Bus, Generator, DCOPF
from pylon.readwrite import PickleReader
from pylon.pyreto import SmartMarket, Bid, Offer

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "auction_case.pkl")

#------------------------------------------------------------------------------
#  "SimpleMarketTestCase" class:
#------------------------------------------------------------------------------

class SimpleMarketTestCase(unittest.TestCase):
    """ Defines a simple test case for the Pyreto market.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        bus1 = Bus(p_demand=80.0)
        g1 = Generator(bus1, p_max=60.0, p_min=0.0)
        g2 = Generator(bus1, p_max=100.0, p_min=0.0)
        self.case = Case(buses=[bus1], generators=[g1, g2])


    def test_offers(self):
        """ Test market clearing of offers using results from DC OPF.
        """
        offers = [Offer(self.case.generators[0], 60.0, 20.0),
                  Offer(self.case.generators[1], 100.0, 10.0)]

        SmartMarket(self.case, offers).clear_offers_and_bids()

        places = 2
        self.assertFalse(offers[0].accepted)
        self.assertAlmostEqual(offers[0].cleared_quantity, 0.0, places)
        self.assertAlmostEqual(offers[0].cleared_price, 10.0, places)
        self.assertTrue(offers[1].accepted)
        self.assertAlmostEqual(offers[1].cleared_quantity, 80.0, places)
        self.assertAlmostEqual(offers[1].cleared_price, 10.0, places)


    def test_multi_offers(self):
        """ Test market clearing of multiple offers per generator.
        """
        offers = [Offer(self.case.generators[0], 30.0, 5.0),
                  Offer(self.case.generators[0], 30.0, 6.0),
                  Offer(self.case.generators[1], 40.0, 10.0),
                  Offer(self.case.generators[1], 40.0, 12.0),
                  Offer(self.case.generators[1], 20.0, 20.0)]

        SmartMarket(self.case, offers).clear_offers_and_bids()

        self.assertTrue(offers[0].accepted)
        self.assertTrue(offers[1].accepted)
        self.assertTrue(offers[2].accepted)
        self.assertFalse(offers[3].accepted)
        self.assertFalse(offers[4].accepted)

        places = 2
        self.assertAlmostEqual(offers[0].cleared_quantity, 30.0, places)
        self.assertAlmostEqual(offers[1].cleared_quantity, 30.0, places)
        self.assertAlmostEqual(offers[2].cleared_quantity, 20.0, places)
        self.assertAlmostEqual(offers[0].cleared_price, 10.0, places)
        self.assertAlmostEqual(offers[1].cleared_price, 10.0, places)
        self.assertAlmostEqual(offers[2].cleared_price, 10.0, places)


    def test_first_price(self):
        """ Test marginal offer/bid setting price.
        """
        offers = [Offer(self.case.generators[0], 60.0, 10.0),
                  Offer(self.case.generators[1], 100.0, 20.0)]

        SmartMarket(self.case, offers).clear_offers_and_bids()

        places = 2
        self.assertTrue(offers[0].accepted)
        self.assertAlmostEqual(offers[0].cleared_quantity, 60.0, places)
        self.assertAlmostEqual(offers[0].cleared_price, 20.0, places)
        self.assertTrue(offers[1].accepted)
        self.assertAlmostEqual(offers[1].cleared_quantity, 20.0, places)
        self.assertAlmostEqual(offers[1].cleared_price, 20.0, places)


    def test_price_cap(self):
        """ Test price cap.
        """
        offers = [Offer(self.case.generators[0], 60.0, 10.0),
                  Offer(self.case.generators[1], 100.0, 20.0)]

        mkt = SmartMarket(self.case, offers, price_cap=15.0)
        mkt.clear_offers_and_bids()

        self.assertFalse(mkt.success) # Blackout.
        self.assertTrue(offers[1].withheld)
        self.assertFalse(offers[0].accepted)
        self.assertFalse(offers[1].accepted)


    def test_bids(self):
        """ Test clearing offers and bids.
        """
        vl = Generator(self.case.buses[0], p_max=0.0, p_min=-50.0)
        self.case.generators.append(vl)

        offers = [Offer(self.case.generators[0], 60.0, 10.0),
                  Offer(self.case.generators[1], 60.0, 20.0)]

        bids = [Bid(vl, 50.0, 30.0)]

        SmartMarket(self.case, offers, bids).clear_offers_and_bids()

        places = 2
        self.assertTrue(bids[0].accepted)
        self.assertAlmostEqual(bids[0].cleared_quantity, 40.0, places)
        self.assertAlmostEqual(bids[0].cleared_price, 30.0, places)


    def test_settlement(self):
        """ Test dispatch orders.
        """
        self.case.generators[0].c_startup = 1000.0
        self.case.generators[0].c_shutdown = 500.0

        offers = [Offer(self.case.generators[0], 30.0, 5.0),
                  Offer(self.case.generators[0], 30.0, 10.0),
                  Offer(self.case.generators[1], 100.0, 20.0)]

        mkt = SmartMarket(self.case, offers, g_online=[False, True])
        settlement = mkt.clear_offers_and_bids()

        d1 = settlement[self.case.generators[0]]
        places = 2
        self.assertAlmostEqual(d1.f, 150.0 + 300.0 + 400.0, places=1)
        self.assertAlmostEqual(d1.quantity, 60.0, places)
        self.assertAlmostEqual(d1.price, 20.0, places)

#        self.assertAlmostEqual(d1.fixed, 0.0, places)
#        self.assertAlmostEqual(d1.variable, 0.0, places)
#        self.assertAlmostEqual(d1.startup, 1000.0, places)
#        self.assertAlmostEqual(d1.shutdown, 0.0, places)

#------------------------------------------------------------------------------
#  "MarketTestCase" class:
#------------------------------------------------------------------------------

#class MarketTestCase(unittest.TestCase):
#    """ Defines a test case for the Pyreto market.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.case = PickleReader().read(DATA_FILE)
#
#        generators = self.case.generators
#
#        self.offers = [
#            Offer(generators[0], 12.0, 20.0),
#            Offer(generators[0], 24.0, 50.0),
#            Offer(generators[0], 24.0, 60.0),
##            Offer(generators[0], 60.0, 0.0, reactive=True),
#
#            Offer(generators[1], 12.0, 20.0),
#            Offer(generators[1], 24.0, 40.0),
#            Offer(generators[1], 24.0, 70.0),
##            Offer(generators[1], 60.0, 0.0, reactive=True),
#
#            Offer(generators[2], 12.0, 20.0),
#            Offer(generators[2], 24.0, 42.0),
#            Offer(generators[2], 24.0, 80.0),
##            Offer(generators[2], 60.0, 0.0, reactive=True),
#
#            Offer(generators[3], 12.0, 20.0),
#            Offer(generators[3], 24.0, 44.0),
#            Offer(generators[3], 24.0, 90.0),
##            Offer(generators[3], 60.0, 0.0, reactive=True),
#
#            Offer(generators[4], 12.0, 20.0),
#            Offer(generators[4], 24.0, 46.0),
#            Offer(generators[4], 24.0, 75.0),
##            Offer(generators[4], 60.0, 0.0, reactive=True),
#
#            Offer(generators[5], 12.0, 20.0),
#            Offer(generators[5], 24.0, 48.0),
#            Offer(generators[5], 24.0, 60.0),
##            Offer(generators[5], 60.0, 3.0, reactive=True),
#        ]
#
#        self.bids = [
##            Bid(generators[0], 15.0, 0.0, reactive=True),
##            Bid(generators[1], 15.0, 0.0, reactive=True),
##            Bid(generators[5], 15.0, 0.0, reactive=True),
##            Bid(generators[7], 15.0, 0.0, reactive=True),
##            Bid(generators[6], 15.0, 0.0, reactive=True),
##            Bid(generators[3], 15.0, 0.0, reactive=True),
#
#            Bid(generators[6], 10.0, 100.0),
#            Bid(generators[6], 10.0, 70.0),
#            Bid(generators[6], 10.0, 60.0),
##            Bid(generators[6], 15.0, 0.0, reactive=True),
#
#            Bid(generators[7], 10.0, 100.0),
#            Bid(generators[7], 10.0, 50.0),
#            Bid(generators[7], 10.0, 20.0),
###            Bid(generators[7], 12.0, 83.9056, reactive=True),
##            Bid(generators[7], 12.0, 20.0, reactive=True),
#
#            Bid(generators[8], 10.0, 100.0),
#            Bid(generators[8], 10.0, 60.0),
#            Bid(generators[8], 10.0, 50.0),
##            Bid(generators[8], 7.5, 0.0, reactive=True)
#        ]
#
#
#    def test_dc_opf(self):
#        """ Test solving the auction case using DC OPF.
#        """
#        routine = DCOPF(self.case, show_progress=False)
#        success = routine.solve()
#        self.assertTrue(success)
#        self.assertAlmostEqual(routine.f, -517.81, places=2)
#
#
#    def test_dc(self):
#        """ Test market clearing using DC OPF routine.
#        """
#        mkt = SmartMarket(self.case, self.offers, self.bids,
#            loc_adjust='dc', auction_type="first price", price_cap=100.0)
#
#        mkt.clear_offers_and_bids()
#
#        for dispatch in mkt.settlement.values():
#            print dispatch.quantity, dispatch.price
#
##        generators = self.case.generators
#
##        self.assertTrue(success)
##        self.assertAlmostEqual(mkt.routine.f, 2802.19, places=2)
##        self.assertAlmostEqual(generators[0].p, 35.01, places=2)
##        self.assertAlmostEqual(generators[1].p, 36.0, places=1)
##        self.assertAlmostEqual(generators[2].p, 36.0, places=1)
##        self.assertAlmostEqual(generators[3].p, 36.0, places=1)
##        self.assertAlmostEqual(generators[4].p, 36.0, places=1)
##        self.assertAlmostEqual(generators[5].p, 36.0, places=1)
##        self.assertAlmostEqual(generators[6].p, -30.0, places=1)
##        self.assertAlmostEqual(generators[7].p, -11.5, places=1)
##        self.assertAlmostEqual(generators[8].p, -21.87, places=2)


if __name__ == "__main__":
    logger = logging.getLogger()#'pylon.pyreto.smart_market')
    dcopf_logger = logging.getLogger('pylon.dc_opf')
    dcopf_logger.setLevel(logging.INFO)
    y_logger = logging.getLogger('pylon.y')
    y_logger.setLevel(logging.INFO)

    # Remove PyBrain handlers.
    for handler in logger.handlers: logger.removeHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
