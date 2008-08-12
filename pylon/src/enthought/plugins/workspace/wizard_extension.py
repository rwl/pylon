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
#  Date:   16/07/2008
#
#------------------------------------------------------------------------------

""" Defines a wizard extension to the workspace plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.traits.api import HasTraits, Instance, Str, List
from enthought.pyface.api import ImageResource

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "WizardExtension" class:
#------------------------------------------------------------------------------

class WizardExtension(HasTraits):
    """ Defines a wizard extension to the workspace plug-in """

    # The wizard contribution's globally unique identifier.
    id = Str

    # Human readable identifier
    name = Str

    # The wizards's image (displayed on selection etc)
    image = Instance(ImageResource)

    # The class of contributed wizard
    wizard_class = Str

    # A longer description of the wizard's function
    description = Str

    def _id_default(self):
        """ Trait initialiser """

        id = "%s.%s" % (type(self).__module__, type(self).__name__)
        logger.warn(
            "wizard contribution %s has no Id - using <%s>" % (self, id)
        )

        return id

# EOF -------------------------------------------------------------------------
