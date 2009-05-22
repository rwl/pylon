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

""" PSS/E data file import plug-in.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin
from enthought.traits.api import Instance, List

#------------------------------------------------------------------------------
#  "PSSEPlugin" class:
#------------------------------------------------------------------------------

class PSSEPlugin(Plugin):
    """ PSS/E data file import plug-in.
    """

    # Extension point IDs
    IMPORT_WIZARDS = "puddle.resource.import_wizards"

    # Unique plugin identifier
    id = "pylon.plugin.readwrite.psse.psse_plugin"

    # Human readable plugin name
    name = "PSS/E Reader"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed resource import wizards:
    import_wizards = List(contributes_to=IMPORT_WIZARDS)

    #--------------------------------------------------------------------------
    #  "PSSEPlugin" interface:
    #--------------------------------------------------------------------------

    def _import_wizards_default(self):
        """ Trait initialiser.
        """
        from psse_wizard_extension import PSSEImportWizardExtension

        return [PSSEImportWizardExtension]

# EOF -------------------------------------------------------------------------
