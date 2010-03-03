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

""" Defines a solver for DC power flow [1].

    [1] Ray Zimmerman, "dcpf.m", MATPOWER, PSERC Cornell, version 3.2,
        http://www.pserc.cornell.edu/matpower/, June 2007
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import time
import logging
import math

from numpy import array, linalg, pi, r_, ix_

from scipy.sparse.linalg import spsolve

from pylon.case import REFERENCE, PV, PQ

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "DCPF" class:
#------------------------------------------------------------------------------

class DCPF(object):
    """ Solves DC power flow [1].

        [1] Ray Zimmerman, "dcpf.m", MATPOWER, PSERC Cornell, version 3.2,
            http://www.pserc.cornell.edu/matpower/, June 2007
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, solver="UMFPACK"):
        """ Initialises a DCPF instance.
        """
        # Solved case.
        self.case = case

        # Vector of voltage phase angles.
        self.v_angle = None


    def solve(self):
        """ Solves DC power flow for the given case.
        """
        case = self.case
        logger.info("Starting DC power flow [%s]." % case.name)
        t0 = time.time()
        # Update bus indexes.
        self.case.index_buses()

        # Find the index of the refence bus.
        ref_idx = self._get_reference_index(case)
        if ref_idx < 0:
            return False

        # Build the susceptance matrices.
        B, Bsrc, p_businj, p_srcinj = case.Bdc
        # Get the vector of initial voltage angles.
        v_angle_guess = self._get_v_angle_guess(case)
        # Calculate the new voltage phase angles.
        v_angle, p_ref = self._get_v_angle(case, B, v_angle_guess, p_businj,
                                           ref_idx)
        logger.debug("Bus voltage phase angles: \n%s" % v_angle)
        self.v_angle = v_angle

        # Push the results to the case.
        self._update_model(case, B, Bsrc, v_angle, p_srcinj, p_ref, ref_idx)

        logger.info("DC power flow completed in %.3fs." % (time.time() - t0))

        return True

    #--------------------------------------------------------------------------
    #  Reference bus index:
    #--------------------------------------------------------------------------

    def _get_reference_index(self, case):
        """ Returns the index of the reference bus.
        """
        refs = [bus._i for bus in case.connected_buses if bus.type == REFERENCE]
        if len(refs) == 1:
            return refs [0]
        else:
            logger.error("Single swing bus required for DCPF.")
            return -1

    #--------------------------------------------------------------------------
    #  Build voltage phase angle guess vector:
    #--------------------------------------------------------------------------

    def _get_v_angle_guess(self, case):
        """ Make the vector of voltage phase guesses.
        """
        v_angle = array([bus.v_angle_guess * (pi / 180.0)
                         for bus in case.connected_buses])
        return v_angle

    #--------------------------------------------------------------------------
    #  Calculate voltage angles:
    #--------------------------------------------------------------------------

    def _get_v_angle(self, case, B, v_angle_guess, p_businj, iref):
        """ Calculates the voltage phase angles.
        """
        buses = case.connected_buses

        pv_idxs = [bus._i for bus in buses if bus.type == PV]
        pq_idxs = [bus._i for bus in buses if bus.type == PQ]
        pvpq_idxs = pv_idxs + pq_idxs
        pvpq_rows = [[i] for i in pvpq_idxs]

        # Get the susceptance matrix with the column and row corresponding to
        # the reference bus removed.
        Bpvpq = B[pvpq_rows, pvpq_idxs]

        Bref = B[pvpq_rows, [iref]]

        # Bus active power injections (generation - load) adjusted for phase
        # shifters and real shunts.
        p_surplus = array([case.s_surplus(v).real for v in buses])
        g_shunt = array([bus.g_shunt for bus in buses])
        Pbus = (p_surplus - p_businj - g_shunt) / case.base_mva

        Pbus.shape = len(Pbus), 1

        A = Bpvpq
        b = Pbus[pvpq_idxs] - Bref * v_angle_guess[iref]

#        x, res, rank, s = linalg.lstsq(A.todense(), b)
        x = spsolve(A, b)

        # Insert the reference voltage angle of the slack bus.
        v_angle = r_[x[:iref], v_angle_guess[iref], x[iref:]]

        return v_angle, Pbus[iref]

    #--------------------------------------------------------------------------
    #  Update model with solution:
    #--------------------------------------------------------------------------

    def _update_model(self, case, B, Bsrc, v_angle, p_srcinj, p_ref, ref_idx):
        """ Updates the case with values computed from the voltage phase
            angle solution.
        """
        iref = ref_idx
        base_mva = case.base_mva
        buses = case.connected_buses
        branches = case.online_branches

        p_from = (Bsrc * v_angle + p_srcinj) * base_mva
        p_to = -p_from

        for i, branch in enumerate(branches):
            branch.p_from = p_from[i]
            branch.p_to = p_to[i]
            branch.q_from = 0.0
            branch.q_to = 0.0

        for j, bus in enumerate(buses):
            bus.v_angle = v_angle[j] * (180 / pi)
            bus.v_magnitude = 1.0

        # Update Pg for swing generator.
        g_ref = [g for g in case.generators if g.bus == buses[iref]][0]
        # Pg = Pinj + Pload + Gs
        # newPg = oldPg + newPinj - oldPinj
        p_inj = (B[iref, :] * v_angle - p_ref) * base_mva
        g_ref.p += p_inj[0]

# EOF -------------------------------------------------------------------------
