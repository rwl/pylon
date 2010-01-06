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
from pylon import OPF, Generator, REFERENCE, POLYNOMIAL, PW_LINEAR
from pylon.opf import INF, DCOPFSolver#, PDIPMSolver, CVXOPTSolver

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

        self.opf = OPF(self.case, show_progress=False)


    def test_algorithm_parameters(self):
        """ Test setting of CVXOPT solver options.
        """
        self.opf.max_iterations = 150
        self.opf.absolute_tol = 1e-8

        self.opf._algorithm_parameters()

        self.assertFalse(solvers.options["show_progress"])
        self.assertEqual(solvers.options["maxiters"], 150)
        self.assertEqual(solvers.options["abstol"], 1e-8)


    def test_one_reference(self):
        """ Test the check for one reference bus.
        """
        oneref, refs = self.opf._ref_check(self.case)

        self.assertTrue(oneref)
        self.assertEqual(refs[0], 0)


    def test_not_one_reference(self):
        """ Test check for one reference bus.
        """
        self.case.buses[1].type = REFERENCE
        oneref, refs = self.opf._ref_check(self.case)

        self.assertFalse(oneref)
        self.assertEqual(len(refs), 2)


    def test_remove_isolated(self):
        """ Test deactivation of isolated branches and generators.
        """
        # TODO: Repeat for a case with isolated buses.
        buses, branches, generators = self.opf._remove_isolated(self.case)

        self.assertEqual(len(buses), 6)
        self.assertEqual(len(branches), 11)
        self.assertEqual(len(generators), 3)


    def test_pwl1_to_poly(self):
        """ Test conversion of single-block pwl costs into linear polynomial.
        """
        g1 = Generator(self.case.buses[1], pcost_model=PW_LINEAR,
            p_cost=[(0.0, 0.0), (100.0, 1000.0)])
        g2 = Generator(self.case.buses[2], pcost_model=PW_LINEAR,
            p_cost=[(0.0, 0.0), (50.0, 500.0), (100.0, 1200.0)])

        self.opf._pwl1_to_poly([g1, g2])

        self.assertEqual(g1.pcost_model, POLYNOMIAL)
        self.assertEqual(g1.p_cost[0], 10.0)
        self.assertEqual(g1.p_cost[1], 0.0)
        self.assertEqual(g2.pcost_model, PW_LINEAR)


    def test_voltage_angle_var(self):
        """ Test the voltage angle variable.
        """
        _, refs = self.opf._ref_check(self.case)
        Va = self.opf._voltage_angle_var(refs, self.case.buses)

        self.assertEqual(len(Va.v0), 6)
        self.assertEqual(Va.v0[0], 0.0)
        self.assertEqual(Va.v0[5], 0.0)

        self.assertEqual(Va.vu.size, (6, 1))
        self.assertEqual(Va.vu[0], 0.0)
        self.assertEqual(Va.vu[1], INF)

        self.assertEqual(Va.vl.size, (6, 1))
        self.assertEqual(Va.vl[0], 0.0)
        self.assertEqual(Va.vl[1], -INF)

#        self.assertEqual(len(Vm.v0), 6)
#        self.assertEqual(Vm.v0[0], 1.05)
#        self.assertEqual(Vm.v0[2], 1.07)
#        self.assertEqual(Vm.v0[3], 1.00)


    def test_p_gen_var(self):
        """ Test active power variable.
        """
        Pg = self.opf._p_gen_var(self.case.generators, self.case.base_mva)

        self.assertEqual(len(Pg.v0), 3)
        self.assertEqual(Pg.v0[0], 0.0)
        self.assertEqual(Pg.v0[1], 0.5)
        self.assertEqual(Pg.v0[2], 0.6)

#        self.assertEqual(len(Qg.v0), 3)
#        self.assertEqual(Qg.v0[0], 0.0)
#        self.assertEqual(Qg.v0[2], 0.0)

        self.assertEqual(Pg.vl[0], 0.5)
        self.assertEqual(Pg.vl[1], 0.375)
        self.assertEqual(Pg.vl[2], 0.45)

        self.assertEqual(Pg.vu[0], 2.0)
        self.assertEqual(Pg.vu[1], 1.5)
        self.assertEqual(Pg.vu[2], 1.8)

