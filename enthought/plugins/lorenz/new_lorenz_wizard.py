""" A wizard for Lorenz resource creation """

import pickle

from enthought.io.api import File
from enthought.plugins.workspace.resource_wizard import BaseResourceWizard

from lorenz import Lorenz

class NewLorenzWizard(BaseResourceWizard):
    """ A wizard for Lorenz resource creation """

    def _finished_fired(self):
        """ Performs the resource creation """

        container_page = self.pages[0]
        resource_page = self.pages[1]

        resource = File(resource_page.abs_path)
        if not resource.exists:
            lorenz = Lorenz()
            resource.create_file(contents=pickle.dumps(lorenz))

        self._open_resource(resource)
        # FIXME: Refresh the parent folder not the whole tree
        self._refresh_container(None)
