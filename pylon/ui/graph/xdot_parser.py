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

""" Network visualisation using Graphviz xdot output parsed with pyparsing
and rendered with Enable.

See: XDot by Jose.R.Fonseca (http://code.google.com/p/jrfonseca/wiki/XDot)

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os
import sys
import subprocess
import math
import shutil
import tempfile
import logging

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, File, Delegate, \
    Event, Tuple, Font, Bool, Range, Default, Property, Enum, Color, Any

from enthought.traits.ui.api import View, Item, Group, HGroup, VGroup
from enthought.traits.ui.menu import NoButtons

from enthought.enable.api import Container, Canvas, Viewport
from enthought.enable.tools.api import MoveTool, TraitsTool, ViewportPanTool
from enthought.enable.colors import color_table

from pylon.ui.graph.pydot.pydot import \
    Dot, Node, Edge, Graph, graph_from_dot_data

from pylon.ui.graph.component.api import Pen, Text, Ellipse, Bezier, Polygon
from pylon.ui.graph.component.node import Node as NodeContainer
from pylon.ui.graph.component.edge import Edge as EdgeContainer

#------------------------------------------------------------------------------
#  Logging
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "XdotAttrParser" class:
#------------------------------------------------------------------------------

class XDotAttrParser(HasTraits):
    """ Parse component xdot attributes """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Parent parser, required for transform method which is used in the
    # read_pont method only
    # FIXME: The transform method should not be in the xdot_parser
#    xdot_parser = Any

    # The position of the Node or Edge container component
    container_pos = List(Float)#Tuple(Float, Float)
#    container_x = Float
#    container_y = Float

    # The bounds of the Node or Edge container component
    container_bounds = List(Float)#Tuple(Float, Float)
#    container_w = Float
#    container_h = Float

    # The attribute to be parsed
    buf = String

    # Current position in the buffer
    pos = Int

    #--------------------------------------------------------------------------
    #  Initialise object:
    #--------------------------------------------------------------------------

#    def __init__(self, xdot_parser, buf, **traits):
#        self.xdot_parser = xdot_parser
#        self.buf = self.unescape(buf)
#        super(XDotAttrParser, self).__init__(xdot_parser=xdot_parser, buf=buf, **traits)


    def __nonzero__(self):
        return self.pos < len(self.buf)


    def unescape(self, buf):
        buf = buf.replace('\\"', '"')
        buf = buf.replace('\\n', '\n')
        return buf


    def read_code(self):
        pos = self.buf.find(" ", self.pos)
        res = self.buf[self.pos:pos]
        self.pos = pos + 1
        while self.pos < len(self.buf) and self.buf[self.pos].isspace():
            self.pos += 1
        return res


    def read_number(self):
        return int(self.read_code())


    def read_float(self):
        return float(self.read_code())


    def read_point(self):
        x = self.read_number()
        y = self.read_number()

        # Positions in the xdot output are all relative to the graph origin,
        # but when the components are added to a container they are drawn
        # relative to the position of the container.  Here we offset the
        # position of all points by the position of the container.
        x -= self.container_pos[0]
        y -= self.container_pos[1]

        return x, y


    def read_text(self):
        num = self.read_number()
        pos = self.buf.find("-", self.pos) + 1
        self.pos = pos + num
        res = self.buf[pos:self.pos]
        while self.pos < len(self.buf) and self.buf[self.pos].isspace():
            self.pos += 1
        return res


    def read_polygon(self):
        n = self.read_number()
        p = []
        for i in range(n):
            x, y = self.read_point()
            p.append((x, y))
        return p


    def read_color(self):
        # See http://www.graphviz.org/doc/info/attrs.html#k:color
        c = self.read_text()
#        logger.debug("Reading colour: %s" % c)
        c1 = c[:1]
        if c1 == '#':
            # "#%2x%2x%2x%2x" - Red-Green-Blue-Alpha (RGBA)
            hex2float = lambda h: float(int(h, 16)/255.0)
            r = hex2float(c[1:3])
            g = hex2float(c[3:5])
            b = hex2float(c[5:7])
            try:
                a = hex2float(c[7:9])
            except (IndexError, ValueError):
                a = 1.0
            return (r, g, b, a)
        elif c1.isdigit():
            # H[, ]+S[, ]+V - Hue-Saturation-Value (HSV) 0.0 <= H,S,V <= 1.0
            h, s, v = map(float, c[1:].split(","))
            raise NotImplementedError, "HSV to RGBA conversion required"
        else:
            # String
            if color_table.has_key(c):
                return color_table[c]
            else:
                logger.warning("Colour [%s] may not be valid" % c)
                return c


    def parse(self):
        """ Parses an attribute string and returns a list of components """

        shapes = []
        pen = Pen()

        while self:
            op = self.read_code()
            if op == "c":
                colour = self.read_color()
                logger.debug("Pen stroke colour: %s" % str(colour))
                pen.colour = colour
            elif op == "C":
                colour = self.read_color()
                logger.debug("Pen fill colour: %s" % str(colour))
                pen.fill_colour = colour
            elif op == "S":
                self.read_text()
            elif op == "F":
                font_size = self.read_float()
                font_name = self.read_text()
                pen.font = "%s %d" % (font_name, int(font_size))
                logger.debug("Font: %s" % (pen.font))
            elif op == "T": # Text
                x, y = self.read_point()
                j = self.read_number()
                w = self.read_number()
                t = self.read_text()
                logger.debug(
                    "Text '%s' at (%d, %d), width %d, justified %d" %
                    (t, x, y, w, j)
                )
                tc = Text(
                    pen=pen,
                    text_x=x,#self.container_w/2,
                    text_y=y,#self.container_h/2,
                    text_w=w, text=t,
                    justification=j,
#                    bounds=[w, y],
#                    position=[0, 0]#[x, y]
                )
                shapes.append(tc)
            elif op == "E": # Filled ellipse
                x0, y0 = self.read_point()
                w = self.read_number()
                h = self.read_number()
                logger.debug(
                    "Filled ellipse, %d by %d, at (%d, %d)" % (w, h, x0, y0)
                )
                ec = Ellipse(
                    pen=pen,
                    x_origin=x0, y_origin=y0,
                    e_width=w, e_height=h, filled=True,
                    bounds=[w*2, h*2], position=[0, 0] #relative to node component
                )
                shapes.append(ec)
            elif op == "e": # Unfilled ellipse
                x0, y0 = self.read_point()
                w = self.read_number()
                h = self.read_number()
                logger.debug(
                    "Unfilled ellipse, %d by %d, at (%d, %d)" % (w, h, x0, y0)
                )
                ec = Ellipse(
                    pen=pen,
                    x_origin=x0, y_origin=y0,
                    e_width=w, e_height=h,
                    bounds=[w, h], position=[x0, y0]
                )
                shapes.append(ec)
            elif op == "B": # Bezier curve
                points = self.read_polygon()
                # width
#                x_points = [x for x, y in points]
#                min_x, max_x = min(x_points), max(x_points)
                # height
#                y_points = [y for x, y in points]
#                min_y, max_y = min(y_points), max(y_points)
                bc = Bezier(
                    pen=pen, points=points,
#                    bounds=[10, 10],#[max_x-min_x, max_y-min_y],
#                    position=[5, 5]
                )
                shapes.append(bc)
            elif op == "P": # Filled polygon
                points = self.read_polygon()
                logger.debug("Filled polygon points: %s" % points)
                x_points = [x for x, y in points]
                min_x, max_x = min(x_points), max(x_points)
                y_points = [y for x, y in points]
                min_y, max_y = min(y_points), max(y_points)
                pc = Polygon(
                    pen=pen, points=points, filled=True,
                    bounds=[max_x-min_x, max_y-min_y],
                    position=[0, 0]
                )
                shapes.append(pc)
            elif op == "p": # Unfilled polygon
                points = self.read_polygon()
                logger.debug("Unfilled polygon points: %s" % points)
                x_points = [x for x, y in points]
                min_x, max_x = min(x_points), max(x_points)
                y_points = [y for x, y in points]
                min_y, max_y = min(y_points), max(y_points)
                pc = Polygon(
                    pen=pen, points=points,
                    bounds=[max_x-min_x, max_y-min_y],
                    position=[0, 0]
                )
                shapes.append(pc)
            else:
                logger.error("Unknown xdot opcode '%s'\n" % op)
                break
        return shapes


    def offset(self, x, y):
        """ Offsets an absolute position by the container position """

        offset_x = x - self.container_x
        offset_y = x - self.container_y

        return offset_x, offset_y

#------------------------------------------------------------------------------
#  "XdotParser" class:
#------------------------------------------------------------------------------

class XDotParser(HasTraits):
    """ Parse Graphviz xdot code and populate the graph container """

    #--------------------------------------------------------------------------
    #  Public interface
    #--------------------------------------------------------------------------

    def parse_code(self, xdot_code):#, container=None):
        """ Allows xdot code to be passed directly """

        graph = graph_from_dot_data(xdot_code)
        return self.parse(graph)


    def parse(self, graph):#, container=None):
        """ Parses an xdot graph and returns a canvas """

        logger.debug("Parsing graph:\n%s" % graph.to_string())

#        bb = graph.get_bb()
#        bb = bb.strip('"') # Strip double-quotation marks
#        xmin, ymin, xmax, ymax = map(int, bb.split(","))

#        width = xmax - xmin
#        height = ymax - ymin

#        logger.debug("Graph size: (%s, %s)" % (width, height))

        canvas = Canvas()

        for node in self._parse_nodes(graph):
            canvas.add(node)
        for edge in self._parse_edges(graph):
            canvas.add(edge)

        return canvas

    #--------------------------------------------------------------------------
    #  Private interface
    #--------------------------------------------------------------------------

    def _parse_nodes(self, graph):
        """ Parses the xdot node data and returns a list of containers """

        nodes = []

        for node in graph.get_node_list():
            if node.get_pos() is None:
                logger.debug(
                    "Skipping node [%s] with no position" % node.to_string()
                )
                continue
            logger.debug("Parsing node: %s" % node.to_string())
            x, y = self._parse_node_pos(node.get_pos())
            w = float(node.get_width().strip('"'))*72
            h = float(node.get_height().strip('"'))*72
            id = node.get_name()
            logger.debug(
                "Node [%s] at position (%d, %d) with size (%d, %d)" %
                (id, x, y, w, h)
            )

            pos = [x-w/2, y-h/2]
            bounds = [w, h]

            node_shapes = []
            for attr in ('_draw_', '_ldraw_'):
                # FIXME: hasattr does not work for pydot Node class, but
                # the get() method will return None if there is no attr
                if node.get(attr) is not None:
#                if hasattr(node, attr):
#                    attr = getattr(node, attr)
                    value = node.get(attr).strip('"')
                    parser = XDotAttrParser(
                        container_pos=pos, container_bounds=bounds, buf=value
                    )
                    logger.debug("Parsing attr: %s" % value)
                    shapes = parser.parse()
                    node_shapes.extend(shapes)
            logger.debug("Node shapes: %s" % node_shapes)
            if node_shapes:
                # Graphviz node is positioned according to its centre, but
                # an Enable component according to the bottom-left corner
                cont = NodeContainer(position=pos, bounds=bounds)
                for shape in node_shapes:
                    cont.add(shape)
                # Add some handy tools
                cont.tools.append(MoveTool(cont))
#                cont.tools.append(TraitsTool(cont))
                # Add node component to the list to be drawn on the canvas
                nodes.append(cont)
            logger.debug("Nodes: %s", nodes)

        return nodes


    def _parse_edges(self, graph):
        """ Parses xdot edge data and returns a list of containers """

        edges = []

        for edge in graph.get_edge_list():
            if edge.get_pos() is None:
                logger.debug(
                    "Skipping edge [%s] with no position" % edge.to_string()
                )
                continue
            logger.debug("Parsing edge: %s" % edge.to_string())
            points = self._parse_edge_pos(edge.get_pos().strip('"'))

            # Edge position
            x_points = [x for x, y in points]
            y_points = [y for x, y in points]
            min_x, max_x = min(x_points), max(x_points)
            min_y, max_y = min(y_points), max(y_points)

            # Edge size
            w, h = max_x-min_x, max_y-min_y
            logger.debug("Edge (%d, %d) with points %s" % (w, h, str(points)))

            # If bounds are set to 0, horizontal/vertical lines will not render
            bounds = [max(w, 6), max(h, 1)]
            pos = [min_x, min_y]

            edge_shapes = []
            attrs = (
                "_draw_", "_ldraw_", "_hdraw_",
                "_tdraw_", "_hldraw_", "_tldraw_"
            )
            for attr in attrs:
                if edge.get(attr) is not None:
                    value = edge.get(attr).strip('"')
                    parser = XDotAttrParser(
                        container_pos=pos, container_bounds=bounds, buf=value
                    )
                    logger.debug("Parsing edge attr: %s" % value)
                    shapes = parser.parse()
                    logger.debug("Edge attr shapes: %s" % shapes)
                    edge_shapes.extend(shapes)
            if edge_shapes:

#                source_name = edge.get_source()
#                target_name = edge.get_destination()
#                source_node = target_node
#                for node in graph.get_node_list():
#                    name = node.get_name()

                cont = EdgeContainer(bounds=bounds, position=pos)
                for shape in edge_shapes:
                    cont.add(shape)
                # Add some handy tools
                cont.tools.append(MoveTool(cont))
                edges.append(cont)

        return edges


    def _parse_node_pos(self, pos):
        """ Returns a tuple of a nodes position """

        pos = pos.strip('"')
        x, y = pos.split(",")
#        return self.transform(float(x), float(y))
        return float(x), float(y)


    def _parse_edge_pos(self, pos):
        """ Returns a list of tuples """

        points = []
        for entry in pos.split(" "):
            fields = entry.split(",")
            try:
                x, y = fields
            except ValueError:
                # TODO: handle start/end points
                continue
            else:
#                points.append(self.transform(float(x), float(y)))
                points.append((float(x), float(y)))
        return points


#    def transform(self, x, y):
#        # FIXME: this is not the right place for this code
#        x = (x + self.xoffset)*self.xscale
#        y = (y + self.yoffset)*self.yscale
#        return x, y

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    from component_viewer import ComponentViewer

    simple = """digraph simple {
    node [label="\N"];
    graph [bb="0,0,74,126",
        _draw_="c 5 -white C 5 -white P 4 0 0 0 126 74 126 74 0 ",
        xdotversion="1.2"];
    node1 [label=node1, shape=ellipse, pos="37,108", width="1.03", height="0.50", _draw_="c 5 -black e 37 108 37 18 ", _ldraw_="F 14.000000 11 -Times-Roman c 5 -black T 37 103 0 37 5 -node1 "];
    node2 [label=node2, shape=rectangle, pos="37,18", width="0.75", height="0.50", _draw_="c 5 -black p 4 64 36 10 36 10 0 64 0 ", _ldraw_="F 14.000000 11 -Times-Roman c 5 -black T 37 13 0 37 5 -node2 "];
    node1 -> node2 [label=edge1, pos="e,37,36 37,90 37,77 37,61 37,46", lp="55,63", _draw_="c 5 -black B 4 37 90 37 77 37 61 37 46 ", _hdraw_="S 5 -solid S 15 -setlinewidth(1) c 5 -black C 5 -black P 3 41 46 37 36 34 46 ", _ldraw_="F 14.000000 11 -Times-Roman c 5 -black T 55 58 0 36 5 -edge1 "];
}"""

    node = """digraph simple {
    node [label="\N"];
    graph [bb="0,0,74,36",
        _draw_="c 5 -white C 5 -white P 4 0 0 0 36 74 36 74 0 ",
        xdotversion="1.2"];
    node1 [label=node1, shape=ellipse, pos="37,18", width="1.03", height="0.50", _draw_="c 5 -black e 37 18 37 18 ", _ldraw_="F 14.000000 11 -Times-Roman c 5 -black T 37 13 0 37 5 -node1 "];
}"""

    edge = """"v_1-#a2104c" -> "v_2-#d72da0"  [_draw_="c 5 -black B 4 27 90 27 77 27 61 27 46 ", _hdraw_="S 5 -solid S 15 -setlinewidth(1) c 5 -black C 5 -black P 3 31 46 27 36 24 46 ", lp="37,63", _ldraw_="F 14.000000 11 -Times-Roman c 5 -black T 37 58 0 21 3 -e_1 ", pos="e,27,36 27,90 27,77 27,61 27,46", label=e_1];"""
    black_pen = "c 5 -black B 4 27 90 27 77 27 61 27 46"
    text = "F 14.000000 11 -Times-Roman c 5 -black T 37 58 0 21 3 -e_1"
    triangle = "S 5 -solid S 15 -setlinewidth(1) c 5 -black C 5 -black P 3 31 46 27 36 24 46"

    canvas = XDotParser().parse_code(simple)
    canvas.draw_axes = True

    from enthought.enable.primitives.api import Box
    box = Box(
        color="steelblue",
        border_color="darkorchid", border_size=1,
        bounds=[50, 50], position=[100, 100]
    )
    canvas.add(box)

    viewer = ComponentViewer(canvas=canvas)
#    for shape in parser.parse():
#        cv.canvas.add(shape)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------