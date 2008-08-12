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

""" The environment as perceived by a participant """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.traits.api import HasTraits, List, Instance, Any, Float, Either
from enthought.traits.ui.api import View, Group, Item, DropEditor, HGroup
from enthought.pyface.image_resource import ImageResource

from pyqle.environment.elementary_environment import ElementaryEnvironment

from pylon.pyreto.market_action import MarketAction
from pylon.pyreto.market_environment import MarketEnvironment
from pylon.api import Generator, Load

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.ui.api.__file__)

#------------------------------------------------------------------------------
#  "ParticipantEnvironment" class:
#------------------------------------------------------------------------------

class ParticipantEnvironment(ElementaryEnvironment):
    """ The environment as perceived by a participant """

    # Assets in the agents local environment:
#    assets = List(Either(Instance(Generator), Instance(Load)))
#    asset = Either(Instance(Generator), Instance(Load))
    asset = Instance(HasTraits, desc="Assets in the agents local environment")

    # Rated maximum for asset
    max = Float(desc="Rated maximum for asset")

    # Rated minimum for asset
    min = Float(desc="Rated minimum for asset")

    # Default view:
    traits_view = View(
        HGroup(
            Item(name="max"),
            Item(name="min"),
        ),
        Item(
            name="asset", style="readonly", show_label=False,
            editor=DropEditor(klass=HasTraits)
        ),
        Item(name="asset", show_label=False, style="simple"),
        id="pylon.pyreto.participant_environment_view",
        icon=ImageResource("frame.ico", search_path=[IMAGE_LOCATION]),
        resizable=True
    )

    #--------------------------------------------------------------------------
    #  "ParticipantEnvironment" interface:
    #--------------------------------------------------------------------------

    def _asset_changed(self, new):
        """ Handle the asset changing """

        if isinstance(new, Generator):
            self.max = new.p_max
            self.min = new.p_min
        elif isinstance(new, Load):
            self.max = new.p
            self.min = 0
        else:
            raise ValueError

    #--------------------------------------------------------------------------
    #  "ElementaryEnvironment" interface:
    #--------------------------------------------------------------------------

    def _get_action_list(self, state):
        """ Gives the list of possible actions from a given state """

        if isinstance(self.asset, Generator):
            min_action = MarketAction(
                name="Minimum", asset=self.asset, value=self.min
            )
            max_action = MarketAction(
                name="Maximum", asset=self.asset, value=self.max
            )
            actions = [max_action]

        elif isinstance(self.asset, Load):
            n_actions = 10
            actions = []
            for i in range(1, n_actions+1):
                val = self.max/n_actions * i
                action = MarketAction(
                    name="Profiled "+str(i), asset=self.asset,
                    value=val
                )
                actions.append(action)
        else:
            actions = []

        return actions


    def _initial_state_default(self):
        """ State is obtained from the swarm environment """

        return None


    def _get_reward(self):
        """ The swarm environment returns the rewards """

        return None


    def _get_is_final(self):
        """ Final state determined by the swarm environment """

        return None


    def _get_winner(self):
        """ No meaning here """

        return None

# EOF -------------------------------------------------------------------------
