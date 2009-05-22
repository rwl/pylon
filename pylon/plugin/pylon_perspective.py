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

""" Pylon workbench perspectives.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.workbench.api import Perspective, PerspectiveItem

#------------------------------------------------------------------------------
#  "PylonEditPerspective" class:
#------------------------------------------------------------------------------

class PylonEditPerspective(Perspective):
    """ The Pylon editing perspective.
    """
    # The perspective's unique identifier (unique within a workbench window).
    id = "pylon.plugin.pylon_edit_perspective"

    # The perspective's name.
    name = "Pylon"

    # Should the editor area be shown in this perspective:
    show_editor_area = True

    # The contents of the perspective:
    contents = [
        PerspectiveItem(
            id="puddle.resource.resource_view",
            position="left", width=0.2),
        PerspectiveItem(
            id="enthought.plugins.python_shell_view",
            position="bottom", height=0.2),
        PerspectiveItem(
            id="enthought.logger.plugin.view.logger_view.LoggerView",
            position="with", height=0.2,
            relative_to="enthought.plugins.python_shell_view"),
        PerspectiveItem(
            id="puddle.property_view.property_view",
            position="right", width=0.2),
        PerspectiveItem(
            id="enthought.plugins.ipython_shell.namespace_view",
            position="with", width=0.2,
            relative_to="puddle.property_view.property_view")
    ]

# EOF -------------------------------------------------------------------------
