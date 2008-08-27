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

from enthought.traits.api import Instance, Float, List, Tuple, on_trait_change
from enthought.traits.ui.api import View, Item, Group
from enthought.enable.api import Component

from pen import Pen

def nsplit(seq, n=2):
    """Split a sequence into pieces of length n

    If the lengt of the sequence isn't a multiple of n, the rest is discareded.
    Note that nsplit will strings into individual characters.

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
    bgcolor = (1.0, 0.5, 0.5, 1.0)

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

        gc.save_state()
        try:
            gc.set_fill_color(self.pen.fill_colour_)

            gc.set_line_width(self.pen.line_width)
            gc.set_stroke_color(self.pen.colour_)

            gc.begin_path()
            x0, y0 = self.points[0]
            gc.lines(self.points)
            gc.move_to(x0, y0)
            for i in xrange(0, len(self.points), 3):
                x1, y1 = self.points[i]
                x2, y2 = self.points[i + 1]
                x3, y3 = self.points[i + 2]
                gc.curve_to(x1, y1, x2, y2, x3, y3)
#            gc.close_path()
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
#        # FIXME: This is likely slow for large numbers of lines
#        pt1 = self.points[0]
#        pt2 = self.points[-1]
#        mouse = [x, y]
#
#        # How close to the line do we have to be?
#        tolerance = 3
#
#        # If the length of the enable_line is 0, returning False
#        xdiff, ydiff = pt1[0]-pt2[0], pt1[1]-pt2[1]
#
#        if xdiff <= 0 or ydiff <= 0:
#            result = False
#        elif (distance_to_line(pt1, pt2, mouse) < tolerance and
#            point_in_box(pt1, pt2, mouse, tolerance)):
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

    bezier = Bezier(
        pen=Pen(line_width=1), points=[(50, 50), (75, 100), (50, 150)],
#        bounds=[50, 50], position=[50, 50]
    )

    viewer = ComponentViewer(component=bezier)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------
