#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Defines a tile component of a grid based map """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from StringIO import StringIO

from enthought.traits.api import Any, Trait
from enthought.enable.api import Component
from enthought.kiva.backend_image import Image

#------------------------------------------------------------------------------
#  "Tile" component class:
#------------------------------------------------------------------------------

class Tile(Component):
    """ A map tile """

    # Image as a file-like object
    image = Any#Trait(StringIO)

    bgcolor = "transparent"

    #--------------------------------------------------------------------------
    #  Draw the component in a specified graphics context:
    #--------------------------------------------------------------------------

#    def _draw(self, gc):
    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draw the component in a specified graphics context """

        self.image.seek(0)
        img = Image(self.image)

        x, y = self.position

        gc.draw_image(img, (x, y, img.width(), img.height()))

# EOF -------------------------------------------------------------------------
