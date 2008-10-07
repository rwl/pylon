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

""" Python editor wizard extensions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.api import ImageResource

from enthought.plugins.workspace.wizard_extension import WizardExtension

#------------------------------------------------------------------------------
#  "NewFileWizardExtension" class:
#------------------------------------------------------------------------------

class NewFileWizardExtension(WizardExtension):
    """ Contributes a new file wizard """

    # The wizard contribution's globally unique identifier.
    id = "enthought.plugins.python_editor.new_file_wizard"

    # Human readable identifier
    name = "File"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("document")

    # The class of contributed wizard
    wizard_class = "enthought.plugins.python_editor.new_file_wizard:" \
    "NewFileWizard"

    # A longer description of the wizard's function
    description = "Create a new file resource"

# EOF -------------------------------------------------------------------------
