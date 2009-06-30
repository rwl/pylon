#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------

""" Test case for the DC Optimal Power Flow routine.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from pylon.readwrite.api import read_matpower
from pylon.routine.api import DCOPFRoutine

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data/case6ww.m")

#-------------------------------------------------------------------------------
#  "DCOPFTest" class:
#-------------------------------------------------------------------------------

class DCOPFTest(unittest.TestCase):
    """ We use a MATPOWER data file and validate the results against those
        obtained from running the MATPOWER rundcopf.m script with the same data
        file. See reader_test_case.py for validation of MATPOWER data file
        parsing.
    """

    routine = DCOPFRoutine

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        network = read_matpower(DATA_FILE)
        self.routine = DCOPFRoutine(network, show_progress=False)
        self.routine.solve()


    def test_theta_injection_source(self):
        """ Test phase shift 'quiescent' injections, used for calculating
            branch real power flows at the from end.

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
        """ Test phase shift injection vector used for bus real power
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
        """ Test selection of quadratic solver for polynomial cost model.
        """
        self.assertEqual(self.routine._solver_type, "quadratic")


    def test_x_vector(self):
        """ Test the the x vector where AA * x <= bb.

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
        """ Test the DC OPF cost constaints.
        """
        # TODO: Repeat for case with piecewise-linear cost curves.
        Acc = self.routine._aa_cost
        bcc = self.routine._bb_cost

        self.assertEqual(Acc.size, (0, 9))
        self.assertEqual(bcc.size, (0, 1))


    def test_ref_bus_phase_angle_constraint(self):
        """ Test reference bus phase angle constraint.

            Aref =

                 1     0     0     0     0     0     0     0     0

            bref =

                 0
        """
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
        """ Test power balance (mismatch) constraint.

            A_mismatch =

               13.3333   -5.0000         0   -5.0000   -3.3333         0   -1.0000         0         0
               -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000         0   -1.0000         0
                     0   -4.0000   17.8462         0   -3.8462  -10.0000         0         0   -1.0000
               -5.0000  -10.0000         0   17.5000   -2.5000         0         0         0         0
               -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333         0         0         0
                     0   -5.0000  -10.0000         0   -3.3333   18.3333         0         0         0

            b_mismatch =

                     0
                     0
                     0
               -0.7000
               -0.7000
               -0.7000
        """
        # TODO: Repeat for case with piecewise-linear cost curves.
        A_mismatch = self.routine._aa_mismatch
        b_mismatch = self.routine._bb_mismatch

        places = 4

        A_1_1 = 27.3333
        A_4_2 = -3.8462

        A_0_6 = -1.0000
        A_2_8 = -1.0000
        A_5_8 = 0.0000

        self.assertEqual(A_mismatch.size, (6, 9)) # Size
        # See y_test_case.py for full susceptance matrix test case.
        self.assertAlmostEqual(A_mismatch[1, 1], A_1_1, places) # B diagonal
        self.assertAlmostEqual(A_mismatch[4, 2], A_4_2, places) # Off-diagonal

        self.assertAlmostEqual(A_mismatch[0, 6], A_0_6, places)
        self.assertAlmostEqual(A_mismatch[2, 8], A_2_8, places)
        self.assertAlmostEqual(A_mismatch[5, 8], A_5_8, places)

        b_0 = 0.0000
        b_3 = -0.7000
        b_5 = -0.7000

        self.assertEqual(b_mismatch.size, (6, 1))
        self.assertAlmostEqual(b_mismatch[0], b_0, places)
        self.assertAlmostEqual(b_mismatch[3], b_3, places)
        self.assertAlmostEqual(b_mismatch[5], b_5, places)


    def test_generator_limit_constraints(self):
        """ Test the upper and lower generator output constraints.

            A_gen =

                 0     0     0     0     0     0    -1     0     0
                 0     0     0     0     0     0     0    -1     0
                 0     0     0     0     0     0     0     0    -1
                 0     0     0     0     0     0     1     0     0
                 0     0     0     0     0     0     0     1     0
                 0     0     0     0     0     0     0     0     1

            b_gen =

               -0.5000
               -0.3750
               -0.4500
                2.0000
                1.5000
                1.8000
        """
        A_gen = self.routine._aa_generation
        b_gen = self.routine._bb_generation

        places = 4

        A_0_0 = 0.0000
        A_5_5 = 0.0000

        A_0_6 = -1.0000
        A_2_6 = 0.0000
        A_2_8 = -1.0000

        A_3_6 = 1.0000
        A_5_6 = 0.0000
        A_5_8 = 1.0000

        self.assertEqual(A_gen.size, (6, 9))
        self.assertAlmostEqual(A_gen[0, 0], A_0_0, places)
        self.assertAlmostEqual(A_gen[5, 5], A_5_5, places)
        self.assertAlmostEqual(A_gen[0, 6], A_0_6, places)
        self.assertAlmostEqual(A_gen[2, 6], A_2_6, places)
        self.assertAlmostEqual(A_gen[2, 8], A_2_8, places)
        self.assertAlmostEqual(A_gen[3, 6], A_3_6, places)
        self.assertAlmostEqual(A_gen[5, 6], A_5_6, places)
        self.assertAlmostEqual(A_gen[5, 8], A_5_8, places)

        b_0 = -0.5000
        b_2 = -0.4500
        b_4 = 1.5000
        b_5 = 1.8000

        self.assertEqual(b_gen.size, (6, 1))
        self.assertAlmostEqual(b_gen[0], b_0, places)
        self.assertAlmostEqual(b_gen[2], b_2, places)
        self.assertAlmostEqual(b_gen[4], b_4, places)
        self.assertAlmostEqual(b_gen[5], b_5, places)


    def test_branch_flow_limit_constraints(self):
        """ Test branch maximum flow limit constraints.

            A_flow =

                5.0000   -5.0000         0         0         0         0         0         0         0
                5.0000         0         0   -5.0000         0         0         0         0         0
                3.3333         0         0         0   -3.3333         0         0         0         0
                     0    4.0000   -4.0000         0         0         0         0         0         0
                     0   10.0000         0  -10.0000         0         0         0         0         0
                     0    3.3333         0         0   -3.3333         0         0         0         0
                     0    5.0000         0         0         0   -5.0000         0         0         0
                     0         0    3.8462         0   -3.8462         0         0         0         0
                     0         0   10.0000         0         0  -10.0000         0         0         0
                     0         0         0    2.5000   -2.5000         0         0         0         0
                     0         0         0         0    3.3333   -3.3333         0         0         0

               -5.0000    5.0000         0         0         0         0         0         0         0
               -5.0000         0         0    5.0000         0         0         0         0         0
               -3.3333         0         0         0    3.3333         0         0         0         0
                     0   -4.0000    4.0000         0         0         0         0         0         0
                     0  -10.0000         0   10.0000         0         0         0         0         0
                     0   -3.3333         0         0    3.3333         0         0         0         0
                     0   -5.0000         0         0         0    5.0000         0         0         0
                     0         0   -3.8462         0    3.8462         0         0         0         0
                     0         0  -10.0000         0         0   10.0000         0         0         0
                     0         0         0   -2.5000    2.5000         0         0         0         0
                     0         0         0         0   -3.3333    3.3333         0         0         0

            b_flow =

                0.4000
                0.6000
                0.4000
                0.4000
                0.6000
                0.3000
                0.9000
                0.7000
                0.8000
                0.2000
                0.4000

                0.4000
                0.6000
                0.4000
                0.4000
                0.6000
                0.3000
                0.9000
                0.7000
                0.8000
                0.2000
                0.4000
        """
        A_flow = self.routine._aa_flow
        b_flow = self.routine._bb_flow

        places = 4

        A_0_0 = 5.0000
        A_2_4 = -3.3333
        A_4_1 = 10.0000
        A_7_4 = -3.8462
        A_0_6 = 0.0000
        A_9_8 = 0.0000

        A_11_0 = -A_0_0
        A_13_4 = -A_2_4
        A_18_4 = -A_7_4
        A_20_8 = 0.0000

        self.assertEqual(A_flow.size, (22, 9))
        self.assertAlmostEqual(A_flow[0, 0], A_0_0, places)
        self.assertAlmostEqual(A_flow[2, 4], A_2_4, places)
        self.assertAlmostEqual(A_flow[4, 1], A_4_1, places)
        self.assertAlmostEqual(A_flow[7, 4], A_7_4, places)
        self.assertAlmostEqual(A_flow[0, 6], A_0_6, places)
        self.assertAlmostEqual(A_flow[9, 8], A_9_8, places)

        self.assertAlmostEqual(A_flow[11, 0], A_11_0, places)
        self.assertAlmostEqual(A_flow[13, 4], A_13_4, places)
        self.assertAlmostEqual(A_flow[18, 4], A_18_4, places)
        self.assertAlmostEqual(A_flow[20, 8], A_20_8, places)

        b_0 = 0.4000
        b_6 = 0.9000
        b_12 = 0.6000
        b_19 = 0.8000

        self.assertEqual(b_flow.size, (22, 1))
        self.assertAlmostEqual(b_flow[0], b_0, places)
        self.assertAlmostEqual(b_flow[6], b_6, places)
        self.assertAlmostEqual(b_flow[12], b_12, places)
        self.assertAlmostEqual(b_flow[19], b_19, places)


    def test_objective_function(self):
        """ Test objective function of the form: 0.5 * x'*H*x + c'*x

            H =

                 0         0         0         0         0         0         0         0         0
                 0         0         0         0         0         0         0         0         0
                 0         0         0         0         0         0         0         0         0
                 0         0         0         0         0         0         0         0         0
                 0         0         0         0         0         0         0         0         0
                 0         0         0         0         0         0         0         0         0
                 0         0         0         0         0         0  106.6000         0         0
                 0         0         0         0         0         0         0  177.8000         0
                 0         0         0         0         0         0         0         0  148.2000

            c =

               1.0e+03 *

                     0
                     0
                     0
                     0
                     0
                     0
                1.1669
                1.0333
                1.0833
        """
        H = self.routine._hh
        c = self.routine._cc

        places = 4

        H_0_0 = 0.0000
        H_8_5 = 0.0000
        H_2_7 = 0.0000
        H_6_6 = 106.6000
        H_8_8 = 148.2000

        self.assertEqual(H.size, (9, 9))
        self.assertAlmostEqual(H[0, 0], H_0_0, places)
        self.assertAlmostEqual(H[8, 5], H_8_5, places)
        self.assertAlmostEqual(H[2, 7], H_2_7, places)
        self.assertAlmostEqual(H[6, 6], H_6_6, places)
        self.assertAlmostEqual(H[8, 8], H_8_8, places)

        c_0 = 0.0000
        c_5 = 0.0000
        c_7 = 1.0333e+03
        c_8 = 1.0833e+03

        self.assertEqual(c.size, (9, 1))
        self.assertAlmostEqual(c[0], c_0, places)
        self.assertAlmostEqual(c[5], c_5, places)
        self.assertAlmostEqual(c[7], c_7, places)
        self.assertAlmostEqual(c[8], c_8, places)


    def test_solver_output(self):
        """ Test the output from the solver.

            x =

                     0
               -0.0052
               -0.0049
               -0.0521
               -0.0640
               -0.0539
                0.5000
                0.8807
                0.7193
        """
        x = self.routine.x

        places = 4

        x_0 = 0.0000 # Va_ref
        x_2 = -0.0049
        x_5 = -0.0539
        x_6 = 0.5000 # Pg[0]
        x_7 = 0.8807

        self.assertEqual(x.size, (9, 1))
        self.assertAlmostEqual(x[0], x_0, places)
        self.assertAlmostEqual(x[2], x_2, places)
        self.assertAlmostEqual(x[5], x_5, places)
        self.assertAlmostEqual(x[6], x_6, places)
        self.assertAlmostEqual(x[7], x_7, places)


    def test_model_update(self):
        """ Test update of the model with the results.
        """
        pass

if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
