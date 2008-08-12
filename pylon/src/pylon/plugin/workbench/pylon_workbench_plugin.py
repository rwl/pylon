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

""" Pylon workbench plug-in with customised actions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.workbench.workbench_plugin import WorkbenchPlugin

#------------------------------------------------------------------------------
#  "PylonWorkbenchPlugin" class:
#------------------------------------------------------------------------------

class PylonWorkbenchPlugin(WorkbenchPlugin):
    """ Overridden actions and preferences pages """

    #--------------------------------------------------------------------------
    #  "WorkbenchPlugin" interface:
    #--------------------------------------------------------------------------

    def _my_preferences_pages_default(self):
        """ Trait initialiser. """

        from pylon_workbench_preferences_page import \
            PylonWorkbenchPreferencesPage

        return [PylonWorkbenchPreferencesPage]


    def _my_action_sets_default(self):
        """ Trait initialiser """

        from pylon_workbench_action_set import PylonWorkbenchActionSet

#        action_sets = super(PylonWorkbenchPlugin, self)._my_action_sets_default()

        return [PylonWorkbenchActionSet]# + action_sets

# EOF -------------------------------------------------------------------------
