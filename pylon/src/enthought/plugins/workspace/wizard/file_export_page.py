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

""" Defines a generic wizard page for file export """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import exists

from enthought.traits.api import File, Property, Str, cached_property
from enthought.traits.ui.api import View, Group, Item, Heading
from enthought.pyface.wizard.api import WizardPage

#------------------------------------------------------------------------------
#  "FileExportPage" class:
#------------------------------------------------------------------------------

class FileExportPage(WizardPage):
    """ Defines a wizard page for file selection """

    # The name of the file type
    file_type = Str

    data_file = File(
        exists=False, filter=["All Files|*.*"], auto_set=True, auto_enter=True
    )

    # A label with instructions
    _label = Property(Str, depends_on=["data_file"])

    traits_view = View(
        Group(
            Heading("File"),
            Item("_label", style="readonly", show_label=False),
            "_",
        ),
        Item("data_file")
    )

    #--------------------------------------------------------------------------
    #  "FileImportPage" interface:
    #--------------------------------------------------------------------------

    @cached_property
    def _get__label(self):
        """ Property getter """

        if self.data_file == "":
            l = "Select a %s file." % self.file_type
            self.complete = False
        else:
            l = "Click Finish to continue."
            self.complete = True

        return l

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

        ui = self.edit_traits(parent=parent, kind="subpanel")

        return ui.control

# EOF -------------------------------------------------------------------------
