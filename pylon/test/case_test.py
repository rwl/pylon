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

import os
from os.path import join, dirname, exists, getsize
import unittest
import tempfile

from pylon import Case, Bus, Branch, Generator
from pylon.readwrite import PickleReader

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

MP_DATA_FILE = join(dirname(__file__), "data", "case6ww.m")
DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")
PWL_FILE = join(dirname(__file__), "data", "case30pwl.pkl")

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

    #--------------------------------------------------------------------------
    #  Admittance matrix tests.
    #--------------------------------------------------------------------------

    def test_admittance(self):
        """ Test the values of the admittance matrix.

           4.0063 -11.7479i  -2.0000 + 4.0000i        0            -1.1765 + 4.7059i  -0.8299 + 3.1120i        0
          -2.0000 + 4.0000i   9.3283 -23.1955i  -0.7692 + 3.8462i  -4.0000 + 8.0000i  -1.0000 + 3.0000i  -1.5590 + 4.4543i
                0            -0.7692 + 3.8462i   4.1557 -16.5673i        0            -1.4634 + 3.1707i  -1.9231 + 9.6154i
          -1.1765 + 4.7059i  -4.0000 + 8.0000i        0             6.1765 -14.6359i  -1.0000 + 2.0000i        0
          -0.8299 + 3.1120i  -1.0000 + 3.0000i  -1.4634 + 3.1707i  -1.0000 + 2.0000i   5.2933 -14.1378i  -1.0000 + 3.0000i
                0            -1.5590 + 4.4543i  -1.9231 + 9.6154i        0            -1.0000 + 3.0000i   4.4821 -17.0047i

        """
        Y, _, _ = self.case.Y

        self.assertEqual(Y.shape, (6, 6))

        places = 4

        # Validate diagonal values.
        Y_0_0 = 4.0063-11.7479j
        Y_2_2 = 4.1557-16.5673j
        Y_5_5 = 4.4821-17.0047j
        self.assertAlmostEqual(abs(Y[0, 0]), abs(Y_0_0), places)
        self.assertAlmostEqual(abs(Y[2, 2]), abs(Y_2_2), places)
        self.assertAlmostEqual(abs(Y[5, 5]), abs(Y_5_5), places)

        # Validate off-diagonal values.
        Y_0_1 = -2.0000+4.0000j
        Y_2_0 = 0.0000
        Y_4_1 = -1.0000+3.0000j
        Y_2_5 = -1.9231+9.6154j
        self.assertAlmostEqual(abs(Y[0, 1]), abs(Y_0_1), places)
        self.assertAlmostEqual(abs(Y[2, 0]), abs(Y_2_0), places)
        self.assertAlmostEqual(abs(Y[4, 1]), abs(Y_4_1), places)
        self.assertAlmostEqual(abs(Y[2, 5]), abs(Y_2_5), places)

        # Validate that elements [i, j] and [j, i] are equal.
        w, h = Y.shape
        for i in range(w):
            for j in range(h):
                if (i != j) and (i < j):
                    self.assertEqual(abs(Y[i, j]), abs(Y[j, i]))

    #--------------------------------------------------------------------------
    #  Susceptance matrix tests.
    #--------------------------------------------------------------------------

    def test_susceptance(self):
        """ Test the values of the susceptance matrix.

            B =

               13.3333   -5.0000         0   -5.0000   -3.3333         0
               -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000
                     0   -4.0000   17.8462         0   -3.8462  -10.0000
               -5.0000  -10.0000         0   17.5000   -2.5000         0
               -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333
                     0   -5.0000  -10.0000         0   -3.3333   18.3333

        """
        B, Bf, Pbusinj, Pfinj = self.case.Bdc

        places = 4

        self.assertEqual(B.shape, (6,6))
        # Validate diagonal values.
        self.assertAlmostEqual(B[0, 0], 13.3333, places)
        self.assertAlmostEqual(B[2, 2], 17.8462, places)
        self.assertAlmostEqual(B[4, 4], 16.3462, places)
        # Validate off-diagonal values.
        self.assertAlmostEqual(B[0, 1], -5.0000, places)
        self.assertAlmostEqual(B[0, 4], -3.3333, places)
        self.assertAlmostEqual(B[5, 2], -10.000, places)
        # Validate that elements [i, j] and [j, i] are equal.
        w, h = B.shape
        for i in range(w):
            for j in range(h):
                if (i != j) and (i < j):
                    self.assertEqual(abs(B[i, j]), abs(B[j, i]))

        self.assertEqual(Bf.shape, (11,6))
        self.assertAlmostEqual(Bf[0, 0], 5.0000, places)
        self.assertAlmostEqual(Bf[4, 3],-10.000, places)
        self.assertAlmostEqual(Bf[7, 2], 3.8462, places)
        self.assertAlmostEqual(Bf[9, 3], 2.5000, places)

        self.assertEqual(Pbusinj.shape, (6,))
        for v in Pbusinj:
            self.assertEqual(v, 0.0)

        self.assertEqual(Pfinj.shape, (11,))
        for v in Pfinj:
            self.assertEqual(v, 0.0)

    #--------------------------------------------------------------------------
    #  Bus injection tests:
    #--------------------------------------------------------------------------

    def test_bus_injections(self):
        """ Test totals of complex bus power injection.
        """
        bus = Bus(p_demand=200.0, q_demand=120.0)
        g1 = Generator(bus, p=200.0, q=50.0)
        g2 = Generator(bus, p=100.0, q=50.0)
        g3 = Generator(bus, p=-50, q=-10, p_max=0.0, p_min=-100.0)
        case = Case(buses=[bus], generators=[g1, g2, g3])

        self.assertAlmostEqual(abs(case.s_supply(bus)), 316.2278, 4)
        self.assertAlmostEqual(abs(case.s_demand(bus)), 281.7801, 4)
        self.assertAlmostEqual(abs(case.s_surplus(bus)), 58.3095, 4)

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

        self.assertEqual(bus.v_magnitude, 0.0)
        self.assertEqual(bus.v_angle, 0.0)
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


    def test_losses(self):
        """ Test the power loss properties.
        """
        e = Branch(Bus(), Bus())
        e.p_from = 100.0
        e.p_to = -90.0

        self.assertAlmostEqual(e.p_losses, 10.0, places=4)

        e.q_from = 30.0
        e.q_to = -20.0

        self.assertAlmostEqual(e.q_losses, 10.0, places=4)


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


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
