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

"""
Enthought pyface package component

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import PyQt4

from enthought.traits.api import Bool, String, Enum

from enthought.util.clean_strings import python_name

from enthought.util.wx.drag_and_drop import PythonDropTarget

from enthought.pyface.key_pressed_event import KeyPressedEvent

from enthought.pyface.api import Widget

from enthought.pyface.ui.qt4.ipython_view import IPShellWidget

#------------------------------------------------------------------------------
#  "IPythonShell" class:
#------------------------------------------------------------------------------

class IPythonShell(Widget):
    """
    The toolkit specific implementation of an IPythonShell. Not to be
    confused with the IPythonShell interface.

    """

    # Show the IPython banner with version numbers etc by default:
    ipython_banner = Bool(True)

    # Message to display instead of the IPython banner:
    intro = String

    # Enables Scintilla completion:
    completion_method = Enum("IPython", "STC")

    # Choice of white or black background:
    background_colour = Enum("White", "Black")

    #--------------------------------------------------------------------------
    #  "object" interface.
    #--------------------------------------------------------------------------

    def __init__(self, parent, **traits):
        """ Creates a new shell """

        # Base class constructor.
        super(IPythonShell, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

    #--------------------------------------------------------------------------
    #  "Widget" interface.
    #--------------------------------------------------------------------------

    def _create_control(self, parent):
        """
        Create the toolkit-specific control that represents the widget.

        """

        # Show a custom banner if not the IPython one:
        if not self.ipython_banner:
            intro = self.intro
        else:
            intro = None

        shell = IPShellWidget(
            parent, intro=intro,
            background_color=self.background_colour.upper()
        )

        # Set the initial completion method
        shell.setCompletionMethod(self.completion_method.upper())

        # Enable the shell as a drag and drop target
#        shell.SetDropTarget(PythonDropTarget(self))

        return shell

    #--------------------------------------------------------------------------
    #  "PythonDropTarget" handler interface.
    #--------------------------------------------------------------------------

    def on_drop(self, x, y, obj, default_drag_result):
        """ Called when a drop occurs on the shell. """

        # If we can't create a valid Python identifier for the name of an
        # object we use this instead.
        name = 'dragged'

        if hasattr(obj, 'name') \
           and isinstance(obj.name, basestring) and len(obj.name) > 0:
            py_name = python_name(obj.name)

            # Make sure that the name is actually a valid Python identifier.
            try:
                if eval(py_name, {py_name : True}):
                    name = py_name
            except:
                pass

        self.control.IP.updateNamespace({name: obj})
        self.control.IP.doExecute(name)
        self.control.SetFocus()

        # We always copy into the shell since we don't want the data
        # removed from the source
        return PyQt4


    def on_drag_over(self, x, y, obj, default_drag_result):
        """ Indicates the object will be copied """

        return PyQt4

    #--------------------------------------------------------------------------
    #  "IPythonShell" interface.
    #--------------------------------------------------------------------------

    def _completion_changed(self, new):
        """ Handles the code completion method """

        if self.control is not None:
            self.control.setCompletionMethod(new.upper())


    def _background_colour_changed(self, new):
        """ Handles the shell background colour """

        if self.control is not None:
            self.control.setBackgroundColor(new.upper())

# EOF -------------------------------------------------------------------------
