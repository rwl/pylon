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
#  "Circuit" class:
#------------------------------------------------------------------------------

class Circuit:
    """ Defines a container of circuit elements """

    case_name = ""

    active_bus_idx = 1

    # Fundamental and default base frequency
    fundamental = 60.0

    auto_add_buses = []

    devices = []

    faults = []

    ckt_elements = []

    pde_elements = []

    pce_elements = []

    dss_controls = []

    sources = []

    meter_elements = []

    generators = []

    # Not yet used
    substations = []

    transformers = []

    cap_controls = []

    reg_controls = []

    lines = []

    loads = []

    shunt_capacitors = []

    feeders = []

    control_queue = []

    solution = None

    auto_add_obj = None

    # AutoAdd -----------------------------------------------------------------

    ue_weight = 1.0

    loss_weight = 1.0

    ue_regs = [10]

    n_ue_regs = 0

    loss_regs = [13]

    n_loss_regs = 0

    capacity_start = 0.9

    capacity_increment = 0.005

    # Default to Euler method
    trapezoidal_integration = False

    log_events = True

    load_dur_curve = ""

    load_dur_curve_obj = None

    price_curve = ""

    price_curve_obj = None

    n_devices = property

    n_buses = property

    n_nodes = property

    max_devices = 1000

    max_buses = 1000

    max_nodes = 3000

    inc_devices = 1000

    inc_buses = 1000

    inc_nodes = 3000

    # Bus and Node ------------------------------------------------------------

    buses = []

    node_bus_map = {}

    # Flags -------------------------------------------------------------------

    is_solved = False

    allow_duplicates = False

    # Meter zones recomputed after each change
    zones_locked = False

    meter_zones_computed = False

    # Model is to be interpreted as Pos seq
    positive_sequence = False

    # Voltage limits ----------------------------------------------------------

    normal_min_volts = 0.95

    normal_max_volts = 1.05

    # per unit voltage restraints for this circuit
    emerg_min_volts = 0.90

    emerg_max_volts = 1.08

    legal_voltage_bases = [0.208, 0.480, 12.47, 24.9, 35.4, 115.0, 230.0]

    # Global circuit multipliers ----------------------------------------------

    generator_dispatch_ref = 0.0

    default_growth_rate = 1.025

    default_growth_factor = 1.0

    # global multiplier for every generator
    gen_multiplier = 1.0

    harm_mult = 1.0

    default_hour_mult

    # price signal for entire circuit
    price_signal = 25.0

    # Energy meter totals -----------------------------------------------------

    register_totals = []

    default_daily_shape_obj = None

    default_yearly_shape_obj = None

    current_directory = ""

    reduction_strategy = None

    reduction_max_angle = 15.0

    reduction_z_mag = 0.02

    reduction_strategy_string = ""

    pct_normal_factor

# EOF -------------------------------------------------------------------------
