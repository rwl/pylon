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

""" Defines a generic wizard page for file import """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import exists

from enthought.traits.api import File, Property, Str, cached_property
from enthought.traits.ui.api import View, Group, Item, Heading
from enthought.pyface.wizard.api import WizardPage

#------------------------------------------------------------------------------
#  "FileImportPage" class:
#------------------------------------------------------------------------------

class FileImportPage(WizardPage):
    """ Defines a wizard page for file selection """

    # The name of the file type
    file_type = Str

    data_file = File(
        exists=True, filter=["All Files|*.*"]
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

        if not exists(self.data_file):
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
