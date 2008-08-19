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

"""
Graphviz dot representation of a Pylon network using pydot by Ero Carrera

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import \
    HasTraits, Instance, Bool, List, Delegate, Event, Property, \
    on_trait_change

from enthought.traits.ui.api import View, Group, HGroup, VGroup, Item

from pylon.ui.graph.pydot.pydot import Dot, Node, Edge

from pylon.ui.graph.dot_preference import DotPreferences

from pylon.api import Network, Bus, Branch, Generator

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
#  "rgba2hex" function:
#------------------------------------------------------------------------------

def rgba2hex(rgba):
    """
    Convert colour in tuple (r,g,b,a) form to an integer which
    in hex is of the form #RRGGBB

    TODO: Implement Graphviz colour trait

    """

    ret = "#"
    for f in rgba:
        h = hex(int(f*255))[2:]
        if h == "0":
            h = "00"
        ret += h
    return ret

#------------------------------------------------------------------------------
#  "BusNode" class:
#------------------------------------------------------------------------------

class BusNode(HasTraits):
    """
    Wrapper for a Pylon bus and pydot Node

    """

    network_dot = Instance(HasTraits)#"pylon.ui.graph.network_dot.NetworkDot")

    dot_prefs = Delegate("network_dot")

    bus = Instance(Bus)

    node = Instance(Node)

    updated = Event

    def _node_default(self):
        bus = self.bus
        if bus is not None:
            node = Node(bus.id)
            node.set_name(bus.id)
            node.set_label(bus.name)
            if self.network_dot is not None:
                prefs = self.dot_prefs
                node.set_shape(prefs.v_shape)
                node.set_fillcolor(rgba2hex(prefs.v_fill_colour_))
                node.set_color(rgba2hex(prefs.v_stroke_colour_))
                node.set_fontcolor(rgba2hex(prefs.font_colour_))
                # TODO: Check that set_style() does not take a list
                for sty in prefs.v_style:
                    node.set_style(sty)
            return node
        else:
            return None


    def _bus_changed(self, new):
        """ An unlikely event handler """
        self.reset_traits(["node"])


    def _name_changed_for_bus(self, new):
        self.node.set_label(new)
        self.updated = True


    def _v_shape_changed_for_dot_prefs(self, new):
        self.node.set_shape(new)
        self.updated = True


    def _v_fill_colour_changed_for_dot_prefs(self, obj ,name, old, new):
        colour = rgba2hex(getattr(obj, name+"_"))
        self.node.set_fillcolor(rgba2hex(new_))
        self.updated = True


    def _v_stroke_colour_changed_for_dot_prefs(self, obj ,name, old, new):
        colour = rgba2hex(getattr(obj, name+"_"))
        self.node.set_color(colour)
        self.updated = True


    def _font_colour_changed_for_dot_prefs(self, obj ,name, old, new):
        colour = rgba2hex(getattr(obj, name+"_"))
        self.node.set_fontcolor(colour)
        self.updated = True

#------------------------------------------------------------------------------
#  "BranchEdge" class:
#------------------------------------------------------------------------------

class BranchEdge(HasTraits):
    """
    Wrapper for a Pylon branch and pydot Edge

    """

    network_dot = Instance(HasTraits)#"pylon.ui.graph.network_dot.NetworkDot")

    dot_prefs = Delegate("network_dot")

    branch = Instance(Branch)

    edge = Instance(Edge)

    updated = Event

    def _edge_default(self):
        br = self.branch
        if br is not None:
            edge = Edge(br.source_bus.id, br.target_bus.id)
#            node.set_name(br.id)
            edge.set_label(br.name)
            if self.network_dot is not None:
                prefs = self.dot_prefs
            return edge
        else:
            return None


    def _branch_changed(self, new):
        """ An unlikely event handler """
        self.reset_traits(["edge"])


#    def _name_changed_for_bus(self, new):
#        self.edge.set_label(new)
#        self.updated = True

#------------------------------------------------------------------------------
#  "NetworkDot" class:
#------------------------------------------------------------------------------

class NetworkDot(HasTraits):
    """
    Dot representation of a Pylon network

    """

    network = Instance(Network)

    dot = Instance(Dot, Dot(graph_name="Pylon", graph_type="digraph"))

    dot_prefs = Instance(DotPreferences, (), allow_none=False)

    updated = Event(desc="dot representation modified")

    suspend_update = Bool(False)

    bus_nodes = List(BusNode)

    branch_edges = List(BranchEdge)

    traits_view = View(
        Item(name="dot_prefs", style="custom", show_label=False)
    )

    @on_trait_change("network")#,network.branches.source_bus,network.branches.target_bus")
    def regraph(self):
        logger.debug("Re-graphing the network!")
        n = self.network
        self.dot = Dot(graph_name="Pylon", graph_type="digraph")
        self.bus_nodes = self.branch_edges = []
        if n is not None:
            # Wait until all nodes and edges have been added before updating
            self.suspend_update = True
            for v in n.buses:
                self.add_bus_node(v)
            for e in n.branches:
                self.add_branch_edge(e)
            self.suspend_update = False
            self.update()


    @on_trait_change("bus_nodes.updated,branch_edges.updated")
    def update(self):
        if not self.suspend_update:
            logger.debug("Updating network dot!")
            self.updated = True

    # Bus ---------------------------------------------------------------------

    def add_bus_node(self, bus):
        """ Adds a bus node to the list """
        bn = BusNode(network_dot=self, bus=bus)
        self.dot.add_node(bn.node)
        self.bus_nodes.append(bn)


    def _buses_items_changed_for_network(self, event):
        for v in event.added:
            self.add_bus_node(v)
        if event.removed:
#            self.bus_nodes = [bn for bn in self.bus_nodes if bn.bus is not v]
            # Bus removal currently requires a complete refresh
            # TODO: Implement node removal in pydot
            self.regraph()

    # Branch ------------------------------------------------------------------

    def add_branch_edge(self, branch):
        """ Adds a branch edge to the list """
        be = BranchEdge(network_dot=self, branch=branch)
        self.dot.add_edge(be.edge)
        self.branch_edges.append(be)


    def _branches_items_changed_for_network(self, event):
        for e in event.added:
            self.add_branch_edge(e)
        if event.removed:
            self.regraph()

# EOF -------------------------------------------------------------------------
