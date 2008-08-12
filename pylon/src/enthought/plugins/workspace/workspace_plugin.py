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
#  Date:   09/07/2008
#
#------------------------------------------------------------------------------

""" Workspace plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

import sys

from os import mkdir

from os.path import dirname, isdir, join, exists, basename, expanduser

from enthought.etsconfig.api import ETSConfig
from enthought.envisage.api import Plugin, ExtensionPoint, ServiceOffer
from enthought.traits.api import List, Instance, String, Callable
from enthought.pyface.api import error
from enthought.plugins.workspace.workspace_launcher import WorkspaceLauncher

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "WorkspacePlugin" class:
#------------------------------------------------------------------------------

class WorkspacePlugin(Plugin):
    """ Workspace plug-in """

    # Extension point IDs
    SERVICE_OFFERS = "enthought.envisage.service_offers"
    VIEWS = "enthought.envisage.ui.workbench.views"
    PREFERENCES_PAGES = "enthought.envisage.ui.workbench.preferences_pages"
    ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"
#    BINDINGS = "enthought.plugins.python_shell.bindings"
    BINDINGS = "enthought.plugins.ipython_shell.bindings"
    # Workspace extension point IDs
    NEW_WIZARDS = "enthought.plugins.workspace.new_wizards"
    IMPORT_WIZARDS = "enthought.plugins.workspace.import_wizards"
    EXPORT_WIZARDS = "enthought.plugins.workspace.export_wizards"
    EDITORS = "enthought.plugins.workspace.editors"

    # Unique plugin identifier
    id = "enthought.plugins.workspace"

    # Human readable plugin name
    name = "Workspace"

    #--------------------------------------------------------------------------
    #  Extension points:
    #--------------------------------------------------------------------------

    new_wizards = ExtensionPoint(List(Callable), id=NEW_WIZARDS)

    import_wizards = ExtensionPoint(List(Callable), id=IMPORT_WIZARDS)

    export_wizards = ExtensionPoint(List(Callable), id=EXPORT_WIZARDS)

    editors = ExtensionPoint(List(Callable), id=EDITORS)

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed services:
    workspace_service_offers = List(contributes_to=SERVICE_OFFERS)

    # Contributed views:
    contributed_views = List(contributes_to=VIEWS)

    # Contributed preference pages:
    preferences_pages = List(contributes_to=PREFERENCES_PAGES)

    # Contributed action sets:
    action_sets = List(contributes_to=ACTION_SETS)

    # Contributed bindings:
    bindings_extensions = List(contributes_to=BINDINGS)

    # Contributed new element wizards:
    workspace_new_wizards = List(contributes_to=NEW_WIZARDS)

    # Contributed resource import wizards:
    workspace_import_wizards = List(contributes_to=IMPORT_WIZARDS)

    # Contributed export wizards:
    workspace_export_wizards = List(contributes_to=EXPORT_WIZARDS)

    #--------------------------------------------------------------------------
    #  "Plugin" interface:
    #--------------------------------------------------------------------------

#    def start(self):
#        """ Start the plug-in. """
#
#        prompt = self.application.preferences.get(
#            "enthought.plugins.workspace.prompt", "True"
#        )
#
#        default_path = self.application.preferences.get(
#            "enthought.plugins.workspace.default",
#            join(expanduser("~"), "workspace")
#        )
#
#        # FIXME: Implement preferences helper for type coercion
#        if (prompt == "True") or (not exists(default_path)):
#            # Note that we always offer the service via its name, but look it up
#            # via the actual protocol.
#            from i_workspace import IWorkspace
#
#            workspace = self.application.get_service(IWorkspace)
#            wl = WorkspaceLauncher(
#                workspace=workspace, app_name=self.application.name
#            )
#
#            retval = wl.edit_traits(kind="livemodal")
#            if retval.result:
#                # The preference trait is the opposite to the dialog trait
#                prompt_pref = not wl.default
#                # Set the preferences
#                self.application.preferences.set(
#                    "enthought.plugins.workspace.prompt", prompt_pref
#                )
#                self.application.preferences.set(
#                    "enthought.plugins.workspace.default",
#                    wl.workspace.absolute_path
#                )
#
#                # If a workspace didn't exist we would have to create one
#                if not wl.workspace.exists:
#                    try:
#                        wl.workspace.create_workspace()
#                    except ValueError:
#                        error(
#                            self.window.control, title="Error",
#                            message="An error was encountered trying to "
#                            "create the workspace."
#                        )
#                        self._exit_application()
#                del wl
#            else:
#                self._exit_application()
#
#        # TODO: Implement workspace refresh on start up
#
#        return


    def stop(self):
        """ Stop the plug-in """

        from i_workspace import IWorkspace
        workspace = self.application.get_service(IWorkspace)

        self.application.preferences.set(
            "enthought.plugins.workspace.default",
            workspace.absolute_path
        )

    #--------------------------------------------------------------------------
    #  "WorkspacePlugin" interface:
    #--------------------------------------------------------------------------

    def _workspace_service_offers_default(self):
        """ Trait initialiser """

        workspace_service_offer = ServiceOffer(
            protocol="enthought.plugins.workspace.i_workspace.IWorkspace",
            factory=self._create_workspace_service
        )

        return [workspace_service_offer]


    def _contributed_views_default(self):
        """ Trait initialiser """

        from workspace_view import WorkspaceView
        from workspace_tree_view import WorkspaceTreeView

        return [WorkspaceView]


    def _preferences_pages_default(self):
        """ Trait initialiser """

        from workspace_preferences_page import WorkspacePreferencesPage

        return [WorkspacePreferencesPage]


    def _action_sets_default(self):
        """ Trait initialiser """

        from workspace_action_set import \
            WorkspaceActionSet, ContextMenuActionSet

        return [WorkspaceActionSet, ContextMenuActionSet]


    def _bindings_extensions_default(self):
        """ Trait initialiser """

        from i_workspace import IWorkspace

        workspace = self.application.get_service(IWorkspace)

        return [{"workspace": workspace}]


    def _workspace_new_wizards_default(self):
        """ Trait initialiser """

        from workspace_wizard import FolderWizardExtension

        return [FolderWizardExtension]


    def _workspace_import_wizards_default(self):
        """ Trait initialiser """

        from workspace_wizard import ImportFileSystemWizardExtension

        return []


    def _workspace_export_wizards_default(self):
        """ Trait initialiser """

        return []

    #--------------------------------------------------------------------------
    #  Private interface:
    #--------------------------------------------------------------------------

    def _create_workspace_service(self):
        """ Factory method for the "Workspace" service. """

        # Only do imports when you need to! This makes sure that the import
        # only happens when somebody needs an "IWorkspace" service.
        from enthought.plugins.workspace.workspace_resource import File

        path = self.application.preferences.get(
            "enthought.plugins.workspace.default", expanduser("~")
        )

        return File(path)


    def _exit_application(self):
        """ Stops all plug-ins and exits """

        # FIXME: Is there a cleaner way of exiting?
        self.application.stop()
        sys.exit()

# EOF -------------------------------------------------------------------------
