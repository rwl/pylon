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

""" Defines a text component.

See: XDot by Jose.R.Fonseca (http://code.google.com/p/jrfonseca/wiki/XDot)

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Float, Int, String
from enthought.enable.api import Component
#from enthought.kiva import Font, MODERN

from pen import Pen

#------------------------------------------------------------------------------
#  "Text" class:
#------------------------------------------------------------------------------

class Text(Component):
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

# EOF -------------------------------------------------------------------------
