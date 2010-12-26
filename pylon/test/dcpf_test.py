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

""" Defines a test case for DC power flow.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from os.path import join, dirname

from scipy import array, alltrue
from scipy.io.mmio import mmread

from pylon import Case, DCPF

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_DIR = join(dirname(__file__), "data")

#------------------------------------------------------------------------------
#  "DCPFTest" class:
#------------------------------------------------------------------------------

class DCPFTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(DCPFTest, self).__init__(methodName)

        #: Name of the folder in which the MatrixMarket data exists.
        self.case_name = "case6ww"

        self.case = None


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(join(DATA_DIR, self.case_name,
                                   self.case_name + ".pkl"))


    def testVa(self):
        """ Test voltage angle solution vector from DC power flow.
        """
        solver = DCPF(self.case)
        solver.solve()

        mpVa = mmread(join(DATA_DIR, self.case_name, "Va.mtx")).flatten()

        self.assertTrue(abs(max(solver.v_angle - mpVa)) < 1e-14,self.case_name)

#------------------------------------------------------------------------------
#  "DCPFCase24RTSTest" class:
#------------------------------------------------------------------------------

class DCPFCase24RTSTest(DCPFTest):

    def __init__(self, methodName='runTest'):
        super(DCPFCase24RTSTest, self).__init__(methodName)

        self.case_name = "case24_ieee_rts"

#------------------------------------------------------------------------------
#  "DCPFCaseIEEE30Test" class:
#------------------------------------------------------------------------------

class DCPFCaseIEEE30Test(DCPFTest):

    def __init__(self, methodName='runTest'):
        super(DCPFCaseIEEE30Test, self).__init__(methodName)

        self.case_name = "case_ieee30"


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")
    unittest.main()

# EOF -------------------------------------------------------------------------
