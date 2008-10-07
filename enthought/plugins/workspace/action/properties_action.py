#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Richard W. Lincoln
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Richard W. Lincoln
#  Date:   24/07/2008
#
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
