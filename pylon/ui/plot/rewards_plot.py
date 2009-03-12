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

""" Plot of Pyreto rewards.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join
from random import randint
from numpy import array, arange, append

from enthought.traits.api import \
    HasTraits, Instance, Button, Any, File, Button, Enum, Str, on_trait_change

from enthought.traits.ui.api \
    import View, Group, Item, Label, HGroup, VGroup, spring

from enthought.traits.ui.menu import OKCancelButtons, NoButtons

from enthought.chaco.api import \
    ArrayDataSource, BarPlot, DataRange1D, LabelAxis, LinearMapper, Plot, \
    OverlayPlotContainer, PlotAxis, PlotGrid, VPlotContainer, HPlotContainer, \
    AbstractPlotData, ArrayPlotData, add_default_grids, PlotGraphicsContext

from enthought.chaco.tools.api import PanTool, SimpleZoom, DragZoom, ZoomTool

from enthought.enable.component_editor import ComponentEditor

from pylon.ui.plot.colours import dark, light, color_blind

#------------------------------------------------------------------------------
#  "RewardsPlot" class:
#------------------------------------------------------------------------------

class RewardsPlot(HasTraits):
    """ Plot of Pyreto rewards.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Title for the plot.
    title = Str

    # Label for the index axis.
    index_label = Str("Index")

    # Label for the y-axis.
    value_label = Str("Value")

    # A plot of all rewards received.
    plot = Instance(Plot)

    # Index and reward data.
    data = Instance(AbstractPlotData)

    # Save plot to file.
    save_to_file = Button("Save")

    # File to which to save plot.
    save_file = File(join(expanduser("~"), "plot.pdf"))

    # Format in which to save the plot.
    format = Enum("PDF", "PNG", desc="output format for saved plot")

    # Copy a bitmap of the plot to the clipboard.
    clipboard_copy = Button("Copy", desc="a bitmap of "
                            "the plot copied to the clipboard")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        HGroup(Item(name="plot", editor=ComponentEditor(height=200),
                    show_label=False, style="custom"),
               VGroup(spring,
                      Item("format", show_label=False),
                      Item("save_to_file", show_label=False),
#                      Item("clipboard_copy", show_label=False)
                      spring)),
        id="pylon.ui.plot.rewards_plot",
        resizable=True
    )

    file_view = View(Item("save_file"), title="Select file",
                     buttons=["OK", "Cancel"], width=.3)

    #--------------------------------------------------------------------------
    #  "RewardsPlot" interface:
    #--------------------------------------------------------------------------

    def _data_default(self):
        """ Trait initialiser.
        """
        return ArrayPlotData()#x=[0])


    def _plot_default(self):
        """ Trait initialiser """

        plot = Plot(self.data, title=self.title,
                    bgcolor="white",
                    padding_top=50,
#                    fill_padding=True,
#                    height = 50,
#                    resizable = "v",
                    padding_bg_color="powderblue",
                    border_visible=True,
                    auto_colors=color_blind+dark)

        add_default_grids(plot)

        # Plot axes.
        index_axis = PlotAxis(component=plot, orientation="bottom",
            title=self.index_label, mapper=plot.index_mapper,
            title_font="modern 14", title_spacing=25,
            tick_label_font="modern 12", tick_interval=1.0)
        value_axis = PlotAxis(component=plot, orientation="left",
            title=self.value_label, mapper=plot.value_mapper)
#        plot.underlays.append(index_axis)
#        plot.underlays.append(value_axis)

        # Plot tools.
        plot.tools.append(PanTool(plot, constrain=True,
                                  constrain_direction="x"))

        plot.overlays.append(ZoomTool(plot, drag_button="right",
                                      always_on=True, tool_mode="range",
                                      axis="index"))
        # The DragZoom tool just zooms in and out as the user drags
        # the mouse vertically.
#        plot.tools.append(DragZoom(plot, drag_button="right"))

        # Plot axes
        index_axis = PlotAxis(component=plot, orientation="bottom",
            title="Time", mapper=plot.index_mapper)
        value_axis = PlotAxis(component=plot, orientation="left",
            title="Value", mapper=plot.value_mapper)
        plot.underlays.append(index_axis)
        plot.underlays.append(value_axis)

#        plot.index_mapper.range = self.action_plot.index_mapper.range
        plot.origin_axis_visible = True

        return plot


#    @on_trait_change("experiment.step")
    def set_data(self, rewards):
        """ Sets the reward plot data.
        """
        plot = self.plot
        plot_data = self.data

        # Set the index values.
#        size = len(plot_data.get_data("x"))
        if len(rewards) > 0:
            rows, cols = rewards[0].shape
        else:
            cols = 1
        plot_data.set_data("x", range(cols))

        for i, reward in enumerate(rewards):

            # Update plot data or add a new plot
            plot_name = str(i)
            if plot_name in plot_data.list_data():
                past_data = plot_data.get_data(plot_name)
                plot_data.set_data(plot_name, reward[0])
#                self.plot.request_redraw
            else:
                plot_data.set_data(plot_name, reward[0])

                colour = dark[randint(0, len(dark)-1)]
#                colour = self._get_colour(action.asset.id)

                plot.plot(("x", plot_name), name=plot_name, color="auto",
                          type="line", marker_size=6, marker="square",
                          line_width=2, tick_interval=1.0)


    def _save_to_file_fired(self, new):
        """ Handles the save plot button event.
        """
        self.save_plot()


    def save_plot(self, filename=None, size=(1024, 768)):
        """ Draws the plot to a pdf file.
        """
        plot = self.plot
        orig_w, orig_h = self.plot.outer_bounds

        if filename is None:
            retval = self.edit_traits(view="file_view", kind="livemodal")
            if retval.result:
                filename = self.save_file
            else:
                return

#        plot.bounds = list(size)
        plot.outer_bounds = list(size)
        plot.do_layout(force=True)

        if self.format == "PDF":
            from enthought.chaco.pdf_graphics_context \
                import PdfPlotGraphicsContext

            gc = PdfPlotGraphicsContext(filename=filename,
                                        dest_box = (0.5, 0.5, 5.0, 5.0))


        elif self.format == "PNG":
            gc = PlotGraphicsContext(size, dpi=72)

        gc.render_component(plot)
        gc.save(filename)

        plot.outer_bounds = orig_w, orig_h


    def _format_changed(self, new):
        """ Updates the file extension.
        """
        if new == "PDF":
            if self.save_file.endswith(".png"):
                self.save_file = self.save_file[:-4] + ".pdf"
        elif new == "PNG":
            if self.save_file.endswith(".pdf"):
                self.save_file = self.save_file[:-4] + ".png"
        else:
            pass


    @on_trait_change("clipboard_copy")
    def copy_to_clipboard(self):
        """ WX specific, though QT implementation is similar using
            QImage and QClipboard.
        """
        import wx
        width, height = self.plot.outer_bounds

        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(self.plot)

        # Create a bitmap the same size as the plot
        # and copy the plot data to it
        bitmap = wx.BitmapFromBufferRGBA(width+1, height+1,
                                    gc.bmp_array.flatten())
        data = wx.BitmapDataObject()
        data.SetBitmap(bitmap)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
#            wx.MessageBox("Plot copied to the clipboard.", "Success")
        else:
            wx.MessageBox("Unable to open the clipboard.", "Error")


    def _get_colour(self, id):
        """ Returns a colour from an id """

        idx = int(id[-3:]) % len(dark)-1

        return dark[idx]

# EOF -------------------------------------------------------------------------
