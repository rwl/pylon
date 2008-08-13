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

""" Defaines an action for running a Python file """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.io.api import File
from enthought.traits.api import Instance
from enthought.traits.ui.menu import Action
from enthought.pyface.api import ImageResource
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow


#------------------------------------------------------------------------------
#  "RunAsPythonAction" class:
#------------------------------------------------------------------------------

class PythonRunAction(Action):
    """ Action for running a Python file """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Run the file in the Python shell"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Python Run"

    # A short description of the action used for tooltip text etc:
    tooltip = "Python Run"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("python")

    # Keyboard accelerator:
    accelerator = "Ctrl+R"

    #--------------------------------------------------------------------------
    #  "DCOPFAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "DCOPFAction" interface:
    #--------------------------------------------------------------------------

    def _selection_changed_for_window(self, new):
        """ Enables the action when a File object is selected """

        if len(new) == 1:
            selection = new[0]
            if isinstance(selection, File) and (selection.ext == ".py"):
                self.enabled = True
            else:
                self.enabled = False
        else:
            self.enabled = False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def _enabled_default(self):
        """ Trait initialiser """

        if self.window.selection:
            sel = self.window.selection[0]
            if isinstance(sel, File) and (sel.ext == ".py"):
                return True
            else:
                return False
        else:
            return False


    def perform(self, event):
        """ Perform the action. """

        selected = self.window.selection[0]

        # The file must be saved first!
#        self.save()

        # Execute the code.
        if len(selected.path) > 0:
            view = self.window.get_view_by_id(
                'enthought.plugins.python_shell_view'
            )

            if view is not None:
                view.execute_command(
                    'execfile(r"%s")' % selected.path, hidden=False
                )

        return

# EOF -------------------------------------------------------------------------
