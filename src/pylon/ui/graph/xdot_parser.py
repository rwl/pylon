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
from enthought.kiva.fonttools.font import str_to_font

from pylon.ui.graph.pydot.pydot import \
    Dot, Node, Edge, Graph, graph_from_dot_data

from pylon.ui.graph.graph_component import \
    Pen, TextComponent, EllipseComponent, BezierComponent, \
    PolygonComponent#, NodeComponent, EdgeComponent, GraphContainer

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
#    container_pos = Tuple(Float, Float)
    container_x = Float
    container_y = Float

    # The size of the Node or Edge container component
#    container_size = Tuple(Float, Float)
    # FIXME: Make NodeContainer and EdgeContainer objects draw their
    # components relative to their centre point by default
    container_w = Float
    container_h = Float

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
#        return self.transform(x, y)
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
            # Adjust points relative to the container position
            x -= self.container_x-self.container_w/2
            y -= self.container_y-self.container_h/2
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
        shapes = []
        pen = Pen()
        s = self

        while s:
            op = s.read_code()
            if op == "c":
                colour = s.read_color()
                logger.debug("Pen stroke colour: %s" % str(colour))
                pen.colour = colour
            elif op == "C":
                colour = s.read_color()
                logger.debug("Pen fill colour: %s" % str(colour))
                pen.fill_colour = colour
            elif op == "S":
                s.read_text()
            elif op == "F":
                font_size = s.read_float()
                font_name = s.read_text()
#                pen.font = str_to_font(font_size + font_name)
                pen.font = str(font_size) + " point " + font_name
            elif op == "T": # Text
                x, y = s.read_point()
                j = s.read_number()
                w = s.read_number()
                t = s.read_text()
                logger.debug(
                    "Text '%s' at (%d, %d), width %d, justified %d" %
                    (t, x, y, w, j)
                )
                tc = TextComponent(
                    pen=pen,
                    text_x=self.container_w/2,
                    text_y=self.container_h/2,
                    text_w=w, text=t,
                    justification=j,
                    bounds=[w, y],
                    position=[0, 0]#[x, y]
                )
#                shapes.append(tc)
            elif op == "E": # Filled ellipse
                x0, y0 = s.read_point()
                w = s.read_number()
                h = s.read_number()
                logger.debug(
                    "Filled ellipse, %d by %d, at (%d, %d)" % (w, h, x0, y0)
                )
                ec = EllipseComponent(
                    pen=pen,
                    x_origin=self.container_w/2,
                    y_origin=self.container_h/2,
                    ew=w, eh=h,
                    filled=True,
                    bounds=[w*2, h*2],
                    position=[0, 0] #relative to node component
                )
                shapes.append(ec)
            elif op == "e": # Unfilled ellipse
                x0, y0 = s.read_point()
                w = s.read_number()
                h = s.read_number()
                logger.debug(
                    "Unfilled ellipse, %d by %d, at (%d, %d)" % (w, h, x0, y0)
                )
                ec = EllipseComponent(
                    pen=pen, x_origin=x0, y_origin=y0, ew=w, eh=h,
                    bounds=[w, h],
                    position=[x0, y0]
                )
                shapes.append(ec)
            elif op == "B": # Bezier curve
                points = self.read_polygon()
                # width
                x_points = [x for x, y in points]
                min_x, max_x = min(x_points), max(x_points)
                # height
                y_points = [y for x, y in points]
                min_y, max_y = min(y_points), max(y_points)
                bc = BezierComponent(
                    pen=pen, points=points,
                    bounds=[10, 10],#[max_x-min_x, max_y-min_y],
                    position=[5, 5]
                )
