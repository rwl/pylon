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

""" Defines a plot of the cost curves for all generators in a network.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Int, TraitListEvent, on_trait_change

from enthought.chaco.tools.api import LineInspector

from pylon.api import Network, Generator

from base_plot import BasePlot

from numpy import array

#------------------------------------------------------------------------------
#  "CostPlot" class:
#------------------------------------------------------------------------------

class CostPlot(BasePlot):
    """ Defines a plot of the cost curves for all generators in a network.
    """

    # Power system model with costly generators.
    network = Instance(Network)

    # Number of points to use plotting costs.
    points = Int(10)

    def _plot_default(self):
        """ Trait initialiser.
        """
        plot = super(CostPlot, self)._plot_default()
        plot.tools.append(LineInspector(plot))
        return plot

    def _replot_fired(self):
        """ Re-plots the plot data.
        """
        self.on_generator(self.network, "", [], self.network)


    @on_trait_change("network.all_generators,network.all_generators_items")
    def on_generator(self, obj, name, old, new):
        """ Handles addition and removal of generators.
        """
        # Use the same method for the list being set and for items being
        # added and removed from the list.  When individual items are changed
        # the last argument is an event with '.added' and '.removed' traits.
        if isinstance(new, TraitListEvent):
            old = new.removed
            new = new.added
        else:
            new = new.all_generators

        index_array = array( range(self.points) )
        self.plot.data.set_data("x", index_array)

        for generator in new:
            c0, c1, c2 = generator.cost_coeffs
            points = self.points
            values = [ c0 + c1*x + c2*x**2 for x in xrange(points) ]
            self.plot.data.set_data( str(id(generator)), array(values) )

            if str(id(generator)) not in self.plot.plots.keys():

                self.plot.plot(("x", str(id(generator))),
                    name=str(id(generator)),
                    color="auto", type="line", marker_size=6, marker="square",
                    line_width=2, tick_interval=1.0, padding=0)

                self.plot.x_axis = None


#    @on_trait_change("network.all_generators.cost_coeffs")
    def on_cost(self, obj, name, old, new):
        """ Handles changes in costs.
        """
        generator = obj
        assert isinstance(obj, Generator)

        c0, c1, c2 = new
        points = self.points
        values = [ c0 + c1*x + c2*x**2 for x in xrange(points) ]
        self.plot.data.set_data( str(id(generator)), array(values) )

# EOF -------------------------------------------------------------------------
