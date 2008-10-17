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

""" Defines the line element """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Str, Int, Float, Enum, Array, Bool

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.circuit_element import CircuitElementColumn

from pylon.dss.common.bus import Bus

from pylon.dss.general.line_code import LineCode

from power_delivery_element import PowerDeliveryElement

#------------------------------------------------------------------------------
#  "Line" class:
#------------------------------------------------------------------------------

class Line(PowerDeliveryElement):
    """ Line impedances are specified in per unit length and are multiplied by
    the length when the primitive Y matrix is computed.

    You may specify the impedances of the line either by symmetrical components
    or by R, X, and nodal C matrices  (also per unit length).

    All C's is entered in nano farads.

    The ultimate values are in the matrices.  If you specify matrices, then the
    symmetrical component values are ignored.  However, if you change any of
    the symmetrical component values the matrices will be recomputed.  It is
    assumed you want to use symmetrical component values.  Don't mix data entry
    by matrix and by symmetrical components.

    Note that if you change the number of phases, the matrices are reallocated
    and reinitialized with whatever is currently in the symmetrical component
    data.


    Multi-phase, two-port line or cable.  Pi model.  Power delivery element
    described by its impedance.  Impedances may be specified by symmetrical
    component values or by matrix values.  Alternatively, you may simply refer
    to an existing LineCode object from which the impedance values will be
    copied.  Then you need only specify the length.

    You can define the line impedance at a base frequency directly in a Line
    object definition or you can import the impedance definition from a
    LineCode object. Both of these definitions of impedance are quite similar
    except that the LineCode object can perform Kron reduction.

    If the geometry property is specified all previous definitions are ignored.
    The DSS will compute the impedance matrices from the specified geometry
    each time the frequency changes.

    Whichever definition is the most recent applies, as with nearly all DSS
    functions.

    Note the units property; you can declare any length measurement in whatever
    units you please.  Internally, everything is converted to meters. Just be
    sure to declare the units. Otherwise, they are assumed to be compatible
    with other data or irrelevant.

    """

    # Name of bus for terminal 1. Node order definitions optional.
    bus_1 = Instance(Bus)

    # Name of bus for terminal 2.
    bus_2 = Instance(Bus)

    # Name of linecode object describing line impedances.
    # If you use a line code, you do not need to specify the impedances here.
    # The line code must have been PREVIOUSLY defined.  The values specified
    # last will prevail over those specified earlier (left-to-right sequence
    # of properties).  If no line code or impedance data are specified, line
    # object defaults to 336 MCM ACSR on 4 ft spacing.
    line_code = Instance(LineCode)

    # Length of line. If units do not match the impedance data, specify "units"
    # property.
    length = Float(1.0)

    # No. of phases.  A line has the same number of conductors per terminal as
    # phases.  Neutrals are not explicitly modeled unless declared as a phase
    # and the impedance matrices adjusted accordingly.
    phases = Int(3)

    # Positive-sequence Resistance, ohms per unit length.
    r1 = Float(
        0.058, desc="Positive-sequence resistance, ohms per unit length"
    )

    # Positive-sequence Reactance, ohms per unit length.
    x1 = Float(
        0.1206, desc="Positive-sequence reactance, ohms per unit length"
    )

    # Zero-sequence resistance, ohms per unit length.
    r0 = Float(0.1784, desc="Zero-sequence resistance, ohms per unit length")

    # Zero-sequence Reactance, ohms per unit length.
    x0 = Float(0.4047, desc="Zero-sequence reactance, ohms per unit length")

    # Positive-sequence capacitance, nF per unit length.
    c1 = Float(3.4, desc="Positive-sequence capacitance, nF per unit length")

    # Zero-sequence capacitance, nF per unit length.
    c0 = Float(1.6, desc="Zero-sequence capacitance, nF per unit length")

    # Resistance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases. May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    r_matrix = Array

    # Reactance matrix, lower triangle, ohms per unit length. Order of the
    # matrix is the number of phases. May be used to specify the impedance of
    # any line configuration.  For balanced line models, you may use the
    # standard symmetrical component data definition instead.
    x_matrix = Array

    # Nodal Capacitance matrix, lower triangle, nf per unit length.Order of the
    # matrix is the number of phases.  May be used to specify the shunt
    # capacitance of any line configuration.  For balanced line models, you may
    # use the standard symmetrical component data definition instead.
    c_matrix = Array

    # {Y/N | T/F}  Default= No/False.  Designates this line as a switch for
    # graphics and algorithmic purposes.
    # SIDE EFFECT: Sets R1=0.001 X1=0.0. You must reset if you want something
    # different.
    switch = Bool(False)

    # Carson earth return resistance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    rg = Float(0.0, desc="Carson earth return resistance per unit length")

    # Carson earth return reactance per unit length used to compute impedance
    # values at base frequency.  For making better frequency adjustments.
    xg = Float(0.0, desc="Carson earth return reactance per unit length")

    # Earth resistivity used to compute earth correction factor. Overrides Line
    # geometry definition if specified.
    rho = Float(100.0, desc="Earth resistivity")

    # Geometry code for LineGeometry Object. Supercedes any previous definition
    # of line impedance. Line constants are computed for each frequency change
    # or rho change. CAUTION: may alter number of phases.
    geometry = Str

    # Length Units = {none | mi|kft|km|m|Ft|in|cm } Default is None - assumes
    # length units match impedance units.
    units = Enum("None", "mi", "kft", "km", "m", "ft", "in", "cm")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        [
            # CircuitElement traits
            "enabled", "base_freq",
            # PowerDeliveryElement traits
            "norm_amps", "emerg_amps", "fault_rate", "pct_perm", "repair",
            # Line traits
            "bus_1", "bus_2", "line_code", "length", "phases", "r1", "x1",
            "r0", "x0", "c1", "c0", "r_matrix", "x_matrix", "c_matrix",
            "switch", "rg", "xg", "rho", "geometry", "units"
        ],
        id="pylon.delivery.line",
        resizable=True, title="Line",
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  Line table editor:
#------------------------------------------------------------------------------

lines_table_editor = TableEditor(
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
        # Line traits
        CircuitElementColumn(
            name="bus_1",
#            editor=InstanceEditor(name="buses", editable=False),
            label="Source", format_func=lambda obj: obj.name
        ),
        CircuitElementColumn(
            name="bus_2",
#            editor=InstanceEditor(name="buses", editable=False),
            label="Target", format_func=lambda obj: obj.name
        ),
        CircuitElementColumn(
            name="line_code",
#            editor=InstanceEditor(name="buses", editable=False),
            format_func=lambda obj: obj.name
        ),
        CircuitElementColumn(name="length"),
        CircuitElementColumn(name="phases"),
        CircuitElementColumn(name="r1"),
        CircuitElementColumn(name="x1"),
        CircuitElementColumn(name="r0"),
        CircuitElementColumn(name="x0"),
        CircuitElementColumn(name="c1"),
        CircuitElementColumn(name="c0"),
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="r_matrix"),
        CircuitElementColumn(name="x_matrix"),
        CircuitElementColumn(name="c_matrix"),
        CircuitElementColumn(name="switch"),
        CircuitElementColumn(name="rg"),
        CircuitElementColumn(name="xg"),
        CircuitElementColumn(name="rho"),
        CircuitElementColumn(name="geometry"),
        CircuitElementColumn(name="units")
    ],
    show_toolbar=True, deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=Line,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Line().configure_traits()


# EOF -------------------------------------------------------------------------
