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

""" Test case for the optimal power flow solver.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname
import unittest

from numpy import Inf, zeros

from pylon import OPF, Case, Generator, REFERENCE, POLYNOMIAL, PW_LINEAR
from pylon.opf import DCOPFSolver, PIPSSolver

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

POLY_FILE = join(dirname(__file__), "data", "case6ww.pkl")
PWL_FILE  = join(dirname(__file__), "data", "case30pwl.pkl")

#------------------------------------------------------------------------------
#  "PWLOPFTest" class:
#------------------------------------------------------------------------------

class PWLOPFTest(unittest.TestCase):
    """ Tests results from OPF against those obtained from MATPOWER using a
        version of the 30 bus system with piece-wise linear generator costs.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(PWL_FILE)

        self.opf = OPF(self.case, dc=True)


    def test_one_reference(self):
        """ Test the check for one reference bus.
        """
        oneref, refs = self.opf._ref_check(self.case)

        self.assertTrue(oneref)
        self.assertEqual(refs[0], 0)


    def test_remove_isolated(self):
        """ Test deactivation of isolated branches and generators.
        """
        bs, ln, gn = self.opf._remove_isolated(self.case)

        self.assertEqual(len(bs), 30)
        self.assertEqual(len(ln), 41)
        self.assertEqual(len(gn), 6)


    def test_get_voltage_angle_var(self):
        """ Test the voltage angle variable.
        """
        _, refs = self.opf._ref_check(self.case)
        Va = self.opf._get_voltage_angle_var(refs, self.case.buses)

        self.assertEqual(len(Va.v0), 30)
        for v0 in Va.v0:
            self.assertEqual(v0, 0.0)

        self.assertEqual(Va.vu.shape, (30, ))
        self.assertEqual(Va.vu[0], 0.0)
        for vu in Va.vu[1:]:
            self.assertEqual(vu, Inf)

        self.assertEqual(Va.vl.shape, (30, ))
        self.assertEqual(Va.vl[0], 0.0)
        for vl in Va.vl[1:]:
            self.assertEqual(vl, -Inf)


    def test_get_pgen_var(self):
        """ Test active power variable.
        """
        Pg = self.opf._get_pgen_var(self.case.generators, self.case.base_mva)

        self.assertEqual(len(Pg.v0), 6)
        self.assertEqual(Pg.v0[0], 0.2354)
        self.assertEqual(Pg.v0[1], 0.6097)
        self.assertEqual(Pg.v0[2], 0.2159)
        self.assertEqual(Pg.v0[3], 0.2691)
        self.assertEqual(Pg.v0[4], 0.1920)
        self.assertEqual(Pg.v0[5], 0.3700)

        for vl in Pg.vl:
            self.assertEqual(vl, 0.0)

        self.assertEqual(Pg.vu[0], 0.8)
        self.assertEqual(Pg.vu[1], 0.8)
        self.assertEqual(Pg.vu[2], 0.5)
        self.assertEqual(Pg.vu[3], 0.55)
        self.assertEqual(Pg.vu[4], 0.3)
        self.assertEqual(Pg.vu[5], 0.4)


    def test_power_mismatch_dc(self):
        """ Test power balance constraints using DC model.
        """
        self.case.sort_generators() # ext2int()
        # See case_test.py for B test.
        B, _, Pbusinj, _ = self.case.Bdc
        Pmis = self.opf._power_mismatch_dc(self.case.buses,
                                           self.case.generators,
                                           B, Pbusinj, self.case.base_mva)

        self.assertEqual(Pmis.A.shape, (30, 36))

        places = 4
        self.assertAlmostEqual(Pmis.A[0, 0], 21.9298, places) # B diagonal
        self.assertAlmostEqual(Pmis.A[11, 3], -3.8462, places) # Off-diagonal

        self.assertAlmostEqual(Pmis.A[0, 30], -1.0, places)
        self.assertAlmostEqual(Pmis.A[12, 32], -1.0, places)
        self.assertAlmostEqual(Pmis.A[26, 35], -1.0, places)

        self.assertEqual(Pmis.l.shape, (30, ))
        self.assertAlmostEqual(Pmis.l[0], 0.0, places)
        self.assertAlmostEqual(Pmis.l[1], -0.2170, places)
        self.assertAlmostEqual(Pmis.l[29], -0.1060, places)


    def test_branch_flow_dc(self):
        """ Test maximum branch flow limit constraints.
        """
        _, Bf, _, Pfinj = self.case.Bdc
        Pf, Pt = self.opf._branch_flow_dc(self.case.branches, Bf, Pfinj,
                                          self.case.base_mva)

        self.assertEqual(Pf.l.shape, (41, ))
        self.assertEqual(Pf.N, Pt.N)

        for l in Pf.l:
            self.assertEqual(l, -Inf)

        self.assertEqual(Pf.u.shape, (41, ))
        self.assertEqual(Pf.u[0], 1.3)
        self.assertEqual(Pf.u[40], 0.32)

        for i in range(Pf.N):
            self.assertEqual(Pf.u[i], Pt.u[i])


    def test_voltage_angle_difference_limit(self):
        """ Test branch voltage angle difference limit.
        """
        self.opf.ignore_ang_lim = False
        ang = self.opf._voltage_angle_diff_limit(self.case.buses,
                                                 self.case.branches)

        self.assertEqual(ang.A.shape, (0, 30))
        self.assertEqual(ang.l.shape, (0,))
        self.assertEqual(ang.u.shape, (0,))
