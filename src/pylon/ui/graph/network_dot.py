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

from pylon.api import Network, Bus, Branch, Generator

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#  "rgba2hex" function:
#------------------------------------------------------------------------------

def rgba2hex(rgba):
    """ Convert colour in tuple (r,g,b,a) form to an integer which
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
    """ Links a Pylon bus and pydot Node """

    # A reference to the containing class
#    network_dot = Instance(HasTraits)#"pylon.ui.graph.network_dot.NetworkDot")

#    dot_attrs = Delegate("network_dot")
    # Attributes used by various Graphviz tools
    dot_attrs = Instance(DotAttributes)

    # The bus being represented by a node
    bus = Instance(Bus)

    # The node representing the bus
    node = Instance(Node)

    # An event fired when the node has been updated significantly
    updated = Event

    def _node_default(self):
        """ Trait initialiser """

        bus = self.bus
        if bus is not None:
            node = Node(bus.id)
            node.set_name(bus.id)
            node.set_label(bus.name)
            if self.dot_attrs is not None:
                prefs = self.dot_attrs
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


    def _name_changed_for_bus(self, new):
        """ Handles the bus name changing """

        self.node.set_label(new)
        self.updated = True


#    def _v_shape_changed_for_dot_attrs(self, new):
#        """ Handles the node shape preference changing """
#
#        self.node.set_shape(new)
#        self.updated = True
#
#
#    def _v_fill_colour_changed_for_dot_attrs(self, obj ,name, old, new):
#        """ Handles the node fill colour changing """
#
#        colour = rgba2hex(getattr(obj, name+"_"))
#        self.node.set_fillcolor(colour)
#        self.updated = True
#
#
#    def _v_stroke_colour_changed_for_dot_attrs(self, obj ,name, old, new):
#        """ Handles the node stroke colour changing """
#
#        colour = rgba2hex(getattr(obj, name+"_"))
#        self.node.set_color(colour)
#        self.updated = True
#
#
#    def _font_colour_changed_for_dot_attrs(self, obj ,name, old, new):
#        """ Handles the node font colour changing """
#
#        colour = rgba2hex(getattr(obj, name+"_"))
#        self.node.set_fontcolor(colour)
#        self.updated = True

#------------------------------------------------------------------------------
#  "BranchEdge" class:
#------------------------------------------------------------------------------

class BranchEdge(HasTraits):
    """ Links a Pylon branch and a Pydot Edge """

#    network_dot = Instance(HasTraits)#"pylon.ui.graph.network_dot.NetworkDot")

#    dot_attrs = Delegate("network_dot")
    # Attributes used by various Graphviz tools
    dot_attrs = Instance(DotAttributes)

    # The branch being represented by an edge
    branch = Instance(Branch)

    # The Pydot edge representing a branch
    edge = Instance(Edge)

    # An event fired when the edge has been updated significantly
    updated = Event

    def _edge_default(self):
        """ Trait initialiser """

        br = self.branch
        if br is not None:
            edge = Edge(br.source_bus.id, br.target_bus.id)
#            node.set_name(br.id)
            edge.set_label(br.name)
            if self.network_dot is not None:
                prefs = self.dot_attrs
            return edge
        else:
            return None


#    def _name_changed_for_bus(self, new):
#        self.edge.set_label(new)
#        self.updated = True

#------------------------------------------------------------------------------
#  "NetworkDot" class:
#------------------------------------------------------------------------------

class NetworkDot(HasTraits):
    """ Links a Pylon network to a Pydot Dot """

    # The network being represented
    network = Instance(Network)

    # The dot representation of the network
    dot = Instance(Dot, Dot(graph_name="Pylon", graph_type="digraph"))

    # Attributes used by various Graphviz tools
    dot_attrs = Instance(DotAttributes, (), allow_none=False)

    # An event that we fire when the structure of the graph has changed
    # significantly
    updated = Event(desc="dot representation modified")

    # A flag that when set prevents firing of the updated event
    suspend_update = Bool(False)

    # A list of Bus-Node linkers
    bus_nodes = List(BusNode)

    # A list of Branch-Edge linkers
    branch_edges = List(BranchEdge)

    # The default view
    traits_view = View(
        Item(name="dot_attrs", style="custom", show_label=False)
    )

    @on_trait_change(
        "network,network.branches.source_bus,network.branches.target_bus"
    )
    def regraph(self):
        """ Graphs the whole network from scratch """

        logger.debug("Graphing the whole network!")
        n = self.network

        # Wait until all changes have been made before updating
        logger.debug("Suspending graph updates")
        self.suspend_update = True

        self.dot = Dot(graph_name="Pylon", graph_type="digraph")
        self.bus_nodes = self.branch_edges = []
        if n is not None:
            for v in n.buses:
                self.add_bus_node(v)
            for e in n.branches:
                self.add_branch_edge(e)

        logger.debug("Resuming graph updates")
        self.suspend_update = False
        self.update()


    @on_trait_change("bus_nodes.updated,branch_edges.updated")
    def update(self):
        """ Signals that the dot representation has been updated """

        if not self.suspend_update:
            logger.debug("Updating network dot representation!")
            self.updated = True

    # Bus ---------------------------------------------------------------------

    def add_bus_node(self, bus):
        """ Adds a bus node """

        logger.debug("Adding BusNode for bus: %s" % bus.name)
        bn = BusNode(dot_attrs=self.dot_attrs, bus=bus)
        self.dot.add_node(bn.node)
        self.bus_nodes.append(bn)


    def _buses_items_changed_for_network(self, event):
        """ Handles buses being added and removed from the network """

        if event.removed:
            # Bus removal currently requires a complete refresh
            # TODO: Implement node removal in pydot
            self.regraph()
        else:
            for v in event.added:
                self.add_bus_node(v)

    # Branch ------------------------------------------------------------------

    def add_branch_edge(self, branch):
        """ Adds a branch edge providing each with a reference to the
        branch preferences.

        """

        logger.debug("Adding BranchEdge for branch: %s" % branch.name)
        be = BranchEdge(network_dot=self, branch=branch)
        self.dot.add_edge(be.edge)
        self.branch_edges.append(be)


    def _branches_items_changed_for_network(self, event):
        """ Handles branches being added and removed from the network """

        if event.removed:
            # Branch removal currently requires a complete refresh
            # TODO: Implement edge removal in pydot
            self.regraph()
        else:
            for e in event.added:
                self.add_branch_edge(e)

    #--------------------------------------------------------------------------
    #  Bus attribute handlers:
    #--------------------------------------------------------------------------

    @on_trait_change("dot_attrs.v_shape")
    def on_v_shape_change(self, new):
        """ Handles the node shape preference changing """

        for bus_node in self.bus_nodes:
            bus_node.node.set_shape(new)
        self.update()


    @on_trait_change("dot_attrs.v_fill_colour")
    def on_v_fill_colour_change(self, obj ,name, old, new):
        """ Handles the node fill colour changing """

        colour = rgba2hex(getattr(obj, name+"_"))
        for bus_node in self.bus_nodes:
            bus_node.node.set_fillcolor(colour)
        self.update()


    @on_trait_change("dot_attrs.v_stroke_colour")
    def on_v_stroke_colour_change(self, obj ,name, old, new):
        """ Handles the node stroke colour changing """

        colour = rgba2hex(getattr(obj, name+"_"))
        for bus_node in self.bus_nodes:
            bus_node.node.set_color(colour)
        self.update()


    @on_trait_change("dot_attrs.font_colour")
    def on_font_colour_change(self, obj ,name, old, new):
        """ Handles the node font colour changing """

        colour = rgba2hex(getattr(obj, name+"_"))
        for bus_node in self.bus_nodes:
            bus_node.node.set_fontcolor(colour)
        self.update()

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    tup = (0.56470588235294117, 0.93333333333333335, 0.56470588235294117, 1.0)
#    tup = (0.0, 1.0, 1.0, 1.0)

    gviz = rgba2hex(tup)

    print gviz

# EOF -------------------------------------------------------------------------
