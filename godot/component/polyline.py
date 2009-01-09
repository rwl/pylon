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

""" Defines a polyline. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    Instance, Float, Bool, List, Trait, Tuple, on_trait_change

from enthought.traits.ui.api import View, Item, Group
from enthought.enable.api import Component
from enthought.kiva import EOF_FILL_STROKE, FILL_STROKE
from enthought.kiva.agg import points_in_polygon

from pen import Pen

#------------------------------------------------------------------------------
#  "Polyline" class:
#------------------------------------------------------------------------------

class Polyline(Component):
    """ Defines a component with multiple line segments. """

    #--------------------------------------------------------------------------
    #  "Polyline" interface:
    #--------------------------------------------------------------------------

    # Pen used to draw the polyline.
    pen = Instance(Pen, desc="the pen with which to draw the lines")

    # Points defining the line ends.
    points = List(
        Tuple(Float, Float, labels=["x", "y"], cols=2, minlen=2),
        desc="points defining the line ends"
    )

    #--------------------------------------------------------------------------
    #  "Component" interface:
    #--------------------------------------------------------------------------

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
        )
    )

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws a closed polygon. """

        gc.save_state()
        try:
#            self._draw_bounds(gc)
            if len(self.points) >= 2:
                # Set the drawing parameters.
                gc.set_fill_color(self.pen.fill_color_)
                gc.set_stroke_color(self.pen.color_)
                gc.set_line_width(self.pen.line_width)

                # Draw the path.
                gc.begin_path()
                gc.lines(self.points)

                gc.stroke_path()
        finally:
            gc.restore_state()


    def _draw_bounds(self, gc):
        """ Draws the component bounds for testing purposes. """

        dx, dy = self.bounds
        x, y = self.position
        gc.rect(x, y, dx, dy)
        gc.stroke_path()


    def normal_left_down(self, event):
        """ Handles left mouse button clicks in 'normal' mode """

        print "Polyline selected at (%d, %d)" % (event.x, event.y)


    @on_trait_change("pen.+,points")
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
    from component_viewer import ComponentViewer

    pen = Pen()
    polyline = Polyline(
        pen=pen, points=[(50, 50), (50, 100), (100, 100)],
#        bounds=[50, 50], position=[50, 50]
    )

    viewer = ComponentViewer(component=polyline)

    from enthought.enable.primitives.api import Box
    box = Box(
        color="red", border_color="blue", border_size=1,
        bounds=[50, 50], position=[100, 100]
    )
#    viewer.canvas.add(box)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------