#        self.assertEqual(ang, None)


    def test_pwl_gen_cost(self):
        """ Test piece-wise linear generator cost constraints.
        """
        y, ycon = self.opf._pwl_gen_costs(self.case.generators,
                                          self.case.base_mva)

        self.assertEqual(y.N, 6)
        self.assertEqual(ycon.A.shape, (18, 12))
        self.assertEqual(ycon.u.shape, (18,))

#------------------------------------------------------------------------------
#  "PWLDCOPFSolverTest" class:
#------------------------------------------------------------------------------

class PWLDCOPFSolverTest(unittest.TestCase):
    """ Test case for the DC OPF solver.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(PWL_FILE)
        self.opf = OPF(self.case, dc=True, opt={"verbose": True})
        self.om = self.opf._construct_opf_model(self.case)
        self.solver = DCOPFSolver(self.om)


    def test_unpack_model(self):
        """ Test unpacking the OPF model.
        """
        buses, branches, generators, _ = self.solver._unpack_model(self.om)

        self.assertEqual(len(buses), 30)
        self.assertEqual(len(branches), 41)
        self.assertEqual(len(generators), 6)

        self.assertEqual(generators[0].bus, buses[0])
        self.assertEqual(generators[1].bus, buses[1])
        self.assertEqual(generators[2].bus, buses[21])


    def test_dimension_data(self):
        """ Test problem dimensions.
        """
        b, l, g, _ = self.solver._unpack_model(self.om)
        ipol, ipwl, nb, nl, nw, ny, nxyz = self.solver._dimension_data(b, l, g)

        self.assertEqual(len(ipol), 0)
        self.assertEqual(len(ipwl), 6)
        self.assertEqual(nb, 30)
        self.assertEqual(nl, 41)
        self.assertEqual(nw, 0)
        self.assertEqual(ny, 6)
        self.assertEqual(nxyz, 42)


    def test_constraints(self):
        """ Test equality and inequality constraints.
        """
        AA, ll, uu = self.solver._linear_constraints(self.om)

        self.assertEqual(AA.shape, (130, 42))
        self.assertEqual(ll.shape, (130,))
        self.assertEqual(uu.shape, (130,))


    def test_pwl_costs(self):
        """ Test piecewise linear costs.
        """
        b, l, g, _ = self.solver._unpack_model(self.om)
        _, ipwl, _, _, _, ny, nxyz = self.solver._dimension_data(b, l, g)
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz,
                                                                      ipwl)

        self.assertEqual(any_pwl, 1)
        self.assertEqual(Npwl.shape, (1, 42))
        self.assertEqual(Hpwl.shape, (1, 1))
        self.assertEqual(Cpwl.shape, (1,))
        self.assertEqual(fparm_pwl.shape, (1, 4))


    def test_poly_costs(self):
        """ Test quadratic costs.
        """
        base_mva = self.om.case.base_mva
        b, l, g, _ = self.solver._unpack_model(self.om)
        ipol, _, _, _, _, _, nxyz = self.solver._dimension_data(b, l, g)
        Npol, Hpol, Cpol, fparm_pol, _, npol = \
            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)

        self.assertEqual(npol, 0)
        self.assertEqual(Npol, None)
        self.assertEqual(Hpol, None)
        self.assertEqual(Cpol.shape, (0,))
        self.assertEqual(fparm_pol.shape, (0, 4))


    def test_combine_costs(self):
        """ Test combination of pwl and poly costs.

            TODO: Repeat with both pwl and poly costs.
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

        self.assertEqual(NN.shape, (1, 42))
        self.assertEqual(HHw.shape, (1, 1))
        self.assertEqual(CCw.shape, (1,))
        self.assertEqual(ffparm.shape, (1, 4))


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
        HH, CC, C0 = \
            self.solver._transform_coefficients(NN, HHw, CCw, ffparm, polycf,
                                                any_pwl, npol, nw)

        self.assertEqual(HH.shape, (42, 42))
        self.assertEqual(HH[0, 0], 0.0)
        self.assertEqual(HH[41, 41], 0.0)

        self.assertEqual(CC.shape, (42,))
        self.assertEqual(CC[0], 0.0)
        self.assertEqual(CC[36], 1.0)

        self.assertEqual(C0[0], 0.0)


    def test_var_bounds(self):
        """ Test bounds on optimisation variables.
        """
        x0, LB, UB = self.solver._var_bounds()

        self.assertEqual(x0.shape, (42,))
        self.assertEqual(x0[0], 0.0)
        self.assertEqual(x0[35], 0.3700) # Pg[5]

        self.assertEqual(LB.shape, (42,))
        self.assertEqual(LB[0], 0.0)
        self.assertEqual(LB[1], -Inf)
        self.assertEqual(LB[35], 0)

        self.assertEqual(UB.shape, (42,))
        self.assertEqual(UB[0], 0.0)
        self.assertEqual(UB[1], Inf)
        self.assertEqual(UB[35], 0.4000)


    def test_initial_point(self):
        """ Test selection of an initial interior point.
        """
        b, l, g, _ = self.solver._unpack_model(self.om)
        _, LB, UB = self.solver._var_bounds()
        _, _, _, _, _, ny, _ = self.solver._dimension_data(b, l, g)
        x0 = self.solver._initial_interior_point(b, g, LB, UB, ny)

        self.assertEqual(x0.shape, (42,))
        self.assertEqual(x0[0], 0.0)
        self.assertEqual(x0[30], 0.4)
        self.assertAlmostEqual(x0[41], 3643.2, 4)


    def test_run_opf(self):
        """ Test solution from the PIPS solver.
        """
        solution = self.solver.solve()
        x = solution["x"]
        lmbda = solution["lmbda"]

        pl = 4
        self.assertEqual(solution["output"]["iterations"], 10)
        self.assertEqual(x.shape, (42,))
        self.assertAlmostEqual(x[0], 0.0, pl)
        self.assertAlmostEqual(x[1], -0.0140, pl)
        self.assertAlmostEqual(x[30], 0.3600, pl)
        self.assertAlmostEqual(x[31], 0.2818, pl)
        self.assertAlmostEqual(x[40], 753.70, places=1)
        self.assertAlmostEqual(x[41], 1008.0, places=1)

