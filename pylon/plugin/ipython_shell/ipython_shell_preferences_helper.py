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

"""
Preference helpers for the IPython shell preferences

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Bool

from enthought.preferences.api import PreferencesHelper

#------------------------------------------------------------------------------
#  "IPythonShellPreferencesHelper" class:
#------------------------------------------------------------------------------

class IPythonShellPreferencesHelper(PreferencesHelper):

    # The preferences path for which we use.
    preferences_path = "enthought.plugins.ipython_shell"

    #--------------------------------------------------------------------------
    #  Preferences:
    #--------------------------------------------------------------------------

    # Show the IPython banner with version numbers etc by default:
    ipython_banner = Bool(True, desc="Show the IPython banner on startup")

# EOF -------------------------------------------------------------------------
