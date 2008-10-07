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

""" Plot of Pylon bus data """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from numpy import array, arange

from enthought.traits.api import \
    HasTraits, Instance, Button, Any, on_trait_change

from enthought.traits.ui.api import View, Group, Item, Label
from enthought.traits.ui.menu import OKCancelButtons, NoButtons

from enthought.chaco.api import \
    ArrayDataSource, BarPlot, DataRange1D, LabelAxis, LinearMapper, Plot, \
    OverlayPlotContainer, PlotAxis, PlotGrid, VPlotContainer, HPlotContainer, \
    AbstractPlotData, ArrayPlotData

from enthought.chaco.tools.api import PanTool, SimpleZoom

from enthought.enable.component_editor import ComponentEditor

from pylon.api import Network
from pylon.ui.plot.colours import colours

#------------------------------------------------------------------------------
#  "BusPlot" class:
#------------------------------------------------------------------------------

class BusPlot(HasTraits):
    """ Defines a plot of bus data """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Network container object:
    network = Instance(Network)

    # Plot data
    data = Instance(AbstractPlotData)

    # Bus voltage plot:
    plot = Instance(Plot)

    # A plot container for overlaying all bus plots
    container = Instance(OverlayPlotContainer)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item(name="network"),
#        Item(
#            name="container", show_label=False,
#            editor=PlotContainerEditor()
#        ),
        Item(name="plot", editor=ComponentEditor()),
        title="Bus Plot", id="pylon.ui.plot.bus_plot",
        resizable=True, buttons=NoButtons,
        width=.6, height=.4,
    )

    #--------------------------------------------------------------------------
    #  Initialise the object:
    #--------------------------------------------------------------------------

#    def _network_changed(self, old, new):
#        """ Adds and removes static handlers """
#
#        if old is not None:
#            old.on_trait_change(self.plot_power, "buses_items", remove=True)
#        if new is not None:
#            old.on_trait_change(self.plot_power, "buses_items")

    #--------------------------------------------------------------------------
    #  Default plot:
    #--------------------------------------------------------------------------

    def _data_default(self):
        """ Trait initialiser """

        if self.network is not None:
            x = self.network.n_buses
            v = [bus.v_amplitude for bus in self.network.buses]
        else:
            x = v = [0]

        return ArrayPlotData(x=x, voltage=v)


    def _plot_default(self):
        """ Trait initialiser """

        plot = Plot(self.data)
        plot.plot(
            ("x", "voltage"), name="voltage plot",
            color="red", type="scatter"
        )
        plot.tools.append(PanTool(plot))
        plot.overlays.append(SimpleZoom(plot))

        return plot

    #--------------------------------------------------------------------------
    #  Default Chaco plot container:
    #--------------------------------------------------------------------------

    def _container_default(self):
        """ Trait initialiser """

        container = OverlayPlotContainer(
            use_draw_order=False, bgcolor="white"
        )
        container.add(self.plot)

        return container

    #--------------------------------------------------------------------------
    #  Plot the graph:
    #--------------------------------------------------------------------------

    @on_trait_change("network.buses.v_amplitude")
    def _refresh_voltage_data(self):
        """ Refreshes the plotted voltage data """

        indexes = range(self.network.n_buses)
        print self.data.list_data()
#        self.plot.datasources["x"].set_data(indexes)
        self.data.set_data("x", indexes)

        v = [bus.v_amplitude for bus in self.network.buses]
#        self.plot.datasources["voltage"].set_data(v)
        self.data.set_data("voltage", v)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.filter.api import import_matpower

    data_file = "/home/rwl/python/aes/matpower_3.2/rwl_003.m"
    #data_file = "/home/rwl/python/aes/model/matpower/case30.m"
    n = import_matpower(data_file)

    plot = BusPlot(network=n)
    plot.configure_traits()

# EOF -------------------------------------------------------------------------
