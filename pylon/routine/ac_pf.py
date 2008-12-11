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

""" Defines a base class for may AC power flow routines.

References:
    D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
    MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path
import math
import cmath

import numpy
from numpy import dot

from cvxopt.base import matrix, spmatrix, sparse, gemv, exp, mul, div

from cvxopt.umfpack import linsolve
import cvxopt.blas

from pylon.routine.y import make_admittance_matrix

#------------------------------------------------------------------------------
#  "ACPFRoutine" class:
#------------------------------------------------------------------------------

class ACPFRoutine:
    """ Base class for many AC power flow routines.

    For implementations refer to:
        newton_pf.py,
        gauss_pf.py, and
        fast_decoupled_pf.py

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Convergence tolerance
    tolerance = 1e-08

    # Maximum number of iterations:
    iter_max = 10

    # The initial bus voltages:
    v_initial = matrix

    # Sparse admittance matrix:
    Y = spmatrix

    # Apparent power supply at each node:
    s_supply = matrix

    # Apparent power demand at each node:
    s_demand = matrix

    # Flag indicating if the solution converged:
    converged = False

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, network):
        """ Returns a new ACPFRoutine instance """

        self.network = network

    #--------------------------------------------------------------------------
    #  Solve power flow:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves the AC power flow for the referenced network. """

        self.admittance = make_admittance_matrix(self.network)
        self._make_initial_voltage_vector()
#        self._make_apparent_power_vector()

#        self.iterate()

    #--------------------------------------------------------------------------
    #  Form array of initial voltages at each node:
    #--------------------------------------------------------------------------

    def _make_initial_voltage_vector(self):
        """ Makes the initial vector of complex bus voltages.  The bus voltage
        vector contains the set point for generator (including ref bus) buses,
        and the reference angle of the swing bus, as well as an initial guess
        for remaining magnitudes and angles.

        """

        j = 0+1j #cmath.sqrt(-1)
        pi = math.pi
        buses = self.network.non_islanded_buses

        Vm0 = matrix([bus.v_amplitude_guess for bus in buses], tc='z')
        Va0 = matrix([bus.v_phase_guess for bus in buses]) #degrees

        Va0r = Va0 * pi / 180 #convert to radians

        v_initial = mul(Vm0, exp(j * Va0r)) #element-wise product

        # Incorporate generator set points.
        for i, bus in enumerate(buses):
            if len(bus.generators) > 0:
                # FIXME: Handle more than one generator at a bus
                g = bus.generators[0]
                # MATPOWER:
                #   V0(gbus) = gen(on, VG) ./ abs(V0(gbus)).* V0(gbus);
                #
                #            Vg
                #   V0 = ---------
                #        |V0| . V0
                #
#                v = mul(abs(v_initial[i]), v_initial[i])
#                v_initial[i] = div(g.v_amplitude, v)
#                v = abs(v_initial[i]) * v_initial[i]
#                v_initial[i] = g.v_amplitude / v
                v_initial[i] = g.v_amplitude

        self.v_initial = v_initial


    def iterate(self):
        """ Performs the iterations. """

        raise NotImplementedError("Override this method.")

# EOF -------------------------------------------------------------------------
