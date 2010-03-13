#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines a test case for AC power flow.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from os.path import join, dirname

from numpy import complex128, angle, abs

from pylon import Case, NewtonPF, FastDecoupledPF
from pylon.ac_pf import _ACPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "ACPFTest" class:
#------------------------------------------------------------------------------

class ACPFTest(unittest.TestCase):
    """ Test AC power flow results against those obtained with MATPOWER.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = self.case = Case.load(DATA_FILE)

        self.solver = _ACPF(case)


    def test_bus_indexing(self):
        """ Test the indexing of buses according their mode.
        """
        b, _, _, nb, nl, ng, _ = self.solver._unpack_case(self.case)

        self.assertEqual(nb, 6)
        self.assertEqual(nl, 11)
        self.assertEqual(ng, 3)

        refs, pq, pv, pvpq = self.solver._index_buses(b)

        self.assertEqual(len(refs), 1)
        self.assertEqual(len(pv), 2)
        self.assertEqual(len(pq), 3)
        self.assertEqual(len(pvpq), 5)

        self.assertEqual(pv[0], 1)
        self.assertEqual(pq[2], 5)
        self.assertEqual(pvpq[3], 4)


    def test_voltage_vector(self):
        """ Test the initial vector of complex bus voltages.
        """
        b, _, g, _, _, _, _ = self.solver._unpack_case(self.case)

        V0 = self.solver._initial_voltage(b, g)

        self.assertEqual(V0.dtype, complex128)
        self.assertEqual(V0.shape, (6,))

        places = 4
        # TODO: Repeat test for a case with generator voltage set points
        # different to the initial bus voltage magnitudes.
        self.assertAlmostEqual(abs(V0[0]), 1.0500, places)
        self.assertAlmostEqual(abs(V0[2]), 1.0700, places)
        self.assertAlmostEqual(abs(V0[5]), 1.0000, places)

#------------------------------------------------------------------------------
#  "NewtonPFTest" class:
#------------------------------------------------------------------------------

class NewtonPFTest(unittest.TestCase):
    """ Test power flow results using Newton's method against those obtained
        using MATPOWER.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = self.case = Case.load(DATA_FILE)

        self.solver = NewtonPF(case)


    def test_function_evaluation(self):
        """ Test function evaluation without iteration.
        """
        places = 4

        b, l, g, _, _, _, _ = self.solver._unpack_case(self.case)
        _, pq, pv, _ = self.solver._index_buses(b)

        V0 = self.solver._initial_voltage(b, g)
        Ybus, _, _ = self.case.getYbus(b, l)
        Sbus = self.case.getSbus(b)

        F = self.solver._evaluate_function(Ybus, V0, Sbus, pv, pq)

        self.assertEqual(F.shape, (8,))

        self.assertAlmostEqual(F[0],-0.1718, places)
        self.assertAlmostEqual(F[6], 0.0274, places)


    def test_convergence_check(self):
        """ Test convergence satisfaction check.

            normF =

                0.5061
        """
        solver = self.solver

        b, l, g, _, _, _, _ = self.solver._unpack_case(self.case)
        _, pq, pv, _ = self.solver._index_buses(b)
        V0 = self.solver._initial_voltage(b, g)
        Ybus, _, _ = self.case.getYbus(b, l)
        Sbus = self.case.getSbus(b)
        F = self.solver._evaluate_function(Ybus, V0, Sbus, pv, pq)

        # True negative
        solver.converged = False
        solver.tolerance = 0.500
        self.assertFalse(solver._check_convergence(F))

        # True positive
        solver.converged = False
        solver.tolerance = 0.510
        self.assertTrue(solver._check_convergence(F))


    def test_jacobian(self):
        """ Test creation of the Jacobian matrix.
        """
        b, _, g, _, _, _, _ = self.solver._unpack_case(self.case)
        _, pq, pv, pvpq = self.solver._index_buses(b)
        V0 = self.solver._initial_voltage(b, g)
        Ybus, _, _ = self.case.Y

        J = self.solver._build_jacobian(Ybus, V0, pv, pq, pvpq).tocsr()

        self.assertEqual(J.shape, (8, 8))

        places = 4
        self.assertAlmostEqual(J[0, 0], 24.9582, places)
        self.assertAlmostEqual(J[6, 3], -5.4872, places)
        self.assertAlmostEqual(J[3, 6],  5.0994, places)
        self.assertAlmostEqual(J[7, 1],  2.0577, places)
        self.assertAlmostEqual(J[0, 7], -1.6370, places)
        self.assertAlmostEqual(J[6, 7], -3.0000, places)


    def test_iteration(self):
        """ Test iteration of full Newton's method.
        """
        b, _, g, _, _, _, _ = self.solver._unpack_case(self.case)
        _, pq, pv, pvpq = self.solver._index_buses(b)
        V0 = self.solver._initial_voltage(b, g)
        Va0 = angle(V0)
        Vm0 = abs(V0)
        Sbus = self.case.Sbus
        Ybus, _, _ = self.case.Y

        # Initial evaluation of f(x0) and convergency check
        F = self.solver._evaluate_function(Ybus, V0, Sbus, pv, pq)
        V1, Vm1, Va1 = self.solver._one_iteration(F, Ybus, V0, Vm0, Va0,
                                                  pv, pq, pvpq)

        self.assertEqual(V1.shape, (6,))

        places = 4
        self.assertAlmostEqual(abs(V1[2]), abs(1.0672-0.0767j), places)
        self.assertAlmostEqual(abs(V1[4]), abs(0.9832-0.0884j), places)

        # Second iteration.
        F1 = self.solver._evaluate_function(Ybus, V1, Sbus, pv, pq)
        V2, _, _ = self.solver._one_iteration(F1, Ybus, V1, Vm1, Va1,
                                                  pv, pq, pvpq)

        self.assertAlmostEqual(abs(V2[1]), abs(1.0478-0.0672j), places)
        self.assertAlmostEqual(abs(V2[5]), abs(0.9990-0.1041j), places)


    def test_solution(self):
        """ Test resulting voltage vector.
        """
        result = self.solver.solve()
        V = result["V"]

        self.assertTrue(result["success"])
        self.assertEqual(result["iterations"], 3)

        places = 4
        self.assertAlmostEqual(abs(V[1]), abs(1.0478-0.0672j), places)
        self.assertAlmostEqual(abs(V[2]), abs(1.0670-0.0797j), places)
        self.assertAlmostEqual(abs(V[5]), abs(0.9990-0.1041j), places)

