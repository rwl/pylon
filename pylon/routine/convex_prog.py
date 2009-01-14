#------------------------------------------------------------------------------
# Copyright (C) 2000 Richard W. Lincoln
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

"""
Primal-dual interior point solver for convex programs with convex inequality
constraints.

References:
    P. Carbonetto, "MATLAB implementation of a primal-dual interior-point
    solver for convex programs with constraints", Dept. of Computer Science,
    Univeristy of British Columbia, www.cs.ubc.ca/~pcarbo/convexprog.html,
    May 21, 2008

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from cvxopt.base import matrix, spmatrix, sparse, spdiag, mul, exp

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

options = {}

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "cpnl" function:
#------------------------------------------------------------------------------

def cpnl(x, F, constraints):
    """
    Solves a convex optimisation problem

        minimise    f0(x)
        subject to  fk(x) < 0, k = 1, ..., mnl

    where f = (f0, f1, ..., fmnl) is convex and twice differentiable and the
    inequalities are conex in x.

    """

    try:
        MAXITERS = options["maxiters"]
    except KeyError:
        MAXITERS = 100
    else:
        if type(MAXITERS) is not int or MAXITERS < 1:
            raise ValueError, "options['maxiters'] must be a positive integer"

    # Some algorithm parameters.
    EPS = options["eps"] = 1e-8
    SIGMAMAX = options["sigmamax"] = 0.5 # The maximum centering parameter.
    ETAMAX = options["etamax"] = 0.25 # The maximum forcing number.
    MUMIN = options["mumin"] = 1e-9 # Minimum barrier parameter.
    ALPHAMAX = options["alphamax"] = 0.995 # Maximum step size.
    ALPHAMIN = options["alphamin"] = 1e-6 # Minimum step size.
    BETA = options["beta"] = 0.75 # Granularity of backtracking search.
    TAU = options["tau"] = 0.01 # Acceptable decrease in line search.

    # Turns output to screen on or off.
    show_progress = options["show_progress"] = True

    #--------------------------------------------------------------------------
    #  Initialisation:
    #--------------------------------------------------------------------------

    c  = constraints(x)
    n  = len(x) # Number of primal variables
    m  = len(c) # Number of constraints
    nv = n + m # Total number of primal-dual optimisation variables
    z  = matrix(1, (m,1), tc="i") # Lagrange multipliers
    B  = spmatrix(1, range(n), range(n)) # Second-order information

    if show_progress:
        print "  i f(x)       lg(mu) sigma   ||rx||  ||rc||  alpha   #ls\n"

    #--------------------------------------------------------------------------
    #  Iterate:
    #--------------------------------------------------------------------------

    # Repeat while the convergence criterion has not been satisfied, and we
    # haven't reached the maximum number of iterations.

    iter = 0
    while iter < MAXITERS:
        pass

# EOF -------------------------------------------------------------------------
