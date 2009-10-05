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

""" Test case for the DC Optimal Power Flow routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from pylon.readwrite import PickleReader
from pylon import DCOPF
from pylon.y import SusceptanceMatrix

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")
PWL_FILE  = join(dirname(__file__), "data", "case30pwl.pkl")

#MP_HOME = "/home/rwl/tmp/matpower3.2"
#PWL_FILE2 = join(MP_HOME, "case6pwl.pkl")
#
#class PiecewiseLinearDCOPFTest2(unittest.TestCase):
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        reader = MATPOWERReader()
#        self.case = reader(PWL_FILE2)
#
#        self.routine = DCOPF(show_progress=False)
##        success = self.routine(case)
#        self.routine.case = self.case
#
#
#    def test_solver_output(self):
#        """ Test the output from the solver with case6pwl input.
#        """
##        self.routine.solver = "glpk"
##        self.routine.solver = "mosek"
#        self.routine.solve(self.case)
#
##        print "\n", self.routine.x

#------------------------------------------------------------------------------
#  "PiecewiseLinearDCOPFTest" class:
#------------------------------------------------------------------------------

class PiecewiseLinearDCOPFTest(unittest.TestCase):
    """ Uses a MATPOWER data file with piecewise linear generator costs and
        validates the results against those obtained from running the MATPOWER
        rundcopf.m script with the same file.

        See reader_test_case.py for MATPOWER data file parsing tests.
        See y_test_case.py for testing the susceptance matrix.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(PWL_FILE)

        self.routine = DCOPF(show_progress=False)
#        success = self.routine(case)
        self.routine.case = self.case


    def test_cost_model(self):
        """ Test selection of quadratic solver for pwl cost model.
        """
        self.assertEqual(self.routine._solver_type, "linear")


    def test_x_vector(self):
        """ Test the the x vector where AA * x <= bb.

            x =

               1.0e+03 *

                     0 # [0]
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
                     0
                     0
                     0
                     0
                     0
                     0
                     0 # [29]
                0.0002
                0.0006
                0.0002
                0.0003
                0.0002
                0.0004
                0.5594
                3.3935
                0.6620
                0.6808
                0.5568
                1.0840
        """
        x = self.routine._get_x()

        places = 4

        0.2354
        0.6097
        0.2159
        0.2691
        0.1920
        0.3700

        x_0  = 0.0
        x_29 = 0.0

        x_31 = 0.6097
        x_33 = 0.2691
        x_34 = 0.1920

        x_37 = 3393.5
        x_40 = 556.8

        self.assertEqual(len(x), 42)

        self.assertAlmostEqual(x[0], x_0, places)
        self.assertAlmostEqual(x[29], x_29, places)

        # FIXME: In MATPOWER generators are ordered according to how they
        # appear in the data file. In PYLON they are ordered according to the
        # order of the buses to which they are connected.
        self.assertAlmostEqual(x[31], x_31, places)
#        self.assertAlmostEqual(x[33], x_33, places)
#        self.assertAlmostEqual(x[34], x_34, places)

        self.assertAlmostEqual(x[37], x_37, places=1)
#        self.assertAlmostEqual(x[40], x_40, places)


    def test_cost_constraints(self):
        """ Test the piecewise linear DC OPF cost constaints.
           1200           0           0           0           0           0          -1           0           0           0           0           0
           3600           0           0           0           0           0          -1           0           0           0           0           0
           7600           0           0           0           0           0          -1           0           0           0           0           0
              0        2000           0           0           0           0           0          -1           0           0           0           0
              0        4400           0           0           0           0           0          -1           0           0           0           0
              0        8400           0           0           0           0           0          -1           0           0           0           0
              0           0        2000           0           0           0           0           0          -1           0           0           0
              0           0        4400           0           0           0           0           0          -1           0           0           0
              0           0        8400           0           0           0           0           0          -1           0           0           0
              0           0           0        1200           0           0           0           0           0          -1           0           0
              0           0           0        3600           0           0           0           0           0          -1           0           0
              0           0           0        7600           0           0           0           0           0          -1           0           0
              0           0           0           0        2000           0           0           0           0           0          -1           0
              0           0           0           0        4400           0           0           0           0           0          -1           0
              0           0           0           0        8400           0           0           0           0           0          -1           0
              0           0           0           0           0        1200           0           0           0           0           0          -1
              0           0           0           0           0        3600           0           0           0           0           0          -1
              0           0           0           0           0        7600           0           0           0           0           0          -1

            Acc =

               (1,31)          1200
               (2,31)          3600
               (3,31)          7600
               (4,32)          2000
               (5,32)          4400
               (6,32)          8400
               (7,33)          2000
               (8,33)          4400
               (9,33)          8400
              (10,34)          1200
              (11,34)          3600
              (12,34)          7600
              (13,35)          2000
              (14,35)          4400
              (15,35)          8400
              (16,36)          1200
              (17,36)          3600
              (18,36)          7600
               (1,37)            -1
               (2,37)            -1
               (3,37)            -1
               (4,38)            -1
               (5,38)            -1
               (6,38)            -1
               (7,39)            -1
               (8,39)            -1
               (9,39)            -1
              (10,40)            -1
              (11,40)            -1
              (12,40)            -1
              (13,41)            -1
              (14,41)            -1
              (15,41)            -1
              (16,42)            -1
              (17,42)            -1
              (18,42)            -1


            bcc =

                       0
                     288
                    1728
                       0
                     288
                    1728
                       0
                     288
                    1728
                       0
                     288
                    1728
                       0
                     288
                    1728
                       0
                     288
                    1728
        """
        self.routine._solver_type = self.routine._get_solver_type()

        Acc, bcc = self.routine._get_cost_constraint()

        self.assertEqual(Acc.size, (18, 42))
        self.assertEqual(bcc.size, (18, 1))

        places = 1

        self.assertAlmostEqual(Acc[0, 30], 1200.0, places)
        # FIXME: In MATPOWER generators are ordered according to how they
        # appear in the data file. In PYLON they are ordered according to the
        # order of the buses to which they are connected.
#        self.assertAlmostEqual(Acc[8, 32], 8400.0, places)
        self.assertAlmostEqual(Acc[17, 35], 7600.0, places)

        self.assertAlmostEqual(Acc[0, 36], -1.0, places)
        self.assertAlmostEqual(Acc[1, 36], -1.0, places)
        self.assertAlmostEqual(Acc[2, 36], -1.0, places)
        self.assertAlmostEqual(Acc[0, 37], 0.0, places)
        self.assertAlmostEqual(Acc[0, 38], 0.0, places)

        self.assertAlmostEqual(Acc[15, 41], -1.0, places)
        self.assertAlmostEqual(Acc[16, 41], -1.0, places)
        self.assertAlmostEqual(Acc[17, 41], -1.0, places)

        self.assertAlmostEqual(bcc[0], 0.0, places)
        self.assertAlmostEqual(bcc[7], 288.0, places)
        self.assertAlmostEqual(bcc[17], 1728.0, places)


    def test_power_balance_constraint(self):
        """ Test piecewise linear power balance (mismatch) constraint.
        """
        susceptance = SusceptanceMatrix()
        self.routine.B, self.routine.Bsrc = susceptance(self.case)

        self.routine._solver_type = self.routine._get_solver_type()

        self.routine._theta_inj_source = self.routine._get_theta_inj_source()
        self.routine._theta_inj_bus = self.routine._get_theta_inj_bus()

        A_mis, b_mis = self.routine._get_active_power_flow_equations()

        self.assertEqual(A_mis.size, (30, 42))

        # See y_test_case.py for full susceptance matrix test case.
        self.assertAlmostEqual(A_mis[2, 2], 30.2632, places=4) # B diagonal
        self.assertAlmostEqual(A_mis[4, 6], -8.3333, places=4) # Off-diagonal

        # Bus-(online)generator incidence matrix.
        # FIXME: In MATPOWER generators are ordered according to how they
        # appear in the data file. In PYLON they are ordered according to the
        # order of the buses to which they are connected.
        self.assertAlmostEqual(A_mis[0, 30], -1.0, places=4)
        self.assertAlmostEqual(A_mis[22, 34], -1.0, places=4)

        # Zero matrix for pwl cost variables.
        self.assertEqual(sum(A_mis[:, -6:]), 0.0)


    def test_generator_limit_constraints(self):
        """ Test the pwl upper and lower generator output constraints.
        """
        self.routine._solver_type = self.routine._get_solver_type()

        A_gen, b_gen = self.routine._get_generation_limit_constraint()


        self.assertEqual(A_gen.size, (12, 42))
        self.assertAlmostEqual(A_gen[0, 0], 0.0, places=1)
        self.assertAlmostEqual(A_gen[0, 30], -1.0, places=1)

        self.assertEqual(b_gen.size, (12, 1))
        self.assertAlmostEqual(b_gen[0], 0.0, places=1)
        self.assertAlmostEqual(b_gen[6], 0.80, places=2)


#    def test_objective_function(self):
#        """ Test pwl objective function.
#        """
#        self.routine._solver_type = self.routine._get_solver_type()
#
#        H = self.routine._get_hessian()
#        c = self.routine._get_c()


    def test_solver_output(self):
        """ Test the output from the solver.

            x =

            1.0e+03 *

                0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
                0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0001
               -0.0001
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
               -0.0000
                0.0000
               -0.0000
               -0.0000
               -0.0000
                0.0004
                0.0003
                0.0003
                0.0004
                0.0002
                0.0004
                1.0080
                1.0948
                1.0159
                1.0080
                0.5981
                1.0080
        """
