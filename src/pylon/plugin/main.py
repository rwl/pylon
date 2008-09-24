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

""" Run the Pylon application """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from enthought.envisage.core_plugin import CorePlugin

from enthought.envisage.developer.developer_plugin import DeveloperPlugin

from enthought.envisage.developer.ui.developer_ui_plugin import \
    DeveloperUIPlugin

#try:
#    from enthought.plugins.ipython_shell.ipython_shell_plugin import \
#        IPythonShellPlugin as PythonShellPlugin
#except ImportError:
from enthought.plugins.python_shell.python_shell_plugin import \
    PythonShellPlugin

from enthought.plugins.text_editor.text_editor_plugin import TextEditorPlugin

from enthought.plugins.python_editor.python_editor_plugin import \
    PythonEditorPlugin

from enthought.plugins.workspace.workspace_plugin import WorkspacePlugin

from enthought.plugins.property_view.property_view_plugin import \
    PropertyViewPlugin

from enthought.plugins.image_editor.image_editor_plugin import \
    ImageEditorPlugin

from enthought.logger.plugin.logger_plugin import LoggerPlugin

#------------------------------------------------------------------------------
#  Pylon imports:
#------------------------------------------------------------------------------

from pylon.plugin.workbench.pylon_workbench_application import \
    PylonWorkbenchApplication

from pylon.plugin.workbench.pylon_workbench_plugin import PylonWorkbenchPlugin

from pylon.plugin.pylon_plugin import PylonPlugin

from pylon.plugin.filter.matpower.matpower_plugin import MATPOWERPlugin
from pylon.plugin.filter.psat.psat_plugin import PSATPlugin
from pylon.plugin.filter.psse.psse_plugin import PSSEPlugin
from pylon.plugin.filter.m3.m3_plugin import M3Plugin

from pylon.plugin.routine.dc_opf.dc_opf_plugin import DCOPFPlugin
from pylon.plugin.routine.dc_pf.dc_pf_plugin import DCPFPlugin
from pylon.plugin.routine.ac_opf.ac_opf_plugin import ACOPFPlugin
from pylon.plugin.routine.ac_pf.ac_pf_plugin import ACPFPlugin

from pylon.plugin.graph.graph_plugin import GraphPlugin

from pylon.plugin.graph_image.graph_image_plugin import GraphImagePlugin

from pylon.plugin.pyreto.pyreto_plugin import PyretoPlugin

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
    application = PylonWorkbenchApplication(
        id = "pylon",
        plugins = [
            CorePlugin(),
            DeveloperPlugin(),
            DeveloperUIPlugin(),
            PythonShellPlugin(),
#            TextEditorPlugin(),
            PythonEditorPlugin(),
            WorkspacePlugin(),
            PropertyViewPlugin(),
            ImageEditorPlugin(),
            LoggerPlugin(),
            # Pylon plug-ins:
            PylonWorkbenchPlugin(),
            PylonPlugin(),
            MATPOWERPlugin(),
            PSATPlugin(),
            PSSEPlugin(),
            M3Plugin(),
            DCPFPlugin(),
            DCOPFPlugin(),
            ACPFPlugin(),
            ACOPFPlugin(),
            GraphImagePlugin(),
            GraphPlugin(),
            PyretoPlugin()
        ]
    )

    # Run it!
    application.run()

    return


if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
