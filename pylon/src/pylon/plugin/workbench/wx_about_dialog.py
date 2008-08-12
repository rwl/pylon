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

"""
wxPython specific about dialog derived from the pyface dialog, but
no Enthought copyright notice.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys

import wx
import wx.html
import wx.lib.wxpTag

from enthought.pyface.ui.wx.about_dialog import AboutDialog

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

_DIALOG_TEXT = """
<html>
  <body>
    <center>
      <table width="100%%" cellspacing="4" cellpadding="0" border="0">
        <tr>
          <td align="center">
          <p>
            <img src="%s" alt="">
          </td>
        </tr>
      </table>

      <p>
      %s<br>
      <br>
      Python %s<br>
      wxPython %s<br>
      </p>
      <p>
      Copyright &copy; 2008 Richard W. Lincoln
      </p>

      <p>
        <wxp module="wx" class="Button">
          <param name="label" value="%s">
          <param name="id"    value="ID_OK">
        </wxp>
      </p>
  </center>
  </body>
</html>
"""

#------------------------------------------------------------------------------
#  "AboutPylonDialog" class:
#------------------------------------------------------------------------------

class AboutPylonDialog(AboutDialog):
    """
    wxPython specific about dialog derived from the pyface dialog, but
    no Enthought copyright notice.

    """

    #--------------------------------------------------------------------------
    #  Protected "IDialog" interface.
    #--------------------------------------------------------------------------

    def _create_contents(self, parent):
        if parent.GetParent() is not None:
            title = parent.GetParent().GetTitle()

        else:
            title = ""

        # Set the title.
        self.title = "About %s" % title

        # Load the image to be displayed in the about box.
        image = self.image.create_image()
        path  = self.image.absolute_path

        # The additional strings.
        additions = '<br />'.join(self.additions)

        # The width of a wx HTML window is fixed (and  is given in the
        # constructor). We set it to the width of the image plus a fudge
        # factor! The height of the window depends on the content.
        width = image.GetWidth() + 80
        html = wx.html.HtmlWindow(parent, -1, size=(width, -1))

        # Get the version numbers.
        py_version = sys.version[0:sys.version.find("(")]
        wx_version = wx.VERSION_STRING

        # Get the text of the OK button.
        if self.ok_label is None:
            ok = "OK"
        else:
            ok = self.ok_label

        # Set the page contents.
        html.SetPage(
            _DIALOG_TEXT % (path, additions, py_version, wx_version, ok)
        )

        # Make the 'OK' button the default button.
        ok_button = html.FindWindowById(wx.ID_OK)
        ok_button.SetDefault()

        # Set the height of the HTML window to match the height of the content.
        internal = html.GetInternalRepresentation()
        html.SetSize((-1, internal.GetHeight()))

        # Make the dialog client area big enough to display the HTML window.
        # We add a fudge factor to the height here, although I'm not sure why
        # it should be necessary, the HTML window should report its required
        # size!?!
        width, height = html.GetSize()
        parent.SetClientSize((width, height + 10))

# EOF -------------------------------------------------------------------------
