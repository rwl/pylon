#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" Optimal power flow routine, translated from MATPOWER.

    References:
        Ray Zimmerman, "runopf.m", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 3.2, June 2007

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
import numpy

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul, exp, div
from cvxopt import solvers

from pylon.routine.util import conj

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "dS_dV" function:
#------------------------------------------------------------------------------

def dSbus_dV(Y, v):
    """
    Computes the partial derivative of power injection w.r.t. voltage.

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, "dSbus_dV.m",
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    j = 0+1j
    n = len(v)
    i = Y * v

    diag_v = spdiag(v)
    diag_i = spdiag(i)
    diag_vnorm = spdiag(div(v, abs(v))) # Element-wise division.

    ds_dvm = diag_v * conj(Y * diag_vnorm) + conj(diag_i) * diag_vnorm
    ds_dva = j * diag_v * conj(diag_i - Y * diag_v)

    return ds_dvm, ds_dva

#------------------------------------------------------------------------------
#  "dSbr_dV" function:
#------------------------------------------------------------------------------

def dSbr_dV(branches, Y_source, Y_target, v):
    """ Computes the branch power flow vector and the partial derivative of
    branch power flow w.r.t voltage.

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, "dSbr_dV.m",
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    j = 0+1j
    n_branches = len(branches)
    n_buses = len(v)

    source_idxs = matrix([e.source_bus_idx for e in branches])
    target_idxs = matrix([e.target_bus_idx for e in branches])

    # Compute currents.
    i_source = Y_source * v
    i_target = Y_target * v

    # dV/dVm = diag(V./abs(V))
    v_norm = div(v, abs(v))

    diagVsource = spdiag(v[source_idxs])
    diagIsource = spdiag(i_source)
    diagVtarget = spdiag(v[target_idxs])
    diagItarget = spdiag(i_target)
    diagV = spdiag(v)
    diagVnorm = spdiag(v_norm)

    # Partial derivative of S w.r.t voltage phase angle.
    dSf_dVa = j * (conj(diagIsource) * spmatrix(v[source_idx],
                                                range(n_branches),
                                                source_idxs,
                                                (n_branches, n_buses)) - \
        diagVsource * conj(Y_source * diagV))

    dSt_dVa = j * (conj(diagItarget) * spmatrix(v[target_idx],
                                                range(n_branches),
                                                target_idxs,
                                                (n_branches, n_buses)) - \
        diagVtarget * conj(Y_target * diagV))

    # Partial derivative of S w.r.t. voltage amplitude.
    dSf_dVm = diagVsource * conj(Y_source * diagVnorm) + conj(diagIsource) * \
        spmatrix(v_norm[source_idxs], range(n_branches),
            source_idxs, (n_branches, n_buses))

    dSt_dVm = diagVtarget * conj(Y_target * diagVnorm) + conj(diagItarget) * \
        spmatrix(v_norm[target_idxs], range(n_branches),
            target_idxs, (n_branches, n_buses))

    # Compute power flow vectors.
    s_source = mul(v[source_idxs], conj(i_source))
    s_target = mul(v[target_idxs], conj(i_target))

    return dSf_dVa, dSt_dVa, dSf_dVm, dSt_dVm, s_source, s_target

#------------------------------------------------------------------------------
#  "dAbr_dV" function:
#------------------------------------------------------------------------------

def dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, s_source, s_target):
    """ Computes the partial derivatives of apparent power flow w.r.t voltage.

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, "dAbr_dV.m",
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    n_branches = len(s_source)

    # Compute apparent powers.
    a_source = abs(s_source)
    a_target = abs(s_target)

    # Compute partial derivative of apparent power w.r.t active and
    # reactive power flows.  Partial derivative must equal 1 for lines with
    # zero flow to avoid division by zero errors (1 comes from L'Hopital).
    def zero2one(x):
        if x != 0: return x
        else: return 1.0

    p_source = div(s_source.real(), map(zero2one, a_source))
    q_source = div(s_target.imag(), map(zero2one, a_source))
    p_target = div(s_target.real(), map(zero2one, a_target))
    q_target = div(s_target.imag(), map(zero2one, a_target))

    dAf_dPf = spdiag(p_source)
    dAf_dQf = spdiag(q_source)
    dAt_dPt = spdiag(p_target)
    dAt_dQt = spdiag(q_target)

    # Partial derivative of apparent power magnitude w.r.t voltage phase angle.
    dAf_dVa = dAf_dPf * dSf_dVa.real() + dAf_dQf * dSf_dVa.imag()
    dAt_dVa = dAt_dPt * dSt_dVa.real() + dAt_dQt * dSt_dVa.imag()
    # Partial derivative of apparent power magnitude w.r.t. voltage amplitude.
    dAf_dVm = dAf_dPf * dSf_dVm.real() + dAf_dQf * dSf_dVm.imag()
    dAt_dVm = dAf_dPt * dSt_dVm.real() + dAt_dQt * dSt_dVm.imag()

    return dAf_dVa, dAt_dVa, dAf_dVm, dAt_dVm

#------------------------------------------------------------------------------
#  "OptimalPowerFlow" class:
#------------------------------------------------------------------------------

class ACOPFRoutine:
    """ Optimal power flow routine, translated from MATPOWER.

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, MATPOWER,
        version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    # Network instance to be optimised.
    network = None

    #--------------------------------------------------------------------------
    #  Algorithm parameters:
    #--------------------------------------------------------------------------

    # Turns the output to the screen on or off.
    show_progress = True

    # Maximum number of iterations.
    max_iterations = 100

    # Absolute accuracy.
    absolute_tol = 1e-7

    # Relative accuracy.
    relative_tol = 1e-6

    # Tolerance for feasibility conditions.
    feasibility_tol = 1e-7

    # Number of iterative refinement steps when solving KKT equations.
    refinement = 1

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network, show_progress=True, max_iterations=100,
            absolute_tol=1e-7, relative_tol=1e-6, feasibility_tol=1e-7,
            refinement=1):
        """ Initialises a new ACOPFRoutine instance. """

        self.network = network
        self.show_progress = show_progress
        self.max_iterations = max_iterations
        self.absolute_tol = absolute_tol
        self.relative_tol = relative_tol
        self.feasibility_tol = feasibility_tol
        self.refinement = refinement

    #--------------------------------------------------------------------------
    #  Solve AC Optimal Power Flow problem:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves AC OPF. """

        # Turn off output to screen.
        solvers.options["show_progress"] = self.show_progress
        solvers.options["maxiters"] = self.max_iterations
        solvers.options["abstol"] = self.absolute_tol
        solvers.options["reltol"] = self.relative_tol
        solvers.options["feastol"] = self.feasibility_tol
        solvers.options["refinement"] = self.refinement

        network = self.network
        logger.debug("Solving AC OPF [%s]" % network.name)

        buses = network.connected_buses
        branches = network.online_branches
        generators = network.online_generators
        n_buses = len(network.connected_buses)
        n_branches = len(network.online_branches)
        n_generators = len(network.online_generators)

        # The number of non-linear equality constraints.
        n_equality = 2 * n_buses
        # The number of control variables.
        n_control = 2 * n_buses + 2 * n_generators

        # Definition of indexes for the optimisation variable vector.
        ph_base = 0 # Voltage phase angle.
        ph_end  = ph_base + n_buses-1;
        v_base  = ph_end + 1 # Voltage amplitude.
        v_end   = v_base + n_buses-1
        pg_base = v_end + 1
        pg_end  = pg_base + n_generators-1
        qg_base = pg_end + 1
        qg_end  = qg_base + n_generators-1

        # TODO: Definition of indexes for the constraint vector.

        def F(x=None, z=None):
            """ Evaluates the objective and nonlinear constraint functions. """

            if x is None:
                # Compute initial vector.
                x_ph = matrix([bus.v_phase_guess for bus in buses])
                # TODO: Initialise V from any present generators.
                x_v = matrix([bus.v_amplitude_guess for bus in buses])
                x_pg = matrix([g.p for g in generators])
                x_qg = matrix([g.q for g in generators])

                return n_equality, matrix([x_ph, x_v, x_pg, x_qg])

            # Evaluate objective function -------------------------------------

            p_gen = x[pg_base:pg_end+1] # Active generation in p.u.
            q_gen = x[qg_base:qg_end+1] # Reactive generation in p.u.

            # Setting P and Q for each generator triggers re-evaluation of the
            # generator cost (See _get_p_cost()).
            for i, g in enumerate(generators):
                g.p = p_gen[i]# * network.base_mva
                g.q = q_gen[i]# * network.base_mva

            costs = matrix([g.p_cost for g in generators])
            f0 = sum(costs)
            # TODO: Generalised cost term.

            # Evaluate cost gradient ------------------------------------------

            # Partial derivative w.r.t. polynomial cost Pg and Qg.
            df0 = spmatrix([], [], [], (n_generators*2, 1))
            for i, g in enumerate(generators):
                der = numpy.polyder(list(g.cost_coeffs))
                df0[i] = numpy.polyval(der, g.p) * network.base_mva

            # Evaluate nonlinear constraints ----------------------------------

            # Net injected power in p.u.
            s = matrix([complex(b.p_surplus, b.q_surplus) for b in buses])

            # Bus voltage vector.
            v_phase = x[ph_base:ph_end+1]
            v_amplitude = x[v_base:v_end]
