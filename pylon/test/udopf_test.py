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

""" Defines a test case for the combined unit decommitment / OPF routine.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
import unittest

from os.path import dirname, join

from pylon.readwrite import PickleReader
from pylon.ud_opf import UDOPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")
PWL_FILE  = join(dirname(__file__), "..", "pyreto", "test", "data",
    "auction_case.pkl")

#------------------------------------------------------------------------------
#  "UOPFTestCase" class:
#------------------------------------------------------------------------------

class UOPFTestCase(unittest.TestCase):
    """ Defines a test case for the UOPF routine.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        case = self.case = PickleReader().read(DATA_FILE)
        self.solver = UDOPF(case, dc=True)


    def test_dc(self):
        """ Test solver using DC formulation.
        """
        solution = self.solver.solve()
        generators = self.case.generators

        self.assertTrue(solution["status"] == "optimal")
        # Generator 1 gets shutdown.
        self.assertFalse(generators[0].online)
        self.assertAlmostEqual(generators[1].p, 110.80, places=2)
        self.assertAlmostEqual(generators[2].p,  99.20, places=2)

        self.assertAlmostEqual(self.solver.solver.f, 2841.59, places=2)


    def test_pwl(self):
        """ Test UDOPF solver with pwl auction case.
        """
        case = PickleReader().read(PWL_FILE)
        solver = UDOPF(case, dc=True)
        solution = solver.solve()
        generators = self.case.generators

        self.assertTrue(solution["status"] == "optimal")
        self.assertTrue(False not in [g.online for g in generators])


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    unittest.main()

# EOF -------------------------------------------------------------------------
