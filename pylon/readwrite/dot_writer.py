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

""" Defines a class for writing case data in Graphviz DOT language.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

import subprocess

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DEFAULT_BUS_ATTR = {"color": "blue"}
DEFAULT_BRANCH_ATTR = {"color": "green"}
DEFAULT_GENERATOR_ATTR = {}
DEFAULT_LOAD_ATTR = {}

#------------------------------------------------------------------------------
#  "DOTWriter" class:
#------------------------------------------------------------------------------

class DotWriter(object):
    """ Write case data to file in Graphviz DOT language.
    """

    def __init__(self, bus_attr=None):
        """ Initialises a new DOTWriter instance.
        """
        self.case = None
        self.file_or_filename = ""

        if bus_attr is None:
            self.bus_attr = DEFAULT_BUS_ATTR
        else:
            self.bus_attr = bus_attr

        self.branch_attr = DEFAULT_BRANCH_ATTR
        self.generator_attr = DEFAULT_GENERATOR_ATTR
        self.load_attr = DEFAULT_LOAD_ATTR


    def __call__(self, case, file_or_filename):
        """ Calls the writer with the given case.
        """
        self.write(case, file_or_filename)


    def write(self, case, file_or_filename):
        """ Writes case data to file in Graphviz DOT language.
        """
        self.case = case
        self.file_or_filename = file_or_filename

        file = _get_file(file_or_filename)

        self.write_header(case, file)
        self.write_bus_data(case, file)
        self.write_branch_data(case, file)
#        self.write_generator_data(case, file)
#        self.write_load_data(case, file)
#        self.write_generator_cost_data(case, file)

        file.write("}\n")

        # Close if passed the name of a file.
        if isinstance(file_or_filename, basestring):
            file.close()


    def write_header(self, case, file):
        """ Writes the header to file.
        """
        file.write("digraph %s {" % case.name)
        file.write("\n")


    def write_bus_data(self, case, file, padding="    "):
        """ Writes bus data to file.
        """
        for bus in case.buses:
#            attr = 'label="%s", %s' % (bus.name, self.bus_attr)
            bus_attr = self.bus_attr

            attrs = ['%s="%s"' % (k, v) for k, v in bus_attr.iteritems()]
            attrs.insert(0, 'label="%s"' % bus.name)
            attr_str = ", ".join(attrs)

            file.write("%s%s [%s];" % (padding, id(bus), attr_str))
            file.write("\n")


    def write_branch_data(self, case, file, padding="    "):
        """ Writes branch data to file.
        """
        for branch in case.branches:
            source_bus = branch.source_bus
            target_bus = branch.target_bus
            branch_attr = self.branch_attr

            attrs = ['%s="%s"' % (k, v) for k, v in branch_attr.iteritems()]
            attr_str = ", ".join(attrs)

            file.write("%s%s -> %s [%s];" % \
                       (padding, id(source_bus), id(target_bus), attr_str))
            file.write("\n")


    def write_generator_data(self, case, file):
        """ Write generator data to file.
        """
        for bus in case.buses:
            for generator in bus.generators:
                # Generator node.
                file.write("%s%s [%s];" % \
                           (padding, id(generator), attr_str))
                file.write("\n")

                # Edge connecting generator and bus.
                file.write("%s%s -> %s [%s];" % \
                           (padding, id(generator), id(bus), edge_attr_str))
                file.write("\n")


    def write_load_data(self, case, file):
        """ Writes load data to file.
        """
        for bus in case.buses:
            for load in bus.loads:
                # Load node.
                file.write("%s%s [%s];" % \
                           (padding, id(load), attr_str))
                file.write("\n")

                # Edge connecting load and bus.
                file.write("%s%s -> %s [%s];" % \
                           (padding, id(bus), id(load), edge_attr_str))
                file.write("\n")


    def write_generator_cost_data(self, case, file):
        """ Writes generator cost data to file.
        """
        pass

#------------------------------------------------------------------------------
#  Create and return a representation of the graph:
#------------------------------------------------------------------------------

def create_graph(dotdata, prog="dot", format="xdot"):
    """ Creates and returns a representation of the graph using the
        Graphviz layout program given by 'prog', according to the given
        format.

        Writes the graph to a temporary dot file and processes it with
        the program given by 'prog' (which defaults to 'dot'), reading
        the output and returning it as a string if the operation is
        successful. On failure None is returned.

        Valid 'prog' values may be: "dot", "circo", "neato", "twopi", "fdp"

        Valid 'format' values may be: 'dot', 'canon', 'cmap', 'cmapx',
        'cmapx_np', 'dia', 'fig', 'gd', 'gd2', 'gif', 'hpgl', 'imap',
        'imap_np', 'ismap', 'jpe', 'jpeg', 'jpg', 'mif', 'mp', 'pcl', 'pdf',
        'pic', 'plain', 'plain-ext', 'png', 'ps', 'ps2', 'svg', 'svgz', 'vml',
        'vmlz', 'vrml', 'vtx', 'wbmp', 'xdot', 'xlib', 'bmp', 'eps', 'gtk',
        'ico', 'tga', 'tiff'
    """
    import os, tempfile
    from dot2tex.dotparsing import find_graphviz

    # Map Graphviz executable names to their paths.
    progs = find_graphviz()
    if progs is None:
        logger.warning("GraphViz executables not found.")
        return None
    if not progs.has_key(prog):
        logger.warning('Invalid program [%s]. Available programs are: %s' % \
                       (prog, progs.keys()))
        return None

    # Make a temporary file ...
    tmp_fd, tmp_name = tempfile.mkstemp()
    os.close(tmp_fd)
    # ... and save the graph to it.
    dot_fd = file(tmp_name, "w+b")
    dot_fd.write(dotdata) # DOT language.
    dot_fd.close()

    # Get the temporary file directory name.
    tmp_dir = os.path.dirname(tmp_name)

    # Process the file using the layout program, specifying the format.
    p = subprocess.Popen((progs[prog], '-T'+format, tmp_name),
        cwd=tmp_dir, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    stderr = p.stderr
    stdout = p.stdout

    # Make sense of the standard output form the process.
    stdout_output = list()
    while True:
        data = stdout.read()
        if not data:
            break
        stdout_output.append(data)
    stdout.close()

    if stdout_output:
        stdout_output = ''.join(stdout_output)

    # Similarly so for any standard error.
    if not stderr.closed:
        stderr_output = list()
        while True:
            data = stderr.read()
            if not data:
                break
            stderr_output.append(data)
        stderr.close()

        if stderr_output:
            stderr_output = ''.join(stderr_output)

    status = p.wait()

    if status != 0 :
        logger.error("Program [%s] terminated with status: %d. stderr " \
            "follows: %s" % ( prog, status, stderr_output ) )
    elif stderr_output:
        logger.error( "%s", stderr_output )

    # Remove the temporary file.
    os.unlink(tmp_name)

    return stdout_output

#------------------------------------------------------------------------------
#  "XDOTWriter" class:
#------------------------------------------------------------------------------

#class XDotWriter(DotWriter):
#    """ Write case data to file in Graphviz XDOT format.
#    """
#
#    def __init__(self, prog="dot", format="xdot"):
#        """ Initialises a new XDotWriter instance.
#        """
#        super(XDOTWriter, self).__init__(**kw_args)
#
#        # Graphviz layout program ("dot", "circo", "neato", "twopi", "fdp").
#        self.prog = "dot"
#
#        # Format for writing to file.
#        self.format = "xdot"
#
#        # A dictionary containing the Graphviz executable names as keys and
#        # their paths as values.
#        progs = self.programs = find_graphviz()
#        if progs is None:
#            logger.warning("GraphViz executables not found.")
#            self.programs = {}
#
#
#    def write(self, case, file_or_filename):
#        """ Writes case data to file in Graphviz XDOT language.
#        """
#        xdot_data = self.create(case)
#
#        file = _get_file(file_or_filename)
#        file.write(xdot_data)
#        file.close()
#
#
#    def write_header(self, case, file):
#        """ Writes the header to file.
#        """
#        raise NotImplementedError
#
#
#    def write_bus_data(self, case, file):
#        """ Writes bus data to file.
#        """
#        raise NotImplementedError
#
#
#    def write_branch_data(self, case, file):
#        """ Writes branch data to file.
#        """
#        raise NotImplementedError
#
#
#    def write_generator_data(self, case, file):
#        """ Write generator data to file.
#        """
#        raise NotImplementedError
#
#
#    def write_load_data(self, case, file):
#        """ Writes load data to file.
#        """
#        raise NotImplementedError
#
#
#    def write_generator_cost_data(self, case, file):
#        """ Writes generator cost data to file.
#        """
#        raise NotImplementedError


#------------------------------------------------------------------------------
#  "Returns an open file from a file or a filename"
#------------------------------------------------------------------------------

def _get_file(file_or_filename):
    """ Returns an open file from a file or a filename.
    """
    if isinstance(file_or_filename, basestring):
        file = open(file_or_filename, "wb")
    else:
        file = file_or_filename

    return file

# EOF -------------------------------------------------------------------------
