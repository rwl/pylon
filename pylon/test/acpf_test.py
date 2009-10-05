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

""" Test case for the AC Power Flow routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase, main

from pylon.readwrite import PickleReader
from pylon.y import AdmittanceMatrix
from pylon import NewtonRaphson

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "NewtonPFTest" class:
#------------------------------------------------------------------------------

class NewtonPFTest(TestCase):
    """ We use a MATPOWER data file and validate the results against those
        obtained from running the MATPOWER runacpf.m script with the same data
        file. See reader_test_case.py for validation of MATPOWER data file
        parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        # See 'reader_test_case.py' for MATPOWER reader tests.
        self.case = PickleReader().read(DATA_FILE)

        self.routine = NewtonRaphson()


    def test_voltage_vector(self):
        """ Test the initial vector of complex bus voltages.

            V0 =

                1.0500
                1.0500
                1.0700
                1.0000
                1.0000
                1.0000
        """
        self.routine.case = self.case
        v_initial = self.routine._get_initial_voltage_vector()

#        print v_initial

        self.assertEqual(v_initial.typecode, "z")
        self.assertEqual(v_initial.size, (6, 1))

        places = 4

        # TODO: Repeat test for a case with generator voltage set points
        # different to the initial bus voltage magnitudes.
        v0_0 = 1.0500
        v0_2 = 1.0700
        v0_5 = 1.0000

        self.assertAlmostEqual(abs(v_initial[0]), v0_0, places)
        self.assertAlmostEqual(abs(v_initial[2]), v0_2, places)
        self.assertAlmostEqual(abs(v_initial[5]), v0_5, places)


    def test_apparent_power_vector(self):
        """ Test the vector of complex bus power injections.

            Sbus =

                    0
               0.5000
               0.6000
              -0.7000 - 0.7000i
              -0.7000 - 0.7000i
              -0.7000 - 0.7000i
        """
        self.routine.case = self.case
        s_surplus = self.routine._get_power_injection_vector()

        self.assertEqual(s_surplus.typecode, "z")
        self.assertEqual(s_surplus.size, (6, 1))

        places = 4

        s_0 = 0.0000
        s_2 = 0.6000
        s_35 = -0.7000

        self.assertAlmostEqual(abs(s_surplus[0]), s_0, places)
        self.assertAlmostEqual(abs(s_surplus[2]), s_2, places)
        self.assertAlmostEqual(s_surplus[3].real, s_35, places)
        self.assertAlmostEqual(s_surplus[3].imag, s_35, places)
        self.assertAlmostEqual(s_surplus[5].real, s_35, places)
        self.assertAlmostEqual(s_surplus[5].imag, s_35, places)


    def test_function_evaluation(self):
        """ Test function evaluation without iteration.

            F =

               -0.1718
               -0.3299
                0.4412
                0.5061
                0.4874
               -0.0053
                0.0274
               -0.2608
        """
        places = 4
        routine = self.routine

        # Perform preliminary steps.
        routine.case = self.case

        # See 'y_test_case.py' for admittance matrix tests.
        routine.Y, Ysrc, Ytgt = AdmittanceMatrix().build(self.case)

        routine.v = routine._get_initial_voltage_vector()
        routine.s_surplus = routine._get_power_injection_vector()
        routine._index_buses()

        f = routine._evaluate_function()

        self.assertEqual(f.size, (8, 1))

        f_0 = -0.1718
        f_6 = 0.0274

        self.assertAlmostEqual(f[0], f_0, places)
        self.assertAlmostEqual(f[6], f_6, places)


    def test_convergence_check(self):
        """ Test convergence satisfaction check.

            normF =

                0.5061
        """
        routine = self.routine

        # Perform preliminary steps.
        routine.case = self.case

        # See 'y_test_case.py' for admittance matrix tests.
        routine.Y, Ysrc, Ytgt = AdmittanceMatrix().build(self.case)

        routine.v = self.routine._get_initial_voltage_vector()
        routine.s_surplus = self.routine._get_power_injection_vector()
        routine._index_buses()
        routine.f = routine._evaluate_function()

        # True negative
        routine.converged = False
        routine.tolerance = 0.500
        self.assertFalse(routine._check_convergence())

        # True positive
        routine.converged = False
        routine.tolerance = 0.510
        self.assertTrue(routine._check_convergence())


    def test_bus_indexing(self):
        """ Test the indexing of buses according their mode.

            ref =

                1

            pv_bus =

                2  3

            pq_bus =

                4  5  6

            pvpq_bus =

                2  3  4  5  6
        """
        routine = self.routine
        routine.case = self.case
        routine._index_buses()

        self.assertEqual(len(routine.pv_idxs), 2)
        self.assertEqual(len(routine.pq_idxs), 3)
        self.assertEqual(len(routine.pvpq_idxs), 5)

        pv_0 = 1
        pq_2 = 5
        pvpq_3 = 4

        self.assertEqual(routine.pv_idxs[0], pv_0)
        self.assertEqual(routine.pq_idxs[2], pq_2)
        self.assertEqual(routine.pvpq_idxs[3], pvpq_3)


    def test_jacobian(self):
        """ Test creation of the Jacobian matrix.

            dS_dVm[0] =

               4.3070 +12.6527i  -2.1000 - 4.2000i        0            -1.2353 - 4.9412i  -0.8714 - 3.2676i        0
              -2.1000 - 4.2000i  10.1072 +24.9408i  -0.8077 - 4.0385i  -4.2000 - 8.4000i  -1.0500 - 3.1500i  -1.6370 - 4.6771i
                    0            -0.8231 - 4.1154i   4.6991 +18.6294i        0            -1.5659 - 3.3927i  -2.0577 -10.2885i
              -1.1765 - 4.7059i  -4.0000 - 8.0000i        0             5.9176 +13.9306i  -1.0000 - 2.0000i        0
              -0.8299 - 3.1120i  -1.0000 - 3.0000i  -1.4634 - 3.1707i  -1.0000 - 2.0000i   5.0994 +13.4652i  -1.0000 - 3.0000i
                    0            -1.5590 - 4.4543i  -1.9231 - 9.6154i        0            -1.0000 - 3.0000i   4.2695 +16.0439i

            dS_dVa[0] =

              12.6188 - 4.3117i  -4.4100 + 2.2050i        0            -4.9412 + 1.2353i  -3.2676 + 0.8714i         0
              -4.4100 + 2.2050i  24.9582 - 9.9562i  -4.3212 + 0.8642i  -8.4000 + 4.2000i  -3.1500 + 1.0500i  -4.6771 + 1.6370i
                    0            -4.3212 + 0.8642i  18.0023 - 4.4878i        0            -3.3927 + 1.5659i -10.2885 + 2.0577i
              -4.9412 + 1.2353i  -8.4000 + 4.2000i        0            15.3412 - 6.4353i  -2.0000 + 1.0000i        0
              -3.2676 + 0.8714i  -3.1500 + 1.0500i  -3.3927 + 1.5659i  -2.0000 + 1.0000i  14.8103 - 5.4872i  -3.0000 + 1.0000i
                    0            -4.6771 + 1.6370i -10.2885 + 2.0577i        0            -3.0000 + 1.0000i  17.9655 - 4.6947i


            dS_dVm =
                [-1.22e+01+j4.52e+00  4.20e+00-j2.10e+00          0           4.94e+00-j1.24e+00  3.27e+00-j8.71e-01          0         ]
                [ 4.20e+00-j2.10e+00 -2.40e+01+j1.04e+01  4.04e+00-j8.08e-01  8.40e+00-j4.20e+00  3.15e+00-j1.05e+00  4.68e+00-j1.64e+00]
                [         0           4.12e+00-j8.23e-01 -1.75e+01+j5.35e+00          0           3.39e+00-j1.57e+00  1.03e+01-j2.06e+00]
                [ 4.71e+00-j1.18e+00  8.00e+00-j4.00e+00          0          -1.49e+01+j5.47e+00  2.00e+00-j1.00e+00          0         ]
                [ 3.11e+00-j8.30e-01  3.00e+00-j1.00e+00  3.17e+00-j1.46e+00  2.00e+00-j1.00e+00 -1.43e+01+j4.62e+00  3.00e+00-j1.00e+00]
                [         0           4.45e+00-j1.56e+00  9.62e+00-j1.92e+00          0           3.00e+00-j1.00e+00 -1.72e+01+j3.52e+00]

            dS_dVa =
                [ 1.26e+01-j4.31e+00 -4.41e+00+j2.21e+00          0          -4.94e+00+j1.24e+00 -3.27e+00+j8.71e-01          0         ]
                [-4.41e+00+j2.21e+00  2.50e+01-j9.96e+00 -4.32e+00+j8.64e-01 -8.40e+00+j4.20e+00 -3.15e+00+j1.05e+00 -4.68e+00+j1.64e+00]
                [         0          -4.32e+00+j8.64e-01  1.80e+01-j4.49e+00          0          -3.39e+00+j1.57e+00 -1.03e+01+j2.06e+00]
                [-4.94e+00+j1.24e+00 -8.40e+00+j4.20e+00          0           1.53e+01-j6.44e+00 -2.00e+00+j1.00e+00          0         ]
                [-3.27e+00+j8.71e-01 -3.15e+00+j1.05e+00 -3.39e+00+j1.57e+00 -2.00e+00+j1.00e+00  1.48e+01-j5.49e+00 -3.00e+00+j1.00e+00]
                [         0          -4.68e+00+j1.64e+00 -1.03e+01+j2.06e+00          0          -3.00e+00+j1.00e+00  1.80e+01-j4.69e+00]

            J11[0] =

               24.9582   -4.3212   -8.4000   -3.1500   -4.6771
               -4.3212   18.0023         0   -3.3927  -10.2885
               -8.4000         0   15.3412   -2.0000         0
               -3.1500   -3.3927   -2.0000   14.8103   -3.0000
               -4.6771  -10.2885         0   -3.0000   17.9655


            J12[0] =

               -4.2000   -1.0500   -1.6370
                     0   -1.5659   -2.0577
                5.9176   -1.0000         0
               -1.0000    5.0994   -1.0000
                     0   -1.0000    4.2695

            J21[0] =

                4.2000         0   -6.4353    1.0000         0
                1.0500    1.5659    1.0000   -5.4872    1.0000
                1.6370    2.0577         0    1.0000   -4.6947


            J22[0] =

               13.9306   -2.0000         0
               -2.0000   13.4652   -3.0000
                     0   -3.0000   16.0439


            J[0] =

               24.9582   -4.3212   -8.4000   -3.1500   -4.6771   -4.2000   -1.0500   -1.6370
               -4.3212   18.0023         0   -3.3927  -10.2885         0   -1.5659   -2.0577
               -8.4000         0   15.3412   -2.0000         0    5.9176   -1.0000         0
               -3.1500   -3.3927   -2.0000   14.8103   -3.0000   -1.0000    5.0994   -1.0000
               -4.6771  -10.2885         0   -3.0000   17.9655         0   -1.0000    4.2695
                4.2000         0   -6.4353    1.0000         0   13.9306   -2.0000         0
                1.0500    1.5659    1.0000   -5.4872    1.0000   -2.0000   13.4652   -3.0000
                1.6370    2.0577         0    1.0000   -4.6947         0   -3.0000   16.0439

            J12 =
                [ 8.40e+00  3.15e+00  4.68e+00]
                [    0      3.39e+00  1.03e+01]
                [-1.49e+01  2.00e+00     0    ]
                [ 2.00e+00 -1.43e+01  3.00e+00]
                [    0      3.00e+00 -1.72e+01]

            J22 =
                [ 5.47e+00 -1.00e+00     0    ]
                [-1.00e+00  4.62e+00 -1.00e+00]
                [    0     -1.00e+00  3.52e+00]

            J =

            [ 2.50e+01 -4.32e+00 -8.40e+00 -3.15e+00 -4.68e+00  8.40e+00  3.15e+00 ... ]
            [-4.32e+00  1.80e+01     0     -3.39e+00 -1.03e+01     0      3.39e+00 ... ]
            [-8.40e+00     0      1.53e+01 -2.00e+00     0     -1.49e+01  2.00e+00 ... ]
            [-3.15e+00 -3.39e+00 -2.00e+00  1.48e+01 -3.00e+00  2.00e+00 -1.43e+01 ... ]
            [-4.68e+00 -1.03e+01     0     -3.00e+00  1.80e+01     0      3.00e+00 ... ]
            [ 4.20e+00     0     -6.44e+00  1.00e+00     0      5.47e+00 -1.00e+00 ... ]
            [ 1.05e+00  1.57e+00  1.00e+00 -5.49e+00  1.00e+00 -1.00e+00  4.62e+00 ... ]
            [ 1.64e+00  2.06e+00     0      1.00e+00 -4.69e+00     0     -1.00e+00 ... ]
        """
        routine = self.routine

        routine.case = self.case

        # See 'y_test_case.py' for admittance matrix tests.
        routine.Y, Ysrc, Ytgt = AdmittanceMatrix().build(self.case)

        routine.v = self.routine._get_initial_voltage_vector()
        routine.s_surplus = self.routine._get_power_injection_vector()
        routine._index_buses()

        J = routine._get_jacobian()

        self.assertEqual(J.size, (8, 8))

        places = 4

        J0_0 = 24.9582
        J6_3 = -5.4872
        J3_6 = 5.0994
        J7_1 = 2.0577
        J0_7 = -1.6370
        J6_7 = -3.0000

        self.assertAlmostEqual(J[0, 0], J0_0, places)
        self.assertAlmostEqual(J[6, 3], J6_3, places)
        self.assertAlmostEqual(J[3, 6], J3_6, places)
        self.assertAlmostEqual(J[7, 1], J7_1, places)
        self.assertAlmostEqual(J[0, 7], J0_7, places)
        self.assertAlmostEqual(J[6, 7], J6_7, places)


    def test_iteration(self):
        """ Test iteration of full Newton's method.

            dx[0] =

               -0.0616
               -0.0717
               -0.0714
               -0.0897
               -0.1012
               -0.0094
               -0.0128
                0.0053

            V[0] =

               1.0500
               1.0480 - 0.0647i
               1.0672 - 0.0767i
               0.9880 - 0.0707i
               0.9832 - 0.0884i
               1.0002 - 0.1016i

            V[1] =

               1.0500
               1.0478 - 0.0672i
               1.0670 - 0.0797i
               0.9867 - 0.0724i
               0.9813 - 0.0906i
               0.9990 - 0.1041i
        """
        routine = self.routine

        routine.case = self.case

        # See 'y_test_case.py' for admittance matrix tests.
        routine.Y, Ysrc, Ytgt = AdmittanceMatrix().build(self.case)

        routine.v = self.routine._get_initial_voltage_vector()
        routine.s_surplus = self.routine._get_power_injection_vector()
        routine._index_buses()

        # Initial evaluation of f(x0) and convergency check
#        routine.converged = False
        routine.f = routine._evaluate_function()
#        routine._check_convergence()

        # First iteration.
        routine._iterate()
        v = routine.v

        self.assertEqual(v.size, (6, 1))

        places = 4

        v0_2 = abs(1.0672-0.0767j)
        v0_4 = abs(0.9832-0.0884j)

        self.assertAlmostEqual(abs(v[2]), v0_2, places)
        self.assertAlmostEqual(abs(v[4]), v0_4, places)

        # Second iteration.
        routine._iterate()
        v = routine.v

        self.assertEqual(v.size, (6, 1))

        v1_1 = abs(1.0478-0.0672j)
        v1_5 = abs(0.9990-0.1041j)

#        self.assertAlmostEqual(abs(v[1]), v1_1, places)
#        self.assertAlmostEqual(abs(v[5]), v1_5, places)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")

    main()

# EOF -------------------------------------------------------------------------
