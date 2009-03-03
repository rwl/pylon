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

""" Defines power system branch components.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Delegate, Event, \
    Array, Bool, Range, Property, Enum, Complex, Disallow

from pylon.ui.branch_view import branch_view, line_view, transformer_view

from pylon.bus import Bus

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  'Branch' class:
#------------------------------------------------------------------------------

class Branch(HasTraits):
    """ Defines a network edge that links two Bus objects.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Deprecated identifier.
    id = Disallow

    # Human readable identifier.
    name = String("e", desc="Branch name")

    # Source/from/start Bus instance.
    source_bus = Instance(Bus, desc="source/from/start Bus instance",
        allow_none=False)

    # Index of the source bus in the list of all buses.
    source_bus_idx = Property(Int, depends_on=["source_bus", "buses"])

    # Target/to/end Bus instance.
    target_bus = Instance(Bus, desc="target/to/end Bus instance",
        allow_none=False)

    # Index of the target bus in the bus list.
    target_bus_idx = Property(Int, depends_on=["target_bus", "buses"])

    # Obsolete parent network reference.
    network = Disallow

    # List of all buses in the network. Set at the network level.
    buses = List(Instance(Bus), desc="buses present in the network")

    # List of buses from which to select the source bus.
    _source_buses = Property(List(Instance(Bus)),
        depends_on=["buses", "buses_items"])

    # List of buses from which to select the targe bus.
    _target_buses = Property(List(Instance(Bus)),
        depends_on=["buses", "buses_items"])

    # Is the branch operating as line or a transformer?
    mode = Property(Enum("Line", "Transformer"), depends_on=["v_ratio"])

    # Nominal voltage of the source bus.
#    v_source = Float

    # Nominal voltage of the target bus.
#    v_target = Float

    # Ratio between the source_bus voltage and the target_bus voltage:
    v_ratio = Property(Float,
        depends_on=["source_bus.v_amplitude", "target_bus.v_amplitude"])

    # Power rating (MVA).
#    s_rating = Float(250.0, desc="power rating (MVA)", label="S_{rating}")

    # Voltage rating (kV).
#    v_rating = Float(400.0, desc="voltage rating (kV)", label="V_{rating}")

    # Frequency rating (Hz).
#    f_rating = Float(50.0, desc="frequency rating (Hz)", label="f_{rating}")

    # Is the branch in service?
    online = Bool(True, desc="connection status")

    # TransmissionLine --------------------------------------------------------

#    length = Float(desc="length (km)")

    # Positive sequence branch resistance.
    r = Float(0.01, desc="positive sequence resistance (p.u. or Ohm/km)")

    # Positive sequence branch reactance.
    x = Float(0.01, desc="positive sequence reactance (p.u. or H/km)")

    # Total positive sequence line charging susceptance.
    b = Float(0.01, desc="total positive sequence line charging "
        "susceptance (p.u. or F/km)")

    # Zero sequence resistance.
#    r_zero = Float(0.001, desc="per-unit zero sequence resistance")

    # Zero sequence reactance.
#    x_zero = Float(0.001, desc="per-unit zero sequence reactance")

    # Standard line MVA rating (p.u.).
    s_max = Float(desc="standard line MVA rating (p.u.)")
#    s_max_source = Float(desc="standard line source end MVA rating")
#    s_max_target = Float(desc="standard line target end MVA rating")

    # Summer line apparent power rating.
#    s_max_summer = Float(desc="summer line apparent power rating")
#    s_max_summer_source = Float(desc="summer line source end MVA rating")
#    s_max_summer_target = Float(desc="summer line target end MVA rating")

    # Winter line apparent power rating.
#    s_max_winter = Float(desc="winter line apparent power rating")
#    s_max_winter_source = Float(desc="winter line source end MVA rating")
#    s_max_winter_target = Float(desc="winter line target end MVA rating")

    # Short line apparent power rating.
#    s_max_short = Float(desc="short line apparent power rating")
#    s_max_short_source = Float(desc="short line source end MVA rating")
#    s_max_short_target = Float(desc="short line target end MVA rating")

#    s_max_emergency = Float(desc="MVA rating C (emergency rating)")

    # Active power limit (p.u.).
#    p_max = Float(desc="active power limit (p.u.)")

    # Current limit (p.u.).
