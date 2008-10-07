""" Defines an adapter for adapting files containing pickled objects to
IContainers.

"""

import pickle
from enthought.io.api import File
from enthought.traits.api import Adapter, adapts, Instance
from i_container import IContainer

class FileIContainerAdapter(Adapter):
    """ An adapter from "File" to "IContainer" """

    # Declare the interfaces this adapter implements for its client:
    adapts(File, to=IContainer, when="adaptee.ext == '.pkl'")

    # The object that is being adapted.
    adaptee = Instance(File)

    def get_object(self):
        """ Gets the contained object """

        fd = None
        try:
            fd = open(self.adaptee.absolute_path, "rb")
            object = pickle.load(fd)
        finally:
            if fd is not None:
                fd.close()

        return object

class FileIEditableAdapter(Adapter):
    """ An adapter from "File" to "IEditable" """

    # Declare the interfaces this adapter implements for its client:
    adapts(File, to=IContainer, when="adaptee.ext == '.pkl'")

    # The object that is being adapted.
    adaptee = Instance(File)

    # Is the object 'dirty'?
    dirty = Bool(False)

    # The time of the last modification
    m_time = Float

#    def get_editor_input(self):
#        """ Returns the object to be edited """

    def save(self, obj):
        """ Save to file """

        fd = None
        try:
            fd = open(self.adaptee.absolute_path, "wb")
            pickle.dump(obj, fd)
        finally:
            if fd is not None:
                fd.close()


    def load(self):
        """ Load the file """

        fd = None
        try:
            fd = open(self.adaptee.absolute_path, "rb")
            obj = pickle.load(fd)
        finally:
            if fd is not None:
                fd.close()

        return obj
