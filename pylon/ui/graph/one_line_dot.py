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

import uuid
import logging

from enthought.traits.api import \
    HasTraits, Instance, Bool, List, Delegate, Event, Property, String, \
    on_trait_change

from enthought.traits.ui.api import View, Group, HGroup, VGroup, Item

from pylon.ui.graph.pydot.pydot import Dot, Node, Edge
from pylon.ui.graph.dot_attributes import DotAttributes
from pylon.api import Network, Bus, Branch, Generator, Load

from network_dot import NetworkDot, BusNode, BranchEdge, rgba2hex

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
            node = Node( str( id(g) ) )
            node.set_name( str( id(g) ) )
            node.set_label(g.name)
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
                node.set_shape(prefs.g_shape)
                node.set_fillcolor(rgba2hex(prefs.g_fill_colour_))
                node.set_color(rgba2hex(prefs.g_stroke_colour_))
                node.set_fixedsize(prefs.g_fixed_size)
                for sty in prefs.g_style:
                    node.set_style(sty)
                if prefs.g_height != 0.0:
                    node.set_width(prefs.g_height)
                if prefs.g_width != 0.0:
                    node.set_height(prefs.g_width)
                node.set_fixedsize(prefs.g_fixed_size)
            return node
        else:
            logger.warning("GeneratorNodeEdge has no generator reference")
            return None


    def _edge_default(self):
        """ Trait initialiser """

        g = self.generator
        if g is not None:
            edge = Edge( str( id(g) ), str( id(self.bus) ) )
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
                edge.set_arrowhead("none")
            return edge
        else:
            logger.warning("GeneratorNodeEdge has no generator reference")
            return None


    def _name_changed_for_generator(self, new):
        """ Handles the name of the generator changing """

        self.node.set_label(new)
        self.updated = True

#------------------------------------------------------------------------------
#  "LoadNodeEdge" class:
#------------------------------------------------------------------------------

class LoadNodeEdge(HasTraits):
    """ Maps a Generator to a Node and an Edge """

    # Parent bus
    bus = Instance(Bus)

    # Attributes used by various Graphviz tools
    dot_attrs = Instance(DotAttributes)

    # Mapped load
    load = Instance(Load)

    # Graph node for the load
    node = Instance(Node)

    # Graph edge connecting the load node to that of the host bus
    edge = Instance(Edge)

    # An event fired when the edge or node is updated significantly
    updated = Event

    def _node_default(self):
        """ Trait initialiser """

        l = self.load
        if l is not None:
            node = Node( str( id(l) ) )
            node.set_name( str( id(l) ) )
            node.set_label(l.name)
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
                node.set_shape(prefs.l_shape)
                node.set_fillcolor(rgba2hex(prefs.l_fill_colour_))
                node.set_color(rgba2hex(prefs.l_stroke_colour_))
                node.set_fixedsize(prefs.l_fixed_size)
                for sty in prefs.l_style:
                    node.set_style(sty)
                if prefs.l_height != 0.0:
                    node.set_width(prefs.l_height)
                if prefs.l_width != 0.0:
                    node.set_height(prefs.l_width)
                node.set_fixedsize(prefs.l_fixed_size)
            return node
        else:
            logger.warning("LoadNodeEdge has no load reference")
            return None


    def _edge_default(self):
        """ Trait initialiser """

        l = self.load
        if l is not None:
            edge = Edge( str( id(l) ), str( id(self.bus) ) )
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
                edge.set_arrowhead("none")
            return edge
        else:
            logger.warning("LoadNodeEdge has no load reference")
            return None


    def _name_changed_for_load(self, new):
        """ Handles the name of the load changing """

        self.node.set_label(new)
        self.updated = True

#------------------------------------------------------------------------------
#  "TransformerEdgeNodeEdge" class:
#------------------------------------------------------------------------------

class TransformerEdgeNodeEdge(BranchEdge):
    """ Maps a branch in transformer mode to two edges and a node """

    id = String(desc="unique node identifier")

    # Attributes used by various Graphviz tools
#    dot_attrs = Instance(DotAttributes)

    # The branch being represented
#    branch = Instance(Branch)

    # Pydot edge for the primary winding
    primary_edge = Instance(Edge)

    # Pydot node for the transformer
    node = Instance(Node)

    # Pydot edge for the secondary winding
    secondary_edge = Instance(Edge)

    # An event fired when the edge has been updated significantly