#        self.routine.solver = "glpk"
#        self.routine.solver = "mosek"
        self.routine.solve(self.case)
        x = self.routine.x

        places = 4

        x_0 = 0.0000 # Va_ref
        x_30 = 0.0004
        x_37 = 1.0948 # Pg[1]
        x_41 = 1.0080

#        self.assertEqual(x.size, (42, 1))

#------------------------------------------------------------------------------
#  "DCOPFTest" class:
#------------------------------------------------------------------------------

class DCOPFTest(unittest.TestCase):
    """ Uses a MATPOWER data file and validates the results against those
        obtained from running the MATPOWER rundcopf.m script with the same
        file.

        See reader_test_case.py for MATPOWER data file parsing tests.
        See y_test_case.py for testing the susceptance matrix.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)

        self.routine = DCOPF(show_progress=False)
        self.routine.case = self.case
#        success = self.routine(self.case)


    def test_theta_injection_source(self):
        """ Test phase shift 'quiescent' injections, used for calculating
            branch real power flows at the from end.

            Pfinj =

                 0  0  0  0  0  0  0  0  0  0  0
        """
        theta_inj = self.routine._get_theta_inj_source()

        self.assertEqual(len(theta_inj), 11)
        # FIXME: Repeat for a case with transformers or shunt capacitors.
        self.assertEqual(theta_inj[0], 0.0)
        self.assertEqual(theta_inj[10], 0.0)


    def test_theta_injection_bus(self):
        """ Test phase shift injection vector used for bus real power
            injection calculation.

            Pbusinj =

                 0  0  0  0  0  0
        """
        self.routine._theta_inj_source = self.routine._get_theta_inj_source()

        theta_inj = self.routine._get_theta_inj_bus()

        self.assertEqual(len(theta_inj), 6)
        # FIXME: Require a case with transformers or shunt capacitors.
        self.assertEqual(theta_inj[0], 0.0)
        self.assertEqual(theta_inj[5], 0.0)


    def test_cost_model(self):
        """ Test selection of quadratic solver for polynomial cost model.
        """
        solver_type = self.routine._get_solver_type()
        self.assertEqual(solver_type, "quadratic")


    def test_x_vector(self):
        """ Test the the x vector where AA * x <= bb.

            x =

                 0  0  0  0  0  0  0  0.5000  0.6000
        """
        self.routine._solver_type = self.routine._get_solver_type()
        x = self.routine._get_x()

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
        self.routine._solver_type = self.routine._get_solver_type()

        Acc, bcc = self.routine._get_cost_constraint()
#        bcc = self.routine._bb_cost

        self.assertEqual(Acc.size, (0, 9))
        self.assertEqual(bcc.size, (0, 1))


    def test_ref_bus_phase_angle_constraint(self):
        """ Test reference bus phase angle constraint.

            Aref =

                 1     0     0     0     0     0     0     0     0

            bref =

                 0
        """
        self.routine._solver_type = self.routine._get_solver_type()

        Aref, bref = self.routine._get_reference_angle_constraint()
#        bref = self.routine._bb_ref

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

               13.3333   -5.0000         0   -5.0000   -3.3333         0   ...
               -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000   ...
                     0   -4.0000   17.8462         0   -3.8462  -10.0000   ...
               -5.0000  -10.0000         0   17.5000   -2.5000         0   ...
               -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333   ...
                     0   -5.0000  -10.0000         0   -3.3333   18.3333   ...

            b_mismatch =

                     0
                     0
                     0
               -0.7000
               -0.7000
               -0.7000
        """
        susceptance = SusceptanceMatrix()
        self.routine.B, self.routine.Bsrc = susceptance(self.case)

        self.routine._solver_type = self.routine._get_solver_type()

        self.routine._theta_inj_source = self.routine._get_theta_inj_source()
        self.routine._theta_inj_bus = self.routine._get_theta_inj_bus()

        A_mis, b_mis = self.routine._get_active_power_flow_equations()
