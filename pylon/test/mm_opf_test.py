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
from pylon.opf import Solver, DCOPFSolver
from pylon.util import mfeq2

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_DIR = join(dirname(__file__), "data")

#------------------------------------------------------------------------------
#  "DCOPFTest" class:
#------------------------------------------------------------------------------

class DCOPFTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(DCOPFTest, self).__init__(methodName)

        self.case_name = "case6ww"
        self.case = None
        self.opf = None


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

        if ang.A.shape[0] != 0:
            Aang = mmread(join(DATA_DIR, self.case_name, "opf", "Aang.mtx"))
        else:
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

#------------------------------------------------------------------------------
#  "SolverTest" class:
#------------------------------------------------------------------------------

class SolverTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(SolverTest, self).__init__(methodName)

        self.case_name = "case6ww"
        self.case = None
        self.opf = None
        self.om = None
        self.solver = None


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(join(DATA_DIR, self.case_name, "case.pkl"))
        self.opf = OPF(self.case, dc=True)
        self.om = self.opf._construct_opf_model(self.case)
        self.solver = Solver(self.om)


    def test_constraints(self):
        """ Test equality and inequality constraints.
        """
        AA, ll, uu = self.solver._linear_constraints(self.om)

        mpA = mmread(join(DATA_DIR, self.case_name, "opf", "A_DC.mtx"))
        mpl = mmread(join(DATA_DIR, self.case_name, "opf", "l_DC.mtx"))
        mpu = mmread(join(DATA_DIR, self.case_name, "opf", "u_DC.mtx"))

        self.assertTrue(mfeq2(AA, mpA.tocsr()))
        self.assertTrue(alltrue(ll == mpl.flatten()))
        self.assertTrue(alltrue(uu == mpu.flatten()))


    def test_var_bounds(self):
        """ Test bounds on optimisation variables.
        """
        _, xmin, xmax = self.solver._var_bounds()

#        mpx0 = mmread(join(DATA_DIR, self.case_name, "opf", "x0_DC.mtx"))
        mpxmin = mmread(join(DATA_DIR, self.case_name, "opf", "xmin_DC.mtx"))
        mpxmax = mmread(join(DATA_DIR, self.case_name, "opf", "xmax_DC.mtx"))

#        self.assertTrue(alltrue(x0 == mpx0.flatten()))
        self.assertTrue(alltrue(xmin == mpxmin.flatten()))
        self.assertTrue(alltrue(xmax == mpxmax.flatten()))


    def test_initial_point(self):
        """ Test selection of an initial interior point.
        """
        b, l, g, _ = self.solver._unpack_model(self.om)
        _, LB, UB = self.solver._var_bounds()
        _, _, _, _, _, ny, _ = self.solver._dimension_data(b, l, g)
        x0 = self.solver._initial_interior_point(b, g, LB, UB, ny)

        mpx0 = mmread(join(DATA_DIR, self.case_name, "opf", "x0_DC.mtx"))

        self.assertTrue(alltrue(x0 == mpx0.flatten()))

#------------------------------------------------------------------------------
#  "DCOPFSolverTest" class:
#------------------------------------------------------------------------------

class DCOPFSolverTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(DCOPFSolverTest, self).__init__(methodName)

        self.case_name = "case6ww"
        self.case = None
        self.opf = None
        self.om = None
        self.solver = None


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(join(DATA_DIR, self.case_name, "case.pkl"))
        self.opf = OPF(self.case, dc=True)
        self.om = self.opf._construct_opf_model(self.case)
        self.solver = DCOPFSolver(self.om)


    def test_pwl_costs(self):
        """ Test piecewise linear costs.
        """
        b, l, g, _ = self.solver._unpack_model(self.om)
        _, ipwl, _, _, _, ny, nxyz = self.solver._dimension_data(b, l, g)
        Npwl, Hpwl, Cpwl, fparm_pwl, _ = \
            self.solver._pwl_costs(ny, nxyz, ipwl)

        if Npwl is not None:
            mpNpwl = mmread(join(DATA_DIR, self.case_name, "opf", "Npwl.mtx"))
        mpHpwl = mmread(join(DATA_DIR, self.case_name, "opf", "Hpwl.mtx"))
        mpCpwl = mmread(join(DATA_DIR, self.case_name, "opf", "Cpwl.mtx"))
        mpfparm = mmread(join(DATA_DIR, self.case_name, "opf","fparm_pwl.mtx"))

        if Npwl is not None:
            self.assertTrue(alltrue(Npwl == mpNpwl.flatten()))
        if Hpwl is not None:
            self.assertTrue(alltrue(Hpwl == mpHpwl.flatten()))
        self.assertTrue(alltrue(Cpwl == mpCpwl.flatten()))
