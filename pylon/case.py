#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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

""" Defines the Pylon network model.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from math import pi

from util import Named, Serializable

from cvxopt.base import matrix, spmatrix, spdiag, exp, mul, div

from util import conj, zero2one

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

j = 0 + 1j

BIGNUM = 1e12#numpy.Inf

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Case" class:
#------------------------------------------------------------------------------

class Case(Named, Serializable):
    """ Defines representation of an electric power system as a graph
        of Bus objects connected by Branches.
    """

    def __init__(self, name=None, base_mva=100.0, buses=None, branches=None,
            generators=None):
        """ Initialises a new Case instance.
        """
        # Unique name.
        self.name = name

        # Base apparent power (MVA).
        self.base_mva = base_mva

        # Busbars.
        self.buses = buses if buses is not None else []

        # Transmission lines, transformers and phase shifters.
        self.branches = branches if branches is not None else []

        # Generating units and dispatchable loads.
        self.generators = generators if generators is not None else []


    @property
    def connected_buses(self):
        """ Returns a list of buses that are connected to one or more branches
            or the first bus in a branchless system.
        """
        if self.branches:
            source_buses = [e.source_bus for e in self.branches]
            target_buses = [e.target_bus for e in self.branches]

            return [v for v in self.buses if v in source_buses + target_buses]
#            return [bus for bus in self.buses if bus.type != "isolated"]
        else:
            return self.buses[:1]


    @property
    def online_generators(self):
        """ All in-service generators.
        """
        return [g for g in self.generators if g.online]


    @property
    def online_branches(self):
        """ Property getter for in-service branches.
        """
        return [branch for branch in self.branches if branch.online]


    def p_supply(self, bus):
        """ Returns the total active power generation capacity at the given
            bus.
        """
        return sum([g.p for g in self.generators if g.bus == bus])


    def q_supply(self, bus):
        """ Returns the total reactive power generation capacity at the given
            bus.
        """
        return sum([g.q for g in self.generators if g.bus == bus])


    def p_demand(self, bus):
        """ Returns the total active power load at the given bus.
        """
        return sum([b.p_demand for b in self.buses if b == bus])


    def q_demand(self, bus):
        """ Returns the total reactive power load at the given bus.
        """
        return sum([b.q_demand for b in self.buses if b == bus])


    def p_surplus(self, bus):
        """ Returns the difference between active power supply and demand at
            the given bus.
        """
        return self.p_supply(bus) - self.p_demand(bus)


    def q_surplus(self, bus):
        """ Returns the difference between reactive power supply and demand at
            the given bus.
        """
        return self.p_supply(bus) - self.p_demand(bus)

    #--------------------------------------------------------------------------
    #  Admittance matrix:
    #--------------------------------------------------------------------------

    def get_admittance_matrix(self, bus_shunts=True, line_shunts=True,
            tap_positions=True, line_resistance=True, phase_shift=True):
        """ Returns the bus and branch admittance matrices, Ysrc and Ytgt, such
            that Ysrc * V is the vector of complex branch currents injected at
            each branch's "source" bus.

            References:
                Ray Zimmerman, "makeYbus.m", MATPOWER, PSERC Cornell,
                http://www.pserc.cornell.edu/matpower/, version 1.8, June 2007
        """
        n_bus = len(self.buses)
        n_branch = len(self.branches)

        online = matrix([e.online for e in self.branches])

        #----------------------------------------------------------------------
        #  Series admittance.
        #----------------------------------------------------------------------

        # Ys = stat ./ (branch(:, BR_R) + j * branch(:, BR_X))
        if line_resistance:
            r = matrix([e.r for e in self.branches])
        else:
            r = matrix(0.0, (n_branch, 1)) # Zero out line resistance.
        x = matrix([e.x for e in self.branches])

        Ys = div(online, (r + j * x))

        #----------------------------------------------------------------------
        #  Line charging susceptance.
        #----------------------------------------------------------------------

        # Bc = stat .* branch(:, BR_B);
        if line_shunts:
            b = matrix([e.b for e in self.branches])
        else:
            b = matrix(0.0, (n_branch, 1)) # Zero out line charging shunts.
        Bc = mul(online, b)

        #----------------------------------------------------------------------
        #  Transformer tap ratios.
        #----------------------------------------------------------------------

        tap = matrix(1.0, (n_branch, 1), tc="d") # Default tap ratio = 1.0.
        if tap_positions:
            # Indices of branches with non-zero tap ratio.
            idxs = [i for i, e in enumerate(self.branches) if e.ratio != 0.0]
            # Transformer off nominal turns ratio ( = 0 for lines ) (taps at
            # "from" bus, impedance at 'to' bus, i.e. ratio = Vf / Vt)"
            ratio = matrix([e.ratio for e in self.branches])
            # Set non-zero tap ratios.
            tap[idxs] = ratio[idxs]

        #----------------------------------------------------------------------
        #  Phase shifters.
        #----------------------------------------------------------------------

        # tap = tap .* exp(j*pi/180 * branch(:, SHIFT));
        # Convert branch attribute in degrees to radians
        if phase_shift:
            shift = matrix([e.phase_shift * pi / 180 for e in self.branches])
        else:
            phase_shift = matrix(0.0, (n_branch, 1))

        tap = mul(tap, exp(j * shift))

        #----------------------------------------------------------------------
        #  Branch admittance matrix elements.
        #----------------------------------------------------------------------

        #  | If |   | Yff  Yft |   | Vf |
        #  |    | = |          | * |    |
        #  | It |   | Ytf  Ytt |   | Vt |
        #
        # Ytt = Ys + j*Bc/2;
        # Yff = Ytt ./ (tap .* conj(tap));
        # Yft = - Ys ./ conj(tap);
        # Ytf = - Ys ./ tap;
        Ytt = Ys + j * Bc / 2
        Yff = div(Ytt, (mul(tap, conj(tap))))
        Yft = div(-Ys, conj(tap))
        Ytf = div(-Ys, tap)

        #----------------------------------------------------------------------
        #  Shunt admittance.
        #----------------------------------------------------------------------

        # Ysh = (bus(:, GS) + j * bus(:, BS)) / baseMVA;
        g_shunt = matrix([v.g_shunt for v in self.buses])
        if bus_shunts:
            b_shunt = matrix([v.b_shunt for v in self.buses])
        else:
            b_shunt = matrix(0.0, (n_bus, 1)) # Zero out shunts at buses.
        Ysh = (g_shunt + j * b_shunt) / self.base_mva

        #----------------------------------------------------------------------
        #  Connection matrices.
        #----------------------------------------------------------------------

        src = matrix([self.buses.index(e.source_bus) for e in self.branches])
        tgt = matrix([self.buses.index(e.target_bus) for e in self.branches])
        Cf = spmatrix(1.0, src, range(n_branch))
        Ct = spmatrix(1.0, tgt, range(n_branch))

        # Build bus admittance matrix
        # Ybus = spdiags(Ysh, 0, nb, nb) + ... %% shunt admittance
        # Cf * spdiags(Yff, 0, nl, nl) * Cf' + ...
        # Cf * spdiags(Yft, 0, nl, nl) * Ct' + ...
        # Ct * spdiags(Ytf, 0, nl, nl) * Cf' + ...
        # Ct * spdiags(Ytt, 0, nl, nl) * Ct';

        ff = Cf * spdiag(Yff) * Cf.T
        ft = Cf * spdiag(Yft) * Ct.T
        tf = Ct * spdiag(Ytf) * Cf.T
        tt = Ct * spdiag(Ytt) * Ct.T

        # Resize otherwise all-zero rows/columns are lost.
        Y = spdiag(Ysh) + \
            spmatrix(ff.V, ff.I, ff.J, (n_bus, n_bus), tc="z") + \
            spmatrix(ft.V, ft.I, ft.J, (n_bus, n_bus), tc="z") + \
            spmatrix(tf.V, tf.I, tf.J, (n_bus, n_bus), tc="z") + \
            spmatrix(tt.V, tt.I, tt.J, (n_bus, n_bus), tc="z")

        n_branch = len(self.branches)
        i = matrix(range(n_branch) + range(n_branch))
        j = matrix([src, tgt])
        Ysrc = spmatrix(matrix([Yff, Yft]), i, j, (n_branch, len(self.buses)))
        Ytgt = spmatrix(matrix([Ytf, Ytt]), i, j, (n_branch, len(self.buses)))

        return Y, Ysrc, Ytgt

    Y = property(get_admittance_matrix)

    #--------------------------------------------------------------------------
    #  Susceptance matrix:
    #--------------------------------------------------------------------------

    @property
    def B(self):
        """ Returns the sparse susceptance matrices.

            The bus real power injections are related to bus voltage angles by
                P = Bbus * Va + Pbusinj

            The real power flows at the from end the lines are related to the
            bus voltage angles by
                Pf = Bf * Va + Pfinj

            References:
                Ray Zimmerman, "makeBdc.m", MATPOWER, PSERC Cornell,
                http://www.pserc.cornell.edu/matpower/, version 1.10, June 2007
        """
        buses = self.connected_buses
        branches = self.online_branches
        n_bus = len(buses)
        n_branch = len(branches)

        # Create empty sparse susceptance matrices.
        # http://abel.ee.ucla.edu/cvxopt/documentation/users-guide/node32.html
        b = spmatrix([], [], [], (n_bus, n_bus))
        b_source = spmatrix([], [], [], (n_branch, n_bus))

        for e_idx, e in enumerate(branches):
            # Find the indexes of the buses at either end of the branch
            src_idx = buses.index(e.source_bus)
            dst_idx = buses.index(e.target_bus)

            # B = 1/X
            if e.x != 0.0: # Avoid zero division error.
                b_branch = 1 / e.x
            else:
                # Infinite susceptance for zero reactance branch.
                b_branch = BIGNUM

            # Divide by the branch tap ratio
            if e.ratio != 0.0:
                b_branch /= e.ratio

            # Off-diagonal matrix elements (i, j) are the negative
            # susceptance of branches between buses[i] and buses[j]
            b[src_idx, dst_idx] += -b_branch
            b[dst_idx, src_idx] += -b_branch
            # Diagonal matrix elements (k, k) are the sum of the
            # susceptances of the branches connected to buses[k]
            b[src_idx, src_idx] += b_branch
            b[dst_idx, dst_idx] += b_branch

            # Build Bf such that Bf * Va is the vector of real branch
            # powers injected at each branch's "source" bus
            b_source[e_idx, src_idx] = b_branch
            b_source[e_idx, dst_idx] = -b_branch

        return b, b_source

    #--------------------------------------------------------------------------
    #  Partial derivative of power injection w.r.t. voltage:
    #--------------------------------------------------------------------------

    def dSbus_dV(self, Y, v):
        """ Computes the partial derivative of power injection w.r.t. voltage.
        """
        i = Y * v

        diag_v = spdiag(v)
        diag_i = spdiag(i)
        diag_vnorm = spdiag(div(v, abs(v))) # Element-wise division.

        dS_dVm = diag_v * conj(Y * diag_vnorm) + conj(diag_i) * diag_vnorm
        dS_dVa = j * diag_v * conj(diag_i - Y * diag_v)

        return dS_dVm, dS_dVa

    #--------------------------------------------------------------------------
    #  Partial derivative of branch power flow w.r.t voltage:
    #--------------------------------------------------------------------------

    def dSbr_dV(self, Ysrc, Ytgt, v):
        """ Computes the branch power flow vector and the partial derivative of
            branch power flow w.r.t voltage.
        """
        n_branch = len(self.branches)
        n_bus = len(v)

        source_idxs = matrix([self.buses.index(branch.source_bus)
                              for branch in self.branches])
        target_idxs = matrix([self.buses.index(branch.target_bus)
                              for branch in self.branches])

        # Compute currents.
        i_source = Ysrc * v
        i_target = Ytgt * v

        # dV/dVm = diag(V./abs(V))
        v_norm = div(v, abs(v))

        diagVsource = spdiag(v[source_idxs])
        diagIsource = spdiag(i_source)
        diagVtarget = spdiag(v[target_idxs])
        diagItarget = spdiag(i_target)
        diagV = spdiag(v)
        diagVnorm = spdiag(v_norm)

        br_idx = range(n_branch)
        size = (n_branch, n_bus)
        # Partial derivative of S w.r.t voltage phase angle.
        dSf_dVa = j * (conj(diagIsource) *
            spmatrix(v[source_idxs], br_idx, source_idxs, size) - \
            diagVsource * conj(Ysrc * diagV))

        dSt_dVa = j * (conj(diagItarget) *
            spmatrix(v[target_idxs], br_idx, target_idxs, size) - \
            diagVtarget * conj(Ytgt * diagV))

        # Partial derivative of S w.r.t. voltage amplitude.
        dSf_dVm = diagVsource * conj(Ysrc * diagVnorm) + conj(diagIsource) * \
            spmatrix(v_norm[source_idxs], br_idx, source_idxs, size)

        dSt_dVm = diagVtarget * conj(Ytgt * diagVnorm) + conj(diagItarget) * \
            spmatrix(v_norm[target_idxs], br_idx, target_idxs, size)

        # Compute power flow vectors.
        s_source = mul(v[source_idxs], conj(i_source))
        s_target = mul(v[target_idxs], conj(i_target))

        return dSf_dVa, dSt_dVa, dSf_dVm, dSt_dVm, s_source, s_target

    #--------------------------------------------------------------------------
    #  Partial derivative of apparent power flow w.r.t voltage:
    #--------------------------------------------------------------------------

    def dAbr_dV(self, dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, s_source, s_target):
        """ Computes the partial derivatives of apparent power flow w.r.t
            voltage.
        """
        # Compute apparent powers.
        a_source = abs(s_source)
        a_target = abs(s_target)

        # Compute partial derivative of apparent power w.r.t active and
        # reactive power flows.  Partial derivative must equal 1 for lines with
        # zero flow to avoid division by zero errors (1 comes from L'Hopital).
        p_source = div(s_source.real(), map(zero2one, a_source))
        q_source = div(s_target.imag(), map(zero2one, a_source))
        p_target = div(s_target.real(), map(zero2one, a_target))
        q_target = div(s_target.imag(), map(zero2one, a_target))

        dAf_dPf = spdiag(p_source)
        dAf_dQf = spdiag(q_source)
        dAt_dPt = spdiag(p_target)
        dAt_dQt = spdiag(q_target)

        # Partial derivative of apparent power magnitude w.r.t voltage
        # phase angle.
        dAf_dVa = dAf_dPf * dSf_dVa.real() + dAf_dQf * dSf_dVa.imag()
        dAt_dVa = dAt_dPt * dSt_dVa.real() + dAt_dQt * dSt_dVa.imag()
        # Partial derivative of apparent power magnitude w.r.t. voltage
        # amplitude.
        dAf_dVm = dAf_dPf * dSf_dVm.real() + dAf_dQf * dSf_dVm.imag()
        dAt_dVm = dAt_dPt * dSt_dVm.real() + dAt_dQt * dSt_dVm.imag()

        return dAf_dVa, dAt_dVa, dAf_dVm, dAt_dVm

    #--------------------------------------------------------------------------
    #  "Serializable" interface:
    #--------------------------------------------------------------------------

    def save_matpower(self, fd):
        """ Serialize the case as a MATPOWER data file.
        """
        from pylon.readwrite import MATPOWERWriter
        MATPOWERWriter().write(self, fd)


    @classmethod
    def load_matpower(cls, fd):
        """ Returns a case from the given MATPOWER file object.
        """
        from pylon.readwrite import MATPOWERReader
        return MATPOWERReader().read(fd)


    def save_psse(self, fd):
        raise NotImplementedError


    @classmethod
    def load_psse(cls, fd):
        """ Returns a case from the given PSS/E file object.
        """
        from pylon.readwrite import PSSEReader
        return PSSEReader().read(fd)


    def save_psat(self, fd):
        raise NotImplementedError


    @classmethod
    def load_psat(cls, fd):
        """ Returns a case object from the given PSAT data file.
        """
        from pylon.readwrite import PSATReader
        return PSATReader().read(fd)


    def save_rest(self, fd):
        """ Save a reStructuredText representation of the case.
        """
        from pylon.readwrite import ReSTWriter
        ReSTWriter().write(self, fd)


    def save_csv(self, fd):
        """ Saves the case as a series of Comma-Separated Values.
        """
        from pylon.readwrite import CSVWriter
        CSVWriter().write(self, fd)


    def save_excel(self, fd):
        """ Saves the case as an Excel spreadsheet.
        """
        from pylon.readwrite.excel_writer import ExcelWriter
        ExcelWriter().write(self, fd)


    def save_dot(self, fd):
        """ Saves a representation of the case in the Graphviz DOT language.
        """
        from pylon.readwrite import DotWriter
        DotWriter().write(self, fd)

#------------------------------------------------------------------------------
#  "Bus" class:
#------------------------------------------------------------------------------

class Bus(Named):
    """ Defines a power system bus node.
    """

    def __init__(self, name=None, type="PQ", v_base=100.0,
            v_magnitude_guess=1.0, v_angle_guess=0.0, v_max=1.1, v_min=0.9,
            p_demand=0.0, q_demand=0.0, g_shunt=0.0, b_shunt=0.0):
        """ Initialises a new Bus instance.
        """
        # Unique name.
        self.name = name

        # Bus type: 'PQ', 'PV', 'ref' and 'isolated' (default: 'PQ')
        self.type = type

        # Base voltage
        self.v_base = v_base

        # Voltage magnitude initial guess (pu).
        self.v_magnitude_guess = v_magnitude_guess
        # Voltage angle initial guess (degrees).
        self.v_angle_guess = v_angle_guess

        # Maximum voltage magnitude (pu).
        self.v_max = v_max
        # Minimum voltage magnitude (pu).
        self.v_min = v_min

        # Total fixed active power load at this bus.
        self.p_demand = p_demand
        # Total fixed reactive power load at this bus.
        self.q_demand = q_demand

        # Shunt conductance (MW (demanded) at V = 1.0 p.u.).
        self.g_shunt = g_shunt
        # Shunt susceptance (MVAr (injected) at V = 1.0 p.u.).
        self.b_shunt = b_shunt

        # Generators defined by their active power and voltage.
#        if generators is None:
#            self.generators = []
#        else:
#            self.generators = generators

        # Loads that specify real and reactive power demand.
#        if loads is None:
#            self.loads = []
#        else:
#            self.loads = loads

        # Voltage magnitude, typically determined by a routine.
        self.v_magnitude = 0.0
        # Voltage angle, typically determined by a routine.
        self.v_angle = 0.0

        # Lambda (GBP/MWh).
        self.p_lambda = 0.0
        # Lambda (GBP/MVAr-hr).
        self.q_lambda = 0.0

        # Lagrangian multiplier for voltage constraint.
        self.mu_vmin = 0.0
        self.mu_vmax = 0.0

#    @property
#    def mode(self):
#        """ Bus mode may be 'pv', 'pq' or 'slack'.
#        """
#        if self.slack:
#            return "slack"
#        elif self.generators:
#            for g in self.generators:
#                if g.q_limited:
#                    return "pq"
#            return "pv"
#        else:
#            return "pq"

