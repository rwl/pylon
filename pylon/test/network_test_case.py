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

from pylon.api import Network, Bus, Branch, Generator, Load
from pylon.readwrite.api import read_matpower

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

    network = None

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.network = read_matpower(DATA_FILE)


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
        self.assertEqual(network.slack_model, "Distributed")

        # Single slack bus model.
        network.buses[0].slack = True
        self.assertEqual(len(get_slackers(network)), 1)
        self.assertEqual(network.slack_model, "Single")

        # No more than one slack bus.
        network.buses[1].slack = True
        self.assertEqual(len(get_slackers(network)), 1)
        self.assertTrue(network.buses[1].slack)

        # Require generation at the slack bus.
        network.buses[5].slack = True
        self.assertEqual(len(get_slackers(network)), 1)
        self.assertFalse(network.buses[5].slack)
        self.assertTrue(network.buses[1].slack)

if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
