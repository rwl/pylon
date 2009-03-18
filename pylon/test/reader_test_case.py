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

""" Data file parsing tests. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path

from unittest import TestCase, main

from pylon.network import Network
from pylon.readwrite.matpower_reader import read_matpower
from pylon.readwrite.api import PSSEReader

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

MATPOWER_DATA_FILE = "data/case6ww.m"

PSSE_DATA_FILE = "data/ehv3.raw"

#------------------------------------------------------------------------------
#  "ReaderTest" class:
#------------------------------------------------------------------------------

class ReaderTest(TestCase):
    """ Base class for many reader test cases """

    filter = None

    network = Network

    def _validate_base(self, base_mva):
        """ Validate the Network objects properties """

        n = self.network

        self.assertEqual(n.base_mva, base_mva)


    def _validate_object_numbers(self, **numbers):
        """ Validates the expected number of objects """

        n = self.network

        self.assertEqual(
            len(n.buses), n_buses,
            "%d buses expected, %d found" % (n_buses, len(n.buses))
        )

        self.assertEqual(
            len(n.branches), n_branches,
            "%d branches expected, %d found" % (n_branches, len(n.branches))
        )

        self.assertEqual(
            len(n.all_generators), n_gen,
            "%d generators expected, %d found" % (n_gen, len(n.all_generators))
        )

        self.assertEqual(
            len(n.all_loads), n_loads,
            "%d loads expected, %d found" % (n_loads, len(n.all_loads))
        )


    def _validate_slack_bus(self, slack_idx):
        """ Validates the location and number of slack buses """

        n = self.network

        slack_idxs = [n.buses.index(v) for v in n.buses if v.slack]

        self.assertEqual(slack_idxs, [slack_idx])


    def _validate_generator_connections(self, gbus_idxs):
        """ Validates that generators are connected to the expected buses """

        n = self.network

        for idx in gbus_idxs:
            bus = n.buses[idx]
            self.assertTrue(
                len(bus.generators), "No generators at bus: %s" % bus
            )


    def _validate_branch_connections(self, source_idxs, target_idxs):
        """ Validates that Branch objects are connected to the expected
        source and target buses.

        """

        n = self.network

        for e in n.branches:
            source_idx = n.buses.index(e.source_bus)
            source_expected = source_idxs[n.branches.index(e)]
            self.assertEqual(
                source_idx, source_expected,
                "Source bus %d expected, %d found" %
                (source_expected, source_idx)
            )

            target_idx = n.buses.index(e.target_bus)
            target_expected = target_idxs[n.branches.index(e)]
            self.assertEqual(
                target_idx, target_expected,
                "Target bus %d expected, %d found" %
                (target_expected, target_idx)
            )

#------------------------------------------------------------------------------
#  "MatpowerReaderTest" class:
#------------------------------------------------------------------------------

class MatpowerReaderTest(ReaderTest):

    def test_case6ww(self):
        """ Validate parsing of the case6ww.m file """

        # Parse the file
        self.network = read_matpower(MATPOWER_DATA_FILE)

        self._validate_base(base_mva=100)

        # Network structure validation
        self._validate_object_numbers(
            n_buses=6, n_branches=11, n_gen=3, n_loads=3
        )

        self._validate_slack_bus(slack_idx=0)

        self._validate_generator_connections(gbus_idxs=[0, 1, 2])

        self._validate_branch_connections(
            source_idxs=[0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4],
            target_idxs=[1, 3, 4, 2, 3, 4, 5, 4, 5, 4, 5]
        )

#------------------------------------------------------------------------------
#  "PSSEReaderTest" class:
#------------------------------------------------------------------------------

#class PSSEReaderTest(FilterTestCase):
#
#    def test_ehv3(self):
#        """
#        Validate parsing of the ehv3.raw file translated from the UKGDS
#
#        """
#
#        filter = PSSEReader()
#
#        # Parse the file
#        self.network = filter.parse_file(PSSE_DATA_FILE)
#
#        # Network structure validation
#        self._validate_base(base_mva=100)
#
#        self._validate_object_numbers(
#            n_buses=102,
#            n_branches=142, # 75 lines + 67 transformers = 142 branches
#            n_gen=3,
#            n_loads=26
#        )
#
#        self._validate_slack_bus(slack_idx=0)
#
#        self._validate_generator_connections(gbus_idxs=[0, 1])
#
#        self._validate_branch_connections(
#            source_idxs=[0, 0, 1],
#            target_idxs=[1, 2, 2]
#        )

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging, sys
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    main()

# EOF -------------------------------------------------------------------------