#        self.assertEqual(Qmin[0], -1.0)
#        self.assertEqual(Qmin[2], -1.0)
#
#        self.assertEqual(Qmax[0], 1.0)
#        self.assertEqual(Qmax[2], 1.0)


    def test_power_mismatch_dc(self):
        """ Test power balance constraints using DC model.

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
        B, _, Pbusinj, _ = self.case.B
        Pmis = self.opf._power_mismatch_dc(self.case.buses,
                                              self.case.generators,
                                              B, Pbusinj, self.case.base_mva)

        self.assertEqual(Pmis.A.size, (6, 9))

        places = 4
        self.assertAlmostEqual(Pmis.A[1, 1], 27.3333, places) # B diagonal
        self.assertAlmostEqual(Pmis.A[4, 2], -3.8462, places) # Off-diagonal

        self.assertAlmostEqual(Pmis.A[0, 6], -1.0, places)
        self.assertAlmostEqual(Pmis.A[2, 8], -1.0, places)
        self.assertAlmostEqual(Pmis.A[5, 8],  0.0, places)

        self.assertEqual(Pmis.l.size, (6, 1))
        self.assertAlmostEqual(Pmis.l[0], 0.0, places)
        self.assertAlmostEqual(Pmis.l[3], -0.7, places)
        self.assertAlmostEqual(Pmis.l[5], -0.7, places)


    def test_branch_flow_dc(self):
        """ Test maximum branch flow limit constraints.
        """
        _, Bf, _, Pfinj = self.case.B
        Pf, Pt = self.opf._branch_flow_dc(self.case.branches, Bf, Pfinj,
                                             self.case.base_mva)

        self.assertEqual(Pf.l.size, (11,1))
        self.assertEqual(Pf.l[0],  -INF)
        self.assertEqual(Pf.l[10], -INF)

        self.assertEqual(Pf.u.size, (11,1))
        self.assertEqual(Pf.u[0], 0.4)
        self.assertEqual(Pf.u[5], 0.3)
        self.assertEqual(Pf.u[6], 0.9)
        self.assertEqual(Pf.u[9], 0.2)

        self.assertEqual(Pt.u.size, (11,1))
        self.assertEqual(Pt.u[1], 0.6)
        self.assertEqual(Pt.u[4], 0.6)
        self.assertEqual(Pt.u[7], 0.7)
        self.assertEqual(Pt.u[8], 0.8)


    def test_voltage_angle_difference_limit(self):
        """ Test branch voltage angle difference limit.
        """
        self.opf.ignore_ang_lim = False
        ang = self.opf._voltage_angle_diff_limit(self.case.buses,
                                                    self.case.branches)

        self.assertEqual(ang.A.size, (0, 6))
        self.assertEqual(ang.l.size, (0, 0))
        self.assertEqual(ang.u.size, (0, 0))


    def test_pwl_gen_cost(self):
        """ Test piece-wise linear generator cost constraints.
        """
        y, ycon = self.opf._pwl_gen_costs(self.case.generators,
                                          self.case.base_mva)

        self.assertEqual(y, None)
        self.assertEqual(ycon, None)
#        self.assertEqual(ycon.A.size, (3, 0))
#        self.assertEqual(ycon.u.size, (0, 0))

#------------------------------------------------------------------------------
#  "DCOPFSolverTest" class:
#------------------------------------------------------------------------------

class DCOPFSolverTest(unittest.TestCase):
    """ Test case for the DC OPF solver.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)
        self.opf = OPF(self.case, show_progress=False)
        self.om = self.opf._construct_opf_model(self.case)
        self.solver = DCOPFSolver(self.om)


    def test_unpack_model(self):
        """ Test unpacking the OPF model.
        """
        buses, branches, generators, cp, Bf, Pfinj = \
                                            self.solver._unpack_model(self.om)

        self.assertEqual(len(buses), 6)
        self.assertEqual(len(branches), 11)
        self.assertEqual(len(generators), 3)

        self.assertEqual(generators[0].bus, buses[0])
        self.assertEqual(generators[1].bus, buses[1])
        self.assertEqual(generators[2].bus, buses[2])


    def test_dimension_data(self):
        """ Test problem dimensions.
        """
        b, l, g, _, _, _ = self.solver._unpack_model(self.om)
        ipol, ipwl, nb, nl, nw, ny, nxyz = self.solver._dimension_data(b, l, g)

        self.assertEqual(list(ipol), [0, 1, 2])
        self.assertEqual(ipwl.size, (0, 1))
        self.assertEqual(nb, 6)
        self.assertEqual(nl, 11)
        self.assertEqual(nw, 0)
        self.assertEqual(ny, 0)
        self.assertEqual(nxyz, 9)


    def test_constraints(self):
        """ Test equality and inequality constraints.
        """
        Aeq, beq, Aieq, bieq = self.solver._split_constraints(self.om)

        self.assertEqual(Aeq.size, (6, 9))
        self.assertEqual(beq.size, (6, 1))
        self.assertEqual(Aieq.size, (22, 9))
        self.assertEqual(bieq.size, (22, 1))


    def test_pwl_costs(self):
        """ Test piecewise linear costs.
        """
        b, l, g, _, _, _ = self.solver._unpack_model(self.om)
        _, _, _, _, _, ny, nxyz = self.solver._dimension_data(b, l, g)
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz)

        self.assertEqual(any_pwl, 0)
        self.assertEqual(Npwl.size, (0, 9))
        self.assertEqual(Hpwl.size, (0, 0))
        self.assertEqual(Cpwl.size, (0, 1))
        self.assertEqual(fparm_pwl.size, (0, 4))


    def test_poly_costs(self):
        """ Test quadratic costs.
        """
        base_mva = self.om.case.base_mva
        b, l, g, _, _, _ = self.solver._unpack_model(self.om)
        ipol, _, _, _, _, _, nxyz = self.solver._dimension_data(b, l, g)
        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)

        self.assertEqual(npol, 3)

        self.assertEqual(Npol.size, (3, 9))
        self.assertEqual(Npol[0, 0], 0.0)
        self.assertEqual(Npol[1, 7], 1.0)

        self.assertEqual(Hpol.size, (3, 3))
        self.assertEqual(Hpol[0, 0], 106.6)
        self.assertEqual(Hpol[1, 1], 177.8)
        self.assertEqual(Hpol[2, 2], 148.2)

        self.assertEqual(Cpol.size, (3, 1))
        self.assertEqual(Cpol[0], 1.1669e3)
        self.assertEqual(Cpol[1], 1.0333e3)
        self.assertEqual(Cpol[2], 1.0833e3)

        self.assertEqual(fparm_pol.size, (3, 4))
        self.assertEqual(fparm_pol[0, 0], 1.0)
        self.assertEqual(fparm_pol[1, 0], 1.0)
        self.assertEqual(fparm_pol[1, 1], 0.0)
        self.assertEqual(fparm_pol[2, 3], 1.0)


    def test_combine_costs(self):
        """ Test combination of pwl and poly costs.

            TODO: Repeat with combined pwl and poly costs.
        """
        base_mva = self.om.case.base_mva
        b, l, g, _, _, _ = self.solver._unpack_model(self.om)
        ipol, _, _, _, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz)
        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
        NN, HHw, CCw, ffparm = \
            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
                                       Npol, Hpol, Cpol, fparm_pol, npol)

        self.assertEqual(NN.size, (3, 9))
        self.assertEqual(HHw.size, (3, 3))
        self.assertEqual(CCw.size, (3, 1))
        self.assertEqual(ffparm.size, (3, 4))


    def test_coefficient_transformation(self):
        """ Test transformation of quadratic coefficients for w into
            coefficients for X.
        """
        base_mva = self.om.case.base_mva
        b, l, g, _, _, _ = self.solver._unpack_model(self.om)
        ipol, _, _, _, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz)
        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
        NN, HHw, CCw, ffparm = \
            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
                                       Npol, Hpol, Cpol, fparm_pol, npol)
        HH, CC, C0 = self.solver._transform_coefficients(NN, HHw, CCw, ffparm,
                                                         polycf, any_pwl, npol,
                                                         nw)

        self.assertEqual(HH.size, (9, 9))
        self.assertEqual(HH[0, 0], 0.0)
        self.assertEqual(HH[8, 8], 148.2)

        self.assertEqual(CC.size, (9, 1))
        self.assertEqual(CC[0], 0.0)
        self.assertEqual(CC[6], 1.1669e3)

        self.assertEqual(C0[0], 653.1)


    def test_var_bounds(self):
        """ Test bounds on optimisation variables.
        """
        x0, LB, UB = self.solver.var_bounds()

        self.assertEqual(x0.size, (9, 1))
        self.assertEqual(x0[0], 0.0)
        self.assertEqual(x0[7], 0.5)

        self.assertEqual(LB.size, (9, 1))
        self.assertEqual(LB[0], 0.0)
        self.assertTrue(LB[1] == -INF)
        self.assertEqual(LB[7], 0.375)

        self.assertEqual(UB.size, (9, 1))
        self.assertEqual(UB[0], 0.0)
        self.assertTrue(UB[1] == INF)
        self.assertEqual(UB[8], 1.8)


    def test_initial_point(self):
        """ Test selection of an initial interior point.
        """
        b, _, _, _, _, _ = self.solver._unpack_model(self.om)
        _, LB, UB = self.solver.var_bounds()
        x0 = self.solver._initial_interior_point(self.om, b, LB, UB)

        self.assertEqual(x0.size, (9, 1))
        self.assertEqual(x0[0], 0.0)
        self.assertEqual(x0[8], 1.125)


