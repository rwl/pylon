#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Defines admittance and susceptance matrices.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from math import pi

from cvxopt.base import matrix, spmatrix, spdiag, exp, mul, div

from pylon.util import conj

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
#  "AdmittanceMatrix" class:
#------------------------------------------------------------------------------

class AdmittanceMatrix(object):
    """ Build sparse Y matrix.

        References:
            Ray Zimmerman, "makeYbus.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 1.8, June 2007
    """

    def __init__(self, bus_shunts=True, line_shunts=True, taps=True,
                 line_resistance=True, phase_shift=True):
        """ Initialises a new AdmittanceMatrix instance.
        """
        # Should shunts at buses be considered?
        self.bus_shunts = bus_shunts
        # Should line charging shunts be considered?
        self.line_shunts = line_shunts
        # Should tap positions be considered?
        self.taps = taps
        # Should line resistance be considered?
        self.line_resistance = line_resistance
        # Should phase shifters be considered?
        self.phase_shift = phase_shift

        # Sparse admittance matrix.
        self.Y = None


    def __call__(self, case):
        return self.build(case)


    def build(self, case=None):
        """ Builds the admittance matrix.
        """
        j = 0 + 1j

        base_mva   = case.base_mva
        buses      = case.connected_buses
        branches   = case.online_branches
        n_buses    = len(buses)
        n_branches = len(branches)

        online = matrix([e.online for e in branches])

        # Series admittance.
        # Ys = stat ./ (branch(:, BR_R) + j * branch(:, BR_X))
        if self.line_resistance:
            r = matrix([e.r for e in branches])
        else:
            r = matrix(0.0, (n_branches, 1)) # Zero out line resistance.

        x = matrix([e.x for e in branches])

        Ys = div(online, (r + j*x))

        # Line charging susceptance
        # Bc = stat .* branch(:, BR_B);
        if self.line_shunts:
            b = matrix([e.b for e in branches])
        else:
            b = matrix(0.0, (n_branches, 1)) # Zero out line charging shunts.
        Bc = mul(online, b)

        # Default tap ratio = 1.0.
        tap = matrix(1.0, (n_branches, 1), tc="d")
        if self.taps:
            # Indices of branches with non-zero tap ratio.
            idxs = [i for i, e in enumerate(branches) if e.ratio != 0.0]
            # Transformer off nominal turns ratio ( = 0 for lines ) (taps at
            # "from" bus, impedance at 'to' bus, i.e. ratio = Vf / Vt)"
            ratio = matrix([e.ratio for e in branches])
            # Assign non-zero tap ratios
            tap[idxs] = ratio[idxs]

        # Phase shifters
        # tap = tap .* exp(j*pi/180 * branch(:, SHIFT));
        # Convert branch attribute in degrees to radians
        if self.phase_shift:
            phase_shift = matrix([e.phase_shift * pi / 180 for e in branches])
        else:
            phase_shift = matrix(0.0, (n_branches, 1))

        tap = mul(tap, exp(j * phase_shift))

        # Ytt = Ys + j*Bc/2;
        # Yff = Ytt ./ (tap .* conj(tap));
        # Yft = - Ys ./ conj(tap);
        # Ytf = - Ys ./ tap;
        Ytt = Ys + j * Bc / 2
        Yff = div(Ytt, (mul(tap, conj(tap))))
        Yft = div(-Ys, conj(tap))
        Ytf = div(-Ys, tap)

        # Shunt admittance
        # Ysh = (bus(:, GS) + j * bus(:, BS)) / baseMVA;
        g_shunt = matrix([v.g_shunt for v in buses])
        if self.bus_shunts:
            b_shunt = matrix([v.b_shunt for v in buses])
        else:
            b_shunt = matrix(0.0, (n_buses, 1)) # Zero out shunts at buses.
        Ysh = (g_shunt + j * b_shunt) / base_mva

        # Connection matrices.
        source_bus = matrix([buses.index(e.source_bus) for e in branches])
        target_bus = matrix([buses.index(e.target_bus) for e in branches])
        Cf = spmatrix(1.0, source_bus, range(n_branches))
        Ct = spmatrix(1.0, target_bus, range(n_branches))

        # Build bus admittance matrix
        # Ybus = spdiags(Ysh, 0, nb, nb) + ...            %% shunt admittance
        # Cf * spdiags(Yff, 0, nl, nl) * Cf' + ...    %% Yff term of branch admittance
        # Cf * spdiags(Yft, 0, nl, nl) * Ct' + ...    %% Yft term of branch admittance
        # Ct * spdiags(Ytf, 0, nl, nl) * Cf' + ...    %% Ytf term of branch admittance
        # Ct * spdiags(Ytt, 0, nl, nl) * Ct';         %% Ytt term of branch admittance

        ff = Cf * spdiag(Yff) * Cf.T
        ft = Cf * spdiag(Yft) * Ct.T
        tf = Ct * spdiag(Ytf) * Cf.T
        tt = Ct * spdiag(Ytt) * Ct.T

        # Resize otherwise all-zero rows/columns are lost.
        Y = self.Y = spdiag(Ysh) + \
            spmatrix(ff.V, ff.I, ff.J, (n_buses, n_buses), tc="z") + \
            spmatrix(ft.V, ft.I, ft.J, (n_buses, n_buses), tc="z") + \
            spmatrix(tf.V, tf.I, tf.J, (n_buses, n_buses), tc="z") + \
            spmatrix(tt.V, tt.I, tt.J, (n_buses, n_buses), tc="z")

        # Build Ysrc and Ytgt such that Ysrc * V is the vector of complex
        # branch currents injected at each branch's "source" bus.
        i = matrix(range(n_branches) + range(n_branches))
        j = matrix([source_bus, target_bus])
        Ysource = spmatrix(matrix([Yff, Yft]), i, j, (n_branches, n_buses))
        Ytarget = spmatrix(matrix([Ytf, Ytt]), i, j, (n_branches, n_buses))

        return Y, Ysource, Ytarget