#                shapes.append(bc)
            elif op == "P": # Filled polygon
                points = self.read_polygon()
                logger.debug("Filled polygon points: %s" % points)
                x_points = [x for x, y in points]
                min_x, max_x = min(x_points), max(x_points)
                y_points = [y for x, y in points]
                min_y, max_y = min(y_points), max(y_points)
                pc = PolygonComponent(
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
                pc = PolygonComponent(
                    pen=pen, points=points,
                    bounds=[max_x-min_x, max_y-min_y],
                    position=[0, 0]
                )
                shapes.append(pc)
            else:
                logger.error("Unknown xdot opcode '%s'\n" % op)
                break
        return shapes


#    def transform(self, x, y):
#        return self.xdot_parser.transform(x, y)

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
        return self.parse(graph, container)


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

            node_shapes = []
            for attr in ('_draw_', '_ldraw_'):
                # FIXME: hasattr does not work for pydot Node class, but
                # the get method will return None if there is no attr
                if node.get(attr) is not None:
#                if hasattr(node, attr):
#                    attr = getattr(node, attr)
                    value = node.get(attr).strip('"')
                    parser = XDotAttrParser(
                        container_x=x, container_y=y,
                        container_w=w, container_h=h,
                        buf=value
                    )
                    logger.debug("Parsing attr: %s" % value)
                    shapes = parser.parse()
                    logger.debug("Attr shapes: %s" % shapes)
                    node_shapes.extend(shapes)
            logger.debug("Node shapes: %s" % node_shapes)
            if node_shapes:
                # Graphviz node is positioned according to its centre, but
                # an Enable component according to the bottom-left corner
                cont = Container(bounds=[w, h], position=[x-w/2, y-h/2])
                for shape in node_shapes:
                    cont.add(shape)
                # Add some handy tools
#                cont.tools.append(MoveTool(cont))
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
            # Component width
            x_points = [x for x, y in points]
            min_x, max_x = min(x_points), max(x_points)
            w = max_x-min_x
            # Component height
            y_points = [y for x, y in points]
            min_y, max_y = min(y_points), max(y_points)
            h = max_y-min_y
            logger.debug("Edge (%d, %d) with points %s" % (w, h, str(points)))

            edge_shapes = []
            attrs = (
                "_draw_", "_ldraw_", "_hdraw_",
                "_tdraw_", "_hldraw_", "_tldraw_"
            )
            for attr in attrs:
                if edge.get(attr) is not None:
                    value = edge.get(attr).strip('"')
                    parser = XDotAttrParser(
                        container_x=min_x, container_y=min_y,
                        container_w=w, container_h=h,
                        buf=value
                    )
                    logger.debug("Parsing edge attr: %s" % value)
                    shapes = parser.parse()
                    logger.debug("Edge attr shapes: %s" % shapes)
                    edge_shapes.extend(shapes)
            if shapes:
                cont = Container(bounds=[100, 150], position=[min_x, min_y])
                for shape in shapes:
                    cont.add(shape)
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
    from enthought.enable.component_editor import ComponentEditor

    edge = """"v_1-#a2104c" -> "v_2-#d72da0"  [_draw_="c 5 -black B 4 27 90 27 77 27 61 27 46 ", _hdraw_="S 5 -solid S 15 -setlinewidth(1) c 5 -black C 5 -black P 3 31 46 27 36 24 46 ", lp="37,63", _ldraw_="F 14.000000 11 -Times-Roman c 5 -black T 37 58 0 21 3 -e_1 ", pos="e,27,36 27,90 27,77 27,61 27,46", label=e_1];"""
    black_pen = "c 5 -black B 4 27 90 27 77 27 61 27 46"
    text = "F 14.000000 11 -Times-Roman c 5 -black T 37 58 0 21 3 -e_1"
    triangle = "S 5 -solid S 15 -setlinewidth(1) c 5 -black C 5 -black P 3 31 46 27 36 24 46"

    class ComponentViewer(HasTraits):
        canvas = Instance(Canvas)
        viewport = Instance(Viewport)

        traits_view=View(
            Item(
                name="viewport", editor=ComponentEditor(),
                show_label=False, id='.viewport_view'
            ),
            id="pylon.ui.graph.xdot_parser",
            resizable=True, width=.4, height=.4
        )

        def _viewport_default(self):
            vp = Viewport(component=self.canvas, enable_zoom=True)
            vp.view_position = [0,0]
            vp.tools.append(ViewportPanTool(vp))
            return vp

    parser = XDotAttrParser(
        container_x=0, container_y=0,
        container_w=0, container_h=44,
        buf=triangle
    )

    canvas = Canvas(bgcolor="ivory")
#    for shape in parser.parse():
#        canvas.add(shape)

    cv = ComponentViewer(canvas=canvas)

    cv.configure_traits()

# EOF -------------------------------------------------------------------------