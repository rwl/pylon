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

""" Defines generator test cases.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon import Bus, Generator, POLYNOMIAL, PW_LINEAR
from pyreto import Offer, Bid

#------------------------------------------------------------------------------
#  "GeneratorTest" class:
#------------------------------------------------------------------------------

class GeneratorTest(unittest.TestCase):
    """ Test case for the Generator class.
    """

    def test_total_polynomial_cost(self):
        """ Test total cost calculation with polynomial cost model.
        """
        g = Generator(Bus(), p_max=100.0, p_min=20.0,
                      p_cost=(0.06, 0.6, 6.0))

        self.assertEqual(g.pcost_model, POLYNOMIAL)
        self.assertEqual(g.total_cost(5.0), 10.5)
        self.assertEqual(g.total_cost(6.0), 11.76)

        # TODO: Reactive power costs.


    def test_total_piecewise_linear_cost(self):
        """ Test total cost calculation with piecewise linear cost model.
        """
        p0 = (0.0, 0.0)
        p1 = (40.0, 100.0)
        p2 = (100.0, 400.0)

        g = Generator(Bus(), p_max=100.0, p_min=20.0, p_cost=[p0, p1, p2])

        self.assertEqual(g.pcost_model, PW_LINEAR)
        self.assertAlmostEqual(g.total_cost(30.0), 75.0, places=4)
        self.assertAlmostEqual(g.total_cost(60.0), 200.0, places=4)

        # TODO: Reactive power costs.


#    def test_poly_cost(self):
#        """ Test evaluation of polynomial generator costs and derivatives.
#        """
#        g = Generator(Bus(), p_cost=(0.0053, 11.6690, 213.1000))
#
#        f0 = g.poly_cost(val=125.0, der=0)
#        self.assertEqual(f0, 1.755e03)
#
#        f1 = g.poly_cost(val=125.0, der=1)
#        self.assertEqual(f1, 13.0015)


    def test_poly_to_pwl(self):
        """ Test cost model conversion from polynomial to piece-wise linear.
        """
        g = Generator(Bus(), p_min=0.0, p_max=80.0, p_cost=(0.02, 2.0, 0.0))

        g.poly_to_pwl(n_points=10)

        self.assertEqual(g.pcost_model, PW_LINEAR)
        self.assertEqual(len(g.p_cost), 10)

        self.assertAlmostEqual(g.p_cost[2][0], 17.78, places=2)
        self.assertAlmostEqual(g.p_cost[2][1], 41.88, places=2)

        self.assertAlmostEqual(g.p_cost[6][0], 53.33, places=2)
        self.assertAlmostEqual(g.p_cost[6][1], 163.56, places=2)

        g.p_min = 10.0
        g.pcost_model = POLYNOMIAL
        g.p_cost = (0.02, 2.0, 0.0)

        g.poly_to_pwl(n_points=10)

        self.assertEqual(len(g.p_cost), 10)

        self.assertAlmostEqual(g.p_cost[1][0], 10.0, places=2)
        self.assertAlmostEqual(g.p_cost[1][1], 22.0, places=2)

        self.assertAlmostEqual(g.p_cost[9][0], 80.0, places=2)
        self.assertAlmostEqual(g.p_cost[9][1], 288.0, places=2)

        # TODO: Reactive power costs.


    def test_offers(self):
        """ Test conversion of cost function to price/quantity offers.

        case6ww.m
        q =

           50.0000   37.5000   37.5000   37.5000   37.5000
           37.5000   28.1250   28.1250   28.1250   28.1250
           45.0000   33.7500   33.7500   33.7500   33.7500


        p =

           11.9355   12.4019   12.8016   13.2014   13.6011
           10.6664   11.2498   11.7498   12.2499   12.7500
           11.1665   11.7500   12.2502   12.7503   13.2505

        case30pwl.m
        q =

            12    24    24
            12    24    24
            12    24    24
            12    24    24
            12    24    24
            12    24    24


        p =

            12    36    76
            20    44    84
            20    44    84
            12    36    76
            20    44    84
            12    36    76
        """
        places = 4

        g = Generator(Bus(), p_min=50.0, p_max=200.0)
        g.pcost_model="poly"
        g.p_cost=(0.00533, 11.669, 213.1)

        poly_offers = g.get_offers()

        self.assertEqual(len(poly_offers), 5)
        self.assertAlmostEqual(poly_offers[0].quantity, 50.0, places)
        self.assertAlmostEqual(poly_offers[0].price, 11.9355, places)
        self.assertAlmostEqual(poly_offers[3].quantity, 37.5, places)
        self.assertAlmostEqual(poly_offers[3].price, 13.2014, places)


        g = Generator(Bus(), p_min=0.0, p_max=80.0)
        g.pcost_model="pwl"
        g.p_cost=[(0, 0), (12, 144), (36, 1008), (60, 2832)]

        pwl_offers = g.get_offers()
        self.assertEqual(len(pwl_offers), 3)
        self.assertAlmostEqual(pwl_offers[0].quantity, 12.0, places)
        self.assertAlmostEqual(pwl_offers[0].price, 12.0, places)
        self.assertAlmostEqual(pwl_offers[2].quantity, 24.0, places)
        self.assertAlmostEqual(pwl_offers[2].price, 76.0, places)

