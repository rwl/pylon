#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" Test case for the Bus class. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from unittest import TestCase, main

from pylon.api import Bus, Generator, Load

#------------------------------------------------------------------------------
#  "BusTest" class:
#------------------------------------------------------------------------------

class BusTest(TestCase):
    """ Test case for the Bus class. """


    def test_q_limited(self):
        """ Test the reactive power limit property. """

        v = Bus()
        g1 = Generator(q=1.0, q_max=10.0, q_min=-10.0)
        g2 = Generator(q=1.0, q_max=10.0, q_min=-10.0)
        v.generators.extend([g1, g2])

        self.assertFalse(v.q_limited)

        # Should a bus be Q limited if any one generator is at its limit?
        g2.q = 11.0

        self.assertTrue(v.q_limited)


    def test_mode(self):
        """ Test the mode property. """

        v = Bus()

        # Should a bus be PQ by default?
        self.assertEqual(v.mode, "PQ")

        g = Generator(q=1.0, q_max=10.0, q_min=-10.0)
        v.generators.append(g)
        self.assertEqual(v.mode, "PV")

        g.q = 11.0
        self.assertEqual(v.mode, "PQ")

        v.slack = True
        self.assertEqual(v.mode, "Slack")


    def test_surplus(self):
        """ Test the power surplus properties. """

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

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
