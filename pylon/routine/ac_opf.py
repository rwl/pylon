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

""" Optimal power flow routine, translated from MATPOWER

References:
    D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
    MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

import math

from numpy import pi, zeros, ones, Inf, hstack, vstack, arange, conjugate

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul, exp
from cvxopt.umfpack import linsolve

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "OptimalPowerFlow" class:
#------------------------------------------------------------------------------

class ACOPFRoutine:
    """ Optimal power flow routine, translated from MATPOWER

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    #--------------------------------------------------------------------------
    #  Solve AC Optimal Power Flow problem:
    #--------------------------------------------------------------------------

    def solve(self, base_mva, buses, branches, generators,
              Au=None, l_bu=None, u_bu=None):
        """ Solves AC OPF """

        n_buses = len(buses)
        n_branches = len(branches)
        n_generators = len(generators)

        # The number of non-linear equality constraints
        n_equality = 2*n_buses
        # The number of control variables
        n_control = 2*n_buses + 2*n_generators

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

# EOF -------------------------------------------------------------------------
