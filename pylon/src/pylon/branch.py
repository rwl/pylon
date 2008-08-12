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

"""
Power system branch components

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Delegate, Event, \
    Array, Bool, Range, Default, Property, Enum, Complex

from pylon.ui.branch_view import branch_view

from pylon.bus import Bus

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  'Branch' class:
#------------------------------------------------------------------------------

class Branch(HasTraits):
    """
    Abstract class that links two Bus objects

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    source_bus = Instance(
        Bus, desc="source/from/start Bus instance", allow_none=False
    )

    target_bus = Instance(
        Bus, desc="target/to/end Bus instance", allow_none=False
    )

    # A default view
    traits_view = branch_view

    # Parent network:
    # TODO: Implement Drag-n-Drop and remove this two-way reference
    network = Instance("pylon.network.Network", allow_none=False)

    # List of buses from which to select connections:
    buses = Delegate("network")

#    from_buses = Property(List(Bus), depends_on=["buses", "buses_items"])
#
#    to_buses = Property(List(Bus), depends_on=["buses", "buses_items"])

    name = String("e", desc="Branch name")

    v_source = Float
#    Delegate(
#        "source_bus", "v_nominal",
#        desc="voltage of the source_bus",
#        label="Vsource"
#    )

    v_target = Float
#    Delegate(
#        "target_bus", "v_nominal",
#        desc="voltage of the target_bus",
#        label="Vtarget"
#    )

#    rating_s = Float(250.0, desc="power rating (MVA)", label="S_{rating}")
#
#    rating_v = Float(400.0, desc="voltage rating (kV)", label="V_{rating}")
#
#    rating_f = Float(50.0, desc="frequency rating (Hz)", label="f_{rating}")

    in_service = Bool(True, desc="connection status")

    # TransmissionLine --------------------------------------------------------

#    length = Float(desc="length (km)")

    r = Float(0.01, desc="positive sequence resistance (p.u. or Ohm/km)")

    x = Float(0.01, desc="positive sequence reactance (p.u. or H/km)")

    b = Float(0.01, desc="total positive sequence line charging "
        "susceptance (p.u. or F/km)")

#    r_zero = Float(0.001, desc="per-unit zero sequence resistance")
#
#    x_zero = Float(0.001, desc="per-unit zero sequence reactance")

    s_max = Float(desc="standard line MVA rating (p.u.)")

#    s_max_source = Float(desc="standard line source end apparent power rating")
#
#    s_max_target = Float(desc="standard line target end apparent power rating")

#    s_max_summer = Float(desc="summer line apparent power rating")

#    s_max_summer_source = Float(desc="summer line source end apparent power rating")
#
#    s_max_summer_target = Float(desc="summer line target end apparent power rating")

#    s_max_winter = Float(desc="winter line apparent power rating")

#    s_max_winter_source = Float(desc="winter line source end apparent power rating")
#
#    s_max_winter_target = Float(desc="winter line target end apparent power rating")

#    s_max_short = Float(desc="short line apparent power rating")

#    s_max_short_source = Float(desc="short line source end apparent power rating")
#
#    s_max_short_target = Float(desc="short line target end apparent power rating")

#    s_max_emergency = Float(desc="MVA rating C (emergency rating)")

#    i_max = Float(desc="current limit (p.u.)")
#
#    p_max = Float(desc="active power limit (p.u.)")

    # Derived from power flow routine:
    p_source = Float(
        style="readonly",
        desc="active power injected at the source bus"
    )

    p_target = Float(
        style="readonly",
        desc="active power injected at the target bus"
    )

    q_source = Float(
        style="readonly",
        desc="reactive power injected at the source bus"
    )

    q_target = Float(
        style="readonly",
        desc="reactive power injected at the target bus"
    )

    p_losses = Property(
        Float,
        style="readonly",
        depends_on=["p_source", "p_target"]
    )

    q_losses = Property(
        Float,
        style="readonly",
        depends_on=["q_source", "q_target"]
    )

    # Transformer -------------------------------------------------------------

    ratio = Float(desc="transformer off nominal turns ratio ( = 0 for lines ) "
        "(taps at 'from' bus, impedance at 'to' bus, i.e. ratio = Vf / Vt)")

    phase_shift = Float(
        desc="phase shift angle in degrees. If > 0 then the target end "
        "voltage leads the source end voltage.  positive => delay"
    )

    phase_shift_max = Float(90.0, desc="maximum phase shift angle in degrees")

    phase_shift_min = Float(-90.0, desc="minimum phase shift angle in degrees")

    # TODO: minimum and maximum angle difference,
    # angle(Vf) - angle(Vt) (degrees)

