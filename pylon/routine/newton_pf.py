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

""" Defines a routine for solving the power flow problem using full Newton's
method.

References:
    D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
    MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import math
import cmath
import logging

from cvxopt.base import matrix, spmatrix, sparse, gemv, exp, mul, div
from cvxopt.umfpack import linsolve
import cvxopt.blas

from pylon.routine.ac_pf import ACPFRoutine

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Convenient conjugate function:
#------------------------------------------------------------------------------

def conj(A):
    """ Returns the complex conjugate of A as a new matrix. """

    return A.ctrans().trans()

#------------------------------------------------------------------------------
#  "NewtonPFRoutine" class:
#------------------------------------------------------------------------------

class NewtonPFRoutine(ACPFRoutine):
    """ Solves the power flow using full Newton's method. """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Sparse Jacobian matrix (updated each iteration)
    J = spmatrix

    # Vector of bus voltages
    v = matrix

    # Function of non-linear differential agebraic equations
    f = matrix

    # Bus indexing for updating v
    pv_idxs = []
    pq_idxs = []
    pvpq_idxs = []
    slack_idx = 0

    #--------------------------------------------------------------------------
    #  Solve power flow using full Newton's method:
    #--------------------------------------------------------------------------

    def solve(self):
        """ Solves the AC power flow for the referenced network using full
        Newton's method.

        """

        self._make_admittance_matrix()
        self._initialise_voltage_vector()
        self._make_apparent_power_injection_vector()
        self._index_buses()

        # Initial evaluation of f(x0) and convergency check
        self.converged = False
        self._evaluate_function()
        self._check_convergence()

        iter = 0
#        while (not self.converged) and (iter < self.iter_max):
#            self.iterate()
#            self._evaluate_function()
#            self._check_convergence()
#            iter += 1

        if self.converged:
            logger.info("Routine converged in %d iterations." % iter)
        else:
            logger.info("Routine failed to converge in %d iterations." % iter)

    #--------------------------------------------------------------------------
    #  Newton iterations:
    #--------------------------------------------------------------------------

    def iterate(self):
        """ Performs Newton iterations. """

        J = self._make_jacobian()
        F = self.f

        # Compute update step
        # Solves the sparse set of linear equations AX=B where A is a sparse
        # matrix and B is a dense matrix of the same type ("d" or "z") as A. On
        # exit B contains the solution.
        # TODO: trace inaccuracy back to F(x0)
        linsolve(J, F)
        dx = -1 * F
        print "dx", dx

        # Update voltage vector
        if pv_idxs:
            Va[pv_idxs] = Va[pv_idxs] + dx[range(len(pv_idxs))]

        if pq_idxs:
            Va[pq_idxs] = Va[pq_idxs] + dx[
                range(len(pv_idxs), len(pv_idxs)+len(pq_idxs))
            ]

            Vm[pq_idxs] = Vm[pq_idxs] + dx[
                range(
                    len(pv_idxs)+len(pq_idxs),
                    len(pv_idxs)+len(pq_idxs)+len(pq_idxs)
                )
            ]

        voltage = Vm * numpy.exp(j * Va)
        # Avoid wrapped round negative Vm
        # TODO: check necessity
        Vm = numpy.abs(voltage)
        Va = angle(voltage)

    #--------------------------------------------------------------------------
    #  Evaluate Jacobian:
    #--------------------------------------------------------------------------

    def _make_jacobian(self):
        """ Evaluates the Jacobian matrix. """

        j = cmath.sqrt(-1)
        Y = self.Y
        v = self.v

#        Ibus = cvxopt.blas.dot(matrix(self.admittance), voltage)
        Ibus = Y * v
#        Ibus = self.admittance.trans() * voltage
        print "Ibus", Ibus

        n_buses = len(self.network.buses)

        diagV = spmatrix(v, range(n_buses), range(n_buses), tc="z")
        print "diagV", diagV

        diagIbus = spmatrix(Ibus, range(n_buses), range(n_buses), tc="z")
        print "diagIbus", diagIbus

        diagVnorm = spmatrix(
            div(v, abs(v)), range(n_buses), range(n_buses), tc="z"
        )
        print "diagVnorm", diagVnorm

#        dS_dVm = dot(
#            dot(diagV, conj(dot(Y, diagVnorm))) + conj(diagIbus), diagVnorm
#        )
        #dS_dVm = dot(diagV, conj(dot(Y, diagVnorm))) + dot(conj(diagIbus), diagVnorm)

