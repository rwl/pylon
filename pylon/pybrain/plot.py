#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Defines the Pyreto plots.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, Button, Any, on_trait_change

from enthought.traits.ui.api import View, Group, Item, Label
from enthought.traits.ui.menu import OKCancelButtons, NoButtons

from enthought.chaco.api import \
    ArrayDataSource, BarPlot, DataRange1D, LabelAxis, LinearMapper, Plot, \
    OverlayPlotContainer, PlotAxis, PlotGrid, VPlotContainer, HPlotContainer, \
    AbstractPlotData, ArrayPlotData, FilledLinePlot, add_default_grids, \
    PlotLabel

from enthought.chaco.tools.api import PanTool, SimpleZoom, DragZoom, ZoomTool

from pybrain.rl.agents.history import HistoryAgent

#------------------------------------------------------------------------------
#  "BasePlot" class:
#------------------------------------------------------------------------------

class BasePlot(HasTraits):
    """ Defines a base class for plots.
    """

    # Plot of values.
    plot = Instance(Plot, desc="plot component")

    data = Instance(AbstractPlotData, ArrayPlotData(x=[0]))

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(Item("plot", editor=ComponentEditor(), style="custom",
        show_label=False), id="pylon.plot.base_plot", resizable=True)

    #--------------------------------------------------------------------------
    #  "BasePlot" interface:
    #--------------------------------------------------------------------------

    def _plot_default(self):
        """ Trait initialiser.
        """
        index = []
        reward = []

        time_ds = ArrayDataSource(index)
        reward_ds = ArrayDataSource(reward, sort_order="none")

        xmapper = LinearMapper(range=DataRange1D(time_ds))
        reward_mapper = LinearMapper(range=DataRange1D(reward_ds))

        reward_plot = FilledLinePlot(index = time_ds, value = reward_ds,
                                    index_mapper = xmapper,
                                    value_mapper = reward_mapper,
                                    edge_color = "blue",
                                    face_color = "paleturquoise",
                                    bgcolor = "white",
                                    border_visible = True)

        add_default_grids(price_plot)
        reward_plot.overlays.append(PlotAxis(reward_plot,
                                             mapper=reward_mapper,
                                             orientation='left'))
        reward_plot.overlays.append(PlotAxis(reward_plot,
                                             mapper=xmapper,
                                             orientation='bottom'))

        # Plot tools.
        reward_plot.tools.append(PanTool(reward_plot, constrain=True,
                                         constrain_direction="x"))
        reward_plot.overlays.append(ZoomTool(reward_plot, drag_button="right",
                                             always_on=True, tool_mode="range",
                                             axis="index"))

        plot.origin_axis_visible = True

        return plot

#------------------------------------------------------------------------------
#  "RewardPlot" class:
#------------------------------------------------------------------------------

class RewardPlot(HasTraits):
    """ Defines a plot of an agents rewards.
    """

    agent = Instance(HistoryAgent)

    #--------------------------------------------------------------------------
    #  "BasePlot" interface:
    #--------------------------------------------------------------------------

    def _plot_default(self):
        """ Trait initialiser.
        """


#    @on_trait_change("agent.reward")
    def _reward_changed_for_agent(self, rewards):
        """ Maintains the reward plot data.
        """
        plot = self.plot
        plot_data = self.data

        # Increment the index values
        size = len(plot_data.get_data("x"))
        plot_data.set_data("x", range(size+1))

        for i, reward in enumerate(rewards):
            # Update plots or add new plots for new agents
            plot_name = str(i)
            if plot_name in plot_data.list_data():
                past_data = plot_data.get_data(plot_name)
                plot_data.set_data(plot_name, append(past_data, reward))
            else:
                plot_data.set_data(plot_name, [reward])

                colour = dark[randint(0, len(dark)-1)]
#                colour = self._get_colour(action.asset.id)

                plot.plot(
                    ("x", plot_name), color=colour, type="line",
                    marker_size=6, market="square", line_width=4
                )

# EOF -------------------------------------------------------------------------