#    @property
#    def p_supply(self):
#        """ Total active power generation capacity.
#        """
#        return sum([g.p for g in self.generators])

#    @property
#    def p_demand(self):
#        """ Total active power load.
#        """
#        return sum([l.p for l in self.loads])

#    @property
#    def p_surplus(self):
#        """ Supply and demand difference.
#        """
#        return self.p_supply - self.p_demand

#    @property
#    def q_supply(self):
#        """ Total reactive power generation capacity.
#        """
#        return sum([g.q for g in self.generators])

#    @property
#    def q_demand(self):
#        """ Total reactive power load.
#        """
#        return sum([l.q for l in self.loads])

#    @property
#    def q_surplus(self):
#        """ Supply and demand difference.
#        """
#        return self.q_supply - self.q_demand

#------------------------------------------------------------------------------
#  "Branch" class:
#------------------------------------------------------------------------------

class Branch(Named):
    """ Defines a case edge that links two Bus objects.
    """

    def __init__(self, source_bus, target_bus, name=None, online=True, r=0.001,
            x=0.001, b=0.001, s_max=2.0, ratio=1.0, phase_shift=0.0):
        """ Initialises a new Branch instance.
        """
        # Source/from/start bus.
        self.source_bus = source_bus
#        self.source_bus_idx = 0
        # Target/to/end bus.
        self.target_bus = target_bus