#------------------------------------------------------------------------------
#  "SusceptanceMatrix" class:
#------------------------------------------------------------------------------

class SusceptanceMatrix(object):
    """ Build sparse B matrices

        The bus real power injections are related to bus voltage angles by
            P = Bbus * Va + Pbusinj

        The real power flows at the from end the lines are related to the bus
        voltage angles by
            Pf = Bf * Va + Pfinj

        TODO: Speed up by using spdiag(x)
    """

    def __call__(self, case):
        return self.build(case)


    def build(self, case):
        """ Builds the susceptance matrices.
        """
        buses      = case.connected_buses
        branches   = case.online_branches
        n_buses    = len(buses)
        n_branches = len(branches)

        # Create an empty sparse susceptance matrix.
        # http://abel.ee.ucla.edu/cvxopt/documentation/users-guide/node32.html
        self.b = b = spmatrix([], [], [], (n_buses, n_buses))

        # Make an empty sparse source bus susceptance matrix
        self.b_source = b_source = spmatrix([], [], [], (n_branches, n_buses))

        for e in branches:
            e_idx = branches.index(e)
            # Find the indexes of the buses at either end of the branch
            src_idx = buses.index(e.source_bus)
            dst_idx = buses.index(e.target_bus)

            # B = 1/X
            if e.x != 0.0: # Avoid zero division
                b_branch = 1/e.x
            else:
                # infinite susceptance for zero reactance branch
                b_branch = 1e12#numpy.Inf

            # Divide by the branch tap ratio
            if e.ratio != 0.0:
                b_branch /= e.ratio

            # Off-diagonal matrix elements (i,j) are the negative
            # susceptance of branches between buses[i] and buses[j]
            b[src_idx, dst_idx] += -b_branch
            b[dst_idx, src_idx] += -b_branch
            # Diagonal matrix elements (k,k) are the sum of the
            # susceptances of the branches connected to buses[k]
            b[src_idx, src_idx] += b_branch
            b[dst_idx, dst_idx] += b_branch

            # Build Bf such that Bf * Va is the vector of real branch
            # powers injected at each branch's "source" bus
            b_source[e_idx, src_idx] = b_branch
            b_source[e_idx, dst_idx] = -b_branch

        logger.debug("Built branch susceptance matrix:\n%s" % b)

        logger.debug("Built source bus susceptance matrix:\n%s" % b_source)

        return b, b_source

#------------------------------------------------------------------------------
#  "AdmittanceMatrix" class:
#------------------------------------------------------------------------------

class PSATAdmittanceMatrix(object):
    """ Defines an admittance matrix as translated from PSAT.
    """

    def __call__(self, case):
        j = 0 + 1j
        buses = case.connected_buses
        n_buses = len(buses)
        branches = case.online_branches

        y = spmatrix([], [], [], size=(n_buses, n_buses), tc='z')