#        self.assertTrue(alltrue(fparm_pwl == mpfparm.flatten()))


    def test_poly_costs(self):
        """ Test quadratic costs.
        """
        base_mva = self.om.case.base_mva
        b, l, g, _ = self.solver._unpack_model(self.om)
        ipol, _, _, _, _, _, nxyz = self.solver._dimension_data(b, l, g)
        Npol, Hpol, Cpol, fparm_pol, _, _ = \
            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)

        mpNpol = mmread(join(DATA_DIR, self.case_name, "opf", "Npol.mtx"))
        mpHpol = mmread(join(DATA_DIR, self.case_name, "opf", "Hpol.mtx"))
        mpCpol = mmread(join(DATA_DIR, self.case_name, "opf", "Cpol.mtx"))
        mpfparm = mmread(join(DATA_DIR, self.case_name, "opf","fparm_pol.mtx"))

        self.assertTrue(mfeq2(Npol, mpNpol.tocsr()))
        self.assertTrue(mfeq2(Hpol, mpHpol.tocsr()))
        self.assertTrue(alltrue(Cpol == mpCpol.flatten()))
        self.assertTrue(alltrue(fparm_pol == mpfparm))


    def test_combine_costs(self):
        """ Test combination of pwl and poly costs.
        """
        base_mva = self.om.case.base_mva
        b, l, g, _ = self.solver._unpack_model(self.om)
        ipol, ipwl, _, _, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz,
                                                                      ipwl)
        Npol, Hpol, Cpol, fparm_pol, _, npol = \
            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
        NN, HHw, CCw, ffparm = \
            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
                                       Npol, Hpol, Cpol, fparm_pol, npol, nw)

        mpNN = mmread(join(DATA_DIR, self.case_name, "opf", "NN.mtx"))
        mpHHw = mmread(join(DATA_DIR, self.case_name, "opf", "HHw.mtx"))
        mpCCw = mmread(join(DATA_DIR, self.case_name, "opf", "CCw.mtx"))
        mpffparm = mmread(join(DATA_DIR, self.case_name, "opf", "ffparm.mtx"))

        self.assertTrue(mfeq2(NN, mpNN.tocsr()))
        self.assertTrue(mfeq2(HHw, mpHHw.tocsr()))
        self.assertTrue(alltrue(CCw == mpCCw.flatten()))
        self.assertTrue(alltrue(ffparm == mpffparm))


    def test_coefficient_transformation(self):
        """ Test transformation of quadratic coefficients for w into
            coefficients for X.
        """
        base_mva = self.om.case.base_mva
        b, l, g, _ = self.solver._unpack_model(self.om)
        ipol, ipwl, _, _, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = \
            self.solver._pwl_costs(ny, nxyz, ipwl)
        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
        NN, HHw, CCw, ffparm = \
            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
                                       Npol, Hpol, Cpol, fparm_pol, npol, nw)
        HH, CC, _ = \
            self.solver._transform_coefficients(NN, HHw, CCw, ffparm, polycf,
                                                any_pwl, npol, nw)

        mpHH = mmread(join(DATA_DIR, self.case_name, "opf", "HH.mtx"))
        mpCC = mmread(join(DATA_DIR, self.case_name, "opf", "CC.mtx"))

        self.assertTrue(mfeq2(HH, mpHH.tocsr()))
        self.assertTrue(alltrue(CC == mpCC.flatten()))


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")
    unittest.main()

# EOF -------------------------------------------------------------------------