#        dS_dVa = dot(dot(j, diagV), conj(dot(diagIbus - Y, diagV)))
        #dS_dVa = dot(dot(j, diagV), conj(diagIbus - dot(Y, diagV)))

        # from MATPOWER v3.2
        # dSbus_dVm = diagV * conj(Ybus * diagVnorm) + conj(diagIbus) * diagVnorm;
        # dSbus_dVa = j * diagV * conj(diagIbus - Ybus * diagV);


#            dP_dVm = spmatrix(map(lambda x: x.real, dS_dVm), dS_dVm.I, dS_dVa.J, tc="d")
#            print "dP_dVm", dP_dVm
#
#            dP_dVa = spmatrix(map(lambda x: x.real, dS_dVa), dS_dVa.I, dS_dVa.J, tc="d")
#            print "dP_dVa", dP_dVa
#
#            dQ_dVm = spmatrix(map(lambda x: x.imag, dS_dVm), dS_dVm.I, dS_dVm.J, tc="d")
#            print "dQ_dVm", dQ_dVm
#
#            dQ_dVa = spmatrix(map(lambda x: x.imag, dS_dVa), dS_dVa.I, dS_dVa.J, tc="d")
#            print "dQ_dVa", dQ_dVa

#            J11 = dP_dVa[pvpq_idxs, pvpq_idxs]
#            J12 = dP_dVm[pvpq_idxs, pq_idxs]
#            J21 = dQ_dVa[pq_idxs, pvpq_idxs]
#            J22 = dQ_dVm[pq_idxs, pq_idxs]

#        J11 = dS_dVa[pvpq_idxs, pvpq_idxs].real()
#        J12 = dS_dVm[pvpq_idxs, pq_idxs].real()
#        J21 = dS_dVa[pq_idxs, pvpq_idxs].imag()
#        J22 = dS_dVm[pq_idxs, pq_idxs].imag()

        # The width and height of one quadrant of the Jacobian.
#        w, h = J11.size
#        print "w, h", J11.size, J12.size, J21.size, J22.size

        # A single-column dense matrix containing the numerical values of
        # the nonzero entries of the four quadrants of the Jacobian in
        # column-major order.
#        values = numpy.vstack((J11.V, J12.V, J21.V, J22.V))

        # A single-column integer matrix with the row indices of the entries
        # in "values" shifted appropriately by the width of one quadrant.
#        row_idxs = numpy.vstack((J11.I, J12.I, J21.I+h, J22.I+h))

        # A single-column integer matrix with the column indices of the
        # entries in "values" shifted appropriately by the width of one
        # quadrant.
#        col_idxs = numpy.vstack((J11.J, J12.J+w, J21.J, J22.J+w))

        # A deep copy of "values" is required for contiguity.
#        J = spmatrix(values.copy(), row_idxs, col_idxs)
#        print "J", J

#        return J

    #--------------------------------------------------------------------------
    #  Evaluate F(x):
    #--------------------------------------------------------------------------

    def _evaluate_function(self):
        """ Evaluates F(x). """

        # MATPOWER:
        #   mis = V .* conj(Ybus * V) - Sbus;
        v = self.v
        mismatch = mul(v, conj(self.Y * v)) - self.s_surplus


        real = mismatch[self.pvpq_idxs].real()
        imag = mismatch[self.pq_idxs].imag()

        self.f = f = matrix([real, imag])

        return f

    #--------------------------------------------------------------------------
    #  Check convergence:
    #--------------------------------------------------------------------------

    def _check_convergence(self):
        """ Checks if the solution has converged to within the specified
        tolerance.

        """

        F = self.f

        normF = max(abs(F))

        if normF < self.tolerance:
            self.converged = converged = True
        else:
            self.converged = converged = False
#            logger.info("Difference: %.3f" % normF-self.tolerance)

        return converged

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

        self.slack_idx = matrix(slack_idx)
        self.pv_idxs = matrix(pv_idxs)
        self.pq_idxs = matrix(pq_idxs)
        self.pvpq_idxs = matrix(pvpq_idxs)

#------------------------------------------------------------------------------
#  Standalone call:
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

    routine = NewtonPFRoutine(n).solve()

# EOF -------------------------------------------------------------------------