#        self.target_bus_idx = 0

        # Unique name.
        self.name = name
        # Is the branch in service?
        self.online = online
        # Positive sequence resistance (pu).
        self.r = r
        # Positive sequence reactance (pu).
        self.x = x
        # Total positive sequence line charging susceptance (pu).
        self.b = b
        # General purpose maximum MVA rating (MVA).
        self.s_max = s_max
        # Transformer off nominal turns ratio.
        self.ratio = ratio
        # Phase shift angle (degrees).
        self.phase_shift = phase_shift

        # Power flow results --------------------------------------------------

        # Active power injected at the source bus (MW).
        self.p_source = 0.0
        # Active power injected at the target bus (MW).
        self.p_target = 0.0
        # Reactive power injected at the source bus (MVAr).
        self.q_source = 0.0
        # Reactive power injected at the target bus (MVAr).
        self.q_target = 0.0

        # |S_source| mu.
        self.mu_s_source = 0.0
        # |S_target| mu.
        self.mu_s_target = 0.0

    @property
    def mode(self):
        """ Branch mode may be 'line' or 'transformer'.
        """
        if self.source_bus.v_magnitude == self.target_bus.v_magnitude:
            return "line"
        else:
            return "transformer"

    @property
    def p_losses(self):
        """ Active power losses.
        """
        return self.p_source - self.p_target

    @property
    def q_losses(self):
        """ Reactive power losses.
        """
        return self.q_source - self.q_target

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(Named):
    """ Defines a power system generator component. Fixes voltage magnitude
        and active power injected at parent bus. Or when at it's reactive
        power limit fixes active and reactive power injected at parent bus.
    """

    def __init__(self, bus, name=None, online=True, base_mva=100.0, p=100.0,
            p_max=200.0, p_min=0.0, v_magnitude=1.0, q=0.0, q_max=30.0,
            q_min=-30.0, pwl_points=None, cost_coeffs=None,
            rate_up=1.0, rate_down=1.0, min_up=0,
            min_down=0, initial_up=1, initial_down=0):
        """ Initialises a new Generator instance.
        """
        # Busbar to which the generator is connected.
        self.bus = bus

        # Unique name.
        self.name = name

        # Is the generator in service?
        self.online = online

        # Machine MVA base.
        self.base_mva = base_mva

        # Active power output (MW).
        self.p = p
        # Maximum active power output (MW).
        self.p_max = p_max
        self.rated_pmax = p_max
        # Minimum active power output (MW).
        self.p_min = p_min
        self.rated_pmin = p_min

        # Voltage magnitude setpoint (pu).
        self.v_magnitude = v_magnitude

        # Reactive power output (MVAr).
        self.q = q
        # Maximum reactive power (MVAr).
        self.q_max = q_max
        # Minimum reactive power (MVAr).
        self.q_min = q_min

        # Maximum active power output bid. Used in OPF routines. Should be less
        # than or equal to p_max.
