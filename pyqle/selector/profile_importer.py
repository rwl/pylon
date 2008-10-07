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

""" Defines a class for importing profiles from CSV files """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, List, Range, String, Float, File, Array, Property

from enthought.traits.ui.api import View, Item, Group, Tabbed, HGroup

from enthought.traits.ui.menu import OKCancelButtons

from enthought.chaco.chaco_plot_editor import ChacoPlotItem

#------------------------------------------------------------------------------
#  "ProfileImporter" class:
#------------------------------------------------------------------------------

class ProfileImporter(HasTraits):
    """ Defines a class for importing profiles from CSV files """

    #--------------------------------------------------------------------------
    #  Traits definitions:
    #--------------------------------------------------------------------------

    # The file from which to import comma separated values
    csv_file = File(filter=["CSV Files (*.csv)|*.csv", "All Files (*.*)|*.*"])

    # The values imported from the csv_file
    values = List(Float)

    # Value to which a profile value of 0.0 relates
    low_value = Float(
        0.0, desc="the value to which a profile value of 0.0 relates"
    )

    # Value to which a profile value of 1.0 relates
    high_value = Float(
        1.0, desc="the value to which a profile value of 1.0 relates"
    )

    # The resulting profile
    profile = List(Range(low=0.0, high=1.0))

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item(name="csv_file", label="File"),
        HGroup(
            Item(name="low_value"),
            Item(name="high_value")
        ),
        Group(
            ChacoPlotItem(
                "_index", "_profile",
                type="line",
                # Basic axis and label properties
                show_label=False, resizable=True, orientation="h",
                title="Imported Profile",
                # Axis properties
                y_auto=False, y_bounds=(0.0, 1.0),
                x_label="Period", y_label="Coefficient",
                # Plot properties
                color="red", bgcolor="ivory",
                # Border properties
                border_color="darkblue", #border_width=2,
                # Specific to scatter plot
                marker="circle", marker_size=2, outline_color="none",
                # Border, padding properties
                border_visible=True, border_width=1,
                padding_bg_color="powderblue"
            ),
            label="Profile", show_border=True
        ),
        title="Profile Importer",
        id="pylon.pyreto.profile_importer_view",
        resizable=True, #buttons=OKCancelButtons
    )

    #--------------------------------------------------------------------------
    #  Private traits:
    #--------------------------------------------------------------------------

    # Profile plot index values
    _index = Property(Array, depends_on=["profile", "profile_items"])

    # Profile values
    _profile = Property(Array, depends_on=["profile", "profile_items"])

    #--------------------------------------------------------------------------
    #  "ProfileImporter" interface:
    #--------------------------------------------------------------------------

    def _csv_file_changed(self, new):
        """ Handles the import file changing """

        fd = None
        try:
            fd = open(new, "rb")
            csv = fd.read().strip("\n")
            self.values = [float(v) for v in csv.split(",")]
        finally:
            if fd is not None:
                fd.close()


    def _values_changed(self, new):
        """ Handles the imported values changing """

        low = self.low_value
        high = self.high_value

        if high-low == 0.0:
            profile = [value-low for value in new]
        else:
            profile = [(value-low)/(high-low) for value in new]

        if (max(profile) <= 1.0) and (min(profile) >= 0.0):
            self.profile = profile
        else:
            pass

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

    def _get__index(self):
        """ Property getter """

        if self.profile:
            return [i for i in range(len(self.profile)+1)]
        else:
            return [0]


    def _get__profile(self):
        """ Property getter """

        if self.profile:
            return self.profile[:]
        else:
            return [0]

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    pi = ProfileImporter()
    pi.configure_traits()

# EOF -------------------------------------------------------------------------
