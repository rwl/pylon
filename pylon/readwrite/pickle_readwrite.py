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

""" Defines a reader of pickled networks.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle
import logging

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "PickleReader" class:
#------------------------------------------------------------------------------

class PickleReader(object):
    """ Defines a reader for pickled networks.
    """
    # Path to the data file or file object.
    file_or_filename = None

    # The resulting network object.
    network = Network

    def __init__(self, file_or_filename):
        """ Initialises a new PSATReader instance.
        """
        self.file_or_filename = file_or_filename
        self.network = self.parse_file(file_or_filename)


    def parse_file(self, file_or_filename=None):
        """ Loads a pickled network.
        """
        if file_or_filename is None:
            file_or_filename = self.file_or_filename


        if isinstance(file_or_filename, basestring):
            file = None
            try:
                file = open(file_or_filename, "rb")
                network = pickle.load(file)
            except:
                logger.error("Could not open '%s'." % file_or_filename)
                return None
            finally:
                if file is not None:
                    file.close()
        else:
            file = file_or_filename
            network = pickle.load(file)

        return network

#------------------------------------------------------------------------------
#  "PickleWriter" class:
#------------------------------------------------------------------------------

class PickleWriter(object):
    """ Writes a network to file using pickle.
    """
    network = None

    file_or_filename = ""

    def __init__(self, network, file_or_filename):
        """ Initialises a new PickleWriter instance.
        """
        self.network = network
        self.file_or_filename = file_or_filename


    def write(self):
        """ Writes the network to file using pickle.
        """
        network = self.network
        file_or_filename = self.file_or_filename

        if isinstance(file_or_filename, basestring):
            file = None
            try:
                file = open(file_or_filename, "wb")
                pickle.dump(file, network)
            except:
                logger.error("Could not open '%s'." % file_or_filename)
                return False
            finally:
                if file is not None:
                    file.close()
        else:
            file = file_or_filename
            pickle.dump(file, network)

        return True

# EOF -------------------------------------------------------------------------
