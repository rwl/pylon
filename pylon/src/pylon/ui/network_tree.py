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

"""
Tree editor for Pylon networks

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item

from pylon.network import Network
from pylon.bus import Bus
from pylon.branch import Branch
from pylon.generator import Generator
from pylon.load import Load

from pylon.ui.network_view import \
    minimal_view, buses_view, branches_view, \
    all_generators_view, all_loads_view

from pylon.ui.bus_view import bus_view, generators_view, loads_view
from pylon.ui.branch_view import branch_view
from pylon.ui.generator_view import generator_view
from pylon.ui.load_view import load_view

#------------------------------------------------------------------------------
#  Network tree editor:
#------------------------------------------------------------------------------

no_view = View()

network_tree_editor = TreeEditor(
    nodes=[
        TreeNode(
            node_for=[Network],
            auto_open=True, children="", label="name",
            view=minimal_view,
        ),
        TreeNode(
            node_for=[Network], auto_open=True,
            children="buses", label="=Buses",
            view=buses_view, add=[Bus]
        ),
        TreeNode(
            node_for=[Network], auto_open=True,
            children="branches", label="=Branches",
            view=branches_view,
        ),
        TreeNode(
            node_for=[Network], auto_open=False,
            children="generators", label="=_generators",
            view=all_generators_view,
        ),
        TreeNode(
            node_for=[Network], auto_open=False,
            children="loads", label="=_loads",
            view=all_loads_view
        ),
        TreeNode(
            node_for=[Bus], label="name", view=bus_view
        ),
        TreeNode(
            node_for=[Bus], children="generators", label="=Generators",
            view=generators_view, add=[Generator]
        ),
        TreeNode(
            node_for=[Bus], children="loads", label="=Loads",
            view=loads_view, add=[Load]
        ),
        TreeNode(
            node_for=[Branch], auto_open=True, label="name",
            view=branch_view
        ),
        TreeNode(
            node_for=[Generator], label="name", view=generator_view
        ),
        TreeNode(
            node_for=[Load], label="name", view=load_view
        ),
    ],
    orientation="horizontal"
)

# EOF -------------------------------------------------------------------------