#        if p_max_bid is None:
#            self.p_max_bid = p_max
#        else:
#            self.p_max_bid = 0.0
        # Minimum active power bid. Used in OPF routines. Should be greater
        # than or equal to p_min.
#        if p_min_bid is None:
#            self.p_min_bid = p_min
#        else:
#            self.p_min_bid = 0.0

#        # Start up cost.
#        self.c_startup = c_startup
#        # Shut down cost.
#        self.c_shutdown = c_shutdown

        # Generator cost model: 'poly' or 'pwl' (default: 'poly')
        if pwl_points is not None:
            self.cost_model = "pwl"
        elif cost_coeffs is not None:
            self.cost_model = "poly"
        else:
            self.cost_model = "pwl"

        # Polynomial cost curve coefficients.
        # (a, b, c) relates to: cost = c*p**3 + b*p**2 + a*p.
        if cost_coeffs:
            self.cost_coeffs = cost_coeffs
        else:
            self.cost_coeffs = (0.01, 0.1, 10.0)
        # Piecewise linear cost segment points.
        if pwl_points:
            self.pwl_points = pwl_points
        else:
            self.pwl_points = [(0.0, 0.0), (1.0, 10.0)]

        # Ramp up rate (p.u./h).
        self.rate_up = rate_up
        # Ramp down rate (p.u./h).
        self.rate_down = rate_down
        # Minimum running time (h).

        self.min_up = min_up
        # Minimum shut down time (h).
        self.min_down = min_down

        # Initial number of periods up.
        self.initial_up = initial_up
        # Initial number of periods down.
        self.initial_down = initial_down

        # The output power that the Generator is despatched to generate
        # as a result of solving the OPF problem.
