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

See: XDot by Jose.R.Fonseca (http://code.google.com/p/jrfonseca/wiki/XDot)

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Float, Int, Bool
from enthought.enable.api import Component

from pen import Pen

#------------------------------------------------------------------------------
#  "Ellipse" class:
#------------------------------------------------------------------------------

class Ellipse(Component):
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

# EOF -------------------------------------------------------------------------
