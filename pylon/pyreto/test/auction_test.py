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

""" Defines a test case for the Pyreto auction.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import unittest

from os.path import dirname, join

from pylon import DCOPF
from pylon.readwrite import PickleReader
from pylon.pyreto import SmartMarket, Bid, Offer

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "auction_case.pkl")

#------------------------------------------------------------------------------
#  "MarketTestCase" class:
#------------------------------------------------------------------------------

class MarketTestCase(unittest.TestCase):
    """ Defines a test case for the Pyreto market.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)

        generators = self.case.all_generators

#        for gen in generators:
#            print gen.name, gen.is_load, gen.pwl_points

        # NB: Pylon orders the generators according to bus number.
        # Bus No:  1, 2, 3, 4, 5, 6, 7, 8, 9
        # Index:   0, 1, 2, 3, 4, 5, 6, 7, 8
        # MP No:   1, 2, 7, 6, 8, 3, 5, 4, 9

        self.offers = [
            Offer(generators[0], 12.0, 20.0),
            Offer(generators[0], 24.0, 50.0),
            Offer(generators[0], 24.0, 60.0),
#            Offer(generators[0], 60.0, 0.0, reactive=True),

            Offer(generators[1], 12.0, 20.0),
            Offer(generators[1], 24.0, 40.0),
            Offer(generators[1], 24.0, 70.0),
#            Offer(generators[1], 60.0, 0.0, reactive=True),

            Offer(generators[5], 12.0, 20.0),
            Offer(generators[5], 24.0, 42.0),
            Offer(generators[5], 24.0, 80.0),
#            Offer(generators[5], 60.0, 0.0, reactive=True),

            Offer(generators[7], 12.0, 20.0),
            Offer(generators[7], 24.0, 44.0),
            Offer(generators[7], 24.0, 90.0),
#            Offer(generators[7], 60.0, 0.0, reactive=True),

            Offer(generators[6], 12.0, 20.0),
            Offer(generators[6], 24.0, 46.0),
            Offer(generators[6], 24.0, 75.0),
#            Offer(generators[6], 60.0, 0.0, reactive=True),

            Offer(generators[3], 12.0, 20.0),
            Offer(generators[3], 24.0, 48.0),
            Offer(generators[3], 24.0, 60.0),
#            Offer(generators[3], 60.0, 3.0, reactive=True),
        ]

        self.bids = [
#            Bid(generators[0], 15.0, 0.0, reactive=True),
#            Bid(generators[1], 15.0, 0.0, reactive=True),
#            Bid(generators[5], 15.0, 0.0, reactive=True),
#            Bid(generators[7], 15.0, 0.0, reactive=True),
#            Bid(generators[6], 15.0, 0.0, reactive=True),
#            Bid(generators[3], 15.0, 0.0, reactive=True),

            Bid(generators[2], 10.0, 100.0),
            Bid(generators[2], 10.0, 70.0),
            Bid(generators[2], 10.0, 60.0),
#            Bid(generators[2], 15.0, 0.0, reactive=True),

            Bid(generators[4], 10.0, 100.0),
            Bid(generators[4], 10.0, 50.0),
            Bid(generators[4], 10.0, 20.0),
##            Bid(generators[4], 12.0, 83.9056, reactive=True),
#            Bid(generators[4], 12.0, 20.0, reactive=True),

            Bid(generators[8], 10.0, 100.0),
            Bid(generators[8], 10.0, 60.0),
            Bid(generators[8], 10.0, 50.0),
#            Bid(generators[8], 7.5, 0.0, reactive=True)
        ]


    def test_dc_opf(self):
        """ Test solving the auction case using DC OPF.
        """
        routine = DCOPF(self.case, show_progress=False)
        success = routine.solve()
        self.assertTrue(success)
        self.assertAlmostEqual(routine.f, -517.81, places=2)


    def test_dc(self):
        """ Test market clearing using DC OPF routine.
        """
        mkt = SmartMarket(self.case, self.offers, self.bids,
            loc_adjust='dc', auction_type="first price", price_cap=100.0)

        settlement = mkt.clear_offers_and_bids()

#        for dispatch in settlement:
#            print dispatch.quantity, dispatch.price

#        generators = self.case.all_generators

#        self.assertTrue(success)
#        self.assertAlmostEqual(mkt.routine.f, 2802.19, places=2)
#        self.assertAlmostEqual(generators[0].p, 35.01, places=2)
#        self.assertAlmostEqual(generators[1].p, 36.0, places=1)
#        self.assertAlmostEqual(generators[2].p, 36.0, places=1)
#        self.assertAlmostEqual(generators[3].p, 36.0, places=1)
#        self.assertAlmostEqual(generators[4].p, 36.0, places=1)
#        self.assertAlmostEqual(generators[5].p, 36.0, places=1)
#        self.assertAlmostEqual(generators[6].p, -30.0, places=1)
#        self.assertAlmostEqual(generators[7].p, -11.5, places=1)
#        self.assertAlmostEqual(generators[8].p, -21.87, places=2)


if __name__ == "__main__":
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#        format="%(levelname)s: %(message)s")

    logger = logging.getLogger('pylon.pyreto.smart_market')

    # Remove PyBrain handlers.
    for handler in logger.handlers:
        logger.removeHandler(handler)

#    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    unittest.main()

# EOF -------------------------------------------------------------------------
