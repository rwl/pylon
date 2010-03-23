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
    "v_angle_guess", "v_max", "v_min", "p_demand", "q_demand",
    "g_shunt", "b_shunt", "v_magnitude", "v_angle",
    "p_lmbda", "q_lmbda", "mu_vmin", "mu_vmax", "position"]

BRANCH_ATTRS = ["name", "online", "r", "x", "b", "rate_a", "rate_b", "rate_c",
    "ratio", "phase_shift", "ang_min", "ang_max", "p_from", "p_to",
    "q_from", "q_to", "mu_s_from", "mu_s_to", "mu_angmin", "mu_angmax"]

GENERATOR_ATTRS = ["name", "online", "base_mva", "p", "p_max", "p_min",
    "v_magnitude", "q", "q_max", "q_min", "c_startup", "c_shutdown",
    "pcost_model", "p_cost", "qcost_model", "q_cost", "mu_pmin", "mu_pmax"]

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
                logger.error("Error writing data: %s" % detail)
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
