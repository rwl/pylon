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

""" Defines an edge container """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance
from enthought.enable.api import Container

from text import Text
from node import Node

#------------------------------------------------------------------------------
#  "Edge" class:
#------------------------------------------------------------------------------

class Edge(Container):
    """ Defines a container for all components constituting an edge """

    # Main text label of the edge
    label = Instance(Text)

    # Text label positioned near the head of the edge
    head_label = Instance(Text)

    # Text label positioned near the tail of the edge
    tail_label = Instance(Text)

    # From/source/start node container
    source_node = Instance(Node)

    # To/target/end node container
    target_node = Instance(Node)

    #--------------------------------------------------------------------------
    #  Component interface
    #--------------------------------------------------------------------------

    # The background colour of this component.
    bgcolor = "transparent"

# EOF -------------------------------------------------------------------------
