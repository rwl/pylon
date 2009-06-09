#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" MATPOWER data file plug-in.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin
from enthought.traits.api import Instance, List

#------------------------------------------------------------------------------
#  "MATPOWERPlugin" class:
#------------------------------------------------------------------------------

class MATPOWERPlugin(Plugin):
    """ MATPOWER data file import plug-in
    """

    # Extension point IDs
    PREFERENCES_PAGES = "enthought.envisage.ui.workbench.preferences_pages"
    IMPORT_WIZARDS = "puddle.resource.import_wizards"
    EXPORT_WIZARDS = "puddle.resource.export_wizards"

    # Unique plugin identifier
    id = "pylon.plugin.readwrite.matpower_plugin"

    # Human readable plugin name
    name = "MATPOWER Reader"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed resource import wizards:
    import_wizards = List(contributes_to=IMPORT_WIZARDS)

    # Contributed resource export wizards:
    export_wizards = List(contributes_to=EXPORT_WIZARDS)

    #--------------------------------------------------------------------------
    #  "MATPOWERPlugin" interface:
    #--------------------------------------------------------------------------

    def _import_wizards_default(self):
        """ Trait initialiser.
        """
        from matpower_wizard import MATPOWERImportWizardExtension

        return [MATPOWERImportWizardExtension]


    def _export_wizards_default(self):
        """ Trait initialiser.
        """
        from matpower_wizard import MATPOWERExportWizardExtension

        return [MATPOWERExportWizardExtension]

# EOF -------------------------------------------------------------------------