#        b_mismatch = self.routine._bb_mismatch

        places = 4

        A_1_1 = 27.3333
        A_4_2 = -3.8462

        A_0_6 = -1.0000
        A_2_8 = -1.0000
        A_5_8 = 0.0000

        self.assertEqual(A_mis.size, (6, 9)) # Size
        # See y_test_case.py for full susceptance matrix test case.
        self.assertAlmostEqual(A_mis[1, 1], A_1_1, places) # B diagonal
        self.assertAlmostEqual(A_mis[4, 2], A_4_2, places) # Off-diagonal

        self.assertAlmostEqual(A_mis[0, 6], A_0_6, places)
        self.assertAlmostEqual(A_mis[2, 8], A_2_8, places)
        self.assertAlmostEqual(A_mis[5, 8], A_5_8, places)

        b_0 = 0.0000
        b_3 = -0.7000
        b_5 = -0.7000

        self.assertEqual(b_mis.size, (6, 1))
        self.assertAlmostEqual(b_mis[0], b_0, places)
        self.assertAlmostEqual(b_mis[3], b_3, places)
        self.assertAlmostEqual(b_mis[5], b_5, places)


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
        self.routine._solver_type = self.routine._get_solver_type()

        A_gen, b_gen = self.routine._get_generation_limit_constraint()
