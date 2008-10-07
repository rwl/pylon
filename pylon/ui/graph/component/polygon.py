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

""" Defines an ellipse component.

References:
    Jose.R.Fonseca, 'XDot', http://code.google.com/p/jrfonseca/wiki/XDot

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from numpy import array

from enthought.traits.api import \
    Instance, Float, Bool, List, Trait, Tuple, on_trait_change

from enthought.traits.ui.api import View, Item, Group
from enthought.enable.api import Component
from enthought.kiva import EOF_FILL_STROKE, FILL_STROKE
from enthought.kiva.agg import points_in_polygon

from pen import Pen

#------------------------------------------------------------------------------
#  "Polygon" class:
#------------------------------------------------------------------------------

class Polygon(Component):
    """ Component with Polygon traits """

    #--------------------------------------------------------------------------
    #  "Polygon" interface:
    #--------------------------------------------------------------------------

    # Pen used to draw the polygon
    pen = Instance(Pen, desc="the pen with which to draw the polygon")

    # Points defining the vertices of the polygon
    points = List(
        Tuple(Float, Float, labels=["x", "y"], cols=2),
        desc="points defining the vertices of the polygon"
    )

    # Is the polygon filled?
    filled = Bool(False, desc="Should the component be filled")

    # Rule to use to determine the inside of the polygon
    inside_rule = Trait(
        "winding", {"winding":FILL_STROKE, "oddeven":EOF_FILL_STROKE},
        desc="the rule to use to determine the inside of the polygon"
    )

    # Background colour of the component
    bgcolor = "transparent"#(1.0, 0.5, 0.5, 0.33)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Group(
            Item("pen", style="custom", show_label=False),
            label="Pen", show_border=True
        ),
        Group(
            Item("points", height=250, show_label=False),
            label="Points", show_border=True
        ),
        Item("filled"), Item("inside_rule")
    )

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws a closed polygon """

        gc.save_state()
        try:
#            self._draw_bounds(gc)
            if len(self.points) >= 2:
                # Set the drawing parameters.
                gc.set_fill_color(self.pen.fill_colour_)
                gc.set_stroke_color(self.pen.colour_)
                gc.set_line_width(self.pen.line_width)

                # Draw the path.
                gc.begin_path()
#                x0 = self.points[0][0] - self.x
#                y0 = self.points[0][1] + self.y
#                gc.move_to(x0, y0)
#                offset_points = [(x-self.x, y+self.y) for x, y in self.points]
                gc.lines(self.points)

                gc.close_path()
                if self.filled:
                    gc.draw_path(self.inside_rule_)
                else:
                    gc.stroke_path()
        finally:
            gc.restore_state()


    def is_in(self, point_x, point_y):
        """ Test if a point is within this polygonal region """

        point_array = array(((point_x, point_y),))
        vertices = array(self.points)
        winding = self.inside_rule == "winding"
        result = points_in_polygon(point_array, vertices, winding)
        return result[0]


    def _draw_bounds(self, gc):
        """ Draws the component bounds for testing purposes """

        dx, dy = self.bounds
        x, y = self.position
        gc.rect(x, y, dx, dy)
        gc.stroke_path()


    def normal_left_down(self, event):
        """ Handles left mouse button clicks in 'normal' mode """

        print "Polygon selected at (%d, %d)" % (event.x, event.y)


    @on_trait_change("pen.+,points,filled")
    def _update(self):
        if not self.points: return
        x_points = [x for x, y in self.points]
        y_points = [y for x, y in self.points]
        x = min(x_points)
        x2 = max(x_points)
        y = min(y_points)
        y2 = max(y_points)
        self.position = [x, y]
        # Don't let bounds be set to 0, otherwise, horizontal and vertical
        # lines will not render because enable skips rendering items with
        # bounds=[0,0]
        self.bounds = [max(x2-x,1), max(y2-y,1)]

        self.request_redraw()

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.ui.graph.component_viewer import ComponentViewer

    pen = Pen()
    polygon = Polygon(
        pen=pen, points=[(50, 50), (50, 100), (100, 100)],
#        bounds=[50, 50], position=[50, 50]
    )

    viewer = ComponentViewer(component=polygon)

    from enthought.enable.primitives.api import Box
    box = Box(
        color="red", border_color="blue", border_size=1,
        bounds=[50, 50], position=[100, 100]
    )
#    viewer.canvas.add(box)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------
