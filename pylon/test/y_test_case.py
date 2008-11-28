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

""" Test case for admittance and susceptance matrices """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase, main

from pylon.readwrite.api import MATPOWERReader
from pylon.routine.y import make_susceptance

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/case6ww.m")

#------------------------------------------------------------------------------
#  "BTest" class:
#------------------------------------------------------------------------------

class BTest(TestCase):
    """ Uses a MATPOWER data file and validates the results against those
    obtained from running the MATPOWER makeBdc.m scripts with the
    same data file. See filter_test_case.py for validation of MATPOWER data
    file parsing.

    """

    network = None

    reader = None

    def setUp(self):
        """ The test runner will execute this method prior to each test """

        if self.reader is None:
            self.reader = reader = MATPOWERReader(DATA_FILE)
            self.network = reader.network
        else:
            self.network = Network().copy_traits(self.reader.network)


    def test_susceptance(self):
        """ The routine is a method class so we have only one test. In this
        test we validate each stage of the computation.

        """

        B, B_source = make_susceptance(self.network)
        self._validate_susceptance_diagonal_values(B)
        self._validate_suseptance_off_diagonal_equality(B)


    def _validate_susceptance_diagonal_values(self, B):
        """ Assert that the calculated susceptance matrix is the same as that
        computed by MATPOWER

        B =

           (1,1)      13.3333
           (2,1)      -5.0000
           (4,1)      -5.0000
           (5,1)      -3.3333
           (1,2)      -5.0000
           (2,2)      27.3333
           (3,2)      -4.0000
           (4,2)     -10.0000
           (5,2)      -3.3333
           (6,2)      -5.0000
           (2,3)      -4.0000
           (3,3)      17.8462
           (5,3)      -3.8462
           (6,3)     -10.0000
           (1,4)      -5.0000
           (2,4)     -10.0000
           (4,4)      17.5000
           (5,4)      -2.5000
           (1,5)      -3.3333
           (2,5)      -3.3333
           (3,5)      -3.8462
           (4,5)      -2.5000
           (5,5)      16.3462
           (6,5)      -3.3333
           (2,6)      -5.0000
           (3,6)     -10.0000
           (5,6)      -3.3333
           (6,6)      18.3333

        """

        places = 4

        B_0_0 = 13.3333
        B_2_2 = 17.8462
        B_4_4 = 16.3462

        self.assertAlmostEqual(
            B_0_0, B[0, 0], places,
            "B element [0, 0] expected %d, %d found)" % (B_0_0, B[0, 0])
        )

        self.assertAlmostEqual(
            B_2_2, B[2, 2], places,
            "B element [1, 1] expected %d, %d found)" % (B_2_2, B[2, 2])
        )

        self.assertAlmostEqual(
            B_4_4, B[4, 4], places,
            "B element [2, 2] expected %d, %d found)" % (B_4_4, B[4, 4])
        )


    def _validate_susceptance_off_diagonal_values(self, B):
        """ Assert that the calculated susceptance matrix is the same as that
        computed by MATPOWER.

        """

        places = 4

        B_0_1 = -5.0000
        B_0_4 = -3.3333
        B_5_2 = -10.0000

        self.assertAlmostEqual(
            B_0_1, B[0, 1], places,
            "B element [0, 1] expected %d, %d found)" % (B_0_1, B[0, 1])
        )

        self.assertAlmostEqual(
            B_0_4, B[0, 4], places,
            "B element [0, 2] expected %d, %d found)" % (B_0_4, B[0, 4])
        )

        self.assertAlmostEqual(
            B_5_2, B[5, 2], places,
            "B element [1, 2] expected %d, %d found)" % (B_5_2, B[5, 2])
        )


    def _validate_suseptance_off_diagonal_equality(self, B):
        """ Validate that elements [i, j] and [j, i] are equal """
        w, h = B.size
        for i in range(w):
            for j in range(h):
                if (i != j) and (i < j):
                    self.assertEqual(
                        B[i, j], B[j, i],
                        "Susceptance matrix elements [%d, %d] and [%d, %d] "
                        "should be equal but are %d and %d respectively" %
                        (i, j, j, i, B[i, j], B[j, i])
                    )

if __name__ == "__main__":
    import logging, sys
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    main()

# EOF -------------------------------------------------------------------------
