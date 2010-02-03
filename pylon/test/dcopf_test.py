#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

import unittest
from os.path import join, dirname

from pylon import Case, DCOPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")
PWL_FILE  = join(dirname(__file__), "data", "case30pwl.pkl")

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
        case = self.case = Case.load(PWL_FILE)

        self.solver = DCOPF(case, show_progress=False)


    def test_cost_model(self):
        """ Test selection of quadratic solver for pwl cost model.
        """
        _, _, g, _, _, _, _ = self.solver._unpack_case(self.case)
        self.assertTrue(self.solver._linear_formulation(g))


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
        b, _, g, _, _, _, base_mva = self.solver._unpack_case(self.case)
        linear = self.solver._linear_formulation(g)

        x0 = self.solver._initial_x(b, g, base_mva, linear)

        places = 4

        self.assertEqual(len(x0), 42)

        self.assertAlmostEqual(x0[0], 0.0, places)
        self.assertAlmostEqual(x0[29], 0.0, places)
        self.assertAlmostEqual(x0[30], 0.2354, places)
        self.assertAlmostEqual(x0[35], 0.3700, places)
        self.assertAlmostEqual(x0[37], 3393.5, places=1)
        self.assertAlmostEqual(x0[41], 1084.0, places=1)


    def test_cost_constraints(self):
        """ Test the piecewise linear DC OPF cost constaints.

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
        _, _, g, nb, _, ng, base_mva = self.solver._unpack_case(self.case)
        linear = self.solver._linear_formulation(g)

        Acc, bcc = self.solver._generator_cost(g, nb, ng, base_mva, linear)

        self.assertEqual(Acc.size, (18, 42))
        self.assertEqual(bcc.size, (18, 1))

        places = 1

        self.assertAlmostEqual(Acc[0, 30], 1200.0, places)
        self.assertAlmostEqual(Acc[8, 32], 8400.0, places)
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


    def test_ref_bus_phase_angle_constraint(self):
        """ Test reference bus phase angle constraint.

            Aref =

          Columns 1 through 13

             1     0     0     0     0     0     0     0     0     0     0     0     0

          Columns 14 through 26

             0     0     0     0     0     0     0     0     0     0     0     0     0

          Columns 27 through 39

             0     0     0     0     0     0     0     0     0     0     0     0     0

          Columns 40 through 42

             0     0     0

            bref =

                 0
        """
        b, _, g, nb, _, ng, _ = self.solver._unpack_case(self.case)
        linear = self.solver._linear_formulation(g)

        Aref, bref = self.solver._reference_angle(b, g, nb, ng, linear)

        places = 4
        self.assertEqual(Aref.size, (1, 42))
        self.assertAlmostEqual(Aref[0], 1.0000, places)
        self.assertAlmostEqual(Aref[8], 0.0000, places)

        self.assertEqual(bref.size, (1, 1))
        self.assertAlmostEqual(bref[0], 0.0000, places)


    def test_power_balance_constraint(self):
        """ Test piecewise linear power balance (mismatch) constraint.

        Amis =

           (1,1)      21.9298
           (2,1)     -16.6667
           (3,1)      -5.2632
           (1,2)     -16.6667
           (2,2)      33.1046
           (4,2)      -5.8824
           (5,2)      -5.0000
           (6,2)      -5.5556
           (1,3)      -5.2632
           (3,3)      30.2632
           (4,3)     -25.0000
           (2,4)      -5.8824
           (3,4)     -25.0000
           (4,4)      59.7285
           (6,4)     -25.0000
          (12,4)      -3.8462
           (2,5)      -5.0000
           (5,5)      13.3333
           (7,5)      -8.3333
           (2,6)      -5.5556
           (4,6)     -25.0000
           (6,6)      91.2698
           (7,6)     -12.5000
           (8,6)     -25.0000
           (9,6)      -4.7619
          (10,6)      -1.7857
          (28,6)     -16.6667
           (5,7)      -8.3333
           (6,7)     -12.5000
           (7,7)      20.8333
           (6,8)     -25.0000
           (8,8)      30.0000
          (28,8)      -5.0000
           (6,9)      -4.7619
           (9,9)      18.6147
          (10,9)      -9.0909
          (11,9)      -4.7619
           (6,10)     -1.7857
           (9,10)     -9.0909
          (10,10)     49.0909
          (17,10)    -12.5000
          (20,10)     -4.7619
          (21,10)    -14.2857
          (22,10)     -6.6667
           (9,11)     -4.7619
          (11,11)      4.7619
           (4,12)     -3.8462
          (12,12)     27.5275
          (13,12)     -7.1429
          (14,12)     -3.8462
          (15,12)     -7.6923
          (16,12)     -5.0000
          (12,13)     -7.1429
          (13,13)      7.1429
          (12,14)     -3.8462
          (14,14)      8.8462
          (15,14)     -5.0000
          (12,15)     -7.6923
          (14,15)     -5.0000
          (15,15)     22.2378
          (18,15)     -4.5455
          (23,15)     -5.0000
          (12,16)     -5.0000
          (16,16)     10.2632
          (17,16)     -5.2632
          (10,17)    -12.5000
          (16,17)     -5.2632
          (17,17)     17.7632
          (15,18)     -4.5455
          (18,18)     12.2378
          (19,18)     -7.6923
          (18,19)     -7.6923
          (19,19)     21.9780
          (20,19)    -14.2857
          (10,20)     -4.7619
          (19,20)    -14.2857
          (20,20)     19.0476
          (10,21)    -14.2857
          (21,21)     64.2857
          (22,21)    -50.0000
          (10,22)     -6.6667
          (21,22)    -50.0000
          (22,22)     62.2222
          (24,22)     -5.5556
          (15,23)     -5.0000
          (23,23)      8.7037
          (24,23)     -3.7037
          (22,24)     -5.5556
          (23,24)     -3.7037
          (24,24)     12.2896
          (25,24)     -3.0303
          (24,25)     -3.0303
          (25,25)     10.4238
          (26,25)     -2.6316
          (27,25)     -4.7619
          (25,26)     -2.6316
          (26,26)      2.6316
          (25,27)     -4.7619
          (27,27)     11.3095
          (28,27)     -2.5000
          (29,27)     -2.3810
          (30,27)     -1.6667
           (6,28)    -16.6667
           (8,28)     -5.0000
          (27,28)     -2.5000
          (28,28)     24.1667
          (27,29)     -2.3810
          (29,29)      4.6032
          (30,29)     -2.2222
          (27,30)     -1.6667
          (29,30)     -2.2222
          (30,30)      3.8889
           (1,31)     -1.0000
           (2,32)     -1.0000
          (22,33)     -1.0000
          (27,34)     -1.0000
          (23,35)     -1.0000
          (13,36)     -1.0000

        bmis =

                 0
           -0.2170
           -0.0240
           -0.0760
                 0
                 0
           -0.2280
           -0.3000
                 0
           -0.0580
                 0
           -0.1120
                 0
           -0.0620
           -0.0820
           -0.0350
           -0.0900
           -0.0320
           -0.0950
           -0.0220
           -0.1750
                 0
           -0.0320
           -0.0870
                 0
           -0.0350
                 0
                 0
           -0.0240
           -0.1060

        """
        b, _, g, nb, _, ng, base_mva = self.solver._unpack_case(self.case)
        linear = self.solver._linear_formulation(g)
        B, _, Pbusinj, _ = self.case.Bdc

        Amis, bmis = self.solver._power_balance(B, Pbusinj, b, g, nb, ng,
                                                base_mva, linear)

        self.assertEqual(Amis.size, (30, 42))

        places = 4
        self.assertAlmostEqual(Amis[0, 0], 21.9298, places)
        self.assertAlmostEqual(Amis[2, 2], 30.2632, places) # B diagonal
        self.assertAlmostEqual(Amis[4, 6], -8.3333, places) # Off-diagonal

        self.assertAlmostEqual(Amis[20, 20], 64.2857, places)
        self.assertAlmostEqual(Amis[29, 26], -1.6667, places)
        self.assertAlmostEqual(Amis[21, 32], -1.0000, places)

        self.assertEqual(bmis.size, (30, 1))
        self.assertAlmostEqual(bmis[0], 0.0000, places)
        self.assertAlmostEqual(bmis[1], -0.217, places)
        self.assertAlmostEqual(bmis[16], -0.09, places)
        self.assertAlmostEqual(bmis[29], -0.1060, places)


    def test_generator_limit_constraints(self):
        """ Test the pwl upper and lower generator output constraints.

        Agen =

           (1,31)      -1
           (7,31)       1
           (2,32)      -1
           (8,32)       1
           (3,33)      -1
           (9,33)       1
           (4,34)      -1
          (10,34)       1
           (5,35)      -1
          (11,35)       1
           (6,36)      -1
          (12,36)       1

        bgen =

            0
            0
            0
            0
            0
            0
            0.8000
            0.8000
            0.5000
            0.5500
            0.3000
            0.4000
        """
        _, _, g, nb, _, ng, base_mva = self.solver._unpack_case(self.case)
        linear = self.solver._linear_formulation(g)

        Agen, bgen = self.solver._generation_limit(g, nb, ng, base_mva, linear)

        places = 4
        self.assertEqual(Agen.size, (12, 42))
        self.assertAlmostEqual(Agen[0, 0], 0.0, places)
        self.assertAlmostEqual(Agen[0, 30], -1.0, places)
        self.assertAlmostEqual(Agen[1, 31], -1.0, places)
        self.assertAlmostEqual(Agen[10, 34], 1.0, places)
        self.assertAlmostEqual(Agen[11, 35], 1.0, places)

        self.assertEqual(bgen.size, (12, 1))
        self.assertAlmostEqual(bgen[0], 0.0, places)
        self.assertAlmostEqual(bgen[5], 0.0, places)
        self.assertAlmostEqual(bgen[6], 0.80, places)
        self.assertAlmostEqual(bgen[9], 0.55, places)


    def test_branch_flow_limit_constraints(self):
        """ Test branch maximum flow limit constraints.

            Aflow =

               (1,1)      16.6667
               (2,1)       5.2632
              (42,1)     -16.6667
              (43,1)      -5.2632
               (1,2)     -16.6667
               (3,2)       5.8824
               (5,2)       5.0000
               (6,2)       5.5556
              (42,2)      16.6667
              (44,2)      -5.8824
              (46,2)      -5.0000
              (47,2)      -5.5556
               (2,3)      -5.2632
               (4,3)      25.0000
              (43,3)       5.2632
              (45,3)     -25.0000
               (3,4)      -5.8824
               (4,4)     -25.0000
               (7,4)      25.0000
              (15,4)       3.8462
              (44,4)       5.8824
              (45,4)      25.0000
              (48,4)     -25.0000
              (56,4)      -3.8462
               (5,5)      -5.0000
               (8,5)       8.3333
              (46,5)       5.0000
              (49,5)      -8.3333
               (6,6)      -5.5556
               (7,6)     -25.0000
               (9,6)      12.5000
              (10,6)      25.0000
              (11,6)       4.7619
              (12,6)       1.7857
              (41,6)      16.6667
              (47,6)       5.5556
              (48,6)      25.0000
              (50,6)     -12.5000
              (51,6)     -25.0000
              (52,6)      -4.7619
              (53,6)      -1.7857
              (82,6)     -16.6667
               (8,7)      -8.3333
               (9,7)     -12.5000
              (49,7)       8.3333
              (50,7)      12.5000
              (10,8)     -25.0000
              (40,8)       5.0000
              (51,8)      25.0000
              (81,8)      -5.0000
              (11,9)      -4.7619
              (13,9)       4.7619
              (14,9)       9.0909
              (52,9)       4.7619
              (54,9)      -4.7619
              (55,9)      -9.0909
              (12,10)     -1.7857
              (14,10)     -9.0909
              (25,10)      4.7619
              (26,10)     12.5000
              (27,10)     14.2857
              (28,10)      6.6667
              (53,10)      1.7857
              (55,10)      9.0909
              (66,10)     -4.7619
              (67,10)    -12.5000
              (68,10)    -14.2857
              (69,10)     -6.6667
              (13,11)     -4.7619
              (54,11)      4.7619
              (15,12)     -3.8462
              (16,12)      7.1429
              (17,12)      3.8462
              (18,12)      7.6923
              (19,12)      5.0000
              (56,12)      3.8462
              (57,12)     -7.1429
              (58,12)     -3.8462
              (59,12)     -7.6923
              (60,12)     -5.0000
              (16,13)     -7.1429
              (57,13)      7.1429
              (17,14)     -3.8462
              (20,14)      5.0000
              (58,14)      3.8462
              (61,14)     -5.0000
              (18,15)     -7.6923
              (20,15)     -5.0000
              (22,15)      4.5455
              (30,15)      5.0000
              (59,15)      7.6923
              (61,15)      5.0000
              (63,15)     -4.5455
              (71,15)     -5.0000
              (19,16)     -5.0000
              (21,16)      5.2632
              (60,16)      5.0000
              (62,16)     -5.2632
              (21,17)     -5.2632
              (26,17)    -12.5000
              (62,17)      5.2632
              (67,17)     12.5000
              (22,18)     -4.5455
              (23,18)      7.6923
              (63,18)      4.5455
              (64,18)     -7.6923
              (23,19)     -7.6923
              (24,19)     14.2857
              (64,19)      7.6923
              (65,19)    -14.2857
              (24,20)    -14.2857
              (25,20)     -4.7619
              (65,20)     14.2857
              (66,20)      4.7619
              (27,21)    -14.2857
              (29,21)     50.0000
              (68,21)     14.2857
              (70,21)    -50.0000
              (28,22)     -6.6667
              (29,22)    -50.0000
              (31,22)      5.5556
              (69,22)      6.6667
              (70,22)     50.0000
              (72,22)     -5.5556
              (30,23)     -5.0000
              (32,23)      3.7037
              (71,23)      5.0000
              (73,23)     -3.7037
              (31,24)     -5.5556
              (32,24)     -3.7037
              (33,24)      3.0303
              (72,24)      5.5556
              (73,24)      3.7037
              (74,24)     -3.0303
              (33,25)     -3.0303
              (34,25)      2.6316
              (35,25)      4.7619
              (74,25)      3.0303
              (75,25)     -2.6316
              (76,25)     -4.7619
              (34,26)     -2.6316
              (75,26)      2.6316
              (35,27)     -4.7619
              (36,27)     -2.5000
              (37,27)      2.3810
              (38,27)      1.6667
              (76,27)      4.7619
              (77,27)      2.5000
              (78,27)     -2.3810
              (79,27)     -1.6667
              (36,28)      2.5000
              (40,28)     -5.0000
              (41,28)    -16.6667
              (77,28)     -2.5000
              (81,28)      5.0000
              (82,28)     16.6667
              (37,29)     -2.3810
              (39,29)      2.2222
              (78,29)      2.3810
              (80,29)     -2.2222
              (38,30)     -1.6667
              (39,30)     -2.2222
              (79,30)      1.6667
              (80,30)      2.2222

              bflow =

                    1.3000
                    1.3000
                    0.6500
                    1.3000
                    1.3000
                    0.6500
                    0.9000
                    0.7000
                    1.3000
                    0.3200
                    0.6500
                    0.3200
                    0.6500
                    0.6500
                    0.6500
                    0.6500
                    0.3200
                    0.3200
                    0.3200
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.3200
                    0.3200
                    0.3200
                    0.3200
                    0.3200
                    0.3200
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.6500
                    0.1600
                    0.1600
                    0.1600
                    0.3200
                    0.3200
                    1.3000
                    1.3000
                    0.6500
                    1.3000
                    1.3000
                    0.6500
                    0.9000
                    0.7000
                    1.3000
                    0.3200
                    0.6500
                    0.3200
                    0.6500
                    0.6500
                    0.6500
                    0.6500
                    0.3200
                    0.3200
                    0.3200
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.3200
                    0.3200
                    0.3200
                    0.3200
                    0.3200
                    0.3200
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.1600
                    0.6500
                    0.1600
                    0.1600
                    0.1600
                    0.3200
                    0.3200
        """
        _, l, g, _, nl, ng, base_mva = self.solver._unpack_case(self.case)
        linear = self.solver._linear_formulation(g)
        _, Bf, _, Pfinj = self.case.Bdc

        Aflow, bflow = self.solver._branch_flow(Bf, Pfinj, g, ng, l, nl,
                                         base_mva, linear)

        places = 4
        self.assertEqual(Aflow.size, (82, 42))
        self.assertAlmostEqual(Aflow[0, 0], 16.6667, places)
        self.assertAlmostEqual(Aflow[2, 1], 5.8824, places)
        self.assertAlmostEqual(Aflow[45, 1], -5.0000, places)

        self.assertEqual(bflow.size, (82, 1))
        self.assertAlmostEqual(bflow[0], 1.3000, places)
        self.assertAlmostEqual(bflow[81], 0.3200, places)


    def test_objective_function(self):
        """ Test pwl objective function.
        """
        _, _, g, nb, _, ng, base_mva = self.solver._unpack_case(self.case)
        linear = self.solver._linear_formulation(g)

        H, c = self.solver._objective_function(g, nb, ng, base_mva, linear)

        self.assertEqual(H.size, (42, 42))
        self.assertEqual(sum(H), 0.0)

        self.assertEqual(c.size, (42, 1))
        self.assertEqual(c[0], 0.0)
        self.assertEqual(c[36], 1.0)
        self.assertEqual(c[41], 1.0)


    def test_solver_output(self):
        """ Test the output from the solver.

            x =

            1.0e+03 *

                0.0000 # Va_ref
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
                0.0004 # Pg[1]
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
#        self.solver.solver = "glpk"
#        self.solver.solver = "mosek"
        self.solver.solve()
        x = self.solver._solution["x"]

        # Total system cost ($/h).
        self.assertAlmostEqual(self.solver._f, 5732.80, 2)

        places = 1 # FIXME: Improve accuracy.
        self.assertEqual(x.size, (42, 1))
        self.assertAlmostEqual(x[0], 0.0000, places) # Va[0]
        self.assertAlmostEqual(x[29], 0.0000, places)

        self.assertAlmostEqual(x[30], 0.3600, places) # Pg[0]
        self.assertAlmostEqual(x[31], 0.3143, places)
        self.assertAlmostEqual(x[32], 0.2963, places)
        self.assertAlmostEqual(x[33], 0.3600, places)
        self.assertAlmostEqual(x[34], 0.2014, places)
        self.assertAlmostEqual(x[35], 0.3600, places)

        self.assertAlmostEqual(x[36], 1.0080e03, places) # y[0]
