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

""" DC Optimal Power Flow plug-in for Pylon """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin

from enthought.traits.api import Instance, List

#------------------------------------------------------------------------------
#  "DCOPFPlugin" class:
#------------------------------------------------------------------------------

class DCOPFPlugin(Plugin):
    """ DC Optimal Power Flow plug-in """

    # Extension point IDs
    ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"

    # Unique plugin identifier
    id = "pylon.plugin.routine.dc_opf_plugin"

    # Human readable plugin name
    name = "DC OPF"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed action sets:
    action_sets = List(contributes_to=ACTION_SETS)

    #--------------------------------------------------------------------------
    #  "DCOPFPlugin" interface:
    #--------------------------------------------------------------------------

    def _action_sets_default(self):
        """ Trait initialiser """

        from pylon.plugin.routine.dc_opf.dc_opf_action_set import \
            DCOPFActionSet

        return [DCOPFActionSet]

# EOF -------------------------------------------------------------------------
