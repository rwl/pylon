#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

from enthought.traits.api \
    import HasTraits, Instance, Str, List, TraitListEvent, Disallow

#------------------------------------------------------------------------------
#  "Root" class:
#------------------------------------------------------------------------------

class Root(HasTraits):
    """ Defines a base class for all CIM elements.
    """

    # Unique resource identifier.
    URI = Str

    # Bi-directional association with the containing model.
    ContainedBy = Instance("Model", opposite="Contains")

    #--------------------------------------------------------------------------
    #  'object' interface:
    #--------------------------------------------------------------------------

    def __init__(self, **traits):
        super(Root, self).__init__(**traits)
        # Dictionary of trait definitions matching the given metadata. Metadata
        # values may be lambda expressions or functions that return True
        # if the trait attribute is to be included.
        opposed = self.traits(opposite = lambda val: bool(val))

        print "OPPOSITES:", self, opposed.keys()

        for name, trait in opposed.iteritems():
            if trait.is_trait_type( Instance ):
                print "Instance handler:", self, name
                self.on_trait_change(self._on_instance, name)

            elif trait.is_trait_type( List ):# and \
#                trait.inner_traits[0].is_trait_type( Instance ):
                print "List handler:", self, name
                self.on_trait_change(self._on_list, name)
                self.on_trait_change(self._on_list, name + "_items")

        # Fire trait change events for any traits specified.
        for trait_name, value in traits.iteritems():
            self.trait_property_changed(name, getattr(self, trait_name), value)

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    def _on_instance(self, obj, name, old, new):
        """ Handles traits of type Instance changing.
        """
        opposite = obj.trait(name).opposite

        print "ON INSTANCE:", obj, name, old, new

        if old is not None:
            opposite_trait = old.trait(opposite)
            # Unset old one-to-one association.
            if opposite_trait.is_trait_type( Instance ):
                print "Unsetting one-to-one:", old, opposite
                setattr(old, opposite, None)
            # Remove instance from old one-to-many association.
            elif opposite_trait.is_trait_type( List ) and \
                (obj in getattr(old, opposite)):
                print "Removing one-to-many:", old, opposite
                getattr(old, opposite).remove(obj)

        if new is not None:
            opposite_trait = new.trait(opposite)
            # Set new one-to-one association.
            if opposite_trait.is_trait_type( Instance ):
                print "Setting one-to-one:", new, opposite
                setattr(new, opposite, obj)
            # Set new one-to-many association.
            elif opposite_trait.is_trait_type( List ) and \
                (obj not in getattr(new, opposite)):
                print "Setting one-to-many:", new, opposite
                getattr(new, opposite).append(obj)


    def _on_list(self, obj, name, old, new):
        """ Handles List instances changing.
        """
        print "ON LIST:", obj, name, old, new
        # Use the same method for the list being set and for items being
        # added and removed from the list.  When individual items are changed
        # the last argument is an event with '.added' and '.removed' traits.
        if isinstance(new, TraitListEvent):
            old = new.removed
            new = new.added

        # Name of the trait on the referenced object that is the 'opposite'
        # reference back to obj.
        opposite = obj.trait(name).opposite

        for old_obj in old:
            opposite_trait = old_obj.trait(opposite)
            # Unset old many-to-one associations.
            if opposite_trait.is_trait_type( Instance ):
                print "Unsetting many-to-one:", old_obj, opposite
                setattr(old_obj, opposite, None)
            # Remove instance from old many-to-many associtaions.
            elif opposite_trait.is_trait_type( List ) and \
                (old_obj in getattr(old_obj, opposite)):
                print "Removing many-to-many:", old_obj, opposite
                getattr(old_obj, opposite).remove(obj)

        for new_obj in new:
            opposite_trait = new_obj.trait(opposite)
            # Set new many-to-one associations.
            if opposite_trait.is_trait_type( Instance ):
                print "Setting many-to-one:", new_obj, opposite
                setattr(new_obj, opposite, obj)
            # Set new many-to-many associations.
            elif opposite_trait.is_trait_type( List ) and \
                (new_obj not in getattr(new_obj, opposite)):
                print "Setting many-to-many:", getattr(new_obj, opposite)
                getattr(new_obj, opposite).append(obj)

#------------------------------------------------------------------------------
#  "Model" class:
#------------------------------------------------------------------------------

class Model(Root):
    """ Defines a container class for all model elements.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions.:
    #--------------------------------------------------------------------------

    # Model nesting not permitted.
    ContainedBy = Disallow

    # Model elements.
    Contains = List(Instance(Root), opposite="ContainedBy")

# EOF -------------------------------------------------------------------------