#        self.assertEqual(lmbda["eqnonlin"].shape, (0,))
#        self.assertEqual(lmbda["ineqnonlin"].shape, (0,))
        self.assertEqual(lmbda["mu_l"].shape, (130,))
        self.assertEqual(lmbda["mu_u"].shape, (130,))
        self.assertEqual(lmbda["lower"].shape, (42,))
        self.assertEqual(lmbda["upper"].shape, (42,))
        self.assertAlmostEqual(lmbda["mu_u"][0], 4400.0, pl)
        self.assertAlmostEqual(lmbda["mu_u"][30], 0.0, pl)
        self.assertAlmostEqual(lmbda["mu_u"][129], 0.2, pl)
        self.assertAlmostEqual(lmbda["lower"][0], 0.0, pl)
        self.assertAlmostEqual(lmbda["lower"][31], 1.115e-5, places=8)
        self.assertAlmostEqual(lmbda["lower"][34], 1.669e-5, places=8)
        self.assertAlmostEqual(lmbda["upper"][0], 0.0, pl)
        self.assertAlmostEqual(lmbda["upper"][33], 1.821e-5, places=8)
        self.assertAlmostEqual(lmbda["upper"][35], 8.652e-5, places=8)

        self.assertTrue(solution["converged"])


    def test_update_solution_data(self):
        """ Test objective function value.
        """
        solver = self.solver

        base_mva = self.solver.om.case.base_mva
        buses, branches, generators, cp = \
            self.solver._unpack_model(self.om)
        ipol, ipwl, nb, nl, nw, ny, nxyz = \
            self.solver._dimension_data(buses, branches, generators)
        AA, ll, uu = self.solver._linear_constraints(self.om)
        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = \
            self.solver._pwl_costs(ny, nxyz, ipwl)
        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
            self.solver._quadratic_costs(generators, ipol, nxyz, base_mva)
        NN, HHw, CCw, ffparm = \
            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
                                       Npol, Hpol, Cpol, fparm_pol, npol, nw)
        HH, CC, C0 = \
            self.solver._transform_coefficients(NN, HHw, CCw, ffparm, polycf,
                                                any_pwl, npol, nw)
        _, LB, UB = self.solver._var_bounds()
        x0 = self.solver._initial_interior_point(buses, generators, LB, UB, ny)
        s = self.solver._run_opf(HH, CC, AA, ll, uu, LB, UB, x0,
                                 self.solver.opt)

        Va, Pg = self.solver._update_solution_data(s, HH, CC, C0)

        pl = 4
        self.assertAlmostEqual(Va[0], 0.0, pl)
        self.assertAlmostEqual(Va[27], -0.0308, pl)
        self.assertAlmostEqual(Va[29], -0.0177, pl)

        self.assertAlmostEqual(Pg[0], 0.3600, pl)
        self.assertAlmostEqual(Pg[1], 0.2818, pl)

        self.assertAlmostEqual(s["f"], 5.7328e03, pl)


    def test_update_case(self):
        """ Test solution from the PIPS solver.
        """
        case = self.case

        solution = self.solver.solve()

        pl = 4
        self.assertAlmostEqual(case.buses[1].v_angle, -0.8022, pl)
        self.assertAlmostEqual(case.buses[25].v_angle, -0.4973, places=3)
        self.assertAlmostEqual(case.buses[0].p_lmbda, 44.0, pl)
        self.assertAlmostEqual(case.buses[29].p_lmbda, 44.0, pl)

        self.assertAlmostEqual(case.branches[0].p_from, 23.3340, places=2)
        self.assertAlmostEqual(case.branches[0].p_to, -23.3340, places=2)
        self.assertAlmostEqual(case.branches[0].mu_s_from, 0.0, pl)
        self.assertAlmostEqual(case.branches[0].mu_s_to, 0.0, pl)

        self.assertAlmostEqual(case.generators[0].p, 36.0, pl)
        self.assertAlmostEqual(case.generators[1].p, 28.1824, places=2)
        self.assertAlmostEqual(case.generators[0].mu_pmin, 0.0, pl)
        self.assertAlmostEqual(case.generators[1].mu_pmax, 0.0, pl)

