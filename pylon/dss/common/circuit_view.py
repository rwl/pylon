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

from pylon.dss.delivery.fault import faults_table_editor
from pylon.dss.conversion.voltage_source import voltage_sources_table_editor
from pylon.dss.conversion.current_source import current_sources_table_editor

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
            Item(name="faults", editor=faults_table_editor, show_label=False),
            label="Faults"
        ),
        Group(
            Item(
                name="voltage_sources", editor=voltage_sources_table_editor,
                show_label=False
            ),
            label="Voltage Sources"
        ),
        Group(
            Item(
                name="current_sources", editor=current_sources_table_editor,
                show_label=False
            ),
            label="Current Sources"
        ),
        Group(Item(name="meter_elements"), label="Meters"),
        Group(Item(name="generators"), label="Generators"),
        Group(Item(name="transformers"), label="Transformers"),
        Group(Item(name="cap_controls"), label="Capacitor Controls"),
        Group(Item(name="reg_controls"), label="Regulator Controls"),
        Group(Item(name="lines"), label="Lines"),
        Group(Item(name="loads"), label="Loads"),
        Group(Item(name="shunt_capacitors"), label="Shunt Capacitors"),
    ),
    id="pylon.dss.ui.circuit"
)

# EOF -------------------------------------------------------------------------
