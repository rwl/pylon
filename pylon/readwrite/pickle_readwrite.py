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

""" Defines a reader of pickled cases.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path
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
    """ Defines a reader for pickled cases.
    """

    def __call__(self, file_or_filename):
        """ Calls the reader with the given file or file name.
        """
        self.read(file_or_filename)


    def read(self, file_or_filename):
        """ Loads a pickled case.
        """
        if isinstance(file_or_filename, basestring):
            fname = os.path.basename(file_or_filename)
            logger.info("Unpickling case file [%s]." % fname)

            file = None
            try:
                file = open(file_or_filename, "rb")
                case = pickle.load(file)
            except:
                logger.error("Error unpickling '%s'." % fname)
                return None
            finally:
                if file is not None:
                    file.close()
        else:
            file = file_or_filename
            case = pickle.load(file)

        return case

#------------------------------------------------------------------------------
#  "PickleWriter" class:
#------------------------------------------------------------------------------

class PickleWriter(object):
    """ Writes a case to file using pickle.
    """

    def __call__(self, case, file_or_filename):
        """ Calls the writer with the given file or file name.
        """
        self.write(case, file_or_filename)


    def write(self, case, file_or_filename):
        """ Writes the case to file using pickle.
        """
        if isinstance(file_or_filename, basestring):
            fname = os.path.basename(file_or_filename)
            logger.info("Pickling case [%s]." % fname)

            file = None
            try:
                file = open(file_or_filename, "wb")
                pickle.dump(case, file)
            except:
                logger.error("Error writing to '%s'." % fname)
                return False
            finally:
                if file is not None:
                    file.close()
        else:
            file = file_or_filename
            pickle.dump(file, case)

        return True

# EOF -------------------------------------------------------------------------
