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

""" A generic (i.e. available for any problem) Human Player """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Standard library imports.
import logging
from os import path

from enthought.traits.api import \
    HasTraits, List, Instance, Property, Delegate, String, implements

from enthought.traits.ui.api import \
    View, Group, Item, InstanceEditor

from pyqle.environment.i_action import IAction
from pyqle.selector.i_selector import ISelector

# Setup a logger for this module.
logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

ICON_LOCATION = path.join(path.dirname(__file__), "../ui/icons")

#------------------------------------------------------------------------------
#  "HumanSelector" class:
#------------------------------------------------------------------------------

class HumanSelector(HasTraits):
    """ A generic (i.e. available for any problem) Human Player """

    implements(ISelector)

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Human readable identifier
    name = String("Human Selector")

    # The list of actions from which to select:
    actions = List(IAction)

#    action_descriptions = Property(List(String), depends_on=["action_list"])

    chosen_action = Instance(IAction, auto_set=True)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(Item("name"))

    choice_view = View(
        Item(
            name="chosen_action",
            editor=InstanceEditor(name="actions", editable=False)
        ),
        Item(name="chosen_action", style="custom"),
#        Item(name="chosen_action", style="custom"),
        id="human_selector.configure_view", title="Human Selector",
        resizable = True, buttons=["OK"],
        # Ensure closing via the dialog close button is the same
        # as clicking ok.
        close_result=True,
    )

    #--------------------------------------------------------------------------
    #  "ISelector" interface:
    #--------------------------------------------------------------------------

    def choose(self, state, action_list):
        """ Lists the actions and asks the human to choose """

        self.actions = [action for action in action_list]

        # Select the first action by default:
        if len(self.actions):
            self.chosen_action = self.actions[0]
        else:
            raise ValueError, "No actions from which to select"

        self.configure_traits(kind="livemodal", view="choice_view")

        return self.chosen_action


    def learn(self, starting_state, action, resulting_state, reward):
        """ Learning  is left to the human """

        pass


#    def __str__(self):
#        return self.name

# EOF -------------------------------------------------------------------------
