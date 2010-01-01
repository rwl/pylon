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

""" Test case for the optimal power flow solver.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from cvxopt import solvers

from pylon.readwrite import PickleReader
from pylon import OPF, Generator, REFERENCE, POLYNOMIAL, PIECEWISE_LINEAR

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DATA_FILE = join(dirname(__file__), "data", "case6ww.pkl")
PWL_FILE  = join(dirname(__file__), "data", "case30pwl.pkl")

#------------------------------------------------------------------------------
#  "OPFTest" class:
#------------------------------------------------------------------------------

class OPFTest(unittest.TestCase):
    """ Tests results from OPF against those obtained from MATPOWER.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)

        self.solver = OPF(self.case, show_progress=False)


    def test_algorithm_parameters(self):
        """ Test setting of CVXOPT solver options.
        """
        self.solver.max_iterations = 150
        self.solver.absolute_tol = 1e-8

        self.solver._algorithm_parameters()

        self.assertFalse(solvers.options["show_progress"])
        self.assertEqual(solvers.options["maxiters"], 150)
        self.assertEqual(solvers.options["abstol"], 1e-8)


    def test_one_reference(self):
        """ Test the check for one reference bus.
        """
        oneref, refs = self.solver._ref_check(self.case)

        self.assertTrue(oneref)
        self.assertEqual(refs[0], 0)


    def test_not_one_reference(self):
        """ Test check for one reference bus.
        """
        self.case.buses[1].type = REFERENCE
        oneref, refs = self.solver._ref_check(self.case)

        self.assertFalse(oneref)
        self.assertEqual(len(refs), 2)


    def test_remove_isolated(self):
        """ Test deactivation of isolated branches and generators.
        """
        # TODO: Repeat for a case with isolated buses.
        buses, branches, generators = self.solver._remove_isolated(self.case)

        self.assertEqual(len(buses), 6)
        self.assertEqual(len(branches), 11)
        self.assertEqual(len(generators), 3)


    def test_dimension_data(self):
        """ Test computation of problem dimensions.
        """
        buses, branches, generators = self.solver._remove_isolated(self.case)
        nb, nl, ng = self.solver._dimension_data(buses, branches, generators)

        self.assertEqual(nb, 6)
        self.assertEqual(nl, 11)
        self.assertEqual(ng, 3)


    def test_pwl1_to_poly(self):
        """ Test conversion of single-block pwl costs into linear polynomial.
        """
        g1 = Generator(self.case.buses[1], pcost_model=PIECEWISE_LINEAR,
            p_cost=[(0.0, 0.0), (100.0, 1000.0)])
        g2 = Generator(self.case.buses[2], pcost_model=PIECEWISE_LINEAR,
            p_cost=[(0.0, 0.0), (50.0, 500.0), (100.0, 1200.0)])

        self.solver._pwl1_to_poly([g1, g2])

        self.assertEqual(g1.pcost_model, POLYNOMIAL)
        self.assertEqual(g1.p_cost[0], 10.0)
        self.assertEqual(g1.p_cost[1], 0.0)
        self.assertEqual(g2.pcost_model, PIECEWISE_LINEAR)


    def test_variables(self):
        """ Test initial problem variables.
        """
        Va, Vm, Pg, Qg = self.solver._init_vars(self.case.buses,
                                                self.case.generators,
                                                self.case.base_mva)

        self.assertEqual(len(Va), 6)
        self.assertEqual(Va[0], 0.0)
        self.assertEqual(Va[5], 0.0)

        self.assertEqual(len(Vm), 6)
        self.assertEqual(Vm[0], 1.05)
        self.assertEqual(Vm[2], 1.07)
        self.assertEqual(Vm[3], 1.00)

        self.assertEqual(len(Pg), 3)
        self.assertEqual(Pg[0], 0.0)
        self.assertEqual(Pg[1], 0.5)
        self.assertEqual(Pg[2], 0.6)

        self.assertEqual(len(Qg), 3)
        self.assertEqual(Qg[0], 0.0)
        self.assertEqual(Qg[2], 0.0)


    def test_bounds(self):
        """ Test problem bounds.
        """
        Pmin, Pmax, Qmin, Qmax = self.solver._init_bounds(self.case.generators,
                                                          self.case.base_mva)

        self.assertEqual(Pmin[0], 0.5)
        self.assertEqual(Pmin[1], 0.375)
        self.assertEqual(Pmin[2], 0.45)

        self.assertEqual(Pmax[0], 2.0)
        self.assertEqual(Pmax[1], 1.5)
        self.assertEqual(Pmax[2], 1.8)

        self.assertEqual(Qmin[0], -1.0)
        self.assertEqual(Qmin[2], -1.0)

        self.assertEqual(Qmax[0], 1.0)
        self.assertEqual(Qmax[2], 1.0)


    def test_dc_power_mismatch(self):
        """ Test power balance constraint with DC model.

        Amis =

          Columns 1 through 7

           13.3333   -5.0000         0   -5.0000   -3.3333         0   -1.0000
           -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000         0
                 0   -4.0000   17.8462         0   -3.8462  -10.0000         0
           -5.0000  -10.0000         0   17.5000   -2.5000         0         0
           -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333         0
                 0   -5.0000  -10.0000         0   -3.3333   18.3333         0

          Columns 8 through 9

                 0         0
           -1.0000         0
                 0   -1.0000
                 0         0
                 0         0
                 0         0

        bmis =

                 0
                 0
                 0
           -0.7000
           -0.7000
           -0.7000
        """
        # See case_test.py for B test.
        B, _, Pbusinj, Pfinj = self.case.B
        nb, _, ng = self.solver._dimension_data(self.case.buses,
                                                 self.case.branches,
                                                 self.case.generators)
        Amis, bmis = self.solver._power_mismatch(self.case.buses,
                                                 self.case.generators,
                                                 nb, ng, B, Pbusinj,
                                                 self.case.base_mva)

        self.assertEqual(Amis.size, (6, 9))

        places = 4
        self.assertAlmostEqual(Amis[1, 1], 27.3333, places) # B diagonal
        self.assertAlmostEqual(Amis[4, 2], -3.8462, places) # Off-diagonal

        self.assertAlmostEqual(Amis[0, 6], -1.0, places)
        self.assertAlmostEqual(Amis[2, 8], -1.0, places)
        self.assertAlmostEqual(Amis[5, 8],  0.0, places)

        self.assertEqual(bmis.size, (6, 1))
        self.assertAlmostEqual(bmis[0], 0.0, places)
        self.assertAlmostEqual(bmis[3], -0.7, places)
        self.assertAlmostEqual(bmis[5], -0.7, places)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    logger = logging.getLogger("pylon")

    unittest.main()

# EOF -------------------------------------------------------------------------