#    i_max = Float(desc="current limit (p.u.)")

    #--------------------------------------------------------------------------
    #  Transformer trait definitions.
    #--------------------------------------------------------------------------

    # Off nominal turns ratio.
    ratio = Float(desc="transformer off nominal turns ratio ( = 0 for lines ) "
        "(taps at 'from' bus, impedance at 'to' bus, i.e. ratio = Vf / Vt)")

    # Phase shift angle in degrees.
    phase_shift = Float(desc="phase shift angle in degrees. If > 0 then the "
        "target end voltage leads the source end voltage.  positive => delay")

    # Maximum phase shift angle in degrees.
    phase_shift_max = Float(90.0, desc="maximum phase shift angle in degrees")

    # Minimum phase shift angle in degrees.
    phase_shift_min = Float(-90.0, desc="minimum phase shift angle in degrees")

    # TODO: minimum and maximum angle difference,
    # angle(Vf) - angle(Vt) (degrees)

    # Increment of phase shift angle change.
#    phase_shift_increment = Float(0.01,
#        desc="increment of phase shift angle change")

    # Primary and secondary voltage ratio.
#    tau = Float(desc="primary and secondary voltage ratio (kV/kV)")

    # Winding connection.
#    winding = Enum("Source winding", "Target winding", "Phase shift",
#        desc="winding connection")

    # Flat start tap position.
#    tap_position_nom = Float(desc="flat start tap position")

    # Tap position for next load flow.
#    tap_position = Float(desc="tap position for next load flow", label="tap")

    # Increment by which the tap may be changed.
#    tap_increment = Float(0.01,
#        desc="increment by which the tap may be changed")

    # Minimum tap position.
    # TODO: Implement validator that ensures <= 0 (Range)
#    tap_position_min = Float(desc="minimum tap position", label="tap_min")

    # Maximum tap position.
    # TODO: Implement validator that ensures >= 0
#    tap_position_max = Float(desc="maximum tap position", label="tap_max")

    # Change in reactance per tap position change.
#    tap_dxdp = Float("change in reactance per tap position change")

    # Target/objective voltage.
#    v_objective = Enum("Source bus", "Target bus", "Fixed tap",
#        desc="target voltage")

    # Maximum bandwidth of the voltage sensing relay.
    # TODO: Implement validator that ensures value >= self.tap_increment
#    v_relay_bandwidth = Float(desc="maximum bandwidth of the voltage "
#                              "sensing relay")

    # Target power for quadrature booster.
#    p_objective = Float(desc="target power for quadrature booster")

    # Target power for quadrature booster, controlled from the source end.
#    p_objective_source = Float(desc="target power for quadrature "
#        "booster, controlled from the source end")

    # Fixed tap ratio.
#    a = Float(desc="fixed tap ratio (p.u./p.u.)")

    # Fixed phase shift.
#    theta = Float(desc="fixed phase shift (deg)")

    # Transformer phase shift angle.
#    angle = Float(desc="transformer phase shift angle (degrees), "
#        "positive => delay")

    # Maximum angle difference.
#    delta_max = Float(desc="maximum angle difference, "
#        "angle(Vf) - angle(Vt) (degrees)")

    # Minimum angle difference.
