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

@mlab.show
def planet():
    """ Creates a planet! """

#    x = numpy.random.random((4,))
#    y = numpy.random.random((4,))
#    z = numpy.random.random((4,))
#
#    mlab.points3d(x, y, z, mode="sphere", scale_factor=0.1, opacity=0.8)
#
#    mlab.show()

    #test_imshow()
    test_surf()


@mlab.show
def test_mesh_sphere(r=1.0, npts=(5, 9), colormap="Blues"):
    """Create a simple sphere."""
    pi = numpy.pi
    cos = numpy.cos
    sin = numpy.sin
    np_phi = npts[0]*1j
    np_theta = npts[1]*1j
    phi, theta = numpy.mgrid[0:pi:np_phi, 0:2*pi:np_theta]
    x = r*sin(phi)*cos(theta)
    print x
    y = r*sin(phi)*sin(theta)
    z = r*cos(phi)
    mlab.mesh(x, y, z, colormap=colormap)

#    mlab.view(.0, -5.0, 6.)
#    mlab.show()


test_mesh_sphere()
#planet()

# EOF -------------------------------------------------------------------------
