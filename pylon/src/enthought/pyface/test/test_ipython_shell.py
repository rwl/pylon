""" IPython shell example. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.api import ApplicationWindow, GUI

from enthought.pyface.ipython_shell import IPythonShell

#------------------------------------------------------------------------------
#  "MainWindow" class:
#------------------------------------------------------------------------------

class MainWindow(ApplicationWindow):
    """ The main application window. """

    size = (800, 600)

    #--------------------------------------------------------------------------
    #  Protected "IApplication" interface.
    #--------------------------------------------------------------------------

    def _create_contents(self, parent):
        """ Create the editor. """

        self._shell = IPythonShell(parent)

        return self._shell.control

#------------------------------------------------------------------------------
#  Application entry point:
#------------------------------------------------------------------------------

if __name__ == '__main__':
    # Create the GUI.
    gui = GUI()

    # Create and open the main window.
    window = MainWindow()
    window.open()

    # Start the GUI event loop!
    gui.start_event_loop()

# EOF -------------------------------------------------------------------------
