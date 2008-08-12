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

""" Solves AC power flow

References:
    D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
    MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path
import cmath

import numpy
from numpy import dot

from cvxopt.base import matrix, spmatrix, sparse, gemv
from cvxopt.umfpack import linsolve
import cvxopt.blas

from pylon.routine.y import SimpleAdmittanceMatrix

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ICON_LOCATION = path.join(path.dirname(__file__), "icons")

#------------------------------------------------------------------------------
#  "ACPFRoutine" class:
#------------------------------------------------------------------------------

class ACPFRoutine:
    """ Solves AC power flow

    References:
        D. Zimmerman, Carlos E. Murillo-Sanchez and Deqiang (David) Gan,
        MATPOWER, version 3.2, http://www.pserc.cornell.edu/matpower/

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Flag indicating if the solution converged:
    converged = False

    # Convergence tolerance
    tolerance = 1e-08

    # Maximum number of iterations:
    maximum_iterations = 10

    # The initial bus voltages:
    initial_voltage = matrix

    # Sparse admittance matrix:
    admittance = spmatrix

    # Apparent power supply at each node:
    apparent_supply = matrix

    # Apparent power demand at each node:
    apparent_demand = matrix

    #--------------------------------------------------------------------------
    #  Solve power flow:
    #--------------------------------------------------------------------------

    def solve(self):
        sam = SimpleAdmittanceMatrix()
        self.admittance = sam.build(self.network)
        self.initial_voltage = self._get_initial_voltage_vector()
#        self.apparent_supply = self._get_apparent_supply_vector()
#        self.apparent_demand = self._get_apparent_demand_vector()
        self.apparent = self._get_apparent_power_vector()
        print 'Apparent', self.apparent

        self.iterate()

    #--------------------------------------------------------------------------
    #  Form array of initial voltages at each node:
    #--------------------------------------------------------------------------

    def _get_initial_voltage_vector(self):
        j = cmath.sqrt(-1)
        Vm0 = numpy.ones(len(self.network.buses))
        Va0 = numpy.zeros(len(self.network.buses)) #degrees

        Vm0[1] = 1.02
        Va0[1] = 0.1

        # convert to radians
        Va0d = (Va0 * cmath.pi) / 180
        return matrix((Vm0 * numpy.exp(j * Va0d)), tc='z')

    #--------------------------------------------------------------------------
    #  Evaluate Jacobian:
    #--------------------------------------------------------------------------

    def _get_jacobian_matrix(self, voltage):
        Y = self.admittance
        print 'Ybus', Y

        j = cmath.sqrt(-1)

        print 'voltage', voltage

#        voltage = matrix([1,1.02,1], (3,1), tc='z')

#        Ibus = cvxopt.blas.dot(matrix(self.admittance), voltage)
        Ibus = dot(matrix(self.admittance), voltage)
#        Ibus = self.admittance.trans() * voltage
        print 'Ibus', Ibus

        n_buses = len(self.network.buses)

        diagV = spmatrix(voltage, range(n_buses), range(n_buses), tc='z')
        print 'diagV', diagV

        diagIbus = spmatrix(Ibus, range(n_buses), range(n_buses), tc='z')
        print 'diagIbus', diagIbus

        diagVnorm = spmatrix(
            numpy.divide(voltage, abs(voltage)),
            range(n_buses), range(n_buses), tc="z"
        )
        print 'diagVnorm', diagVnorm

        dS_dVm = dot(
            dot(diagV, conj(dot(Y, diagVnorm))) + conj(diagIbus), diagVnorm
        )
        #dS_dVm = dot(diagV, conj(dot(Y, diagVnorm))) + dot(conj(diagIbus), diagVnorm)

        dS_dVa = dot(dot(j, diagV), conj(dot(diagIbus - Y, diagV)))
        #dS_dVa = dot(dot(j, diagV), conj(diagIbus - dot(Y, diagV)))

        # from MATPOWER v3.2
        # dSbus_dVm = diagV * conj(Ybus * diagVnorm) + conj(diagIbus) * diagVnorm;
        # dSbus_dVa = j * diagV * conj(diagIbus - Ybus * diagV);

        return dS_dVm, dS_dVa


    def iterate(self):
        buses = self.network.buses
        n_buses = len(buses)

        j = cmath.sqrt(-1)

        voltage = self.initial_voltage
        Vm = matrix(numpy.abs(voltage), tc='d')
        Va = matrix(numpy.angle(voltage), tc='d')

        pv_idxs = [buses.index(v) for v in buses if v.type is 'PV']

        pq_idxs = [buses.index(v) for v in buses if v.type is 'PQ']

        pvpq_idxs = [
            buses.index(v) for v in buses if v.type is 'PQ' or v.type is 'PV'
        ]

        slack_idxs = [buses.index(v) for v in buses if v.type is 'Slack']

        # Check that ther is only one slack bus
        if len(slack_idxs) is not 1:
            print 'One and only one slack bus must be specified'
            return
        else:
            slack_idx = slack_idxs[0]

        self.converged = False
        iteration = 0

        voltage_sp = spmatrix(self.initial_voltage, range(n_buses), [0]*n_buses)
        print 'voltage (sparse)', voltage_sp

        apparent_sp = spmatrix(self.apparent, range(n_buses), [0]*n_buses)
        print 'apparent (sparse)', apparent_sp

        # Evaluate F(x0)
        # TODO: inaccuracy in Bus 2
        # TODO: sparse necessity
        mis = conj(dot(self.admittance, voltage_sp)) - apparent_sp
        print 'mis', mis

        Re = matrix(mis[pvpq_idxs].real())
        print 'Re', Re
        Im = matrix(mis[pq_idxs].imag())
        print 'Im', Im
        F = matrix(numpy.vstack((Re, Im)))
        print 'F', F

        while(not self.converged and iteration < self.maximum_iterations):

            dS_dVm, dS_dVa = self._get_jacobian_matrix(voltage)
            print 'dS_dVm', dS_dVm
            print 'dS_dVa', dS_dVa

