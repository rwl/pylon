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

""" Test case for the state estimator.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from cvxopt import matrix

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

        self.sigma = matrix([0.02, 0.02, 0,0, 0.015, 0, 0.01, 0])


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
        se.run()

# EOF -------------------------------------------------------------------------
