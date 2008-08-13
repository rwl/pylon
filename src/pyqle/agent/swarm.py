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

""" A Swarm is composed of several Agents, each one with its own selector. A
Swarm has no selector of its own.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, Property, Instance, Int, Float, List, Disallow

from enthought.traits.ui.api import \
    View, Group, Item, TableEditor, InstanceEditor, VGroup, HGroup, Tabbed

from enthought.traits.ui.table_column import ObjectColumn
from enthought.pyface.image_resource import ImageResource

from agent import Agent
from elementary_agent import ElementaryAgent

#------------------------------------------------------------------------------
#  Setup a logger for this module:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#  Elementary agent factory function:
#-------------------------------------------------------------------------------

#def elementary_agent_factory(**row_factory_kw):
#        if "__table_editor__" in row_factory_kw:
#            swarm = row_factory_kw["__table_editor__"].object
#
#            environment = swarm.environment
#            agent = ElementaryAgent()
#
#            del row_factory_kw['__table_editor__']

#------------------------------------------------------------------------------
#  Elementary agents "TableEditor" instance:
#------------------------------------------------------------------------------

elementary_agents_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="name"),
        ObjectColumn(name="reward", editable=False),
        ObjectColumn(
            name="selector",
            editor=InstanceEditor(name="selectors", editable=False),
            format_func=lambda obj: obj.name
        )
    ],
    deletable=False, orientation="horizontal",
    edit_view="traits_view",
    row_factory=ElementaryAgent,
#    row_factory_kw = {'__table_editor__': ''}
)

#------------------------------------------------------------------------------
#  "Swarm" class:
#------------------------------------------------------------------------------

class Swarm(Agent):
    """ A Swarm is composed of several Agents, each one with its own
    selector.  A Swarm has no selector of its own.

    """

    # The list of all elementary agents composing the swarm:
    elementary_agents = List(ElementaryAgent)

    # The number of elementary agents composing the swarm:
    n_agents = Property(Int, depends_on=["elementary_agents"])

    # The last collective reward received:
#    reward = Delegate("environment")#List(Float)

    # A composition of elementary actions:
#    composed_action = Instance(ComposedAction)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Tabbed(
            Group(
                Item(name="environment", show_label=False, style="custom"),
                label="Environment"#, show_border=True
            ),
            Group(
                Item(
                    name="elementary_agents",
                    editor=elementary_agents_table_editor,
                    show_label=False, id=".participants_table"
                ),
                label="Elementary Agents"#, show_border=True
            ),
            dock="tab"
        ),
        id="pyqle.agent.swarm.swarm_view",
        resizable=True, style="custom",
        title="Swarm", height=.4
    )

    #--------------------------------------------------------------------------
    #  "Swarm" interface:
    #--------------------------------------------------------------------------

    def _selector_default(self):
        """ Trait initialiser """

        return None


    def _get_n_agents(self):
        """ Property getter """

        return len(self.elementary_agents)

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _state_changed_for_environment(self, env, name, old_state, new_state):
#    def _state_changed(self, old_state, new_state):
        """ Handle environment state changing """

        env = self.environment

        logger.debug(
            "Swarm [%s] noticed the environment state [%s] change" %
            (self.name, new_state)
        )

        if new_state is not None:
            # NB: The action list is None as the list of possible actions
            # is provided by the agents local environment
            composed_action = self.choose(new_state, env.action_list)

            self._apply_action(composed_action)


    def _reward_changed_for_environment(self, new):
        """ Handle the environment's reward changing. Dish out rewards
        to elementary agents.

        """

        logger.debug(
            "Swarm [%s] received collective reward [%s]" %
            (self.name, new)
        )

        for i, agent in enumerate(self.elementary_agents):
            reward = new[i]
            if agent.reward == reward:
                # Force agent to learn for identical reward
                agent.trait_property_changed("reward", agent.reward, reward)
            else:
                agent.reward = reward

    #--------------------------------------------------------------------------
    #  "Agent" interface
    #--------------------------------------------------------------------------

    def choose(self, state, action_list):
        """ Asks each agent to choose its own action, collects those actions
        into a composed one.

        """

        logger.debug(
            "Swarm [%s] requesting a choice of action from agents [%s]" %
            (self.name, self.elementary_agents)
        )

        composed_action = []#ComposedAction()

        for agent in self.elementary_agents:
            action = agent.choose(state, action_list)
            composed_action.append(action)#add_elementary_action(agent, action)
            #self.last_action.add_elementary_action(agent, action)

        return composed_action


    def _apply_action(self, composed_action):
        """ Apply the composed action """

#        old_state = self.state.copy()

        logger.debug(
            "Swarm [%s] applying composed action [%s] on the environment "
            "[%s]" % (self.name, composed_action, self.environment)
        )

        self.environment.apply_action(composed_action)

# EOF -------------------------------------------------------------------------
