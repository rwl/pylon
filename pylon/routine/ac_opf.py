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
    D. Zimmerman, Carlos E. Murillo-Sanchez and D. Gan, MATPOWER, version 3.2,
    http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul, exp
from cvxopt.solvers import cp

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

def costfmin(x=None, z=None):
    """ Evaluates the objective and nonlinear constraint functions.

    F() returns a tuple (m, x0), where m is the number of nonlinear
    constraints and x0 is a point in the domain of f.

    F(x), with x a dense real matrix of size (n,1), returns a tuple (f, Df).
    f is a dense real matrix of size (m+1,1).  Df is a dense or sparse real
    matrix of size (m+1, n).

    F(x,z), with x a dense real matrix of size (n,1) and z a positive dense
    real matrix of size (m+1,1) returns a tuple (f, Df, H).  H is a square
    dense or sparse real matrix of size (n, n).

    """

    if x is None:
        return 0, matrix(0.0, (n, 1))

    if z is None:
        return val, Df

    return val, Df, H

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
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network):
        """ Initialises a new ACOPFRoutine instance. """

        self.network = network

    #--------------------------------------------------------------------------
    #  Solve AC Optimal Power Flow problem:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves AC OPF. """

        logger.debug("Solving AC OPF [%s]" % self.network.name)

        n_buses = len(buses)
        n_branches = len(branches)
        n_generators = len(generators)

        # The number of non-linear equality constraints.
        n_equality = 2*n_buses
        # The number of control variables.
        n_control = 2*n_buses + 2*n_generators

        def F(x=None, z=None):
            """ Evaluates the objective and nonlinear constraint functions. """

            if x is None:
                return n_equality, matrix(0.0, (n_control, 1))


        # cp(F, G=None, h=None, dims=None, A=None, b=None, kktsolver=None)
        #
        #     minimize    f0(x)
        #     subject to  fk(x) <= 0, k = 1, ..., mnl
        #                 G*x   <= h
        #                 A*x   =  b.
        solution = cp(F)


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
