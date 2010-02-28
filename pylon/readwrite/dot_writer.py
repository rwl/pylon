#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines a class for writing case data in Graphviz DOT language.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
import subprocess
import StringIO

from pylon.readwrite.common import CaseWriter

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

BUS_ATTR = {"color": "blue"}
BRANCH_ATTR = {"color": "green"}
GENERATOR_ATTR = {}

#------------------------------------------------------------------------------
#  "DOTWriter" class:
#------------------------------------------------------------------------------

class DotWriter(CaseWriter):
    """ Write case data to file in Graphviz DOT language.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case, bus_attr=None, branch_attr=None, gen_attr=None):
        """ Initialises a new DOTWriter instance.
        """
        super(DotWriter, self).__init__(case)

        self.bus_attr = BUS_ATTR if bus_attr is None else bus_attr

        self.branch_attr = BRANCH_ATTR if branch_attr is None else branch_attr

        self.gen_attr = GENERATOR_ATTR if gen_attr is None else gen_attr

    #--------------------------------------------------------------------------
    #  "CaseWriter" interface:
    #--------------------------------------------------------------------------

    def write(self, file_or_filename, prog=None, format='xdot'):
        """ Writes the case data in Graphviz DOT language.

            The format 'raw' is used to dump the Dot representation of the
            Case object, without further processing. The output can be
            processed by any of graphviz tools, defined in 'prog'.
        """
        if prog is None:
            file = super(DotWriter, self).write(file_or_filename)
        else:
            buf = StringIO.StringIO()
            super(DotWriter, self).write(buf)
            buf.seek(0)
            data = self.create(buf.getvalue(), prog, format)

            if isinstance(file_or_filename, basestring):
                file = None
                try:
                    file = open(file_or_filename, "wb")
                    file.write(data)
                except Exception, detail:
                    logger.error("Error writing Dot data: %s" % detail)
                finally:
                    if file is not None:
                        file.close()
            else:
                file = file_or_filename
                file.write(data)

        return file


    def _write_data(self, file):
        super(DotWriter, self)._write_data(file)
        file.write("}\n")


    def write_case_data(self, file):
        """ Writes the case data to file
        """
        file.write("digraph %s {\n" % self.case.name)


    def write_bus_data(self, file, padding="    "):
        """ Writes bus data to file.
        """
        for bus in self.case.buses:
            attrs = ['%s="%s"' % (k, v) for k, v in self.bus_attr.iteritems()]
#            attrs.insert(0, 'label="%s"' % bus.name)
            attr_str = ", ".join(attrs)

            file.write("%s%s [%s];\n" % (padding, bus.name, attr_str))


    def write_branch_data(self, file, padding="    "):
        """ Writes branch data in Graphviz DOT language.
        """
        attrs = ['%s="%s"' % (k,v) for k,v in self.branch_attr.iteritems()]
        attr_str = ", ".join(attrs)

        for br in self.case.branches:
            file.write("%s%s -> %s [%s];\n" % \
                (padding, br.from_bus.name, br.to_bus.name, attr_str))


    def write_generator_data(self, file, padding="    "):
        """ Write generator data in Graphviz DOT language.
        """
        attrs = ['%s="%s"' % (k, v) for k, v in self.gen_attr.iteritems()]
        attr_str = ", ".join(attrs)

        edge_attrs = ['%s="%s"' % (k,v) for k,v in {}.iteritems()]
        edge_attr_str = ", ".join(edge_attrs)

        for g in self.case.generators:
            # Generator node.
            file.write("%s%s [%s];\n" % (padding, g.name, attr_str))

            # Edge connecting generator and bus.
            file.write("%s%s -> %s [%s];\n" % \
                       (padding, g.name, g.bus.name, edge_attr_str))

    #--------------------------------------------------------------------------
    #  "DotWriter" interface:
    #--------------------------------------------------------------------------

    def create(self, dotdata, prog="dot", format="xdot"):
        """ Creates and returns a representation of the graph using the
            Graphviz layout program given by 'prog', according to the given
            format.

            Writes the graph to a temporary dot file and processes it with
            the program given by 'prog' (which defaults to 'dot'), reading
            the output and returning it as a string if the operation is
            successful. On failure None is returned.

            Originally from PyDOT by Ero Carrera.
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

# EOF -------------------------------------------------------------------------
