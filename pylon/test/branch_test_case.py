#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Test case for the Branch class. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from pylon.api import Network, Bus, Branch

#------------------------------------------------------------------------------
#  "BranchTest" class:
#------------------------------------------------------------------------------

class BranchTest(unittest.TestCase):
    """ Test case for the Branch class. """

    def test_bus_indexes(self):
        """ Test the source/target bus index property. """

        n = Network(name="n")
        bus1 = Bus(name="Bus 1")
        bus2 = Bus(name="Bus 2")
        bus3 = Bus(name="Bus 3")
        n.buses = [bus1, bus2, bus3]

        # Append to list.
        branch1 = Branch(bus3, bus1)
        n.branches.append(branch1)

        self.assertEqual(branch1.source_bus_idx, 2)
        self.assertEqual(branch1.target_bus_idx, 0)

        # Set list.
        branch2 = Branch(bus2, bus3)
        branch3 = Branch(bus2, bus1)
        n.branches = [branch2, branch3]

        self.assertEqual(branch2.source_bus_idx, 1)
        self.assertEqual(branch2.target_bus_idx, 2)

        # Move branch.
        branch2.source_bus = bus1
        self.assertEqual(branch2.source_bus_idx, 0)


    def test_v_ratio(self):
        """ Test the voltage ratio property. """

        sb = Bus(v_amplitude=0.9)
        tb = Bus(v_amplitude=1.1)
        e = Branch(sb, tb)

        self.assertAlmostEqual(e.v_ratio, 0.81818, places=5)


    def test_mode(self):
        """ Test the mode property. """

        sb = Bus(v_amplitude=1.0)
        tb = Bus(v_amplitude=1.0)
        e = Branch(sb, tb)

        self.assertEqual(e.mode, "Line")

        sb.v_amplitude = 2.0
        tb.v_amplitude = 0.5

        self.assertEqual(e.mode, "Transformer")


    def test_losses(self):
        """ Test the power loss properties. """

        e = Branch(Bus(), Bus())
        e.p_source = 1.0
        e.p_target = 0.9

        self.assertAlmostEqual(e.p_losses, 0.1, places=4)

        e.q_source = 0.3
        e.q_target = 0.1

        self.assertAlmostEqual(e.q_losses, 0.2, places=4)


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