#        self.p_despatch = 0.0

        self.mu_pmin = 0.0
        self.mu_pmax = 0.0

    @property
    def q_limited(self):
        """ Is the machine at it's limit of reactive power?
        """
        if (self.q >= self.q_max) or (self.q <= self.q_min):
            return True
        else:
            return False

    @property
    def mode(self):
        """ Does the machine represent a generator or a despatchable load.
        """
        raise DeprecationWarning, "Use .is_load instead."

        if 0 <= self.p_min < self.p_max:
            return "generator"
        elif self.p_min < self.p_max <= 0.0:
            return "vload"
        else:
            return "unknown"

    @property
    def p_cost(self):
        """ Active power cost at the current output.
        """
        return self.total_cost(self.p)

    @property
    def is_load(self):
        """ Returns true if the generator if a dispatchable load. This may
            need to be revised to allow sensible specification of both elastic
            demand and pumped storage units.
        """
        return self.p_min < 0.0 and self.p_max == 0.0


    def total_cost(self, p):
        """ Computes total cost for the generator at the given output level.
        """
        if self.cost_model == "pwl":
            n_segments = len(self.pwl_points) - 1
            # Iterate over the piece-wise linear segments.
            for i in range(n_segments):
                x1, y1 = self.pwl_points[i]
                x2, y2 = self.pwl_points[(i + 1)]

                m = (y2 - y1) / (x2 - x1)
                c = y1 - m * x1

                result = m*p + c

                if x1 <= p <= x2:
                    break
