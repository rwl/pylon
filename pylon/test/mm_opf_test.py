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

from scipy import array, alltrue
from scipy.io.mmio import mmread

from pylon import Case, OPF
from pylon.util import mfeq2

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_DIR = join(dirname(__file__), "data")
OPF_DIR = join(DATA_DIR, "opf")

#------------------------------------------------------------------------------
#  "DCOPFTest" class:
#------------------------------------------------------------------------------

class DCOPFTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(DCOPFTest, self).__init__(methodName)

        self.case_name = "case6ww"
        self.case = None
        self.solver = None


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(join(DATA_DIR, self.case_name, "case.pkl"))
        self.opf = OPF(self.case, dc=True)


    def testVa(self):
        """ Test voltage angle variable.
        """
        bs, _, _ = self.opf._remove_isolated(self.case)
        _, refs = self.opf._ref_check(self.case)
        Va = self.opf._get_voltage_angle_var(refs, bs)

        mpVa0 = mmread(join(DATA_DIR, self.case_name, "opf", "Va0.mtx"))
        mpVal = mmread(join(DATA_DIR, self.case_name, "opf", "Val.mtx"))
        mpVau = mmread(join(DATA_DIR, self.case_name, "opf", "Vau.mtx"))

        self.assertTrue(alltrue(Va.v0 == mpVa0.flatten()))
        self.assertTrue(alltrue(Va.vl == mpVal.flatten()))
        self.assertTrue(alltrue(Va.vu == mpVau.flatten()))


    def testVm(self):
        """ Test voltage magnitude variable.
        """
        bs, _, gn = self.opf._remove_isolated(self.case)
        Vm = self.opf._get_voltage_magnitude_var(bs, gn)

        mpVm0 = mmread(join(DATA_DIR, self.case_name, "opf", "Vm0.mtx"))

        self.assertTrue(alltrue(Vm.v0 == mpVm0.flatten()))


    def testPg(self):
        """ Test active power variable.
        """
        _, _, gn = self.opf._remove_isolated(self.case)
        Pg = self.opf._get_pgen_var(gn, self.case.base_mva)

        mpPg0 = mmread(join(DATA_DIR, self.case_name, "opf", "Pg0.mtx"))
        mpPmin = mmread(join(DATA_DIR, self.case_name, "opf", "Pmin.mtx"))
        mpPmax = mmread(join(DATA_DIR, self.case_name, "opf", "Pmax.mtx"))

        self.assertTrue(alltrue(Pg.v0 == mpPg0.flatten()))
        self.assertTrue(alltrue(Pg.vl == mpPmin.flatten()))
        self.assertTrue(alltrue(Pg.vu == mpPmax.flatten()))


    def testQg(self):
        """ Test reactive power variable.
        """
        _, _, gn = self.opf._remove_isolated(self.case)
        Qg = self.opf._get_qgen_var(gn, self.case.base_mva)

        mpQg0 = mmread(join(DATA_DIR, self.case_name, "opf", "Qg0.mtx"))
        mpQmin = mmread(join(DATA_DIR, self.case_name, "opf", "Qmin.mtx"))
        mpQmax = mmread(join(DATA_DIR, self.case_name, "opf", "Qmax.mtx"))

        self.assertTrue(alltrue(Qg.v0 == mpQg0.flatten()))
        self.assertTrue(alltrue(Qg.vl == mpQmin.flatten()))
        self.assertTrue(alltrue(Qg.vu == mpQmax.flatten()))


    def testPmis(self):
        """ Test active power mismatch constraints.
        """
        case = self.case
        case.sort_generators() # ext2int
        B, _, Pbusinj, _ = case.Bdc
        bs, _, gn = self.opf._remove_isolated(case)
        Pmis = self.opf._power_mismatch_dc(bs, gn, B, Pbusinj, case.base_mva)

        mpAmis = mmread(join(DATA_DIR, self.case_name, "opf", "Amis.mtx"))
        mpbmis = mmread(join(DATA_DIR, self.case_name, "opf", "bmis.mtx"))

        self.assertTrue(mfeq2(Pmis.A, mpAmis.tocsr()))
        self.assertTrue(alltrue(Pmis.l == mpbmis.flatten()))
        self.assertTrue(alltrue(Pmis.u == mpbmis.flatten()))


    def testPfPt(self):
        """ Test branch flow limit constraints.
        """
        _, ln, _ = self.opf._remove_isolated(self.case)
        _, Bf, _, Pfinj = self.case.Bdc
        Pf, Pt = self.opf._branch_flow_dc(ln, Bf, Pfinj, self.case.base_mva)

        lpf = mmread(join(DATA_DIR, self.case_name, "opf", "lpf.mtx"))
        upf = mmread(join(DATA_DIR, self.case_name, "opf", "upf.mtx"))
        upt = mmread(join(DATA_DIR, self.case_name, "opf", "upt.mtx"))

        self.assertTrue(alltrue(Pf.l == lpf.flatten()))
        self.assertTrue(alltrue(Pf.u == upf.flatten()))
        self.assertTrue(alltrue(Pt.l == lpf.flatten()))
        self.assertTrue(alltrue(Pt.u == upt.flatten()))


    def testVang(self):
        """ Test voltage angle difference limit constraint.
        """
        self.opf.ignore_ang_lim = False
        bs, ln, _ = self.opf._remove_isolated(self.case)
        ang = self.opf._voltage_angle_diff_limit(bs, ln)

        try:
            Aang = mmread(join(DATA_DIR, self.case_name, "opf", "Aang.mtx"))
        except ValueError:
            Aang = None
        lang = mmread(join(DATA_DIR, self.case_name, "opf", "lang.mtx"))
        uang = mmread(join(DATA_DIR, self.case_name, "opf", "uang.mtx"))

        if Aang is not None:
            self.assertTrue(mfeq2(ang.A, Aang.tocsr()))
        self.assertTrue(alltrue(ang.l == lang.flatten()))
        self.assertTrue(alltrue(ang.u == uang.flatten()))


    def testAy(self):
        """ Test basin constraints for piece-wise linear gen cost variables.
        """
        _, _, gn = self.opf._remove_isolated(self.case)
        _, ycon = self.opf._pwl_gen_costs(gn, self.case.base_mva)

        if ycon is not None:
            Ay = mmread(join(DATA_DIR, self.case_name, "opf", "Ay.mtx"))
            by = mmread(join(DATA_DIR, self.case_name, "opf", "by.mtx"))

            self.assertTrue(mfeq2(ycon.A, Ay.tocsr()))
            self.assertTrue(alltrue(ycon.u == by.flatten()))


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")
    unittest.main()

# EOF -------------------------------------------------------------------------
