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

""" A player which follows a profile """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from itertools import cycle

from enthought.traits.api import \
    HasTraits, List, Range, String, Float, Trait, File, Array, \
    Property, Instance, Button, implements

from enthought.traits.ui.api import View, Item, Group, Tabbed, HGroup

from enthought.chaco.chaco_plot_editor import ChacoPlotItem

from pyqle.selector.i_selector import ISelector
from pyqle.environment.i_profile_action import IProfileAction

from profile_importer import ProfileImporter

#------------------------------------------------------------------------------
#  Setup a logger for this module:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ProfileSelector" class:
#------------------------------------------------------------------------------

class ProfileSelector(HasTraits):
    """ A player which follows a profile """

    implements(ISelector)

    #--------------------------------------------------------------------------
    #  Traits definitions:
    #--------------------------------------------------------------------------

    name = String("Profile Selector")

    # The actions from which to select
    actions = List(Instance(IProfileAction))

    # The profile to be followed
    profile = List(Range(low=0.0, high=1.0), [1.0])

    # The value to which a profile value of 0.0 relates
    low_value = Float(
        0.0, desc="the value to which a profile value of 0.0 relates"
    )

    # The value to which a profile value of 1.0 relates
    high_value = Float(
        1.0, desc="the value to which a profile value of 1.0 relates"
    )

    # A CSV importer
    profile_importer = Instance(ProfileImporter)

    # The default view
    traits_view = View(
        HGroup(Item(name="low_value"), Item(name="high_value")),
        Group(
            Item(name="profile", height=150, show_label=False),
            ChacoPlotItem(
                "_index", "_profile",
                type="line",
                # Basic axis and label properties
                show_label=False, resizable=True, orientation="h",
                title="Profile",
                # Axis properties
                y_auto=False, y_bounds=(0.0, 1.0),
                x_label="Period", y_label="Coefficient",
                # Plot properties
                color="blue", bgcolor="ivory",
                # Border properties
                border_color="darkblue", #border_width=2,
                # Specific to scatter plot
                marker="circle", marker_size=2, outline_color="none",
                # Border, padding properties
                border_visible=True, border_width=1,
                padding_bg_color="aliceblue"
            ),
            label="Profile", show_border=True
        ),
        Item(name="profile_importer", show_label=False),
        title="Profile Selector",
        id="pylon.pyreto.profile_selector_view",
        resizable=True
    )

    #--------------------------------------------------------------------------
    #  Private traits:
    #--------------------------------------------------------------------------

    # An iterator that cycles through the profile indefinitely:
    _cycle = Trait(cycle, transient=True)

    # Profile plot index values
    _index = Property(Array, depends_on=["profile", "profile_items"])

    # Profile values
    _profile = Property(Array, depends_on=["profile", "profile_items"])

    #--------------------------------------------------------------------------
    #  "ProfileSelector" interface:
    #--------------------------------------------------------------------------

    def __cycle_default(self):
        """ Trait initialiser """

        if not self.profile:
            self.profile = [1.0]

        return cycle(self.profile)


    def _profile_importer_default(self):
        """ Trait initialiser """

        pi = ProfileImporter()
        # FIXME: Dynamic handler does not work
        pi.on_trait_change(self.on_profile_change, "profile")

        return pi


    def _profile_changed(self, new):
        """ Refresh the coefficient cycle """

        self._cycle = cycle(new)


    def _get_coefficient(self):
        """ Returns the next profile coefficient """

        return self._cycle.next()


    def on_profile_change(self, new):
        """ Handles a new profile from the importer """

        self.profile = new[:]

    #--------------------------------------------------------------------------
    #  "Selector" interface:
    #--------------------------------------------------------------------------

    def choose(self, state, actions):
        """ Selects an action according to the profile """

        self.actions = actions # type validation

        coeff = self._get_coefficient()
        target = coeff*(self.high_value-self.low_value)
        diffs = [abs(a.value-target) for a in actions]

        lowest = min(diffs)
        chosen = actions[diffs.index(lowest)]

        logger.debug(
            "Selector [%s] chose action [%s] with value: %f" %
            (self.name, chosen.name, chosen.value)
        )

        return chosen


    def learn(self, starting_state, action, resulting_state, reward):
        """ There is no learning for this algorithm """

        pass


#    def __str__(self):
#        """ String representation """
#
#        return self.name

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

    def _get__index(self):
        """ Property getter """

        if self.profile:
            return [i for i in range(len(self.profile)+1)]
        else:
            return [0]


    def _get__profile(self):
        """ Property getter """

        if self.profile:
            return self.profile[:]
        else:
            return [0]

# EOF -------------------------------------------------------------------------
