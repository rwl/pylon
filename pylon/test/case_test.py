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

""" Defines the case test case.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os
from os.path import join, dirname, exists, getsize
import unittest
import tempfile
from numpy import complex128

from scipy import alltrue
from scipy.io.mmio import mmread

from pylon import Case, Bus, Branch, Generator, NewtonPF, XB, BX
from pylon.io import PickleReader
from pylon.util import CaseReport, mfeq2

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

MP_DATA_FILE = join(dirname(__file__), "data", "case6ww.m")
DATA_FILE = join(dirname(__file__), "data", "case6ww","case6ww.pkl")
PWL_FILE = join(dirname(__file__), "data", "case30pwl", "case30pwl.pkl")
DATA_DIR = join(dirname(__file__), "data")

#------------------------------------------------------------------------------
#  "CaseMatrixTest" class:
#------------------------------------------------------------------------------

class CaseMatrixTest(unittest.TestCase):
    """ Defines a test case for the Pylon case.
    """

    def __init__(self, methodName='runTest'):
        super(CaseMatrixTest, self).__init__(methodName)

        #: Name of the folder in which the MatrixMarket data exists.
        self.case_name = "case6ww"

        self.case = None


    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        path = join(DATA_DIR, self.case_name, self.case_name + ".pkl")
        self.case = PickleReader().read(path)


    def testSbus(self):
        """ Test the vector of bus power injections.
        """
        Sbus = self.case.Sbus
        mpSbus = mmread(join(DATA_DIR, self.case_name, "Sbus.mtx")).flatten()

#        self.assertTrue(alltrue(Sbus == mpSbus))
        # FIXME: Improve accuracy.
        self.assertTrue(abs(max(Sbus - mpSbus)) < 1e-06, msg=self.case_name)


    def testYbus(self):
        """ Test bus and branch admittance matrices.
        """
        self.case.index_buses()
        Ybus, Yf, Yt = self.case.Y

        mpYbus = mmread(join(DATA_DIR, self.case_name, "Ybus.mtx")).tocsr()
        mpYf = mmread(join(DATA_DIR, self.case_name, "Yf.mtx")).tocsr()
        mpYt = mmread(join(DATA_DIR, self.case_name, "Yt.mtx")).tocsr()

        self.assertTrue(mfeq2(Ybus, mpYbus, diff=1e-12), self.case_name)
        self.assertTrue(mfeq2(Yf, mpYf, diff=1e-12), self.case_name)
        self.assertTrue(mfeq2(Yt, mpYt, diff=1e-12), self.case_name)


    def testB(self):
        """ Test FDPF B matrices.
        """
        self.case.index_buses()
        xbBp, xbBpp = self.case.makeB(method=XB)

        mpxbBp = mmread(join(DATA_DIR, self.case_name, "Bp_XB.mtx")).tocsr()
        mpxbBpp = mmread(join(DATA_DIR, self.case_name, "Bpp_XB.mtx")).tocsr()

        self.assertTrue(mfeq2(xbBp, mpxbBp, diff=1e-12), self.case_name)
        self.assertTrue(mfeq2(xbBpp, mpxbBpp, diff=1e-12), self.case_name)

        bxBp, bxBpp = self.case.makeB(method=BX)

        mpbxBp = mmread(join(DATA_DIR, self.case_name, "Bp_BX.mtx")).tocsr()
        mpbxBpp = mmread(join(DATA_DIR, self.case_name, "Bpp_BX.mtx")).tocsr()

        self.assertTrue(mfeq2(bxBp, mpbxBp, diff=1e-12), self.case_name)
        self.assertTrue(mfeq2(bxBpp, mpbxBpp, diff=1e-12), self.case_name)


    def testBdc(self):
        """ Test DCPF B matrices and phase shift injection vectors.
        """
        self.case.index_buses()
        B, Bf, Pbusinj, Pfinj = self.case.Bdc

        mpB = mmread(join(DATA_DIR, self.case_name, "B.mtx")).tocsr()
        self.assertTrue(mfeq2(B, mpB, diff=1e-12), self.case_name)

        mpBf = mmread(join(DATA_DIR, self.case_name, "Bf.mtx")).tocsr()
        self.assertTrue(mfeq2(Bf, mpBf, diff=1e-12), self.case_name)

        mpPbusinj = mmread(join(DATA_DIR, self.case_name,
                                "Pbusinj.mtx")).flatten()
        self.assertTrue(abs(max(Pbusinj - mpPbusinj)) < 1e-14, self.case_name)

        mpPfinj = mmread(join(DATA_DIR, self.case_name, "Pfinj.mtx")).flatten()
        self.assertTrue(abs(max(Pfinj - mpPfinj)) < 1e-14, self.case_name)


    def test_dSbus_dV(self):
        """ Test partial derivative of power injection w.r.t. voltage.
        """
        mpYbus = mmread(join(DATA_DIR, self.case_name, "Ybus.mtx")).tocsr()
        mpV0 = mmread(join(DATA_DIR, self.case_name, "V0.mtx")).flatten()

        dSbus_dVm, dSbus_dVa = self.case.dSbus_dV(mpYbus, mpV0)

        mp_dSbus_dVm = mmread(join(DATA_DIR, self.case_name, "dSbus_dVm0.mtx"))
        mp_dSbus_dVa = mmread(join(DATA_DIR, self.case_name, "dSbus_dVa0.mtx"))

        self.assertTrue(mfeq2(dSbus_dVm, mp_dSbus_dVm.tocsr(), 1e-12),
                        self.case_name)
        self.assertTrue(mfeq2(dSbus_dVa, mp_dSbus_dVa.tocsr(), 1e-12),
                        self.case_name)

#------------------------------------------------------------------------------
#  "CaseMatrix24RTSTest" class:
#------------------------------------------------------------------------------

class CaseMatrix24RTSTest(CaseMatrixTest):

    def __init__(self, methodName='runTest'):
        super(CaseMatrix24RTSTest, self).__init__(methodName)

        self.case_name = "case24_ieee_rts"

#------------------------------------------------------------------------------
#  "CaseMatrixIEEE30Test" class:
#------------------------------------------------------------------------------

class CaseMatrixIEEE30Test(CaseMatrixTest):

    def __init__(self, methodName='runTest'):
        super(CaseMatrixIEEE30Test, self).__init__(methodName)

        self.case_name = "case_ieee30"

#------------------------------------------------------------------------------
#  "CaseTest" class:
#------------------------------------------------------------------------------

class CaseTest(unittest.TestCase):
    """ Defines a test case for the Pylon case.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)


    def test_reset(self):
        """ Test zeroing of result attributes.
        """
        case = self.case

        case.buses[5].p_lmbda = 1.1
        case.generators[2].mu_pmax = 1.1
        case.branches[10].p_from = 1.1

        case.reset()

        self.assertEqual(case.buses[5].p_lmbda, 0.0)
        self.assertEqual(case.generators[2].mu_pmax, 0.0)
        self.assertEqual(case.branches[10].p_from, 0.0)


    def test_sort_generators(self):
        """ Test ordering of generators according to bus index.
        """
        case = PickleReader().read(PWL_FILE)

        self.assertEqual(case.buses.index(case.generators[2].bus), 21)
        self.assertEqual(case.buses.index(case.generators[5].bus), 12)

        case.sort_generators()

        self.assertEqual(case.buses.index(case.generators[2].bus), 12)
        self.assertEqual(case.buses.index(case.generators[5].bus), 26)

    #--------------------------------------------------------------------------
    #  Serialisation tests.
    #--------------------------------------------------------------------------

    def test_load_matpower(self):
        """ Test loading a MATPOWER data file.
        """
        case = Case.load(MP_DATA_FILE, "matpower")

        self.assertEqual(len(case.generators), 3)
        self.assertTrue(isinstance(case, Case))


    def test_infer_matpower_format(self):
        """ Test inference of MATPOWER format from file extension.
        """
        case = Case.load(MP_DATA_FILE) # Format not specified.

        self.assertEqual(len(case.generators), 3)
        self.assertTrue(isinstance(case, Case))


    def test_save_matpower(self):
        """ Test saving a case in MATPOWER format.
        """
        tmp_fd, tmp_name = tempfile.mkstemp(".m")
        os.close(tmp_fd)
        os.remove(tmp_name)
