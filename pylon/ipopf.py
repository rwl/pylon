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

""" Defines an IPOPT OPF solver.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# http://code.google.com/p/pyipopt/
import pyipopt

from numpy import Inf, ones, r_, zeros

from scipy.sparse import vstack, tril

from pylon.solver import PIPSSolver

#------------------------------------------------------------------------------
#  "IPOPFSolver" class:
#------------------------------------------------------------------------------

class IPOPFSolver(PIPSSolver):
    """ Solves AC optimal power flow using IPOPT.
    """

    def _g(self, x, user_data=None):
        A = user_data["A"]
        h, g = self._g()
        if A is None:
            b = r_[g, h]
        else:
            b = r_[g, h, A * x]
        return b


    def _dg(self, x, flag, user_data=None):
        A = user_data["A"]
        dh, dg = self._dgh(x)
        if A is None:
            J = vstack([dg.T, dh.T], "coo")
        else:
            J = vstack([dg.T, dh.T, A], "coo")

        if flag:
            return (J.row, J.col)
        else:
            return J.data


    def _h(self, x, lagrange, obj_factor, flag, user_data=None):
        neqnln = user_data["neqnln"]
        niqnln = user_data["niqnln"]
        lmbda = {"eqnonlin": lagrange[:neqnln],
                 "ineqnonlin": lagrange[neqnln:neqnln + niqnln]}
        H = tril(self._hessfcn(x, lmbda), format="coo")
        if flag:
            return (H.row, H.col)
        else:
            return H.data



    def _solve(self, x0, A, l, u, xmin, xmax):
        """ Solves using the Interior Point OPTimizer.
        """
        # Indexes of constrained lines.
        il = [i for i,l in enumerate(self._ln) if 0.0 < l.rate_a < 1e10]
        nl2 = len(il)

        neqnln = 2 * self._nb # no. of non-linear equality constraints
        niqnln = 2 * len(il)  # no. of lines with constraints

        user_data = {"A": A, "neqnln": neqnln, "niqnln": niqnln}

        n = len(x0) # the number of variables
        gl = r_[zeros(2 * self._nb), -Inf * ones(2 * nl2), l]
        gu = r_[zeros(2 * self._nb),       zeros(2 * nl2), u]
        m = len(gl) # the number of constraints
        nnzj = 0 # the number of nonzeros in Jacobian matrix
        nnzh = 0 # the number of non-zeros in Hessian matrix

        nlp = pyipopt.create(n, xmin, xmax, m, gl, gu, nnzj, nnzh,
                             self._f, self._df, self._g, self._dg, self._h)

#        x, zl, zu, obj = nlp.solve(x0)
        success = nlp.solve(x0, user_data)
        nlp.close()

        print "Success:", success
        print "Solution of the primal variables, x"
#        print x
        print "Solution of the bound multipliers, z_L and z_U"
#        print zl, zu
        print "Objective value"
#        print "f(x*) =", obj

# EOF -------------------------------------------------------------------------
