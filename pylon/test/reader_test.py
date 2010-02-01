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

""" Data file parsing tests.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path
import logging

from unittest import TestCase, main

from pylon.readwrite import MATPOWERReader, PSSEReader, PSATReader

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

MATPOWER_DATA_FILE = os.path.join(DATA_DIR, "case6ww.m")
PWL_MP_DATA_FILE   = os.path.join(DATA_DIR, "case30pwl.m")
UKGDS_DATA_FILE    = os.path.join(DATA_DIR, "ehv3.raw")
IPSA_DATA_FILE     = os.path.join(DATA_DIR, "ipsa.raw")
PSAT_DATA_FILE     = os.path.join(DATA_DIR, "d_006_mdl.m")

#------------------------------------------------------------------------------
#  "ReaderTest" class:
#------------------------------------------------------------------------------

class ReaderTest(TestCase):
    """ Defines a base class for many reader test cases.
    """

    def _validate_base(self, base_mva):
        """ Validate the Network objects properties.
        """

        c = self.case

        self.assertEqual(c.base_mva, base_mva)


    def _validate_object_numbers(self, n_buses, n_branches, n_gen):
        """ Validates the expected number of objects.
        """
        c = self.case

        self.assertEqual(len(c.buses), n_buses,
            "%d buses expected, %d found" % (n_buses, len(c.buses)))

        self.assertEqual(len(c.branches), n_branches,
            "%d branches expected, %d found" % (n_branches, len(c.branches)))

        self.assertEqual(len(c.generators), n_gen,
            "%d generators expected, %d found" % (n_gen,len(c.generators)))


    def _validate_slack_bus(self, slack_idx):
        """ Validates the location and number of slack buses.
        """
        c = self.case
        slack_idxs = [c.buses.index(v) for v in c.buses if v.type == "ref"]

        self.assertEqual(slack_idxs, [slack_idx])


    def _validate_generator_connections(self, gbus_idxs):
        """ Validates that generators are connected to the expected buses.
        """
        for i, g in enumerate(self.case.generators):
            busidx = self.case.buses.index(g.bus)
            self.assertEqual(busidx, gbus_idxs[i])


    def _validate_branch_connections(self, from_idxs, to_idxs):
        """ Validates that Branch objects are connected to the expected
            from and to buses.
        """
        c = self.case

        for e in c.branches:
            from_idx = c.buses.index(e.from_bus)
            from_expected = from_idxs[c.branches.index(e)]
            self.assertEqual(from_idx, from_expected,
                "From bus %d expected, %d found" %
                (from_expected, from_idx))

            to_idx = c.buses.index(e.to_bus)
            to_expected = to_idxs[c.branches.index(e)]
            self.assertEqual(to_idx, to_expected,
                "To bus %d expected, %d found" %
                (to_expected, to_idx))

#------------------------------------------------------------------------------
#  "MatpowerReaderTest" class:
#------------------------------------------------------------------------------

class MatpowerReaderTest(ReaderTest):
    """ Defines a test case for the MATPOWER reader.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.reader = MATPOWERReader()


    def test_case6ww(self):
        """ Test parsing case6ww.m file.
        """
        self.case = c = self.reader.read(MATPOWER_DATA_FILE)

        self._validate_base(base_mva=100.0)

        # Network structure validation.
        self._validate_object_numbers(n_buses=6, n_branches=11, n_gen=3)

        self._validate_slack_bus(slack_idx=0)

        self._validate_generator_connections(gbus_idxs=[0, 1, 2])

        self._validate_branch_connections(
            from_idxs=[0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4],
            to_idxs=[1, 3, 4, 2, 3, 4, 5, 4, 5, 4, 5])

        # Generator costs.
        for g in c.generators:
            self.assertEqual(g.pcost_model, "poly")
            self.assertEqual(len(g.p_cost), 3)

        self.assertEqual(c.generators[0].p_cost[0], 0.00533)
        self.assertEqual(c.generators[1].p_cost[1], 10.333)
        self.assertEqual(c.generators[2].p_cost[2], 240)



    def test_case30pwl(self):
        """ Test parsing case30pwl.m.
        """
        case = self.case = self.reader.read(PWL_MP_DATA_FILE)

        self._validate_base(base_mva=100.0)

        self._validate_object_numbers(n_buses=30, n_branches=41, n_gen=6)

        self._validate_slack_bus(slack_idx=0)

        self._validate_generator_connections(gbus_idxs=[0, 1, 21, 26, 22, 12])

        self._validate_branch_connections(
            from_idxs=[0, 0, 1, 2, 1, 1, 3, 4, 5, 5, 5, 5, 8, 8, 3, 11, 11,
                       11, 11, 13, 15, 14, 17, 18, 9, 9, 9, 9, 20, 14, 21,
                       22, 23, 24, 24, 27, 26, 26, 28, 7, 5],
            to_idxs=[1, 2, 3, 3, 4, 5, 5, 6, 6, 7, 8, 9, 10, 9, 11, 12, 13,
                     14, 15, 14, 16, 17, 18, 19, 19, 16, 20, 21, 21, 22,
                     23, 23, 24, 25, 26, 26, 28, 29, 29, 27, 27])

        # Generator costs.
        generators = case.generators

        for g in generators:
            self.assertEqual(g.pcost_model, "pwl")
            self.assertEqual(len(g.p_cost), 4)
            self.assertEqual(g.p_cost[0], (0.0, 0.0))

        self.assertEqual(generators[0].p_cost[1], (12.0, 144.0))
        self.assertEqual(generators[4].p_cost[2], (36.0, 1296.0))
        self.assertEqual(generators[5].p_cost[3], (60.0, 2832.0))

#------------------------------------------------------------------------------
#  "PSSEReaderTest" class:
#------------------------------------------------------------------------------

#class PSSEReaderTest(ReaderTest):
#    """ Defines a test case for the PSS/E data file reader.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.reader = PSSEReader()
#
#
#    def test_ipsa(self):
#        """ Test parsing of a data file exported from IPSA.
#        """
#        self.case = self.reader.read(IPSA_DATA_FILE)
#
#        self._validate_base(100.0)
#        self._validate_object_numbers(n_buses=56, n_branches=67, n_gen=24)
#
#
#    def test_ukgds(self):
#        """ Test parsing of PSS/E data file exported from the UKGDS.
#        """
#        # Parse the file.
#        self.case = self.reader(UKGDS_DATA_FILE)
#
#        # Network structure validation
#        self._validate_base(100.0)
#
#        self._validate_object_numbers(n_buses=102,
#                                      # 75 lines + 67 transformers = 142
#                                      n_branches=142,
#                                      n_gen=3)
#
#        self._validate_slack_bus(slack_idx=0)
#
#        self._validate_generator_connections(gbus_idxs=[0, 1])
#
#        self._validate_branch_connections(from_idxs=[0, 0, 1],
#                                          to_idxs=[1, 2, 2])

#------------------------------------------------------------------------------
#  "PSATReaderTest" class:
#------------------------------------------------------------------------------

#class PSATReaderTest(ReaderTest):
#    """ Defines a test case for the PSAT data file reader.
#    """
#
#    def test_psat(self):
#        """ Test parsing of a PSAT data file.
#        """
#        reader = PSATReader()
#        self.case = reader(PSAT_DATA_FILE)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")
    main()

# EOF -------------------------------------------------------------------------
