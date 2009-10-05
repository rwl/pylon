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

""" Test case for the AC Power Flow routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase, main

from pylon.readwrite import PickleReader
from pylon import FastDecoupled

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "FDPFTest" class:
#------------------------------------------------------------------------------

class FDPFTest(TestCase):
    """ We use a MATPOWER data file and validate the results against those
        obtained from running the MATPOWER runpf.m script with the same data
        file and PF_ALG set to 2 and 3 in mpoption.m. See reader_test_case.py
        for validation of MATPOWER data file parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = PickleReader().read(DATA_FILE)
        self.routine = FastDecoupled()
        success = self.routine.solve(case)


    def test_mismatch(self):
        """ Test FDPF mismatch evaluation.

        P =

           -0.1636
           -0.3083
            0.4412
            0.5061
            0.4874


        Q =

           -0.0053
            0.0274
           -0.2608

        """

        routine = self.routine

        routine._make_admittance_matrix()
        routine._initialise_voltage_vector()
        routine._make_power_injection_vector()
        routine._index_buses()

        routine._evaluate_mismatch()

        P = routine.p
        Q = routine.q

        self.assertEqual(P.size, (5, 1))
        self.assertEqual(Q.size, (3, 1))

        places = 4

        P_0 = -0.1636
        P_3 = 0.5061
        Q_0 = -0.0053
        Q_2 = -0.2608

        self.assertAlmostEqual(P[0], P_0, places)
        self.assertAlmostEqual(P[3], P_3, places)
        self.assertAlmostEqual(Q[0], Q_0, places)
        self.assertAlmostEqual(Q[2], Q_2, places)


    def test_convergence(self):
        """ Test convergence satisfaction check.

        normP =

            0.5061


        normQ =

            0.2608

        """

        routine = self.routine

        routine._make_admittance_matrix()
        routine._initialise_voltage_vector()
        routine._make_power_injection_vector()
        routine._index_buses()

        routine._evaluate_mismatch()

        # True negative
        routine.converged = False
        routine.tolerance = 0.5000
        self.assertFalse(routine._check_convergence())

        # True positive
        routine.converged = False
        routine.tolerance = 0.6000
        self.assertTrue(routine._check_convergence())


    def test_B_prime(self):
        """ Test build of FDPF matrix B prime.

        Bp =

           13.3333   -5.0000         0   -5.0000   -3.3333         0
           -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000
                 0   -4.0000   17.8462         0   -3.8462  -10.0000
           -5.0000  -10.0000         0   17.5000   -2.5000         0
           -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333
                 0   -5.0000  -10.0000         0   -3.3333   18.3333

        """

        Bp = self.routine._make_B_prime()

        self.assertEqual(Bp.size, (6, 6))

        places = 4

        Bp0_0 = 13.3333
        Bp5_5 = 18.3333
        Bp3_1 = -10.0000
        Bp2_4 = -3.8462

        self.assertAlmostEqual(Bp[0, 0], Bp0_0, places)
        self.assertAlmostEqual(Bp[5, 5], Bp5_5, places)
        self.assertAlmostEqual(Bp[3, 1], Bp3_1, places)
        self.assertAlmostEqual(Bp[2, 4], Bp2_4, places)


    def test_B_double_prime(self):
        """ Test build of FDPF matrix B double prime.

        Bpp =

           11.7479   -4.0000         0   -4.7059   -3.1120         0
           -4.0000   23.1955   -3.8462   -8.0000   -3.0000   -4.4543
                 0   -3.8462   16.5673         0   -3.1707   -9.6154
           -4.7059   -8.0000         0   14.6359   -2.0000         0
           -3.1120   -3.0000   -3.1707   -2.0000   14.1378   -3.0000
                 0   -4.4543   -9.6154         0   -3.0000   17.0047

        """

        Bpp = self.routine._make_B_double_prime()

        self.assertEqual(Bpp.size, (6, 6))

        places = 4

        Bpp0_0 = 11.7479
        Bpp5_5 = 17.0047
        Bpp3_1 = -8.0000
        Bpp2_4 = -3.1707

        self.assertAlmostEqual(Bpp[0, 0], Bpp0_0, places)
        self.assertAlmostEqual(Bpp[5, 5], Bpp5_5, places)
        self.assertAlmostEqual(Bpp[3, 1], Bpp3_1, places)
        self.assertAlmostEqual(Bpp[2, 4], Bpp2_4, places)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    main()

# EOF -------------------------------------------------------------------------
