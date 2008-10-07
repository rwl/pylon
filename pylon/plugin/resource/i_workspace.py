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

""" Defines the workspace interface """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Interface

#------------------------------------------------------------------------------
#  "IWorkspace" interface class:
#------------------------------------------------------------------------------

class IWorkspace(Interface):
    """ Defines the workspace interface """

    def get_project(self, name):
        """ Returns a project resource """

    def add_project(self, project):
        """ Adds a project resource to the workspace """

# EOF -------------------------------------------------------------------------
