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

""" Defines an ideal current source """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Enum

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.dss.common.circuit_element import CircuitElementColumn

from pylon.dss.common.bus import Bus

from power_conversion_element import PowerConversionElement

#------------------------------------------------------------------------------
#  "CurrentSource" class:
#------------------------------------------------------------------------------

class CurrentSource(PowerConversionElement):
    """ Ideal current source.

    ISource maintains a positive sequence for harmonic scans.  If you want zero
    sequence, use three single-phase ISource.

    """

    # Name of bus to which source is connected.
    bus_1 = Instance(Bus)

    # Magnitude of current source, each phase, in Amps.
    amps = Float(0.0, desc="Current source magnitude")

    # Phase angle in degrees of first phase. Phase shift between phases is
    # assumed 120 degrees when number of phases <= 3
    angle = Float(0.0, desc="Phase angle of the first phase")

    # Source frequency.  Defaults to  circuit fundamental frequency.
    frequency = Float(60.0)

    # Number of phases. For 3 or less, phase shift is 120 degrees.
    phases = Int(3)

    # {pos*| zero | none} Maintain specified sequence for harmonic solution.
    # Otherwise, angle between phases rotates with harmonic.
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
            "bus_1", "amps", "angle", "frequency", "phases", "scan_type"
        ],
        id="pylon.conversion.current_source",
        resizable=True,
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  CurrentSource table editor:
#------------------------------------------------------------------------------

current_sources_table_editor = TableEditor(
    columns=[
        # CircuitElement traits
        CheckboxColumn(name="enabled"),
        CircuitElementColumn(name="base_freq"),
        # PowerConversionElement traits
        CircuitElementColumn(name="spectrum"),
        CircuitElementColumn(name="inj_current"),
        # VoltageSource traits
        CircuitElementColumn(name="bus_1"),
        CircuitElementColumn(name="amps"),
        CircuitElementColumn(name="angle"),
        CircuitElementColumn(name="frequency"),
        CircuitElementColumn(name="phases"),
        CircuitElementColumn(name="scan_type"),
    ],
    show_toolbar=True,
    deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=CurrentSource,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    CurrentSource().configure_traits()

# EOF -------------------------------------------------------------------------
