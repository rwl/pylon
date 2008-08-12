#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Richard W. Lincoln
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Richard W. Lincoln
#  Date:   09/07/2008
#
#------------------------------------------------------------------------------

""" Property view plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin
from enthought.traits.api import List

#------------------------------------------------------------------------------
#  "PropertyViewPlugin" class:
#------------------------------------------------------------------------------

class PropertyViewPlugin(Plugin):
    """ Property view plug-in """

    # Extension point IDs
    VIEWS = "enthought.envisage.ui.workbench.views"

    # Unique plugin identifier
    id = "enthought.plugins.property_view"

    # Human readable plugin name
    name = "Property View"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Views contributed to the workbench:
    contributed_views = List(contributes_to=VIEWS)

    #--------------------------------------------------------------------------
    #  "PropertyViewPlugin" interface:
    #--------------------------------------------------------------------------

    def _contributed_views_default(self):
        """ Trait initialiser """

        from property_view import PropertyView

        return [PropertyView]

# EOF -------------------------------------------------------------------------