#            else:
##                raise ValueError, "Value [%f] outwith pwl cost curve." % p
#                # Use the last segment for values outwith the cost curve.
#                result = m*p + c

        elif self.cost_model == "poly":
            result = self.cost_coeffs[-1]

            for i in range(1, len(self.cost_coeffs)):
                result += self.cost_coeffs[-(i + 1)] * p**i

        else:
            raise ValueError

        return result


    def poly_to_pwl(self, n_points=10):
        """ Sets the piece-wise linear cost attribute, converting the
            polynomial cost variable by evaluating at zero and then at
            n_points evenly spaced points between p_min and p_max.
        """
        p_min = self.p_min
        p_max = self.p_max
        self.pwl_points = []
        # Ensure that the cost model is polynomial for calling total_cost.
        self.cost_model = "poly"

        if p_min > 0.0:
            # Make the first segment go from the origin to p_min.
            step = (p_max - p_min) / (n_points - 2)

            y0 = self.total_cost(0.0)
            self.pwl_points.append((0.0, y0))

            x = p_min
            n_points -= 1
        else:
            step = (p_max - p_min) / (n_points - 1)
            x = 0.0

        for _ in range(n_points):
            y = self.total_cost(x)
            self.pwl_points.append((x, y))
            x += step

        # Change the cost model.
        self.cost_model = "pwl"


    def get_offers(self, n_points=6):
        """ Returns quantity and price offers created from the cost function.
        """
        from pylon.pyreto.smart_market import Offer

        qtyprc = self._get_qtyprc(n_points)

        return [Offer(self, qty, prc) for qty, prc in qtyprc]


    def get_bids(self, n_points=6):
        """ Returns quantity and price bids created from the cost function.
        """
        from pylon.pyreto.smart_market import Bid

        qtyprc = self._get_qtyprc(n_points)

        return [Bid(self, qty, prc) for qty, prc in qtyprc]


    def _get_qtyprc(self, n_points=6):
        """ Returns a list of tuples of the form (qty, prc) created from the
            cost function.  If the cost function is polynomial it will be
            converted to piece-wise linear using poly_to_pwl(n_points).
        """
        if self.cost_model == "poly":
            # Convert polynomial cost function to piece-wise linear.
            self.poly_to_pwl(n_points)

        n_segments = len(self.pwl_points) - 1

        qtyprc = []

        for i in range(n_segments):
            x1, y1 = self.pwl_points[i]
            x2, y2 = self.pwl_points[(i + 1)]

            quantity = x2 - x1
            price = (y2 - y1) / quantity

            qtyprc.append((quantity, price))

        return qtyprc


    def adjust_limits(self):
        """ Sets the active power limits, 'p_max' and 'p_min', according to the
            pwl cost function points.
        """
        if not self.is_load:
            self.p_max = max([point[0] for point in self.pwl_points])
        else:
            p_min = min([point[0] for point in self.pwl_points])
            if self.rated_pmin <= p_min <= self.rated_pmax:
                self.q_min = self.q_min * p_min / self.rated_pmin
                self.q_max = self.q_max * p_min / self.rated_pmin
            else:
                logger.error("Active power limit outwith rating.")
            self.p_min = p_min


    def reset_limits(self):
        """ Resets active power limits to the generator ratings.
        """
        self.p_max = self.rated_pmax
        self.p_min = self.rated_pmin


    def offers_to_pwl(self, offers):
        """ Updates the piece-wise linear total cost function using the given
            offer blocks.

            @see: matpower3.2/extras/smartmarket/off2case.m
        """
        # Only apply offers associated with this generator.
        g_offers = [offer for offer in offers if offer.generator == self]

        # Fliter out zero quantity offers.
        valid = [offr for offr in g_offers if round(offr.quantity, 4) > 0.0]

        # Ignore withheld offers.
        valid = [offer for offer in valid if not offer.withheld]

        if valid:
            self.pwl_points = self._offbids_to_points(valid)

            # FIXME: Convert reactive power bids into piecewise linear segments.
            # FIXME: Set all reactive costs to zero if not provided.

            self.cost_model = "pwl"
            self.online = True
        elif not self.is_load:
            logger.info("No valid offers for generator, shutting down.")
            self.online = False
        else:
            logger.info("No valid offers for generator.")


    def bids_to_pwl(self, bids):
        """ Updates the piece-wise linear total cost function using the given
            bid blocks.

            @see: matpower3.2/extras/smartmarket/off2case.m
        """
        # Apply only those bids associated with this dispatchable load.
        vl_bids = [bid for bid in bids if bid.vload == self]

        # Filter out zero quantity bids.
        valid_bids = [bid for bid in vl_bids if round(bid.quantity, 4) > 0.0]

        # Ignore withheld offers.
        valid_bids = [bid for bid in valid_bids if not bid.withheld]

        if valid_bids:
            points = self._offbids_to_points(valid_bids)

            # Shift the points to represent bids by subtracting the maximum value
            # from each.
            x_end, y_end = points[-1]
            points = [(pnt[0] - x_end, pnt[1] - y_end) for pnt in points]

            self.pwl_points = points
            # FIXME: Convert reactive power bids into piecewise linear segments.
            # FIXME: Set all reactive costs to zero if not provided.
            self.cost_model = "pwl"
        elif self.is_load:
            logger.info("No valid bids for dispatchable load, shutting down.")
            self.online = False


    def _offbids_to_points(self, offbids):
        """ Returns a list of points for a piece-wise linear function from the
            given offer/bid blocks.
        """
        # Sort offers/bids by price in ascending order.
        offbids.sort(key=lambda x: x.price)

        points = [(0.0, 0.0)]
        # Form piece-wise linear total cost function.
        for i, offbid in enumerate(offbids):
            x1, y1 = points[i]
            x2 = points[i][0] + offbid.quantity # MW.
            m = offbid.price # $/MWh
            y2 = m * (x2 - x1) + y1
            points.append((x2, y2))

        n_segs = len(points) - 1
        plural = "" if n_segs == 1 else "s"
        logger.info("Creating pwl cost function with %d segment%s [%s]." %
                    (n_segs, plural, points))

        return points

