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

""" Action for solving the DC Power Flow problem """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.io.api import File
from enthought.traits.api import Instance, Callable
from enthought.traits.ui.menu import Action
from enthought.pyface.api import ImageResource
from enthought.plugins.workspace.resource_editor import PickledProvider
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from pylon.api import Network
from pylon.ui.routine.dc_pf_view_model import DCPFViewModel

#------------------------------------------------------------------------------
#  "DCPFAction" class:
#------------------------------------------------------------------------------

class DCPFAction(Action):
    """ Action for solving the DC Power Flow problem """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Solve the DC Power Flow for the current network"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&DC PF"

    # A short description of the action used for tooltip text etc:
    tooltip = "DC Power Flow"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("dc.png")

    # Keyboard accelerator:
    accelerator = "Alt+D"

    #--------------------------------------------------------------------------
    #  "DCPFAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "DCPFAction" interface:
    #--------------------------------------------------------------------------

    def _selection_changed_for_window(self, new):
        """ Enables the action when a File object is selected """

        if len(new) == 1:
            selection = new[0]
            if isinstance(selection, File) and (selection.ext == ".pyl"):
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
            if isinstance(sel, File) and (sel.ext == ".pyl"):
                return True
            else:
                return False
        else:
            return False


    def perform(self, event):
        """ Perform the action. """

        selected = self.window.selection[0]
        provider = PickledProvider()
        network = provider.create_document(selected)

        if isinstance(network, Network):
            vm = DCPFViewModel(network=network)
            vm.run = True
            vm.edit_traits(parent=self.window.control, kind="livemodal")

            provider.do_save(selected, network)

        return

# EOF -------------------------------------------------------------------------