#------------------------------------------------------------------------------
#  "PIPSSolverTest" class:
#------------------------------------------------------------------------------

class PIPSSolverTest(unittest.TestCase):
    """ Test case for the PIPS OPF solver.
    """

    def setUp(self):
        """ The test runner will execute this method prior to each test.
        """
        self.case = Case.load(PWL_FILE)
        self.case.sort_generators()

        self.opf = OPF(self.case, dc=False)
        self.om = self.opf._construct_opf_model(self.case)
        self.solver = PIPSSolver(self.om, opt={"verbose": True})


    def test_solution(self):
        """ Test solution to AC OPF using PIPS.
        """
#        self.solver.opt["max_it"] = 1 # remove

        solution = self.solver.solve()
        x = solution["x"]
        lmbda = solution["lmbda"]

#        self.assertEqual(solution["output"]["iterations"], 14)

        self.assertEqual(x.shape, (78,))
        pl = 4
        # Va
        self.assertAlmostEqual(x[0], 0.0, pl)
        self.assertAlmostEqual(x[1], -0.0141, pl)
        self.assertAlmostEqual(x[29], -0.0266, pl)
        # Vm
        self.assertAlmostEqual(x[30], 0.9836, places=2)
        self.assertAlmostEqual(x[59], 1.0391, pl)
        # Pg
        self.assertAlmostEqual(x[60], 0.3600, pl)
        self.assertAlmostEqual(x[61], 0.3077, places=2)
        # Qg
        self.assertAlmostEqual(x[66],-0.0425, pl)
        self.assertAlmostEqual(x[67], 0.0589, pl)
        # y
        self.assertAlmostEqual(x[72], 1007.99, places=1)
        self.assertAlmostEqual(x[73], 1065.7, places=1)


    def test_update_case(self):
        """ Test solution from the PIPS solver.
        """
        case = self.case

        _ = self.solver.solve()

        pl = 4
        self.assertAlmostEqual(case.buses[1].v_angle, -0.8097, pl)
        self.assertAlmostEqual(case.buses[29].v_angle, -1.5253, pl)
        self.assertAlmostEqual(case.buses[0].v_magnitude, 0.9836, pl)
        self.assertAlmostEqual(case.buses[29].v_magnitude, 1.0391, pl)
        self.assertAlmostEqual(case.buses[0].p_lmbda, 43.6247, pl)
        self.assertAlmostEqual(case.buses[29].p_lmbda, 48.4146, pl)
        self.assertAlmostEqual(case.buses[0].q_lmbda, 0.0, pl)
        self.assertAlmostEqual(case.buses[7].q_lmbda, 18.0384, pl)
        self.assertAlmostEqual(case.buses[0].mu_vmax, 0.0, pl)
        self.assertAlmostEqual(case.buses[28].mu_vmax, 307.1142, pl)
        self.assertAlmostEqual(case.buses[0].mu_vmin, 0.0, pl)
        self.assertAlmostEqual(case.buses[29].mu_vmin, 0.0, pl)

        self.assertAlmostEqual(case.branches[0].p_from, 22.5473, pl)
        self.assertAlmostEqual(case.branches[0].p_to, -22.4421, pl)
        self.assertAlmostEqual(case.branches[0].q_from, -1.8726, pl)
        self.assertAlmostEqual(case.branches[0].q_to, -0.7021, pl)
        self.assertAlmostEqual(case.branches[9].mu_s_from, 30.3085, pl)
        self.assertAlmostEqual(case.branches[28].mu_s_to, 2.6488, pl)

        self.assertAlmostEqual(case.generators[0].p, 36.0, pl)
        self.assertAlmostEqual(case.generators[1].p, 30.7654, pl)
        self.assertAlmostEqual(case.generators[0].mu_pmax, 0.0, pl)
        self.assertAlmostEqual(case.generators[0].mu_pmin, 0.0, pl)
        self.assertAlmostEqual(case.generators[0].mu_qmax, 0.0, pl)
        self.assertAlmostEqual(case.generators[0].mu_qmin, 0.0, pl)

#------------------------------------------------------------------------------
#  "OPFTest" class:
#------------------------------------------------------------------------------

