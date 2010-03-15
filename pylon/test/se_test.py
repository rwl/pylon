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

""" Test case for the state estimator.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from scipy import array

from pylon.readwrite import PickleReader
from pylon.estimator import StateEstimator, Measurement, PF, PT, PG, VM

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case3bus_P6_6.pkl")

#------------------------------------------------------------------------------
#  "StateEstimatorTest" class:
#------------------------------------------------------------------------------

class StateEstimatorTest(unittest.TestCase):
    """ Tests the state estimator using data from Problem 6.7 in 'Computational
        Methods for Electric Power Systems' by Mariesa Crow.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = self.case = PickleReader().read(DATA_FILE)

        self.measurements = [
            Measurement(case.branches[0], PF, 0.12),
            Measurement(case.branches[1], PF, 0.10),
            Measurement(case.branches[2], PT, -0.04),
            Measurement(case.buses[0], PG, 0.58),
            Measurement(case.buses[1], PG, 0.30),
            Measurement(case.buses[2], PG, 0.14),
            Measurement(case.buses[1], VM, 1.04),
            Measurement(case.buses[2], VM, 0.98),
        ]

        self.sigma = array([0.02, 0.02, 0,0, 0.015, 0, 0.01, 0])


    def test_case(self):
        """ Test the Pylon case.
        """
        self.assertEqual(len(self.case.buses), 3)
        self.assertEqual(len(self.case.branches), 3)
        self.assertEqual(len(self.case.generators), 3)


    def test_estimation(self):
        """ Test state estimation.
        """
        se = StateEstimator(self.case, self.measurements, self.sigma)
        solution = se.run()
        V = solution["V"]

        places = 4
        self.assertAlmostEqual(abs(V[0]), abs(1.0), places)
        self.assertAlmostEqual(abs(V[1]), abs(1.0256-0.0175j), places)
        self.assertAlmostEqual(abs(V[2]), abs(0.9790+0.0007j), places)


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
