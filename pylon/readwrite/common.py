#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard Lincoln
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

bus_attrs = ["name", "mode", "slack", "v_base", "v_magnitude_guess",
    "v_angle_guess", "v_max", "v_min", "v_magnitude", "v_angle", "g_shunt",
    "b_shunt", "zone"]

branch_attrs = ["name", "mode", "online", "r", "x", "b", "s_max",
    "phase_shift", "phase_shift_max", "phase_shift_min", "online"]

generator_attrs = ["name", "base_mva", "v_magnitude", "p", "p_max", "p_min",
    "q", "q_max", "q_min", "c_startup", "c_shutdown", "cost_model",
    "cost_coeffs", "pwl_points", "p_cost", "u", "rate_up", "rate_down",
    "min_up", "min_down", "initial_up", "initial_down", "online"]

#load_attrs = ["name", "p", "q", "online"]

#------------------------------------------------------------------------------
#  "CaseWriter" class:
#------------------------------------------------------------------------------

class CaseWriter(object):
    """ Defines a base class for many writers of case data.
    """

    def __init__(self, case, file_or_filename):
        # Case to be written.
        self.case

        # File-like-object or name of the file to be written to.
        self.file_or_filename = file_or_filename

    def write(self):
        """ Writes the case data to file.
        """
        if isinstance(self.file_or_filename, basestring):
            file = open(self.file_or_filename, "wb")
        else:
            file = self.file_or_filename

        self.write_header()
        self.write_bus_data()
        self.write_branch_data()
        self.write_generator_data()
        self.write_generator_cost_data()

        file.close()


    def write_header(self):
        """ Writes header data to file.
        """
        raise NotImplementedError


    def write_bus_data(self):
        """ Writes bus data to file.
        """
        raise NotImplementedError


    def write_branch_data(self):
        """ Writes branch data to file.
        """
        raise NotImplementedError


    def write_generator_data(self):
        """ Writes generator data to file.
        """
        raise NotImplementedError


    def write_generator_cost_data(self):
        """ Writes generator cost data to file.
        """
        raise NotImplementedError

#------------------------------------------------------------------------------
#  "CaseReader" class:
#------------------------------------------------------------------------------

class CaseReader(object):
    """ Defines a base class for many case readers.
    """

    def __init__(self, file_or_filename):
        """ Constructs a new CaseReader instance.
        """
        # Path to the data file or file object.
        self.file_or_filename = None


    def read(self):
        """ Reads the data file and returns a case.
        """
        raise NotImplementedError

# EOF -------------------------------------------------------------------------
