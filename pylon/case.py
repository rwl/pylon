# Copyright (C) 2011 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from numpy import zeros

from traits.api import HasTraits, Int, Enum, Float, Bool, List

from pypower.idx_bus import BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, VM, VA, \
    BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN


class Bus(HasTraits):
    bus_i = Int(desc='bus number', label='i', idx=BUS_I)
    bus_type = Enum('PQ', 'PV', 'REF', 'NONE', label='type', idx=BUS_TYPE)
    Pd = Float(desc='real power demand (MW)', idx=PD)
    Qd = Float(desc='reactive power demand (MVAr)', idx=QD)
    Gs = Float(desc='shunt conductance (MW at V = 1.0 p.u.)', idx=GS)
    Bs = Float(desc='shunt susceptance (MVAr at V = 1.0 p.u.)', idx=BS)
    bus_area = Int(desc='area number', label='area', idx=BUS_AREA)
    Vm = Float(desc='voltage magnitude (p.u.)', idx=VM)
    Va = Float(desc='voltage angle (degrees)', idx=VA)
    base_kV = Float(desc='base voltage (kV)', idx=BASE_KV)
    zone = Int(desc='loss zone', idx=ZONE)
    Vmax = Float(desc='maximum voltage magnitude (p.u.)', idx=VMAX)
    Vmin = Float(desc='minimum voltage magnitude (p.u.)', idx=VMIN)

    lam_P = Float(desc='Lagrange multiplier on real power mismatch (u/MW)', idx=LAM_P)
    lam_Q = Float(desc='Lagrange multiplier on reactive power mismatch (u/MVAr)', idx=LAM_Q)
    mu_Vmax = Float(desc='Kuhn-Tucker multiplier on upper voltage limit (u/p.u.)', idx=MU_VMAX)
    mu_Vmin = Float(desc='Kuhn-Tucker multiplier on lower voltage limit (u/p.u.)', idx=MU_VMIN)


class Generator(HasTraits):
    gen_bus = Int(desc='bus number', label='bus')
    Pg = Float(desc='real power output (MW)')
    Qg = Float(desc='reactive power output (MVAr)')
    Qmax = Float(desc='maximum reactive power output at Pmin (MVAr)')
    Qmin = Float(desc='minimum reactive power output at Pmin (MVAr)')
    Vg = Float(desc='voltage magnitude setpoint (p.u.)')
    mBase = Float(desc='total MVA base of this machine, defaults to baseMVA')
    gen_status = Bool(desc='1 - machine in service, 0 - machine out of service')
    Pmax = Float(desc='maximum real power output (MW)')
    Pmin = Float(desc='minimum real power output (MW)')
    Pc1 = Float(desc='lower real power output of PQ capability curve (MW)')
    Pc2 = Float(desc='upper real power output of PQ capability curve (MW)')
    Qc1min = Float(desc='minimum reactive power output at Pc1 (MVAr)')
    Qc1max = Float(desc='maximum reactive power output at Pc1 (MVAr)')
    Qc2min = Float(desc='minimum reactive power output at Pc2 (MVAr)')
    Qc2max = Float(desc='maximum reactive power output at Pc2 (MVAr)')
    ramp_acg = Float(desc='ramp rate for load following/AGC (MW/min)')
    ramp_10 = Float(desc='ramp rate for 10 minute reserves (MW)')
    ramp_30 = Float(desc='ramp rate for 30 minute reserves (MW)')
    ramp_Q = Float(desc='ramp rate for reactive power (2 sec timescale) (MVAr/min)')
    apf = Float(desc='area participation factor')

    mu_Pmax = Float(desc='Kuhn-Tucker multiplier on upper Pg limit (u/MW)')
    mu_Pmin = Float(desc='Kuhn-Tucker multiplier on lower Pg limit (u/MW)')
    mu_Qmax = Float(desc='Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)')
    mu_Qmin = Float(desc='Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)')


class Branch(HasTraits):
    f_bus = Int(desc='from bus number', label='from')
    t_bus = Int(desc='to bus number', label='to')
    br_r = Float(desc='resistance (p.u.)', label='R')
    br_x = Float(desc='reactance (p.u.)', label='X')
    br_b = Float(desc='total line charging susceptance (p.u.)', label='B')
    rate_a = Float(desc='MVA rating A (long term rating)')
    rate_b = Float(desc='MVA rating B (short term rating)')
    rate_c = Float(desc='MVA rating C (emergency rating)')
    tap = Float(desc='transformer off nominal turns ratio')
    shift = Float(desc='transformer phase shift angle (degrees)')
    br_status = Bool(desc='initial branch status, 1 - in service, 0 - out of service')
    angmin = Float(desc='minimum angle difference, angle(Vf) - angle(Vt) (degrees)')
    angmax = Float(desc='maximum angle difference, angle(Vf) - angle(Vt) (degrees)')

    Pf = Float(desc='real power injected at "from" bus end (MW)')
    Qf = Float(desc='reactive power injected at "from" bus end (MVAr)')
    Pt = Float(desc='real power injected at "to" bus end (MW)')
    Qt = Float(desc='reactive power injected at "to" bus end (MVAr)')

    mu_Sf = Float(desc='Kuhn-Tucker multiplier on MVA limit at "from" bus (u/MVA)')
    mu_St = Float(desc='Kuhn-Tucker multiplier on MVA limit at "to" bus (u/MVA)')
    mu_angmin = Float(desc='Kuhn-Tucker multiplier lower angle difference limit')
    mu_angmax = Float(desc='Kuhn-Tucker multiplier upper angle difference limit')


class Area(HasTraits):
    area_i = Int(desc='area number')
    price_ref_bus = Int(desc='price reference bus for this area')


class Cost(HasTraits):
    mode = Enum('pw_linear', 'polynomial', desc='cost model')
    startup = Float(desc='startup cost in US dollars')
    shutdown = Float(desc='shutdown cost in US dollars')
    ncost = Int(desc='number of cost coefficients to follow for polynomial cost function, or number of data points for piecewise linear')
    cost = List(Float)


class Case(HasTraits):
    buses = List(Bus)
    generators = List(Generator)
    branches = List(Branch)
    areas = List(Area)
    costs = List(Cost)

    def to_ppc(self):
        ppc = {}

        ppc['buses'] = zeros((len(self.buses, MU_VMIN + 1)))
        for i, bus in enumerate(self.buses):
            for attr, trait in bus.traits().iteritems():
                ppc['buses'][i, trait.idx] = getattr(bus, attr)


    def from_ppc(self, ppc):
        if 'buses' in ppc:
            nb, ncol = ppc['buses'].shape
            for i in range(nb):
                bus = Bus()
                for attr, trait in bus.traits({'idx': lambda idx: idx < ncol}):
                    setattr(bus, attr, ppc['buses'][i, trait.idx])
