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
An about dialog derived from the standard qt dialog that does not
include the copyright notice for Enthought and Riverbank Computing

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys

from enthought.pyface.ui.qt4.about_dialog import AboutDialog

from PyQt4 import QtCore, QtGui

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

# The HTML displayed in the QLabel.
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
      PyQt %s<br>
      Qt %s<br>
      </p>
      <p>
      Copyright &copy; 2008 Richard W. Lincoln
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
    An about dialog derived from the standard qt dialog that does not
    include the copyright notice for Enthought and Riverbank Computing

    """

    #--------------------------------------------------------------------------
    #  Protected "IDialog" interface.
    #--------------------------------------------------------------------------

    def _create_contents(self, parent):
        label = QtGui.QLabel()

        if parent.parent() is not None:
            title = parent.parent().windowTitle()
        else:
            title = ""

        # Set the title.
        self.title = "About %s" % title

        # Load the image to be displayed in the about box.
        image = self.image.create_image()
        path = self.image.absolute_path

        # The additional strings.
        additions = "<br />".join(self.additions)

        # Get the version numbers.
        py_version = sys.version[0:sys.version.find("(")]
        pyqt_version = QtCore.PYQT_VERSION_STR
        qt_version = QtCore.QT_VERSION_STR

        # Set the page contents.
        label.setText(
            _DIALOG_TEXT %
            (path, additions, py_version, pyqt_version, qt_version)
        )

        # Create the button.
        buttons = QtGui.QDialogButtonBox()

        if self.ok_label:
            buttons.addButton(self.ok_label, QtGui.QDialogButtonBox.AcceptRole)
        else:
            buttons.addButton(QtGui.QDialogButtonBox.Ok)

        buttons.connect(
            buttons, QtCore.SIGNAL("accepted()"),
            parent, QtCore.SLOT("accept()")
        )

        lay = QtGui.QVBoxLayout()
        lay.addWidget(label)
        lay.addWidget(buttons)

        parent.setLayout(lay)

# EOF -------------------------------------------------------------------------
