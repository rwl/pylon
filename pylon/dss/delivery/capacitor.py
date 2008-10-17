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

""" Defines a capacitor """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    Instance, List, Int, Float, Enum, Either, Array, Bool

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.circuit_element import CircuitElementColumn

from pylon.dss.common.bus import Bus

from power_delivery_element import PowerDeliveryElement

#------------------------------------------------------------------------------
#  "Capacitor" class:
#------------------------------------------------------------------------------

class Capacitor(PowerDeliveryElement):
    """ Basic capacitor

    Implemented as a two-terminal constant impedance (Power Delivery Element)

    Bus2 connection defaults to 0 node of Bus1 (if Bus2 has the default bus
    connection at the time Bus1 is defined.  Therefore, if only Bus1 is
    specified, a shunt capacitor results.
    If delta connected, Bus2 is set to node zero of Bus1 and nothing is
    returned in the lower half of YPrim - all zeroes.

    If an ungrounded wye is desired, explicitly set Bus2= and set all nodes the
    same, e.g. Bus1.4.4.4   (uses 4th node of Bus1 as neutral point)
    or BusNew.1.1.1  (makes a new bus for the neutral point)
    You must specify the nodes or you will get a series capacitor!

    A series capacitor is specified simply by setting bus2 and declaring the
    connection to be Wye.  If the connection is specified as delta, nothing
    will be connected to Bus2. In fact the number of terminals is set to 1.

    Capacitance may be specified as:

     1.  kvar and kv ratings at base frequency.  impedance.  Specify kvar as
         total for
         all phases (all cans assumed equal). For 1-phase, kV = capacitor can
         kV rating. For 2 or 3-phase, kV is line-line three phase. For more
         than 3 phases, specify kV as actual can voltage.
     2.  Capacitance in uF to be used in each phase.  If specified in this
         manner, the given value is always used whether wye or delta.
     3.  A nodal C matrix (like a nodal admittance matrix).
         If conn=wye then 2-terminal through device
         If conn=delta then 1-terminal.
         Microfarads.

    """

    # Name of first bus. Examples:
    #     bus1=busname bus1=busname.1.2.3
    bus_1 = Instance(Bus)

    # Name of 2nd bus. Defaults to all phases connected to first bus, node 0.
    # (Shunt Wye Connection) Not necessary to specify for delta (LL) connection
    bus_2 = Instance(Bus)

    # Number of phases.
    phases = Int(3)

    # Total kvar, if one step, or ARRAY of kvar ratings for each step. Evenly
    # divided among phases. See rules for NUMSTEPS.
    kvar = Float(1200.0) #Either(Float(1200.0), List(Float))

    # For 2, 3-phase, kV phase-phase. Otherwise specify actual can rating.
    kv = Float(12.47)

    # {wye | delta |LN |LL}  Default is wye, which is equivalent to LN
    conn = Enum("Wye", "Delta", "LN", "LL")

    # Nodal cap. matrix, lower triangle, microfarads, of the following form:
    #     cmatrix="c11 | -c21 c22 | -c31 -c32 c33"
    # All steps are assumed the same if this property is used.
    c_matrix = Array(desc="Nodal capacitance matrix")

    # ARRAY of Capacitance, each phase, for each step, microfarads.
    # See Rules for NumSteps.
    cuf = List(Float, desc="Capacitance for each phase")

    # ARRAY of series resistance in each phase (line), ohms.
    r = List(Float, desc="Series resistance in each phase")

    # ARRAY of series inductive reactance(s) in each phase (line) for filter,
    # ohms at base frequency. Use this OR "h" property to define filter.
    xl = List(Float, desc="Series inductive reactance in each phase")

    # ARRAY of harmonics to which each step is tuned. Zero is interpreted as
    # meaning zero reactance (no filter).
    harm = List(Float, desc="Harmonics to which each step is tuned")

    # Number of steps in this capacitor bank. Default = 1. Forces reallocation
    # of the capacitance, reactor, and states array.  Rules:
    # If this property was previously =1, the value in the kvar property is
    # divided equally among the steps. The kvar property does not need to be
    # reset if that is accurate.  If the Cuf or Cmatrix property was used
    # previously, all steps are set to the value of the first step.
    # The states property is set to all steps on. All filter steps are set to
    # the same harmonic.
    # If this property was previously >1, the arrays are reallocated, but no
    # values are altered. You must SUBSEQUENTLY assign all array properties.
    n_steps = Int(1, desc="Number of steps in this capacitor bank")

    # ARRAY of integers {1|0} states representing the state of each step
    # (on|off). Defaults to 1 when reallocated (on).
    # Capcontrol will modify this array as it turns steps on or off.
    states = List(Bool)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        [
            # CircuitElement traits
            "enabled", "base_freq",
            # PowerDeliveryElement traits
            "norm_amps", "emerg_amps", "fault_rate", "pct_perm", "repair",
            # Capacitor traits
            "bus_1", "bus_2", "phases", "kvar", "kv", "conn", "c_matrix",
            "cuf", "r", "xl", "harm", "n_steps", "states"
        ],
        id="pylon.delivery.capacitor",
        resizable=True, title="Capacitor",
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  Capacitor table editor:
#------------------------------------------------------------------------------

capacitors_table_editor = TableEditor(
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
        # Capacitor traits
        CircuitElementColumn(name="bus_1"),
        CircuitElementColumn(name="bus_2"),
        CircuitElementColumn(name="phases"),
    ],
    other_columns = [  # not initially displayed
        CircuitElementColumn(name="kvar"),
        CircuitElementColumn(name="kv"),
        CircuitElementColumn(name="conn"),
        CircuitElementColumn(name="c_matrix"),
        CircuitElementColumn(name="cuf"),
        CircuitElementColumn(name="r"),
        CircuitElementColumn(name="xl"),
        CircuitElementColumn(name="harm"),
        CircuitElementColumn(name="n_steps"),
        CircuitElementColumn(name="states")
    ],
    show_toolbar=True, deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=Capacitor,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Capacitor().configure_traits()

# EOF -------------------------------------------------------------------------
