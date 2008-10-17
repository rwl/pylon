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

""" Defines a fault """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Enum, Array, Bool

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.bus import Bus

from power_delivery_element import PowerDeliveryElement

from pylon.dss.common.circuit_element import CircuitElementColumn

#------------------------------------------------------------------------------
#  "Fault" class:
#------------------------------------------------------------------------------

class Fault(PowerDeliveryElement):
    """ One or more faults can be placed across any two buses in the circuit.
    Like the capacitor, the second bus defaults to the ground node of the
    same bus that bus1 is connected to.

    The fault is basically an uncoupled, multiphase resistance branch. however,
    you may also specify it as NODAL CONDUCTANCE (G) matrix, which will give
    you complete control of a complex fault situation.

    To eliminate a fault from the system after it has been defined, disable it.

    In Monte Carlo Fault mode, the fault resistance is varied by the % std dev
    specified If %Stddev is specified as zero (default), the resistance is
    varied uniformly.

    Fault may have its "ON" time specified (defaults to 0). When Time (t)
    exceeds this value, the fault will be enabled.  Else it is disabled.

    Fault may be designated as Temporary.  That is, after it is enabled, it
    will disable itself if the fault current drops below the MinAmps value.

    """

    # Name of first bus.
    bus_1 = Instance(Bus)

    # Name of 2nd bus.
    bus_2 = Instance(Bus)

    # Number of phases.
    phases = Int(1)

    # Resistance, each phase, ohms. Default is 0.0001. Assumed to be Mean value
    # if gaussian random mode.Max value if uniform mode.  A Fault is actually a
    # series resistance that defaults to a wye connection to ground on the
    # second terminal.  You may reconnect the 2nd terminal to achieve whatever
    # connection.  Use the Gmatrix property to specify an arbitrary conductance
    # matrix.
    r = Float(0.0001)

    # Percent standard deviation in resistance to assume for Monte Carlo fault
    # (MF) solution mode for GAUSSIAN distribution. Default is 0 (no variation
    # from mean).
    pct_std_dev = Float(0.0, desc="Percent standard deviation in resistance")

    # Use this to specify a nodal conductance (G) matrix to represent some
    # arbitrary resistance network. Specify in lower triangle form as usual for
    # DSS matrices.
    g_matrix = Array(desc="Nodal conductance matrix")

    # Time (sec) at which the fault is established for time varying
    # simulations. Default is 0.0 (on at the beginning of the simulation)
    on_time = Float(0.0, desc="Time at which the fault is established")

    # Designate whether the fault is temporary.  For Time-varying simulations,
    # the fault will be removed if the current through the fault drops below
    # the MINAMPS criteria.
    temporary = Bool(False)

    # Minimum amps that can sustain a temporary fault.
    min_amps = Float(
        5.0, desc="Minimum amps that can sustain a temporary fault"
    )

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        # CircuitElement traits
        Item("enabled"),
        Item("base_freq"),
        # PowerDeliveryElement traits
        Item("norm_amps"),
        Item("emerg_amps"),
        Item("fault_rate"),
        Item("pct_perm"),
        Item("repair"),
        # Fault traits
        Item("bus_1"),
        Item("bus_2"),
        Item("phases"),
        Item("r"),
        Item("pct_std_dev"),
        Item("g_matrix"),
        Item("on_time"),
        Item("temporary"),
        Item("min_amps"),
        id="pylon.delivery.fault",
        resizable=True,
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  Faults table editor:
#------------------------------------------------------------------------------

faults_table_editor = TableEditor(
    columns=[
        # CircuitElement traits
        CheckboxColumn(name="enabled"),
        CircuitElementColumn(name="base_freq"),
        # PowerDeliveryElement traits
        CircuitElementColumn(name="norm_amps"),
        CircuitElementColumn(name="emerg_amps"),
        CircuitElementColumn(name="fault_rate"),
        CircuitElementColumn(name="pct_prem"),
        CircuitElementColumn(name="repair"),
        # Fault traits
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
        CircuitElementColumn(name="phases"),
        CircuitElementColumn(name="r"),
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="pct_std_dev"),
        CircuitElementColumn(name="on_time"),
        CircuitElementColumn(name="temporary"),
        CircuitElementColumn(name="min_amps")
    ],
#    show_toolbar=True,
    deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=Fault,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Fault().configure_traits()

# EOF -------------------------------------------------------------------------
