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

""" Enable components for visualisation using Graphviz xdot output.

See: XDot by Jose.R.Fonseca (http://code.google.com/p/jrfonseca/wiki/XDot)

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
import shutil
import tempfile

from numpy import array, pi, sqrt

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, File, \
    Event, Tuple, Font, Bool, Range, Property, Enum, Color, Any

from enthought.enable.api import Component, Pointer, Container
from enthought.enable.colors import ColorTrait
from enthought.kiva import Font, MODERN, EOF_FILL_STROKE, FILL_STROKE
from enthought.kiva.fonttools.font import str_to_font
from enthought.kiva.agg import points_in_polygon

from pylon.ui.graph.pydot.pydot import \
    Dot, Node, Edge, Graph, graph_from_dot_data

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Pen" class:
#------------------------------------------------------------------------------

class Pen(HasTraits):
    """ Store pen traits """

    # Stroke colour
    colour = ColorTrait("black", desc="stroke colour")

    # Fill colour
    fill_colour = ColorTrait("black", desc="fill colour")

    # Stroke width in points
    line_width = Range(
        low=1, high=8, value=1, desc="width of the stroke in points"
    )

    # Text font
    font = Font("14 point Arial")

#------------------------------------------------------------------------------
#  "TextComponent" class:
#------------------------------------------------------------------------------

class TextComponent(Component):
    """ Component with text traits """

    # The background color of this component.
    bgcolor = "blue"

    # Pen for drawing text
    pen = Instance(Pen, desc="pen instance with which to draw the text")

    # X-axis coordinate
    text_x = Float(desc="x-axis coordinate")

    # Y-axis coordinate
    text_y = Float(desc="y-axis coordinate")


    # Text justification
    justification = Int(-1, desc="(LEFT, CENTER, RIGHT = -1, 0, 1)")

    # Width of the text
    text_w = Float(desc="width of the text as computed by the library")

    # Text to be drawn
    text = String(desc="text")

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws the component """

        gc.save_state()

        # Specify the font
#        font = Font(family=MODERN, size=14)
        font = str_to_font(self.pen.font)
        gc.set_font(font)
#        gc.set_antialias(True)

        gc.set_fill_color(self.pen.colour_)

#        gc.translate_ctm(self.text_x, self.text_y)
#        gc.move_to(self.text_x-self.text_w/2, self.text_y)
#
#        width = gc.width()
#        height = gc.height()
#        if self.justification == -1:
#            x = self.text_x
#        elif self.justification == 0:
#            x = self.text_x-0.5*width
#        elif self.justification == 1:
#            x = self.text_x-width
#        else:
#            logger.error("Invalid text justification [%d]" % self.j)
#
#        y = self.text_y-height
#
#        gc.move_to(x, y)
#        gc.show_text(self.text, (self.x, self.y))

#        tx, ty, tw, th = gc.get_text_extent(self.text)
#        tx = self.x + self.width/2.0 - tw/2.0
#        ty = self.y + self.height/2.0 - th/2.0
        gc.show_text_at_point(self.text, self.text_x, self.text_y)

#        tx, ty, tw, th = gc.get_text_extent(self.text)
#        dx, dy = self.bounds
#        x, y = self.position
#        gc.set_text_position(x+(dx-tw)/2, y+(dy-th)/2)
#        gc.show_text(self.text)

        gc.restore_state()


    def normal_left_down(self, event):
        print "TEXT left click:", self, event
        return

#------------------------------------------------------------------------------
#  "EllipseComponent" class:
#------------------------------------------------------------------------------

class EllipseComponent(Component):
    """ Component with Ellipse traits """

    # Pen used to draw the ellipse
    pen = Instance(Pen, desc="Pen instance with which to draw the ellipse")

    # X-axis coordinate of ellipse origin
    x_origin = Float(desc="x-axis coordinate of ellipse origin")

    # Y-axis coordinate of ellipse origin
    y_origin = Float(desc="y-axis coordinate of ellipse origin")

    # Width of the ellipse
    ew = Float(desc="Ellipse width")

    # Height of the ellipse
    eh = Float(desc="Ellipse height")

    # Is the ellipse filled?
    filled = Bool(False, desc="Fill the ellipse")

    # Background colour for the component
    bgcolor = (0.0, 1.0, 0.0, 0.0)

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws the component """

        gc.save_state()

        gc.begin_path()
#        gc.translate_ctm(self.ew, self.eh)
        gc.translate_ctm(self.x_origin, self.y_origin)
        gc.scale_ctm(self.ew, self.eh)
        gc.arc(0.0, 0.0, 1.0, 0, 2.0*pi)
        gc.close_path()
        if self.filled:
            gc.set_fill_color(self.pen.fill_colour_)
            gc.set_line_width(self.pen.line_width)
            gc.set_stroke_color(self.pen.colour_)
            gc.draw_path(FILL_STROKE)
        else:
            gc.set_line_width(self.pen.line_width)
            gc.set_stroke_color(self.pen.colour_)
            gc.stroke_path()

        gc.restore_state()


#    def _is_in(self, point):
#        """
#        Test if the point (an x, y tuple) is within this ellipse
#
#        """
#
#        raise NotImplementedError
#
#
#    def _distance_between(self, (x1, y1), (x2, y2)):
#        """ Return the distance between two points. """
#
#        return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


    def normal_left_down(self, event):
        print "ELLIPSE CLICKED", self, event
        return

