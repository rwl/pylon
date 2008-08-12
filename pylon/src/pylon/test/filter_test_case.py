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

"""
Parsing data files test cases.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path

from unittest import TestCase, main

from pylon.network import Network

from pylon.filter.filter import Filter

from pylon.filter.matpower import MATPOWERImporter

from pylon.filter.psse import PSSEImporter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

MATPOWER_DATA_FILE = "data/3bus.m"

PSSE_DATA_FILE = "data/ehv3.raw"

#------------------------------------------------------------------------------
#  "FilterTestCase" class:
#------------------------------------------------------------------------------

class FilterTestCase(TestCase):
    """
    Base class for many filter test cases

    """

    filter = Filter

    network = Network

    def _validate_base(self, mva_base):
        """
        Validate the Network objects properties

        """

        n = self.network

        self.assertEqual(n.mva_base, mva_base)


    def _validate_object_numbers(self, n_buses, n_branches, n_gen, n_loads):
        """
        Validates that the Network contains the expected number of objects.

        """

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
            len(n.generators), n_gen,
            "%d generators expected, %d found" % (n_gen, len(n.generators))
        )

        self.assertEqual(
            len(n.loads), n_loads,
            "%d loads expected, %d found" % (n_loads, len(n.loads))
        )


    def _validate_slack_bus(self, slack_idx):
        """
        Validates the location and number of slack buses

        """

        n = self.network

        slack_idxs = [n.buses.index(v) for v in n.buses if v.slack]

        self.assertEqual(slack_idxs, [slack_idx])


    def _validate_generator_connections(self, gbus_idxs):
        """
        Validates that all Generator objects are connected to the
        expected buses.

        """

        n = self.network

        for g in n.generators:
            gbus_idx = n.buses.index(g.bus)
            expected_idx = gbus_idxs[n.generators.index(g)]
            self.assertEqual(
                gbus_idx, expected_idx,
                "Bus %d expected, %d found" % (expected_idx, gbus_idx)
            )


    def _validate_branch_connections(self, source_idxs, target_idxs):
        """
        Validates that all Branch objects are connected to the expected
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
#  "MatpowerFilterTestCase" class:
#------------------------------------------------------------------------------

class MatpowerFilterTestCase(FilterTestCase):

    def test_3bus(self):
        """
        Validate parsing of the 3bus.m file

        """

        filter = MATPOWERImporter()

        # Parse the file
        self.network = filter.parse_file(MATPOWER_DATA_FILE)

        self._validate_base(mva_base=100)

        # Network structure validation
        self._validate_object_numbers(
            n_buses=3,
            n_branches=3,
            n_gen=2,
            n_loads=1
        )

        self._validate_slack_bus(slack_idx=0)

        self._validate_generator_connections(gbus_idxs=[0, 1])

        self._validate_branch_connections(
            source_idxs=[0, 0, 1],
            target_idxs=[1, 2, 2]
        )

#------------------------------------------------------------------------------
#  "PSSEImporterTestCase" class:
#------------------------------------------------------------------------------

class PSSEImporterTestCase(FilterTestCase):

    def test_ehv3(self):
        """
        Validate parsing of the ehv3.raw file translated from the UKGDS

        """

        filter = PSSEImporter()

        # Parse the file
        self.network = filter.parse_file(PSSE_DATA_FILE)

        # Network structure validation
        self._validate_base(mva_base=100)

        self._validate_object_numbers(
            n_buses=102,
            n_branches=142, # 75 lines + 67 transformers = 142 branches
            n_gen=3,
            n_loads=26
        )

        self._validate_slack_bus(slack_idx=0)

        self._validate_generator_connections(gbus_idxs=[0, 1])

        self._validate_branch_connections(
            source_idxs=[0, 0, 1],
            target_idxs=[1, 2, 2]
        )

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
