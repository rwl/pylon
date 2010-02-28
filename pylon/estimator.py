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

""" State estimation based on code by Rui Bo and James S. Thorp.

    References:
        Ray Zimmerman and Rui Bo, "extras/se", MATPOWER, PSERC Cornell,
        http://www.pserc.cornell.edu/matpower/, version 4.0b1, December 2009
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging

from time import time

from numpy import array, pi, angle, multiply, exp, linalg, conj

from case import REFERENCE, PV, PQ

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

PF = "Pf" # Measurement of active power flow at a branch from end.
PT = "Pt"
QF = "Qf"
QT = "Qt"
PG = "Pg" # Active power generation at a bus.
QG = "Qg"
VA = "Va"
VM = "Vm"

CASE_GUESS = "case guess"
FLAT_START = "flat start"
FROM_INPUT = "from input"

#------------------------------------------------------------------------------
#  "Measurement" class:
#------------------------------------------------------------------------------

class Measurement(object):
    """ Defines a measurement at a bus or a branch.
    """

    def __init__(self, bus_or_line, type, value):
        """ Initialises a new Measurement instance.
        """
        # Bus or branch component at which the measure was made.
        self.b_l = bus_or_line

        # Type of value measured.
        self.type = type

        # Measurement value.
        self.value = value

#------------------------------------------------------------------------------
#  "StateEstimator" class:
#------------------------------------------------------------------------------

class StateEstimator(object):
    """ State estimation based on code by Rui Bo.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, measurements, sigma=None, v_mag_guess=None,
                 max_iter=100, tolerance=1e-05, verbose=True):
        """ Initialises a new StateEstimator instance.
        """
        self.case = case

        # Measured values for the case.
        self.measurements = measurements

        # Measurement variances.
        self.sigma = matrix(0.0, (8, 1)) if sigma is None else sigma

        # Initial guess for voltage magnitude vector.
        self.v_mag_guess = v_mag_guess

        # Maximum number of iterations.
        self.max_iter = max_iter

        # Convergence tolerance.
        self.tolerance = tolerance

        # Log progress information.
        self.verbose = verbose

    #--------------------------------------------------------------------------
    #  Run the state estimator:
    #--------------------------------------------------------------------------

    def run(self):
        """ Solves a state estimation problem.
        """
        case = self.case
        baseMVA = case.base_mva
        buses = self.case.connected_buses
        branches = case.online_branches
        generators = case.online_generators

        # Index buses.
#        ref = [buses.index(b) for b in buses if b.type == REFERENCE]
        pv  = matrix([buses.index(b) for b in buses if b.type == PV])
        pq  = matrix([buses.index(b) for b in buses if b.type == PQ])

        # Build admittance matrices.
        Ybus, Yf, Yt = case.Y

        # Prepare initial guess.
        V0 = self.getV0(self.v_mag_guess, buses, generators)

        # Start the clock.
        t0 = time()

        # Initialise SE.
        converged = False
        i = 0
        V = V0
        Va = matrix(angle(V0))
        Vm = abs(V0)

        nb = Ybus.size[0]
        f = matrix([buses.index(b.from_bus) for b in branches])
        t = matrix([buses.index(b.to_bus)   for b in branches])
        nonref = matrix([pv, pq])

        # Form measurement vector.
        z = matrix([m.value for m in self.measurements])

        # Form measurement index vectors.
        idx_zPf = matrix([branches.index(m.b_l) for m in self.measurements
                          if m.type == PF])
        idx_zPt = matrix([branches.index(m.b_l) for m in self.measurements
                          if m.type == PT])
        idx_zQf = matrix([branches.index(m.b_l) for m in self.measurements
                          if m.type == QF])
        idx_zQt = matrix([branches.index(m.b_l) for m in self.measurements
                          if m.type == QT])
        idx_zPg = matrix([buses.index(m.b_l) for m in self.measurements
                          if m.type == PG])
        idx_zQg = matrix([buses.index(m.b_l) for m in self.measurements
                          if m.type == QG])
        idx_zVm = matrix([buses.index(m.b_l) for m in self.measurements
                          if m.type == VM])
        idx_zVa = matrix([buses.index(m.b_l) for m in self.measurements
                          if m.type == VA])

        # Create inverse of covariance matrix with all measurements.
