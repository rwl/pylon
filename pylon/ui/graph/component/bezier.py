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

""" Defines a Bezier line component.

References:
    Jose.R.Fonseca, 'XDot', http://code.google.com/p/jrfonseca/wiki/XDot

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from itertools import izip

from enthought.traits.api import Instance, Float, List, Tuple, on_trait_change
from enthought.traits.ui.api import View, Item, Group
from enthought.enable.api import Component

from pen import Pen
from recipes import cubic

#def calculate_bezier(p, steps = 30):
#    """ Calculate a bezier curve from 4 control points and return a
#    list of the resulting points.
#
#    The function uses the forward differencing algorithm described here:
#    http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
#
#    """
#
#    t = 1.0 / steps
#    temp = t*t
#
#    f = p[0]
#    fd = 3 * (p[1] - p[0]) * t
#    fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
#    fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t
#
#    fddd = fddd_per_2 + fddd_per_2
#    fdd = fdd_per_2 + fdd_per_2
#    fddd_per_6 = fddd_per_2 * (1.0 / 3)
#
#    points = []
#    for x in range(steps):
#        points.append(f)
#        f = f + fd + fdd_per_2 + fddd_per_6
#        fd = fd + fdd + fddd_per_2
#        fdd = fdd + fddd
#        fdd_per_2 = fdd_per_2 + fddd_per_2
#    points.append(f)
#    return points


def nsplit(seq, n=2):
    """Split a sequence into pieces of length n

    If the length of the sequence isn't a multiple of n, the rest is discarded.
    Note that nsplit will split strings into individual characters.

    Examples:
    >>> nsplit('aabbcc')
    [('a', 'a'), ('b', 'b'), ('c', 'c')]
    >>> nsplit('aabbcc',n=3)
    [('a', 'a', 'b'), ('b', 'c', 'c')]

    # Note that cc is discarded
    >>> nsplit('aabbcc',n=4)
    [('a', 'a', 'b', 'b')]

    """

    return [xy for xy in izip(*[iter(seq)]*n)]

#------------------------------------------------------------------------------
#  "Bezier" class:
#------------------------------------------------------------------------------

class Bezier(Component):
    """ Component with Bezier traits """

    # Pen used to draw the Bezier curve
    pen = Instance(Pen, desc="Pen instance with which to draw the component")

    # Points defining the path of the polygon
    points = List(
        Tuple(Float, Float, labels=["x", "y"], cols=2),
        desc="Point defining the path of the polygon"
    )

    # Background colour of the component
    bgcolor = "transparent"#(1.0, 0.5, 0.5, 1.0)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Group(
            Item("pen", style="custom", show_label=False),
            label="Pen", show_border=True
        ),
        Item("points", height=250, show_label=False)
    )

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws the Bezier component """

        if not self.points: return
        gc.save_state()
        try:
            gc.set_fill_color(self.pen.fill_colour_)

            gc.set_line_width(self.pen.line_width)
            gc.set_stroke_color(self.pen.colour_)

            gc.begin_path()
            start_x, start_y = self.points[0]
            gc.move_to(start_x, start_y)
            for triple in nsplit(self.points[1:], 3):
                x1, y1 = triple[0]
                x2, y2 = triple[1]
                end_x, end_y = triple[2]
                gc.curve_to(x1, y1, x2, y2, end_x, end_y)
                # One point overlap
                gc.move_to(end_x, end_y)
            gc.stroke_path()
        finally:
            gc.restore_state()


    def normal_left_down(self, event):
        """ Handles left mouse button clicks in 'normal' mode """

        print "Bezier selected at (%d, %d)" % (event.x, event.y)

    #--------------------------------------------------------------------------
    #  CoordinateBox interface
    #--------------------------------------------------------------------------

#    def is_in(self, x, y):
#        """ Tests if a point is within a certain tolerance of the line """
#
#        if not self.points: return False
#
#        # First-pass bounding box check
#        minx, miny = self.position
#        maxx = minx + self.bounds[0]
#        maxy = miny + self.bounds[1]
#        if (minx <= x <= maxx) and (miny <= y <= maxy):
#            print "IS IN?"
#            # P(t) = (1-t)^3 P0 + 3t(1-t)^2 P1 + 3(1-t)t^2 P2 + t^3 P3
#            x0, y0 = self.points[0]
#            for triple in nsplit(self.points[1:], 3):
#                x1, y1 = triple[0]
#                x2, y2 = triple[1]
#                x3, y3 = triple[2]
#
#                a = -x0 + 3*x1 - 3*x2 + x3
#                b = 3*x0 - 6*x1 + 3*x2
#                c = -3*x0 + 3*x1
#                d = x0 - x
#                t, r2, r3 = cubic(a, b, c, d)
#
#                ans = ((1-t)**3)*x0 + 3*t*((1-t)**2)*x1 + 3*(1-t)*(t**2)*x2 + (t**3)*x3
#
#                print "ANS:", ans
#
#                ay = -y0 + 3*y1 - 3*y2 + y3
#                by = 3*y0 - 6*y1 + 3*y2
#                cy = -3*y0 + 3*y1
#                dy = y0 - y
#                ry1, ry2, ry3 = cubic(ay, by, cy, dy)
#
#                print "Root 1:", t, ry1
#                print "Root 2:", r2, ry2
#                print "Root 3:", r3, ry3
#
##                x0, y0 = triple[2]
#            result = True
#        else:
#            result = False
#
#        return result

    #--------------------------------------------------------------------------
    #  Bezier interface
    #--------------------------------------------------------------------------

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
        # If bounds are set to 0, horizontal/vertical lines will not render
        self.bounds = [max(x2-x,1), max(y2-y,1)]

        self.request_redraw()

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.ui.graph.component_viewer import ComponentViewer

    bezier = Bezier(
        pen=Pen(line_width=1),
        points=[(37.0, 90.0), (37.0, 77.0), (37.0, 61.0), (37.0, 46.0)]#[
#            (0, 50), (50, 0), (150, 0), (200, 150),
#            (25, 225), (75, 300), (100, 275),
#            (125, 200), (150, 100), (200, 25)
#        ],
    )

    viewer = ComponentViewer(component=bezier)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------
