#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

from enthought.traits.api import \
    HasTraits, Instance, List, ListStr, Enum, Callable, Str
from enthought.traits.ui.api import View, Group, Item

from enthought.enable.api import Canvas, Viewport
from enthought.enable.tools.api import ViewportPanTool
from enthought.enable.component_editor import ComponentEditor

from pylon.ui.graph.component.node import DiagramNode
from pylon.ui.graph.pydot.pydot import Dot, Node, Edge, graph_from_dot_data
from pylon.ui.graph.xdot_parser import XDotParser

class CanvasMapping(HasTraits):

    # A list of the names of the traits of the domain model that correspond to
    # the nodes on the canvas.
    node_lists = ListStr

    # The canvas on which the graph diagram is drawn
    diagram_canvas = Instance(Canvas)

    domain_model = Instance(HasTraits)

#    palette

#    node_mappings = List(Instance(NodeMapping))

    # A view into a sub-region of the canvas
    viewport = Instance(Viewport)

    traits_view=View(
        Item(
            name="viewport", editor=ComponentEditor(),
            show_label=False, id='.diagram_viewport'
        ),
        Item(name="domain_model", show_label=False, style="custom"),
        id="pyramid.canvas_mapping", resizable=True
    )

    def _viewport_default(self):
        """ Trait initialiser """

        vp = Viewport(component=self.diagram_canvas, enable_zoom=True)
        vp.view_position = [0,0]
        vp.tools.append(ViewportPanTool(vp))
        return vp


    def _domain_model_changed(self, new):
        """ Handles change of the domain model """

        self.diagram_canvas = Canvas(bgcolor="lightslategrey", draw_axes=True)


class LabelMapping(HasTraits):

    diagram_label = Instance(HasTraits)

    node_mapping = Instance(HasTraits)


class NodeMapping(HasTraits):

    # TopNodeReference trait
    containment_trait = Str

    element = Callable #Instance(HasTraits, allow_none=False)

    diagram_node = Instance(DiagramNode)

    tool = Instance(HasTraits)

    label = Instance(LabelMapping)


class LinkMapping(HasTraits):

    element = Instance(HasTraits)

    diagram_link = Instance(HasTraits)

    tool = Instance(HasTraits)

    label = Instance(LabelMapping)


class Mapping(HasTraits):

    diagram = Instance(CanvasMapping)

    nodes = List(Instance(NodeMapping))

    links = List(Instance(LinkMapping))

    # Graphviz layout program
    program = Enum("dot", "circo", "fdp", "neato", "twopi")

    # XDot code parser
    parser = Instance(XDotParser, XDotParser())

    def _domain_model_changed_for_diagram(self, obj, name, old, new):
        """ Handles the domain model changing """

        dot = Dot()

        for node_mapping in self.nodes:
            ct = node_mapping.containment_trait
            if hasattr(new, ct):
                elements = getattr(new, ct)
                for element in elements:
                    pydot_node = Node(str(id(element)))
                    dot_attrs = node_mapping.diagram_node.dot_attrs
                    if dot_attrs is not None:
                        pydot_node.set_label(dot_attrs.name)
                    dot.add_node(pydot_node)

                    new.on_trait_change(self.map_element, ct+"_items")

        code = dot.create(self.program, "xdot")
        xdot = graph_from_dot_data(code)
        parser = XDotParser()
        diagram_nodes = parser.parse_nodes(xdot)

        for diagram_node in diagram_nodes:
            self.diagram.diagram_canvas.add(diagram_node)


    def map_element(self, obj, name, event):
        """ Handles mapping elements to diagram components """

        canvas = self.diagram.diagram_canvas

        for element in event.added:
            for node_mapping in self.nodes:
                ct = name[-6] #strip '_items'
                if node_mapping.containment_trait == ct:
                    diagram_node = node_mapping.diagram_node
                    canvas.add(diagram_node)

        for element in event.removed:
            for component in canvas.components:
                if component.dot_attrs.name == str(id(element)):
                    canvas.remove(component)


if __name__ == "__main__":
    from pylon.dss.common.api import Circuit, Bus

    class BusNode(DiagramNode):
        pass

    circuit = Circuit(buses=[Bus(), Bus()])
    diagram = CanvasMapping()
    node_mappings = [
        NodeMapping(containment_trait="buses", diagram_node=BusNode),
        NodeMapping(containment_trait="lines"),
        NodeMapping(containment_trait="transformers"),
        NodeMapping(containment_trait="generators"),
        NodeMapping(containment_trait="loads"),
        NodeMapping(containment_trait="faults"),
        NodeMapping(containment_trait="voltage_sources"),
        NodeMapping(containment_trait="current_sources"),
        NodeMapping(containment_trait="shunt_capacitors"),
        NodeMapping(containment_trait="cap_controls"),
        NodeMapping(containment_trait="reg_controls")
    ]
    mapping = Mapping(diagram=diagram, nodes=node_mappings)
    diagram.domain_model=circuit
    diagram.configure_traits()

# EOF -------------------------------------------------------------------------
