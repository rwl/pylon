# Copyright (C) 1996-2010 Power System Engineering Research Center (PSERC)
# Copyright (C) 2007-2010 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Analytic centering with cone constraint example from CVXOPT.

    minimize     -log(1 - x_1^2) - log(1 - x_2^2) - log(1 - x_3^2)

    subject to    ||x||_2 <= 1

    http://abel.ee.ucla.edu/cvxopt/userguide/solvers.html
"""

import numpy as np
from scipy.sparse import csr_matrix

from pdipm import pdipm

x0 = np.zeros(3)

G = np.array([[0,-1, 0, 0,-21,-11,  0,-11, 10,  8,  0,  8, 5],
              [0, 0,-1, 0,  0, 10, 16, 10,-10,-10, 16,-10, 3],
              [0, 0, 0,-1, -5,  2,-17,  2, -6,  8,-17, -7, 6]], "d")

h = np.array([1, 0, 0, 0, 20, 10, 40, 10, 80, 10, 40, 10, 15], "d")

k = -np.Inf * np.ones(h.shape[0])

def f(x):
    if max(abs(x)) >= 1.0:
        return None
    u = 1 - x**2
    val = -sum(np.log(u))
    df = (2*x / u).T
    return val, df, None

def gh(x):
    g = np.array([])
    h = np.array([])
    dg = None
    dh = None
    return g, h, dg, dh

def hess(x, lmbda):
    u = 1 - x**2
    H = csr_matrix((2 * lmbda[0] * 1 + u**2 / u**2, ()))
    return H

sol = pdipm(f, gh, hess, x0, A=G, l=k, u=h)
print sol["x"]
