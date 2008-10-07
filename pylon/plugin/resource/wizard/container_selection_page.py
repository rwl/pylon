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

""" Defines a wizard page for container selection """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join, exists

from enthought.io.api import File

from enthought.traits.api import \
    HasTraits, Directory, Bool, Str, Property, Instance, cached_property

from enthought.traits.ui.api import View, Item, Group, Heading, Label

from enthought.pyface.wizard.api import SimpleWizard, WizardPage

#from enthought.plugins.workspace.workspace_resource import Workspace

#------------------------------------------------------------------------------
#  "ContainerSelectionPage" class:
#------------------------------------------------------------------------------

class ContainerSelectionPage(WizardPage):
    """ Wizard page for container selection """

    #--------------------------------------------------------------------------
    #  "ContainerSelectionPage" interface:
    #--------------------------------------------------------------------------

    # The workspace from which the folder may be selected
    workspace = Instance(File)

    # The containing directory
    directory = Directory(exists=True)

    # The default view
    traits_view = View(
        Heading("Container"),
        Label("Enter or select the parent directory"),
#        Item(name="directory", style="text", show_label=False),
        Item(name="directory", style="simple", show_label=False)
    )

    #--------------------------------------------------------------------------
    #  "ContainerSelectionPage" interface:
    #--------------------------------------------------------------------------

    def _directory_default(self):
        """ Trait initialiser """

        # FIXME: Under Windows if a 'custom' directory editor is used in the
        # view then this initialiser is called after the page has been
        # destroyed and any call to self raises an error.
        if self.workspace is not None:
            self.complete = True
            return self.workspace.absolute_path
        else:
            self.complete = True
            return expanduser("~")


    def _directory_changed(self, new):
        """ Complete the wizard when a container is selected """

        if new != "":
            self.complete = True
        else:
            self.complete = False

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

        ui = self.edit_traits(parent=parent, kind="subpanel")

        return ui.control

# EOF -------------------------------------------------------------------------
