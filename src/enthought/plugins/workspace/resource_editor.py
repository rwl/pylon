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
#  Date:   14/07/2008
#
#------------------------------------------------------------------------------

""" Defines a resource editor for the workspace plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import getmtime

import pickle as pickle

from enthought.traits.api import \
    HasTraits, Instance, Property, Bool, DelegatesTo, Either, Str, Float

from enthought.traits.ui.api import View
from enthought.pyface.api import ImageResource, confirm, YES
from enthought.pyface.workbench.api import TraitsUIEditor

#------------------------------------------------------------------------------
#  "PickledProvider" class:
#------------------------------------------------------------------------------

class PickledProvider(HasTraits):
    """ Defines a DocumentProvider that handles reading and saving
    pickled objects.

    """

    is_modifiable = Property(Bool)

    id_readonly = Property(Bool)

    def create_document(self, resource):
        """ Unpickles the resource """

        fd = None
        try:
            fd = open(resource.absolute_path, "rb")
            document = pickle.load(fd)
        finally:
            if fd is not None:
                fd.close()

#        fd = open(resource.absolute_path, "rb")
#        document = pickle.Unpickler(fd).load()
#        fd.close()

        return document


    def do_save(self, resource, document):
        """ Pickles the resource """

        print "SAVING!", resource.absolute_path

        fd = None
        try:
            fd = open(resource.absolute_path, "wb")
            pickle.dump(document, fd)
        finally:
            if fd is not None:
                fd.close()

#        fd = open(resource.absolute_path, "w")
#        pickle.dump(document, fd)
#        fd.close()

        return True


    def _get_is_modifiable(self):
        """ Property getter """

        return True


    def _get_is_readonly(self):
        """ Property getter """

        return True

#------------------------------------------------------------------------------
#  "ResourceEditor" class:
#------------------------------------------------------------------------------

class ResourceEditor(TraitsUIEditor):
    """ An editor with a dynamic name and pickling abilities """

    #--------------------------------------------------------------------------
    #  "ResourceEditor" interface
    #--------------------------------------------------------------------------

    # The object provided by the resource being edited
    document = Instance(HasTraits)

    # Document provider that handles reading and saving resources
    provider = Instance(PickledProvider, ())

    # The time of the last modification to the resource
    m_time = Float

    # A View object (or its name) that defines a user interface for
    # editing trait attribute values of the current object. If the view is
    # defined as an attribute on this class, use the name of the attribute.
    # Otherwise, use a reference to the view object. If this attribute is
    # not specified, the View object returned by trait_view() is used.
    view = Either(Str, Instance(View))

    # An optional reference to the currently selected object in the editor
    selected = Instance(HasTraits)

    #--------------------------------------------------------------------------
    #  "TraitsUIEditor" interface
    #--------------------------------------------------------------------------

    def _name_default(self):
        """ Trait initialiser """

        if hasattr(self.obj, "name") and hasattr(self.obj, "ext"):
            self.obj.on_trait_change(self.on_name, "name")
            return self.obj.name + self.obj.ext
        else:
            return str(self.obj)


    def _m_time_default(self):
        """ Trait initialiser """

        if self.obj.exists:
            return getmtime(self.obj.absolute_path)
        else:
            return 0.0


    def create_ui(self, parent):
        """ Creates the traits UI that represents the editor """

        self.document = document = self.provider.create_document(self.obj)

        ui = document.edit_traits(
            view=self._create_view(), parent=parent, kind="subpanel"
        )

        # Dynamic notification of document object modification
        document.on_trait_change(self.on_document_modified)

        return ui


    def _create_view(self):
        """ Create a view with a tree editor """

        return self.view

    #--------------------------------------------------------------------------
    #  "ResourceEditor" interface
    #--------------------------------------------------------------------------

    def on_name(self, new):
        """ Handle the object name changing """

        self.name = new


    def on_document_modified(self):
        """ Dirties the editor when the document is modified """

        self.dirty = True


    def _dirty_fired(self, old, new):
        """ Prepends a '*' to the editor's name when dirty and
        removes it when clean.

        """

        if (old is False) and (new is True):
            self.name = "*" + self.name

        if (old is True) and (new is False):
            if self.name and (self.name[0] == "*"):
                self.name = self.name[1:]


    def save(self):
        """ Calls on the document provider to persist that state of
        the document

        """

        if self.document is not None:
            saved = self.provider.do_save(self.obj, self.document)
            if saved:
                self.dirty = False


    def _editor_closing_changed_for_window(self, editor):
        """ Handle the editor being closed """

        if (editor is self) and self.dirty:
            retval = confirm(
                self.window.control, title="Save Resource",
                message="'%s' has been modified. Save changes?" % self.name[1:]
            )

            if retval == YES:
                self.save()


    def _active_editor_changed_for_window(self, new):
        """ Handle the active editor changing """

        file = self.obj

        if (new is self) and file.exists \
        and (self.m_time != getmtime(file.absolute_path)):
            if self.dirty:
                name = self.name[1:]
            else:
                name = self.name

            retval = confirm(
                self.window.control, title="Load Resource",
                message="'%s' has been modified. Load modified resource?" %
                name
            )

            if retval == YES:
                raise NotImplementedError
#                self.window.edit(self.obj, kind=type(self))
#                self.window.close_editor(new)

# EOF -------------------------------------------------------------------------