#        source_idxs = [e.source_bus for e in branches]
#        target_idxs = [e.target_bus for e in branches]
#
#        z = []
#        for e in branches:
#            if e.x != 0 and e.r != 0:
#                z.append(1/complex(e.r, e.x))
#            else:
#                z.append(Inf)
#
#        charge = [0.5*complex(0, e.b) for e in branches]
#
#        ts = [e.ratio*exp(j*e.phase_shift*pi/180) for e in branches]

        # TODO: Test speed increase with matrix algebra implementation
        for e in branches:
            source_idx = buses.index(e.source_bus)
            target_idx = buses.index(e.target_bus)

            # y = 1/(R+jX) + (G+jB)/2
            # The conductance (G) is considered negligible
            try: #avoid zero division
                z = 1 / (complex(e.r, e.x))
            except ZeroDivisionError:
                z = complex(0, 1e09) #infinite admittance for zero reactance

            # Shunt admittance
            charge = complex(0, e.b) / 2

            ts = e.ratio * exp(j * (e.phase_shift * pi / 180))
            ts2 = ts * conj(ts)

            # off-diagonal matrix elements (i,j) are the negative
            # admittance of branches between buses[i] and buses[j]
            # TODO: Establish why PSAT does it this way
            y[source_idx, target_idx] += -z * ts
            y[target_idx, source_idx] += -z * conj(ts)
            # diagonal matrix elements (k,k) are the sum of the
            # admittances of the branches connected to buses[k]
            y[source_idx, source_idx] += z + charge
            y[target_idx, target_idx] += z * ts2 + charge

        return y

#------------------------------------------------------------------------------
#  "make_susceptance_matrix" function:
#------------------------------------------------------------------------------

#def make_susceptance_matrix(case):
#    """ Returns the susceptance and source bus susceptance matrices for the
#        given case.
#    """
#
#    buses      = case.connected_buses
#    branches   = case.online_branches
#    n_buses    = len(buses)
#    n_branches = len(branches)
#
#    # Create an empty sparse susceptance matrix.
#    # http://abel.ee.ucla.edu/cvxopt/documentation/users-guide/node32.html
#    b = spmatrix([], [], [], (n_buses, n_buses))
#
#    # Make an empty sparse source bus susceptance matrix
#    b_source = spmatrix([], [], [], (n_branches, n_buses))
#
#    # Filter out branches that are out of service
##        active_branches = [e for e in branches if e.online]
#
#    for e in branches:
#        e_idx = branches.index(e)
#        # Find the indexes of the buses at either end of the branch
#        src_idx = buses.index(e.source_bus)
#        dst_idx = buses.index(e.target_bus)
#
#        # B = 1/X
#        if e.x != 0.0: # Avoid zero division
#            b_branch = 1/e.x
#        else:
#            # infinite susceptance for zero reactance branch
#            b_branch = 1e12#numpy.Inf
#
#        # Divide by the branch tap ratio
#        if e.ratio != 0.0:
#            b_branch /= e.ratio
#
#        # Off-diagonal matrix elements (i,j) are the negative
#        # susceptance of branches between buses[i] and buses[j]
#        b[src_idx, dst_idx] += -b_branch
#        b[dst_idx, src_idx] += -b_branch
#        # Diagonal matrix elements (k,k) are the sum of the
#        # susceptances of the branches connected to buses[k]
#        b[src_idx, src_idx] += b_branch
#        b[dst_idx, dst_idx] += b_branch
#
#        # Build Bf such that Bf * Va is the vector of real branch
#        # powers injected at each branch's "source" bus
#        b_source[e_idx, src_idx] = b_branch
#        b_source[e_idx, dst_idx] = -b_branch
#
#    logger.debug("Built branch susceptance matrix:\n%s" % b)
#
#    logger.debug("Built source bus susceptance matrix:\n%s" % b_source)
#
#    return b, b_source

#------------------------------------------------------------------------------
#  "make_admittance_matrix" function:
#------------------------------------------------------------------------------

#def make_admittance_matrix(case):
#    """ Returns an admittance matrix for the supplied case.
#    """
#    buses    = case.connected_buses
#    n_buses  = len(buses)
#    branches = case.online_branches
#
#    Y = spmatrix([], [], [], size=(n_buses, n_buses), tc="z")
#
#    for br in branches:
#        src_idx = buses.index(br.source_bus)
#        dst_idx = buses.index(br.target_bus)
#        # y = 1/(R+jX) + (G+jB)/2
#        # The conductance (G) is considered negligble
#        try:
#            y = 1/(complex(br.r, br.x))
#        except ZeroDivisionError:
##            print 'WW: zero division'
#            # if the branch has zero resistance and reactance then
#            # the admittance is infinite
#            y = 1e10
##        print 'y', y
#        chrg = complex(0, br.b)/2
#        # off-diagonal matrix elements (i,j) are the negative
#        # admittance of branches between buses[i] and buses[j]
#
#        # TODO: find out why the shunt admittance is not added
#        # to off-diagonal elements.
#        Y[src_idx, dst_idx] += -y
#        Y[dst_idx, src_idx] += -y
#        # diagonal matrix elements (k,k) are the sum of the
#        # admittances of the branches connected to buses[k]
#        Y[src_idx, src_idx] += y + chrg
#        Y[dst_idx, dst_idx] += y + chrg
#
#        # TODO: investigate why the imaginary componenets of the admittance
#        # matrix are slightly different to this from MATPOWER
#    return Y

# EOF -------------------------------------------------------------------------
