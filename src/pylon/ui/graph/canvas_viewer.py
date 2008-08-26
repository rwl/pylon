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

""" Defines a canvas with a viewport for testing purposes """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.ui.api import View, Item
from enthought.enable.api import Canvas, Viewport
from enthought.enable.tools.api import ViewportPanTool
from enthought.enable.component_editor import ComponentEditor

#------------------------------------------------------------------------------
#  "CanvasViewer" class:
#------------------------------------------------------------------------------

class CanvasViewer(HasTraits):
    canvas = Instance(Canvas)
    viewport = Instance(Viewport)
    traits_view = View(
        Item("viewport", editor=ComponentEditor(), show_label=False),
        resizable=True, id="canvas_viewer", width=.4, height=.4
    )

    def _canvas_default(self):
        canvas = Canvas(draw_axes=True)#bgcolor="lightslategrey")
        return canvas

    def _viewport_default(self):
        viewport = Viewport(component=self.canvas, enable_zoom=True)
        viewport.tools.append(ViewportPanTool(viewport))
        return viewport

# EOF -------------------------------------------------------------------------
