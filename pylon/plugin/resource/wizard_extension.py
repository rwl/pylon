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
    """ Defines a wizard extension to the resource plug-in """

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