#    delta_min = Float(desc="minimum angle difference, "
#        "angle(Vf) - angle(Vt) (degrees)")

    #--------------------------------------------------------------------------
    #  Power flow routine results:
    #--------------------------------------------------------------------------

    # Active power injected at the source bus.
    p_source = Float(style="readonly",
                     desc="active power injected at the source bus")

    # Active power injected at the target bus.
    p_target = Float(style="readonly",
                     desc="active power injected at the target bus")

    # Reactive power injected at the source bus.
    q_source = Float(style="readonly",
                     desc="reactive power injected at the source bus")

    # Reactive power injected at the target bus.
    q_target = Float(style="readonly",
                     desc="reactive power injected at the target bus")

    # Active power losses.
    p_losses = Property(Float, style="readonly",
                        depends_on=["p_source", "p_target"])

    # Reactive power losses.
    q_losses = Property(Float, style="readonly",
                        depends_on=["q_source", "q_target"])

    mu_s_source = Float(style="readonly", desc="|S_source| mu")

    mu_s_target = Float(style="readonly", desc="|S_target| mu")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # A default view.
    traits_view = branch_view

    # View of the branch line properties.
    line_view = line_view

    # View of the branch transformer properties.
    transformer_view = transformer_view

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, source_bus, target_bus, **traits):
        """ Initialises a new Branch instance.
        """
        self.source_bus = source_bus
        self.target_bus = target_bus

        super(Branch, self).__init__(source_bus=source_bus,
            target_bus=target_bus, **traits)

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _mode_changed(self, new):
        """ Handles the branch mode changing.
        """
        if new is "Line":
            self.ratio = 0.0
        elif new is "Transformer":
            self.ratio = 1.0
        else:
            raise ValueError

    #--------------------------------------------------------------------------
    #  Voltage ratio between the source bus and  the target bus:
    #--------------------------------------------------------------------------

    def _get_v_ratio(self):
        """ Property getter.
        """
        sb = self.source_bus
        tb = self.target_bus

        if (sb is not None) and (tb is not None) and (tb.v_amplitude != 0.0):
            return sb.v_amplitude / tb.v_amplitude
        else:
            return 1.0


    def _get_mode(self):
        """ Property getter.
        """
        # FIXME: Should the nominal voltage be used here?
        if 0.99 <= self.v_ratio <= 1.01:
            return "Line"
        else:
            return "Transformer"


    def _get_source_bus_idx(self):
        """ Property getter.
        """
        return self.buses.index(self.source_bus)


    def _get_target_bus_idx(self):
        """ Property getter.
        """
        return self.buses.index(self.target_bus)


    def _get__source_buses(self):
        """ Property getter.
        """
        return [bus for bus in self.buses if bus != self.target_bus]


    def _get__target_buses(self):
        """ Property getter.
        """
        return [bus for bus in self.buses if bus != self.source_bus]


    def _get_p_losses(self):
        """ Property getter.
        """
        return self.p_source - self.p_target


    def _get_q_losses(self):
        """ Property getter.
        """
        return self.q_source - self.q_target

#-------------------------------------------------------------------------------
#  "ThreeWindingTransformer" class:
#-------------------------------------------------------------------------------

#class ThreeWindingTransformer(HasTraits):
#
#    #--------------------------------------------------------------------------
#    #  Trait definitions:
#    #--------------------------------------------------------------------------
#
#    bus_1 = Int(desc="bus number of the first winding")
#
#    bus_2 = Int(desc="bus number of the second winding")
#
#    bus_3 = Int(desc="bus number of the third winding")
#
#    rating_v_1 = Float(desc="voltage rating of the first winding (kV)")
#
#    rating_v_2 = Float(desc="voltage rating of the second winding (kV)")
#
#    rating_v_3 = Float(desc="voltage rating of the third winding (kV)")
#
#    r_1_2 = Float(desc="resistance of the branch 1-2")
#
#    r_1_3 = Float(desc="resistance of the branch 1-3")
#
#    r_2_3 = Float(desc="resistance of the branch 2-3")
#
#    x_1_2 = Float(desc="reactance of the branch 1-2")
#
#    x_1_3 = Float(desc="reactance of the branch 1-3")
#
#    x_2_3 = Float(desc="reactance of the branch 2-3")
#
#    i_max_1 = Float(desc="current limit of the first branch (p.u.)")
#
#    i_max_2 = Float(desc="current limit of the second branch (p.u.)")
#
#    i_max_3 = Float(desc="current limit of the third branch (p.u.)")
#
#    p_max_1 = Float(desc="active power limit of the first branch (p.u.)")
#
#    p_max_2 = Float(desc="active power limit of the second branch (p.u.)")
#
#    p_max_3 = Float(desc="active power limit of the third branch (p.u.)")
#
#    s_max_1 = Float(desc="apparent power limit of the first branch (p.u.)")
#
#    s_max_2 = Float(desc="apparent power limit of the second branch (p.u.)")
#
#    s_max_3 = Float(desc="apparent power limit of the third branch (p.u.)")

#-------------------------------------------------------------------------------
#  "Shunt" class:
#-------------------------------------------------------------------------------

#class Shunt(HasTraits):
#
#    bus = Instance("pylon.bus.Bus", allow_none=False)
#
#    rating_s = Float(desc="power rating (MVA)")
#
#    rating_v = Float(desc="voltage rating (kV)")
#
#    rating_f = Float(desc="frequency rating (Hz)")
#
#    g = Float(desc="conductance (p.u.)")
#
#    b = Float(desc="susceptance (p.u.)")
#
#    online = Bool(desc="connection status")

# EOF -------------------------------------------------------------------------
