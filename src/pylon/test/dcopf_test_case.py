#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------

"""
Test case for the DC Optimal Power Flow routine

"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path import join, dirname

from unittest import TestCase

from pylon.network import Network

from pylon.bus import Bus

from pylon.filter.api import MATPOWERImporter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/3bus.m")

#-------------------------------------------------------------------------------
#  "DCOPFTest" class:
#-------------------------------------------------------------------------------

class DCOPFTest(TestCase):
    """
    We use a MATPOWER data file and validate the results against those
    obtained from running the MATPOWER rundcopf.m script with the same
    data file. See filter_test_case.py for validation of MATPOWER data
    file parsing.

    """

    def setUp(self):
        """
        The test runner will execute this method prior to each test

        """

        mf = MATPOWERImporter()
        self.network = mf.parse_file(DATA_FILE)


    def test_dcopf(self):
        """
        The routine is essentially a method class so we have on one
        test.  In this test we validate each stage of the computation.

        """

        self.validate_v_phases()


    def validate_v_phases(self):
        """
        Validate the vector of initial bus voltage phases

        """

        pass


#    def test_admittance_formation(self):
#        """
#        Test formation of the admittance matrix for a simple 3 bus network
#
#        """
#
#        bus_1 = Bus()
#        bus_2 = bus()
#        bus_3 = Bus()
#        self.network.add_buses([bus_1, bus_2, bus_3])
#
#        branch_1 = Branch(
#            source_bus=bus1,
#            target_bus=bus_2,
#            r=0.01,
#            x=0.02,
#            b=0.03
#        )
#        self.network.add_branch(branch_1)
#
#        branch_2 = Branch(
#            source_bus=bus1,
#            target_bus=bus_3,
#            r=0.04,
#            x=0.05,
#            b=0.06
#        )
#        self.network.add_branch(branch_2)
#
#        branch_3 = Branch(
#            source_bus=bus2,
#            target_bus=bus_3,
#            r=0.07,
#            x=0.08,
#            b=0.09
#        )
#        self.network.add_branch(branch_3)
#
#        self._validate_admittance_diagonal_values(self.network.admittance)
#        self._validate_admittance_off_diagonal_values(self.network.admittance)
#        self._validate_admittance_off_diagonal_equality(self.network.admittance)
#
#
#    def test_admittance_events(self):
#        """
#        Test that the admittance matrix is updated when:
#            * a new branch is added
#            * a branch is or branches are removed
#            * the resistance of a branch is changed
#            * the reactance of a branch is changed
#            * the susceptance of a branch is changed
#
#        """
#
#        # Branch addition
#        inital_length = len(self.network.admittance)
#
#        bus_1 = Bus()
#        bus_2 = bus()
#        self.network.add_buses([bus_1, bus_2])
#
#        branch_1 = Branch(
#            source_bus=bus1,
#            target_bus=bus_2,
#            r=0.01,
#            x=0.02,
#            b=0.03
#        )
#        self.network.add_branch(branch_1)
#
#        self.assertNotEqual(
#            inital_length,
#            len(self.network.admittance),
#            "The dimensions of the admittance matrix (%d) have not changed" %
#            (initial_length)
#        )
#
#        # Change of resistance
#        before_r = self.network.admittance[0, 0]
#        branch_1.r = 0.1
#        after_r = self.network.admittance[0, 0]
#
#        self.assertNotEqual(before_r, after_r)
#
#        # Change of reactance
#        before_x = self.network.admittance[0, 0]
#        branch_1.x = 0.2
#        after_x = self.network.admittance[0, 0]
#
#        self.assertNotEqual(before_x, after_x)
#
#        # Change of susceptance
#        before_b = self.network.admittance[0, 0]
#        branch_1.b = 0.2
#        after_b = self.network.admittance[0, 0]
#
#        self.assertNotEqual(before_b, after_b)
#
#        # Branch removal
#        inital_length = len(self.network.admittance)
#
#        self.network.branches = []
#
#        self.assertNotEqual(
#            inital_length,
#            len(self.network.admittance),
#            "The dimensions of the admittance matrix (%d) have not changed" %
#            (initial_length)
#        )
#
#
#    def _validate_admittance_diagonal_values(self, admittance):
#        """
#        Assert that the calculated admittance matrix is the same as that
#        computed by MATPOWER
#
#        Ybus =
#
#           (1,1)     12.7789 -40.6958i
#           (2,1)     -5.8824 +23.5294i
#           (3,1)     -6.8966 +17.2414i
#           (1,2)     -5.8824 +23.5294i
#           (2,2)     12.5490 -36.7827i
#           (3,2)     -6.6667 +13.3333i
#           (1,3)     -6.8966 +17.2414i
#           (2,3)     -6.6667 +13.3333i
#           (3,3)     13.5632 -30.4897i
#
#        """
#
#        Y_0_0 = complex(12.7789, -40.6958)
#        Y_1_1 = complex(12.5490, -36.7827)
#        Y_2_2 = complex(13.5632, -30.4897)
#
#        self.assertEqual(
#            Y_0_0,
#            admittance[0, 0],
#            "Admittance matrix element [0, 0] expected %d, %d found)" %
#            (Y_0_0, admittance[0, 0])
#        )
#
#        self.assertEqual(
#            Y_1_1,
#            admittance[1, 1],
#            "Admittance matrix element [1, 1] expected %d, %d found)" %
#            (Y_1_1, admittance[1, 1])
#        )
#
#        self.assertEqual(
#            Y_2_2,
#            admittance[2, 2],
#            "Admittance matrix element [2, 2] expected %d, %d found)" %
#            (Y_2_2, admittance[2, 2])
#        )
#
#
#    def _validate_admittance_off_diagonal_values(self, admittance):
#        """
#
#        """
#
#        Y_0_1 = complex(-5.8824, 23.5294)
#        Y_0_2 = complex(-6.8966, 17.2414)
#        Y_1_2 = complex(-6.6667, 13.3333)
#
#        self.assertEqual(
#            Y_0_1,
#            admittance[0, 1],
#            "Admittance matrix element [0, 1] expected %d, %d found)" %
#            (Y_0_1, admittance[0, 1])
#        )
#
#        self.assertEqual(
#            Y_0_2,
#            admittance[0, 2],
#            "Admittance matrix element [0, 2] expected %d, %d found)" %
#            (Y_0_2, admittance[0, 2])
#        )
#
#        self.assertEqual(
#            Y_1_2,
#            admittance[1, 2],
#            "Admittance matrix element [1, 2] expected %d, %d found)" %
#            (Y_1_2, admittance[1, 2])
#        )
#
#
#    def _validate_admittance_off_diagonal_equality(self):
#        """
#        Validate that off diagonal elements [i, j] and [j, i] are equal
#
#        """
#
#        for i in range(len(admittance)):
#            for j in range(len(admittance)):
#                if i is not j and i < j:
#                    self.assertEqual(
#                        admittance[i, j],
#                        admittance[j, i],
#                        "Admittance matrix elements [%d, %d] and [%d, %d] "
#                        "should be equal bus are %d and %d respectively" %
#                        (i, j, j, i, admittance[i, j], admittance[j, i])
#                    )

if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
