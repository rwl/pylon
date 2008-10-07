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

""" Resource wizard extensions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.api import ImageResource

from wizard_extension import WizardExtension

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
    wizard_class = "pylon.plugin.resource.wizard.folder_wizard:" \
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
    id = "pylon.plugin.resource.file_system_import_wizard"

    # Human readable identifier
    name = "File System"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("closed_folder")

    # The class of contributed wizard
    wizard_class = "pylon.plugin.resource.wizard." \
    "import_file_system_wizard:ImportFileSystemWizard"

    # A longer description of the wizard's function
    description = "Import resources from the file system to existing projects."

# EOF -------------------------------------------------------------------------
