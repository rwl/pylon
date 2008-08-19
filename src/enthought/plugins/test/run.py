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

""" Run the test application """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.envisage.api import Application
from enthought.envisage.ui.workbench.api import WorkbenchApplication
from enthought.envisage.core_plugin import CorePlugin
from enthought.envisage.ui.workbench.workbench_plugin import WorkbenchPlugin
from enthought.envisage.developer.developer_plugin import DeveloperPlugin
from enthought.logger.plugin.logger_plugin import LoggerPlugin

from enthought.envisage.developer.ui.developer_ui_plugin import \
    DeveloperUIPlugin

try:
    from enthought.plugins.ipython_shell.ipython_shell_plugin import \
        IPythonShellPlugin as PythonShellPlugin
except ImportError:
    from enthought.plugins.python_shell.python_shell_plugin import \
        PythonShellPlugin

from enthought.plugins.python_editor.python_editor_plugin import \
    PythonEditorPlugin

from enthought.plugins.image_editor.image_editor_plugin import \
    ImageEditorPlugin

from enthought.plugins.workspace.workspace_plugin import WorkspacePlugin

from enthought.plugins.lorenz.lorenz_plugin import LorenzPlugin

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger()
handler = logging.StreamHandler()
#handler = logging.StreamHandler(file("/tmp/pylon.log", "w"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#  "main" function:
#------------------------------------------------------------------------------

def main():
    """ Runs the application """

    # Create an Envisage application.
    application = WorkbenchApplication(
        id = "test",
        plugins = [
            CorePlugin(),
            WorkbenchPlugin(),
#            DeveloperPlugin(),
#            DeveloperUIPlugin(),
            LoggerPlugin(),
            PythonShellPlugin(),
            PythonEditorPlugin(),
            ImageEditorPlugin(),
            WorkspacePlugin(),
            LorenzPlugin()
        ]
    )

    # Run it!
    application.run()

    return


if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
