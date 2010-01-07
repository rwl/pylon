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

""" Defines the case test case.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os
from os.path import join, dirname, exists, getsize
import unittest
import tempfile

from pylon import Case, Bus, Branch, Generator
from pylon.readwrite import PickleReader
from pylon.pyreto import Offer, Bid

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

MP_DATA_FILE = join(dirname(__file__), "data", "case6ww.m")
DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "CaseTest" class:
#------------------------------------------------------------------------------

class CaseTest(unittest.TestCase):
    """ Defines a test case for the Pylon case.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)


    def test_reset(self):
        """ Test zeroing of result attributes.
        """
        self.case.buses[5].p_lambda = 1.1
        self.case.generators[2].mu_pmax = 1.1
        self.case.branches[10].p_from = 1.1

        self.case.reset()

        self.assertEqual(self.case.buses[5].p_lambda, 0.0)
        self.assertEqual(self.case.generators[2].mu_pmax, 0.0)
        self.assertEqual(self.case.branches[10].p_from, 0.0)

    #--------------------------------------------------------------------------
    #  Serialisation tests.
    #--------------------------------------------------------------------------

    def test_load_matpower(self):
        """ Test loading a MATPOWER data file.
        """
        case = Case.load(MP_DATA_FILE, "matpower")
        self.assertTrue(isinstance(case, Case))


    def test_infer_matpower_format(self):
        """ Test inference of MATPOWER format from file extension.
        """
        case = Case.load(MP_DATA_FILE) # Format not specified.
        self.assertTrue(isinstance(case, Case))


    def test_save_matpower(self):
        """ Test saving a case in MATPOWER format.
        """
        tmp_fd, tmp_name = tempfile.mkstemp(".m")
        os.close(tmp_fd)
        os.remove(tmp_name)
#        os.unlink(tmp_name)

        self.assertFalse(exists(tmp_name))

        self.case.save(tmp_name)

        self.assertTrue(exists(tmp_name))
        self.assertTrue(getsize(tmp_name) > 0)

    #--------------------------------------------------------------------------
    #  Admittance matrix tests.
    #--------------------------------------------------------------------------

    def test_admittance(self):
        """ Test the values of the admittance matrix.

           4.0063 -11.7479i  -2.0000 + 4.0000i        0            -1.1765 + 4.7059i  -0.8299 + 3.1120i        0
          -2.0000 + 4.0000i   9.3283 -23.1955i  -0.7692 + 3.8462i  -4.0000 + 8.0000i  -1.0000 + 3.0000i  -1.5590 + 4.4543i
                0            -0.7692 + 3.8462i   4.1557 -16.5673i        0            -1.4634 + 3.1707i  -1.9231 + 9.6154i
          -1.1765 + 4.7059i  -4.0000 + 8.0000i        0             6.1765 -14.6359i  -1.0000 + 2.0000i        0
          -0.8299 + 3.1120i  -1.0000 + 3.0000i  -1.4634 + 3.1707i  -1.0000 + 2.0000i   5.2933 -14.1378i  -1.0000 + 3.0000i
                0            -1.5590 + 4.4543i  -1.9231 + 9.6154i        0            -1.0000 + 3.0000i   4.4821 -17.0047i

        """
        Y, _, _ = self.case.Y

        self.assertEqual(Y.size, (6, 6))

        self._validate_diagonal_admittance_values(Y)
        self._validate_off_diagonal_admittance_values(Y)
        self._validate_off_diagonal_equality(Y)


    def _validate_diagonal_admittance_values(self, Y):
        """ Assert that the diagonal values of the admittance matrix are
            equal to those calculated by MATPOWER.
        """
        places = 4

        Y_0_0 = 4.0063-11.7479j
        Y_2_2 = 4.1557-16.5673j
        Y_5_5 = 4.4821-17.0047j

        self.assertAlmostEqual(abs(Y[0, 0]), abs(Y_0_0), places)
        self.assertAlmostEqual(abs(Y[2, 2]), abs(Y_2_2), places)
        self.assertAlmostEqual(abs(Y[5, 5]), abs(Y_5_5), places)


    def _validate_off_diagonal_admittance_values(self, Y):
        """ Assert that the off-diagonal values of the admittance matrix are
            equal to those calculated by MATPOWER.
        """
        places = 4

        Y_0_1 = -2.0000+4.0000j
        Y_2_0 = 0.0000
        Y_4_1 = -1.0000+3.0000j
        Y_2_5 = -1.9231+9.6154j

        self.assertAlmostEqual(abs(Y[0, 1]), abs(Y_0_1), places)
        self.assertAlmostEqual(abs(Y[2, 0]), abs(Y_2_0), places)
        self.assertAlmostEqual(abs(Y[4, 1]), abs(Y_4_1), places)
        self.assertAlmostEqual(abs(Y[2, 5]), abs(Y_2_5), places)


    def _validate_off_diagonal_equality(self, Y):
        """ Validate that elements [i, j] and [j, i] are equal.
        """
        w, h = Y.size

        for i in range(w):
            for j in range(h):
                if (i != j) and (i < j):
                    self.assertEqual(abs(Y[i, j]), abs(Y[j, i]))

    #--------------------------------------------------------------------------
    #  Susceptance matrix tests.
    #--------------------------------------------------------------------------

    def test_susceptance(self):
        """ Test the values of the susceptance matrix.

            B =

               13.3333   -5.0000         0   -5.0000   -3.3333         0
               -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000
                     0   -4.0000   17.8462         0   -3.8462  -10.0000
               -5.0000  -10.0000         0   17.5000   -2.5000         0
               -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333
                     0   -5.0000  -10.0000         0   -3.3333   18.3333

        """
        B, _, _, _ = self.case.Bdc

        self._validate_susceptance_diagonal_values(B)
        self._validate_susceptance_off_diagonal_values(B)
        self._validate_off_diagonal_equality(B)


    def _validate_susceptance_diagonal_values(self, B):
        """ Assert that the susceptance matrix diagonal values are the same as
            those computed by MATPOWER.
        """
        places = 4

        B_0_0 = 13.3333
        B_2_2 = 17.8462
        B_4_4 = 16.3462

        self.assertAlmostEqual(B_0_0, B[0, 0], places)
        self.assertAlmostEqual(B_2_2, B[2, 2], places)
        self.assertAlmostEqual(B_4_4, B[4, 4], places)


    def _validate_susceptance_off_diagonal_values(self, B):
        """ Assert that the susceptance matrix off-diagonal values are the same
            as those computed by MATPOWER.
        """
        places = 4

        B_0_1 = -5.0000
        B_0_4 = -3.3333
        B_5_2 = -10.0000

        self.assertAlmostEqual(B_0_1, B[0, 1], places)
        self.assertAlmostEqual(B_0_4, B[0, 4], places)
        self.assertAlmostEqual(B_5_2, B[5, 2], places)