#    phase_shift_increment = Float(
#        0.01,
#        desc="increment of phase shift angle change"
#    )
#
#    tau = Float(desc="primary and secondary voltage ratio (kV/kV)")

    # Ratio between the source_bus voltage and the target_bus voltage:
    v_ratio = Property(Float, depends_on=['v_source', 'v_target'])

#    winding = Enum(
#        "Source winding", "Target winding", "Phase shift",
#        desc="winding connection"
#    )
#
#    tap_position_nom = Float(desc="flat start tap position")
#
#    tap_position = Float(desc="tap position for next load flow", label="tap")
#
#    tap_increment = Float(
#        0.01,
#        desc="increment by which the tap may be changed"
#    )
#
#    # TODO: Implement validator that ensures <= 0
#    tap_position_min = Float(desc="minimum tap position", label="tap_min")
#
#    # TODO: Implement validator that ensures >= 0
#    tap_position_max = Float(desc="maximum tap position", label="tap_max")
#
#    tap_dxdp = Float("change in reactance per tap position change")
#
#    v_objective = Enum(
#        "Source bus", "Target bus", "Fixed tap",
#        desc="target voltage"
#    )
#
#    # TODO: Implement validator that ensures value >= self.tap_increment
#    v_relay_bandwidth = Float(
#        desc="maximum bandwidth of the voltage sensing relay"
#    )
#
#    p_objective = Float(desc="target power for quadrature booster")
#
#    p_objective_source = Float(desc="target power for quadrature "
#        "booster, controlled from the source end")
#
#    a = Float(desc="fixed tap ratio (p.u./p.u.)")
#
#    theta = Float(desc="fixed phase shift (deg)")
#
#    angle = Float(desc="transformer phase shift angle (degrees), "
#        "positive => delay")
#
#    delta_max = Float(desc="maximum angle difference, "
#        "angle(Vf) - angle(Vt) (degrees)")
#
#    delta_min = Float(desc="minimum angle difference, "
#        "angle(Vf) - angle(Vt) (degrees)")

    #--------------------------------------------------------------------------
    #  Initialise the object:
    #--------------------------------------------------------------------------

#    def __init__(self, network=None, **traits):
#        """
#        Handle being instantiated from a table editor
#
#        """
#
#        if "__table_editor__" in traits:
#            network = traits["__table_editor__"].object
#            self.source_bus = network.buses[0]
#            self.target_bus = network.buses[1]
#            del traits["__table_editor__"]
#
#        self.network = network
#
#        super(BranchViewModel, self).__init__(network=network, **traits)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, source_bus, target_bus, **traits):
#        """ This is only necessary for compatibility with pypylon """
#
#        self.source_bus = source_bus
#        self.target_bus = target_bus
#
#        super(Branch, self).__init__(
#            source_bus=source_bus, target_bus=target_bus, **traits
#        )

    #--------------------------------------------------------------------------
    #  Default source bus:
    #--------------------------------------------------------------------------

    def _source_bus_default(self):
        if self.network is not None:
            return self.network.buses[0]
        else:
            logger.warning(
                "Branch [%s] source bus not set to default" % self
            )
            return None

    #--------------------------------------------------------------------------
    #  Default destination bus:
    #--------------------------------------------------------------------------

    def _target_bus_default(self):
        if self.network is not None:
            return self.network.buses[1]
        else:
            logger.warning(
                "Branch [%s] source bus not set to default" % self
            )
            return None


    def _get_p_losses(self):
        """
        Property getter

        """

        return self.p_source - self.p_target


    def _get_q_losses(self):
        """
        Property getter

        """

        return self.q_source - self.q_target

    #--------------------------------------------------------------------------
    #  Maintain a property indicating the ratio between the source bus voltage
    #  and the target bus voltage:
    #--------------------------------------------------------------------------

    def _get_v_ratio(self):
        return self.source_volt/self.target_volt

#-------------------------------------------------------------------------------
#  "ThreeWindingTransformer" class:
#-------------------------------------------------------------------------------

#class ThreeWindingTransformer(HasTraits):
#    """
#
#    """
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
#    """
#
#    """
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
#    in_service = Bool(desc="connection status")

# EOF -------------------------------------------------------------------------
