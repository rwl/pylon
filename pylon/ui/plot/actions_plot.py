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

""" Plot of Pyreto actions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path
from random import randint
from numpy import array, arange, append

from enthought.traits.api import \
    HasTraits, Instance, Button, Any, on_trait_change

from enthought.traits.ui.api import View, Group, Item, Label
from enthought.traits.ui.menu import OKCancelButtons, NoButtons

from enthought.chaco.api import \
    ArrayDataSource, BarPlot, DataRange1D, LabelAxis, LinearMapper, Plot, \
    OverlayPlotContainer, PlotAxis, PlotGrid, VPlotContainer, HPlotContainer, \
    AbstractPlotData, ArrayPlotData

from enthought.chaco.tools.api import PanTool, SimpleZoom, DragZoom

from enthought.enable.component_editor import ComponentEditor

from pylon.ui.plot.colours import dark, light

#------------------------------------------------------------------------------
#  "ActionsPlot" class:
#------------------------------------------------------------------------------

class ActionsPlot(HasTraits):
    """ Plot of Pyreto actions """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The reward producing environment
    environment = Instance("pyqle.environment.environment.Environment")

    # A plot of the values of all actions performed
    plot = Instance(Plot)
    data = Instance(AbstractPlotData, ArrayPlotData(x=[0]))

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item(name="plot", editor=ComponentEditor(), show_label=False),
        id="pylon.ui.plot.actions_plot",
        resizable=True, style="custom", width=.3
    )

    #--------------------------------------------------------------------------
    #  "ActionsPlot" interface:
    #--------------------------------------------------------------------------

    def _plot_default(self):
        """ Trait initialiser """

        plot = Plot(
            self.data, title="Actions",
            bgcolor="ivory",
            padding_bg_color="aliceblue"
        )

        # Plot tools
        plot.tools.append(PanTool(plot))
#        plot.overlays.append(SimpleZoom(plot))
        # The DragZoom tool just zooms in and out as the user drags
        # the mouse vertically.
        plot.tools.append(DragZoom(plot, drag_button="right"))

        # Plot axes
        index_axis = PlotAxis(
            orientation="bottom", title="Periods",
            mapper=plot.index_mapper, component=plot
        )
        value_axis = PlotAxis(
            orientation="left", title="Value",
            mapper=plot.value_mapper, component=plot
        )
        plot.underlays.append(index_axis)
        plot.underlays.append(value_axis)

        # Plot attributes
        plot.origin_axis_visible = True
#        plot.legend.visible = True

        return plot

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def update_action_plot(self, composed_action):
        """ Maintains the action plot data """

        plot = self.plot
        plot_data = self.data

        # Increment the index values
        size = len(plot_data.get_data("x"))
        plot_data.set_data("x", range(size+1))

        for action in composed_action:
            # Update plots or add new plots for new agents
            plot_name = action.asset.id
            if plot_name in plot_data.list_data():
                past_data = plot_data.get_data(plot_name)
                plot_data.set_data(plot_name, append(past_data, action.value))
            else:
                plot_data.set_data(plot_name, [action.value])

                colour = dark[randint(0, len(dark)-1)]
#                colour = self._get_colour(action.asset.id)

                plot.plot(
                    ("x", plot_name), color=colour, type="line", line_width=4,
                    marker_size=6, marker="circle", outline_color=colour
                )


    def _get_colour(self, id):
        """ Returns a colour from an id """

        idx = int(id[-3:]) % len(dark)-1

        return dark[idx]

# EOF -------------------------------------------------------------------------
