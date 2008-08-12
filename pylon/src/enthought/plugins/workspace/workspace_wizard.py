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

""" Workspace wizard extensions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.api import ImageResource

from enthought.plugins.workspace.wizard_extension import WizardExtension

#------------------------------------------------------------------------------
#  "FolderWizard" class:
#------------------------------------------------------------------------------

class FolderWizardExtension(WizardExtension):
    """ Contributes a new folder wizard """

    # The wizard contribution's globally unique identifier.
    id = "enthought.plugins.workspace.folder_wizard"

    # Human readable identifier
    name = "Folder"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("new")

    # The class of contributed wizard
    wizard_class = "enthought.plugins.workspace.wizard.folder_wizard:" \
    "FolderWizard"

    # A longer description of the wizard's function
    description = "Create a new folder resource"

#------------------------------------------------------------------------------
#  "ImportFileSystemWizard" class:
#------------------------------------------------------------------------------

class ImportFileSystemWizardExtension(WizardExtension):
    """ Contributes a wizard for importing resources from the file system
    to existing projects.

    """

    # The wizard contribution's globally unique identifier.
    id = "enthought.plugins.workspace.file_system_import_wizard"

    # Human readable identifier
    name = "File System"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("closed_folder")

    # The class of contributed wizard
    wizard_class = "enthought.plugins.workspace.wizard." \
    "import_file_system_wizard:ImportFileSystemWizard"

    # A longer description of the wizard's function
    description = "Import resources from the file system to existing projects."

# EOF -------------------------------------------------------------------------