#        os.unlink(tmp_name)

        self.assertFalse(exists(tmp_name))

        self.case.save(tmp_name)

        self.assertTrue(exists(tmp_name))
        self.assertTrue(getsize(tmp_name) > 0)


#------------------------------------------------------------------------------
#  "BusTest" class:
#------------------------------------------------------------------------------

class BusTest(unittest.TestCase):
    """ Test case for the Bus class.
    """

    def test_reset(self):
        """ Test initialisation of bus result attributes.
        """
        bus = Bus()
        bus.v_magnitude = 0.95
        bus.v_angle = 15.0
        bus.p_lmbda = 50.0
        bus.q_lmbda = 20.0
        bus.mu_vmin = 10.0
        bus.mu_vmax = 10.0

        bus.reset()

        self.assertEqual(bus.v_magnitude, 0.95)
        self.assertEqual(bus.v_angle, 15.0)
        self.assertEqual(bus.p_lmbda, 0.0)
        self.assertEqual(bus.q_lmbda, 0.0)
        self.assertEqual(bus.mu_vmin, 0.0)
        self.assertEqual(bus.mu_vmax, 0.0)

#------------------------------------------------------------------------------
#  "BranchTest" class:
#------------------------------------------------------------------------------

class BranchTest(unittest.TestCase):
    """ Test case for the Branch class.
    """

    def test_bus_indexes(self):
        """ Test the from/to bus index property.
        """
        c = Case(name="c")
        bus1 = Bus(name="Bus 1")
        bus2 = Bus(name="Bus 2")
        bus3 = Bus(name="Bus 3")
        c.buses = [bus1, bus2, bus3]

        # Append to list.
        branch1 = Branch(bus3, bus1)
        c.branches.append(branch1)

        self.assertEqual(c.buses.index(branch1.from_bus), 2)
        self.assertEqual(c.buses.index(branch1.to_bus), 0)

        # Set list.
        branch2 = Branch(bus2, bus3)
        branch3 = Branch(bus2, bus1)
        c.branches = [branch2, branch3]

        self.assertEqual(c.buses.index(branch2.from_bus), 1)
        self.assertEqual(c.buses.index(branch2.to_bus), 2)

        # Move branch.
        branch2.from_bus = bus1
        self.assertEqual(c.buses.index(branch2.from_bus), 0)


    def test_reset(self):
        """ Test initialisation of bus result attributes.
        """
        branch = Branch(Bus(), Bus())

        branch.p_from = 25.0
        branch.p_to = -25.0
        branch.q_from = -9.0
        branch.q_to = 9.0
        branch.mu_s_from = 90.0
        branch.mu_s_to = 0.0
        branch.mu_angmin = 60.0
        branch.mu_angmax = 0.0

        branch.reset()

        self.assertEqual(branch.p_from, 0.0)
        self.assertEqual(branch.p_to, 0.0)
        self.assertEqual(branch.q_from, 0.0)
        self.assertEqual(branch.q_to, 0.0)
        self.assertEqual(branch.mu_s_from, 0.0)
        self.assertEqual(branch.mu_s_to, 0.0)
        self.assertEqual(branch.mu_angmin, 0.0)
        self.assertEqual(branch.mu_angmax, 0.0)

