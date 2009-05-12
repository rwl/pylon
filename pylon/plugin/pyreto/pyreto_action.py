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

""" Workbench actions for the Pyreto plug-in.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.traits.api import Instance, Callable
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar
from enthought.envisage.ui.workbench.api import WorkbenchActionSet
from enthought.pyface.api import ImageResource, FileDialog, OK
from enthought.pyface.action.api import Action as PyFaceAction

from pylon.plugin.pyreto.experiment_wizard import ExperimentWizard

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_PATH = join(dirname(__file__), "..", "..", "ui", "images")

#------------------------------------------------------------------------------
#  "NewExperimentAction" class:
#------------------------------------------------------------------------------

class NewExperimentAction(PyFaceAction):
    """ An action for creating a new Pyreto experiment resource.
    """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Create a new experiment"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Experiment"

    # A short description of the action used for tooltip text etc:
    tooltip = "New Experiment"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("psse", search_path=[IMAGE_PATH])

    #--------------------------------------------------------------------------
    #  "NewExperimentAction" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action.
        """
        wizard = ExperimentWizard(parent=self.window.control,
            window=self.window, title="New Experiment")

        # Open the wizard
        if wizard.open() == OK:
            wizard.finished = True

#------------------------------------------------------------------------------
#  "PyretoActionSet" class:
#------------------------------------------------------------------------------

class PyretoActionSet(WorkbenchActionSet):
    """ An action set for the Pyreto plug-in.
    """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier.
    id = "pylon.plugin.pyreto.workbench_action_set"

    # The menus in this set
    menus = [ Menu(name="&New", path="MenuBar/File", group="OpenGroup",
        groups=["ContainerGroup", "ComponentGroup", "OtherGroup"]) ]

    # The actions in this set.
    actions = [
        Action(path="MenuBar/File/New", group="ComponentGroup",
            class_name="pylon.plugin.pyreto.pyreto_action:NewExperimentAction"),
        Action(path="Resource/New", group="ComponentGroup",
            class_name="pylon.plugin.pyreto.pyreto_action:NewExperimentAction")
    ]

# EOF -------------------------------------------------------------------------
