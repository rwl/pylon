#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Richard W. Lincoln
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Richard W. Lincoln
#  Date:   14/06/2008
#
#------------------------------------------------------------------------------

""" A Python code editor """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import exists, basename

from enthought.pyface.workbench.api import TraitsUIEditor

from enthought.traits.api import Code, Instance, Str

from enthought.traits.ui.api import View, Item, Group, CodeEditor

from enthought.pyface.api import PythonEditor, FileDialog, CANCEL

#------------------------------------------------------------------------------
#  "PythonWorkbenchEditor" class:
#------------------------------------------------------------------------------

class PythonWorkbenchEditor(TraitsUIEditor):
    """ A text editor """

    #--------------------------------------------------------------------------
    #  "PythonEditor" interface:
    #--------------------------------------------------------------------------

    # The text being edited:
    text = Code

    # The default traits view.
    traits_view = View(
        Group(
            Item(
                name="text", editor=CodeEditor(show_line_numbers=False)
            ),
            show_labels=False
        ),
        id="enthought.plugins.python_editor.python_workbench_editor",
        kind="live", resizable=True,
    )

    #--------------------------------------------------------------------------
    #  "TraitsUIEditor" interface.
    #--------------------------------------------------------------------------

    def _name_default(self):
        """ Trait initialiser """

#        self.obj.on_trait_change(self.on_path, "path")

        if self.obj.path == "":
            return "Unsaved Script"
        else:
            return basename(self.obj.path)


#    def on_path(self, new):
#        """ Handle the file path changing """
#
#        self.name = basename(new)


    def create_control(self, parent):
        """ Creates the toolkit-specific control that represents the
        editor. 'parent' is the toolkit-specific control that is
        the editor's parent.

        """

        ed = PythonEditor(parent, show_line_numbers=False)

        # FIXME: Implement toolkit specific Python editor subclass
        import wx
        styles = [
            wx.stc.STC_STYLE_DEFAULT,
            wx.stc.STC_STYLE_CONTROLCHAR,
            wx.stc.STC_STYLE_BRACELIGHT,
            wx.stc.STC_STYLE_BRACEBAD,
            wx.stc.STC_P_DEFAULT,
            wx.stc.STC_P_COMMENTLINE,
            wx.stc.STC_P_NUMBER,
            wx.stc.STC_P_STRING,
            wx.stc.STC_P_CHARACTER,
            wx.stc.STC_P_WORD,
            wx.stc.STC_P_TRIPLE,
            wx.stc.STC_P_TRIPLEDOUBLE,
            wx.stc.STC_P_CLASSNAME,
            wx.stc.STC_P_DEFNAME,
            wx.stc.STC_P_OPERATOR,
            wx.stc.STC_P_IDENTIFIER,
            wx.stc.STC_P_COMMENTBLOCK,
            wx.stc.STC_P_STRINGEOL
        ]

        for style in styles:
            ed.control.StyleSetFaceName(style, "monospace")
            ed.control.StyleSetSize(style, 10)

        path = self.obj.path
        if exists(path):
            ed.path = path
            ed.load()

        return ed.control

    #--------------------------------------------------------------------------
    #  "PythonWorkbenchEditor" interface.
    #--------------------------------------------------------------------------

    def save(self):
        """ Saves the text to disk. """

        # If the file has not yet been saved then prompt for the file name.
        if len(self.obj.path) == 0:
            self.save_as()

        else:
            f = file(self.obj.path, 'w')
            f.write(self.text)
            f.close()

            # We have just saved the file so we ain't dirty no more!
            self.dirty = False

        return


    def save_as(self):
        """ Saves the text to disk after prompting for the file name. """

        dialog = FileDialog(
            parent = self.window.control,
            action = 'save as',
            default_filename = self.name,
            wildcard = FileDialog.WILDCARD_PY
        )
        if dialog.open() != CANCEL:
            # Update the editor.
            self.id = dialog.path
            self.name = basename(dialog.path)

            # Update the resource.
            self.obj.path = dialog.path

            # Save it!
            self.save()

        return


    def _text_changed(self, trait_name, old, new):
        """ Static trait change handler. """

        if self.traits_inited():
            self.dirty = True

        return


    def _dirty_changed(self, dirty):
        """ Static trait change handler. """

        if len(self.obj.path) > 0:
            if dirty:
                self.name = basename(self.obj.path) + '*'

            else:
                self.name = basename(self.obj.path)

        return

# EOF -------------------------------------------------------------------------
