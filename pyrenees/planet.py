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

import numpy

from enthought.mayavi import mlab
from enthought.mayavi.tools.helper_functions import test_imshow, test_surf
from enthought.mayavi.scripts import mayavi2
from enthought.tvtk.api import tvtk

IMAGE_PATH = "/tmp/bluemarble.jpg"
#IMAGE_PATH = "/tmp/srtm.jpg"
STARS_IMAGE_PATH = "/tmp/stars.png"

def planet():
    """ Creates a planet! """

    pi = numpy.pi
    eps = 1e-4
    r = 6

    # A plane is defined by specifying an origin point, and then two other
    # points that, together with the origin, define two axes for the plane.
    #
    # Define a 2D plane to act as a base to apply a texture to. The coordinates
    # are specified as origin: {r, pi-eps, 0}, point 1: {r, pi-eps, 2*pi},
    # point 2: {r, eps, 0} and can be thought of as a rectangle oriented
    # parallel to the y-z plane and offset along the x-axis by r.
    ps = tvtk.PlaneSource(
        origin=(r, pi-eps, 0.0),
        point1=(r, pi-eps, 2*pi), point2=(r, eps, 0.0),
        x_resolution=37, y_resolution=19 # number of subdivisions
    )
    ps.update()

    # Converts (r,phi,theta) coordinates to (x,y,z) coordinates and back again
    #
    # Warp the plane's spherical coordinates to Cartesian coordinates using
    # SphericalTransfrom and TransformPolyDataFilter.  The transform will
    # map coordinates into a range suitable for texture mapping: [0,1].
    transform = tvtk.SphericalTransform()

    tpoly = tvtk.TransformPolyDataFilter(
        transform=transform, input=ps.output
    )

    print tpoly.output

    # Load an image: a map of the earth.
    earth = tvtk.JPEGReader(file_name=IMAGE_PATH)
    earth.update()
    earth.update_information()

    # Apply the image to a Texture so that the earth image can be mapped onto
    # our sphere.
    texture = tvtk.Texture(input=earth.output, interpolate=True)

    # Create a mapper to render the sphere.
    mapper = tvtk.DataSetMapper(input=tpoly.output)

    # Create an actor to display and interact with.  The actor will apply the
    # texture map to geometry of the sphere.
    world = tvtk.Actor(mapper=mapper, texture=texture)

    # Stars
    uni_r = 50
    stars_ps = tvtk.PlaneSource(
        origin=(uni_r, pi-eps, 0.0),
        point1=(uni_r, pi-eps, 2*pi), point2=(uni_r, eps, 0.0),
        x_resolution=37, y_resolution=19 # number of subdivisions
    )
    stars_ps.update()

    stars_transform = tvtk.SphericalTransform()

    stars_tpoly = tvtk.TransformPolyDataFilter(
        transform=stars_transform, input=stars_ps.output
    )

    stars = tvtk.PNGReader(file_name=STARS_IMAGE_PATH)
    stars.update()
    stars.update_information()

    stars_texture = tvtk.Texture(input=stars.output, interpolate=True)

    stars_mapper = tvtk.DataSetMapper(input=stars_tpoly.output)

    universe = tvtk.Actor(mapper=stars_mapper, texture=stars_texture)

    # Render window stuff and add actor.
    rw = tvtk.RenderWindow(size=(600, 600))
    ren = tvtk.Renderer(background=(0.5, 0.5, 0.5))
    rw.add_renderer(ren)
    rwi = tvtk.RenderWindowInteractor(render_window=rw)
    ren.add_actor(world)
    ren.add_actor(universe)
    rwi.initialize()
    rwi.start()

if __name__ == "__main__":
    planet()

# EOF -------------------------------------------------------------------------