#        b_gen = self.routine._bb_generation

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

                5.0000   -5.0000         0         0         0         0   ...
                5.0000         0         0   -5.0000         0         0   ...
                3.3333         0         0         0   -3.3333         0   ...
                     0    4.0000   -4.0000         0         0         0   ...
                     0   10.0000         0  -10.0000         0         0   ...
                     0    3.3333         0         0   -3.3333         0   ...
                     0    5.0000         0         0         0   -5.0000   ...
                     0         0    3.8462         0   -3.8462         0   ...
                     0         0   10.0000         0         0  -10.0000   ...
                     0         0         0    2.5000   -2.5000         0   ...
                     0         0         0         0    3.3333   -3.3333   ...

               -5.0000    5.0000         0         0         0         0   ...
               -5.0000         0         0    5.0000         0         0   ...
               -3.3333         0         0         0    3.3333         0   ...
                     0   -4.0000    4.0000         0         0         0   ...
                     0  -10.0000         0   10.0000         0         0   ...
                     0   -3.3333         0         0    3.3333         0   ...
                     0   -5.0000         0         0         0    5.0000   ...
                     0         0   -3.8462         0    3.8462         0   ...
                     0         0  -10.0000         0         0   10.0000   ...
                     0         0         0   -2.5000    2.5000         0   ...
                     0         0         0         0   -3.3333    3.3333   ...

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
        susceptance = SusceptanceMatrix()
        self.routine.B, self.routine.Bsrc = susceptance(self.case)

        self.routine._solver_type = self.routine._get_solver_type()

        self.routine._theta_inj_source = self.routine._get_theta_inj_source()

        A_flow, b_flow = self.routine._get_branch_flow_limit_constraint()
#        b_flow = self.routine._bb_flow

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

                 ...      0         0         0         0         0         0
                 ...      0         0         0         0         0         0
                 ...      0         0         0         0         0         0
                 ...      0         0         0         0         0         0
                 ...      0         0         0         0         0         0
                 ...      0         0         0         0         0         0
                 ...      0         0         0  106.6000         0         0
                 ...      0         0         0         0  177.8000         0
                 ...      0         0         0         0         0  148.2000

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
        self.routine._solver_type = self.routine._get_solver_type()

        H = self.routine._get_hessian()
        c = self.routine._get_c()

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
        self.routine(self.case)
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
        self.routine(self.case)
        self.assertAlmostEqual(self.routine.f, 3046.41, places=2)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    unittest.main()

# EOF -------------------------------------------------------------------------