#class OPFTest(unittest.TestCase):
#    """ Tests results from OPF against those obtained from MATPOWER.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.case = Case.load(POLY_FILE)
#
#        self.opf = OPF(self.case, show_progress=False)
#
#
#    def test_algorithm_parameters(self):
#        """ Test setting of CVXOPT solver options.
#        """
#        self.opf.max_iterations = 150
#        self.opf.absolute_tol = 1e-8
#
#        self.opf._algorithm_parameters()
#
##        self.assertFalse(solvers.options["show_progress"])
##        self.assertEqual(solvers.options["maxiters"], 150)
##        self.assertEqual(solvers.options["abstol"], 1e-8)
#
#
#    def test_one_reference(self):
#        """ Test the check for one reference bus.
#        """
#        oneref, refs = self.opf._ref_check(self.case)
#
#        self.assertTrue(oneref)
#        self.assertEqual(refs[0], 0)
#
#
#    def test_not_one_reference(self):
#        """ Test check for one reference bus.
#        """
#        self.case.buses[1].type = REFERENCE
#        oneref, refs = self.opf._ref_check(self.case)
#
#        self.assertFalse(oneref)
#        self.assertEqual(len(refs), 2)
#
#
#    def test_remove_isolated(self):
#        """ Test deactivation of isolated branches and generators.
#        """
#        # TODO: Repeat for a case with isolated buses.
#        buses, branches, generators = self.opf._remove_isolated(self.case)
#
#        self.assertEqual(len(buses), 6)
#        self.assertEqual(len(branches), 11)
#        self.assertEqual(len(generators), 3)
#
#
#    def test_pwl1_to_poly(self):
#        """ Test conversion of single-block pwl costs into linear polynomial.
#        """
#        g1 = Generator(self.case.buses[1], pcost_model=PW_LINEAR,
#            p_cost=[(0.0, 0.0), (100.0, 1000.0)])
#        g2 = Generator(self.case.buses[2], pcost_model=PW_LINEAR,
#            p_cost=[(0.0, 0.0), (50.0, 500.0), (100.0, 1200.0)])
#
#        self.opf._pwl1_to_poly([g1, g2])
#
#        self.assertEqual(g1.pcost_model, POLYNOMIAL)
#        self.assertEqual(g1.p_cost[0], 10.0)
#        self.assertEqual(g1.p_cost[1], 0.0)
#        self.assertEqual(g2.pcost_model, PW_LINEAR)
#
#
#    def test_get_voltage_angle_var(self):
#        """ Test the voltage angle variable.
#        """
#        _, refs = self.opf._ref_check(self.case)
#        Va = self.opf._get_voltage_angle_var(refs, self.case.buses)
#
#        self.assertEqual(len(Va.v0), 6)
#        self.assertEqual(Va.v0[0], 0.0)
#        self.assertEqual(Va.v0[5], 0.0)
#
#        self.assertEqual(Va.vu.shape, (6, 1))
#        self.assertEqual(Va.vu[0], 0.0)
#        self.assertEqual(Va.vu[1], INF)
#
#        self.assertEqual(Va.vl.shape, (6, 1))
#        self.assertEqual(Va.vl[0], 0.0)
#        self.assertEqual(Va.vl[1], -INF)
#
##        self.assertEqual(len(Vm.v0), 6)
##        self.assertEqual(Vm.v0[0], 1.05)
##        self.assertEqual(Vm.v0[2], 1.07)
##        self.assertEqual(Vm.v0[3], 1.00)
#
#
#    def test_get_pgen_var(self):
#        """ Test active power variable.
#        """
#        Pg = self.opf._get_pgen_var(self.case.generators, self.case.base_mva)
#
#        self.assertEqual(len(Pg.v0), 3)
#        self.assertEqual(Pg.v0[0], 0.0)
#        self.assertEqual(Pg.v0[1], 0.5)
#        self.assertEqual(Pg.v0[2], 0.6)
#
##        self.assertEqual(len(Qg.v0), 3)
##        self.assertEqual(Qg.v0[0], 0.0)
##        self.assertEqual(Qg.v0[2], 0.0)
#
#        self.assertEqual(Pg.vl[0], 0.5)
#        self.assertEqual(Pg.vl[1], 0.375)
#        self.assertEqual(Pg.vl[2], 0.45)
#
#        self.assertEqual(Pg.vu[0], 2.0)
#        self.assertEqual(Pg.vu[1], 1.5)
#        self.assertEqual(Pg.vu[2], 1.8)
#
##        self.assertEqual(Qmin[0], -1.0)
##        self.assertEqual(Qmin[2], -1.0)
##
##        self.assertEqual(Qmax[0], 1.0)
##        self.assertEqual(Qmax[2], 1.0)
#
#
#    def test_power_mismatch_dc(self):
#        """ Test power balance constraints using DC model.
#
#        Amis =
#
#          Columns 1 through 7
#
#           13.3333   -5.0000         0   -5.0000   -3.3333         0   -1.0000
#           -5.0000   27.3333   -4.0000  -10.0000   -3.3333   -5.0000         0
#                 0   -4.0000   17.8462         0   -3.8462  -10.0000         0
#           -5.0000  -10.0000         0   17.5000   -2.5000         0         0
#           -3.3333   -3.3333   -3.8462   -2.5000   16.3462   -3.3333         0
#                 0   -5.0000  -10.0000         0   -3.3333   18.3333         0
#
#          Columns 8 through 9
#
#                 0         0
#           -1.0000         0
#                 0   -1.0000
#                 0         0
#                 0         0
#                 0         0
#
#        bmis =
#
#                 0
#                 0
#                 0
#           -0.7000
#           -0.7000
#           -0.7000
#        """
#        # See case_test.py for B test.
#        B, _, Pbusinj, _ = self.case.Bdc
#        Pmis = self.opf._power_mismatch_dc(self.case.buses,
#                                              self.case.generators,
#                                              B, Pbusinj, self.case.base_mva)
#
#        self.assertEqual(Pmis.A.shape, (6, 9))
#
#        places = 4
#        self.assertAlmostEqual(Pmis.A[1, 1], 27.3333, places) # B diagonal
#        self.assertAlmostEqual(Pmis.A[4, 2], -3.8462, places) # Off-diagonal
#
#        self.assertAlmostEqual(Pmis.A[0, 6], -1.0, places)
#        self.assertAlmostEqual(Pmis.A[2, 8], -1.0, places)
#        self.assertAlmostEqual(Pmis.A[5, 8],  0.0, places)
#
#        self.assertEqual(Pmis.l.shape, (6, 1))
#        self.assertAlmostEqual(Pmis.l[0], 0.0, places)
#        self.assertAlmostEqual(Pmis.l[3], -0.7, places)
#        self.assertAlmostEqual(Pmis.l[5], -0.7, places)
#
#
#    def test_branch_flow_dc(self):
#        """ Test maximum branch flow limit constraints.
#        """
#        _, Bf, _, Pfinj = self.case.Bdc
#        Pf, Pt = self.opf._branch_flow_dc(self.case.branches, Bf, Pfinj,
#                                             self.case.base_mva)
#
#        self.assertEqual(Pf.l.shape, (11,1))
#        self.assertEqual(Pf.l[0],  -INF)
#        self.assertEqual(Pf.l[10], -INF)
#
#        self.assertEqual(Pf.u.shape, (11,1))
#        self.assertEqual(Pf.u[0], 0.4)
#        self.assertEqual(Pf.u[5], 0.3)
#        self.assertEqual(Pf.u[6], 0.9)
#        self.assertEqual(Pf.u[9], 0.2)
#
#        self.assertEqual(Pt.u.shape, (11,1))
#        self.assertEqual(Pt.u[1], 0.6)
#        self.assertEqual(Pt.u[4], 0.6)
#        self.assertEqual(Pt.u[7], 0.7)
#        self.assertEqual(Pt.u[8], 0.8)
#
#
#    def test_voltage_angle_difference_limit(self):
#        """ Test branch voltage angle difference limit.
#        """
#        self.opf.ignore_ang_lim = False
#        ang = self.opf._voltage_angle_diff_limit(self.case.buses,
#                                                    self.case.branches)
#
#        self.assertEqual(ang.A.shape, (0, 6))
#        self.assertEqual(ang.l.shape, (0, 0))
#        self.assertEqual(ang.u.shape, (0, 0))
#
#
#    def test_pwl_gen_cost(self):
#        """ Test piece-wise linear generator cost constraints.
#        """
#        y, ycon = self.opf._pwl_gen_costs(self.case.generators,
#                                          self.case.base_mva)
#
#        self.assertEqual(y, None)
#        self.assertEqual(ycon, None)
##        self.assertEqual(ycon.A.shape, (3, 0))
##        self.assertEqual(ycon.u.shape, (0, 0))

