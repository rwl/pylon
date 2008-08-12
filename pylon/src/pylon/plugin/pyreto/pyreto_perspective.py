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
Pyreto perspectives

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.workbench.api import Perspective, PerspectiveItem

#------------------------------------------------------------------------------
#  "PyretoPerspective" class:
#------------------------------------------------------------------------------

class PyretoPerspective(Perspective):
    """ The Pyreto editing perspective. """

    # The perspective's name.
    name = "Pyreto"

    # Should the editor area be shown in this perspective:
    show_editor_area = True

    # The contents of the perspective:
    contents = [
        PerspectiveItem(
            id="pylon.plugin.pyreto.pyreto_tree_view", position="left"
        ),
        PerspectiveItem(
            id="pylon.plugin.project_tree_view", position="with",
            relative_to="pylon.plugin.pyreto.pyreto_tree_view"
        ),
        PerspectiveItem(
            id="enthought.plugins.ipython_shell_view", position="bottom"
        )
    ]

# EOF -------------------------------------------------------------------------
