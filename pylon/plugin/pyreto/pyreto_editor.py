#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Pyreto editors.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import on_trait_change
from enthought.traits.ui.api import View, Group, Item, HGroup, VGroup, Tabbed

from envisage.resource.resource_editor import ResourceEditor

#-------------------------------------------------------------------------------
#  Participant factory function:
#-------------------------------------------------------------------------------

def participant_factory(**row_factory_kw):
    """ A factory that provides a ParticipantEnvironment association.
    """
    if "__table_editor__" in row_factory_kw:
#        swarm = row_factory_kw["__table_editor__"].object

#        env = ParticipantEnvironment()
#        agent = ElementaryAgent(environment=env)

        del row_factory_kw["__table_editor__"]

        return None

#------------------------------------------------------------------------------
#  "SwarmTableEditor" class:
#------------------------------------------------------------------------------

class SwarmTableEditor(ResourceEditor):
    """ Defines a workbench editor for editing swarm resources with
        tabular views.
    """

    #--------------------------------------------------------------------------
    #  "ResourceEditor" interface
    #--------------------------------------------------------------------------

    def _create_view(self):
        """ Create a view with a tree editor.
        """
        elementary_agents_table_editor.on_select = self._on_select
        elementary_agents_table_editor.row_factory = participant_factory
        elementary_agents_table_editor.row_factory_kw = {"__table_editor__":""}
        elementary_agents_table_editor.edit_view = " "

        view = View(
            Tabbed(
                Group(
                    Item(
                        name="elementary_agents",
                        editor=elementary_agents_table_editor,
                        show_label=False, id=".elementary_agents_table"
                    ),
                    label="Participants"#, show_border=True
                ),
                Group(
                    Item(name="environment", show_label=False, style="custom"),
                    label="Environment",# show_border=True,
                    scrollable=True
                ),
                dock="tab", springy=True
            ),
            id="pylon.plugin.pyreto.pyreto_editor.swarm_view"
        )

        return view


    def _on_select(self, object):
        """ Handle tree node selection.
        """
        self.selected = object


    @on_trait_change(
        "document.elementary_agents.+,"
        "document.elementary_agents.selector.+,"
        "document.environment.+"
    )
    def on_swarm_modified(self):
        """ Handle modification to the swarm.
        """
        self.dirty = True

# EOF -------------------------------------------------------------------------