#------------------------------------------------------------------------------
#  "DCOPFSolverTest" class:
#------------------------------------------------------------------------------

#class DCOPFSolverTest(unittest.TestCase):
#    """ Test case for the DC OPF solver.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.case = Case.load(POLY_FILE)
#        self.opf = OPF(self.case, show_progress=True)
#        self.om = self.opf._construct_opf_model(self.case)
#        self.solver = DCOPFSolver(self.om)
#
#
#    def test_unpack_model(self):
#        """ Test unpacking the OPF model.
#        """
#        buses, branches, generators, cp = self.solver._unpack_model(self.om)
#
#        self.assertEqual(len(buses), 6)
#        self.assertEqual(len(branches), 11)
#        self.assertEqual(len(generators), 3)
#
#        self.assertEqual(generators[0].bus, buses[0])
#        self.assertEqual(generators[1].bus, buses[1])
#        self.assertEqual(generators[2].bus, buses[2])
#
#
#    def test_dimension_data(self):
#        """ Test problem dimensions.
#        """
#        b, l, g, _ = self.solver._unpack_model(self.om)
#        ipol, ipwl, nb, nl, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
#
#        self.assertEqual(list(ipol), [0, 1, 2])
#        self.assertEqual(ipwl.shape, (0, 1))
#        self.assertEqual(nb, 6)
#        self.assertEqual(nl, 11)
#        self.assertEqual(nw, 0)
#        self.assertEqual(ny, 0)
#        self.assertEqual(nxyz, 9)
#
#
#    def test_constraints(self):
#        """ Test equality and inequality constraints.
#        """
#        Aeq, beq, Aieq, bieq = self.solver._linear_constraints(self.om)
#
#        self.assertEqual(Aeq.shape, (6, 9))
#        self.assertEqual(beq.shape, (6, 1))
#        self.assertEqual(Aieq.shape, (22, 9))
#        self.assertEqual(bieq.shape, (22, 1))
#
#
#    def test_pwl_costs(self):
#        """ Test piecewise linear costs.
#        """
#        b, l, g, _ = self.solver._unpack_model(self.om)
#        _, _, _, _, _, ny, nxyz = self.solver._dimension_data(b, l, g)
#        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz)
#
#        self.assertEqual(any_pwl, 0)
#        self.assertEqual(Npwl.shape, (0, 9))
#        self.assertEqual(Hpwl.shape, (0, 0))
#        self.assertEqual(Cpwl.shape, (0, 1))
#        self.assertEqual(fparm_pwl.shape, (0, 4))
#
#
#    def test_poly_costs(self):
#        """ Test quadratic costs.
#        """
#        base_mva = self.om.case.base_mva
#        b, l, g, _ = self.solver._unpack_model(self.om)
#        ipol, _, _, _, _, _, nxyz = self.solver._dimension_data(b, l, g)
#        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
#            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
#
#        self.assertEqual(npol, 3)
#
#        self.assertEqual(Npol.shape, (3, 9))
#        self.assertEqual(Npol[0, 0], 0.0)
#        self.assertEqual(Npol[1, 7], 1.0)
#
#        self.assertEqual(Hpol.shape, (3, 3))
#        self.assertEqual(Hpol[0, 0], 106.6)
#        self.assertEqual(Hpol[1, 1], 177.8)
#        self.assertEqual(Hpol[2, 2], 148.2)
#
#        self.assertEqual(Cpol.shape, (3, 1))
#        self.assertEqual(Cpol[0], 1.1669e3)
#        self.assertEqual(Cpol[1], 1.0333e3)
#        self.assertEqual(Cpol[2], 1.0833e3)
#
#        self.assertEqual(fparm_pol.shape, (3, 4))
#        self.assertEqual(fparm_pol[0, 0], 1.0)
#        self.assertEqual(fparm_pol[1, 0], 1.0)
#        self.assertEqual(fparm_pol[1, 1], 0.0)
#        self.assertEqual(fparm_pol[2, 3], 1.0)
#
#
#    def test_combine_costs(self):
#        """ Test combination of pwl and poly costs.
#
#            TODO: Repeat with combined pwl and poly costs.
#        """
#        base_mva = self.om.case.base_mva
#        b, l, g, _ = self.solver._unpack_model(self.om)
#        ipol, _, _, _, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
#        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz)
#        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
#            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
#        NN, HHw, CCw, ffparm = \
#            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
#                                       Npol, Hpol, Cpol, fparm_pol, npol)
#
#        self.assertEqual(NN.shape, (3, 9))
#        self.assertEqual(HHw.shape, (3, 3))
#        self.assertEqual(CCw.shape, (3, 1))
#        self.assertEqual(ffparm.shape, (3, 4))
#
#
#    def test_coefficient_transformation(self):
#        """ Test transformation of quadratic coefficients for w into
#            coefficients for X.
#        """
#        base_mva = self.om.case.base_mva
#        b, l, g, _ = self.solver._unpack_model(self.om)
#        ipol, _, _, _, nw, ny, nxyz = self.solver._dimension_data(b, l, g)
#        Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl = self.solver._pwl_costs(ny, nxyz)
#        Npol, Hpol, Cpol, fparm_pol, polycf, npol = \
#            self.solver._quadratic_costs(g, ipol, nxyz, base_mva)
#        NN, HHw, CCw, ffparm = \
#            self.solver._combine_costs(Npwl, Hpwl, Cpwl, fparm_pwl, any_pwl,
#                                       Npol, Hpol, Cpol, fparm_pol, npol)
#        HH, CC, C0 = self.solver._transform_coefficients(NN, HHw, CCw, ffparm,
#                                                         polycf, any_pwl, npol,
#                                                         nw)
#
#        self.assertEqual(HH.shape, (9, 9))
#        self.assertEqual(HH[0, 0], 0.0)
#        self.assertEqual(HH[8, 8], 148.2)
#
#        self.assertEqual(CC.shape, (9, 1))
#        self.assertEqual(CC[0], 0.0)
#        self.assertEqual(CC[6], 1.1669e3)
#
#        self.assertEqual(C0[0], 653.1)
#
#
#    def test_var_bounds(self):
#        """ Test bounds on optimisation variables.
#        """
#        x0, LB, UB = self.solver._var_bounds()
#
#        self.assertEqual(x0.shape, (9, 1))
#        self.assertEqual(x0[0], 0.0)
#        self.assertEqual(x0[7], 0.5)
#
#        self.assertEqual(LB.shape, (9, 1))
#        self.assertEqual(LB[0], 0.0)
#        self.assertTrue(LB[1] == -INF)
#        self.assertEqual(LB[7], 0.375)
#
#        self.assertEqual(UB.shape, (9, 1))
#        self.assertEqual(UB[0], 0.0)
#        self.assertTrue(UB[1] == INF)
#        self.assertEqual(UB[8], 1.8)
#
#
#    def test_initial_point(self):
#        """ Test selection of an initial interior point.
#        """
#        b, _, _, _ = self.solver._unpack_model(self.om)
#        _, LB, UB = self.solver._var_bounds()
#        x0 = self.solver._initial_interior_point(b, LB, UB)
#
#        self.assertEqual(x0.shape, (9, 1))
#        self.assertEqual(x0[0], 0.0)
#        self.assertEqual(x0[8], 1.125)


