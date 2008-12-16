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
import logging

import numpy
from numpy import dot

from cvxopt.base import matrix, spmatrix, sparse, gemv, exp, mul, div

from cvxopt.umfpack import linsolve
import cvxopt.blas

from pylon.routine.y import make_admittance_matrix, AdmittanceMatrix

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

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

    # Vector of bus voltages:
    v = matrix

    # Sparse admittance matrix:
    Y = spmatrix

    # Complex bus power injections.
    s_surplus = matrix

    # Flag indicating if the solution converged:
    converged = False

    # Bus indexes for updating v.
    pv_idxs = []
    pq_idxs = []
    pvpq_idxs = []
    slack_idx = 0

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

        self._make_admittance_matrix()
        self._initialise_voltage_vector()
        self._make_apparent_power_injection_vector()

#        self.iterate()


    def _make_admittance_matrix(self):
        """ Forms the admittance matrix for the referenced network. """

        self.Y = make_admittance_matrix(self.network)

    #--------------------------------------------------------------------------
    #  Form array of initial voltages at each node:
    #--------------------------------------------------------------------------

    def _initialise_voltage_vector(self):
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

        self.v = v_initial

    #--------------------------------------------------------------------------
    #  Vector of apparent power injected at each bus:
    #--------------------------------------------------------------------------

    def _make_power_injection_vector(self):
        """ Makes the vector of complex bus power injections (gen - load). """

        buses = self.network.non_islanded_buses

        self.s_surplus = matrix(
            [complex(v.p_surplus, v.q_surplus) for v in buses], tc="z"
        )

    #--------------------------------------------------------------------------
    #  Index buses for updating v:
    #--------------------------------------------------------------------------

    def _index_buses(self):
        """ Set up indexing for updating v. """

        buses = self.network.non_islanded_buses

        # Indexing for updating v
        pv_idxs = [i for i, v in enumerate(buses) if v.mode is "PV"]
        pq_idxs = [i for i, v in enumerate(buses) if v.mode is "PQ"]
        pvpq_idxs = pv_idxs + pq_idxs

        slack_idxs = [i for i, v in enumerate(buses) if v.mode is "Slack"]
        if len(slack_idxs) > 0:
            slack_idx = slack_idxs[0]
        else:
            logger.error    ("No reference/swing/slack bus specified.")
            slack_idx = 0

        self.slack_idx = slack_idx
        self.pv_idxs = pv_idxs
        self.pq_idxs = pq_idxs
        self.pvpq_idxs = pvpq_idxs

# EOF -------------------------------------------------------------------------
