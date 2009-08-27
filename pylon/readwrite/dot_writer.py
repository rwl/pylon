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

""" Defines a class for writing network data in Graphviz DOT language.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from dot2tex.dotparsing import find_graphviz

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

DEFAULT_BUS_ATTR = {"color": "blue"}

#------------------------------------------------------------------------------
#  "DOTWriter" class:
#------------------------------------------------------------------------------

class DotWriter(object):
    """ Write network data to file in Graphviz DOT language.
    """

    def __init__(self, bus_attr=None):
        """ Initialises a new DOTWriter instance.
        """
        self.network = None
        self.file_or_filename = ""

        if bus_attr is None:
            self.bus_attr = DEFAULT_BUS_ATTR
        else:
            self.bus_attr = bus_attr


    def __call__(self, network, file_or_filename):
        """ Calls the writer with the given network.
        """
        self.write(network, file_or_filename)


    def write(self, network, file_or_filename):
        """ Writes network data to file in Graphviz DOT language.
        """
        self.network = network
        self.file_or_filename = file_or_filename

        file = _get_file(file_or_filename)

        self.write_header(network, file)
        self.write_bus_data(network, file)
        self.write_branch_data(network, file)
        self.write_generator_data(network, file)
        self.write_load_data(network, file)
        self.write_generator_cost_data(network, file)

        # Close if passed the name of a file.
        if isinstance(file_or_filename, basestring):
            file.close()


    def write_header(self, network, file):
        """ Writes the header to file.
        """
        file.write("digraph %s {" % network.name)
        file.write("\n")


    def write_bus_data(self, network, file, padding="    "):
        """ Writes bus data to file.
        """
        for bus in network.buses:
#            attr = 'label="%s", %s' % (bus.name, self.bus_attr)
            bus_attr = self.bus_attr

            attrs = ['%s="%s"' % (k, v) for k, v in bus_attr.iteritems()]
            attrs.insert(0, 'label="%s"' % bus.name)
            attr_str = ", ".join(attrs)

            file.write("%snode %s [%s];" % (padding, id(bus), attr_str))
            file.write("\n")


    def write_branch_data(self, network, file):
        """ Writes branch data to file.
        """
        for branch in network.branches:
            source_bus = branch.source_bus
            target_bus = branch.target_bus
            branch_attr = self.branch_attr

            attrs = ['%s="%s"' % (k, v) for k, v in branch_attr.iteritems()]
            attr_str = ", ".join(attrs)

            file.write("%s%s -> %s [%s];" % \
                       (padding, id(source_bus), id(target_bus), attr_str))
            file.write("\n")


    def write_generator_data(self, network, file):
        """ Write generator data to file.
        """
        for bus in network.buses:
            for generator in bus.generators:
                # Generator node.
                file.write("%snode %s [%s];" % \
                           (padding, id(generator), attr_str))
                file.write("\n")

                # Edge connecting generator and bus.
                file.write("%s%s -> %s [%s];" % \
                           (padding, id(generator), id(bus), edge_attr_str))
                file.write("\n")


    def write_load_data(self, network, file):
        """ Writes load data to file.
        """
        for bus in network.buses:
            for load in bus.loads:
                # Load node.
                file.write("%snode %s [%s];" % \
                           (padding, id(load), attr_str))
                file.write("\n")

                # Edge connecting load and bus.
                file.write("%s%s -> %s [%s];" % \
                           (padding, id(bus), id(load), edge_attr_str))
                file.write("\n")


    def write_generator_cost_data(self, network, file):
        """ Writes generator cost data to file.
        """
        pass

#------------------------------------------------------------------------------
#  "XDOTWriter" class:
#------------------------------------------------------------------------------

class XDotWriter(DotWriter):
    """ Write network data to file in Graphviz XDOT format.
    """

    def __init__(self, prog="dot", format="xdot"):
        """ Initialises a new XDotWriter instance.
        """
        super(XDOTWriter, self).__init__(**kw_args)
        self.prog = prog
        self.format = format


    def write(self, network, file_or_filename):
        """ Writes network data to file in Graphviz XDOT language.
        """


    def write_header(self, network, file):
        """ Writes the header to file.
        """


    def write_bus_data(self, network, file):
        """ Writes bus data to file.
        """


    def write_branch_data(self, network, file):
        """ Writes branch data to file.
        """


    def write_generator_data(self, network, file):
        """ Write generator data to file.
        """


    def write_load_data(self, network, file):
        """ Writes load data to file.
        """


    def create(self, prog=None, format=None):
        """ Creates and returns a representation of the graph using the
            Graphviz layout program given by 'prog', according to the given
            format.

            Writes the graph to a temporary dot file and processes it with
            the program given by 'prog' (which defaults to 'xdot'), reading
            the output and returning it as a string if the operation is
            successful. On failure None is returned.
        """
        prog = self.program if prog is None else prog
        format = self.format if format is None else format

        # Make a temporary file ...
        tmp_fd, tmp_name = tempfile.mkstemp()
        os.close( tmp_fd )
        # ... and save the graph to it.
        dot_fd = file( tmp_name, "w+b" )
        self.save_dot( dot_fd )
        dot_fd.close()

        # Get the temporary file directory name.
        tmp_dir = os.path.dirname( tmp_name )

        # TODO: Shape image files (See PyDot). Important.

        # Process the file using the layout program, specifying the format.
        p = subprocess.Popen(
            ( self.programs[ prog ], '-T'+format, tmp_name ),
            cwd=tmp_dir,
            stderr=subprocess.PIPE, stdout=subprocess.PIPE)

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

        #pid, status = os.waitpid(p.pid, 0)
        status = p.wait()

        if status != 0 :
            logger.error("Program terminated with status: %d. stderr " \
                "follows: %s" % ( status, stderr_output ) )
        elif stderr_output:
            logger.error( "%s", stderr_output )

        # TODO: Remove shape image files from the temporary directory.

        # Remove the temporary file.
        os.unlink(tmp_name)

        return stdout_output


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