#            dP_dVm = spmatrix(map(lambda x: x.real, dS_dVm), dS_dVm.I, dS_dVa.J, tc='d')
#            print 'dP_dVm', dP_dVm
#
#            dP_dVa = spmatrix(map(lambda x: x.real, dS_dVa), dS_dVa.I, dS_dVa.J, tc='d')
#            print 'dP_dVa', dP_dVa
#
#            dQ_dVm = spmatrix(map(lambda x: x.imag, dS_dVm), dS_dVm.I, dS_dVm.J, tc='d')
#            print 'dQ_dVm', dQ_dVm
#
#            dQ_dVa = spmatrix(map(lambda x: x.imag, dS_dVa), dS_dVa.I, dS_dVa.J, tc='d')
#            print 'dQ_dVa', dQ_dVa

#            J11 = dP_dVa[pvpq_idxs, pvpq_idxs]
#            J12 = dP_dVm[pvpq_idxs, pq_idxs]
#            J21 = dQ_dVa[pq_idxs, pvpq_idxs]
#            J22 = dQ_dVm[pq_idxs, pq_idxs]

            J11 = dS_dVa[pvpq_idxs, pvpq_idxs].real()
            J12 = dS_dVm[pvpq_idxs, pq_idxs].real()
            J21 = dS_dVa[pq_idxs, pvpq_idxs].imag()
            J22 = dS_dVm[pq_idxs, pq_idxs].imag()

            # The width and height of one quadrant of the Jacobian.
            w, h = J11.size
            print 'w, h', J11.size, J12.size, J21.size, J22.size

            # A single-column dense matrix containing the numerical values of
            # the nonzero entries of the four quadrants of the Jacobian in
            # column-major order.
            values = numpy.vstack((J11.V, J12.V, J21.V, J22.V))

            # A single-column integer matrix with the row indices of the entries
            # in 'values' shifted appropriately by the width of one quadrant.
            row_idxs = numpy.vstack((J11.I, J12.I, J21.I+h, J22.I+h))

            # A single-column integer matrix with the column indices of the
            # entries in 'values' shifted appropriately by the width of one
            # quadrant.
            col_idxs = numpy.vstack((J11.J, J12.J+w, J21.J, J22.J+w))

            # A deep copy of 'values' is required for contiguity.
            J = spmatrix(values.copy(), row_idxs, col_idxs)
            print 'J', J

            # Compute update step
            # Solves the sparse set of linear equations AX=B where A is a sparse
            # matrix and B is a dense matrix of the same type ('d' or 'z') as A. On
            # exit B contains the solution.
            # TODO: trace inaccuracy back to F(x0)
            linsolve(J, F)
            dx = -1 * F
            print 'dx', dx

            # Update voltage vector
            if len(pv_idxs) > 0:
                Va[pv_idxs] = Va[pv_idxs] + dx[range(len(pv_idxs))]

            if len(pq_idxs) > 0:
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
            Vm = matrix(numpy.abs(voltage), tc='d')
            Va = matrix(numpy.angle(voltage), tc='d')

            print 'voltage', voltage

            # Evaluate F(x)
            voltage_sp = spmatrix(voltage, range(n_buses), [0]*n_buses)
            #apparent_sp = spmatrix(self.apparent, range(n_buses), [0]*n_buses)

            # Evaluate F(x0)
            # TODO: inaccuracy in Bus 2
            # TODO: sparse necessity
            mis = conj(dot(self.admittance, voltage_sp)) - apparent_sp
            print 'mis (iter)', mis

            Re = matrix(mis[pvpq_idxs].real())
            print 'Re', Re
            Im = matrix(mis[pq_idxs].imag())
            print 'Im', Im
            F = matrix(numpy.vstack((Re, Im)))
            print 'F (iter)', F

            # Check for convergence
            normF = max(abs(F))
            print 'normF', normF

            if normF < self.tolerance:
                self.converged = True
                print 'Converged in %d iterations' % iteration

            iteration += 1

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    from pylon.filter.api import PSATImporter

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    filter = PSATImporter()
    data_file = "/home/rwl/python/aes/psat_20080214/src/rwl_003_opf_mdl.m"
    n = filter.parse_file(data_file)

    routine = ACPFRoutine(network=n)

# EOF -------------------------------------------------------------------------
