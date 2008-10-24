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

from enthought.traits.api import HasTraits, List, Instance

from enthought.enable.api import Component

from pylon.ui.graph.component.node import DiagramNode
from pylon.ui.graph.component.edge import DiagramEdge
from pylon.ui.graph.component.text import Text

class DiagramCanvas(HasTraits):

#    figures = List(Instance(Component))

    nodes = List(Instance(DiagramNode))

    connections = List(Instance(DiagramEdge))

    labels = List(Instance(Text))

# EOF -------------------------------------------------------------------------