#------------------------------------------------------------------------------
#  "CaseReportTest" class:
#------------------------------------------------------------------------------

class CaseReportTest(unittest.TestCase):
    """ Defines a test case for the Pylon case report.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(PWL_FILE)


    def test_report(self):
        """ Test case report property values.
        """
        NewtonPF(self.case).solve()
        report = CaseReport(self.case)
        pl = 3

        self.assertEqual(report.n_buses, 30)
        self.assertEqual(report.n_connected_buses, 30)
        self.assertEqual(report.n_generators, 6)
        self.assertEqual(report.n_online_generators, 6)
        self.assertEqual(report.n_loads, 20)
        self.assertEqual(report.n_fixed_loads, 20)
        self.assertEqual(report.n_online_vloads, 0)
        self.assertEqual(report.n_shunts, 2)
        self.assertEqual(report.n_branches, 41)
        self.assertEqual(report.n_transformers, 0)
        self.assertEqual(report.n_interties, 7)
        self.assertEqual(report.n_areas, 3)

        self.assertAlmostEqual(report.total_pgen_capacity, 335.0, pl)
        self.assertAlmostEqual(report.total_qgen_capacity[0], -95.0, pl)
        self.assertAlmostEqual(report.total_qgen_capacity[1], 405.9, pl)
        self.assertAlmostEqual(report.online_pgen_capacity, 335.0, pl)
        self.assertAlmostEqual(report.online_qgen_capacity[0], -95.0, pl)
        self.assertAlmostEqual(report.online_qgen_capacity[1], 405.9, pl)
        self.assertAlmostEqual(report.actual_pgen, 191.644, pl)
        self.assertAlmostEqual(report.actual_qgen, 100.415, pl)
        self.assertAlmostEqual(report.fixed_p_demand, 189.2, pl)
        self.assertAlmostEqual(report.fixed_q_demand, 107.2, pl)
        self.assertAlmostEqual(report.vload_p_demand[0], 0.0, pl)
        self.assertAlmostEqual(report.vload_p_demand[1], 0.0, pl)
        self.assertAlmostEqual(report.p_demand, 189.2, pl)
        self.assertAlmostEqual(report.q_demand, 107.2, pl)
        self.assertAlmostEqual(report.shunt_pinj, 0.0, pl)
        self.assertAlmostEqual(report.shunt_qinj, 0.222, pl)
        self.assertAlmostEqual(report.losses[0], 2.4438, pl)
        self.assertAlmostEqual(report.losses[1], 8.9899, pl)
        self.assertAlmostEqual(report.branch_qinj, 15.553, pl)
        self.assertAlmostEqual(report.total_tie_pflow, 33.181, pl)
        self.assertAlmostEqual(report.total_tie_qflow, 27.076, pl)
        self.assertAlmostEqual(report.min_v_magnitude[0], 0.961, pl)
        self.assertEqual(report.min_v_magnitude[1], 7)
        self.assertAlmostEqual(report.max_v_magnitude[0], 1.000, pl)
#        self.assertEqual(report.max_v_magnitude[1], 0)
        self.assertAlmostEqual(report.min_v_angle[0], -3.9582, pl)
        self.assertEqual(report.min_v_angle[1], 18)
        self.assertAlmostEqual(report.max_v_angle[0], 1.4762, pl)
        self.assertEqual(report.max_v_angle[1], 12)
        self.assertAlmostEqual(report.max_p_losses[0], 0.2892, pl)
        self.assertEqual(report.max_p_losses[1], 1)
        self.assertEqual(report.max_p_losses[2], 5)
        self.assertAlmostEqual(report.max_q_losses[0], 2.0970, pl)
        self.assertEqual(report.max_q_losses[1], 11)
        self.assertEqual(report.max_q_losses[2], 12)


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
