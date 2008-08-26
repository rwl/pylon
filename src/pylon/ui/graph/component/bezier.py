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

See: XDot by Jose.R.Fonseca (http://code.google.com/p/jrfonseca/wiki/XDot)

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Float, List, Tuple
from enthought.enable.api import Component

from pen import Pen

#------------------------------------------------------------------------------
#  "Bezier" class:
#------------------------------------------------------------------------------

class Bezier(Component):
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

# EOF -------------------------------------------------------------------------
