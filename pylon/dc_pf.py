#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

""" Defines a solver for DC power flow.

    References:
        Ray Zimmerman, "dcpf.m", MATPOWER, PSERC Cornell, version 3.2,
        http://www.pserc.cornell.edu/matpower/, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging
import math

from cvxopt import matrix, umfpack, cholmod

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "DCPF" class:
#------------------------------------------------------------------------------

class DCPF(object):
    """ Solves DC power flow.

        References:
            Ray Zimmerman, "dcpf.m", MATPOWER, PSERC Cornell, version 3.2,
            http://www.pserc.cornell.edu/matpower/, June 2007
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, solver="UMFPACK"):
        """ Initialises a DCPF instance.
        """
        # CVXOPT offers interfaces to two routines for solving sets of sparse
        # linear equations: 'UMFPACK' and 'CHOLMOD' (default: 'UMFPACK')
        self.solver = solver

        # Solved case.
        self.case = case

        # Branch susceptance matrix.
        self.B = None

        # Branch from bus susceptance matrix.
        self.Bsrc = None

        # Vector of bus phase shift injections.
        self.p_businj = None

        # Vector of phase shift injections at the from buses.
        self.p_srcinj = None

        # Vector of voltage angle guesses.
        self.v_angle_guess = None

        # Vector of voltage phase angles.
        self.v_angle = None

        # Index of the reference bus.
        self.ref_idx = -1

        # Active power injection at the reference bus.
        self.p_ref = 0.0


    def solve(self):
        """ Solves DC power flow for the given case.
        """
        case = self.case

        logger.info("Starting DC power flow [%s]." % case.name)

        t0 = time.time()

        # Find the index of the refence bus.
        self.ref_idx = self._get_reference_index(case)

        if self.ref_idx < 0:
            return False

        # Build the susceptance matrices.
        self.B, self.Bsrc, self.p_businj, self.p_srcinj = case.Bdc

        # Get the vector of initial voltage angles.
        self.v_angle_guess = self._get_v_angle_guess(case)

        # Calculate the new voltage phase angles.
        self.v_angle = self._get_v_angle(case)
        logger.debug("Bus voltage phase angles: \n%s" % self.v_angle)

        # Push the results to the case.
        self._update_model(case)

        logger.info("DC power flow completed in %.3fs." % (time.time() - t0))

        return True

    #--------------------------------------------------------------------------
    #  Reference bus index:
    #--------------------------------------------------------------------------

    def _get_reference_index(self, case):
        """ Returns the index of the reference bus.
        """
        for i, bus in enumerate(case.connected_buses):
            if bus.type == "ref":
                return i
        else:
            logger.error("Swing bus required for DCPF.")
            return -1

    #--------------------------------------------------------------------------
    #  Build voltage phase angle guess vector:
    #--------------------------------------------------------------------------

    def _get_v_angle_guess(self, case):
        """ Make the vector of voltage phase guesses.
        """
        v_angle = matrix([bus.v_angle_guess * (math.pi / 180.0)
                       for bus in case.connected_buses])
        return v_angle

    #--------------------------------------------------------------------------
    #  Calculate voltage angles:
    #--------------------------------------------------------------------------

    def _get_v_angle(self, case):
        """ Calculates the voltage phase angles.
        """
        iref = self.ref_idx
        buses = case.connected_buses

        pv_idxs = matrix([i for i, b in enumerate(buses) if b.type == "PV"])
        pq_idxs = matrix([i for i, b in enumerate(buses) if b.type == "PQ"])
        pvpq_idxs = matrix([pv_idxs, pq_idxs])

        # Get the susceptance matrix with the column and row corresponding to
        # the reference bus removed.
        Bpvpq = self.B[pvpq_idxs, pvpq_idxs]

        Bref = self.B[pvpq_idxs, iref]

        # Bus active power injections (generation - load) adjusted for phase
        # shifters and real shunts.
        p_surplus = matrix([case.s_surplus(v).real for v in buses])
        g_shunt = matrix([bus.g_shunt for bus in buses])
        p_bus = (p_surplus - self.p_businj - g_shunt) / case.base_mva

        self.p_ref = p_bus[iref]
        p_pvpq = p_bus[pvpq_idxs]

        v_angle_guess_ref = self.v_angle_guess[iref]

        A = Bpvpq
        b = p_pvpq - Bref * v_angle_guess_ref

        if self.solver == "UMFPACK":
            # Solves the sparse set of linear equations Ax=b where A is a
            # sparse matrix and B is a dense matrix of the same type ('d'
            # or 'z') as A. On exit b contains the solution.
            umfpack.linsolve(A, b)
        elif self.solver == "CHOLMOD":
            # Cholesky factorization routines from the CHOLMOD package.
            cholmod.linsolve(A, b)
        else:
            raise ValueError

        # Insert the reference voltage angle of the slack bus.
        v_angle = matrix([b[:iref], v_angle_guess_ref, b[iref:]])

        return v_angle

    #--------------------------------------------------------------------------
    #  Update model with solution:
    #--------------------------------------------------------------------------

    def _update_model(self, case):
        """ Updates the case with values computed from the voltage phase
            angle solution.
        """
        iref = self.ref_idx
        base_mva = case.base_mva
        buses = case.connected_buses
        branches = case.online_branches

        p_from = (self.Bsrc * self.v_angle + self.p_srcinj) * base_mva
        p_to = -p_from

        for i, branch in enumerate(branches):
            branch.p_from = p_from[i]
            branch.p_to = p_to[i]
            branch.q_from = 0.0
            branch.q_to = 0.0

        for j, bus in enumerate(buses):
            bus.v_angle = self.v_angle[j] * (180 / math.pi)
            bus.v_magnitude = 1.0

        # Update Pg for swing generator.
        g_ref = [g for g in case.generators if g.bus == buses[iref]][0]
        # Pg = Pinj + Pload + Gs
        # newPg = oldPg + newPinj - oldPinj
        p_inj = (self.B[iref, :] * self.v_angle - self.p_ref) * base_mva
        g_ref.p += p_inj[0]

# EOF -------------------------------------------------------------------------