#------------------------------------------------------------------------------
#  "FDPFTest" class:
#------------------------------------------------------------------------------

class FDPFTest(unittest.TestCase):
    """ Test AC power flow results using fast decoupled method against those
        obtained using MATPOWER.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = self.case = Case.load(DATA_FILE)
        self.solver = FastDecoupledPF(case)


    def test_mismatch(self):
        """ Test FDPF mismatch evaluation.
        """
        b, _, g, _, _, _, _ = self.solver._unpack_case(self.case)
        _, pq, _, pvpq = self.solver._index_buses(b)
        V0 = self.solver._initial_voltage(b, g)
        Sbus = self.case.Sbus
        Ybus, _, _ = self.case.Y
        P, Q = self.solver._evaluate_mismatch(Ybus, V0, Sbus, pq, pvpq)

        self.assertEqual(P.shape, (5,))
        self.assertEqual(Q.shape, (3,))

        places = 4
        self.assertAlmostEqual(P[0],-0.1636, places)
        self.assertAlmostEqual(P[3], 0.5061, places)
        self.assertAlmostEqual(Q[0],-0.0053, places)
        self.assertAlmostEqual(Q[2],-0.2608, places)


    def test_convergence(self):
        """ Test convergence satisfaction check.
        """
        b, _, g, _, _, _, _ = self.solver._unpack_case(self.case)
        _, pq, _, pvpq = self.solver._index_buses(b)
        V0 = self.solver._initial_voltage(b, g)
        Sbus = self.case.Sbus
        Ybus, _, _ = self.case.Y
        P, Q = self.solver._evaluate_mismatch(Ybus, V0, Sbus, pq, pvpq)

        # True negative
        self.solver.converged = False
        self.solver.tolerance = 0.5000
        self.assertFalse(self.solver._check_convergence(P, Q, 0, ""))

        # True positive
        self.solver.converged = False
        self.solver.tolerance = 0.6000
        self.assertTrue(self.solver._check_convergence(P, Q, 0, ""))


    def test_solution(self):
        """ Test resulting voltage vector.
        """
        result = self.solver.solve()
        V = result["V"]

        self.assertTrue(result["success"])
        self.assertEqual(result["iterations"], 9)

        places = 4
        self.assertAlmostEqual(abs(V[1]), abs(1.0478-0.0672j), places)
        self.assertAlmostEqual(abs(V[2]), abs(1.0670-0.0797j), places)
        self.assertAlmostEqual(abs(V[5]), abs(0.9990-0.1041j), places)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")
    unittest.main()

# EOF -------------------------------------------------------------------------
