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
        self.routine.solve()


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

        v_initial = self.routine.v_initial

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

# EOF -------------------------------------------------------------------------