#------------------------------------------------------------------------------
#  "PolygonComponent" class:
#------------------------------------------------------------------------------

class PolygonComponent(Component):
    """ Component with Polygon traits """

    # Pen used to draw the polygon
    pen = Instance(Pen, desc="the pen with which to draw the polygon")

    # Points defining the path of the polygon
    points = List(
        Tuple(Float, Float),
        desc="Point defining the path of the polygon"
    )

    # Is the polygon filled?
    filled = Bool(False, desc="Should the component be filled")

    # Rule to use to determine the inside of the polygon
    inside_rule = Trait(
        "winding",
        {"winding":FILL_STROKE, "oddeven":EOF_FILL_STROKE},
        desc="the rule to use to determine the inside of the polygon"
    )

    # Background colour of the component
    bgcolor = (1.0, 0.5, 0.5, 0.33)

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws a closed polygon """

        gc.save_state()

        if len(self.points) >= 2:
            # Set the drawing parameters.
            gc.set_fill_color(self.pen.fill_colour_)
            gc.set_stroke_color(self.pen.colour_)
            gc.set_line_width(self.pen.line_width)

            # Draw the path
#            gc.begin_path()
#            x0, y0 = self.points[-1]
#            gc.move_to(x0, y0)
#            for x, y in self.points:
#                gc.line_to(x, y)
#            gc.close_path()
#
#            if self.filled:
#                gc.fill_path()
#            else:
#                gc.stroke_path()

            # Draw the path.
            gc.begin_path()
            x0 = self.points[0][0] - self.x
            y0 = self.points[0][1] + self.y
            gc.move_to(x0, y0)
            offset_points = [(x-self.x, y+self.y) for x, y in self.points]
            gc.lines(offset_points)

            gc.close_path()
            gc.draw_path(self.inside_rule_)

        gc.restore_state()


#    def _is_in(self, point):
#        """
#        Test if the point (an x, y tuple) is within this polygonal region.
#
#        To perform the test, we use the winding number inclusion algorithm,
#        referenced in the comp.graphics.algorithms FAQ
#        (http://www.faqs.org/faqs/graphics/algorithms-faq/) and described in
#        detail here:
#
#        http://softsurfer.com/Archive/algorithm_0103/algorithm_0103.htm
#
#        """
#
#        point_array = array((point,))
#        vertices = array(self.points)
#        winding = self.inside_rule == 'winding'
#        result = points_in_polygon(point_array, vertices, winding)
#        return result[0]
#
#
#    def normal_left_down(self, event):
#        print "POLYGON CLICKED", self, event
#        return

#------------------------------------------------------------------------------
#  "BezierComponent" class:
#------------------------------------------------------------------------------

