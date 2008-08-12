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
Editor for the network graph container

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.etsconfig.api import ETSConfig

from enthought.traits.ui.api import BasicEditorFactory

if ETSConfig.toolkit == 'wx':
    from enthought.traits.ui.wx.editor import Editor
    from enthought.enable.wx_backend.api import Window
elif ETSConfig.toolkit == 'qt4':
    from enthought.traits.ui.qt4.editor import Editor
    from enthought.enable.qt4_backend.api import Window
else:
    Editor = object
    Window = None

#------------------------------------------------------------------------------
#  "_GraphEditor" class:
#------------------------------------------------------------------------------

class _GraphEditor(Editor):

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # The graph editor is scrollable (overrides Traits UI Editor).
    scrollable = True

    #--------------------------------------------------------------------------
    #  Finishes initialising the editor by creating the underlying toolkit
    #  widget:
    #--------------------------------------------------------------------------

    def init(self, parent):
        """
        Finishes initialising the editor by creating the underlying toolkit
        widget.

        """
        self._window = Window(parent, -1, component=self.value)
        self.control = self._window.control

        # Listen to the "updated" trait of the value being edited
#        self.value.on_trait_change(self.update_editor, "updated")

    #--------------------------------------------------------------------------
    #  Updates the editor when the object trait changes externally to the
    #  editor:
    #--------------------------------------------------------------------------

    def update_editor(self):
#        self._window.component.request_redraw()
        pass

#------------------------------------------------------------------------------
#  "GraphEditor" class:
#------------------------------------------------------------------------------

class GraphEditor(BasicEditorFactory):

    # The editor class to be created:
    klass = _GraphEditor

# EOF -------------------------------------------------------------------------
