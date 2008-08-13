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

""" Python editor extensions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.pyface.api import ImageResource
from enthought.plugins.workspace.editor import Editor

#------------------------------------------------------------------------------
#  "PythonEditorExtension" class:
#------------------------------------------------------------------------------

class PythonEditorExtension(Editor):
    """ Associates a Python editor with *.py files """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.python_editor"

    # A name that will be used in the UI for this editor
    name = "Python Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("python")

    # The contributed editor class
    editor_class = "enthought.plugins.python_editor.python_workbench_editor:" \
        "PythonWorkbenchEditor"

    # The list of file types understood by the editor
    extensions = [".py"]

    # If true, this editor will be used as the default editor for the type
    default = True

#------------------------------------------------------------------------------
#  "TextEditorExtension" class:
#------------------------------------------------------------------------------

class TextEditorExtension(Editor):
    """ Associates a text editor with *.py files """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.python_editor.text_editor_extension"

    # A name that will be used in the UI for this editor
    name = "Text Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("python")

    # The contributed editor class
    editor_class = "enthought.plugins.text_editor.editor.text_editor:" \
        "TextEditor"

    # The list of file types understood by the editor
    extensions = [".py"]

    # If true, this editor will be used as the default editor for the type
    default = True

# EOF -------------------------------------------------------------------------