#------------------------------------------------------------------------------
#  "Load" class:
#------------------------------------------------------------------------------

#class Load(Named):
#    """ Defines a PQ load component.
#    """
#
#    def __init__(self, name=None, online=True, p=1.0, q=0.1, p_max=1.0,
#            p_min=0.0, p_profile=None):
#        """ Initialises a new Load instance.
#        """
#        # Is the load in service?
#        self.online = online
#        # Active power demand (MW).
#        self.p = p
#        # Reactive power demand (MVAr).
#        self.q = q
#        # Maximum active power (MW).
#        self.p_max = p_max
#        # Minimum active power (MW).
#        self.p_min = p_min
#
#        self._p_profile = []
#        # Active power profile (%).
#        if p_profile is None:
#            self.p_profile = [100.0]
#        else:
#            self.p_profile = p_profile
#
#        self._p_cycle = cycle(self.p_profile)
#
#
#    def __getstate__(self):
#        """ Prevents the 'cycle' from being pickled.
#        """
#        result = self.__dict__.copy()
#        del result['_p_cycle']
#        return result
#
#
#    def __setstate__(self, dict):
#        """ Sets the load profile cycle when unpickling.
#        """
#        self.__dict__ = dict
#        self._p_cycle = cycle(self.p_profile)
#
#    @property
#    def p_profiled(self):
#        """ Active power demand scaled between 'p_max' and 'p_min'
#            according to the 'p_profile' percentages.
#        """
#        percent = self._p_cycle.next()
#        return (percent / 100) * (self.p_max - self.p_min)
#
#
#    def get_p_profile(self):
#        """ Returns the active power profile for the load.
#        """
#        return self._p_profile
#
#
#    def set_p_profile(self, profile):
#        """ Sets the active power profile, updating the cycle iterator.
#        """
#        self._p_cycle = cycle(profile)
#        self._p_profile = profile
#
#
#    p_profile = property(get_p_profile, set_p_profile)

#------------------------------------------------------------------------------
#  "CaseReport" class:
#------------------------------------------------------------------------------

class CaseReport(object):
    """ Defines a statistical case report.
    """

    def __init__(self, case):
        """ Initialises a CaseReport instance.
        """
        self.case = case


    @property
    def n_buses(self):
        """ Total number of buses.
        """
        return len(self.case.buses)


    @property
    def n_connected_buses(self):
        """ Total number of non-islanded buses.
        """
        return len(self.case.connected_buses)


    @property
    def n_generators(self):
        """ Total number of generators.
        """
        return len(self.case.generators)


    @property
    def n_online_generators(self):
        """ Total number of generators in service.
        """
        return len(self.case.online_generators)


    @property
    def committed_generators(self):
        """ Generators that have been despatched.
        """
        return [g for g in self.case.generators if g.p > 0.0]


    @property
    def n_committed_generators(self):
        """ Number of committed generators.
        """
        return len(self.committed_generators)


    @property
    def n_loads(self):
        """ Total number of loads.
        """
        return self.n_fixed + self.n_despatchable