#        full_scale = 30
#        sigma = [
#            0.02 * abs(Sf)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(St)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(Sbus)    + 0.0052 * full_scale * ones(nb,1),
#            0.2 * pi/180 * 3*ones(nb,1),
#            0.02 * abs(Sf)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(St)      + 0.0052 * full_scale * ones(nbr,1),
#            0.02 * abs(Sbus)    + 0.0052 * full_scale * ones(nb,1),
#            0.02 * abs(V0)      + 0.0052 * 1.1 * ones(nb,1),
#        ] ./ 3

        # Get R inverse matrix.
        sigma_vector = matrix([
            self.sigma[0] * matrix(1.0, (idx_zPf.size[0], 1)),
            self.sigma[1] * matrix(1.0, (idx_zPt.size[0], 1)),
            self.sigma[2] * matrix(1.0, (idx_zQf.size[0], 1)),
            self.sigma[3] * matrix(1.0, (idx_zQt.size[0], 1)),
            self.sigma[4] * matrix(1.0, (idx_zPg.size[0], 1)),
            self.sigma[5] * matrix(1.0, (idx_zQg.size[0], 1)),
            self.sigma[6] * matrix(1.0, (idx_zVm.size[0], 1)),
            self.sigma[7] * matrix(1.0, (idx_zVa.size[0], 1))
        ])
        sigma_squared = sigma_vector**2

        Rinv = spdiag(1.0 / sigma_squared)

        # Do Newton iterations.
        while (not converged) and (i < self.max_iter):
            i += 1

            # Compute estimated measurement.
            Sfe = multiply(V[f], conj(Yf * V))
            Ste = multiply(V[t], conj(Yt * V))
            # Compute net injection at generator buses.
            gbus = matrix([buses.index(g.bus) for g in generators])
            Sgbus = multiply(V[gbus], conj(Ybus[gbus, :] * V))
            # inj S + local Sd
            Sd = matrix([complex(b.p_demand, b.q_demand) for b in buses])
            Sgen = (Sgbus * baseMVA + Sd) / baseMVA

            z_est = matrix([
                Sfe[idx_zPf].real(),
                Ste[idx_zPt].real(),
                Sfe[idx_zQf].imag(),
                Ste[idx_zQt].imag(),
                Sgen[idx_zPg].real(),
                Sgen[idx_zQg].imag(),
                abs(V[idx_zVm]),
                matrix(angle(V[idx_zVa]))
            ])

            # Get H matrix.
            dSbus_dVm, dSbus_dVa = case.dSbus_dV(Ybus, V)
            dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, _, _ = case.dSbr_dV(Yf, Yt,V)

            # Get sub-matrix of H relating to line flow.
            dPF_dVa = dSf_dVa.real() # from end
            dQF_dVa = dSf_dVa.imag()
            dPF_dVm = dSf_dVm.real()
            dQF_dVm = dSf_dVm.imag()
            dPT_dVa = dSt_dVa.real() # to end
            dQT_dVa = dSt_dVa.imag()
            dPT_dVm = dSt_dVm.real()
            dQT_dVm = dSt_dVm.imag()
            # Get sub-matrix of H relating to generator output.
            dPG_dVa = dSbus_dVa[gbus, :].real()
            dQG_dVa = dSbus_dVa[gbus, :].imag()
            dPG_dVm = dSbus_dVm[gbus, :].real()
            dQG_dVm = dSbus_dVm[gbus, :].imag()
            # Get sub-matrix of H relating to voltage angle.
            dVa_dVa = spmatrix(1.0, range(nb), range(nb))
            dVa_dVm = spmatrix([], [], [], (nb, nb))
            # Get sub-matrix of H relating to voltage magnitude.
            dVm_dVa = spmatrix([], [], [], (nb, nb))
            dVm_dVm = spmatrix(1.0, range(nb), range(nb))
            H = sparse([
                [dPF_dVa[idx_zPf, nonref],
                 dQF_dVa[idx_zQf, nonref],
                 dPT_dVa[idx_zPt, nonref],
                 dQT_dVa[idx_zQt, nonref],
                 dPG_dVa[idx_zPg, nonref],
                 dQG_dVa[idx_zQg, nonref],
                 dVm_dVa[idx_zVm, nonref],
                 dVa_dVa[idx_zVa, nonref]],
                [dPF_dVm[idx_zPf, nonref],
                 dQF_dVm[idx_zQf, nonref],
                 dPT_dVm[idx_zPt, nonref],
                 dQT_dVm[idx_zQt, nonref],
                 dPG_dVm[idx_zPg, nonref],
                 dQG_dVm[idx_zQg, nonref],
                 dVm_dVm[idx_zVm, nonref],
                 dVa_dVm[idx_zVa, nonref]]
            ])

            # Compute update step.
            J = H.T * Rinv * H
            F = H.T * Rinv * (z - z_est) # evalute F(x)
            linalg.solve(J, F)
