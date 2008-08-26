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

from enthought.traits.api import Instance, Float, Bool, List, Trait, Tuple
from enthought.enable.api import Component
from enthought.kiva import EOF_FILL_STROKE, FILL_STROKE

from pen import Pen

#------------------------------------------------------------------------------
#  "Polygon" class:
#------------------------------------------------------------------------------

class Polygon(Component):
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
        "winding", {"winding":FILL_STROKE, "oddeven":EOF_FILL_STROKE},
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

# EOF -------------------------------------------------------------------------