#    def test_slack_bus(self):
#        """ Test zero or one slack bus.
#        """
#        case = self.case
#
#        def get_slack_buses(case):
#            return [bus for bus in case.buses if bus.slack]
#
#        # Distributed slack bus model.
#        for bus in case.buses:
#            bus.slack = False
#        self.assertEqual(len(get_slack_buses(case)), 0)
#        self.assertEqual(case.slack_model, "distributed")
#
#        # Single slack bus model.
#        case.buses[0].slack = True
#        self.assertEqual(len(get_slack_buses(case)), 1)
#        self.assertEqual(case.slack_model, "single")

#------------------------------------------------------------------------------
#  "BusTest" class:
#------------------------------------------------------------------------------

class BusTest(unittest.TestCase):
    """ Test case for the Bus class.
    """

#    def test_mode(self):
#        """ Test the mode property.
#        """
#        v = Bus()
#
#        # Should a bus be PQ by default?
#        self.assertEqual(v.type, "PQ")
#
#        g = Generator(v, q=1.0, q_max=10.0, q_min=-10.0)
#        v.generators.append(g)
#        self.assertEqual(v.type, "PV")
#
#        g.q = 11.0
#        self.assertEqual(v.type, "PQ")
#
#        v.slack = True
#        self.assertEqual(v.type, "ref")


    def test_surplus(self):
        """ Test the power surplus properties.
        """
        v = Bus(p_demand=80.0, q_demand=35.0)
        g1 = Generator(v, p=100.0, q=50.0)
        g2 = Generator(v, p=30.0, q=10.0)
        case = Case(buses=[v], generators=[g1, g2])

        # Supply
        self.assertEqual(case.p_supply(v), 130.0)
        self.assertEqual(case.q_supply(v), 60.0)

        # Surplus
        self.assertEqual(case.p_surplus(v), 50.0)
        self.assertEqual(case.q_surplus(v), 25.0)

#------------------------------------------------------------------------------
#  "BranchTest" class:
#------------------------------------------------------------------------------