#    @property
#    def n_online_loads(self):
#        """ Number of active loads.
#        """
#        return len(self.case.online_loads)


    @property
    def fixed(self):
        """ Fixed loads.
        """
        return self.case.all_loads


    @property
    def n_fixed(self):
        """ Total number of fixed loads.
        """
        return len([bus for bus in self.case.buses if bus.p_demand > 0.0])


    @property
    def despatchable(self):
        """ Generators with negative output.
        """
        return [vl for vl in self.case.generators if vl.is_load]


    @property
    def n_despatchable(self):
        """ Number of despatchable loads.
        """
        return len(self.despatchable)

    # Branch property getters -------------------------------------------------

    @property
    def n_branches(self):
        """ Total number of branches.
        """
        return len(self.case.branches)


    @property
    def n_online_branches(self):
        """ Total number of active branches.
        """
        return len(self.case.online_branches)


    @property
    def transformers(self):
        """ Branches operating as transformers.
        """
        return [e for e in self.case.branches if e.mode == "transformer"]


    @property
    def n_transformers(self):
        """ Total number of transformers.
        """
        return len(self.transformers)

    # "How much?" property getters --------------------------------------------

    @property
    def total_gen_capacity(self):
        """ Total generation capacity.
        """
        base_mva = self.case.base_mva
        p = sum([g.p for g in self.case.generators])
        q = sum([g.q for g in self.case.generators])

        return complex(p, q)


    @property
    def online_capacity(self):
        """ Total online generation capacity.
        """
        p = sum([g.p for g in self.case.online_generators])
        q = sum([g.q for g in self.case.online_generators])

        return complex(p, q)


    @property
    def generation_actual(self):
        """ Total despatched generation.
        """
        p = sum([g.p for g in self.case.generators])
        q = sum([g.q for g in self.case.generators])

        return complex(p, q)


    @property
    def load(self):
        """ Total system load.
        """
        return self.fixed_load + self.despatchable_load


    @property
    def fixed_load(self):
        """ Total fixed system load.
        """
        p = sum([bus.p_demand for bus in self.case.buses])
        q = sum([bus.q_demand for bus in self.case.buses])

        return complex(p, q)


    @property
    def despatchable_load(self):
        """ Total volume of despatchable load.
        """
        p = sum([vl.p for vl in self.despatchable])
        q = sum([vl.q for vl in self.despatchable])

        return complex(p, q)


#    @property
#    def shunt_injection(self):
#        """ Total system shunt injection.
#        """
#        return 0.0 + 0.0j # FIXME: Implement shunts


    @property
    def losses(self):
        """ Total system losses.
        """
        p = sum([e.p_losses for e in self.case.branches])
        q = sum([e.q_losses for e in self.case.branches])

        return complex(p, q)


    @property
    def branch_charging(self):
        """ Total branch charging injections.
        """
        return 0.0 + 0.0j # FIXME: Calculate branch charging injections


#    @property
#    def total_inter_tie_flow(self):
#        """ Total inter-tie flow.
#        """
#        return 0.0 + 0.0j # FIXME: Implement inter-ties


    @property
    def min_voltage_amplitude(self):
        """ Minimum bus voltage amplitude.
        """
        if self.case.buses:
#            l.index(min(l))
            return min([bus.v_magnitude for bus in self.case.buses])
        else:
            return 0.0


    @property
    def max_voltage_amplitude(self):
        """ Maximum bus voltage amplitude.
        """
        if self.case.buses:
            return max([bus.v_magnitude for bus in self.case.buses])
        else:
            return 0.0


    @property
    def min_voltage_phase(self):
        """ Minimum bus voltage phase angle.
        """
        if self.case.buses:
            return min([bus.v_angle for bus in self.case.buses])
        else:
            return 0.0


    @property
    def max_voltage_phase(self):
        """ Maximum bus voltage phase angle.
        """
        if self.case.buses:
            return max([bus.v_angle for bus in self.case.buses])
        else:
            return 0.0


    @property
    def min_p_lambda(self):
        """ Minimum bus active power Lagrangian multiplier.
        """
        if self.case.buses:
            return min([v.p_lambda for v in self.case.buses])
        else:
            return 0.0


    @property
    def max_p_lambda(self):
        """ Maximum bus active power Lagrangian multiplier.
        """
        if self.case.buses:
            return max([v.p_lambda for v in self.case.buses])
        else:
            return 0.0


    @property
    def min_q_lambda(self):
        """ Minimum bus reactive power Lagrangian multiplier.
        """
        if self.case.buses:
            return min([v.q_lambda for v in self.case.buses])
        else:
            return 0.0


    @property
    def max_q_lambda(self):
        """ Maximum bus reactive power Lagrangian multiplier.
        """
        if self.case.buses:
            return max([v.q_lambda for v in self.case.buses])
        else:
            return 0.0

# EOF -------------------------------------------------------------------------
