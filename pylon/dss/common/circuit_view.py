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

""" Defines view for a container of circuit elements """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.ui.api import View, Item, Group, HGroup, Tabbed

from pylon.dss.common.bus import buses_table_editor
from pylon.dss.delivery.fault import faults_table_editor
from pylon.dss.conversion.voltage_source import voltage_sources_table_editor
from pylon.dss.conversion.current_source import current_sources_table_editor
from pylon.dss.conversion.generator import generators_table_editor
from pylon.dss.delivery.transformer import transformers_table_editor
from pylon.dss.control.capacitor_control import capacitor_controls_table_editor
from pylon.dss.control.regulator_control import regulator_controls_table_editor
from pylon.dss.delivery.line import lines_table_editor
from pylon.dss.conversion.load import loads_table_editor
from pylon.dss.delivery.capacitor import capacitors_table_editor

#------------------------------------------------------------------------------
#  Default view:
#------------------------------------------------------------------------------

circuit_view = View(
    Tabbed(
        HGroup(
            Group(
                Item("case_name"),
                Item("fundamental"),
                Item("is_solved", style="readonly"),
                Item("allow_duplicates"),
                Item("zones_locked"),
                Item("positive_sequence"),
                "_",
                Item("normal_min_volts"),
                Item("normal_max_volts"),
                Item("emerg_min_volts"),
                Item("emerg_max_volts"),
                Item("legal_voltage_bases"),
            ),
            Group(
                Item("generator_dispatch_ref"),
                Item("default_growth_rate"),
                Item("default_growth_factor"),
                Item("gen_multiplier"),
                Item("harm_mult"),
                Item("default_hour_mult"),
                Item("price_signal"),
            ),
            label="General"
        ),
        Group(
            Item(name="buses", editor=buses_table_editor, show_label=False),
            label="Buses", id=".buses_table"
        ),
        Group(
            Item(name="lines", editor=lines_table_editor, show_label=False),
            label="Lines", id=".lines_table"
        ),
        Group(
            Item(
                name="transformers", editor=transformers_table_editor,
                show_label=False, id=".transformers_table"
            ),
            label="Transformers"
        ),
        Group(
            Item(
                name="generators", editor=generators_table_editor,
                show_label=False, id=".generators_table"
            ),
            label="Generators"
        ),
        Group(
            Item(name="loads", editor=loads_table_editor, show_label=False),
            label="Loads", id=".loads_table"
        ),
        Group(
            Item(name="faults", editor=faults_table_editor, show_label=False),
            label="Faults", id=".faults_table"
        ),
        Group(
            Item(
                name="voltage_sources", editor=voltage_sources_table_editor,
                show_label=False, id=".voltage_sources_table"
            ),
            label="Voltage Sources"
        ),
        Group(
            Item(
                name="current_sources", editor=current_sources_table_editor,
                show_label=False, id=".current_sources_table"
            ),
            label="Current Sources"
        ),
        Group(
            Item(
                name="shunt_capacitors", editor=capacitors_table_editor,
                show_label=False
            ),
            label="Shunt Capacitors", id=".capacitors_table"
        ),
#        Group(Item(name="meter_elements"), label="Meters"),
        Group(
            Item(
                name="cap_controls", editor=capacitor_controls_table_editor,
                show_label=False, id=".capacitor_controls_table"
            ),
            label="Capacitor Controls"
        ),
        Group(
            Item(
                name="reg_controls", editor=regulator_controls_table_editor,
                show_label=False, id=".regulator_controls_table"
            ),
            label="Regulator Controls"
        ),
        dock="tab", springy=True
    ),
    id="pylon.dss.ui.circuit"
)

# EOF -------------------------------------------------------------------------
