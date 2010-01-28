#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
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

""" Defines common components for reading/writing cases.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

BUS_ATTRS = ["name", "type", "v_base", "v_magnitude_guess",
    "v_angle_guess", "v_max", "v_min", "v_magnitude", "v_angle", "g_shunt",
    "b_shunt", "zone"]

BRANCH_ATTRS = ["name", "mode", "online", "r", "x", "b", "rate_a",
    "phase_shift", "online"]

GENERATOR_ATTRS = ["name", "base_mva", "v_magnitude", "p", "p_max", "p_min",
    "q", "q_max", "q_min", "pcost_model", "p_cost", "online"]

#------------------------------------------------------------------------------
#  "CaseWriter" class:
#------------------------------------------------------------------------------

class CaseWriter(object):
    """ Defines a base class for writers of case data.
    """

    def __init__(self, case):
        """ Initialises a new CaseWriter instance.
        """
        # Case to be written.
        self.case = case


    def write(self, file_or_filename):
        """ Writes the case data to file.
        """
        if isinstance(file_or_filename, basestring):
            file = None
            try:
                file = open(file_or_filename, "wb")
                self._write_data(file)
            except Exception, detail:
                logger.error("Error writing Dot data: %s" % detail)
            finally:
                if file is not None:
                    file.close()
        else:
            file = file_or_filename
            self._write_data(file)

        return file


    def _write_data(self, file):
        self.write_case_data(file)
        self.write_bus_data(file)
        self.write_branch_data(file)
        self.write_generator_data(file)
        self.write_generator_cost_data(file)


    def write_case_data(self, file):
        """ Writes case data to file.
        """
        pass


    def write_bus_data(self, file):
        """ Writes bus data to file.
        """
        pass


    def write_branch_data(self, file):
        """ Writes branch data to file.
        """
        pass


    def write_generator_data(self, file):
        """ Writes generator data to file.
        """
        pass


    def write_generator_cost_data(self, file):
        """ Writes generator cost data to file.
        """
        pass

#------------------------------------------------------------------------------
#  "CaseReader" class:
#------------------------------------------------------------------------------

class CaseReader(object):
    """ Defines a base class for case readers.
    """

    def read(self, file_or_filename):
        """ Reads the data file and returns a case.
        """
        raise NotImplementedError

# EOF -------------------------------------------------------------------------
