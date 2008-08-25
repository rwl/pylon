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

""" Defines a layer for the Open Street Map tile server """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import math
from StringIO import StringIO

from urllib2 import \
    ProxyHandler, build_opener, OpenerDirector, HTTPError, URLError

from enthought.traits.api import implements, Int, Trait
from enthought.enable.api import Canvas, ColorTrait

from i_layer import ILayer
from tile import Tile

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

MISSING_TILE_URL = "http://openstreetmap.org/openlayers/img/404.png"

#------------------------------------------------------------------------------
#  "OSM" class:
#------------------------------------------------------------------------------

class OSM(Canvas):
    """ Defines a layer for the Open Street Map tile server """

    implements(ILayer)

    #--------------------------------------------------------------------------
    #  "Canvas" interface:
    #--------------------------------------------------------------------------

    bgcolor = ColorTrait("darkturquoise")

    draw_axes = True

    #--------------------------------------------------------------------------
    #  "OSM" interface:
    #--------------------------------------------------------------------------

    zoom_level = Int

    # Opener of URLs
    opener = Trait(OpenerDirector)

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _opener_default(self):
        """ Trait initialiser """

        proxies = {"http": "http://www-cache5.strath.ac.uk:8080"}
        proxy_handler = ProxyHandler(proxies)
#        proxy_auth_handler = HTTPBasicAuthHandler()
#        proxy_auth_handler.add_password('realm', 'host', 'username', 'password')

        return build_opener(proxy_handler)#, proxy_auth_handler)


    def add_tiles(self, pos, width, height):
        """ Filename(url) format is /zoom/x/y.png """

        res = 256
        zoom = self.zoom_level

        n = int(math.pow(2, zoom)) # n-by-n map
        tiles_wide = width/res
        tiles_high = height/res
        if tiles_wide > n:
            tiles_wide = n
        if tiles_high > n:
            tiles_high = n

        print "VISIBLE:", tiles_wide, tiles_high

        for x in range(tiles_wide):
            for y in range(tiles_high):
                if not self.components_at(x*res, y*res):

                    print x, y, pos, width, height

                    img = self.get_image(zoom, x, y)

                    img_file = StringIO()
                    img_file.write(img.read())

                    tile = Tile(
                        image=img_file, bounds=[res, res],
                        position=[x*res, (tiles_high-(y+1))*res]
                    )
                    self.add(tile)


    def get_image(self, zoom, x, y):
        """ Returns an image from the OSM server as a file-like object """

        url = "http://tile.openstreetmap.org/%s/%s/%s.png" % (zoom, x, y)
        try:
            u = self.opener.open(url)
        except URLError:
            u = self.opener.open(MISSING_TILE_URL)

        return u

# EOF -------------------------------------------------------------------------
