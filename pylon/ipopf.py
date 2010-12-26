#------------------------------------------------------------------------------
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

""" Defines an IPOPT OPF solver.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pyipopt # http://github.com/rwl/pyipopt

from numpy import Inf, ones, r_, zeros

from scipy.sparse import vstack, tril

from pylon.solver import PIPSSolver

#------------------------------------------------------------------------------
#  "IPOPFSolver" class:
#------------------------------------------------------------------------------

class IPOPFSolver(PIPSSolver):
    """ Solves AC optimal power flow using IPOPT.
    """

    #--------------------------------------------------------------------------
    #  PIPSSolver interface:
    #--------------------------------------------------------------------------

    def _solve(self, x0, A, l, u, xmin, xmax):
        """ Solves using the Interior Point OPTimizer.
        """
        # Indexes of constrained lines.
        il = [i for i,ln in enumerate(self._ln) if 0.0 < ln.rate_a < 1e10]
        nl2 = len(il)

        neqnln = 2 * self._nb # no. of non-linear equality constraints
        niqnln = 2 * len(il)  # no. of lines with constraints

        user_data = {"A": A, "neqnln": neqnln, "niqnln": niqnln}

        self._f(x0)
        Jdata = self._dg(x0, False, user_data)
#        Hdata = self._h(x0, ones(neqnln + niqnln), None, False, user_data)

        lmbda = {"eqnonlin": ones(neqnln),
                 "ineqnonlin": ones(niqnln)}
        H = tril(self._hessfcn(x0, lmbda), format="coo")
        self._Hrow, self._Hcol = H.row, H.col

        n = len(x0) # the number of variables
        xl = xmin
        xu = xmax
        gl = r_[zeros(2 * self._nb), -Inf * ones(2 * nl2), l]
        gu = r_[zeros(2 * self._nb),       zeros(2 * nl2), u]
        m = len(gl) # the number of constraints
        nnzj = len(Jdata) # the number of nonzeros in Jacobian matrix
        nnzh = 0#len(H.data) # the number of non-zeros in Hessian matrix

        f_fcn, df_fcn, g_fcn, dg_fcn, h_fcn = \
            self._f, self._df, self._g, self._dg, self._h

        nlp = pyipopt.create(n, xl, xu, m, gl, gu, nnzj, nnzh,
                             f_fcn, df_fcn, g_fcn, dg_fcn)#, h_fcn)

#        print dir(nlp)
#        nlp.str_option("print_options_documentation", "yes")
#        nlp.int_option("max_iter", 10)

#        x, zl, zu, obj = nlp.solve(x0)
        success = nlp.solve(x0, user_data)
        nlp.close()

    #--------------------------------------------------------------------------
    #  IPOPFSolver interface:
    #--------------------------------------------------------------------------

    def _g(self, x, user_data):
        A = user_data["A"]
        h, g = self._gh(x)
        if A is None:
            b = r_[g, h]
        else:
            b = r_[g, h, A * x]
        return b


    def _dg(self, x, flag, user_data):
        A = user_data["A"]
        dh, dg = self._dgh(x)
        if A is None:
            J = vstack([dg.T, dh.T], "coo")
        else:
            J = vstack([dg.T, dh.T, A], "coo")
        if flag:
#            return (J.row, J.col)
            return (J.col, J.row)
        else:
            return J.data


    def _h(self, x, lagrange, obj_factor, flag, user_data=None):
        if flag:
#            return (self._Hrow, self._Hcol)
            return (self._Hcol, self._Hrow)
        else:
            neqnln = user_data["neqnln"]
            niqnln = user_data["niqnln"]
            lmbda = {"eqnonlin": lagrange[:neqnln],
                     "ineqnonlin": lagrange[neqnln:neqnln + niqnln]}
            H = tril(self._hessfcn(x, lmbda), format="coo")
            return H.data

# EOF -------------------------------------------------------------------------