#------------------------------------------------------------------------------
#  "OfferBidToPWLTest" class:
#------------------------------------------------------------------------------

class OfferBidToPWLTest(unittest.TestCase):
    """ Test case for conversion of bid/offer blocks to a pwl cost function.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        g0_points = [(0.0, 0.0), (12.0, 240.0), (36.0, 1200.0), (60.0, 2400.0)]
        g1_points = [(0.0, 0.0), (12.0, 240.0), (36.0, 1200.0), (60.0, 2400.0)]
        g2_points = [(-30.0, 0.0), (-20.0, 1000.0), (-10., 2000.), (0., 3000.)]
        g3_points = [(0.0, 0.0), (12.0, 240.0), (36.0, 1200.0), (60.0, 2400.0)]
        g4_points = [(-30.0, 0.0), (-20.0, 1000.0), (-10., 2000.), (0., 3000.)]

        g0 = Generator(Bus(), p=10.0, q=0.0, q_max=60.0, q_min=-15.0,
                       p_max=60.0, p_min=10.0, p_cost=g0_points)

        g1 = Generator(Bus(), p=10.0, q=0.0, q_max=60.0, q_min=-15.0,
                       p_max=60.0, p_min=12.0,# c_startup=100.0,
                       p_cost=g1_points)

        g2 = Generator(Bus(), p=-30.0, q=-15.0, q_max=0.0, q_min=-15.0,
                       p_max=0.0, p_min=-30.0, p_cost=g2_points) # vload

        g3 = Generator(Bus(), p=10.0, q=0.0, q_max=60.0, q_min=-15.0,
                       p_max=60.0, p_min=12.0, p_cost=g3_points)

        g4 = Generator(Bus(), p=-30.0, q=7.5, q_max=7.5, q_min=0.0, p_max=0.0,
                       p_min=-30.0, p_cost=g4_points)

        self.all_generators = [g0, g1, g2, g3, g4]
        self.generators = [g for g in self.all_generators if not g.is_load]
        self.vloads     = [g for g in self.all_generators if g.is_load]


    def test_p_only(self):
        """ Test active power offers only.
        """
        all_gens = self.all_generators
        gens = self.generators
        vloads = self.vloads

        offers = [Offer(gens[0], 25.0, 10.0),
                  Offer(gens[1], 26.0, 50.0),
                  Offer(gens[2], 27.0, 100.0)]
        bids = []

        for g in gens:
            g.offers_to_pwl(offers)

        for vl in vloads:
            vl.bids_to_pwl(bids)

        # All dispatchable loads are shutdown as they have no bids.
        self.assertTrue(True not in [vl.online for vl in vloads])
        self.assertTrue(False not in [g.online for g in gens])

        # Price models should be piecewise linear.
        self.assertEqual(gens[0].pcost_model, "pwl")
        self.assertEqual(gens[1].pcost_model, "pwl")
        self.assertEqual(gens[2].pcost_model, "pwl")

        # 'p_max' is adjusted to equal to total quantity offered.
        self.assertAlmostEqual(gens[0].p_max, 25.0, places=1)
        self.assertAlmostEqual(gens[1].p_max, 26.0, places=1)
        self.assertAlmostEqual(gens[2].p_max, 27.0, places=1)

        # One piecewise linear segment per offer.
        self.assertEqual(len(gens[0].p_cost), 2)
        self.assertEqual(len(gens[1].p_cost), 2)
        self.assertEqual(len(gens[2].p_cost), 2)

        # Piecewise linear cost curves must begin at the origin.
        self.assertAlmostEqual(gens[0].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(gens[0].p_cost[0][1], 0.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[0][1], 0.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[0][1], 0.0, places=1)

        self.assertAlmostEqual(gens[0].p_cost[1][0], 25.0, places=1)
        self.assertAlmostEqual(gens[0].p_cost[1][1], 250.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[1][0], 26.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[1][1], 1300.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[1][0], 27.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[1][1], 2700.0, places=1)


    def test_zero_quantity(self):
        """ Test offline for zero quantity offer.
        """
        generators = self.generators

        offers = [Offer(generators[0], 0.0, 10.0),
                  Offer(generators[1], 26.0, 50.0),
                  Offer(generators[2], 27.0, 100.0)]
        bids = []

        for g in generators:
            g.offers_to_pwl(offers)

        for vl in [l for l in generators if l.is_load]:
            vl.bids_to_pwl(bids)

        self.assertFalse(generators[0].online)
        self.assertTrue(generators[1].online)
        self.assertTrue(generators[2].online)


    def test_offers_and_bids(self):
        """ Test active power offers and bids.
        """
        generators = self.generators
        vloads = self.vloads

        offers = [Offer(generators[0], 25.0, 10.0),
                  Offer(generators[1], 26.0, 50.0),
                  Offer(generators[2], 27.0, 100.0)]

        bids = [Bid(vloads[0], 20.0, 100.0),
                Bid(vloads[1], 28.0, 10.0)]

        for g in generators:
            g.offers_to_pwl(offers)

        for vl in vloads:
            vl.bids_to_pwl(bids)

        self.assertAlmostEqual(vloads[0].p_min, -20.0, places=1)
        self.assertAlmostEqual(vloads[0].q_min, -10.0, places=1)
        self.assertAlmostEqual(vloads[0].q_max,   0.0, places=1)

        self.assertAlmostEqual(vloads[1].p_min, -28.0, places=1)
        self.assertAlmostEqual(vloads[1].q_min,   0.0, places=1)
        self.assertAlmostEqual(vloads[1].q_max,   7.0, places=1)

        # One piecewise linear segment per offer.
        self.assertEqual(len(vloads[0].p_cost), 2)
        self.assertEqual(len(vloads[1].p_cost), 2)

        # The last point must begin at the origin.
        self.assertAlmostEqual(vloads[0].p_cost[1][0], 0.0, places=1)
        self.assertAlmostEqual(vloads[0].p_cost[1][1], 0.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[1][0], 0.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[1][1], 0.0, places=1)

        self.assertAlmostEqual(vloads[0].p_cost[0][0], -20.0, places=1)
        self.assertAlmostEqual(vloads[0].p_cost[0][1], -2000.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[0][0], -28.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[0][1], -280.0, places=1)


    def test_multi_block(self):
        """ Test conversion of multiple offer/bid blocks.
        """
        generators = self.generators
        vloads = self.vloads

        offers = [Offer(generators[0], 10.0, 10.0),

                  Offer(generators[1], 20.0, 25.0),
                  Offer(generators[1], 30.0, 65.0),

                  Offer(generators[2], 25.0, 50.0)]

        bids = [Bid(vloads[0], 20.0, 100.0),
                Bid(vloads[0], 10.0, 60.0),

                Bid(vloads[1], 12.0, 70.0)]

        for g in generators:
            g.offers_to_pwl(offers)

        for vl in vloads:
            vl.bids_to_pwl(bids)

        self.assertEqual(len(generators[0].p_cost), 2)
        self.assertEqual(len(generators[1].p_cost), 3)
        self.assertEqual(len(generators[2].p_cost), 2)

        self.assertAlmostEqual(generators[0].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(generators[0].p_cost[0][1], 0.0, places=1)
        self.assertAlmostEqual(generators[1].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(generators[1].p_cost[0][1], 0.0, places=1)
        self.assertAlmostEqual(generators[2].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(generators[2].p_cost[0][1], 0.0, places=1)

        self.assertAlmostEqual(generators[0].p_cost[1][0], 10.0, places=1)
        self.assertAlmostEqual(generators[0].p_cost[1][1], 100.0, places=1)
        self.assertAlmostEqual(generators[1].p_cost[1][0], 20.0, places=1)
        self.assertAlmostEqual(generators[1].p_cost[1][1], 500.0, places=1)
        self.assertAlmostEqual(generators[2].p_cost[1][0], 25.0, places=1)
        self.assertAlmostEqual(generators[2].p_cost[1][1], 1250.0, places=1)

        self.assertAlmostEqual(generators[1].p_cost[2][0], 50.0, places=1)
        self.assertAlmostEqual(generators[1].p_cost[2][1], 2450.0, places=1)


        self.assertEqual(len(vloads[0].p_cost), 3)
        self.assertEqual(len(vloads[1].p_cost), 2)

        self.assertAlmostEqual(vloads[0].p_cost[0][0], -30.0, places=1)
        self.assertAlmostEqual(vloads[0].p_cost[0][1], -2600.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[0][0], -12.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[0][1], -840.0, places=1)

        self.assertAlmostEqual(vloads[0].p_cost[1][0], -20.0, places=1)
        self.assertAlmostEqual(vloads[0].p_cost[1][1], -2000.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[1][0], 0.0, places=1)
        self.assertAlmostEqual(vloads[1].p_cost[1][1], 0.0, places=1)

        self.assertAlmostEqual(vloads[0].p_cost[2][0], 0.0, places=1)
        self.assertAlmostEqual(vloads[0].p_cost[2][1], 0.0, places=1)

    # TODO: Implement test for ignoring withheld offers/bids.

if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
