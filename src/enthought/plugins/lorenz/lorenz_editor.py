""" Defines a Lorenz resource editor """

from enthought.traits.api import AdaptedTo, AdaptsTo
from enthought.pyface.workbench.api import TraitsUIEditor

from lorenz_adapters import FileIContainerAdapter

from i_container import IContainer

class LorenzEditor(TraitsUIEditor):
    """ An editor for Lorenz resources """

    editor_input = AdaptsTo(IContainer)

    def _editor_input_default(self):
        """ Trait initialiser """

        return self.obj


    def create_ui(self, parent):
        """ Creates the traits UI that represents the editor """

        print self.editor_input
        obj = self.editor_input.get_object()

        ui = obj.edit_traits(
            parent=parent, view=self.view, kind="subpanel"
        )

        return ui
