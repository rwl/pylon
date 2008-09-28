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

from math import pow, ceil, floor
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

    # Tile resolution
    resolution = Int(256)

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

        res = self.resolution
        zoom = self.zoom_level

        # Viewport bounds
        minx, miny = pos
        maxx = minx + width
        maxy = miny + height

        print "BOUNDS: (%f, %f) (%f, %f)" % (minx, miny, maxx, maxy)

        n = int(pow(2, zoom)) # n-by-n map

        # Bounds of tiles visible in the viewport
        minx_tile = int(floor(minx/res))
        maxx_tile = int(ceil(maxx/res))
        miny_tile = int(floor(miny/res))
        maxy_tile = int(ceil(maxy/res))

        print "VISIBLE: (%d, %d) (%d, %d)" % (minx_tile, miny_tile, maxx_tile, maxy_tile)

        for x in range(minx_tile, maxx_tile):
            for y in range(miny_tile, maxy_tile):
                print "POSITION: (%d, %d)" % (x*res, y*res)
                if not self.components_at(x*res, y*res):
                    # Tile coords relative to map
                    x_tile = ((x % n) + n) % n

                    print "TILE: (%d, %d) %d %d" % (x, y, n, x_tile)

                    img = self.get_image(zoom, x_tile, n-(y+1), n)

                    img_file = StringIO()
                    img_file.write(img.read())

                    tile = Tile(
                        image=img_file, bounds=[res, res],
                        position=[x*res, y*res]
                    )
                    self.add(tile)

#                    from enthought.enable.primitives.api import Box
#
#                    box = Box(
#                        color="steelblue",
#                        border_color="darkorchid", border_size=2,
#                        bounds=[res, res],
#                        position=[x*res, y*res]
#                    )
#                    self.add(box)


    def get_image(self, zoom, x, y, limit):
        """ Returns an image from the OSM server as a file-like object """

        if (y < 0) or (y >= limit):
            url = MISSING_TILE_URL
        else:
            url = "http://tile.openstreetmap.org/%s/%s/%s.png" % (zoom, x, y)

        u = self.opener.open(url)

        return u

class parallelFetcher:
    '''This class is capable of downloading a list of URLs in parallel.
       This is merely an urllib2.open().read() executed by a pool of threads.
       It's handy to get multiple pages in parallel, while limiting the
       number of simultaneous connections.

       WARNING:This class is a quick hack and has been specialized for myRadioPlayer.
       - If an URL is wrong (wrong URL, HTTP error 404, etc.) the URL will simply
         be dropped.
       - Data returned is limited to 200 kb.

       Example:
            urls = ['http://google.com','http://sebsauvage.net','http://spamgourmet.com']
            p = parallelFetcher(urls)
            for (url,data) in p.fetch():
                print url,len(data)  # Data if the data returned from the URL.
    '''
    def __init__(self,urls,numberOfThreads=6):
        '''Go and get these URLs.

           Input:
               urls (list of string): The list of URLs to get.
               numberOfThreads (integer): The number of simultaneous threads
                                          It is not recommended to go over 8.
        '''
        self.inQueue  = Queue.Queue()  # The list of URLs to process
        self.outQueue = Queue.Queue()  # Processed URLs (list of tuples in the form (url,data))
        self.numberOfThreads = numberOfThreads
        for url in urls: # Put all URLs in the queue.
            self.inQueue.put(url)

    def fetch(self):
        ''' Start to fetch all URLs in parallel '''
        # Create and start all threads.
        threads = []
        for i in range(self.numberOfThreads):
            thread = threading.Thread(target=self._fetchURL)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        # Wait for all URLs to be processed.
        self.inQueue.join()  # Wait until the queue of URLs to process is empty
        for thread in threads: # And wait for threads to die (in order to avoid nasty error message when program exits)
            thread.join()

        # Get all processed URLs
        results = []
        while True:
            try:
                results.append(self.outQueue.get_nowait())
            except Queue.Empty:  # Empty exception means the Queue is empty.
                break # Exit the while loop.
        return results

    def _fetchURL(self):
        ''' Fetch data from an URL. This method will be called in parallel by several threads. '''
        headers = { 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache'   }
        while True:
            try:
                url = self.inQueue.get(block=True,timeout=1)  # Get an URL to process
            except Queue.Empty:  # No more URLs to process in the Queue
                break  # Exit this thread
            sys.stdout.write(".")
            data = None
            urlfile = None
            try:
                # Get the page:
                request = urllib2.Request(url, None, headers)
                urlfile = urllib2.urlopen(request)
                data = urlfile.read(200000)
            except urllib2.HTTPError,ex:
                pass
            except urllib2.URLError,ex:
                pass
            if urlfile:
                urlfile.close()
            if data:
                self.outQueue.put((url,data))
            self.inQueue.task_done()   # Tell the Queue I'm done with this URL.

# EOF -------------------------------------------------------------------------
