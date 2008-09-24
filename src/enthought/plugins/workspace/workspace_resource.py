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

""" Defines subclasses of File for use with the workspace """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from os import listdir, mkdir
from os.path import join, isdir, dirname

#from configobj import ConfigObj

from enthought.io.api import File as IOFile

from enthought.traits.api import \
    Property, Bool, List, Instance, implements, This

from enthought.traits.ui.api import View, Group, Item, DirectoryEditor

from i_workspace import IWorkspace

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "File" class:
#------------------------------------------------------------------------------

class File(IOFile):
    """ Files are leaf resources which contain data. The contents of a file
    resource is stored as a file in the local file system.

    """

    implements(IWorkspace)

#    parent = Instance(Folder, allow_none=False)

    traits_view = View(
        Item(name="name")
    )

    def create_file(self, contents=''):
        """ Creates a file at this path """

        super(File, self).create_file(contents)

#        self.parent.add_file(self)

#------------------------------------------------------------------------------
#  "Folder" class:
#------------------------------------------------------------------------------

class Folder(IOFile):
    """ May contain files and/or other folders. A folder resource is stored
    as a directory in the local file system.

    """

#    parent = Instance(This, allow_none=False)

    _children = List(Instance(IOFile))

    traits_view = View(
        Item(name="name")
    )


    def _get_children(self):
        """ Returns the folder's children.

        Returns None if the path does not exist or is not a folder.

        """

        child_names = [f.name+f.ext for f in self._children]

        if self.is_folder:
            for name in listdir(self.path):
                contents_path = join(self.path, name)
                if name not in child_names:
                    if isdir(contents_path):
                        self._children.append(Folder(contents_path))
                    else:
                        self._children.append(File(contents_path))

            # Filter out file/folder resources for which the file system
            # entry no longer exists
#            self._children = [f for f in self._children
#                             if f.name+f.ext in listdir(self.path)]

        else:
            return None

        return self._children

    #--------------------------------------------------------------------------
    #  "Folder" interface.
    #--------------------------------------------------------------------------

    def get_folder(self, name):
        """ Returns a folder resource """

        for child in self.children:
            if child.is_folder:
                if child.name == name:
                    return child
        else:
            path = join(self.absolute_path, name)
            folder = Folder(path)

        return folder


    def get_file(self, name):
        """ Returns a file resource """

        for child in self.children:
            if child.is_file:
                if (child.name+child.ext) == name:
                    return child
        else:
            path = join(self.absolute_path, name)
            file = File(path)
            self.add_file(file)
            return file


    def add_file(self, file):
        """ Adds a file or a folder """

        self._children.append(file)

#------------------------------------------------------------------------------
#  "Project" class:
#------------------------------------------------------------------------------

class Project(Folder):

    #--------------------------------------------------------------------------
    #  "Project" interface.
    #--------------------------------------------------------------------------

#    workspace = Instance(
#        "enthought.plugins.workspace.workspace_resource.Workspace",
#        allow_none=False
#    )

    is_project = Property(Bool)

    traits_view = View(
        Item(name="name")
    )

    #--------------------------------------------------------------------------
    #  "object" interface.
    #--------------------------------------------------------------------------

#    def __init__(self, path, workspace, **traits):
#        """ Creates a new Project instance """
#
#        self.workspace = workspace
#
#        super(Project, self).__init__(path=path, workspace=workspace **traits)

    #--------------------------------------------------------------------------
    #  "IOFile" interface.
    #--------------------------------------------------------------------------

#    def _get_children(self):
#        """ Returns the folder's children.
#
#        Returns None if the path does not exist or is not a folder.
#
#        """
#
#        if self.is_folder:
#            children = []
#            for name in listdir(self.path):
#                # Hide files whose name starts with a "."
#                if name and name[0] is not ".":
#                    children.append(File(join(self.path, name)))
#
#        else:
#            children = None
#
#        return children

    #--------------------------------------------------------------------------
    #  "Project" interface.
    #--------------------------------------------------------------------------

    def _get_is_project(self):
        """ Returns True if the path exists and it contains a .project
        file

        """

        return self.is_folder and ".project" in listdir(self.path)


    def create_project(self):
        """ Creates a project at this path """

        if self.exists:
            raise ValueError("project <%s> already exists" % self.path)

        mkdir(self.path)

        # Create the ".project" file that turns the folder into a project!
#        config = ConfigObj()
#        config.filename = join(self.absolute_path, ".project")
#        config["name"] = self.name
#        config.write()

        # Add oneself to the workspace
#        self.workspace.add_project(self)

        return

#------------------------------------------------------------------------------
#  "Workspace" class:
#------------------------------------------------------------------------------

class Workspace(IOFile):

    implements(IWorkspace)

    # Projects in the workspace
    _children = List(Instance(Project))

    # The parent of this file/folder (None if it has no parent).
    parent = Property(Instance('Workspace'))

    # The default workspace view
    traits_view = View(
        Item(
            name="path", editor=DirectoryEditor(),
            show_label=False, style="simple"
        )
    )

    #--------------------------------------------------------------------------
    #  "IOFile" interface.
    #--------------------------------------------------------------------------

    def _get_children(self):
        """ Returns the folder's children.

        Returns None if the path does not exist or is not a folder.

        """

        project_names = [p.name+p.ext for p in self._children]

        if self.is_folder:
            for name in listdir(self.path):
                contents_path = join(self.path, name)
                # Only list folders:
                if isdir(contents_path):
                    # Hide folders whose name starts with a "."
                    if name and name[0] is not ".":
                        # Only list folders that contain a .project file
                        if ".project" in listdir(contents_path):
                            # Add non-existing projects

                            if name not in project_names:
                                self._children.append(Project(contents_path))
        else:
            return None

        return self._children


    def _get_parent(self):
        """ Returns the parent of this file/folder. """

        return Workspace(dirname(self.path))


    def create_workspace(self):
        """ Creates a workspace at this path """

        self.create_folder()


    def delete(self):
        """ Deletes this file/folder """

        logger.info("Workspace may not be deleted")

    #--------------------------------------------------------------------------
    #  "Workspace" interface.
    #--------------------------------------------------------------------------

    def get_project(self, name):
        """ Returns a project resource """

        for project in self._children:
            if (project.name+project.ext) == name:
                return project
        else:
            project = Project(join(self.absolute_path, name))
            # FIXME: We add the project here so that the workspace lists the
            # same object returned by get_project(). However, if the property
            # getter for 'children' is called before the folder for the project
            # is actually created on the file system then it will be removed
            # from the list.
            self.add_project(project)
            return project


    def add_project(self, project):
        """ Adds a project resource to the workspace """

        self._children.append(project)


    def get_folder(self, path):
        """ Returns a folder resource """

        folder = Folder(path)

        return folder

# EOF -------------------------------------------------------------------------