#        self.assertAlmostEqual(x[37], 1.0948e03, places)
#        self.assertAlmostEqual(x[38], 1.0159e03, places)
        self.assertAlmostEqual(x[39], 1.0080e03, places)
#        self.assertAlmostEqual(x[40], 0.5981e03, places)
        self.assertAlmostEqual(x[41], 1.0080e03, places)

#------------------------------------------------------------------------------
#  "DCOPFTest" class:
#------------------------------------------------------------------------------

#class DCOPFTest(unittest.TestCase):
#    """ Uses a MATPOWER data file and validates the results against those
#        obtained from running the MATPOWER rundcopf.m script with the same
#        file.
#
#        See reader_test_case.py for MATPOWER data file parsing tests.
#        See y_test_case.py for testing the susceptance matrix.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        case = self.case = Case.load(DATA_FILE)
#
#        self.routine = DCOPF(case, show_progress=False)
#
#
#    def test_theta_injection_from(self):
#        """ Test phase shift 'quiescent' injections, used for calculating
#            branch real power flows at the from end.
#
#            Pfinj =
#
#                 0  0  0  0  0  0  0  0  0  0  0
#        """
#        theta_inj = self.routine._get_theta_inj_from()
#
#        self.assertEqual(len(theta_inj), 11)
#        # FIXME: Repeat for a case with transformers or shunt capacitors.
#        self.assertEqual(theta_inj[0], 0.0)
#        self.assertEqual(theta_inj[10], 0.0)
#
#
#    def test_theta_injection_bus(self):
#        """ Test phase shift injection vector used for bus real power
#            injection calculation.
#
#            Pbusinj =
#
#                 0  0  0  0  0  0
#        """
#        self.routine._theta_inj_from = self.routine._get_theta_inj_from()
#
#        theta_inj = self.routine._get_theta_inj_bus()
#
#        self.assertEqual(len(theta_inj), 6)
#        # FIXME: Require a case with transformers or shunt capacitors.
#        self.assertEqual(theta_inj[0], 0.0)
#        self.assertEqual(theta_inj[5], 0.0)
#
#
#    def test_cost_model(self):
#        """ Test selection of quadratic solver for polynomial cost model.
#        """
#        solver_type = self.routine._get_solver_type()
#        self.assertEqual(solver_type, "quadratic")
#
#
#    def test_x_vector(self):
#        """ Test the the x vector where AA * x <= bb.
#
#            x =
#
#                 0  0  0  0  0  0  0  0.5000  0.6000
#        """
#        self.routine._solver_type = self.routine._get_solver_type()
#        x = self.routine._get_x()
#
#        places = 4
#
#        x_2 = 0.0000
#        x_7 = 0.5000
#        x_8 = 0.6000
#
#        self.assertEqual(len(x), 9)
#        self.assertAlmostEqual(x[2], x_2, places)
#        self.assertAlmostEqual(x[7], x_7, places)
#        self.assertAlmostEqual(x[8], x_8, places)
#
#
#    def test_cost_constraints(self):
#        """ Test the DC OPF cost constaints.
#        """
#        self.routine._solver_type = self.routine._get_solver_type()
#
#        Acc, bcc = self.routine._get_cost_constraint()
##        bcc = self.routine._bb_cost
#
#        self.assertEqual(Acc.size, (0, 9))
#        self.assertEqual(bcc.size, (0, 1))
#
#
#    def test_ref_bus_phase_angle_constraint(self):
#        """ Test reference bus phase angle constraint.
#
#            Aref =
#
#                 1     0     0     0     0     0     0     0     0
#
#            bref =
#
#                 0
#        """
#        self.routine._solver_type = self.routine._get_solver_type()
#
#        Aref, bref = self.routine._get_reference_angle_constraint()
##        bref = self.routine._bb_ref
#
#        places = 4
#
#        Aref_0 = 1.0000
#        Aref_8 = 0.0000
#
#        self.assertEqual(Aref.size, (1, 9))
#        self.assertAlmostEqual(Aref[0], Aref_0, places)
#        self.assertAlmostEqual(Aref[8], Aref_8, places)
#
#        bref_0 = 0.0000
#
#        self.assertEqual(bref.size, (1, 1))
#        self.assertAlmostEqual(bref[0], bref_0, places)
#
#
#    def test_power_balance_constraint(self):
#        """ Test power balance (mismatch) constraint.
#
#            A_mismatch =
#
#               13.3333   -5.0000         0   -5.0000   -3.3333         0   ...
#               -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000   ...
#                     0   -4.0000   17.8462         0   -3.8462  -10.0000   ...
#               -5.0000  -10.0000         0   17.5000   -2.5000         0   ...
#               -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333   ...
#                     0   -5.0000  -10.0000         0   -3.3333   18.3333   ...
#
#            b_mismatch =
#
#                     0
#                     0
#                     0
#               -0.7000
#               -0.7000
#               -0.7000
#        """
#        self.routine.B, self.routine.Bf, _, _ = self.case.Bdc
#
#        self.routine._solver_type = self.routine._get_solver_type()
#
#        self.routine._theta_inj_from = self.routine._get_theta_inj_from()
#        self.routine._theta_inj_bus = self.routine._get_theta_inj_bus()
#
#        A_mis, b_mis = self.routine._get_active_power_flow_equations()
##        b_mismatch = self.routine._bb_mismatch
#
#        places = 4
#
#        A_1_1 = 27.3333
#        A_4_2 = -3.8462
#
#        A_0_6 = -1.0000
#        A_2_8 = -1.0000
#        A_5_8 = 0.0000
#
#        self.assertEqual(A_mis.size, (6, 9)) # Size
#        # See y_test_case.py for full susceptance matrix test case.
#        self.assertAlmostEqual(A_mis[1, 1], A_1_1, places) # B diagonal
#        self.assertAlmostEqual(A_mis[4, 2], A_4_2, places) # Off-diagonal
#
#        self.assertAlmostEqual(A_mis[0, 6], A_0_6, places)
#        self.assertAlmostEqual(A_mis[2, 8], A_2_8, places)
#        self.assertAlmostEqual(A_mis[5, 8], A_5_8, places)
#
#        b_0 = 0.0000
#        b_3 = -0.7000
#        b_5 = -0.7000
#
#        self.assertEqual(b_mis.size, (6, 1))
#        self.assertAlmostEqual(b_mis[0], b_0, places)
#        self.assertAlmostEqual(b_mis[3], b_3, places)
#        self.assertAlmostEqual(b_mis[5], b_5, places)
#
#
#    def test_generator_limit_constraints(self):
#        """ Test the upper and lower generator output constraints.
#
#            A_gen =
#
#                 0     0     0     0     0     0    -1     0     0
#                 0     0     0     0     0     0     0    -1     0
#                 0     0     0     0     0     0     0     0    -1
#                 0     0     0     0     0     0     1     0     0
#                 0     0     0     0     0     0     0     1     0
#                 0     0     0     0     0     0     0     0     1
#
#            b_gen =
#
#               -0.5000
#               -0.3750
#               -0.4500
#                2.0000
#                1.5000
#                1.8000
#        """
#        self.routine._solver_type = self.routine._get_solver_type()
#
#        A_gen, b_gen = self.routine._get_generation_limit_constraint()
##        b_gen = self.routine._bb_generation
#
#        places = 4
#
#        A_0_0 = 0.0000
#        A_5_5 = 0.0000
#
#        A_0_6 = -1.0000
#        A_2_6 = 0.0000
#        A_2_8 = -1.0000
#
#        A_3_6 = 1.0000
#        A_5_6 = 0.0000
#        A_5_8 = 1.0000
#
#        self.assertEqual(A_gen.size, (6, 9))
#        self.assertAlmostEqual(A_gen[0, 0], A_0_0, places)
#        self.assertAlmostEqual(A_gen[5, 5], A_5_5, places)
#        self.assertAlmostEqual(A_gen[0, 6], A_0_6, places)
#        self.assertAlmostEqual(A_gen[2, 6], A_2_6, places)
#        self.assertAlmostEqual(A_gen[2, 8], A_2_8, places)
#        self.assertAlmostEqual(A_gen[3, 6], A_3_6, places)
#        self.assertAlmostEqual(A_gen[5, 6], A_5_6, places)
#        self.assertAlmostEqual(A_gen[5, 8], A_5_8, places)
#
#        b_0 = -0.5000
#        b_2 = -0.4500
#        b_4 = 1.5000
#        b_5 = 1.8000
#
#        self.assertEqual(b_gen.size, (6, 1))
#        self.assertAlmostEqual(b_gen[0], b_0, places)
#        self.assertAlmostEqual(b_gen[2], b_2, places)
#        self.assertAlmostEqual(b_gen[4], b_4, places)
#        self.assertAlmostEqual(b_gen[5], b_5, places)
#
#
#    def test_branch_flow_limit_constraints(self):
#        """ Test branch maximum flow limit constraints.
#
#            A_flow =
#
#                5.0000   -5.0000         0         0         0         0   ...
#                5.0000         0         0   -5.0000         0         0   ...
#                3.3333         0         0         0   -3.3333         0   ...
#                     0    4.0000   -4.0000         0         0         0   ...
#                     0   10.0000         0  -10.0000         0         0   ...
#                     0    3.3333         0         0   -3.3333         0   ...
#                     0    5.0000         0         0         0   -5.0000   ...
#                     0         0    3.8462         0   -3.8462         0   ...
#                     0         0   10.0000         0         0  -10.0000   ...
#                     0         0         0    2.5000   -2.5000         0   ...
#                     0         0         0         0    3.3333   -3.3333   ...
#
#               -5.0000    5.0000         0         0         0         0   ...
#               -5.0000         0         0    5.0000         0         0   ...
#               -3.3333         0         0         0    3.3333         0   ...
#                     0   -4.0000    4.0000         0         0         0   ...
#                     0  -10.0000         0   10.0000         0         0   ...
#                     0   -3.3333         0         0    3.3333         0   ...
#                     0   -5.0000         0         0         0    5.0000   ...
#                     0         0   -3.8462         0    3.8462         0   ...
#                     0         0  -10.0000         0         0   10.0000   ...
#                     0         0         0   -2.5000    2.5000         0   ...
#                     0         0         0         0   -3.3333    3.3333   ...
#
#            b_flow =
#
#                0.4000
#                0.6000
#                0.4000
#                0.4000
#                0.6000
#                0.3000
#                0.9000
#                0.7000
#                0.8000
#                0.2000
#                0.4000
#
#                0.4000
#                0.6000
#                0.4000
#                0.4000
#                0.6000
#                0.3000
#                0.9000
#                0.7000
#                0.8000
#                0.2000
#                0.4000
#        """
#        self.routine.B, self.routine.Bf, _, _ = self.case.Bdc
#
#        self.routine._solver_type = self.routine._get_solver_type()
#
#        self.routine._theta_inj_from = self.routine._get_theta_inj_from()
#
#        A_flow, b_flow = self.routine._get_branch_flow_limit_constraint()
##        b_flow = self.routine._bb_flow
#
#        places = 4
#
#        A_0_0 = 5.0000
#        A_2_4 = -3.3333
#        A_4_1 = 10.0000
#        A_7_4 = -3.8462
#        A_0_6 = 0.0000
#        A_9_8 = 0.0000
#
#        A_11_0 = -A_0_0
#        A_13_4 = -A_2_4
#        A_18_4 = -A_7_4
#        A_20_8 = 0.0000
#
#        self.assertEqual(A_flow.size, (22, 9))
#        self.assertAlmostEqual(A_flow[0, 0], A_0_0, places)
#        self.assertAlmostEqual(A_flow[2, 4], A_2_4, places)
#        self.assertAlmostEqual(A_flow[4, 1], A_4_1, places)
#        self.assertAlmostEqual(A_flow[7, 4], A_7_4, places)
#        self.assertAlmostEqual(A_flow[0, 6], A_0_6, places)
#        self.assertAlmostEqual(A_flow[9, 8], A_9_8, places)
#
#        self.assertAlmostEqual(A_flow[11, 0], A_11_0, places)
#        self.assertAlmostEqual(A_flow[13, 4], A_13_4, places)
#        self.assertAlmostEqual(A_flow[18, 4], A_18_4, places)
#        self.assertAlmostEqual(A_flow[20, 8], A_20_8, places)
#
#        b_0 = 0.4000
#        b_6 = 0.9000
#        b_12 = 0.6000
#        b_19 = 0.8000
#
#        self.assertEqual(b_flow.size, (22, 1))
#        self.assertAlmostEqual(b_flow[0], b_0, places)
#        self.assertAlmostEqual(b_flow[6], b_6, places)
#        self.assertAlmostEqual(b_flow[12], b_12, places)
#        self.assertAlmostEqual(b_flow[19], b_19, places)
#
#
#    def test_objective_function(self):
#        """ Test objective function of the form: 0.5 * x'*H*x + c'*x
#
#            H =
#
#                 ...      0         0         0         0         0         0
#                 ...      0         0         0         0         0         0
#                 ...      0         0         0         0         0         0
#                 ...      0         0         0         0         0         0
#                 ...      0         0         0         0         0         0
#                 ...      0         0         0         0         0         0
#                 ...      0         0         0  106.6000         0         0
#                 ...      0         0         0         0  177.8000         0
#                 ...      0         0         0         0         0  148.2000
#
#            c =
#
#               1.0e+03 *
#
#                     0
#                     0
#                     0
#                     0
#                     0
#                     0
#                1.1669
#                1.0333
#                1.0833
#        """
#        self.routine._solver_type = self.routine._get_solver_type()
#
#        H = self.routine._get_hessian()
#        c = self.routine._get_c()
#
#        places = 4
#
#        H_0_0 = 0.0000
#        H_8_5 = 0.0000
#        H_2_7 = 0.0000
#        H_6_6 = 106.6000
#        H_8_8 = 148.2000
#
#        self.assertEqual(H.size, (9, 9))
#        self.assertAlmostEqual(H[0, 0], H_0_0, places)
#        self.assertAlmostEqual(H[8, 5], H_8_5, places)
#        self.assertAlmostEqual(H[2, 7], H_2_7, places)
#        self.assertAlmostEqual(H[6, 6], H_6_6, places)
#        self.assertAlmostEqual(H[8, 8], H_8_8, places)
#
#        c_0 = 0.0000
#        c_5 = 0.0000
#        c_7 = 1.0333e+03
#        c_8 = 1.0833e+03
#
#        self.assertEqual(c.size, (9, 1))
#        self.assertAlmostEqual(c[0], c_0, places)
#        self.assertAlmostEqual(c[5], c_5, places)
#        self.assertAlmostEqual(c[7], c_7, places)
#        self.assertAlmostEqual(c[8], c_8, places)
#
#
#    def test_solver_output(self):
#        """ Test the output from the solver.
#
#            x =
#
#                     0
#               -0.0052
#               -0.0049
#               -0.0521
#               -0.0640
#               -0.0539
#                0.5000
#                0.8807
#                0.7193
#        """
#        self.routine.solve()
#        x = self.routine.x
#
#        places = 4
#
#        x_0 = 0.0000 # Va_ref
#        x_2 = -0.0049
#        x_5 = -0.0539
#        x_6 = 0.5000 # Pg[0]
#        x_7 = 0.8807
#
#        self.assertEqual(x.size, (9, 1))
#        self.assertAlmostEqual(x[0], x_0, places)
#        self.assertAlmostEqual(x[2], x_2, places)
#        self.assertAlmostEqual(x[5], x_5, places)
#        self.assertAlmostEqual(x[6], x_6, places)
#        self.assertAlmostEqual(x[7], x_7, places)
#
#
#    def test_model_update(self):
#        """ Test update of the model with the results.
#        """
#        self.routine.solve()
#        self.assertAlmostEqual(self.routine.f, 3046.41, places=2)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    unittest.main()

# EOF -------------------------------------------------------------------------
