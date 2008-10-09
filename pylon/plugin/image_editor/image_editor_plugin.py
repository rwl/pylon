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
#  Date:   14/06/2008
#
#------------------------------------------------------------------------------

""" Image editor plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin

from enthought.traits.api import List, Dict, String

#------------------------------------------------------------------------------
#  "ImageEditorPlugin" class:
#------------------------------------------------------------------------------

class ImageEditorPlugin(Plugin):
    """ Image editor plug-in """

    # Extension point IDs
    EDITORS = "enthought.plugins.workspace.editors"

    # Unique plugin identifier
    id = "enthought.plugins.image_editor"

    # Human readable plugin name
    name = "Image Editor"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed workspace editors:
    editors = List(contributes_to=EDITORS)

    #--------------------------------------------------------------------------
    #  "ImageEditorPlugin" interface:
    #--------------------------------------------------------------------------

    def _editors_default(self):
        """ Trait initialiser """

        from image_editor_extension import ImageEditorExtension

        return [ImageEditorExtension]

# EOF -------------------------------------------------------------------------