#            Va0r = Va0 * pi / 180 #convert to radians
            v = mul(v_amplitude, exp(j * v_phase)) #element-wise product

            # Evaluate the power flow equations.
            Y = make_admittance_matrix(network)
            mismatch = mul(v, conj(Y * v)) - s

            # Evaluate power balance equality constraint function values.
            fk_eq = matrix([mismatch.real(), mismatch.imag()])

            # Branch power flow inequality constraint function values.
            source_idxs = matrix([e.source_bus_idx for e in branches])
            target_idxs = matrix([e.target_bus_idx for e in branches])
            # Complex power in p.u. injected at the source bus.
            s_source = mul(v[source_idxs], conj(Y_source, v))
            # Complex power in p.u. injected at the target bus.
            s_target = mul(v[target_idxs], conj(Y_target, v))

            s_max = matrix([e.s_max for e in branches])

            fk_ieq = matrix([abs(s_source)-s_max, abs(s_target)-s_max])

            # Evaluate partial derivatives of constraints ---------------------
            # Partial derivative of injected bus power
            ds_dvm, ds_dva = dSbus_dV(Y, v) # w.r.t voltage
            pv_idxs = matrix([buses.index(bus) for bus in buses])
            ds_dpg = spmatrix(-1, pv_idxs, range(n_generators)) # w.r.t Pg
            ds_dqg = spmatrix(-j, pv_idxs, range(n_generators)) # w.r.t Qg

            # Transposed Jacobian of the power balance equality constraints.
            dfk_eq = sparse([
                sparse([
                    ds_dva.real(), ds_dvm.real(), ds_dpg.real(), ds_dqg.real()
                ]),
                sparse([
                    ds_dva.imag(), ds_dvm.imag(), ds_dpg.imag(), ds_dqg.imag()
                ])
            ]).T

            # Partial derivative of branch power flow w.r.t voltage.
            dSf_dVa, dSt_dVa, dSf_dVm, dSt_dVm, s_source, s_target = \
                dSbr_dV(branches, Y_source, Y_target, v)

            # Magnitude of complex power flow.
            df_dVa, dt_dVa, df_dVm, dt_dVm = \
                dAbr_dV(dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, s_source, s_target)

            # Transposed Jacobian of branch power flow inequality constraints.
            dfk_ieq = matrix([
                matrix([df_dVa, df_dVm]),
                matrix([dt_dVa, dt_dVm])
            ]).T

            f = matrix([f0, fk_eq, fk_ieq])
            df = matrix([df0, dfk_eq, dfk_ieq])

            if z is None:
                return f, df

            # Evaluate cost Hessian -------------------------------------------

            d2f_d2pg = spmatrix([], [], [], (n_generators, 1))
            d2f_d2qg = spmatrix([], [], [], (n_generators, 1))
            for i, g in enumerate(generators):
                der = numpy.polyder(list(g.cost_coeffs))
                d2f_d2pg[i] = numpy.polyval(der, g.p) * network.base_mva
                # TODO: Implement reactive power costs.

            i = matrix(range(pg_base, qg_end+1)).T
            H = spmatrix(matrix([d2f_d2pg, d2f_d2qg]), i, i)

            return f, df, H


        # cp(F, G=None, h=None, dims=None, A=None, b=None, kktsolver=None)
        #
        #     minimize    f0(x)
        #     subject to  fk(x) <= 0, k = 1, ..., mnl
        #                 G*x   <= h
        #                 A*x   =  b.
        solution = solvers.cp(F)


    def _build_additional_linear_constraints(self):
        """ A, l, u represent additional linear constraints on the
        optimization variables. """

        if Au is None:
            Au = sparse([], [], [], (0, 0))
            l_bu = matrix([0])
            u_bu = matrix([0])

        # Piecewise linear convex costs
        A_y = spmatrix([], [], [], (0, 0))
        b_y = matrix([0])

        # Branch angle difference limits
        A_ang = spmatrix([], [], [], (0, 0))
        l_ang = matrix([0])
        u_ang = matrix([0])

        # Despatchable loads
        A_vl = spmatrix([], [], [], (0, 0))
        l_vl = matrix([0])
        u_vl = matrix([0])

        # PQ capability curves
        A_pqh = spmatrix([], [], [], (0, 0))
        l_bpqh = matrix([0])
        u_bpqh = matrix([0])

        A_pql = spmatrix([], [], [], (0, 0))
        l_bpql = matrix([0])
        u_bpql = matrix([0])

        # Build linear restriction matrix. Note the ordering.
        # A, l, u represent additional linear constraints on
        # the optimisation variables
        A = sparse([Au, A_pqh, A_pql, A_vl, A_ang])
        l = matrix([l_bu, l_bpqh, l_bpql, l_vl, l_ang])
        u = matrix([u_bu, u_bpqh, u_bpql, u_vl, l_ang])

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from os.path import join, dirname
    from pylon.readwrite.api import read_matpower

    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    data_file = join(dirname(__file__), "../test/data/case6ww.m")
    n = read_matpower(data_file)

    ac_opf = ACOPFRoutine(network=n)
    ac_opf.solve()

# EOF -------------------------------------------------------------------------
