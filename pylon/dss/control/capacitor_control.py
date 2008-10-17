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

""" Defines a capacitor controller """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Bool, Enum

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.circuit_element import CircuitElementColumn

from pylon.dss.delivery.api import PowerDeliveryElement, Capacitor

from control_element import ControlElement

#------------------------------------------------------------------------------
#  "CapacitorControl" class:
#------------------------------------------------------------------------------

class CapacitorControl(ControlElement):
    """ A CapacitorControl is a control element that is connected to a terminal of
    another circuit element and controls a capacitor.  The control is usually
    placed in the terminal of a line or transformer, although a voltage control
    device could be placed in the terminal of the capacitor it controls.

    Capacitor to be controlled must already exist.

    """

    # Full object name of the circuit element, typically a line or transformer,
    # to which the capacitor control's PT and/or CT are connected. There is no
    # default; must be specified.
    element = Instance(
        PowerDeliveryElement, allow_none=False, desc="Circuit element to which"
        "the capacitor control's PT and/or CT is connected"
    )

    # Number of the terminal of the circuit element to which the CapControl is
    # connected. 1 or 2, typically.  Default is 1.
    terminal = Int(1, desc="Connected terminal of the circuit element")

    # Name of Capacitor element which the CapControl controls. No Default; Must
    # be specified.Do not specify the full object name; "Capacitor" is assumed
    # for the object class.
    capacitor = Instance(
        Capacitor, allow_none=False, desc="Capacitor being controlled"
    )

    # {Current | voltage | kvar |time } Control type.  Specify the ONsetting
    # and OFFsetting appropriately with the type of control. (See help for
    # ONsetting)
    type = Enum("Current", "Voltage", "kVar", "Time", desc="Control type")

    # Ratio of the PT that converts the monitored voltage to the control
    # voltage. Default is 60.  If the capacitor is Wye, the 1st phase
    # line-to-neutral voltage is monitored.  Else, the line-to-line voltage
    # (1st - 2nd phase) is monitored.
    pt_ratio = Float(
        60.0, desc="Ratio of the PT that converts the monitored voltage to "
        "the control voltage"
    )

    # Ratio of the CT from line amps to control ampere setting for current and
    # kvar control types.
    ct_ratio = Float(
        60.0, desc="Ratio of the CT from line amps to control amps"
    )

    # Value at which the control arms to switch the capacitor ON (or ratchet up
    # a step).  Type of Control:
    #    Current: Line Amps / CTratio
    #    Voltage: Line-Neutral (or Line-Line for delta) Volts / PTratio
    #    kvar:    Total kvar, all phases (3-phase for pos seq model). This is
    #    directional.
    #    Time:    Hrs from Midnight as a floating point number (decimal).
    #    7:30am would be entered as 7.5.
    on_setting = Float(
        300.0, desc="Value at which the control switches the capacitor on"
    )

    # Value at which the control arms to switch the capacitor OFF. (See help
    # for ONsetting)
    off_setting = Float(
        200.0, desc="Value at which the control switches the capacitor off"
    )

    # Time delay, in seconds, from when the control is armed before it sends
    # out the switching command to turn ON.  The control may reset before the
    # action actually occurs. This is used to determine which capacity control
    # will act first. Default is 15.  You may specify any floating point number
    # to achieve a model of whatever condition is necessary.
    delay = Float(
        15.0, desc="Time delay, in seconds, from when the control is armed "
        "before it sends out the switching command to turn on"
    )

    # Switch to indicate whether VOLTAGE OVERRIDE is to be considered. Vmax and
    # Vmin must be set to reasonable values if this property is Yes.
    volt_override = Bool(False)

    # Maximum voltage, in volts.  If the voltage across the capacitor divided
    # by the PTRATIO is greater than this voltage, the capacitor will switch
    # OFF regardless of other control settings. Default is 126 (goes with a PT
    # ratio of 60 for 12.47 kV system).
    v_max = Float(126.0)

    # Minimum voltage, in volts.  If the voltage across the capacitor divided
    # by the PTRATIO is less than this voltage, the capacitor will switch ON
    # regardless of other control settings. Default is 115 (goes with a PT
    # ratio of 60 for 12.47 kV system).
    v_min = Float(115.0)

    # Time delay, in seconds, for control to turn OFF when present state is ON.
    delay_off = Float(15.0)

    # Dead time after capacitor is turned OFF before it can be turned back ON.
    dead_time = Float(300.0)

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
            # CacacitorControl traits
            "element", "terminal", "capacitor", "type", "pt_ratio", "ct_ratio",
            "on_setting", "off_setting", "delay", "volt_override", "v_max",
            "v_min", "delay_off", "dead_time"
        ],
        id="pylon.conversion.capacitor_control",
        resizable=True, title="Capacitor Control",
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  CapacitorControl table editor:
#------------------------------------------------------------------------------

capacitor_controls_table_editor = TableEditor(
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
        # CapacitorControl traits
        CircuitElementColumn(name="element"),
        CircuitElementColumn(name="terminal"),
        CircuitElementColumn(name="capacitor"),
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="type"),
        CircuitElementColumn(name="pt_ratio"),
        CircuitElementColumn(name="ct_ratio"),
        CircuitElementColumn(name="on_setting"),
        CircuitElementColumn(name="off_setting"),
        CircuitElementColumn(name="delay"),
        CircuitElementColumn(name="volt_override"),
        CircuitElementColumn(name="v_max"),
        CircuitElementColumn(name="v_min"),
        CircuitElementColumn(name="delay_off"),
        CircuitElementColumn(name="dead_time"),
    ],
    show_toolbar=True,
    deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=CapacitorControl,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    CapacitorControl().configure_traits()

# EOF -------------------------------------------------------------------------
