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

""" Defines a node container """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Either
from enthought.enable.api import Container

from text import Text
from ellipse import Ellipse
from polygon import Polygon

#------------------------------------------------------------------------------
#  "Node" class:
#------------------------------------------------------------------------------

class Node(Container):
    """ Defines a container for all components constituting a node """

    # Main node label
    label = Instance(Text)

    # Outermost shape
    node = Either(Ellipse, Polygon)

    #--------------------------------------------------------------------------
    #  Component interface
    #--------------------------------------------------------------------------

    # The background colour of this component.
    bgcolor = "transparent"

    def _position_changed(self, new):

        print "Node position:", new

# EOF -------------------------------------------------------------------------
