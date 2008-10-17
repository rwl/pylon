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

""" Defines a transformer """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    Instance, Int, Float, Enum, Array, Bool, List, Str

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.circuit_element import CircuitElementColumn

from pylon.dss.common.bus import Bus

from power_delivery_element import PowerDeliveryElement

#------------------------------------------------------------------------------
#  "Transformer" class:
#------------------------------------------------------------------------------

class Transformer(PowerDeliveryElement):
    """ The Transfomer model is implemented as a multi-terminal (two or more)
    power delivery element.

    A transfomer consists of two or more Windings, connected in somewhat
    arbitray fashion (with the standard Wye-Delta defaults, of course).  You
    can specify the parameters of a winding one winding at a time or use arrays
    to set all the values.  Use the "wdg=..." parameter to select a winding.

    Transformers have one or more phases.  The number of conductors per
    terminal is always one more than the number of phases.  For wye- or
    star-connected windings, the extra conductor is the neutral point.  For
    delta-connected windings, the extra terminal is open internally (you
    normally leave this connected to node 0).

    """

    # Number of phases this transformer.
    phases = Int(3)

    # Number of windings, this transformers. (Also is the number of terminals)
    windings = Int(2)

    # Winding Defintion -------------------------------------------------------

    # Set this = to the number of the winding you wish to define.  Then set
    # the values for this winding.  Repeat for each winding.  Alternatively,
    # use the array collections (buses, kvas, etc.) to define the windings.
    # Note: impedances are BETWEEN pairs of windings; they are not the property
    # of a single winding.
    wdg = Int(1)

    # Bus to which this winding is connected.
    bus = Instance(Bus)

    # Connection of this winding. Default is "wye" with the neutral solidly
    # grounded.
    conn = Enum("Wye")

    # For 2-or 3-phase, enter phase-phase kV rating.  Otherwise, kV rating of
    # the actual winding
    kv = Float(12.47, desc="Phase-phase kV rating for 2-or 3-phase")

    # Base kVA rating of the winding. Side effect: forces change of max normal
    # and emerg kva ratings.
    kva = Float(1000.0)

    # Per unit tap that this winding is on.
    tap = Float(1.0, desc="Per unit tap that this winding is on")

    # Percent resistance this winding.  (half of total for a 2-winding).
    pct_r = Float(0.2, desc="Percent resistance this winding")

    # Neutral resistance of wye (star)-connected winding in actual ohms. If
    # entered as a negative value, the neutral is assumed to be open, or
    # floating.
    r_neut = Float(-1, desc="Neutral resistance")

    # Neutral reactance of wye(star)-connected winding in actual ohms. May
    # be + or -.
    x_neut = Float(0, desc="Neutral reactance")

    # General Data ------------------------------------------------------------

    # Use the following parameters to set the winding values using arrays
    # (setting of wdg=... is ignored).

    # Use this to specify all the bus connections at once using an array.
    # Example:
    #     New Transformer.T1 buses="Hibus, lowbus"
    buses = List(Float)

    # Use this to specify all the Winding connections at once using an array.
    # Example:
    #    New Transformer.T1 buses="Hibus, lowbus" ~ conns=(delta, wye)
    conns = List(Float)

    # Use this to specify the kV ratings of all windings at once using an
    # array. Example:
    # New Transformer.T1 buses="Hibus, lowbus"
    # ~ conns=(delta, wye)
    # ~ kvs=(115, 12.47)
    # See kV= property for voltage rules.
    kv_s = List(Float)

    # Use this to specify the kVA ratings of all windings at once using an
    # array.
    kva_s = List(Float)

    # Use this to specify the p.u. tap of all windings at once using an array.
    taps = List(Float)

    # Use this to specify the percent reactance, H-L (winding 1 to winding 2).
    # Use for 2- or 3-winding transformers. On the kva base of winding 1.
    x_hl = Float(7.0)

    # Use this to specify the percent reactance, H-T (winding 1 to winding 3).
    # Use for 3-winding transformers only. On the kVA base of winding 1.
    x_ht = Float(35)

    # Use this to specify the percent reactance, L-T (winding 2 to winding 3).
    # Use for 3-winding transformers only. On the kVA base of winding 1.
    x_lt = Float(30)

    # Use this to specify the percent reactance between all pairs of windings
    # as an array.
    # All values are on the kVA base of winding 1.  The order of the values is
    # as follows:
    #    (x12 13 14... 23 24.. 34 ..)
    # There will be n(n-1)/2 values, where n=number of windings.
    x_sc_array = List(Float)

    # Thermal time constant of the transformer in hours.  Typically about 2.
    thermal = Float(2, desc="Thermal time constant in hours")

    # n Exponent for thermal properties in IEEE C57.  Typically 0.8.
    n = Float(0.8, desc="n exponent for thermal properties in IEEE C57")

    # m Exponent for thermal properties in IEEE C57.  Typically 0.9 - 1.0
    m = Float(0.8, desc="m exponent for thermal properties in IEEE C57")

    # Temperature rise, deg C, for full load.
    fl_rise = Float(65.0, desc="Temperature rise, deg C, for full load")

    # Hot spot temperature rise, deg C.
    hs_rise = Float(15.0, desc="Hot spot temperature rise, deg C")

    # Percent load loss at full load. The %R of the High and Low windings (1
    # and 2) are adjusted to agree at rated kVA loading.
    pct_load_loss = Float(0.0, desc="Percent load loss at full load")

    # Percent no load losses at rated excitation voltage. Converts to a
    # resistance in parallel with the magnetising impedance in each winding.
    pct_no_load_loss = Float(
        0.0, desc="Percent no load losses at rated excitation voltage"
    )

    # Normal maximum kVA rating of H winding (winding 1).  Usually 100% - 110%
    # of maximum nameplate rating, depending on load shape. Defaults to 110% of
    # kVA rating of Winding 1.
    norm_h_kva = Float(desc="Normal maximum kVA rating of H winding")

    # Emergency (contingency)  kVA rating of H winding (winding 1).  Usually
    # 140% - 150% of
    # maximum nameplate rating, depending on load shape. Defaults to 150% of
    # kVA rating of Winding 1.
    emerg_h_kva = Float(desc="Emergency (contingency) kVA rating of H winding")

    # {Yes|No}  Designates whether this transformer is to be considered a
    # substation.
    substation = Bool(False, desc="Is the transformer a substation?")

    # Max per unit tap for the active winding.
    max_tap = Float(1.10, desc="Max per unit tap for the active winding")

    # Min per unit tap for the active winding.
    min_tap = Float(0.90, desc="Min per unit tap for the active winding")

    # Total number of taps between min and max tap.
    num_taps = Int(32, desc="Total number of taps between min and max tap")

    # Substation Name. Optional. If specified, printed on plots
    sub_name = Str

    # Percent magnetizing current. Default=0.0. Magnetizing branch is in
    # parallel with windings in each phase. Also, see "ppm_antifloat".
    pct_image = Float(desc="Percent magnetizing current")

    # Parts per million by which the reactive term is increased
    # to protect against accidentally floating a winding.
    # If positive then the effect is adding a small reactor to ground. If
    # negative, then a capacitor.
    ppm_antifloat = Float(
        1.0, desc="Parts per million by which the reactive term is increased"
        "to protect against accidentally floating a winding"
    )

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        [
            # CircuitElement traits
            "enabled", "base_freq",
            # PowerDeliveryElement traits
            "norm_amps", "emerg_amps", "fault_rate", "pct_perm", "repair",
            # Transformer traits
            "phases", "windings", "wdg", "bus", "conn", "kv", "kva", "tap",
            "pct_r", "r_neut", "x_neut", "buses", "conns", "kv_s", "kva_s",
            "taps", "x_hl", "x_ht", "x_lt", "x_sc_array", "thermal", "n", "m",
            "fl_rise", "hs_rise", "pct_load_loss", "pct_no_load_loss",
            "norm_h_kva", "emerg_h_kva", "substation", "max_tap", "min_tap",
            "num_taps", "sub_name", "pct_image", "ppm_antifloat"
        ],
        id="pylon.delivery.transformer",
        resizable=True, title="Transformer",
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  Transformer table editor:
#------------------------------------------------------------------------------