class BezierComponent(Component):
    """ Component with Bezier traits """

    # Pen used to draw the Bezier curve
    pen = Instance(Pen, desc="Pen instance with which to draw the component")

    # Points defining the path of the polygon
    points = List(
        Tuple(Float, Float),
        desc="Point defining the path of the polygon"
    )

    # Background colour of the component
    bgcolor = (1.0, 1.0, 0.5, 0.67)

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws the Bezier component """

        print "DRAWING BEZIER COMPONENT!"
        gc.save_state()

        gc.begin_path()
        x0, y0 = self.points[0]
#        gc.move_to(x0, y0)
#        for i in xrange(1, len(self.points), 3):
#            x1, y1 = self.points[i]
#            x2, y2 = self.points[i + 1]
#            x3, y3 = self.points[i + 2]
#            gc.curve_to(x1, y1, x2, y2, x3, y3)
        gc.close_path()

        gc.set_line_width(self.pen.line_width)
        gc.set_stroke_color(self.pen.colour_)
        gc.stroke_path()

        gc.restore_state()

#------------------------------------------------------------------------------
#  "NodeComponent" class:
#------------------------------------------------------------------------------

class NodeComponent(Container):
    """ Container of components making up a node """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The background color of this component.
    bgcolor = (1.0, 0.0, 0.0, 0.33)#"yellow"#"transparent"

    # components making up the node:
#    components = List(Component)

    # x-axis coordinate of node:
#    x = Float
#
#    # y-axis coordinate of node:
#    y = Float
#
#    # Node width:
#    w = Float
#
#    # Node height:
#    h = Float

#    # x-axis coordinate of bottom-left corner:
#    x1 = Property(Int, depends_on=["x, w"])
#
#    # y-axis coordinate of bottom-left corner:
#    y1 = Property(Int, depends_on=["y, h"])
#
#    # x-axis coordinate of top-right corner:
#    x2 = Property(Int, depends_on=["x, w"])
#
#    # y-axis coordinate of top-right corner:
#    y2 = Property(Int, depends_on=["x, w"])

#    bgcolor = colours[13]
#
#    # Unique resource locator:
#    url = String
#
#    resizable = ""

    #--------------------------------------------------------------------------
    #  Get the x-axis coordinate of the bottom-left corner:
    #--------------------------------------------------------------------------

#    def _get_x1(self): return self.x - 0.5 * self.w
#
#    #--------------------------------------------------------------------------
#    #  Get the y-axis coordinate of the bottom-left corner:
#    #--------------------------------------------------------------------------
#
#    def _get_y1(self): return self.y - 0.5 * self.h
#
#    #--------------------------------------------------------------------------
#    #  Get the x-axis coordinate of the top-right corner:
#    #--------------------------------------------------------------------------
#
#    def _get_x2(self): return self.x + 0.5 * self.w
#
#    #--------------------------------------------------------------------------
#    #  Get the y-axis coordinate of the top-right corner:
#    #--------------------------------------------------------------------------
#
#    def _get_y2(self): return self.y + 0.5 * self.h

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

#    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
#        print "Drawing Node component"
#        print "Node components:", self.components
#        gc.save_state()
#
#        gc.set_fill_color((0.0, 0.0, 1.0, 1.0))
#        dx, dy = 20, 20
#        x, y = 100, 100
#        gc.rect(x, y, dx, dy)
#        gc.fill_path()
#
##        for component in self.components:
##            component._draw_mainlayer(gc)
#
#        gc.restore_state()


#    def normal_left_dclick(self, event):
#        print "NODE EVENT:", self, event
#        return

#------------------------------------------------------------------------------
#  "EdgeComponent" class:
#-------------------------------------------------------------------------------

class EdgeComponent(Container):
    """ Container of components making up an edge """

#    components = List(Component, desc="Components making up the edge")

#    points = List(Tuple)

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

#    def _draw_mainlayer(self, gc):
#        print "Drawing Edge component"
#        print "Edge components:", self.components
#        gc.save_state()
#        for component in self.components:
#            component._draw_mainlayer(gc)
#        gc.restore_state()


    def normal_left_dclick(self, event):
        print "EDGE DCLICK EVENT:", self, event
        return

    def normal_left_down(self, event):
        print "EDGE LEFT DOWN EVENT:", self, event
        return

#------------------------------------------------------------------------------
#  "GraphComponent" class:
#------------------------------------------------------------------------------

class GraphContainer(Container):
    """ Container of all graph components """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Width of the graph:
#    width = Int(1)

    # height of the graph:
#    height = Int(1)

    # Node components:
#    nodes = List(NodeComponent)

    # Edge components:
#    edges = List(EdgeComponent)

#    fit_window = True

#    updated = Event

    intercept_events = False

    bgcolor = "lightslategrey"

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

#    def draw(self, gc, view_bounds=None, mode="default"):
#        print "Drawing graph container components"
#        gc.save_state()
#
##        gc.set_fill_color((0.0, 1.0, 1.0, 1.0))
##        dx, dy = [150.0, 150.0]
##        x, y = [75.0, 75.0]
##        gc.rect(x, y, dx, dy)
##        gc.fill_path()
#
##        for edge in self.edges:
##            edge._draw_mainlayer(gc)
##        for node in self.nodes:
##            node._draw_mainlayer(gc)
#
#        for component in self.components:
#            component._draw_mainlayer(gc)
#
#        gc.restore_state()

    def normal_left_down(self, event):
        print "GRAPH_CONTAINER:", self, event
        return

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":

    viewer = CanvasViewer()
    pen = Pen()
    component = EllipseComponent(
        pen=pen, x_origin=10, y_origin=10, ew=50, eh=33,
        bounds=[50, 50], position=[0, 0]

    )
    viewer.canvas.add(component)

    from enthought.enable.primitives.api import Box
    box = Box(
        color="steelblue",
        border_color="darkorchid", border_size=2,
        bounds=[30, 30], position=[25, 25]
    )
    viewer.canvas.add(box)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------