#            cholmod.linsolve(J, F)
            dx = F

            # Check for convergence.
#            normF = norm(F, inf)
            normF = max(abs(F))

            if self.verbose:
                logger.info("Iteration [%d]: Norm of mismatch: %.3f" %
                            (i, normF))
            if normF < self.tolerance:
                converged = True

            # Update voltage.
            npvpq = nonref.size[0]

            Va[nonref] = Va[nonref] + dx[:npvpq]
            Vm[nonref] = Vm[nonref] + dx[npvpq:2 * npvpq]

            V = multiply(Vm, exp(1j * Va))
            Va = matrix(angle(V))
            Vm = abs(V)

        # Weighted sum squares of error.
        error_sqrsum = sum((z - z_est)**2 / sigma_squared)

        # Update case with solution.
        case.pf_solution(Ybus, Yf, Yt, V)

        # Stop the clock.
        elapsed = time() - t0

        if self.verbose and converged:
            print "State estimation converged in: %.3fs (%d iterations)" % \
            (elapsed, i)
#            self.output_solution(sys.stdout, z, z_est)

        solution = {"V": V, "success": converged, "iterations": i,
                    "z": z, "z_est": z_est, "error_sqrsum": error_sqrsum,
                    "elapsed": elapsed}

        return solution


    def getV0(self, v_mag_guess, buses, generators, type=CASE_GUESS):
        """ Returns the initial voltage profile.
        """
        if type == CASE_GUESS:
            Va = matrix([b.v_angle_guess * (pi / 180.0) for b in buses])
            Vm = matrix([b.v_magnitude_guess for b in buses])
            V0 = multiply(Vm, exp(1j * Va))
        elif type == FLAT_START:
            V0 = matrix(1.0, (len(buses), 1))
        elif type == FROM_INPUT:
            V0 = v_mag_guess
        else:
            raise ValueError

        # Set the voltages of PV buses and the reference bus in the guess.
#        online = [g for g in self.case.generators if g.online]
        gbus = matrix([buses.index(g.bus) for g in generators])
        Vg = matrix([g.v_magnitude for g in generators])

        V0[gbus] = multiply(Vg, abs(V0[gbus]) / V0[gbus])

        return V0


    def output_solution(self, fd, z, z_est, error_sqrsum):
        """ Prints comparison of measurements and their estimations.
        """
        col_width = 11
        sep = ("=" * col_width + " ") * 4 + "\n"

        fd.write("State Estimation\n")
        fd.write("-" * 16 + "\n")
        fd.write(sep)
        fd.write("Type".center(col_width) + " ")
        fd.write("Name".center(col_width) + " ")
        fd.write("Measurement".center(col_width) + " ")
        fd.write("Estimation".center(col_width) + " ")
        fd.write("\n")
        fd.write(sep)

        c = 0
        for t in [PF, PT, QF, QT, PG, QG, VM, VA]:
            for meas in self.measurements:
                if meas.type == t:
                    n = meas.b_l.name[:col_width].ljust(col_width)
                    fd.write(t.ljust(col_width) + " ")
                    fd.write(n + " ")
                    fd.write("%11.5f " % z[c])
                    fd.write("%11.5f\n" % z_est[c])
#                    fd.write("%s\t%s\t%.3f\t%.3f\n" % (t, n, z[c], z_est[c]))
                    c += 1

        fd.write("\nWeighted sum of error squares = %.4f\n" % error_sqrsum)

# EOF -------------------------------------------------------------------------
