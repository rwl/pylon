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

""" Defines the Pylon network model.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from math import pi

from util import Named, Serializable

from cvxopt.base import matrix, spmatrix, spdiag, sparse, exp, mul, div

from util import conj, zero2one

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

PV = "PV"
PQ = "PQ"
REFERENCE = "ref"
ISOLATED = "isolated"
LINE = "line"
TRANSFORMER = "transformer"
GENERATOR = "generator"
DISPATCHABLE_LOAD = "vload"
POLYNOMIAL = "poly"
PW_LINEAR = "pwl"

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
#        if self.branches:
#            from_buses = [e.from_bus for e in self.branches]
#            to_buses = [e.to_bus for e in self.branches]
#
#            return [v for v in self.buses if v in from_buses + to_buses]
#        else:
#            return self.buses[:1]

        return [bus for bus in self.buses if bus.type != ISOLATED]


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


    @property
    def s_bus(self):
        """ Net complex bus power injection vector in p.u.
        """
        s = matrix([complex(self.p_surplus(v),
                            self.q_surplus(v)) / self.base_mva
                            for v in self.buses])
        return s

    #--------------------------------------------------------------------------
    #  Bus injections:
    #--------------------------------------------------------------------------

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
        return self.q_supply(bus) - self.q_demand(bus)

    #--------------------------------------------------------------------------
    #  Admittance matrix:
    #--------------------------------------------------------------------------

    def getYbus(self, buses=None, branches=None, bus_shunts=True,
                line_shunts=True, tap_positions=True, line_resistance=True,
                phase_shift=True):
        """ Returns the bus and branch admittance matrices, Yf and Yt, such
            that Yf * V is the vector of complex branch currents injected at
            each branch's "from" bus.

            References:
                Ray Zimmerman, "makeYbus.m", MATPOWER, PSERC Cornell,
                http://www.pserc.cornell.edu/matpower/, version 1.8, June 2007
        """
        buses = self.buses if buses is None else buses
        branches = self.branches if branches is None else branches

        nb = len(buses)
        nl = len(branches)

        online = matrix([e.online for e in branches])

        #----------------------------------------------------------------------
        #  Series admittance.
        #----------------------------------------------------------------------

        if line_resistance:
            r = matrix([e.r for e in branches])
        else:
            r = matrix(0.0, (nl, 1)) # Zero out line resistance.
        x = matrix([e.x for e in branches])

        Ys = div(online, (r + 1j * x))

        #----------------------------------------------------------------------
        #  Line charging susceptance.
        #----------------------------------------------------------------------

        if line_shunts:
            b = matrix([e.b for e in branches])
        else:
            b = matrix(0.0, (nl, 1)) # Zero out line charging shunts.

        Bc = mul(online, b)

        #----------------------------------------------------------------------
        #  Transformer tap ratios.
        #----------------------------------------------------------------------

        tap = matrix(1.0, (nl, 1), tc="d") # Default tap ratio = 1.0.

        if tap_positions:
            # Indices of branches with non-zero tap ratio.
            idxs = [i for i, e in enumerate(branches) if e.ratio != 0.0]
            # Transformer off nominal turns ratio ( = 0 for lines ) (taps at
            # "from" bus, impedance at 'to' bus, i.e. ratio = Vf / Vt)"
            ratio = matrix([e.ratio for e in branches])
            # Set non-zero tap ratios.
            tap[idxs] = ratio[idxs]

        #----------------------------------------------------------------------
        #  Phase shifters.
        #----------------------------------------------------------------------

        # Convert branch attribute in degrees to radians.
        if phase_shift:
            shift = matrix([e.phase_shift * pi / 180.0 for e in branches])
        else:
            phase_shift = matrix(0.0, (nl, 1))

        tap = mul(tap, exp(1j * shift))

        #----------------------------------------------------------------------
        #  Branch admittance matrix elements.
        #----------------------------------------------------------------------

        #  | If |   | Yff  Yft |   | Vf |
        #  |    | = |          | * |    |
        #  | It |   | Ytf  Ytt |   | Vt |

        Ytt = Ys + 1j * Bc / 2.0
        Yff = div(Ytt, (mul(tap, conj(tap))))
        Yft = div(-Ys, conj(tap))
        Ytf = div(-Ys, tap)

        #----------------------------------------------------------------------
        #  Shunt admittance.
        #----------------------------------------------------------------------

        # Ysh = (bus(:, GS) + j * bus(:, BS)) / baseMVA;
        if bus_shunts:
            g_shunt = matrix([v.g_shunt for v in buses])
            b_shunt = matrix([v.b_shunt for v in buses])
        else:
            g_shunt = matrix(0.0, (nb, 1)) # Zero out shunts at buses.
            b_shunt = matrix(0.0, (nb, 1))

        Ysh = (g_shunt + 1j * b_shunt) / self.base_mva

        #----------------------------------------------------------------------
        #  Connection matrices.
        #----------------------------------------------------------------------

        f = matrix([self.buses.index(e.from_bus) for e in branches])
        t = matrix([self.buses.index(e.to_bus) for e in branches])
        Cf = spmatrix(1.0, f, range(nl))
        Ct = spmatrix(1.0, t, range(nl))

        # Build bus admittance matrix
        # Ybus = spdiags(Ysh, 0, nb, nb) + ... %% shunt admittance
        # Cf * spdiags(Yff, 0, nl, nl) * Cf' + ...
        # Cf * spdiags(Yft, 0, nl, nl) * Ct' + ...
        # Ct * spdiags(Ytf, 0, nl, nl) * Cf' + ...
        # Ct * spdiags(Ytt, 0, nl, nl) * Ct';

#        ff = Cf * spdiag(Yff) * Cf.H
#        ft = Cf * spdiag(Yft) * Ct.H
#        tf = Ct * spdiag(Ytf) * Cf.H
#        tt = Ct * spdiag(Ytt) * Ct.H

        # Resize otherwise all-zero rows/columns are lost.
#        Ybus = spdiag(Ysh) + \
#            spmatrix(ff.V, ff.I, ff.J, (nb, nb), tc="z") + \
#            spmatrix(ft.V, ft.I, ft.J, (nb, nb), tc="z") + \
#            spmatrix(tf.V, tf.I, tf.J, (nb, nb), tc="z") + \
#            spmatrix(tt.V, tt.I, tt.J, (nb, nb), tc="z")

        i = matrix([range(nl), range(nl)]).H
        j = matrix([f, t])
        Yf = spmatrix(sparse([Yff, Yft]), i, j, (nl, nb))
        Yt = spmatrix(sparse([Ytf, Ytt]), i, j, (nl, nb))

        # Branch admittances plus shunt admittances.
        Ybus = Cf.H * Yf + Ct.H * Yt + spdiag(Ysh)
        assert Ybus.size == (nb, nb)

        return Ybus, Yf, Yt

    Y = property(getYbus)

    #--------------------------------------------------------------------------
    #  Susceptance matrix:
    #--------------------------------------------------------------------------

    def makeBdc(self, buses=None, branches=None):
        """ Returns the sparse susceptance matrices and phase shift injection
            vectors needed for a DC power flow.

            The bus real power injections are related to bus voltage angles by
                P = Bbus * Va + Pbusinj

            The real power flows at the from end the lines are related to the
            bus voltage angles by
                Pf = Bf * Va + Pfinj

            | Pf |   | Bff  Bft |   | Vaf |   | Pfinj |
            |    | = |          | * |     | + |       |
            | Pt |   | Btf  Btt |   | Vat |   | Ptinj |

            References:
                Ray Zimmerman, "makeBdc.m", MATPOWER, PSERC Cornell,
                http://www.pserc.cornell.edu/matpower/, version 1.10, June 2007
        """
        buses = self.buses if buses is None else buses
        branches = self.branches if branches is None else branches

        nb = len(buses)
        nl = len(branches)

        # Ones at in-service branches.
        online = matrix([br.online for br in branches])
        # Series susceptance.
        b = div(online, matrix([br.x for br in branches]))

        # Default tap ratio = 1.0.
        tap = matrix(1.0, (nl, 1))
        # Transformer off nominal turns ratio (equals 0 for lines) (taps at
        # "from" bus, impedance at 'to' bus, i.e. ratio = Vsrc / Vtgt)
        for i, branch in enumerate(branches):
            if branch.ratio != 0.0:
                tap[i] = branch.ratio
        b = div(b, tap)

        f = matrix([buses.index(br.from_bus) for br in branches])
        t = matrix([buses.index(br.to_bus) for br in branches])
        i = matrix([matrix(range(nl)).T, matrix(range(nl)).T])
        one = matrix(1.0, (nl, 1))
        Cft = spmatrix(matrix([one, -one]), i, matrix([f, t]), (nl, nb))
#        Cf = spmatrix(1.0, f, range(nl), (nb, nl))
#        Ct = spmatrix(1.0, t, range(nl), (nb, nl))

#        ff = Cf * spdiag(b) * Cf.H
#        ft = Cf * spdiag(-b) * Ct.H
#        tf = Ct * spdiag(-b) * Cf.H
#        tt = Ct * spdiag(b) * Ct.H

        # Resize otherwise all-zero rows/columns are lost.
#        B = spmatrix(ff.V, ff.I, ff.J, (nb, nb), tc="d") + \
#            spmatrix(ft.V, ft.I, ft.J, (nb, nb), tc="d") + \
#            spmatrix(tf.V, tf.I, tf.J, (nb, nb), tc="d") + \
#            spmatrix(tt.V, tt.I, tt.J, (nb, nb), tc="d")

        # Build Bsrc such that Bsrc * Va is the vector of real branch powers
        # injected at each branch's "from" bus.
        Bf = spmatrix(matrix([b, -b]), i, matrix([f, t]), (nl, nb))

        Bbus = Cft.H * Bf

        # Build phase shift injection vectors.
        shift = matrix([br.phase_shift * pi / 180.0 for br in branches])
        Pfinj = mul(b, shift)
        #Ptinj = -Pfinj
        # Pbusinj = Cf * Pfinj + Ct * Ptinj
        Pbusinj = Cft.H * Pfinj

        return Bbus, Bf, Pbusinj, Pfinj

    Bdc = property(makeBdc)

    #--------------------------------------------------------------------------
    #  Partial derivative of power injection w.r.t. voltage:
    #--------------------------------------------------------------------------

    def dSbus_dV(self, Y, V):
        """ Computes the partial derivative of power injection w.r.t. voltage.

            References:
                Ray Zimmerman, "dSbus_dV.m", MATPOWER, version 3.2,
                PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
        """
        I = Y * V

        diag_v = spdiag(V)
        diag_i = spdiag(I)
        diag_vnorm = spdiag(div(V, abs(V))) # Element-wise division.

        dS_dVm = diag_v * conj(Y * diag_vnorm) + conj(diag_i) * diag_vnorm
        dS_dVa = 1j * diag_v * conj(diag_i - Y * diag_v)

        return dS_dVm, dS_dVa

    #--------------------------------------------------------------------------
    #  Partial derivatives of branch currents w.r.t. voltage.
    #--------------------------------------------------------------------------

    def dIbr_dV(self, Yf, Yt, V):
        """ Computes partial derivatives of branch currents w.r.t. voltage.

            Ray Zimmerman, "dIbr_dV.m", MATPOWER, version 4.0b1,
            PSERC (Cornell), http://www.pserc.cornell.edu/matpower/
        """
#        nb = len(V)

        Vnorm = div(V, abs(V))
        diagV = spdiag(V)
        diagVnorm = spdiag(Vnorm)
        dIf_dVa = Yf * 1j * diagV
        dIf_dVm = Yf * diagVnorm
        dIt_dVa = Yt * 1j * diagV
        dIt_dVm = Yt * diagVnorm

        # Compute currents.
        If = Yf * V
        It = Yt * V

        return dIf_dVa, dIf_dVm, dIt_dVa, dIt_dVm, If, It

    #--------------------------------------------------------------------------
    #  Partial derivative of branch power flow w.r.t voltage:
    #--------------------------------------------------------------------------

    def dSbr_dV(self, Yf, Yt, V, buses=None, branches=None):
        """ Computes the branch power flow vector and the partial derivative of
            branch power flow w.r.t voltage.
        """
        buses = self.buses if buses is None else buses
        branches = self.branches if branches is None else branches

        nl = len(branches)
        nb = len(V)

        f = matrix([buses.index(l.from_bus) for l in branches])
        t = matrix([buses.index(l.to_bus) for l in branches])

        # Compute currents.
        If = Yf * V
        It = Yt * V

        Vnorm = div(V, abs(V))

        diagVf = spdiag(V[f])
        diagIf = spdiag(If)
        diagVt = spdiag(V[t])
        diagIt = spdiag(It)
        diagV = spdiag(V)
        diagVnorm = spdiag(Vnorm)

        ibr = range(nl)
        size = (nl, nb)
        # Partial derivative of S w.r.t voltage phase angle.
        dSf_dVa = 1j * (conj(diagIf) *
            spmatrix(V[f], ibr, f, size) - diagVf * conj(Yf * diagV))

        dSt_dVa = 1j * (conj(diagIt) *
            spmatrix(V[t], ibr, t, size) - diagVt * conj(Yt * diagV))

        # Partial derivative of S w.r.t. voltage amplitude.
        dSf_dVm = diagVf * conj(Yf * diagVnorm) + conj(diagIf) * \
            spmatrix(Vnorm[f], ibr, f, size)

        dSt_dVm = diagVt * conj(Yt * diagVnorm) + conj(diagIt) * \
            spmatrix(Vnorm[t], ibr, t, size)

        # Compute power flow vectors.
        Sf = mul(V[f], conj(If))
        St = mul(V[t], conj(It))

        return dSf_dVa, dSt_dVa, dSf_dVm, dSt_dVm, Sf, St

    #--------------------------------------------------------------------------
    #  Partial derivative of apparent power flow w.r.t voltage:
    #--------------------------------------------------------------------------

    def dAbr_dV(self, dSf_dVa, dSf_dVm, dSt_dVa, dSt_dVm, Sf, St):
        """ Computes the partial derivatives of apparent power flow w.r.t
            voltage.
        """
        # Compute apparent powers.
        Af = abs(Sf)
        At = abs(St)

        # Compute partial derivative of apparent power w.r.t active and
        # reactive power flows.  Partial derivative must equal 1 for lines with
        # zero flow to avoid division by zero errors (1 comes from L'Hopital).
        Pf = div(Sf.real(), map(zero2one, Af))
        Qf = div(St.imag(), map(zero2one, Af))
        Pt = div(St.real(), map(zero2one, At))
        Qt = div(St.imag(), map(zero2one, At))

        dAf_dPf = spdiag(Pf)
        dAf_dQf = spdiag(Qf)
        dAt_dPt = spdiag(Pt)
        dAt_dQt = spdiag(Qt)

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
    #  Second derivative of power injection w.r.t voltage:
    #--------------------------------------------------------------------------

    def d2Sbus_dV2(self, Ybus, V, lam):
        """ Computes 2nd derivatives of power injection w.r.t. voltage.
        """
        n = len(V)
        Ibus = Ybus * V
        diaglam = spdiag(lam)
        diagV = spdiag(V)

        A = spmatrix(mul(lam, V), range(n), range(n))
        B = Ybus * diagV
        C = A * conj(B)
        D = Ybus.H * diagV
        E = conj(diagV) * (D * diaglam - spmatrix(D*lam, range(n), range(n)))
        F = C - A * spmatrix(conj(Ibus), range(n), range(n))
        G = spmatrix(div(matrix(1.0, (n, 1)), abs(V)), range(n), range(n))

        Haa = E + F
        Hva = 1j * G * (E - F)
        Hav = Hva.T
        Hvv = G * (C + C.T) * G

        return Haa, Hav, Hva, Hvv

    #--------------------------------------------------------------------------
    #  Second derivative of complex branch current w.r.t. voltage:
    #--------------------------------------------------------------------------

    def d2Ibr_dV2(self, Ybr, V, lam):
        """ Computes 2nd derivatives of complex branch current w.r.t. voltage.
        """
        nb = len(V)
        diaginvVm = spdiag(div(matrix(1.0, (nb, 1)), abs(V)))

        Gaa = spdiag(mul(-(Ybr.T * lam), V))
        Gva = -1j * Gaa * diaginvVm
        Gav = Gva
        Gvv = spmatrix([], [], [], (nb, nb))

        return Gaa, Gav, Gva, Gvv

    #--------------------------------------------------------------------------
    #  Second derivative of complex power flow w.r.t. voltage:
    #--------------------------------------------------------------------------

    def d2Sbr_dV2(self, Cbr, Ybr, V, lam):
        """ Computes 2nd derivatives of complex power flow w.r.t. voltage.
        """
        nb = len(V)

        diaglam = spdiag(lam)
        diagV = spdiag(V)

        A = Ybr.H * diaglam * Cbr
        B = conj(diagV) * A * diagV
        D = spdiag(mul((A*V), conj(V)))
        E = spdiag(mul((A.T * conj(V)), V))
        F = B + B.T
        G = spdiag(div(matrix(1.0, (nb, 1)), abs(V)))

        Gaa = F - D - E
        Gva = 1j * G * (B - B.T - D + E)
        Gav = Gva.T
        Gvv = G * F * G

        return Gaa, Gav, Gva, Gvv

    #--------------------------------------------------------------------------
    #  Second derivative of |complex power flow|**2 w.r.t. voltage:
    #--------------------------------------------------------------------------

    def d2ASbr_dV2(self, dSbr_dVa, dSbr_dVm, Sbr, Cbr, Ybr, V, lam):
        """ Computes 2nd derivatives of |complex power flow|**2 w.r.t. V.
        """
        diaglam = spdiag(lam)
        diagSbr_conj = spdiag(conj(Sbr))

        [Saa, Sav, Sva, Svv] = self.d2Sbr_dV2(Cbr, Ybr, V, diagSbr_conj * lam)

        Gaa = 2 * ( Saa + dSbr_dVa.T * diaglam * conj(dSbr_dVa) ).real()
        Gva = 2 * ( Sva + dSbr_dVm.T * diaglam * conj(dSbr_dVa) ).real()
        Gav = 2 * ( Sav + dSbr_dVa.T * diaglam * conj(dSbr_dVm) ).real()
        Gvv = 2 * ( Svv + dSbr_dVm.T * diaglam * conj(dSbr_dVm) ).real()

        return Gaa, Gav, Gva, Gvv

    #--------------------------------------------------------------------------
    #  Second derivative of |complex current|**2 w.r.t. voltage:
    #--------------------------------------------------------------------------

    def d2AIbr_dV2(self, dIbr_dVa, dIbr_dVm, Ibr, Ybr, V, lam):
        """ Computes 2nd derivatives of |complex current|**2 w.r.t. V.
        """
        diaglam = spdiag(lam)
        diagIbr_conj = spdiag(conj(Ibr))

        Iaa, Iav, Iva, Ivv = self.d2Ibr_dV2(Ybr, V, diagIbr_conj * lam)

        Gaa = 2 * ( Iaa + dIbr_dVa.T * diaglam * conj(dIbr_dVa) ).real()
        Gva = 2 * ( Iva + dIbr_dVm.T * diaglam * conj(dIbr_dVa) ).real()
        Gav = 2 * ( Iav + dIbr_dVa.T * diaglam * conj(dIbr_dVm) ).real()
        Gvv = 2 * ( Ivv + dIbr_dVm.T * diaglam * conj(dIbr_dVm) ).real()

        return Gaa, Gav, Gva, Gvv

    #--------------------------------------------------------------------------
    #  Reset case results:
    #--------------------------------------------------------------------------

    def reset(self):
        """ Resets the result variables for all of the case componenets.
        """
        for bus in self.buses:
            bus.reset()
        for branch in self.branches:
            branch.reset()
        for generator in self.generators:
            generator.reset()

    #--------------------------------------------------------------------------
    #  Deactivate isolated branches and generators:
    #--------------------------------------------------------------------------

    def deactivate_isolated(self):
        """ Deactivates branches and generators connected to isolated buses.
        """
        for l in self.branches:
            if (l.from_bus.type == "isolated") or (l.to_bus.type == "isolated"):
                l.online = False
        for g in self.generators:
            if g.bus.type == "isolated":
                g.online = False

    #--------------------------------------------------------------------------
    #  "Serializable" interface:
    #--------------------------------------------------------------------------

    def save_matpower(self, fd):
        """ Serialize the case as a MATPOWER data file.
        """
        from pylon.readwrite import MATPOWERWriter
        MATPOWERWriter(self).write(fd)


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


    def save_rst(self, fd):
        """ Save a reStructuredText representation of the case.
        """
        from pylon.readwrite import ReSTWriter
        ReSTWriter(self).write(fd)


    def save_csv(self, fd):
        """ Saves the case as a series of Comma-Separated Values.
        """
        from pylon.readwrite import CSVWriter
        CSVWriter(self).write(fd)


    def save_excel(self, fd):
        """ Saves the case as an Excel spreadsheet.
        """
        from pylon.readwrite.excel_writer import ExcelWriter
        ExcelWriter(self).write(fd)


    def save_dot(self, fd):
        """ Saves a representation of the case in the Graphviz DOT language.
        """
        from pylon.readwrite import DotWriter
        DotWriter(self).write(fd)

#------------------------------------------------------------------------------
#  "Bus" class:
#------------------------------------------------------------------------------

class Bus(Named):
    """ Defines a power system bus node.
    """

    def __init__(self, name=None, type=PQ, v_base=100.0,
            v_magnitude_guess=1.0, v_angle_guess=0.0, v_max=1.1, v_min=0.9,
            p_demand=0.0, q_demand=0.0, g_shunt=0.0, b_shunt=0.0):
        """ Initialises a new Bus instance.
        """
        # Unique name.
        self.name = name

        # Bus type: 'PQ', 'PV', 'ref' and 'isolated' (default: 'PQ')
        self.type = type

        # Base voltage.
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


    def reset(self):
        """ Resets the result variables.
        """
        self.v_magnitude = 0.0
        self.v_angle = 0.0
        self.p_lambda = 0.0
        self.q_lambda = 0.0
        self.mu_vmin = 0.0
        self.mu_vmax = 0.0

#------------------------------------------------------------------------------
#  "Branch" class:
#------------------------------------------------------------------------------

class Branch(Named):
    """ Defines a case edge that links two Bus objects.
    """

    def __init__(self, from_bus, to_bus, name=None, online=True, r=0.001,
            x=0.001, b=0.001, s_max=2.0, ratio=1.0, phase_shift=0.0,
            ang_min=None, ang_max=None):
        """ Initialises a new Branch instance.
        """
        # From/source/start bus.
        self.from_bus = from_bus
#        self.from_bus_idx = 0
        # To/target/end bus.
        self.to_bus = to_bus
#        self.to_bus_idx = 0

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

        # Minimum voltage angle difference (angle(Vf) - angle(Vt)) (degrees).
        self.ang_min = ang_min

        # Maximum voltage angle difference (angle(Vf) - angle(Vt)) (degrees).
        self.ang_max = ang_max

        # Power flow results --------------------------------------------------

        # Active power injected at the from bus (MW).
        self.p_from = 0.0
        # Active power injected at the to bus (MW).
        self.p_to = 0.0
        # Reactive power injected at the from bus (MVAr).
        self.q_from = 0.0
        # Reactive power injected at the to bus (MVAr).
        self.q_to = 0.0

        # |S_from| mu.
        self.mu_s_from = 0.0
        # |S_to| mu.
        self.mu_s_to = 0.0

    @property
    def mode(self):
        """ Branch mode may be 'line' or 'transformer'.
        """
        if self.from_bus.v_magnitude == self.to_bus.v_magnitude:
            return LINE
        else:
            return TRANSFORMER

    @property
    def p_losses(self):
        """ Active power losses.
        """
        return self.p_from - self.p_to

    @property
    def q_losses(self):
        """ Reactive power losses.
        """
        return self.q_from - self.q_to


    def reset(self):
        """ Resets the result variables.
        """
        self.p_from = 0.0
        self.p_to = 0.0
        self.q_from = 0.0
        self.q_to = 0.0

        self.mu_s_from = 0.0
        self.mu_s_to = 0.0

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(Named):
    """ Defines a power system generator component. Fixes voltage magnitude
        and active power injected at parent bus. Or when at it's reactive
        power limit fixes active and reactive power injected at parent bus.
    """

    def __init__(self, bus, name=None, online=True, base_mva=100.0,
                 p=100.0, p_max=200.0, p_min=0.0, v_magnitude=1.0,
                 q=0.0, q_max=30.0, q_min=-30.0,
                 p_cost=None, pcost_model=POLYNOMIAL,
                 q_cost=None, qcost_model=None):
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

#        # Start up cost.
#        self.c_startup = c_startup
#        # Shut down cost.
#        self.c_shutdown = c_shutdown

        # Active power cost model: 'poly' or 'pwl' (default: 'poly')
        self.pcost_model = pcost_model

        # Reactive power cost model: 'poly', 'pwl' or None (default: 'poly')
        self.qcost_model = qcost_model

        # Active power cost represented either by a tuple of quadratic
        # polynomial coefficients or a list of piece-wise linear coordinates
        # according to the value of the 'pcost_model' attribute.
        if p_cost is not None:
            self.p_cost = p_cost
        else:
            if pcost_model == POLYNOMIAL:
                self.p_cost = (0.01, 0.1, 10.0)
            elif pcost_model == PW_LINEAR:
                self.p_cost = [(0.0, 0.0), (p_max, 10.0)]
            else:
                raise ValueError

        # Reactive power cost.
        self.q_cost = q_cost

        self.mu_pmin = 0.0
        self.mu_pmax = 0.0

        # Unit Commitment -----------------------------------------------------

        # Ramp up rate (p.u./h).
#        self.rate_up = rate_up
        # Ramp down rate (p.u./h).
#        self.rate_down = rate_down

        # Minimum running time (h).
#        self.min_up = min_up
        # Minimum shut down time (h).
#        self.min_down = min_down

        # Initial number of periods up.
#        self.initial_up = initial_up
        # Initial number of periods down.
#        self.initial_down = initial_down

    @property
    def q_limited(self):
        """ Is the machine at it's limit of reactive power?
        """
        if (self.q >= self.q_max) or (self.q <= self.q_min):
            return True
        else:
            return False

#    @property
#    def mode(self):
#        """ Does the machine represent a generator or a despatchable load.
#        """
#        raise DeprecationWarning, "Use .is_load instead."
#
#        if 0 <= self.p_min < self.p_max:
#            return GENERATOR
#        elif self.p_min < self.p_max <= 0.0:
#            return DISPATCHABLE_LOAD
#        else:
#            return "unknown"