#    updated = Event

    def _node_default(self):
        """ Trait initialiser """

        t = self.branch
        if t is not None:
            node = Node( str( id(self) ) )
            node.set_name( str( id(self) ) )
            node.set_label(" ")#t.name)
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
                node.set_shape(prefs.t_shape)
                node.set_fillcolor(rgba2hex(prefs.t_fill_colour_))
                node.set_color(rgba2hex(prefs.t_stroke_colour_))
                node.set_fontcolor(rgba2hex(prefs.font_colour_))
                # TODO: Check that set_style() does not take a list
                for sty in prefs.t_style:
                    node.set_style(sty)
                if prefs.t_height != 0.0:
                    node.set_height(prefs.t_height)
                if prefs.t_width != 0.0:
                    node.set_width(prefs.t_width)
                node.set_fixedsize(prefs.fixedsize)
            return node
        else:
            return None


    def _primary_edge_default(self):
        """ Trait initialiser """

        return self._get_winding_edge( str( id(self.branch.source_bus) ),
            str( id(self) ) )


    def _secondary_edge_default(self):
        """ Trait initialiser """

        return self._get_winding_edge( str( id(self) ),
            str( id(self.branch.target_bus) ) )


    def _get_winding_edge(self, source_bus_id, target_bus_id):
        """ Trait initialiser """

        br = self.branch
        if br is not None:
            edge = Edge(source_bus_id, target_bus_id)
#            node.set_name(br.id)
#            edge.set_label(br.name)
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
                edge.set_arrowhead("none")

            return edge
        else:
            return None

    # Unique identifier -------------------------------------------------------

    def _id_default(self):
        """ Trait initialiser """

        return uuid.uuid4().hex[:6]


#------------------------------------------------------------------------------
#  "OneLineDot" class:
#------------------------------------------------------------------------------

class OneLineDot(NetworkDot):
    """ Defines a dot representation of a network with nested plant """

    generator_node_edges = List(Instance(GeneratorNodeEdge))

    load_node_edges = List(Instance(LoadNodeEdge))

    transformer_edge_node_edges = List(Instance(TransformerEdgeNodeEdge))

    def map_network(self, network):
        """ Creates mapping between network components and graph features """

        for v in network.buses:
            self.add_bus_node(v)
            for g in v.generators:
                self.add_generator_node_edge(g, v)
            for l in v.loads:
                self.add_load_node_edge(l, v)
        for e in network.branches:
            self.add_branch_edge(e)

    # Generator ---------------------------------------------------------------

    def add_generator_node_edge(self, generator, bus):
        """ Adds a generator node and edge with references to the parent bus
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


    @on_trait_change("network.all_generators")
    def on_generators_change(self, obj, name, old, new):
        """ Handles the population of generators changing """

        self.regraph()

    # Load --------------------------------------------------------------------

    def add_load_node_edge(self, load, bus):
        """ Adds a load node and edge with references to the parent bus and
        the graph attribute preferences.

        """

        logger.debug("Adding LoadNodeEdge for load: %s" % load.name)
        lne = LoadNodeEdge(load=load, bus=bus, dot_attrs=self.dot_attrs)
        self.dot.add_node(lne.node)
        self.dot.add_edge(lne.edge)
        self.load_node_edges.append(lne)


    @on_trait_change("network.all_loads")
    def on_loads_change(self, obj, old, new):
        """ Handles the population of loads changing """

        self.regraph()


    # Transformer -------------------------------------------------------------

    def add_branch_edge(self, branch):
        """ Handles adding new branch edges """

        logger.debug(
            "Adding TransformerEdgeNodeEdge for branch: %s" % branch.name
        )
        tene = TransformerEdgeNodeEdge(branch=branch, dot_attrs=self.dot_attrs)
        if branch.mode == "Line":
            self.dot.add_edge(tene.edge)
        elif branch.mode == "Transformer":
            self.dot.add_edge(tene.primary_edge)
            self.dot.add_node(tene.node)
            self.dot.add_edge(tene.secondary_edge)
        else:
            logger.error("Unrecognised branch mode")

        self.transformer_edge_node_edges.append(tene)


#    @on_trait_change("network.branches.mode")
    def on_branch_mode_change(self, new):
        """ Handles branches changing mode """

        print "TRANSFORMERS:", new
        self.regraph()

# EOF -------------------------------------------------------------------------
