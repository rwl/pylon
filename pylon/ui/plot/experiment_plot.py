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
    PlotLabel, create_line_plot, create_scatter_plot

from enthought.chaco.tools.api import PanTool, SimpleZoom, DragZoom, ZoomTool

from enthought.enable.component_editor import ComponentEditor

from pybrain.rl.agents.history import HistoryAgent

from pylon.pybrain.experiment import MarketExperiment
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
    state_plot = Instance(OverlayPlotContainer,
                          desc="observations of the environment")

    # Actions performed on the environment.
    action_plot = Instance(OverlayPlotContainer,
                           desc="actions performed on the environment")

    # Rewards received for performing actions.
    reward_plot = Instance(OverlayPlotContainer,
                           desc="received rewards")

    # Data source for the index axis of all plots.
    index_data = Instance(ArrayDataSource)

    # Mapping of an agent's name to the data source for its state plot.
    state_data = Dict(Str, Instance(ArrayDataSource))

    # Mapping of an agent's name to the data source for its action plot.
    action_data = Dict(Str, Instance(ArrayDataSource))

    # Mapping of an agent's name to the data source for its reward plot.
    reward_data = Dict(Str, Instance(ArrayDataSource))

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
            bgcolor="lightgray", fill_padding=True, padding=10)

        self.state_plot  = OverlayPlotContainer(bgcolor="yellow")
        self.action_plot = OverlayPlotContainer(bgcolor="white")
        self.reward_plot = OverlayPlotContainer(bgcolor="powderblue")

#        self.plot_container.add(self.reward_plot)
        self.plot_container.add(self.action_plot)
#        self.plot_container.add(self.state_plot)

        # Use the same data source for the index axis of all plots.
        self.index_data = ArrayDataSource( array([0]) )

        self._color_cycle = cycle(color_blind + dark)

        super(ExperimentPlot, self).__init__(experiment=experiment, **traits)

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

#    @on_trait_change("experiment.step")
    def _step_changed_for_experiment(self):
        """ Returns a plot component.
        """
        print "STEP FIRED!", self.experiment.stepid
        # Index axis data.
        actions0 = self.experiment.agents[0].history.getField("action")
        rows, cols = actions0.shape
#        print "NO. SEQ:", rows
        index_array = array( range(rows) )
        self.index_data.set_data(index_array)

        for agent in self.experiment.agents:
            # State observations.
#            observations = agent.history.getField("state")
#            if agent.name in self.state_data.keys():
#                self.state_data[agent.name].set_data( observations[0] )
#            else:
#                state_ds = ArrayDataSource(observations[0])
#                self.state_data[agent.name] = state_ds
#
#                plot = self._create_plot_component(self.index_data, state_ds)
#                self.state_plot.add(plot)

            # Agent actions.
            actions = agent.history.getField("action")
#            print "PLOT ACTIONS:", actions[:, 0], index_array
            if agent.name in self.action_data.keys():
                self.action_data[agent.name].set_data(actions[:, 0])
            else:
                action_ds = ArrayDataSource(actions[:, 0])
                self.action_data[agent.name] = action_ds

                plot = self._create_plot_component(self.index_data, action_ds)
                self.action_plot.add(plot)

#            plot = self._create_plot_component( [0, 1, 2], [0, 6, 10] )
#            self.action_plot.add(plot)
            self.plot_container.request_redraw()

            # Task rewards.
#            rewards = agent.history.getField("reward")
#            if agent.name in self.reward_data.keys():
#                self.reward_data[agent.name].set_data(rewards[0])
#            else:
#                reward_ds = ArrayDataSource(rewards[0])
#                self.reward_data[agent.name] = reward_ds
#
#                plot = self._create_plot_component(self.index_data, reward_ds)
#                self.reward_plot.add(plot)


    def _create_plot_component(self, x, y):
        """ Returns a plot component.
        """
        logger.debug("Creating plot: %s %s" % (x, y))
        plot = create_line_plot((x, y),# color=self._color_cycle.next(),
                                orientation="h", add_axis=True, add_grid=True,
                                dash="solid", width=2.0)

        v_mapper = plot.value_mapper
        h_mapper = plot.index_mapper
        left_axis = PlotAxis(plot, mapper=v_mapper, orientation='left')
#        plot.underlays.append(left_axis)
#        plot.overlays.append(left_axis)

        # Plot tools.
        pan_tool  = PanTool(plot, constrain=True, constrain_direction="x")
        zoom_tool = ZoomTool(plot, drag_button="right", always_on=True,
                             tool_mode="range", axis="index")
        plot.tools.append(pan_tool)
        plot.overlays.append(zoom_tool)

        return plot

# EOF -------------------------------------------------------------------------
