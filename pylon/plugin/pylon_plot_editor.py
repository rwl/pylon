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

""" Defines a plot editor for Pylon resources """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.plugins.workspace.resource_editor import ResourceEditor

from pylon.ui.plot.bus_bar_plot import BusBarPlot

#------------------------------------------------------------------------------
#  "PylonPlotEditor" class:
#------------------------------------------------------------------------------

class PylonPlotEditor(ResourceEditor):
    """ Defines a plot editor for Pylon resources """

    #--------------------------------------------------------------------------
    #  "ResourceEditor" interface
    #--------------------------------------------------------------------------

    def create_ui(self, parent):
        """ Creates the traits UI that represents the editor """

        self.document = document = self.provider.create_document(self.obj)
        plot = BusBarPlot(network=document)

        ui = plot.edit_traits(parent=parent, kind="subpanel")

        return ui

# EOF -------------------------------------------------------------------------
