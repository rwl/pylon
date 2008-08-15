""" Defines an interface for an object container """

from enthought.traits.api import HasTraits, Interface, Instance

class IContainer(Interface):

    obj = Instance(HasTraits)

    def get_object(self):
        """ Gets the contained object """
