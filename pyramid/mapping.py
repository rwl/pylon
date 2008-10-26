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
    HasTraits, Instance, List, ListStr, Enum, Callable, Str, Dict
from enthought.traits.ui.api import View, Group, Item

from enthought.enable.api import Canvas, Viewport, Container
from enthought.enable.tools.api import ViewportPanTool, MoveTool
from enthought.enable.base_tool import BaseTool
from enthought.enable.component_editor import ComponentEditor

from pylon.ui.graph.component.node import DiagramNode
from pylon.ui.graph.pydot.pydot import Dot, Node, Edge, graph_from_dot_data
from pylon.ui.graph.xdot_parser import XDotParser

from godot.node import DotGraphNode as GodotNode
from godot.edge import Edge as GodotEdge

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

#    diagram_node = Instance(Container)

    dot_node = Instance(GodotNode)

    tools = List(Instance(BaseTool))

    label = Instance(LabelMapping)


class LinkMapping(HasTraits):

    containment_trait = Str

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

    _map = Dict(Instance(HasTraits), Instance(Container))

    def _domain_model_changed_for_diagram(self, obj, name, old, new):
        """ Handles the domain model changing """

        dot = Dot()

        for node_mapping in self.nodes:
            ct = node_mapping.containment_trait
            if hasattr(new, ct):
                elements = getattr(new, ct)
                for element in elements:
                    pydot_node = Node(str(id(element)))
                    dot_attrs = node_mapping.dot_node
                    if dot_attrs is not None:
                        pydot_node.set_shape(dot_attrs.shape)
#                        pydot_node.set_fixedsize(str(dot_attrs.fixed_size))
#                        pydot_node.set_width(dot_attrs.width)
#                        pydot_node.set_height(dot_attrs.height)
#                        pydot_node.set_color(dot_attrs.colour)
#                        pydot_node.set_color(dot_attrs.stroke_colour)
                    dot.add_node(pydot_node)

                    new.on_trait_change(self.map_element, ct+"_items")

            if hasattr(old, ct):
                old_elements = getattr(old, ct)
                for old_element in old_elements:
                    old.on_trait_change(
                        self.map_element, ct+"_items", remove=True
                    )

        code = dot.create(self.program, "xdot")
        xdot = graph_from_dot_data(code)

        for node in xdot.get_node_list():
            diagram_node = self.parse_node(node)
            for element in elements:
                if str(id(element)) == diagram_node.dot_node.get_name():
                    diagram_node.element = element
                    break
            else:
                print "Warning: Element for diagram node not found"

            self.diagram.diagram_canvas.add(diagram_node)


    def map_element(self, obj, name, event):
        """ Handles mapping elements to diagram components """

        canvas = self.diagram.diagram_canvas

        for element in event.added:
            for node_mapping in self.nodes:
                ct = name[:-6] #strip '_items'
                if node_mapping.containment_trait == ct:
                    dot_attrs = node_mapping.dot_node
                    dot = Dot()
                    graph_node = Node(str(id(element)), shape=dot_attrs.shape)
                    dot.add_node(graph_node)
                    xdot = graph_from_dot_data(dot.create(self.program,"xdot"))
                    diagram_nodes = XDotParser().parse_nodes(xdot)
                    canvas.add(diagram_nodes[0])
                    canvas.request_redraw()

        for element in event.removed:
            for component in canvas.components:
                if element == component.element:
                    canvas.remove(component)
                    canvas.request_redraw()
                    break


    def get_graph_node(self, element, dot_attrs):
        pass


if __name__ == "__main__":
    from pylon.dss.common.api import Circuit, Bus
    from pylon.dss.delivery.api import Line, Transformer

    circuit = Circuit(buses=[Bus(), Bus()])
    diagram = CanvasMapping()
    node_mappings = [
#        NodeMapping(containment_trait="buses", diagram_node=DiagramNode),
        NodeMapping(
            containment_trait="buses", element=Bus,
            dot_node=GodotNode(
                shape="rectangle", fixed_size=True, width=0.5, height=0.1,
                colour="black", stroke_colour="orange"
            ),
            tools=[MoveTool]
        )
#        NodeMapping(containment_trait="generators"),
#        NodeMapping(containment_trait="loads"),
#        NodeMapping(containment_trait="faults"),
#        NodeMapping(containment_trait="voltage_sources"),
#        NodeMapping(containment_trait="current_sources"),
#        NodeMapping(containment_trait="shunt_capacitors"),
#        NodeMapping(containment_trait="cap_controls"),
#        NodeMapping(containment_trait="reg_controls")
    ]
    link_mappings = [
        LinkMapping(containment_trait="lines"),
        LinkMapping(containment_trait="transformers"),
    ]
    mapping = Mapping(diagram=diagram, nodes=node_mappings)
    diagram.domain_model=circuit
    diagram.configure_traits()

#diagram_editor = DiagramEditor(
#    diagram = CanvasMapping(domain_model=Circuit()),
#    nodes = [
#        NodeMapping(
#            containment_trait="buses", element=Bus,
#            dot_node=GodotNode(
#                shape="rectangle", fixedsize=True, width=0.5, height=0.1,
#                color="black", stroke_color="orange"
#            )
#        )
#    ],
#    edges = [
#        EdgeMapping(
#            containment_trait="generators", element=Line,
#            dot_edge=GodotEdge(width=4, arrowhead="none")
#        )
#    ],
#    show_palette=False, editable=True,
#    deletable=False
#)

# EOF -------------------------------------------------------------------------
