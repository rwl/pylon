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

from pylon.readwrite import MATPOWERReader
from pylon.pyreto.market import SmartMarket, Bid, Offer

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "auction_case.m")

#------------------------------------------------------------------------------
#  "MarketTestCase" class:
#------------------------------------------------------------------------------

class MarketTestCase(unittest.TestCase):
    """ Defines a test case for the Pyreto market.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.network = MATPOWERReader().read(DATA_FILE)

        generators = self.network.generators

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
            Offer(generators[5], 24.0, 60.0),
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


    def test_dc(self):
        """ Test market clearing using DC OPF routine.
        """
        mkt = SmartMarket(self.network, self.bids, self.offers,
            loc_adjust='dc', auction_type="first price", price_cap=100.0)

        mkt.run()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    unittest.main()

# EOF -------------------------------------------------------------------------
