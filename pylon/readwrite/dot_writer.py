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


#------------------------------------------------------------------------------
#  "DOTWriter" class:
#------------------------------------------------------------------------------

class DotWriter(object):
    """ Write network data to file in Graphviz DOT language.
    """

    def __init__(self):
        """ Initialises a new DOTWriter instance.
        """
        self.network = None
        self.file_or_filename = ""

        self.bus_attr = 'color="blue"'


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


    def write_bus_data(self, network, file):
        """ Writes bus data to file.
        """
        padding = "    "
        for bus in network.buses:
            attr = 'label="%s", %s' % (bus.name, self.bus_attr)
            file.write("%snode %s [%s];" % (padding, id(bus), attr))
            file.write("\n")


    def write_branch_data(self, network, file):
        """ Writes branch data to file.
        """


    def write_generator_data(self, network, file):
        """ Write generator data to file.
        """


    def write_load_data(self, network, file):
        """ Writes load data to file.
        """


    def write_generator_cost_data(self, network, file):
        """ Writes generator cost data to file.
        """
        pass


def _get_file(file_or_filename):
    """ Returns an open file from a file or a filename.
    """
    if isinstance(file_or_filename, basestring):
        file = open(file_or_filename, "wb")
    else:
        file = file_or_filename

    return file

# EOF -------------------------------------------------------------------------