#    def test_cvxopt_solution(self):
#        """ Test the solver's solution.
#        """
#        base_mva = self.om.case.base_mva
##        self.opf._algorithm_parameters()
#        b, l, g, _, _, _ = self.solver._unpack_model(self.om)
#        ipol, _, _, _, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
#        Aeq, beq, Aieq, bieq = self.solver._split_constraints(self.om)
#        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz)
#        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
#            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
#        NN, HHw, CCw, ffparm = \
#            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
#                                       Npol, Hpol, Cpol, fparm_pol, npol)
#        HH, CC, C0 = self.solver._transform_coefficients(NN, HHw, CCw, ffparm,
#                                                         polycf, any_pwl, npol,
#                                                         nw)
#        x0, LB, UB = self.solver.var_bounds()
#        sol = self.solver._run_opf(HH, CC, Aieq, bieq, Aeq, beq, LB, UB, x0)
#        x = sol["x"]
#
#        self.assertEqual(sol["status"], "optimal")
#        pl = 2
#        self.assertEqual(x[0], 0.0)
#        self.assertAlmostEqual(x[6], 0.5, pl)
#        self.assertAlmostEqual(x[7], 0.88, pl)
#        self.assertAlmostEqual(x[8], 0.72, pl)


    def test_pdipm_qp_solution(self):
        """ Test the solution from the native PDIPM solver.

            x =

                 0
           -0.0052
           -0.0049
           -0.0521
           -0.0640
           -0.0539
            0.5000
            0.8807
            0.7193
        """
        self.solver.cvxopt = False
        solution = self.solver.solve()
        x = solution["xout"]
        lmbda = solution["lmbdaout"]

        pl = 4
        self.assertAlmostEqual(x[0], 0.0, pl)
        self.assertAlmostEqual(x[6], 0.5, pl)
        self.assertAlmostEqual(x[7], 0.8807, pl)
        self.assertAlmostEqual(x[8], 0.7193, pl)

        self.assertAlmostEqual(lmbda[0], 1.1899e03, places=1)
        self.assertAlmostEqual(lmbda[1], 1.1899e03, places=1)
        self.assertAlmostEqual(lmbda[34], 3.03e01, places=1)

        self.assertEqual(solution["howout"], "success")
        self.assertTrue(solution["success"])