#    def test_cvxopt_solution(self):
#        """ Test the solver's solution.
#        """
#        solution = self.solver.solve()
#        x = solution["x"]
#
#        self.assertEqual(solution["status"], "optimal")
#        pl = 2
#        self.assertEqual(x[0], 0.0)
#        self.assertAlmostEqual(x[6], 0.5, pl)
#        self.assertAlmostEqual(x[7], 0.88, pl)
#        self.assertAlmostEqual(x[8], 0.72, pl)


#    def test_pips_qp_solution(self):
#        """ Test the solution from the native PIPS solver.
#        """
#        self.opf._algorithm_parameters()
#        self.solver.cvxopt = False
#        solution = self.solver.solve()
#        x = solution["xout"]
#        lmbda = solution["lmbdaout"]
#
#        pl = 4
#        self.assertAlmostEqual(x[0], 0.0, pl)
#        self.assertAlmostEqual(x[6], 0.5, pl)
#        self.assertAlmostEqual(x[7], 0.8807, pl)
#        self.assertAlmostEqual(x[8], 0.7193, pl)
#
#        self.assertAlmostEqual(lmbda[0], 1.1899e03, places=1)
#        self.assertAlmostEqual(lmbda[1], 1.1899e03, places=1)
#        self.assertAlmostEqual(lmbda[34], 3.03e01, places=1)
#
#        self.assertEqual(solution["howout"], "success")
#        self.assertTrue(solution["success"])

