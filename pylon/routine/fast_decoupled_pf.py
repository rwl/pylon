#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Defines a routine for solving the power flow problem using fast decoupled
method.

References:
    D. Zimmerman, C. E. Murillo-Sanchez and D. Gan, "fdpf.m", MATPOWER,
    version 3.2, http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import cmath
import logging, sys
from cvxopt.base import matrix, spmatrix, sparse, spdiag, gemv, exp, mul, div

from pylon.routine.ac_pf import ACPFRoutine
from pylon.routine.y import AdmittanceMatrix
from pylon.routine.util import conj

from pylon.api import Network

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#  "FastDecoupledPFRoutine" class:
#------------------------------------------------------------------------------

class FastDecoupledPFRoutine(ACPFRoutine):
    """ Solves the power flow using fast decoupled method. """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # FDPF matrix B prime.
    Bp = spmatrix

    # FDPF matrix B double prime.
    Bpp = spmatrix

    # Use XB or BX method?
    method = "XB"

    p = matrix

    q = matrix

    #--------------------------------------------------------------------------
    #  Solve power flow using Fast Decoupled method:
    #--------------------------------------------------------------------------

    def solve(self):
        """
        Solves the AC power flow for the referenced network using fast
        decoupled method.  Returns the final complex voltages, a flag which
        indicates whether it converged or not, and the number of iterations
        performed.

        """

        self._make_B_prime()
        self._make_B_double_prime()

        self._make_admittance_matrix()
        self._initialise_voltage_vector()
        self._make_power_injection_vector()
        self._index_buses()

        # Initial mismatch evaluation and convergency check.
        self.converged = False
        self._evaluate_mismatch()
        self._check_convergence()

#        iter = 0
#        while (not self.converged) and (iter < self.iter_max):
#            self.iterate()
#            self._evaluate_mismatch()
#            self._check_convergence()
#            iter += 1

        if self.converged:
            logger.info("Routine converged in %d iterations." % iter)
        else:
            logger.info("Routine failed to converge in %d iterations." % iter)

    #--------------------------------------------------------------------------
    #  P and Q iterations:
    #--------------------------------------------------------------------------

    def iterate(self):
        """ Performs P and Q iterations. """

        pass

    #--------------------------------------------------------------------------
    #  Evaluate mismatch:
    #--------------------------------------------------------------------------

    def _evaluate_mismatch(self):
        """ Evaluates the mismatch between .

  -4.0843 - 4.1177i
   1.0738 - 0.2847i
   0.2524 - 0.9024i
   4.6380 - 0.6955i
  -0.1939 + 0.6726i
  -0.2126 + 0.9608i

   4.0063 -11.7479i  -2.6642 + 3.5919i        0            -4.6636 + 1.3341i  -0.8299 + 3.1120i
  -1.2750 + 4.2865i   9.3283 -23.1955i  -0.7692 + 3.8462i  -4.0000 + 8.0000i  -1.0000 + 3.0000i
        0            -0.7692 + 3.8462i   4.1557 -16.5673i        0            -1.4634 + 3.1707i
   3.4872 + 3.3718i  -4.0000 + 8.0000i        0             6.1765 -14.6359i  -1.0000 + 2.0000i
  -0.8299 + 3.1120i  -1.0000 + 3.0000i  -1.4634 + 3.1707i  -1.0000 + 2.0000i   5.2933 -14.1378i
        0            -1.5590 + 4.4543i  -1.9231 + 9.6154i        0            -1.0000 + 3.0000i



        """

        j = 0+1j

        # MATPOWER:
        #   mis = (V .* conj(Ybus * V) - Sbus) ./ Vm;
        v = self.v
        Y = self.Y

#        print "V:", v
#        print "Y:", Y

        mismatch = div(mul(v, conj(self.Y * v) - self.s_surplus), abs(v))
#        mismatch = Y * v

#        print "MIS:", mismatch

        self.p = p = mismatch[self.pvpq_idxs].real()
        self.q = q = mismatch[self.pq_idxs].imag()

        return p, q# + j*q

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self):
        """ Checks if the solution has converged to within the specified
        tolerance.

        """

        P = self.p
        Q = self.q
        tol = self.tolerance

        normP = max(abs(P))
        normQ = max(abs(Q))

        if (normP < tolerance) and (normQ < tolerance):
            self.converged = converged = True
        else:
            self.converged = converged = False
#            logger.info("Difference: %.3f" % normF-self.tolerance)

        return converged

    #--------------------------------------------------------------------------
    #  Make FDPF matrix B prime:
    #--------------------------------------------------------------------------

    def _make_B_prime(self):
        """ Builds the Fast Decoupled Power Flow matrix B prime.

        References:
        D. Zimmerman, C. E. Murillo-Sanchez and D. Gan, "makeB.m", MATPOWER,
        version 1.5, http://www.pserc.cornell.edu/matpower/, July 8, 2005

        """

        if self.method is "XB":
            r_line = False
        else:
            r_line = True

        am = AdmittanceMatrix(
            self.network, bus_shunts=False, line_shunts=False, taps=False,
            line_resistance=r_line
        )

        self.Bp = Bp = -am.Y.imag()

        return Bp

    #--------------------------------------------------------------------------
    #  Make FDPF matrix B double prime:
    #--------------------------------------------------------------------------

    def _make_B_double_prime(self):
        """ Builds the Fast Decoupled Power Flow matrix B double prime.

        References:
        D. Zimmerman, C. E. Murillo-Sanchez and D. Gan, "makeB.m", MATPOWER,
        version 1.5, http://www.pserc.cornell.edu/matpower/, July 8, 2005

        """

        if self.method is "BX":
            r_line = False
        else:
            r_line = True

        am = AdmittanceMatrix(
            self.network, line_resistance=r_line, phase_shift=False
        )

        self.Bpp = Bpp = -am.Y.imag()

        return Bpp

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    from os.path import join, dirname
    from pylon.readwrite.api import read_matpower

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    data_file = join(dirname(__file__), "../test/data/case6ww.m")
    n = read_matpower(data_file)

    routine = FastDecoupledPFRoutine(n).solve()

# EOF -------------------------------------------------------------------------