#------------------------------------------------------------------------------
#  "OPFModelTest" class:
#------------------------------------------------------------------------------

class OPFModelTest(unittest.TestCase):
    """ Test case for the OPF model.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = PickleReader().read(DATA_FILE)
        self.opf = OPF(self.case, show_progress=False)
        self.om = self.opf._construct_opf_model(self.case)


    def test_linear_constraints(self):
        """ Test linear OPF constraints.
        """
        A, l, u = self.om.linear_constraints()

        self.assertEqual(A.size, (28, 9))
        self.assertEqual(l.size, (28, 1))
        self.assertEqual(u.size, (28, 1))

        pl = 4
        self.assertAlmostEqual(A[0, 0], 13.3333, pl)
        self.assertAlmostEqual(A[4, 2], -3.8462, pl)
        self.assertAlmostEqual(A[2, 8], -1.0000, pl)
        self.assertAlmostEqual(A[9, 1],  4.0000, pl)
        self.assertAlmostEqual(A[27, 5], 3.3333, pl)

        self.assertAlmostEqual(l[0], 0.0000, pl)
        self.assertAlmostEqual(l[3], -0.7000, pl)
        self.assertAlmostEqual(l[6], -INF, pl)
        self.assertAlmostEqual(l[27], -INF, pl)

        self.assertAlmostEqual(u[0],  0.0000, pl)
        self.assertAlmostEqual(u[3], -0.7000, pl)
        self.assertAlmostEqual(u[6],  0.4000, pl)
        self.assertAlmostEqual(u[7],  0.6000, pl)
        self.assertAlmostEqual(u[23], 0.9000, pl)


if __name__ == "__main__":
    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(levelname)s: %(message)s")

    logger = logging.getLogger("pylon")

    unittest.main()

# EOF -------------------------------------------------------------------------
