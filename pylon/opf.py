#------------------------------------------------------------------------------
# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
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

""" Defines a generalised OPF solver and an OPF model.

Based on opf.m from MATPOWER by Ray Zimmerman, developed at PSERC Cornell.
See U{http://www.pserc.cornell.edu/matpower/} for more info.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
import random

from time import time

from numpy import \
    array, pi, diff, Inf, ones, r_, float64, zeros, arctan2, sin, cos

from scipy.sparse import lil_matrix, csr_matrix, hstack

from util import _Named, fair_max
from case import REFERENCE
from generator import PW_LINEAR
from solver import DCOPFSolver, PIPSSolver

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "OPF" class:
#------------------------------------------------------------------------------

class OPF(object):
    """ Defines a generalised OPF solver.

    Based on opf.m from MATPOWER by Ray Zimmerman, developed at PSERC
    Cornell. See U{http://www.pserc.cornell.edu/matpower/} for more info.
    """

    def __init__(self, case, dc=True, ignore_ang_lim=True, opt=None):
        """ Initialises a new OPF instance.
        """
        #: Case under optimisation.
        self.case = case

        #: Use DC power flow formulation.
        self.dc = dc

        #: Ignore angle difference limits for branches even if specified.
        self.ignore_ang_lim = ignore_ang_lim

        #: Solver options (See pips.py for futher details).
        self.opt = {} if opt is None else opt

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def solve(self, solver_klass=None):
        """ Solves an optimal power flow and returns a results dictionary.
        """
        # Start the clock.
        t0 = time()

        # Build an OPF model with variables and constraints.
        om = self._construct_opf_model(self.case)
        if om is None:
            return {"converged": False, "output": {"message": "No Ref Bus."}}

        # Call the specific solver.
#        if self.opt["verbose"]:
#            print '\nPYLON Version %s, %s', "0.4.2", "April 2010"
        if solver_klass is not None:
            result = solver_klass(om, opt=self.opt).solve()
        elif self.dc:
#            if self.opt["verbose"]:
#                print ' -- DC Optimal Power Flow\n'
            result = DCOPFSolver(om, opt=self.opt).solve()
        else:
#            if self.opt["verbose"]:
#                print ' -- AC Optimal Power Flow\n'
            result = PIPSSolver(om, opt=self.opt).solve()

        result["elapsed"] = time() - t0

        if self.opt.has_key("verbose"):
            if self.opt["verbose"]:
                logger.info("OPF completed in %.3fs." % result["elapsed"])

        return result

    #--------------------------------------------------------------------------
    #  Private interface:
    #--------------------------------------------------------------------------

    def _construct_opf_model(self, case):
        """ Returns an OPF model.
        """
        # Zero the case result attributes.
        self.case.reset()

        base_mva = case.base_mva

        # Check for one reference bus.
        oneref, refs = self._ref_check(case)
        if not oneref: #return {"status": "error"}
            None

        # Remove isolated components.
        bs, ln, gn = self._remove_isolated(case)

        # Update bus indexes.
        self.case.index_buses(bs)

        # Convert single-block piecewise-linear costs into linear polynomial.
        gn = self._pwl1_to_poly(gn)

        # Set-up initial problem variables.
        Va = self._get_voltage_angle_var(refs, bs)
        Pg = self._get_pgen_var(gn, base_mva)

        if self.dc: # DC model.
            # Get the susceptance matrices and phase shift injection vectors.
            B, Bf, Pbusinj, Pfinj = self.case.makeBdc(bs, ln)

            # Power mismatch constraints (B*Va + Pg = Pd).
            Pmis = self._power_mismatch_dc(bs, gn, B, Pbusinj, base_mva)

            # Branch flow limit constraints.
            Pf, Pt = self._branch_flow_dc(ln, Bf, Pfinj, base_mva)
        else:
            # Set-up additional AC-OPF problem variables.
            Vm = self._get_voltage_magnitude_var(bs, gn)
            Qg = self._get_qgen_var(gn, base_mva)

            Pmis, Qmis, Sf, St = self._nln_constraints(len(bs), len(ln))

            vl = self._const_pf_constraints(gn, base_mva)

            # TODO: Generator PQ capability curve constraints.
#            PQh, PQl = self._pq_capability_curve_constraints(gn)

        # Branch voltage angle difference limits.
        ang = self._voltage_angle_diff_limit(bs, ln)

        if self.dc:
            vars = [Va, Pg]
            constraints = [Pmis, Pf, Pt, ang]
        else:
            vars = [Va, Vm, Pg, Qg]
            constraints = [Pmis, Qmis, Sf, St, #PQh, PQL,
                           vl, ang]

        # Piece-wise linear generator cost constraints.
        y, ycon = self._pwl_gen_costs(gn, base_mva)

        if ycon is not None:
            vars.append(y)
            constraints.append(ycon)

        # Add variables and constraints to the OPF model object.
        opf = OPFModel(case)
        opf.add_vars(vars)
        opf.add_constraints(constraints)

        if self.dc: # user data
            opf._Bf = Bf
            opf._Pfinj = Pfinj

        return opf


    def _ref_check(self, case):
        """ Checks that there is only one reference bus.
        """
        refs = [bus._i for bus in case.buses if bus.type == REFERENCE]

        if len(refs) == 1:
            return True, refs
        else:
            logger.error("OPF requires a single reference bus.")
            return False, refs


    def _remove_isolated(self, case):
        """ Returns non-isolated case components.
        """
#        case.deactivate_isolated()
        buses = case.connected_buses
        branches = case.online_branches
        gens = case.online_generators

        return buses, branches, gens


    def _pwl1_to_poly(self, generators):
        """ Converts single-block piecewise-linear costs into linear
        polynomial.
        """
        for g in generators:
            if (g.pcost_model == PW_LINEAR) and (len(g.p_cost) == 2):
                g.pwl_to_poly()

        return generators

    #--------------------------------------------------------------------------
    #  Optimisation variables:
    #--------------------------------------------------------------------------

    def _get_voltage_angle_var(self, refs, buses):
        """ Returns the voltage angle variable set.
        """
        Va = array([b.v_angle * (pi / 180.0) for b in buses])

        Vau = Inf * ones(len(buses))
        Val = -Vau
        Vau[refs] = Va[refs]
        Val[refs] = Va[refs]

        return Variable("Va", len(buses), Va, Val, Vau)


    def _get_voltage_magnitude_var(self, buses, generators):
        """ Returns the voltage magnitude variable set.
        """
        Vm = array([b.v_magnitude for b in buses])

        # For buses with generators initialise Vm from gen data.
        for g in generators:
            Vm[g.bus._i] = g.v_magnitude

        Vmin = array([b.v_min for b in buses])
        Vmax = array([b.v_max for b in buses])

        return Variable("Vm", len(buses), Vm, Vmin, Vmax)


    def _get_pgen_var(self, generators, base_mva):
        """ Returns the generator active power set-point variable.
        """
        Pg = array([g.p / base_mva for g in generators])

        Pmin = array([g.p_min / base_mva for g in generators])
        Pmax = array([g.p_max / base_mva for g in generators])

        return Variable("Pg", len(generators), Pg, Pmin, Pmax)


    def _get_qgen_var(self, generators, base_mva):
        """ Returns the generator reactive power variable set.
        """
        Qg = array([g.q / base_mva for g in generators])

        Qmin = array([g.q_min / base_mva for g in generators])
        Qmax = array([g.q_max / base_mva for g in generators])

        return Variable("Qg", len(generators), Qg, Qmin, Qmax)

    #--------------------------------------------------------------------------
    #  Constraints:
    #--------------------------------------------------------------------------

    def _nln_constraints(self, nb, nl):
        """ Returns non-linear constraints for OPF.
        """
        Pmis = NonLinearConstraint("Pmis", nb)
        Qmis = NonLinearConstraint("Qmis", nb)
        Sf = NonLinearConstraint("Sf", nl)
        St = NonLinearConstraint("St", nl)

        return Pmis, Qmis, Sf, St


    def _power_mismatch_dc(self, buses, generators, B, Pbusinj, base_mva):
        """ Returns the power mismatch constraint (B*Va + Pg = Pd).
        """
        nb, ng = len(buses), len(generators)
        # Negative bus-generator incidence matrix.
        gen_bus = array([g.bus._i for g in generators])
        neg_Cg = csr_matrix((-ones(ng), (gen_bus, range(ng))), (nb, ng))

        Amis = hstack([B, neg_Cg], format="csr")

        Pd = array([bus.p_demand for bus in buses])
        Gs = array([bus.g_shunt for bus in buses])

        bmis = -(Pd - Gs) / base_mva - Pbusinj

        return LinearConstraint("Pmis", Amis, bmis, bmis, ["Va", "Pg"])


    def _branch_flow_dc(self, branches, Bf, Pfinj, base_mva):
        """ Returns the branch flow limit constraint.  The real power flows
        at the from end the lines are related to the bus voltage angles by
        Pf = Bf * Va + Pfinj.
        """
        # Indexes of constrained lines.
        il = array([i for i,l in enumerate(branches) if 0.0 < l.rate_a < 1e10])
        lpf = -Inf * ones(len(il))
        rate_a = array([l.rate_a / base_mva for l in branches])
        upf = rate_a[il] - Pfinj[il]
        upt = rate_a[il] + Pfinj[il]

        Pf = LinearConstraint("Pf",  Bf[il, :], lpf, upf, ["Va"])
        Pt = LinearConstraint("Pt", -Bf[il, :], lpf, upt, ["Va"])

        return Pf, Pt


    def _const_pf_constraints(self, gn, base_mva):
        """ Returns a linear constraint enforcing constant power factor for
        dispatchable loads.

        The power factor is derived from the original value of Pmin and either
        Qmin (for inductive loads) or Qmax (for capacitive loads). If both Qmin
        and Qmax are zero, this implies a unity power factor without the need
        for an additional constraint.
        """
        ivl = array([i for i, g in enumerate(gn)
                     if g.is_load and (g.q_min != 0.0 or g.q_max != 0.0)])
        vl = [gn[i] for i in ivl]
        nvl = len(vl)

        ng = len(gn)
        Pg = array([g.p for g in vl]) / base_mva
        Qg = array([g.q for g in vl]) / base_mva
        Pmin = array([g.p_min for g in vl]) / base_mva
        Qmin = array([g.q_min for g in vl]) / base_mva
        Qmax = array([g.q_max for g in vl]) / base_mva

        # At least one of the Q limits must be zero (corresponding to Pmax==0).
        for g in vl:
            if g.qmin != 0.0 and g.q_max != 0.0:
                logger.error("Either Qmin or Qmax must be equal to zero for "
                "each dispatchable load.")

        # Initial values of PG and QG must be consistent with specified power
        # factor. This is to prevent a user from unknowingly using a case file
        # which would have defined a different power factor constraint under a
        # previous version which used PG and QG to define the power factor.
        Qlim = (Qmin == 0.0) * Qmax + (Qmax == 0.0) * Qmin
        if any( abs(Qg - Pg * Qlim / Pmin) > 1e-6 ):
            logger.error("For a dispatchable load, PG and QG must be "
                         "consistent with the power factor defined by "
                         "PMIN and the Q limits.")

        # Make Avl, lvl, uvl, for lvl <= Avl * r_[Pg, Qg] <= uvl
        if nvl > 0:
            xx = Pmin
            yy = Qlim
            pftheta = arctan2(yy, xx)
            pc = sin(pftheta)
            qc = -cos(pftheta)
            ii = array([range(nvl), range(nvl)])
            jj = r_[ivl, ivl + ng]
            Avl = csr_matrix(r_[pc, qc], (ii, jj), (nvl, 2 * ng))
            lvl = zeros(nvl)
            uvl = lvl
        else:
            Avl = zeros((0, 2 * ng))
            lvl = array([])
            uvl = array([])

        return LinearConstraint("vl", Avl, lvl, uvl, ["Pg", "Qg"])


    def _voltage_angle_diff_limit(self, buses, branches):
        """ Returns the constraint on the branch voltage angle differences.
        """
        nb = len(buses)

        if not self.ignore_ang_lim:
            iang = [i for i, b in enumerate(branches)
                    if (b.ang_min and (b.ang_min > -360.0))
                    or (b.ang_max and (b.ang_max < 360.0))]
            iangl = array([i for i, b in enumerate(branches)
                     if b.ang_min is not None])[iang]
            iangh = array([i for i, b in enumerate(branches)
                           if b.ang_max is not None])[iang]
            nang = len(iang)

            if nang > 0:
                ii = range(nang) + range(nang)
                jjf = array([b.from_bus._i for b in branches])[iang]
                jjt = array([b.to_bus._i for b in branches])[iang]
                jj = r_[jjf, jjt]
                Aang = csr_matrix(r_[ones(nang), -ones(nang)], (ii, jj))
                uang = Inf * ones(nang)
                lang = -uang
                lang[iangl] = array([b.ang_min * (pi / 180.0)
                                    for b in branches])[iangl]
                uang[iangh] = array([b.ang_max * (pi / 180.0)
                                    for b in branches])[iangh]
            else:
#                Aang = csr_matrix((0, nb), dtype=float64)
#                lang = array([], dtype=float64)
#                uang = array([], dtype=float64)
                Aang = zeros((0, nb))
                lang = array([])
                uang = array([])
        else:
#            Aang = csr_matrix((0, nb), dtype=float64)
#            lang = array([], dtype=float64)
#            uang = array([], dtype=float64)
#            iang = array([], dtype=float64)
            Aang = zeros((0, nb))
            lang = array([])
            uang = array([])

        return LinearConstraint("ang", Aang, lang, uang, ["Va"])


    def _pwl_gen_costs(self, generators, base_mva):
        """ Returns the basin constraints for piece-wise linear gen cost
        variables.  CCV cost formulation expressed as Ay * x <= by.

        Based on makeAy.m from MATPOWER by C. E. Murillo-Sanchez, developed at
        PSERC Cornell. See U{http://www.pserc.cornell.edu/matpower/} for more
        information.
        """
        ng = len(generators)
        gpwl = [g for g in generators if g.pcost_model == PW_LINEAR]
#        nq = len([g for g in gpwl if g.qcost_model is not None])

        if self.dc:
            pgbas = 0        # starting index within x for active sources
            nq = 0           # number of Qg vars
#            qgbas = None     # index of 1st Qg column in Ay
            ybas = ng        # starting index within x for y variables
        else:
            pgbas = 0
            nq = ng
#            qgbas = ng + 1 # index of 1st Qg column in Ay
            ybas = ng + nq

        # Number of extra y variables.
        ny = len(gpwl)

        if ny == 0:
            return None, None

        # Total number of cost points.
        nc = len([co for gn in gpwl for co in gn.p_cost])
#        Ay = lil_matrix((nc - ny, ybas + ny))
        # Fill rows and then transpose.
        Ay = lil_matrix((ybas + ny, nc - ny))
        by = array([])

        j = 0
        k = 0
        for i, g in enumerate(gpwl):
            # Number of cost points: segments = ns-1
            ns = len(g.p_cost)

            p = array([x / base_mva for x, c in g.p_cost])
            c = array([c for x, c in g.p_cost])
            m = diff(c) / diff(p)        # Slopes for Pg (or Qg).

            if 0.0 in diff(p):
                raise ValueError, "Bad Pcost data: %s (%s)" % (p, g.name)
                logger.error("Bad Pcost data: %s" % p)

            b = m * p[:ns-1] - c[:ns-1] # rhs
            by = r_[by, b.T]

#            if i > ng:
#                sidx = qgbas + (i-ng) - 1       # this was for a q cost
#            else:
#                sidx = pgbas + i - 1            # this was for a p cost

            Ay[pgbas + i, k:k + ns - 1] = m

            # FIXME: Repeat for Q costs.

            # Now fill the y rows with -1's
            Ay[ybas + j, k:k + ns - 1] = -ones(ns-1)

            k += (ns - 1)
            j += 1

        y = Variable("y", ny)

        # Transpose Ay since lil_matrix stores in rows.
        if self.dc:
            ycon = LinearConstraint("ycon", Ay.T, None, by, ["Pg", "y"])
        else:
            ycon = LinearConstraint("ycon", Ay.T, None, by, ["Pg", "Qg","y"])

        return y, ycon

#------------------------------------------------------------------------------
#  "UDOPF" class:
#------------------------------------------------------------------------------

class UDOPF(OPF):
    """ The standard OPF formulation has no mechanism for completely shutting
    down generators which are very expensive to operate. Instead they are
    simply dispatched at their minimum generation limits. PYLON includes the
    capability to run an optimal power flow combined with a unit decommitment
    for a single time period, which allows it to shut down these expensive
    units and find a least cost commitment and dispatch.

    Solves a combined unit decommitment and optimal power flow for a
    single time period. Uses an algorithm similar to dynamic programming.
    It proceeds through a sequence of stages, where stage N has N generators
    shut down, starting with N=0. In each stage, it forms a list of candidates
    (gens at their Pmin limits) and computes the cost with each one of them
    shut down. It selects the least cost case as the starting point for the
    next stage, continuing until there are no more candidates to be shut down
    or no more improvement can be gained by shutting something down.

    Based on uopf.m from MATPOWER by Ray Zimmerman, developed at PSERC
    Cornell. See U{http://www.pserc.cornell.edu/matpower/} for more info.

    See also:
      - Ray Zimmerman, "MATPOWER User's Manual", MATPOWER, PSERC Cornell,
        version 3.2, U{http://www.pserc.cornell.edu/matpower/}, Sept, 2007
    """

    def solve(self, solver_klass=None):
        """ Solves the combined unit decommitment / optimal power flow problem.
        """
        case = self.case
        generators = case.online_generators

        logger.info("Solving OPF with unit de-commitment [%s]." % case.name)

        t0 = time()

        # 1. Begin at stage zero (N = 0), assuming all generators are on-line
        # with all limits in place. At most one generator shutdown per stage.
        i_stage = 0

        # Check for sum(p_min) > total load, decommit as necessary.
        online = [g for g in generators if not g.is_load]
        online_vload = [g for g in generators if g.is_load]

        # Total dispatchable load capacity.
        vload_capacity = sum([g.p_min for g in online_vload])
        # Total load capacity.
        load_capacity = sum([b.p_demand for b in case.buses]) - vload_capacity

        # Minimum total online generation capacity.
        p_min_tot = sum([g.p_min for g in online])

        # Shutdown the most expensive units until the minimum generation
        # capacity is less than the total load capacity.
        while p_min_tot > load_capacity:
            i_stage += 1
            logger.debug("De-commitment stage %d." % i_stage)

            # Find generator with the maximum average cost at Pmin.
            avg_pmin_cost = [g.total_cost(g.p_min) / g.p_min for g in online]
            # Select at random from maximal generators with equal cost.
            g_idx, _ = fair_max(avg_pmin_cost)
            generator = online[g_idx]

            logger.info("Shutting down generator [%s] to satisfy all "
                        "p_min limits." % generator.name)

            # Shut down most expensive unit.
            generator.online = False

            # Update minimum generation capacity for while loop.
            online = [g for g in case.online_generators if not g.is_load]
            p_min_tot = sum([g.p_min for g in online])

        # 2. Solve a normal OPF and save the solution as the current best.
        solution = super(UDOPF, self).solve(solver_klass)

        logger.debug("Initial system cost: $%.3f" % solution["f"])

        if not solution["converged"] == True:
            logger.error("Non-convergent UDOPF [%s]." %
                         solution["output"]["message"])
            return solution

        # 3. Go to the next stage, N = N + 1. Using the best solution from the
        # previous stage as the base case for this stage, ...

        # Best case so far. A list of the on-line status of all generators.
        overall_online = [g.online for g in case.generators]
        # The objective function value is the total system cost.
        overall_cost = solution["f"]

        # Best case for this stage.
        stage_online = overall_online
        stage_cost = overall_cost

        # Shutdown at most one generator per stage.
        while True:
            # 4. Form a candidate list of generators with minimum
            # generation limits binding.

            # Activate generators according to the stage best.
            for i, generator in enumerate(case.generators):
                generator.online = stage_online[i]

            # Get candidates for shutdown. Lagrangian multipliers are often
            # very small so we round to four decimal places.
            candidates = [g for g in case.online_generators if \
                          (round(g.mu_pmin, 4) > 0.0) and (g.p_min > 0.0)]

            if len(candidates) == 0:
                break

            # Assume no improvement during this stage.
            done = True

            i_stage += 1
            logger.debug("De-commitment stage %d." % i_stage)

            for candidate in candidates:
                # 5. For each generator on the candidate list, solve an OPF to
                # find the total system cost with the generator shut down.

                # Activate generators according to the stage best.
                for i, generator in enumerate(case.generators):
                    generator.online = stage_online[i]

                # Shutdown candidate generator.
                candidate.online = False

                logger.debug("Solving OPF with generator '%s' shutdown." %
                    candidate.name)

                # Run OPF.
                solution = super(UDOPF, self).solve(solver_klass)

                # Compare total system costs for improvement.
                if solution["converged"] == True \
                    and (solution["f"] < overall_cost):
                    logger.debug("System cost improvement: $%.3f ($%.3f)" %
                                 (stage_cost - solution["f"], solution["f"]))
                    # 6. Replace the current best solution with this one if
                    # it has a lower cost.
                    overall_online = [g.online for g in case.generators]
                    overall_cost = solution["f"]
                    best_candidate = candidate
                    # Check for further decommitment.
                    done = False
                else:
                    logger.debug("Candidate OPF failed [%s]." %
                                 solution["output"]["message"])

                # Reactivate the candidate before deactivating the next.
#                candidate.online = True

            if done:
                # Decommits at this stage did not help.
                break
            else:
                # 7. If any of the candidate solutions produced an improvement,
                # return to step 3.

                # Shutting something else down helps, so let's keep going.
                logger.info("Shutting down generator '%s'.",
                            best_candidate.name)

                stage_online = overall_online
                stage_cost = overall_cost

        # 8. Use the best overall solution as the final solution.
        for i, generator in enumerate(case.generators):
            generator.online = overall_online[i]

        # One final solve using the best case to ensure all results are
        # up-to-date.
        solution = super(UDOPF, self).solve(solver_klass)

        logger.debug("UDOPF system cost: $%.3f" % solution["f"])

        # Compute elapsed time and log it.
        elapsed = time() - t0

        plural = "" if i_stage == 1 else "s"
        logger.info("Unit decommitment OPF solved in %.3fs (%d decommitment "
                    "stage%s)." % (elapsed, i_stage, plural))

        return solution

#------------------------------------------------------------------------------
#  "OPFModel" class:
#------------------------------------------------------------------------------

class OPFModel(object):
    """ Defines a model for optimal power flow.

    Based on @opf_model in MATPOWER by Ray Zimmerman, developed at PSERC
    Cornell. See U{http://www.pserc.cornell.edu/matpower/} for more info.
    """

    def __init__(self, case):
        #: Case to which the model relates.
        self.case = case
        #: Optimisation variables.
        self.vars = []
        #: Linear constraints.
        self.lin_constraints = []
        #: Non-linear constraints.
        self.nln_constraints = []
        #: User defined costs.
        self.costs = []


    @property
    def var_N(self):
        return sum([v.N for v in self.vars])


    def add_var(self, var):
        """ Adds a variable to the model.
        """
        if var.name in [v.name for v in self.vars]:
            logger.error("Variable set named '%s' already exists." % var.name)
            return

        var.i1 = self.var_N
        var.iN = self.var_N + var.N - 1
        self.vars.append(var)


    def add_vars(self, vars):
        """ Adds a set of variables to the model.
        """
        for var in vars:
            self.add_var(var)


    def get_var(self, name):
        """ Returns the variable set with the given name.
        """
        for var in self.vars:
            if var.name == name:
                return var
        else:
            raise ValueError



    def get_var_N(self, name):
        """ Return the number of variables in the named set.
        """
        return self.get_var(name).N


    @property
    def nln_N(self):
        return sum([c.N for c in self.nln_constraints])


    @property
    def lin_N(self):
        return sum([c.N for c in self.lin_constraints])


    @property
    def lin_NS(self):
        return len(self.lin_constraints)


    def linear_constraints(self):
        """ Returns the linear constraints.
        """
        if self.lin_N == 0:
            return None, array([]), array([])

        A = lil_matrix((self.lin_N, self.var_N), dtype=float64)
        l = -Inf * ones(self.lin_N)
        u = -l

        for lin in self.lin_constraints:
            if lin.N:                   # non-zero number of rows to add
                Ak = lin.A              # A for kth linear constrain set
                i1 = lin.i1             # starting row index
                iN = lin.iN             # ending row index
                vsl = lin.vs            # var set list
                kN = -1                 # initialize last col of Ak used
                Ai = lil_matrix((lin.N, self.var_N), dtype=float64)
                for v in vsl:
                    var = self.get_var(v)
                    j1 = var.i1         # starting column in A
                    jN = var.iN         # ending column in A
                    k1 = kN + 1         # starting column in Ak
                    kN = kN + var.N     # ending column in Ak

                    if j1 == jN:
                        # FIXME: Single column slicing broken in lil.
                        for i in range(Ai.shape[0]):
                            Ai[i, j1] = Ak[i, k1]
                    else:
                        Ai[:, j1:jN + 1] = Ak[:, k1:kN + 1]

                A[i1:iN + 1, :] = Ai
                l[i1:iN + 1] = lin.l
                u[i1:iN + 1] = lin.u

        return A.tocsr(), l, u


    def add_constraint(self, con):
        """ Adds a constraint to the model.
        """
        if isinstance(con, LinearConstraint):
            N, M = con.A.shape
            if con.name in [c.name for c in self.lin_constraints]:
                logger.error("Constraint set named '%s' already exists."
                             % con.name)
                return False
            else:
                con.i1 = self.lin_N# + 1
                con.iN = self.lin_N + N - 1

                nv = 0
                for vs in con.vs:
                    nv = nv + self.get_var_N(vs)
                if M != nv:
                    logger.error("Number of columns of A does not match number"
                        " of variables, A is %d x %d, nv = %d", N, M, nv)
                self.lin_constraints.append(con)
        elif isinstance(con, NonLinearConstraint):
            N = con.N
            if con.name in [c.name for c in self.nln_constraints]:
                logger.error("Constraint set named '%s' already exists."
                             % con.name)
                return False
            else:
                con.i1 = self.nln_N# + 1
                con.iN = self.nln_N + N
                self.nln_constraints.append(con)
        else:
            raise ValueError

        return True


    def add_constraints(self, constraints):
        """ Adds constraints to the model.
        """
        for con in constraints:
            self.add_constraint(con)


    def get_lin_constraint(self, name):
        """ Returns the constraint set with the given name.
        """
        for c in self.lin_constraints:
            if c.name == name:
                return c
        else:
            raise ValueError


    def get_nln_constraint(self, name):
        """ Returns the constraint set with the given name.
        """
        for c in self.nln_constraints:
            if c.name == name:
                return c
        else:
            raise ValueError

    @property
    def cost_N(self):
        return sum([c.N for c in self.costs])


    def get_cost_params(self):
        """ Returns the cost parameters.
        """
        return [c.params for c in self.costs]

#------------------------------------------------------------------------------
#  "_Set" class:
#------------------------------------------------------------------------------

class _Set(_Named):

    def __init__(self, name, N):
        #: String identifier.
        self.name = name

        #: Starting index.
        self.i0 = 0

        #: Ending index.
        self.iN = 0

        #: Number in set.
        self.N = N

        #: Number of sets.
        self.NS = 0

        #: Ordered list of sets.
        self.order = []

#------------------------------------------------------------------------------
#  "Variable" class:
#------------------------------------------------------------------------------

class Variable(_Set):
    """ Defines a set of variables.
    """

    def __init__(self, name, N, v0=None, vl=None , vu=None):
        """ Initialises a new Variable instance.
        """
        super(Variable, self).__init__(name, N)

        #: Initial value of the variables. Zero by default.
        if v0 is None:
            self.v0 = zeros(N)
        else:
            self.v0 = v0

        #: Lower bound on the variables. Unbounded below be default.
        if vl is None:
            self.vl = -Inf * ones(N)
        else:
            self.vl = vl

        #: Upper bound on the variables. Unbounded above by default.
        if vu is None:
            self.vu = Inf * ones(N)
        else:
            self.vu = vu

#------------------------------------------------------------------------------
#  "LinearConstraint" class:
#------------------------------------------------------------------------------

class LinearConstraint(_Set):
    """ Defines a set of linear constraints.
    """

    def __init__(self, name, AorN, l=None, u=None, vs=None):
        N, _ = AorN.shape

        super(LinearConstraint, self).__init__(name, N)

        self.A = AorN
        self.l = -Inf * ones(N) if l is None else l
        self.u =  Inf * ones(N) if u is None else u

        # Varsets.
        self.vs = [] if vs is None else vs

        if (self.l.shape[0] != N) or (self.u.shape[0] != N):
            logger.error("Sizes of A, l and u must match.")

#------------------------------------------------------------------------------
#  "NonLinearConstraint" class:
#------------------------------------------------------------------------------

class NonLinearConstraint(_Set):
    """ Defines a set of non-linear constraints.
    """
    pass

#------------------------------------------------------------------------------
#  "Cost" class:
#------------------------------------------------------------------------------

class Cost(_Set):
    def __init__(self):
        self.N = None
        self.H = None
        self.Cw = None
        self.dd = None
        self.rh = None
        self.kk = None
        self.mm = None
        self.vs = None
        self.params = None

# EOF -------------------------------------------------------------------------
