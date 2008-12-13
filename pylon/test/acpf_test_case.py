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

""" Test case for the AC Power Flow routine. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase, main

from pylon.readwrite.api import read_matpower
from pylon.routine.api import NewtonPFRoutine

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/case6ww.m")

#------------------------------------------------------------------------------
#  "ACPFTest" class:
#------------------------------------------------------------------------------

class ACPFTest(TestCase):
    """ We use a MATPOWER data file and validate the results against those
    obtained from running the MATPOWER runacpf.m script with the same data
    file. See reader_test_case.py for validation of MATPOWER data file parsing.

    """

    routine = NewtonPFRoutine

    def setUp(self):
        """ The test runner will execute this method prior to each test. """

        network = read_matpower(DATA_FILE)
        self.routine = NewtonPFRoutine(network)


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

        self.routine._initialise_voltage_vector()
        v_initial = self.routine.v

        self.assertEqual(v_initial.typecode, "z")
        self.assertEqual(v_initial.size, (6, 1))

        places = 4

        # TODO: Repeat test for a network with generator voltage set points
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

        self.routine.solve()
        s_surplus = self.routine.s_surplus

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

        # Perform preliminary steps
        self.routine._make_admittance_matrix()
        self.routine._initialise_voltage_vector()
        self.routine._make_apparent_power_injection_vector()
        self.routine._index_buses()

        self.routine._evaluate_function()
        f = self.routine.f

        self.assertEqual(f.size, (8, 1))

        places = 4

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

        # Perform preliminary steps
        routine._make_admittance_matrix()
        routine._initialise_voltage_vector()
        routine._make_apparent_power_injection_vector()
        routine._index_buses()
        routine._evaluate_function()

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

            2
            3

        pq_bus =

            4
            5
            6

        pvpq_bus =

            2
            3
            4
            5
            6

        """

        routine = self.routine

        routine._index_buses()

        self.assertEqual(routine.pv_idxs.size, (2, 1))
        self.assertEqual(routine.pq_idxs.size, (3, 1))
        self.assertEqual(routine.pvpq_idxs.size, (5, 1))

        pv_0 = 1
        pq_2 = 5
        pvpq_3 = 4

        self.assertEqual(routine.pv_idxs[0], pv_0)
        self.assertEqual(routine.pq_idxs[2], pq_2)
        self.assertEqual(routine.pvpq_idxs[3], pvpq_3)


    def test_jacobian(self):
        """ Test creation of the Jacobian matrix.

        J[0] =

           24.9582   -4.3212   -8.4000   -3.1500   -4.6771   -4.2000   -1.0500   -1.6370
           -4.3212   18.0023         0   -3.3927  -10.2885         0   -1.5659   -2.0577
           -8.4000         0   15.3412   -2.0000         0    5.9176   -1.0000         0
           -3.1500   -3.3927   -2.0000   14.8103   -3.0000   -1.0000    5.0994   -1.0000
           -4.6771  -10.2885         0   -3.0000   17.9655         0   -1.0000    4.2695
            4.2000         0   -6.4353    1.0000         0   13.9306   -2.0000         0
            1.0500    1.5659    1.0000   -5.4872    1.0000   -2.0000   13.4652   -3.0000
            1.6370    2.0577         0    1.0000   -4.6947         0   -3.0000   16.0439

        """

        routine = self.routine

        routine._make_admittance_matrix()
        routine._initialise_voltage_vector()
        routine._make_apparent_power_injection_vector()
        routine._index_buses()

        routine.iterate()

        J = routine.J

        self.assertEqual(J.size, (8, 8))

        places = 4

        J0_0 = 24.9582
        J6_3 = -5.4872
        J3_6 = 5.0994
        J7_1 = 2.0577
        J0_7 = -1.6370

        self.assertAlmostEqual(J[0, 0], J0_0, places)
        self.assertAlmostEqual(J[6, 3], J6_3, places)
        self.assertAlmostEqual(J[3, 6], J3_6, places)
        self.assertAlmostEqual(J[7, 1], J7_1, places)
        self.assertAlmostEqual(J[0, 7], J0_7, places)


    def test_iteration(self):
        """ Test iteration of full Newton's method. """

        routine = self.routine

        routine._make_admittance_matrix()
        routine._initialise_voltage_vector()
        routine._make_apparent_power_injection_vector()
        routine._index_buses()

        # Initial evaluation of f(x0) and convergency check
#        self.converged = False
#        self._evaluate_function()
#        self._check_convergence()

        routine.iterate()


if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