#------------------------------------------------------------------------------
#  "PIPSSolverTest" class:
#------------------------------------------------------------------------------

#class PIPSSolverTest(unittest.TestCase):
#    """ Test case for the PIPS OPF solver.
#    """
#
#    def setUp(self):
#        """ The test runner will execute this method prior to each test.
#        """
#        self.case = Case.load(POLY_FILE)
#        self.opf = OPF(self.case, dc=False)
#        self.om = self.opf._construct_opf_model(self.case)
#        self.solver = PIPSSolver(self.om, opt={"verbose": True})
#
#
#    def test_solution(self):
#        """ Test solution to AC OPF using PIPS.
#
#            x =
#
#                     0
#               -0.0346
#               -0.0390
#               -0.0536
#               -0.0684
#               -0.0719
#                1.0500
#                1.0500
#                1.0700
#                0.9882
#                0.9851
#                1.0046
#                0.7722
#                0.6927
#                0.7042
#                0.2572
#                0.6465
#                0.8664
#        """
#        printing.options["width"] = -1
#        printing.options["dformat"] = "%.20f"
#        self.solver.opt["max_it"] = 1
#
#        solution = self.solver.solve()
#        x = solution["x"]
##        lmbda = solution["lmbdaout"]
#
#        self.assertEqual(solution["output"]["iterations"], 9)
#
#        pl = 4
#        # Va
#        self.assertAlmostEqual(x[0], 0.0, pl)
#        self.assertAlmostEqual(x[1], -0.0346, pl)
#        self.assertAlmostEqual(x[2], -0.0390, pl)
#        self.assertAlmostEqual(x[3], -0.0536, pl)
#        self.assertAlmostEqual(x[4], -0.0684, pl)
#        self.assertAlmostEqual(x[5], -0.0719, pl)
#        # Vm
#        self.assertAlmostEqual(x[6], 1.05, pl)
#        self.assertAlmostEqual(x[7], 1.05, pl)
#        self.assertAlmostEqual(x[8], 1.07, pl)
#        self.assertAlmostEqual(x[9], 0.9882, pl)
#        self.assertAlmostEqual(x[10], 0.9851, pl)
#        self.assertAlmostEqual(x[11], 1.0046, pl)
#        # Pg
#        self.assertAlmostEqual(x[12], 0.7722, pl)
#        self.assertAlmostEqual(x[13], 0.6927, pl)
#        self.assertAlmostEqual(x[14], 0.7042, pl)
#        # Qg
#        self.assertAlmostEqual(x[15], 0.2572, pl)
#        self.assertAlmostEqual(x[16], 0.6465, pl)
#        self.assertAlmostEqual(x[17], 0.8664, pl)

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