#    @property
#    def p_cost(self):
#        """ Active power cost at the current output.
#        """
#        return self.total_cost(self.p)

    @property
    def is_load(self):
        """ Returns true if the generator if a dispatchable load. This may
            need to be revised to allow sensible specification of both elastic
            demand and pumped storage units.
        """
        return (self.p_min < 0.0) and (self.p_max == 0.0)


    def reset(self):
        """ Resets the result variables.
        """
        self.mu_pmin = 0.0
        self.mu_pmax = 0.0


    def total_cost(self, p=None):
        """ Computes total cost for the generator at the given output level.
        """
        p = self.p if p is None else p

        if self.pcost_model == PW_LINEAR:
            n_segments = len(self.p_cost) - 1
            # Iterate over the piece-wise linear segments.
            for i in range(n_segments):
                x1, y1 = self.p_cost[i]
                x2, y2 = self.p_cost[(i + 1)]

                m = (y2 - y1) / (x2 - x1)
                c = y1 - m * x1

                result = m*p + c

                if x1 <= p <= x2:
                    break
#            else:
##                raise ValueError, "Value [%f] outwith pwl cost curve." % p
#                # Use the last segment for values outwith the cost curve.
#                result = m*p + c

        elif self.pcost_model == POLYNOMIAL:
            result = self.p_cost[-1]

            for i in range(1, len(self.p_cost)):
                result += self.p_cost[-(i + 1)] * p**i

        else:
            raise ValueError

        return result


    def poly_cost(self, val=None, der=0, reactive=False):
        """ Evaluates polynomial generator cost and derivatives.
        """
        cost_model = self.qcost_model if reactive else self.pcost_model
        cost = self.q_cost if reactive else self.p_cost
        if val is None:
            val = self.q if reactive else self.p

        if cost_model == PW_LINEAR:
            logger.error("Cost must be polynomial.")
            return

        # Do derivatives.
        for d in range(der):
            if len(cost) >= 2:
                c = cost[1:-d + 1]
            else:
                c = 0.0
                break
            for k in range(1, len(cost) - d):
                c *= k

        # Evaluate polynomial.
        if c == 0.0:
            f = 0.0
        else:
            f = c[0] # constant term
            for k in range(1, len(cost)):
                f += c[k] * val**(k-1)

        return f


    def pwl_to_poly(self):
        """ Converts the first segment of the pwl cost to linear quadratic.
            FIXME: Curve-fit for all segments.
        """
        if self.pcost_model == PW_LINEAR:
            x0 = self.p_cost[0][0]
            y0 = self.p_cost[0][1]
            x1 = self.p_cost[1][0]
            y1 = self.p_cost[1][1]
            m = (y1 - y0) / (x1 - x0)
            c = y0 - m * x0

            self.pcost_model = POLYNOMIAL
            self.p_cost = (m, c)
        else:
            return


    def poly_to_pwl(self, n_points=10):
        """ Sets the piece-wise linear cost attribute, converting the
            polynomial cost variable by evaluating at zero and then at
            n_points evenly spaced points between p_min and p_max.
        """
        p_min = self.p_min
        p_max = self.p_max
        self.p_cost = []
        # Ensure that the cost model is polynomial for calling total_cost.
        self.pcost_model = POLYNOMIAL

        if p_min > 0.0:
            # Make the first segment go from the origin to p_min.
            step = (p_max - p_min) / (n_points - 2)

            y0 = self.total_cost(0.0)
            self.p_cost.append((0.0, y0))

            x = p_min
            n_points -= 1
        else:
            step = (p_max - p_min) / (n_points - 1)
            x = 0.0

        for _ in range(n_points):
            y = self.total_cost(x)
            self.p_cost.append((x, y))
            x += step

        # Change the cost model.
        self.pcost_model = "pwl"


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
        if self.pcost_model == POLYNOMIAL:
            # Convert polynomial cost function to piece-wise linear.
            self.poly_to_pwl(n_points)

        n_segments = len(self.p_cost) - 1

        qtyprc = []

        for i in range(n_segments):
            x1, y1 = self.p_cost[i]
            x2, y2 = self.p_cost[(i + 1)]

            quantity = x2 - x1
            price = (y2 - y1) / quantity

            qtyprc.append((quantity, price))

        return qtyprc


    def adjust_limits(self):
        """ Sets the active power limits, 'p_max' and 'p_min', according to
            the pwl cost function points.
        """
        if not self.is_load:
            self.p_max = max([point[0] for point in self.p_cost])
        else:
            p_min = min([point[0] for point in self.p_cost])
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
            self.p_cost = self._offbids_to_points(valid)

            # FIXME: Convert reactive power bids into piecewise linear segments.
            # FIXME: Set all reactive costs to zero if not provided.

            self.pcost_model = "pwl"
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

            self.p_cost = points
            # FIXME: Convert reactive power bids into piecewise linear segments.
            # FIXME: Set all reactive costs to zero if not provided.
            self.pcost_model = "pwl"
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
