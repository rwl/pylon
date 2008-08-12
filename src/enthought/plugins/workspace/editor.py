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
#  Date:   21/07/2008
#
#------------------------------------------------------------------------------

""" Defines a extension to the "editors" extension point of the
workspace plug-in that associates editors with certain file extensions.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import HasTraits, Instance, Str, List, Bool
from enthought.pyface.api import ImageResource
from enthought.envisage.ui.action.api import Action

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "Editor" class:
#------------------------------------------------------------------------------

class Editor(HasTraits):
    """ Defines a extension to the "editors" extension point of the
    workspace plug-in that associates editors with certain file extensions.

    """

    # The object contribution's globally unique identifier.
    id = Str

    # A name that will be used in the UI for this editor
    name = Str

    # An icon that will be used for all resources that match the
    # specified extensions
    image = Instance(ImageResource)

    # The contributed editor class
    editor_class = Str

    # The list of file types understood by the editor
    extensions = List(Str)

    # If true, this editor will be used as the default editor for the type
    default = Bool(False)

    #--------------------------------------------------------------------------
    #  Editor interface:
    #--------------------------------------------------------------------------

    def _id_default(self):
        """ Trait initialiser """

        id = "%s.%s" % (type(self).__module__, type(self).__name__)
        logger.warn(
            "editor %s has no Id - using <%s>" % (self, id)
        )

        return id

# EOF -------------------------------------------------------------------------
