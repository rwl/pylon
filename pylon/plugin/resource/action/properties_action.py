#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" Defines an action for viewing resource properties """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.io.api import File
from enthought.traits.api import Bool, Instance
from enthought.traits.ui.api import View, Item, Group
from enthought.pyface.action.api import Action

#------------------------------------------------------------------------------
#  "PropertiesAction" class:
#------------------------------------------------------------------------------

class PropertiesAction(Action):
    """ Defines an action for viewing resource properties """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "P&roperties"

    # Keyboard accelerator:
    accelerator = "Alt+Enter"

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        selections = self.window.selection

        if selections:
            selection = selections[0]
            if isinstance(selection, File):
                selection.edit_traits(
                    parent=self.window.control,
                    view=self._create_resource_view(selection),
                    kind="livemodal"
                )

    def _create_resource_view(self, selection):
        """ Creates a resource view """

        resource_view = View(
            Item(name="absolute_path", style="readonly"),
            # FIXME: Readonly boolean editor is just blank
#            Item(name="exists", style="readonly"),
#            Item(name="is_file", style="readonly"),
#            Item(name="is_folder", style="readonly"),
#            Item(name="is_package", style="readonly"),
#            Item(name="is_readonly", style="readonly"),
            Item(name="mime_type", style="readonly"),
            Item(name="url", style="readonly"),
            title="Properties for %s" % selection.name+selection.ext,
            icon=self.window.application.icon
        )

        return resource_view

# EOF -------------------------------------------------------------------------
