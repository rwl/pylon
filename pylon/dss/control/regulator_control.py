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

""" Defines a transformer controller """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Bool

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.circuit_element import CircuitElementColumn

from pylon.dss.delivery.api import Transformer

from pylon.dss.common.bus import Bus

from control_element import ControlElement

#------------------------------------------------------------------------------
#  "RegControl" class:
#------------------------------------------------------------------------------

class RegulatorControl(ControlElement):
    """ A RegulatorControl is a control element that is connected to a terminal
    of another circuit element that must be a transformer.

    """

    # Name of Transformer element to which the RegControl is connected. Do not
    # specify the full object name; "Transformer" is assumed for the object
    # class.
    transformer = Instance(Transformer, allow_none=False)

    # Number of the winding of the transformer element that the RegControl is
    # monitoring. 1 or 2, typically.  Side Effect: Sets TAPWINDING property to
    # the same winding.
    winding = Int(1, desc="Connected transformer winding")

    # Voltage regulator setting, in VOLTS, for the winding being controlled.
    # Multiplying this value times the ptratio should yield the voltage across
    # the WINDING of the controlled transformer.
    v_reg = Float(120.0, desc="Voltage regulator setting")

    # Bandwidth in VOLTS for the controlled bus (see help for ptratio property)
    band = Float(3.0, desc="Bandwidth for the controlled bus")

    # Ratio of the PT that converts the controlled winding voltage to the
    # regulator voltage. If the winding is Wye, the line-to-neutral voltage is
    # used.  Else, the line-to-line voltage is used.
    pt_ratio = Float(
        60.0, desc="Ratio of the controlled winding voltage to the regulator "
        "voltage"
    )

    # Rating, in Amperes, of the primary CT rating for converting the line amps
    # to control amps.The typical default secondary ampere rating is 5 Amps.
    ct_prim = Float(
        300.0, desc="Rating of the primary CT for converting the line amps to "
        "control amps"
    )

    # R setting on the line drop compensator in the regulator, expressed in
    # VOLTS.
    r = Float(0.0, desc="Resistance on the line drop compensator")

    # X setting on the line drop compensator in the regulator, expressed in
    # VOLTS.
    x = Float(0.0, desc="Reactance on the line drop compensator")

    # Name of a bus in the system to use as the controlled bus instead of the
    # bus to which the winding is connected or the R and X line drop
    # compensator settings.  Do not specify this value if you wish to use the
    # line drop compensator settings.  Default is null string. Assumes the base
    # voltage for this bus is the same as the transformer winding base
    # specified above. Note: This bus WILL BE CREATED by the regulator control
    # upon SOLVE if not defined by some other device.
    bus = Instance(Bus, desc="Alternative controlled bus")

    # Time delay, in seconds, from when the voltage goes out of band to when
    # the tap changing begins. This is used to determine which regulator
    # control will act first. You may specify any floating point number to
    # achieve a model of whatever condition is necessary.
    delay = Float(15.0)

    # Indicates whether or not the regulator can be switched to regulate in the
    # reverse direction. Default is No.Typically applies only to line
    # regulators and not to LTC on a substation transformer.
    reversible = Bool(False)

    # Voltage setting in volts for operation in the reverse direction.
    rev_v_reg = Float(120.0, desc="Reverse direction voltage setting")

    # Bandwidth for operating in the reverse direction.
    rev_band = Float(3.0, desc="Reverse direction bandwidth")

    # R line drop compensator setting for reverse direction.
    rev_r = Float(0.0, desc="Reverse direction resistance")

    # X line drop compensator setting for reverse direction.
    rev_x = Float(0.0, desc="Reverse direction reactance")

    # Delay in sec between tap changes. This is how long it takes between
    # changes after the first change.
    tap_delay = Float(2.0)

    # Turn this on to capture the progress of the regulator model for each
    # control iteration.  Creates a separate file for each RegControl named
    # "REG_name.CSV".
    debug_trace = Bool(False)

    # Maximum allowable tap change per control iteration in STATIC control
    # mode. Set this to 1 to better approximate actual control action. Set this
    # to 0 to fix the tap in the current position.
    max_tap_change = Int(
        16, desc="Maximum allowable tap change per control iteration in "
        "static control"
    )

    # The time delay is adjusted inversely proportional to the amount the
    # voltage is outside the band down to 10%.
    inverse_time = Bool(False)

    # Winding containing the actual taps, if different than the WINDING
    # property. Defaults to the same winding as specified by the WINDING
    # property.
    tap_winding = Int(1)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        [
            # CircuitElement traits
            "enabled", "base_freq",
            # ControlElement traits
            "element_name", "element_terminal", "controlled_bus_name",
            "controlled_bus", "monitored_variable", "monitored_var_index",
            "time_delay", "dbl_trace_param",
            # RegulatorControl traits
            "transformer", "winding", "v_reg", "band", "pt_ratio", "ct_prim",
            "r", "x", "bus", "delay", "reversible", "rev_v_reg", "rev_band",
            "rev_r", "rev_x", "tap_delay", "debug_trace", "max_tap_change",
            "inverse_time", "tap_winding"
        ],
        id="pylon.control.regulator_control",
        resizable=True, title="Regulator Control",
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  RegulatorControl table editor:
#------------------------------------------------------------------------------

regulator_controls_table_editor = TableEditor(
    columns=[
        # CircuitElement traits
        CheckboxColumn(name="enabled"),
        CircuitElementColumn(name="base_freq"),
        # ControlElement traits
        CircuitElementColumn(name="element_name"),
        CircuitElementColumn(name="element_terminal"),
        CircuitElementColumn(name="controlled_bus_name"),
        CircuitElementColumn(name="controlled_bus"),
        CircuitElementColumn(name="monitored_variable"),
        CircuitElementColumn(name="monitored_var_index"),
        CircuitElementColumn(name="time_delay"),
        CircuitElementColumn(name="dbl_trace_param"),
        # RegulatorControl traits
        CircuitElementColumn(name="element"),
        CircuitElementColumn(name="terminal"),
        CircuitElementColumn(name="capacitor"),
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="transformer"),
        CircuitElementColumn(name="winding"),
        CircuitElementColumn(name="v_reg"),
        CircuitElementColumn(name="band"),
        CircuitElementColumn(name="pt_ratio"),
        CircuitElementColumn(name="ct_prim"),
        CircuitElementColumn(name="r"),
        CircuitElementColumn(name="x"),
        CircuitElementColumn(name="bus"),
        CircuitElementColumn(name="delay"),
        CircuitElementColumn(name="reversible"),
        CircuitElementColumn(name="rev_v_reg"),
        CircuitElementColumn(name="rev_band"),
        CircuitElementColumn(name="rev_r"),
        CircuitElementColumn(name="rev_x"),
        CircuitElementColumn(name="tap_delay"),
        CircuitElementColumn(name="debug_trace"),
        CircuitElementColumn(name="max_tap_change"),
        CircuitElementColumn(name="inverse_time"),
        CircuitElementColumn(name="tap_winding"),
    ],
    show_toolbar=True,
    deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=RegulatorControl,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    RegulatorControl().configure_traits()

# EOF -------------------------------------------------------------------------
