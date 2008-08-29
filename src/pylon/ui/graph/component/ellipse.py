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

from math import pi, sqrt

from enthought.traits.api import Instance, Float, Int, Bool, on_trait_change
from enthought.traits.ui.api import View, Item, Group
from enthought.enable.api import Component, Pointer
from enthought.kiva import FILL_STROKE

from pen import Pen

#------------------------------------------------------------------------------
#  "Ellipse" class:
#------------------------------------------------------------------------------

class Ellipse(Component):
    """ Component with Ellipse traits """

    #--------------------------------------------------------------------------
    #  "Ellipse" interface:
    #--------------------------------------------------------------------------

    # Pen used to draw the ellipse
    pen = Instance(Pen, desc="Pen instance with which to draw the ellipse")

    # X-axis coordinate of ellipse origin
    x_origin = Float(desc="x-axis coordinate of ellipse origin")

    # Y-axis coordinate of ellipse origin
    y_origin = Float(desc="y-axis coordinate of ellipse origin")

    # Width of the ellipse (semi-major axis)
    e_width = Float(desc="Ellipse width")

    # Height of the ellipse (semi-minor axis)
    e_height = Float(desc="Ellipse height")

    # Is the ellipse filled?
    filled = Bool(False, desc="Fill the ellipse")

    # The background color of this component.
    bgcolor = "fuchsia"

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Group(
            Item("pen", style="custom", show_label=False),
            label="Pen", show_border=True
        ),
        Item("x_origin"), Item("y_origin"),
        Item("e_width", label="Width"),
        Item("e_height", label="Height"),
        Item("filled")
    )

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws the component """

        x_origin = self.x_origin
        y_origin = self.y_origin

        gc.save_state()
        try:
#            self._draw_bounds(gc)
            gc.begin_path()
            gc.translate_ctm(x_origin, y_origin)
            gc.scale_ctm(self.e_width, self.e_height)
            gc.arc(0.0, 0.0, 1.0, 0, 2.0*pi)
            gc.close_path()

            # Draw stroke at same scale as graphics context
#            ctm = gc.get_ctm()
#            if hasattr(ctm, "__len__") and len(ctm) == 6:
#                scale = sqrt( (ctm[0]+ctm[1]) * (ctm[0]+ctm[1]) / 2.0 + \
#                              (ctm[2]+ctm[3]) * (ctm[2]+ctm[3]) / 2.0 )
#            elif hasattr(gc, "get_ctm_scale"):
#                scale = gc.get_ctm_scale()
#            else:
#                raise RuntimeError("Unable to get scale from GC.")

            gc.set_line_width(self.pen.line_width)
            gc.set_stroke_color(self.pen.colour_)

            if self.filled:
                gc.set_fill_color(self.pen.fill_colour_)
                gc.draw_path(FILL_STROKE)
            else:
                gc.stroke_path()
        finally:
            gc.restore_state()


    def is_in(self, point_x, point_y):
        """ Test if the point is within this ellipse """

        x = self.x_origin
        y = self.y_origin
        a = self.e_width#/2 # FIXME: Why divide by two
        b = self.e_height#/2

        return ((point_x-x)**2/(a**2)) + ((point_y-y)**2/(b**2)) < 1.0


    def _draw_bounds(self, gc):
        """ Draws the component bounds for testing purposes """

        dx, dy = self.bounds
        x, y = self.position
        gc.rect(x, y, dx, dy)
        gc.stroke_path()


    def normal_left_down(self, event):
        """ Handles left mouse button clicks in 'normal' mode """

        print "Ellipse selected at (%d, %d)" % (event.x, event.y)


    @on_trait_change("pen.+,x_origin,y_origin,e_width,e_height,filled,container")
    def _update(self):

        x_origin = self.x_origin
        y_origin = self.y_origin

        x = x_origin-(self.e_width)
        x2 = x_origin+(self.e_width)
        y = y_origin-(self.e_height)
        y2 = y_origin+(self.e_height)
        self.position = [x,y]
        # If bounds are set to 0, horizontal/vertical lines will not render
        self.bounds = [max(x2-x, 1), max(y2-y, 1)]

        self.request_redraw()

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.ui.graph.component_viewer import ComponentViewer

    pen = Pen()
    ellipse = Ellipse(
#        filled=True,
        pen=pen, x_origin=150, y_origin=100, e_width=100, e_height=50,
#        bounds=[50, 50], position=[0, 0]

    )

    from enthought.enable.api import Container
    con = Container(bounds=[100, 50], position=[200, 200], bgcolor="green")
    con.add(ellipse)

    viewer = ComponentViewer(component=con)

    from enthought.enable.primitives.api import Box
    box = Box(
        color="steelblue", border_color="darkorchid", border_size=1,
        bounds=[50, 50], position=[50, 50]
    )
    viewer.canvas.add(box)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------