class BranchTest(unittest.TestCase):
    """ Test case for the Branch class.
    """

    def test_bus_indexes(self):
        """ Test the from/to bus index property.
        """
        c = Case(name="c")
        bus1 = Bus(name="Bus 1")
        bus2 = Bus(name="Bus 2")
        bus3 = Bus(name="Bus 3")
        c.buses = [bus1, bus2, bus3]

        # Append to list.
        branch1 = Branch(bus3, bus1)
        c.branches.append(branch1)

        self.assertEqual(c.buses.index(branch1.from_bus), 2)
        self.assertEqual(c.buses.index(branch1.to_bus), 0)

        # Set list.
        branch2 = Branch(bus2, bus3)
        branch3 = Branch(bus2, bus1)
        c.branches = [branch2, branch3]

        self.assertEqual(c.buses.index(branch2.from_bus), 1)
        self.assertEqual(c.buses.index(branch2.to_bus), 2)

        # Move branch.
        branch2.from_bus = bus1
        self.assertEqual(c.buses.index(branch2.from_bus), 0)


#    def test_v_ratio(self):
#        """ Test the voltage ratio property.
#        """
#
#        sb = Bus()
#        tb = Bus()
#        e = Branch(sb, tb)
#
#        sb.v_magnitude = 0.9
#        tb.v_magnitude = 1.1
#
#        self.assertAlmostEqual(e.v_ratio, 0.81818, places=5)


    def test_mode(self):
        """ Test the mode property.
        """
        sb = Bus()
        tb = Bus()

        e = Branch(sb, tb)

        sb.v_magnitude = 1.0
        tb.v_magnitude = 1.0

        self.assertEqual(e.mode, "line")

        sb.v_magnitude = 2.0
        tb.v_magnitude = 0.5

        self.assertEqual(e.mode, "transformer")


    def test_losses(self):
        """ Test the power loss properties.
        """
        e = Branch(Bus(), Bus())
        e.p_from = 100.0
        e.p_to = 90.0

        self.assertAlmostEqual(e.p_losses, 10.0, places=4)

        e.q_from = 30.0
        e.q_to = 10.0

        self.assertAlmostEqual(e.q_losses, 20.0, places=4)

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

        self.assertEqual(g.total_cost(5.0), 10.5)
        self.assertEqual(g.total_cost(6.0), 11.76)


    def test_total_piecewise_linear_cost(self):
        """ Test total cost calculation with piecewise linear cost model.
        """
        p0 = (0.0, 0.0)
        p1 = (40.0, 100.0)
        p2 = (100.0, 400.0)

        g = Generator(Bus(), p_max=100.0, p_min=20.0, p_cost=[p0, p1, p2])

        self.assertAlmostEqual(g.total_cost(30.0), 75.0, places=4)
        self.assertAlmostEqual(g.total_cost(60.0), 200.0, places=4)


    def test_poly_to_pwl(self):
        """ Test cost model conversion from polynomial to piece-wise linear.
        """
        g = Generator(Bus(), p_min=0.0, p_max=80.0,
                      p_cost=(0.02, 2.0, 0.0))

        g.poly_to_pwl(n_points=10)

        self.assertEqual(g.pcost_model, "pwl")
        self.assertEqual(len(g.p_cost), 10)

        self.assertAlmostEqual(g.p_cost[2][0], 17.78, places=2)
        self.assertAlmostEqual(g.p_cost[2][1], 41.88, places=2)

        self.assertAlmostEqual(g.p_cost[6][0], 53.33, places=2)
        self.assertAlmostEqual(g.p_cost[6][1], 163.56, places=2)

        g.p_min = 10.0
        g.poly_to_pwl(n_points=10)

        self.assertEqual(len(g.p_cost), 10)

        self.assertAlmostEqual(g.p_cost[1][0], 10.0, places=2)
        self.assertAlmostEqual(g.p_cost[1][1], 22.0, places=2)

        self.assertAlmostEqual(g.p_cost[9][0], 80.0, places=2)
        self.assertAlmostEqual(g.p_cost[9][1], 288.0, places=2)


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
        g0 = Generator(Bus(), p=10.0, q=0.0, q_max=60.0, q_min=-15.0,
                       p_max=60.0, p_min=10.0, p_cost=g0_points)

        g1_points = [(0.0, 0.0), (12.0, 240.0), (36.0, 1200.0), (60.0, 2400.0)]
        g1 = Generator(Bus(), p=10.0, q=0.0, q_max=60.0, q_min=-15.0,
                       p_max=60.0, p_min=12.0,# c_startup=100.0,
                       p_cost=g1_points)

        g2_points = [(-30.0, 0.0), (-20.0, 1000.0), (-10.0, 2000.0),
                     (0.0, 3000.0)]
        g2 = Generator(Bus(), p=-30.0, q=-15.0, q_max=0.0, q_min=-15.0,
                       p_max=0.0, p_min=-30.0, p_cost=g2_points) # vload

        g3_points = [(0.0, 0.0), (12.0, 240.0), (36.0, 1200.0), (60.0, 2400.0)]
        g3 = Generator(Bus(), p=10.0, q=0.0, q_max=60.0, q_min=-15.0,
                       p_max=60.0, p_min=12.0, p_cost=g3_points)

        g4_points = [(-30.0, 0.0), (-20.0, 1000.0), (-10.0, 2000.0),
                     (0.0, 3000.0)] # vload
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

        for g in all_gens:
            g.offers_to_pwl(offers)
            g.bids_to_pwl(bids)
            g.adjust_limits()

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
        all_gens = self.all_generators
        gens = self.generators

        offers = [Offer(gens[0], 0.0, 10.0),
                  Offer(gens[1], 26.0, 50.0),
                  Offer(gens[2], 27.0, 100.0)]
        bids = []

        for g in all_gens:
            g.offers_to_pwl(offers)
            g.bids_to_pwl(bids)
            g.adjust_limits()

        self.assertFalse(gens[0].online)
        self.assertTrue(gens[1].online)
        self.assertTrue(gens[2].online)


    def test_offers_and_bids(self):
        """ Test active power offers and bids.
        """
        all_gens = self.all_generators
        gens = self.generators
        vloads = self.vloads

        offers = [Offer(gens[0], 25.0, 10.0),
                  Offer(gens[1], 26.0, 50.0),
                  Offer(gens[2], 27.0, 100.0)]

        bids = [Bid(vloads[0], 20.0, 100.0),
                Bid(vloads[1], 28.0, 10.0)]

        for g in all_gens:
            g.offers_to_pwl(offers)
            g.bids_to_pwl(bids)
            g.adjust_limits()

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
        all_gens = self.all_generators
        gens = self.generators
        vloads = self.vloads

        offers = [Offer(gens[0], 10.0, 10.0),

                  Offer(gens[1], 20.0, 25.0),
                  Offer(gens[1], 30.0, 65.0),

                  Offer(gens[2], 25.0, 50.0)]

        bids = [Bid(vloads[0], 20.0, 100.0),
                Bid(vloads[0], 10.0, 60.0),

                Bid(vloads[1], 12.0, 70.0)]

        for g in all_gens:
            g.offers_to_pwl(offers)
            g.bids_to_pwl(bids)
            g.adjust_limits()

        self.assertEqual(len(gens[0].p_cost), 2)
        self.assertEqual(len(gens[1].p_cost), 3)
        self.assertEqual(len(gens[2].p_cost), 2)

        self.assertAlmostEqual(gens[0].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(gens[0].p_cost[0][1], 0.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[0][1], 0.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[0][0], 0.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[0][1], 0.0, places=1)

        self.assertAlmostEqual(gens[0].p_cost[1][0], 10.0, places=1)
        self.assertAlmostEqual(gens[0].p_cost[1][1], 100.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[1][0], 20.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[1][1], 500.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[1][0], 25.0, places=1)
        self.assertAlmostEqual(gens[2].p_cost[1][1], 1250.0, places=1)

        self.assertAlmostEqual(gens[1].p_cost[2][0], 50.0, places=1)
        self.assertAlmostEqual(gens[1].p_cost[2][1], 2450.0, places=1)


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

#------------------------------------------------------------------------------
#  "LoadTest" class:
#------------------------------------------------------------------------------

#class LoadTest(unittest.TestCase):
#    """ Defines a test case for the Load class.
#    """
#
#    def test_profile(self):
#        """ Test profiled active power output.
#        """
#        profile = [100.0, 50.0, 20.0, 90.0]
#
#        load = Load(p_min=10.0, p_max=90.0, p_profile=profile)
#
#        places = 2
#
#        self.assertAlmostEqual(load.p_profiled, 80.0, places)
#        self.assertAlmostEqual(load.p_profiled, 40.0, places)
#        self.assertAlmostEqual(load.p_profiled, 16.0, places)
#        self.assertAlmostEqual(load.p_profiled, 72.0, places)
#        self.assertAlmostEqual(load.p_profiled, 80.0, places)
#
#        # Set new profile.
#        profile2 = [10.0, 20.0]
#        load.p_profile = profile2
#
#        self.assertAlmostEqual(load.p_profiled, 8.0, places)
#        self.assertAlmostEqual(load.p_profiled, 16.0, places)
#        self.assertAlmostEqual(load.p_profiled, 8.0, places)


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
