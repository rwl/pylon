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

    #--------------------------------------------------------------------------
    #  Solve power flow using Fast Decoupled method:
    #--------------------------------------------------------------------------

    def solve(self):
        """
        Solves the AC power flow for the referenced network using fast
        decoupled method.

        """

    #--------------------------------------------------------------------------
    #  P and Q iterations:
    #--------------------------------------------------------------------------

    def iterate(self):
        """ Performs P and Q iterations. """

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
