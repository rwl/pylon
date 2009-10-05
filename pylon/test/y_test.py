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

""" Test case for admittance and susceptance matrices.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase, main

from pylon.readwrite import PickleReader

from pylon.y import AdmittanceMatrix, SusceptanceMatrix

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "YTest" class:
#------------------------------------------------------------------------------

class YTest(TestCase):
    """ Uses a MATPOWER data file and validates the results against those
        obtained from running the MATPOWER makeYbus.m script with the
        same data file. See reader_test_case.py for validation of MATPOWER data
        file parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)


    def test_admittance(self):
        """ Test the values of the admittance matrix.

           4.0063 -11.7479i  -2.0000 + 4.0000i        0            -1.1765 + 4.7059i  -0.8299 + 3.1120i        0
          -2.0000 + 4.0000i   9.3283 -23.1955i  -0.7692 + 3.8462i  -4.0000 + 8.0000i  -1.0000 + 3.0000i  -1.5590 + 4.4543i
                0            -0.7692 + 3.8462i   4.1557 -16.5673i        0            -1.4634 + 3.1707i  -1.9231 + 9.6154i
          -1.1765 + 4.7059i  -4.0000 + 8.0000i        0             6.1765 -14.6359i  -1.0000 + 2.0000i        0
          -0.8299 + 3.1120i  -1.0000 + 3.0000i  -1.4634 + 3.1707i  -1.0000 + 2.0000i   5.2933 -14.1378i  -1.0000 + 3.0000i
                0            -1.5590 + 4.4543i  -1.9231 + 9.6154i        0            -1.0000 + 3.0000i   4.4821 -17.0047i

        """
        Y, Ysrc, Ytgt = AdmittanceMatrix().build(self.case)

        self.assertEqual(Y.size, (6, 6))

        self._validate_diagonal_values(Y)
        self._validate_off_diagonal_values(Y)


    def _validate_diagonal_values(self, Y):
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


    def _validate_off_diagonal_values(self, Y):
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

#------------------------------------------------------------------------------
#  "BTest" class:
#------------------------------------------------------------------------------

class BTest(TestCase):
    """ Uses a MATPOWER data file and validates the results against those
        obtained from running the MATPOWER makeBdc.m scripts with the
        same data file. See filter_test_case.py for validation of MATPOWER
        data file parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)


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
        susceptance_matrix = SusceptanceMatrix()
        B, B_source = susceptance_matrix(self.case)

        self._validate_susceptance_diagonal_values(B)
        self._validate_suseptance_off_diagonal_equality(B)


    def _validate_susceptance_diagonal_values(self, B):
        """ Assert that the susceptance matrix diagonal values are the same as
            those computed by MATPOWER.
        """
        places = 4

        B_0_0 = 13.3333
        B_2_2 = 17.8462
        B_4_4 = 16.3462

        self.assertAlmostEqual(B_0_0, B[0, 0], places,
            "B element [0, 0] expected %d, %d found)" % (B_0_0, B[0, 0]))

        self.assertAlmostEqual(B_2_2, B[2, 2], places,
            "B element [1, 1] expected %d, %d found)" % (B_2_2, B[2, 2]))

        self.assertAlmostEqual(B_4_4, B[4, 4], places,
            "B element [2, 2] expected %d, %d found)" % (B_4_4, B[4, 4]))


    def _validate_susceptance_off_diagonal_values(self, B):
        """ Assert that the susceptance matrix off-diagonal values are the same
            as those computed by MATPOWER.
        """
        places = 4

        B_0_1 = -5.0000
        B_0_4 = -3.3333
        B_5_2 = -10.0000

        self.assertAlmostEqual(B_0_1, B[0, 1], places,
            "B element [0, 1] expected %d, %d found)" % (B_0_1, B[0, 1]))

        self.assertAlmostEqual(B_0_4, B[0, 4], places,
            "B element [0, 2] expected %d, %d found)" % (B_0_4, B[0, 4]))

        self.assertAlmostEqual(B_5_2, B[5, 2], places,
            "B element [1, 2] expected %d, %d found)" % (B_5_2, B[5, 2]))


    def _validate_suseptance_off_diagonal_equality(self, B):
        """ Validate that elements [i, j] and [j, i] are equal.
        """
        w, h = B.size
        for i in range(w):
            for j in range(h):
                if (i != j) and (i < j):
                    self.assertEqual(B[i, j], B[j, i],
                        "Susceptance matrix elements [%d, %d] and [%d, %d] "
                        "should be equal but are %d and %d respectively" %
                        (i, j, j, i, B[i, j], B[j, i]))

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")

    main()

# EOF -------------------------------------------------------------------------
