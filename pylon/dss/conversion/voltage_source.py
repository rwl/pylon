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

""" Defines a voltage source """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Enum

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.bus import Bus

from power_conversion_element import PowerConversionElement

from pylon.dss.common.circuit_element import CircuitElementColumn

#------------------------------------------------------------------------------
#  "VoltageSource" class:
#------------------------------------------------------------------------------

class VoltageSource(PowerConversionElement):
    """ This is a special power conversion element.  It is special because
    voltage sources must be identified to initialize the solution with all
    other injection sources set to zero.

    A Vsource object is simply a multi-phase Thevenin equivalent with data
    specified as it would commonly be for a power system source equivalent:
    Line-line voltage (kV) and short circuit MVA.

    """

    # Name of bus to which the source's one terminal is connected.  Remember
    # to specify the node order if the terminals are connected in some unusual
    # manner.
    bus_1 = Instance(Bus)

    # Base Source kV, usually L-L unless you are making a positive-sequence
    # model in which case, it will be L-N.
    base_kv = Float(115.0)

    # Per unit of the base voltage that the source is actually operating at.
    # Assumed balanced for all phases.
    pu = Float(1.0, desc="Per unit of the base voltage")

    # Phase angle in degrees of first phase.
    angle = Float(0.0, desc="Phase angle of the first phase")

    # Source frequency.
    frequency = Float(60.0)

    # Number of phases.
    phases = Int(3)

    # MVA Short circuit, 3-phase fault.  Z1 is determined by squaring the base
    # kv and dividing by this value.  For single-phase source, this value is
    # not used.
    mva_sc3 = Float(2000.0, desc="MVA Short circuit, 3-phase fault")

    # MVA Short Circuit, 1-phase fault.  The "single-phase impedance", Zs, is
    # determined by squaring the base kV and dividing by this value.  Then Z0
    # is determined by Z0 = 3Zs - 2Z1.  For 1-phase sources, Zs is used
    # directly. Use x0_r0 to define X/R ratio for 1-phase source.
    mva_sc1 = Float(2100, desc="MVA Short Circuit, 1-phase fault")

    # Positive-sequence X/R ratio.
    x1_r1 = Float(4.0, desc="Positive-sequence X/R ratio")

    # Zero-sequence X/R ratio.
    x0_r0 = Float(3.0, desc="Zero-sequence X/R ratio")

    # Alternate method of defining the source impedance. 3-phase short circuit
    # current, amps.
    i_sc3 = Float(10000.0, desc="3-phase short circuit (alt)")

    # Alternate method of defining the source impedance. Single-phase short
    # circuit current, amps.
    i_sc1 = Float(10500.0, desc="Single-phase short (alt)")

    # Alternate method of defining the source impedance. Positive-sequence
    # resistance, ohms.
    r1 = Float(1.65, desc="Positive-sequence resistance")

    # Alternate method of defining the source impedance. Positive-sequence
    # reactance, ohms.
    x1 = Float(6.6, desc="Positive-sequence reactance")

    # Alternate method of defining the source impedance. Zero-sequence
    # resistance, ohms.
    r0 = Float(1.9, desc="Zero-sequence resistance")

    # Alternate method of defining the source impedance. Zero-sequence
    # reactance, ohms.
    x0 = Float(5.7, desc="Zero-sequence reactance")

    # Base Frequency for impedance specifications.
#    base_freq = Float(60.0, desc="Base frequency for impedance specifications")

    # {pos*| zero | none} Maintain specified sequence for harmonic solution.
    # Default is positive sequence. Otherwise, angle between phases rotates
    # with harmonic.
    scan_type = Enum("Positive", "Zero", "None")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        [
            # CircuitElement traits
            "enabled", "base_freq",
            # PowerConversionElement traits
            "spectrum", "inj_current",
            # VoltageSource traits
            "bus_1", "base_kv", "pu", "angle", "frequency", "phases",
            "mva_sc3", "mva_sc1", "x1_r1", "x0_r0", "i_sc3", "i_sc1",
            "r1", "x1", "r0", "x0", "scan_type"
        ],
        id="pylon.conversion.voltage_source",
        resizable=True,
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  VoltageSource table editor:
#------------------------------------------------------------------------------

voltage_sources_table_editor = TableEditor(
    columns=[
        # CircuitElement traits
        CheckboxColumn(name="enabled"),
        CircuitElementColumn(name="base_freq"),
        # PowerConversionElement traits
        CircuitElementColumn(name="spectrum"),
        CircuitElementColumn(name="inj_current"),
        # VoltageSource traits
        CircuitElementColumn(name="bus_1"),
        CircuitElementColumn(name="base_kv"),
        CircuitElementColumn(name="pu"),
        CircuitElementColumn(name="angle"),
        CircuitElementColumn(name="frequency")
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="phases"),
        CircuitElementColumn(name="mva_sc3"),
        CircuitElementColumn(name="mva_sc1"),
        CircuitElementColumn(name="x1_r1"),
        CircuitElementColumn(name="x0_r0"),
        CircuitElementColumn(name="i_sc3"),
        CircuitElementColumn(name="i_sc1"),
        CircuitElementColumn(name="r1"),
        CircuitElementColumn(name="x1"),
        CircuitElementColumn(name="r0"),
        CircuitElementColumn(name="x0"),
        CircuitElementColumn(name="scan_type"),
    ],
    show_toolbar=True,
    deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=VoltageSource,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    VoltageSource().configure_traits()

# EOF -------------------------------------------------------------------------
