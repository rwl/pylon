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

""" Test case for the DC Power Flow routine.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path import join, dirname
from unittest import TestCase, main

from pylon.readwrite import PickleReader
from pylon import DCPF

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#-------------------------------------------------------------------------------
#  "DCPFTest" class:
#-------------------------------------------------------------------------------

class DCPFTest(TestCase):
    """ Uses a MATPOWER data file and validates the results against those
        obtained from running the MATPOWER rundcpf.m script with the same
        data file. See filter_test_case.py for validation of MATPOWER data
        file parsing.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = PickleReader().read(DATA_FILE)
        self.routine = DCPF()
        self.routine.solve(case)


    def test_v_angle_guess_vector(self):
        """ Test the voltage phase guess trait of a bus """

        guesses = self.routine.v_angle_guess

        self.assertEqual(guesses.size, (6, 1))
        self.assertEqual(guesses[1], 0.0)
        self.assertEqual(guesses[5], 0.0)


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

        self.assertAlmostEqual(vp_0, v_angle[0], places)
        self.assertAlmostEqual(vp_2, v_angle[2], places)
        self.assertAlmostEqual(vp_5, v_angle[5], places)


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

        c        = self.routine.case
        buses    = c.connected_buses
        branches = c.online_branches

        # Buses
        v_0 = 0.0000
        v_3 = -4.7632
        v_5 = -5.7418

        for each_bus in buses:
            self.assertEqual(each_bus.v_magnitude, 1.0)
        self.assertAlmostEqual(v_0, buses[0].v_angle, places)
        self.assertAlmostEqual(v_3, buses[3].v_angle, places)
        self.assertAlmostEqual(v_5, buses[5].v_angle, places)

        # Branches
        p_2 = 33.1045
        p_6 = 24.7781
        p_9 = 4.0448

        for branch in branches:
            self.assertEqual(branch.q_source, 0.0)
            self.assertEqual(branch.q_target, 0.0)
            # Source and target real powers are the negative of one and other
            self.assertAlmostEqual(branch.p_source, -branch.p_target, places)
        self.assertAlmostEqual(p_2, branches[2].p_source, places)
        self.assertAlmostEqual(p_6, branches[6].p_source, places)
        self.assertAlmostEqual(p_9, branches[9].p_source, places)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    main()

# EOF -------------------------------------------------------------------------
