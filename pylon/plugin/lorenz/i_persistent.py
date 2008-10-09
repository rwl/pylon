""" Interface for persistent """

from enthought.traits.api import Interface, Bool

class IPersistent(Interface):
    """ Interface for persistent """

    dirty = Bool(False)

    def save(self, file):
        """ Save the object to a file """

    def load(self, file):
        """ Load the object from a file """
