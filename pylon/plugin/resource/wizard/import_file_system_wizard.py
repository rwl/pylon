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

""" Defines a wizard for importing resources from the file system to
an existing project.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import exists, join

from enthought.traits.api import \
    Str, Directory, Property, Bool, cached_property

from enthought.traits.ui.api import View, Group, Item, Heading

from enthought.pyface.wizard.api import SimpleWizard, WizardPage

from pylon.plugin.resource.resource_dialog import \
    FolderSelectionWizardPage

#------------------------------------------------------------------------------
#  "ImportFileSystemWizardPage" class:
#------------------------------------------------------------------------------

class ImportFileSystemWizardPage(WizardPage):
    """ Wizard page for selection of files for import """

    #--------------------------------------------------------------------------
    #  ImportFileSystemWizardPage interface:
    #--------------------------------------------------------------------------

    # The file system directory from which to import
    from_directory = Directory(auto_set=True)

    # A label with instructions
    _label = Property(Str, depends_on=["from_directory"])

    # The default view:
    traits_view = View(
        Group(Heading("File system")),
        Group(
            Item(name="_label", style="readonly", show_label=False),
            "_",
        ),
        Item(name="from_directory")
    )

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

        ui = self.edit_traits(parent=parent, kind='subpanel')

        return ui.control

    #--------------------------------------------------------------------------
    #  Private interface.
    #--------------------------------------------------------------------------

    @cached_property
    def _get__label(self):
        """ Property getter """

        l = "Import resources from the local file system into "
        "an existing project."

        self.complete = True

        return l

#------------------------------------------------------------------------------
#  "ProjectWizard" class:
#------------------------------------------------------------------------------

class ImportFileSystemWizard(SimpleWizard):
    """ A wizard for importing resources from the file system
    to an existing project.

    """

    # The dialog title
    title = "Import"

    def __init__(self, workspace, **traits):
        """ Returns a ProjectWizard """

        self.pages = [
            FolderSelectionWizardPage(
                id="folder_selection", workspace=workspace
            ),
            ImportFileSystemWizardPage(id="file_system", from_directory="/tmp")
        ]

        super(ImportFileSystemWizard, self).__init__(**traits)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":

    from enthought.pyface.api import GUI

    # Create the GUI.
    gui = GUI()

    wizard = ImportFileSystemWizard(parent=None, workspace="/tmp")

    # Open the wizard
    wizard.open()

    # Start the GUI event loop!
    gui.start_event_loop()

# EOF -------------------------------------------------------------------------
