""" Lorenz editor definition """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.api import ImageResource
from enthought.plugins.workspace.editor import Editor

#------------------------------------------------------------------------------
#  "LorenzEditorDefinition" class:
#------------------------------------------------------------------------------

class LorenzEditorDefinition(Editor):
    """ Associates a Lorenz editor with *.lnz files """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.lorenz_editor"

    # A name that will be used in the UI for this editor
    name = "Lorenz Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("document")

    # The contributed editor class
    editor_class = "enthought.plugins.lorenz.lorenz_editor:" \
        "LorenzEditor"

    # The list of file types understood by the editor
    extensions = [".lnz", ".pkl"]

    # If true, this editor will be used as the default editor for the type
    default = True
