#------------------------------------------------------------------------------
# Copyright (C) 2007-2010 Richard Lincoln
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

""" Test case for the optimal power flow solver.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from numpy import Inf

from pylon import OPF, Case

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

POLY_FILE = join(dirname(__file__), "data", "case6ww.pkl")

#------------------------------------------------------------------------------
#  "OPFModelTest" class:
#------------------------------------------------------------------------------

class OPFModelTest(unittest.TestCase):
    """ Test case for the OPF model.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(POLY_FILE)
        self.opf = OPF(self.case)


    def test_dc_linear_constraints(self):
        """ Test linear OPF constraints.
        """
        self.opf.dc = True
        om = self.opf._construct_opf_model(self.case)

        A, l, u = om.linear_constraints()

        self.assertEqual(A.shape, (28, 9))
        self.assertEqual(l.shape, (28, ))
        self.assertEqual(u.shape, (28, ))

        pl = 4
        self.assertAlmostEqual(A[0, 0], 13.3333, pl)
        self.assertAlmostEqual(A[4, 2], -3.8462, pl)
        self.assertAlmostEqual(A[2, 8], -1.0000, pl)
        self.assertAlmostEqual(A[9, 1],  4.0000, pl)
        self.assertAlmostEqual(A[27, 5], 3.3333, pl)

        self.assertAlmostEqual(l[0], 0.0000, pl)
        self.assertAlmostEqual(l[3], -0.7000, pl)
        self.assertEqual(l[6], -Inf)
        self.assertEqual(l[27], -Inf)

        self.assertAlmostEqual(u[0],  0.0000, pl)
        self.assertAlmostEqual(u[3], -0.7000, pl)
        self.assertAlmostEqual(u[6],  0.4000, pl)
        self.assertAlmostEqual(u[7],  0.6000, pl)
        self.assertAlmostEqual(u[23], 0.9000, pl)


    def test_ac_linear_constraints(self):
        """ Test linear OPF constraints.
        """
        self.opf.dc = False
        om = self.opf._construct_opf_model(self.case)

        A, l, u = om.linear_constraints()

        self.assertEqual(A, None)
        self.assertEqual(l.shape, (0, ))
        self.assertEqual(u.shape, (0, ))


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    logger = logging.getLogger("pylon")

    unittest.main()

# EOF -------------------------------------------------------------------------
