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

""" Test case for the DC Power Flow routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest
from os.path import join, dirname

from pylon.readwrite import PickleReader
from pylon import DCPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "DCPFTest" class:
#------------------------------------------------------------------------------

class DCPFTest(unittest.TestCase):
    """ Uses a MATPOWER data file and validates the results against those
        obtained from running the MATPOWER rundcpf.m script with the same
        data file. See filter_test_case.py for validation of MATPOWER data
        file parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)
        self.routine = DCPF(self.case)#"CHOLMOD")
        self.routine.solve()


    def test_v_angle_guess_vector(self):
        """ Test the voltage phase guess trait of a bus.
        """
        Va0 = self.routine._get_v_angle_guess(self.case)

        self.assertEqual(Va0.shape, (6,))
        self.assertEqual(Va0[1], 0.0)
        self.assertEqual(Va0[5], 0.0)


    def test_v_angle_vector(self):
        """ Test the resulting voltage phase angles

        Va =

                 0
           -0.0507
           -0.0553
           -0.0831
           -0.0993
           -0.1002

        """
        places = 4

        vp_0 = 0.0000
        vp_2 = -0.0553
        vp_5 = -0.1002

        v_angle = self.routine.v_angle

        self.assertAlmostEqual(v_angle[0], vp_0, places)
        self.assertAlmostEqual(v_angle[2], vp_2, places)
        self.assertAlmostEqual(v_angle[5], vp_5, places)


    def test_model_results(self):
        """ Test update of the model with results.

        v_magnitude =

                 0
           -2.9024
           -3.1679
           -4.7632
           -5.6902
           -5.7418

        P =

           25.3284
           41.5672
           33.1045
            1.8537
           32.4776
           16.2189
           24.7781
           16.9317
           44.9220
            4.0448
            0.2999

        """
        places = 4

        case = self.routine.case
        buses = case.connected_buses
        branches = case.online_branches

        # Buses
        v_0 =  0.0000
        v_3 = -4.7632
        v_5 = -5.7418

        for each_bus in buses:
            self.assertEqual(each_bus.v_magnitude, 1.0)
        self.assertAlmostEqual(buses[0].v_angle, v_0, places)
        self.assertAlmostEqual(buses[3].v_angle, v_3, places)
        self.assertAlmostEqual(buses[5].v_angle, v_5, places)

        # Branches
        p_2 = 33.1045
        p_6 = 24.7781
        p_9 = 4.0448

        for branch in branches:
            self.assertEqual(branch.q_from, 0.0)
            self.assertEqual(branch.q_to, 0.0)
            # From and to real powers are the negative of one and other
            self.assertAlmostEqual(branch.p_from, -branch.p_to, places)
        self.assertAlmostEqual(branches[2].p_from, p_2, places)
        self.assertAlmostEqual(branches[6].p_from, p_6, places)
        self.assertAlmostEqual(branches[9].p_from, p_9, places)

        # Test swing bus generator set-point.
        self.assertAlmostEqual(case.generators[0].p, 100.0, places)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    unittest.main()

# EOF ------------------------------------------------------------------------
