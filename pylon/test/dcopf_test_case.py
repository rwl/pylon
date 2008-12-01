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

""" Test case for the DC Optimal Power Flow routine """

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase, main

from pylon.readwrite.api import read_matpower
from pylon.routine.api import DCOPFRoutine

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/case6ww.m")

#-------------------------------------------------------------------------------
#  "DCOPFTest" class:
#-------------------------------------------------------------------------------

class DCOPFTest(TestCase):
    """ We use a MATPOWER data file and validate the results against those
    obtained from running the MATPOWER rundcopf.m script with the same data
    file. See filter_test_case.py for validation of MATPOWER data file parsing.

    """

    routine = DCOPFRoutine

    def __init__(self, *args, **kw):
        """ Returns a new DCPFTest instance """

        TestCase.__init__(self, *args, **kw)

        network = read_matpower(DATA_FILE)
        self.routine = DCOPFRoutine(network)
        self.routine.solve()


    def test_theta_injection_source(self):
        """ Tests computation of the phase shift 'quiescent' injections, used
        for calculating branch real power flows at the from end.

        Pfinj =

             0
             0
             0
             0
             0
             0
             0
             0
             0
             0
             0

        """

        theta_inj = self.routine._theta_inj_source

        self.assertEqual(len(theta_inj), 11)
        # FIXME: Repeat for a case with transformers or shunt capacitors
        self.assertEqual(theta_inj[0], 0.0)
        self.assertEqual(theta_inj[10], 0.0)


    def test_theta_injection_bus(self):
        """ Tests phase shift injection vector used for bus real power
        injection calcualtion.

        Pbusinj =

             0
             0
             0
             0
             0
             0

        """

        theta_inj = self.routine._theta_inj_bus

        self.assertEqual(len(theta_inj), 6)
        # FIXME: Require a case with transformers or shunt capacitors
        self.assertEqual(theta_inj[0], 0.0)
        self.assertEqual(theta_inj[5], 0.0)


    def test_cost_model(self):
        """ Tests selection of a quadratic solver if polynomial cost models
        are used.

        """

        self.assertEqual(self.routine._solver_type, "quadratic")


    def test_x_vector(self):
        """ Tests the the x vector where AA * x <= bb.

        x =

             0
             0
             0
             0
             0
             0
             0
        0.5000
        0.6000

        """

        x = self.routine._x

        places = 4

        x_2 = 0.0000
        x_7 = 0.5000
        x_8 = 0.6000

        self.assertEqual(len(x), 9)
        self.assertAlmostEqual(x[2], x_2, places)
        self.assertAlmostEqual(x[7], x_7, places)
        self.assertAlmostEqual(x[8], x_8, places)


    def test_cost_constraints(self):
        """ Test the DC OPF cost constaints. """

        # TODO: Repeat for case with piecewise-linear cost curves.
        Acc = self.routine._aa_cost
        bcc = self.routine._bb_cost

        self.assertEqual(Acc.size, (0, 9))
        self.assertEqual(bcc.size, (0, 1))


    def test_ref_bus_phase_angle_constraint(self):
        """ Test reference bus phase angle constraint. """

        Aref = self.routine._aa_ref
        bref = self.routine._bb_ref

        places = 4

        Aref_0 = 1.0000
        Aref_8 = 0.0000

        self.assertEqual(Aref.size, (1, 9))
        self.assertAlmostEqual(Aref[0], Aref_0, places)
        self.assertAlmostEqual(Aref[8], Aref_8, places)

        bref_0 = 0.0000

        self.assertEqual(bref.size, (1, 1))
        self.assertAlmostEqual(bref[0], bref_0, places)


    def test_power_balance_constraint(self):
        """ Test power balance (mismatch) constraint. """

        # TODO: Repeat for case with piecewise-linear cost curves.
        A_mismatch = self.routine._aa_mismatch
        b_mismatch = self.routine._bb_mismatch

        places = 4

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
