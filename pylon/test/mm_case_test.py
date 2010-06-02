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

""" Defines the case test case.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from os.path import join, dirname

from scipy import alltrue
from scipy.io.mmio import mmread

from pylon import XB, BX
from pylon.readwrite import PickleReader
from pylon.util import mfeq2

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_DIR = join(dirname(__file__), "data")

#------------------------------------------------------------------------------
#  "CaseTest" class:
#------------------------------------------------------------------------------

class CaseTest(unittest.TestCase):
    """ Defines a test case for the Pylon case.
    """

    def __init__(self, methodName='runTest'):
        super(CaseTest, self).__init__(methodName)

        self.case_name = "case6ww"

        self.case = None


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        path = join(DATA_DIR, self.case_name, "case.pkl")
        self.case = PickleReader().read(path)


    def testSbus(self):
        """ Test the vector of bus power injections.
        """
        Sbus = self.case.Sbus
        mpSbus = mmread(join(DATA_DIR, self.case_name, "Sbus.mtx")).flatten()

        self.assertTrue(alltrue(Sbus == mpSbus))


    def testYbus(self):
        """ Test bus and branch admittance matrices.
        """
        Ybus, Yf, Yt = self.case.Y

        mpYbus = mmread(join(DATA_DIR, self.case_name, "Ybus.mtx")).tocsr()
        mpYf = mmread(join(DATA_DIR, self.case_name, "Yf.mtx")).tocsr()
        mpYt = mmread(join(DATA_DIR, self.case_name, "Yt.mtx")).tocsr()

        self.assertTrue(mfeq2(Ybus, mpYbus))
        self.assertTrue(mfeq2(Yf, mpYf))
        self.assertTrue(mfeq2(Yt, mpYt))


    def testB(self):
        """ Test FDPF B matrices.
        """
        xbBp, xbBpp = self.case.makeB(method=XB)

        mpxbBp = mmread(join(DATA_DIR, self.case_name, "Bp_XB.mtx")).tocsr()
        mpxbBpp = mmread(join(DATA_DIR, self.case_name, "Bpp_XB.mtx")).tocsr()

        self.assertTrue(mfeq2(xbBp, mpxbBp))
        self.assertTrue(mfeq2(xbBpp, mpxbBpp))

        bxBp, bxBpp = self.case.makeB(method=BX)

        mpbxBp = mmread(join(DATA_DIR, self.case_name, "Bp_BX.mtx")).tocsr()
        mpbxBpp = mmread(join(DATA_DIR, self.case_name, "Bpp_BX.mtx")).tocsr()

        self.assertTrue(mfeq2(bxBp, mpbxBp))
        self.assertTrue(mfeq2(bxBpp, mpbxBpp))


    def testBdc(self):
        """ Test DCPF B matrices and phase shift injection vectors.
        """
        B, Bf, Pbusinj, Pfinj = self.case.Bdc

        mpB = mmread(join(DATA_DIR, self.case_name, "B.mtx")).tocsr()
        self.assertTrue(mfeq2(B, mpB))

        mpBf = mmread(join(DATA_DIR, self.case_name, "Bf.mtx")).tocsr()
        self.assertTrue(mfeq2(Bf, mpBf))

        mpPbusinj = mmread(join(DATA_DIR, self.case_name,
                                "Pbusinj.mtx")).flatten()
        self.assertTrue(abs(max(Pbusinj - mpPbusinj)) < 1e-14)

        mpPfinj = mmread(join(DATA_DIR, self.case_name, "Pfinj.mtx")).flatten()
        self.assertTrue(abs(max(Pfinj - mpPfinj)) < 1e-14)


    def test_dSbus_dV(self):
        """ Test partial derivative of power injection w.r.t. voltage.
        """
        mpYbus = mmread(join(DATA_DIR, self.case_name, "Ybus.mtx")).tocsr()
        mpV0 = mmread(join(DATA_DIR, self.case_name, "V0.mtx")).flatten()

        dSbus_dVm, dSbus_dVa = self.case.dSbus_dV(mpYbus, mpV0)

        mp_dSbus_dVm = mmread(join(DATA_DIR, self.case_name, "dSbus_dVm0.mtx"))
        mp_dSbus_dVa = mmread(join(DATA_DIR, self.case_name, "dSbus_dVa0.mtx"))

        self.assertTrue(mfeq2(dSbus_dVm, mp_dSbus_dVm.tocsr(), 1e-12))
        self.assertTrue(mfeq2(dSbus_dVa, mp_dSbus_dVa.tocsr(), 1e-12))


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
