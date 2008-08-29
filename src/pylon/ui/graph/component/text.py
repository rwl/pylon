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

References:
    Jose.R.Fonseca, 'XDot', http://code.google.com/p/jrfonseca/wiki/XDot

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from math import sqrt

from enthought.traits.api import \
    Instance, Float, Int, String, Trait, on_trait_change

from enthought.traits.ui.api import View, Item, Group
from enthought.enable.api import Component
#from enthought.kiva import Font as KivaFont
#from enthought.kiva import MODERN
from enthought.kiva.fonttools.font import str_to_font
#from enthought.kiva import Font, MODERN

from pen import Pen

#------------------------------------------------------------------------------
#  "Text" class:
#------------------------------------------------------------------------------

class Text(Component):
    """ Component with text traits """

    #--------------------------------------------------------------------------
    #  "Text" interface:
    #--------------------------------------------------------------------------

    # The background color of this component.
    bgcolor = "transparent"#"fuchsia"

    # Pen for drawing text
    pen = Instance(Pen, desc="pen instance with which to draw the text")

    # X-axis coordinate
    text_x = Float(desc="x-axis coordinate")

    # Y-axis coordinate
    text_y = Float(desc="y-axis coordinate")

    # Text justification
    justification = Int(-1, desc="(LEFT, CENTER, RIGHT = -1, 0, 1)")
#    justification = Trait("Left", {"Left": -1, "Centre": 0, "Right": 1})

    # Width of the text
    text_w = Float(desc="width of the text as computed by the library")

    # Text to be drawn
    text = String(desc="text")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Group(
            Item("pen", style="custom", show_label=False),
            label="Pen", show_border=True
        ),
        Item("text_x"), Item("text_y"), Item("text_w"),
        Item("justification"), Item("text")
    )

    #--------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #--------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draws the component """

        gc.save_state()
        try:
            # Specify the font
            font = str_to_font(str(self.pen.font))
            gc.set_font(font)

            gc.set_fill_color(self.pen.colour_)

            x = self.text_x - (self.text_w/2)
            y = self.text_y# - (font.size/2)

            # Show text at the same scale as the graphics context
            ctm = gc.get_ctm()
            if hasattr(ctm, "__len__") and len(ctm) == 6:
                scale = sqrt( (ctm[0]+ctm[1]) * (ctm[0]+ctm[1]) / 2.0 + \
                              (ctm[2]+ctm[3]) * (ctm[2]+ctm[3]) / 2.0 )
            elif hasattr(gc, "get_ctm_scale"):
                scale = gc.get_ctm_scale()
            else:
                raise RuntimeError("Unable to get scale from GC.")
            x *= scale
            y *= scale
            gc.show_text_at_point(self.text, x, y)
        finally:
            gc.restore_state()


    @on_trait_change("pen.+,text_x,text_y,text_w,justification,text")
    def _update(self):
        if self.pen is None: return
        x = self.text_x - (self.text_w/2)
        x2 = x+self.text_w
        y = self.text_y# - (font.size/2)
        font = str_to_font(str(self.pen.font))
        y2 = y+font.size
        self.position = [x, y]
        # If bounds are set to 0, horizontal/vertical lines will not render
        self.bounds = [max(x2-x, 1), max(y2-y, 1)]

        self.request_redraw()


    def normal_left_down(self, event):
        print "Text [%s] selected at (%d, %d)" % (self.text, event.x, event.y)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.ui.graph.component_viewer import ComponentViewer

    text = Text(
        pen=Pen(), text="Foo",
        text_x=50, text_y=50, text_w=30
    )

    viewer = ComponentViewer(component=text)

    viewer.configure_traits()

# EOF -------------------------------------------------------------------------
