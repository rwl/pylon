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

""" Bar plot of bus data (No pun intended) """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, Any, on_trait_change, DelegatesTo, List

from enthought.traits.ui.api import View, Group, Item, Label, SetEditor
from enthought.traits.ui.menu import OKCancelButtons, NoButtons
from enthought.chaco.tools.api import PanTool, SimpleZoom
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.tools.api import PanTool, SimpleZoom, DragZoom

from enthought.chaco.api import \
    ArrayDataSource, BarPlot, DataRange1D, LabelAxis, LinearMapper, Plot, \
    OverlayPlotContainer, PlotAxis, PlotGrid, VPlotContainer, HPlotContainer

from pylon.api import Network, Bus
from pylon.ui.plot.colours import colours

#------------------------------------------------------------------------------
#  "BusBarPlot" class:
#------------------------------------------------------------------------------

class BusBarPlot(HasTraits):
    """ Defines a bar plot of bus data """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The network containing the buses:
    network = Instance(Network)

    # All buses in the network
    all_buses = DelegatesTo("network", "buses")

    # A potentially filtered list of buses to plot
    buses = List(Instance(Bus))

    # Bus data plot:
    plot = Instance(BarPlot)

    # An axis with bus name labels
    label_axis = Instance(LabelAxis)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item(name="plot", editor=ComponentEditor(), show_label=False),
#        Item(name="network", show_label=False),
#        Item(
#            name="buses", editor=SetEditor(
#                name="all_buses",
#                left_column_title="Buses",
#                right_column_title="Plotted Buses"
#            )
#        ),
        title="Bus Bar Plot", id="pylon.ui.plot.bus_bar_plot",
        resizable=True, buttons=NoButtons,
        width=.6, height=.4,
    )

    #--------------------------------------------------------------------------
    #  Default plot:
    #--------------------------------------------------------------------------

    def _buses_default(self):
        """ Trait initialiser """

        return self.network.buses


    def _plot_default(self):
        """ Trait initialiser """

        idx_points, val_points = self._get_points()

        idx = ArrayDataSource(idx_points)
        val = ArrayDataSource(val_points)

        # Create the index range
        idx_range = DataRange1D(idx, low=0.5, high=len(idx_points)+.5)
        idx_mapper = LinearMapper(range=idx_range)

        # Create the value range
        val_range = DataRange1D(
            low=min(val_points)-.1,
            high=max(val_points)+.1
        )
        val_mapper = LinearMapper(range=val_range)

        # Create the plot
        plot = BarPlot(
            index=idx, value=val,
            value_mapper=val_mapper, index_mapper=idx_mapper,
            line_color="black", fill_color="red", bgcolor="white",
            bar_width=0.8, padding=75, antialias=False
        )

        # Create the plot axes
        left_axis = PlotAxis(plot, orientation="left", title="Value")
        self.label_axis = label_axis = LabelAxis(
            plot, orientation='bottom', title="Buses",
            positions=range(1, len(idx_points)+1),
            labels=[v.name for v in self.network.buses],
            label_rotation=90, small_haxis_style=True
        )
        plot.underlays.append(left_axis)
        plot.underlays.append(label_axis)

        # Add some ploy tools
        plot.tools.append(PanTool(plot))
        # The DragZoom tool just zooms in and out as the user drags
        # the mouse vertically.
        plot.tools.append(DragZoom(plot, drag_button="right"))

        return plot


    @on_trait_change("network,network.buses.v_phase")
    def _refresh_points(self):
        """ Refreshes the plot data points """

        idx_points, val_points = self._get_points()

        self.plot.index.set_data(idx_points)
        self.plot.value.set_data(val_points)

#        axis = self.label_axis
#        axis.positions=range(1, len(idx_points)+1),
#        axis.labels=[v.name for v in self.network.buses]


    def _get_points(self):
        """ Get the plot data points """

        buses = self.network.buses
        n_buses = self.network.n_buses
#        buses = self.buses
#        n_buses = len(buses)

        if buses:
            idx_points = range(1, n_buses+1)
            val_points = [bus.v_phase for bus in buses]
        else:
            idx_points = [1]
            val_points = [0]

        return (idx_points, val_points)


    def _all_buses_items_changed(self, event):
        """ Handle addition and removal of buses """

        buses = self.buses

        for v in event.added:
            buses.append(v)
        for v in event.removed:
            if v in buses:
                buses.remove(v)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.filter.api import import_matpower

    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
#    data_file = "/home/rwl/python/aes/model/matpower/case30.m"
    n = import_matpower(data_file)

    plot = BusBarPlot(network=n)
    plot.configure_traits()

# EOF -------------------------------------------------------------------------