transformers_table_editor = TableEditor(
    columns=[
        # CircuitElement traits
        CheckboxColumn(name="enabled"),
        CircuitElementColumn(name="base_freq"),
        # PowerDeliveryElement traits
        CircuitElementColumn(name="norm_amps"),
        CircuitElementColumn(name="emerg_amps"),
        CircuitElementColumn(name="fault_rate"),
        CircuitElementColumn(name="pct_perm"),
        CircuitElementColumn(name="repair"),
        # Transformer traits
        CircuitElementColumn(name="phases"),
        CircuitElementColumn(name="windings"),
        CircuitElementColumn(name="wdg"),
        CircuitElementColumn(
            name="bus",
#            editor=InstanceEditor(name="buses", editable=False),
            label="Source", format_func=lambda obj: obj.name
        ),
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="conn"),
        CircuitElementColumn(name="kv"),
        CircuitElementColumn(name="kva"),
        CircuitElementColumn(name="tap"),
        CircuitElementColumn(name="pct_r"),
        CircuitElementColumn(name="r_neut"),
        CircuitElementColumn(name="x_neut"),
        CircuitElementColumn(name="buses"),
        CircuitElementColumn(name="conns"),
        CircuitElementColumn(name="kv_s"),
        CircuitElementColumn(name="kva_s"),
        CircuitElementColumn(name="taps"),
        CircuitElementColumn(name="x_hl"),
        CircuitElementColumn(name="x_ht"),
        CircuitElementColumn(name="x_lt"),
        CircuitElementColumn(name="x_sc_array"),
        CircuitElementColumn(name="thermal"),
        CircuitElementColumn(name="n"),
        CircuitElementColumn(name="m"),
        CircuitElementColumn(name="fl_rise"),
        CircuitElementColumn(name="hs_rise"),
        CircuitElementColumn(name="pct_load_loss"),
        CircuitElementColumn(name="pct_no_load_loss"),
        CircuitElementColumn(name="norm_h_kva"),
        CircuitElementColumn(name="emerg_h_kva"),
        CircuitElementColumn(name="substation"),
        CircuitElementColumn(name="max_tap"),
        CircuitElementColumn(name="min_tap"),
        CircuitElementColumn(name="num_taps"),
        CircuitElementColumn(name="sub_name"),
        CircuitElementColumn(name="pct_image"),
        CircuitElementColumn(name="ppm_antifloat"),
    ],
    show_toolbar=True,
    deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=Transformer,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Transformer().configure_traits()

# EOF -------------------------------------------------------------------------
