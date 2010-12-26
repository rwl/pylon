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

""" Defines a test case for AC power flow.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from os.path import join, dirname

from scipy.io.mmio import mmread

from pylon import Case, NewtonPF, FastDecoupledPF, XB, BX
from pylon.ac_pf import _ACPF
from pylon.util import mfeq1

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_DIR = join(dirname(__file__), "data")

#------------------------------------------------------------------------------
#  "ACPFTest" class:
#------------------------------------------------------------------------------

class ACPFTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(ACPFTest, self).__init__(methodName)

        #: Name of the folder in which the MatrixMarket data exists.
        self.case_name = "case6ww"

        #: Case under test.
        self.case = None


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(join(DATA_DIR, self.case_name,
                                   self.case_name + ".pkl"))


    def testV0(self):
        """ Test the initial voltage vector.
        """
        solver = _ACPF(self.case)
        b, _, g, _, _, _, _ = solver._unpack_case(self.case)
        self.case.index_buses(b)

        V0 = solver._initial_voltage(b, g)

        mpV0 = mmread(join(DATA_DIR, self.case_name, "V0.mtx")).flatten()

        self.assertTrue(mfeq1(V0, mpV0), self.case_name)


    def testNewtonV(self):
        """ Test the voltage vector solution from Newton's method.
        """
        solution = NewtonPF(self.case).solve()

        mpV = mmread(join(DATA_DIR, self.case_name, "V_Newton.mtx")).flatten()

        self.assertTrue(mfeq1(solution["V"], mpV), self.case_name)


    def testFastDecoupledPFVXB(self):
        """ Test the voltage vector solution from the fast-decoupled method
            (XB version).
        """
        solution = FastDecoupledPF(self.case, method=XB).solve()

        mpV = mmread(join(DATA_DIR, self.case_name, "V_XB.mtx")).flatten()

        self.assertTrue(mfeq1(solution["V"], mpV), self.case_name)


    def testFastDecoupledPFVBX(self):
        """ Test the voltage vector solution from the fast-decoupled method
            (BX version).
        """
        solution = FastDecoupledPF(self.case, method=BX).solve()

        mpV = mmread(join(DATA_DIR, self.case_name, "V_BX.mtx")).flatten()

        self.assertTrue(mfeq1(solution["V"], mpV), self.case_name)

#------------------------------------------------------------------------------
#  "ACPFCase24RTSTest" class:
#------------------------------------------------------------------------------

class ACPFCase24RTSTest(ACPFTest):

    def __init__(self, methodName="runTest"):
        super(ACPFCase24RTSTest, self).__init__(methodName)

        self.case_name = "case24_ieee_rts"

#------------------------------------------------------------------------------
#  "ACPFCaseIEEE30Test" class:
#------------------------------------------------------------------------------

class ACPFCaseIEEE30Test(ACPFTest):

    def __init__(self, methodName="runTest"):
        super(ACPFCaseIEEE30Test, self).__init__(methodName)

        self.case_name = "case_ieee30"


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")
    unittest.main()

# EOF -------------------------------------------------------------------------
