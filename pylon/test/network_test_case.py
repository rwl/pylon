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

""" Defines the network test case.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from pylon import Network, Bus, Branch, Generator, Load
from pylon.readwrite import MATPOWERReader

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/case6ww.m")

#------------------------------------------------------------------------------
#  "NetworkTest" class:
#------------------------------------------------------------------------------

class NetworkTest(unittest.TestCase):
    """ Defines a test case for the Pylon network.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        reader = MATPOWERReader()
        self.network = reader(DATA_FILE)


    def test_slack_bus(self):
        """ Test zero or one slack bus.
        """
        network = self.network

        def get_slackers(network):
            return [bus for bus in network.buses if bus.slack]

        # Distributed slack bus model.
        for bus in network.buses:
            bus.slack = False
        self.assertEqual(len(get_slackers(network)), 0)
        self.assertEqual(network.slack_model, "distributed")

        # Single slack bus model.
        network.buses[0].slack = True
        self.assertEqual(len(get_slackers(network)), 1)
        self.assertEqual(network.slack_model, "single")

#------------------------------------------------------------------------------
#  "BusTest" class:
#------------------------------------------------------------------------------

class BusTest(unittest.TestCase):
    """ Test case for the Bus class.
    """

    def test_mode(self):
        """ Test the mode property.
        """
        v = Bus()

        # Should a bus be PQ by default?
        self.assertEqual(v.mode, "pq")

        g = Generator(q=1.0, q_max=10.0, q_min=-10.0)
        v.generators.append(g)
        self.assertEqual(v.mode, "pv")

        g.q = 11.0
        self.assertEqual(v.mode, "pq")

        v.slack = True
        self.assertEqual(v.mode, "slack")


    def test_surplus(self):
        """ Test the power surplus properties.
        """
        v = Bus()
        g1 = Generator(p=10.0, q=5.0)
        g2 = Generator(p=3.0, q=1.0)

        # Supply
        v.generators.extend([g1, g2])
        self.assertEqual(v.p_supply, 13.0)
        self.assertEqual(v.q_supply, 6.0)

        # Demand
        v.loads.extend([Load(p=6.0, q=3.0), Load(p=2.0, q=0.5)])
        self.assertEqual(v.p_demand, 8.0)
        self.assertEqual(v.q_demand, 3.5)

        # Surplus
        self.assertEqual(v.p_surplus, 5.0)
        self.assertEqual(v.q_surplus, 2.5)

#------------------------------------------------------------------------------
#  "BranchTest" class:
#------------------------------------------------------------------------------

class BranchTest(unittest.TestCase):
    """ Test case for the Branch class.
    """

    def test_bus_indexes(self):
        """ Test the source/target bus index property.
        """
        n = Network(name="n")
        bus1 = Bus(name="Bus 1")
        bus2 = Bus(name="Bus 2")
        bus3 = Bus(name="Bus 3")
        n.buses = [bus1, bus2, bus3]

        # Append to list.
        branch1 = Branch(bus3, bus1)
        n.branches.append(branch1)

        self.assertEqual(n.buses.index(branch1.source_bus), 2)
        self.assertEqual(n.buses.index(branch1.target_bus), 0)

        # Set list.
        branch2 = Branch(bus2, bus3)
        branch3 = Branch(bus2, bus1)
        n.branches = [branch2, branch3]

        self.assertEqual(n.buses.index(branch2.source_bus), 1)
        self.assertEqual(n.buses.index(branch2.target_bus), 2)

        # Move branch.
        branch2.source_bus = bus1
        self.assertEqual(n.buses.index(branch2.source_bus), 0)


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
        e.p_source = 1.0
        e.p_target = 0.9

        self.assertAlmostEqual(e.p_losses, 0.1, places=4)

        e.q_source = 0.3
        e.q_target = 0.1

        self.assertAlmostEqual(e.q_losses, 0.2, places=4)

#------------------------------------------------------------------------------
#  "GeneratorTest" class:
#------------------------------------------------------------------------------

class GeneratorTest(unittest.TestCase):
    """ Test case for the Generator class.
    """

    def test_total_polynomial_cost(self):
        """ Test total cost calculation with polynomial cost model.
        """
        g = Generator(cost_model="polynomial")

        p_max = 10
        p_min = 2
        c2 = 0.06
        c1 = 0.6
        c0 = 6.0

        g.p_max = p_max
        g.p_min = p_min
        g.cost_coeffs = (c2, c1, c0)

        self.assertEqual(g.total_cost(5.0), 10.5)
        self.assertEqual(g.total_cost(6.0), 11.76)


    def test_total_piecewise_linear_cost(self):
        """ Test total cost calculation with piecewise linear cost model.
        """
        g = Generator(cost_model="piecewise linear")

        p_max = 10.0
        p_min = 2.0
        p0 = (0.0, 0.0)
        p1 = (4.0, 0.6)
        p2 = (10.0, 1.6)

        g.p_max = p_max
        g.p_min = p_min
        g.pwl_points = [p0, p1, p2]

        self.assertAlmostEqual(g.total_cost(3.0), 0.4500, places=4)
        self.assertAlmostEqual(g.total_cost(6.0), 0.9333, places=4)


    def test_poly_to_pwl(self):
        """ Test cost model conversion from polynomial to piece-wise linear.

            0
            0.2
            0.38
            0.55
            0.73
            0.9
            1.08
            1.26
            1.44
            1.61

        """
        g = Generator(p_min=0.0, p_max=0.8, cost_model="polynomial",
                      cost_coeffs=(0.02, 2.0, 0.0))

        g.poly_to_pwl(n_points=10)

        self.assertEqual(g.cost_model, "piecewise linear")
        self.assertEqual(len(g.pwl_points), 10)

        print [p[0] for p in g.pwl_points]
        print [p[1] for p in g.pwl_points]

        g.p_min = 0.1
        g.poly_to_pwl(n_points=10)

        self.assertEqual(len(g.pwl_points), 10)

#------------------------------------------------------------------------------
#  "LoadTest" class:
#------------------------------------------------------------------------------

class LoadTest(unittest.TestCase):
    """ Defines a test case for the Load class.
    """

    def test_profile(self):
        """ Test profiled active power output.
        """
        profile = [100.0, 50.0, 20.0, 90.0]

        load = Load(p_min=0.1, p_max=0.9, p_profile=profile)

        places = 2

        self.assertAlmostEqual(load.p_profiled, 0.80, places)
        self.assertAlmostEqual(load.p_profiled, 0.40, places)
        self.assertAlmostEqual(load.p_profiled, 0.16, places)
        self.assertAlmostEqual(load.p_profiled, 0.72, places)
        self.assertAlmostEqual(load.p_profiled, 0.80, places)

        # Set new profile.
        profile2 = [10.0, 20.0]
        load.p_profile = profile2

        self.assertAlmostEqual(load.p_profiled, 0.08, places)
        self.assertAlmostEqual(load.p_profiled, 0.16, places)
        self.assertAlmostEqual(load.p_profiled, 0.08, places)


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
