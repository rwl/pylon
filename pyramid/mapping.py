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
    HasTraits, Instance, List, ListStr, Enum, Callable, Str, Dict, \
    Event, Button, on_trait_change

from enthought.traits.ui.api import View, Group, Item

from enthought.enable.api import Canvas, Viewport, Container
from enthought.enable.tools.api import ViewportPanTool, MoveTool, ResizeTool
from enthought.enable.base_tool import BaseTool
from enthought.enable.component_editor import ComponentEditor

from pylon.ui.graph.component.node import DiagramNode
from pylon.ui.graph.pydot.pydot import Dot, Node, Edge, graph_from_dot_data
from pylon.ui.graph.xdot_parser import XDotParser

from godot.node import DotGraphNode as GodotNode
from godot.edge import Edge as GodotEdge

from element_tool import ElementTool
from context_menu_tool import ContextMenuTool

class CanvasMapping(HasTraits):

    # A list of the names of the traits of the domain model that correspond to
    # the nodes on the canvas.
    node_lists = ListStr

    # The canvas on which the graph diagram is drawn
    diagram_canvas = Instance(Canvas)

    domain_model = Instance(HasTraits)

    tools = List(Callable)#Instance(BaseTool))

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

    def _diagram_canvas_default(self):
        """ Trait initialiser """

        canvas = Canvas()

        for tool in self.tools:
            canvas.tools.append(tool(canvas))

        return canvas


    def _viewport_default(self):
        """ Trait initialiser """

        vp = Viewport(component=self.diagram_canvas, enable_zoom=True)
        vp.view_position = [0,0]
        vp.tools.append(ViewportPanTool(vp))
        return vp


    @on_trait_change("tools")
    def _diagram_canvas_changed(self, new):
        """ Handles the diagram canvas being set """

        canvas = self.diagram_canvas

        for tool in self.tools:
            if canvas is not None:
                print "Adding tool: %s" % tool
                canvas.tools.append(tool(canvas))


#    def _domain_model_changed(self, new):
#        """ Handles change of the domain model """
#
#        self.clear_canvas()


    def clear_canvas(self):
        """ Removes all components from the canvas """

        canvas = self.diagram_canvas

#        print "COMPONENTS (START)", canvas.components
        for component in canvas.components:
            canvas.remove(component)
#        print "COMPONENTS (MIDDLE)", canvas.components
        for component in canvas.components:
            canvas.remove(component)
        canvas.request_redraw()
#        print "COMPONENTS (END)", canvas.components

        return


class LabelMapping(HasTraits):

    diagram_label = Instance(HasTraits)

    node_mapping = Instance(HasTraits)


class NodeMapping(HasTraits):

    # TopNodeReference trait
    containment_trait = Str

    element = Callable #Instance(HasTraits, allow_none=False)

#    diagram_node = Instance(Container)

    dot_node = Instance(GodotNode)

    tools = List(Callable)#Instance(BaseTool))

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
#    parser = Instance(XDotParser, XDotParser())

#    _map = Dict(Instance(HasTraits), Instance(Container))

    refresh = Button

    traits_view = View(
        Item(name="refresh", show_label=False),
        Item(name="diagram", style="custom", show_label=False),
        id="pyramid.mapping", resizable=True
    )

    @on_trait_change("refresh")
    def refresh_diagram(self):
        """ Refresh the map of the domain model """

        self.map_model(self.diagram.domain_model)


    def _domain_model_changed_for_diagram(self, obj, name, old, new):
        """ Handles the domain model changing """

        if old is not None:
            self.unmap_model(old)
        if new is not None:
            self.map_model(new)


    def unmap_model(self, old):
        """ Removes listeners from a domain model """

        for node_mapping in self.nodes:
            ct = node_mapping.containment_trait
            if hasattr(old, ct):
                old_elements = getattr(old, ct)
                for old_element in old_elements:
                    old.on_trait_change(
                        self.map_element, ct+"_items", remove=True
                    )


    def map_model(self, new):
        """ Maps a domain model to the diagram """

        dot = Dot()

        self.diagram.clear_canvas()

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

        code = dot.create(self.program, "xdot")
        xdot = graph_from_dot_data(code)
        parser = XDotParser()

        for node in xdot.get_node_list():
            diagram_node = parser.parse_node(node)
            if diagram_node is not None:
                for element in elements:
                    if str(id(element)) == diagram_node.dot_node.get_name():
                        diagram_node.element = element
                        break
                else:
                    print "Warning: Element for diagram node not found"

                # Tools
                if isinstance(diagram_node.element, node_mapping.element):
                    for tool in node_mapping.tools:
                        diagram_node.tools.append(tool(diagram_node))

                self.diagram.diagram_canvas.add(diagram_node)

        del parser


    def map_element(self, obj, name, event):
        """ Handles mapping elements to diagram components """

        canvas = self.diagram.diagram_canvas
        parser = XDotParser()

        for element in event.added:
            for node_mapping in self.nodes:
                ct = name[:-6] #strip '_items'
                if node_mapping.containment_trait == ct:
                    dot_attrs = node_mapping.dot_node
                    dot = Dot()
                    graph_node = Node(str(id(element)), shape=dot_attrs.shape)
                    dot.add_node(graph_node)
                    xdot = graph_from_dot_data(dot.create(self.program,"xdot"))
                    diagram_nodes = parser.parse_nodes(xdot)#.get_node_list())
                    for dn in diagram_nodes:
                        if dn is not None:
                            dn.element = element
                            # Tools
                            for tool in node_mapping.tools:
                                dn.tools.append(tool(dn))

                            canvas.add(dn)
                            canvas.request_redraw()

        for element in event.removed:
            for component in canvas.components:
                if element == component.element:
                    canvas.remove(component)
                    canvas.request_redraw()
                    break


#    def get_graph_node(self, element, dot_attrs):
#        pass


if __name__ == "__main__":
    from pylon.dss.common.api import Circuit, Bus
    from pylon.dss.delivery.api import Line, Transformer

    diagram = CanvasMapping(
        domain_model=Circuit(buses=[Bus(), Bus()]),
        diagram_canvas=Canvas(bgcolor="lightslategrey", draw_axes=True),
        tools=[ContextMenuTool]
    )

    node_mappings = [
#        NodeMapping(containment_trait="buses", diagram_node=DiagramNode),
        NodeMapping(
            containment_trait="buses", element=Bus,
            dot_node=GodotNode(
                shape="rectangle", fixed_size=True, width=0.5, height=0.1,
                colour="black", stroke_colour="orange"
            ),
            tools=[MoveTool, ElementTool, ResizeTool]
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
    mapping.refresh_diagram()
#    diagram.domain_model = None
    mapping.configure_traits()

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
