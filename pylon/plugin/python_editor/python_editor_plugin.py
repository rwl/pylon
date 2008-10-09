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

""" Python editor plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.plugins.text_editor.text_editor_plugin import TextEditorPlugin

from enthought.traits.api import List, Dict, String

#------------------------------------------------------------------------------
#  "PythonEditorPlugin" class:
#------------------------------------------------------------------------------

class PythonEditorPlugin(TextEditorPlugin):
    """ Python editor plug-in """

    # Extension point IDs
    ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"
    NEW_WIZARDS = "enthought.plugins.workspace.new_wizards"
    EDITORS = "enthought.plugins.workspace.editors"

    # Unique plugin identifier
    id = "enthought.plugins.python_editor"

    # Human readable plugin name
    name = "Python Editor"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed new resource wizards:
    new_wizards = List(contributes_to=NEW_WIZARDS)

    # Contributed workspace editors:
    editors = List(contributes_to=EDITORS)

    #--------------------------------------------------------------------------
    #  "PythonEditorPlugin" interface:
    #--------------------------------------------------------------------------

    def _action_sets_default(self):
        """ Trait initialiser """

        from python_editor_action_set import PythonEditorActionSet

        return [PythonEditorActionSet]


    def _new_wizards_default(self):
        """ Trait initialiser """

        from wizard_extension import NewFileWizardExtension

        return [NewFileWizardExtension]


    def _editors_default(self):
        """ Trait initialiser """

        from python_editor_extension import \
            PythonEditorExtension, TextEditorExtension

        return [TextEditorExtension]

# EOF -------------------------------------------------------------------------
