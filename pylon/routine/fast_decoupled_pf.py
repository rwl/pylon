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

    Bp = spmatrix

    # Use XB or BX method?
    method = "XB"

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

    #--------------------------------------------------------------------------
    #  P and Q iterations:
    #--------------------------------------------------------------------------

    def iterate(self):
        """ Performs P and Q iterations. """

        pass


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
