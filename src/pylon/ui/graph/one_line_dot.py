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

""" Graphviz dot representation of a Pylon network using Pydot """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, Instance, Bool, List, Delegate, Event, Property, \
    on_trait_change

from enthought.traits.ui.api import View, Group, HGroup, VGroup, Item

from pylon.ui.graph.pydot.pydot import Dot, Node, Edge
from pylon.ui.graph.dot_attributes import DotAttributes
from pylon.api import Network, Bus, Branch, Generator, Load

from network_dot import NetworkDot, BusNode, BranchEdge

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#  "GeneratorNodeEdge" class:
#------------------------------------------------------------------------------

class GeneratorNodeEdge(HasTraits):
    """ Maps a Generator to a Node and an Edge """

    # Parent bus
    bus = Instance(Bus)

    # Attributes used by various Graphviz tools
    dot_attrs = Instance(DotAttributes)

    # Mapped generator
    generator = Instance(Generator)

    # Graph node for the generator
    node = Instance(Node)

    # Graph edge connecting the generator node to that of the host bus
    edge = Instance(Edge)

    # An event fired when the edge or node is updated significantly
    updated = Event

    def _node_default(self):
        """ Trait initialiser """

        g = self.generator
        if g is not None:
            node = Node(g.id)
            node.set_name(g.id)
            node.set_label(g.name)
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
                node.set_shape(prefs.v_shape)
            return node
        else:
            return None


    def _edge_default(self):
        """ Trait initialiser """

        g = self.generator
        if g is not None:
            edge = Edge(g.id, self.bus.id)
            return edge
        else:
            return None


    def _name_changed_for_generator(self, new):
        """ Handles the name of the generator changing """

        self.node.set_label(new)
        self.updated = True

#------------------------------------------------------------------------------
#  "OneLineDot" class:
#------------------------------------------------------------------------------

class OneLineDot(NetworkDot):
    """ Defines a dot representation of a network with nested plant """

    generator_node_edges = List(Instance(GeneratorNodeEdge))

    def map_network(self, network):
        """ Creates mapping between network components and graph features """

        for v in network.buses:
            self.add_bus_node(v)
            for g in v.generators:
                self.add_generator_node_edge(g, v)
        for e in network.branches:
            self.add_branch_edge(e)

    # Generator ---------------------------------------------------------------

    def add_generator_node_edge(self, generator, bus):
        """ Adds a generator node and edge with references ro the parent bus
        and the graph attribute preferences.

        """

        logger.debug(
            "Adding GeneratorNodeEdge for generator: %s" % generator.name
        )
        gne = GeneratorNodeEdge(
            generator=generator, bus=bus, dot_attrs=self.dot_attrs
        )
        self.dot.add_node(gne.node)
        self.dot.add_edge(gne.edge)
        self.generator_node_edges.append(gne)


    @on_trait_change("network.generators")
    def on_generators_change(self, event):
        """ Handles the population of generators changing """

        print "GENERATORS:", event
#        self.update()

# EOF -------------------------------------------------------------------------
