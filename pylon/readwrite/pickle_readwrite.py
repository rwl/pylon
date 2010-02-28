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

""" Defines a reader of pickled cases.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os.path
# import pickle
import cPickle as pickle
import logging

from pylon.readwrite.common import CaseReader, CaseWriter

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "PickleReader" class:
#------------------------------------------------------------------------------

class PickleReader(CaseReader):
    """ Defines a reader for pickled cases.
    """

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
            except Exception, detail:
                logger.error("Error unpickling '%s': %s" % (fname, detail))
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

class PickleWriter(CaseWriter):
    """ Writes a case to file using pickle.
    """

    def write(self, file_or_filename):
        """ Writes the case to file using pickle.
        """
        if isinstance(file_or_filename, basestring):
            fname = os.path.basename(file_or_filename)
            logger.info("Pickling case [%s]." % fname)

            file = None
            try:
                file = open(file_or_filename, "wb")
                pickle.dump(self.case, file)
            except Exception, detail:
                logger.error("Error writing to '%s': %s" % (fname, detail))
                return False
            finally:
                if file is not None:
                    file.close()
        else:
            file = file_or_filename
            pickle.dump(file, self.case)

        return True

# EOF -------------------------------------------------------------------------
