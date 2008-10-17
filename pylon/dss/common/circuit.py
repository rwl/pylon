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

""" Defines a container of circuit elements """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, List, Int, Float, Bool, Str, Dict, Directory

from bus import Bus
from circuit_element import CircuitElement
from feeder import Feeder

from pylon.dss.conversion.api import \
    PowerConversionElement, VoltageSource, CurrentSource, Generator, Load

from pylon.dss.delivery.api import \
    PowerDeliveryElement, Fault, Transformer, Line, Capacitor

from pylon.dss.control.api import \
    ControlElement, CapacitorControl, RegulatorControl

from pylon.dss.meter.api import MeterElement

from circuit_view import circuit_view

#------------------------------------------------------------------------------
#  "Circuit" class:
#------------------------------------------------------------------------------

class Circuit(HasTraits):
    """ Defines a container of circuit elements """

    case_name = Str

    active_bus_idx = Int(1)

    # Fundamental and default base frequency
    fundamental = Float(60.0, desc="Fundamental and default base frequency")

    auto_add_buses = List(Instance(Bus))

    devices = List(Instance(HasTraits))

    faults = List(Instance(Fault))

    ckt_elements = List(Instance(CircuitElement))

    pde_elements = List(Instance(PowerDeliveryElement))

    pce_elements = List(Instance(PowerConversionElement))

    dss_controls = List(Instance(ControlElement))

    voltage_sources = List(Instance(VoltageSource))

    current_sources = List(Instance(CurrentSource))

    meter_elements = List(Instance(MeterElement))

    generators = List(Instance(Generator))

    # Not yet used
    substations = []

    transformers = List(Instance(Transformer))

    cap_controls = List(Instance(CapacitorControl))

    reg_controls = List(Instance(RegulatorControl))

    lines = List(Instance(Line))

    loads = List(Instance(Load))

    shunt_capacitors = List(Instance(Capacitor))

    feeders = List(Instance(Feeder))

    control_queue = List(Instance(ControlElement))

#    solution = Instance(Solution)

    auto_add_obj = None

    # AutoAdd -----------------------------------------------------------------

    ue_weight = Float(1.0)

    loss_weight = Float(1.0)

    ue_regs = List(Float, [10.0])

    n_ue_regs = Float

    loss_regs = List(Float, [13.0])

    n_loss_regs = Float(0.0)

    capacity_start = Float(0.9)

    capacity_increment = Float(0.005)

    # Default to Euler method
    trapezoidal_integration = Bool(False)

    log_events = Bool(True)

    load_dur_curve = Str

#    load_dur_curve_obj = None

    price_curve = Str

#    price_curve_obj = None

    n_devices = Int

    n_buses = Int

    n_nodes = Int

    max_devices = Int(1000)

    max_buses = Int(1000)

    max_nodes = Int(3000)

    inc_devices = Int(1000)

    inc_buses = Int(1000)

    inc_nodes = Int(3000)

    # Bus and Node ------------------------------------------------------------

    buses = List(Instance(Bus))

    node_bus_map = Dict

    # Flags -------------------------------------------------------------------

    is_solved = Bool(False)

    allow_duplicates = Bool(False)

    # Meter zones recomputed after each change
    zones_locked = Bool(False)

    meter_zones_computed = Bool(False)

    # Model is to be interpreted as Pos seq
    positive_sequence = Bool(False)

    # Voltage limits ----------------------------------------------------------

    normal_min_volts = Float(0.95)

    normal_max_volts = Float(1.05)

    # per unit voltage restraints for this circuit
    emerg_min_volts = Float(0.90)

    emerg_max_volts = Float(1.08)

    legal_voltage_bases = List(
        Float, [0.208, 0.480, 12.47, 24.9, 35.4, 115.0, 230.0]
    )

    # Global circuit multipliers ----------------------------------------------

    generator_dispatch_ref = Float(0.0)

    default_growth_rate = Float(1.025)

    default_growth_factor = Float(1.0)

    # global multiplier for every generator
    gen_multiplier = Float(1.0)

    harm_mult = Float(1.0)

    default_hour_mult = Int

    # price signal for entire circuit
    price_signal = Float(25.0)

    # Energy meter totals -----------------------------------------------------

    register_totals = List

#    default_daily_shape_obj = None

#    default_yearly_shape_obj = None

    current_directory = Directory

#    reduction_strategy = None

    reduction_max_angle = Float(15.0)

    reduction_z_mag = Float(0.02)

    reduction_strategy_string = Str

    pct_normal_factor = Float

    # Views -------------------------------------------------------------------

    traits_view = circuit_view

# EOF -------------------------------------------------------------------------
