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

""" Defines plots for a Pyreto experiment.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from itertools import cycle
from numpy import array

from enthought.traits.api import \
    HasTraits, Instance, Button, Any, Dict, Str, Trait, on_trait_change

from enthought.traits.ui.api import View, Group, Item, Label
from enthought.traits.ui.menu import OKCancelButtons, NoButtons

from enthought.chaco.api import \
    ArrayDataSource, BarPlot, DataRange1D, LabelAxis, LinearMapper, Plot, \
    OverlayPlotContainer, PlotAxis, PlotGrid, VPlotContainer, HPlotContainer, \
    AbstractPlotData, ArrayPlotData, FilledLinePlot, add_default_grids, \
    PlotLabel, create_line_plot, create_scatter_plot, add_default_axes

from enthought.chaco.tools.api import PanTool, SimpleZoom, DragZoom, ZoomTool

from enthought.enable.component_editor import ComponentEditor

from pybrain.rl.agents.history import HistoryAgent

from pylon.pyreto.experiment import MarketExperiment
from colours import dark, color_blind

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "ExperimentPlot" class:
#------------------------------------------------------------------------------

class ExperimentPlot(HasTraits):
    """ Defines plots of state, action and reward for a MarketExperiment.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Experiment containing the agents with the data to be plotted.
    experiment = Instance(HasTraits, allow_none=False)

    # Vertical container for state, action and reward plots.
    plot_container = Instance(VPlotContainer)

    # Plot of environment observations.
    state_plot = Instance(Plot, desc="observations of the environment")

    # Actions performed on the environment.
    action_plot = Instance(Plot, desc="actions performed on the environment")

    # Rewards received for performing actions.
    reward_plot = Instance(Plot, desc="received rewards")

#    # Data source that drives the state plot.
#    state_plot_data = Instance(ArrayPlotData)
#
#    # Data source that drives the action plot.
#    action_plot_data = Instance(ArrayPlotData)
#
#    # Data source that drives the reward plot.
#    reward_plot_data = Instance(ArrayPlotData)

    # Iterator that cycles through a list of colours.
    _color_cycle = Trait(cycle)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(Item("plot_container", editor=ComponentEditor(),
                            style="custom", show_label=False),
                       Item("experiment", show_label=False, style="custom",
                            width=200),
                       id="pylon.ui.plot.experiment_plot", resizable=True)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, experiment, **traits):
        """ Initialises the ExperimentPlot.
        """
        self.experiment = experiment

        self.plot_container = VPlotContainer(resizable="hv",
            bgcolor="transparent")#, fill_padding=True, padding=10)

        self.state_plot = Plot(ArrayPlotData(), bgcolor="white",
                                padding_top=0, padding_right=0,
                                padding_bottom=4, border_visible=False)

        self.action_plot = Plot(ArrayPlotData(), bgcolor="white",
                                padding_top=2, padding_right=0,
                                padding_bottom=2, border_visible=False)

        self.reward_plot = Plot(ArrayPlotData(), bgcolor="white",
                                padding_top=4, padding_right=0,
                                padding_bottom=0, border_visible=False)

        for plot in [self.state_plot, self.action_plot, self.reward_plot]:
            plot.tools.append(PanTool(plot, constrain=True,
                                      constrain_direction="x"))

            plot.overlays.append(ZoomTool(plot, drag_button="right",
                                          always_on=True, tool_mode="range",
                                          axis="index"))

        self.plot_container.add(self.reward_plot)
        self.plot_container.add(self.action_plot)
        self.plot_container.add(self.state_plot)

#        self.reward_plot.index_mapper.range = \
#            self.action_plot.index_mapper.range

        self.state_plot.index_mapper.range = \
        self.action_plot.index_mapper.range = \
        self.reward_plot.index_mapper.range

        # Use the same data source for the index axis of all plots.
#        self.index_data = ArrayDataSource( array([0]) )

        self._color_cycle = cycle(color_blind + dark)

        super(ExperimentPlot, self).__init__(experiment=experiment, **traits)

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

#    @on_trait_change("experiment.step")
    def _step_changed_for_experiment(self):
        """ Returns a plot component.
        """
        print "STEP: ", self.experiment.stepid

        # Index axis data.
        actions0 = self.experiment.agents[0].history.getField("action")
        rows, cols = actions0.shape
#        print "NO. SEQ:", rows
        index_array = array( range(rows) )
        self.state_plot.data.set_data("x", index_array)
        self.action_plot.data.set_data("x", index_array)
        self.reward_plot.data.set_data("x", index_array)

        for agent in self.experiment.agents:
            # State observations.
            observations = agent.history.getField("state")
            self.state_plot.data.set_data(agent.name, observations[:, 0])

            if agent.name not in self.state_plot.plots.keys():
                self.state_plot.plot(("x", agent.name), name=agent.name,
                    color="auto", type="line", marker_size=6,
                    marker="square", line_width=2, tick_interval=1.0,
                    padding=0)
                self.state_plot.x_axis = None

            # Agent actions.
            actions = agent.history.getField("action")
            self.action_plot.data.set_data(agent.name, actions[:, 0])

#            if agent.name not in plot_data.list_data():
            if agent.name not in self.action_plot.plots.keys():
                self.action_plot.plot(("x", agent.name), name=agent.name,
                    color="auto", type="line", marker_size=6,
                    marker="square", line_width=2, tick_interval=1.0,
                    padding=0)
                self.action_plot.x_axis = None

            # Task rewards.
            rewards = agent.history.getField("reward")
            self.reward_plot.data.set_data(agent.name, rewards[:, 0])

            if agent.name not in self.reward_plot.plots.keys():
                self.reward_plot.plot(("x", agent.name), name=agent.name,
                    color="auto", type="line", marker_size=6,
                    marker="square", line_width=2, tick_interval=1.0,
                    padding=0)

        self.plot_container.request_redraw()


#    def _create_plot_component(self, x, y):
#        """ Returns a plot component.
#        """
#        logger.debug("Creating plot: %s %s" % (x, y))
#        plot = create_line_plot((x, y), color=self._color_cycle.next(),
#                                orientation="h",
#                                add_axis=False, add_grid=False,
#                                dash="solid", width=2.0)
#
#        plot.padding = 50
#
#        if len(self.action_data) == 1:
#            # Plot tools.
#            pan_tool  = PanTool(plot, constrain=True, constrain_direction="x")
#            zoom_tool = ZoomTool(plot, drag_button="right", always_on=True,
#                                 tool_mode="range", axis="index")
#            plot.tools.append(pan_tool)
#            plot.overlays.append(zoom_tool)
#
#            add_default_grids(plot)
#            add_default_axes(plot)
#
#            v_mapper = plot.value_mapper
#            h_mapper = plot.index_mapper
#            left_axis = PlotAxis(plot, mapper=v_mapper, orientation='left')
#    #        plot.underlays.append(left_axis)
#    #        plot.overlays.append(left_axis)
#
#        return plot

# EOF -------------------------------------------------------------------------
