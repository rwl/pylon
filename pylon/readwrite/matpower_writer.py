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

""" Defines classes for writing MATPOWER data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import basename, splitext

from pylon.case import PQ, PV, REFERENCE, ISOLATED
from pylon.generator import PW_LINEAR, POLYNOMIAL
from pylon.readwrite.common import CaseWriter

#------------------------------------------------------------------------------
#  "MATPOWERWriter" class:
#------------------------------------------------------------------------------

class MATPOWERWriter(CaseWriter):
    """ Write case data to a file in MATPOWER format [1].

        [1] Ray Zimmerman, "savecase.m", MATPOWER, PSERC Cornell,
            http://www.pserc.cornell.edu/matpower/, version 4.0b2, March 2010
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, case):
        """ Initialises a new MATPOWERWriter instance.
        """
        super(MATPOWERWriter, self).__init__(case)

        # Function name must match the file name in MATLAB.
        self._fcn_name = case.name

        self._prefix = "mpc."

    #--------------------------------------------------------------------------
    #  "CaseWriter" interface:
    #--------------------------------------------------------------------------

    def write(self, file_or_filename):
        """ Writes case data to file in MATPOWER format.
        """
        if isinstance(file_or_filename, basestring):
            self._fcn_name, _ = splitext(basename(file_or_filename))
        else:
            self._fcn_name = self.case.name

        super(MATPOWERWriter, self).write(file_or_filename)


#    def _write_data(self, file):
#        super(MATPOWERWriter, self)._write_data(file)
#        self.write_area_data(file)
#        file.write("return;\n")


    def write_case_data(self, file):
        """ Writes the case data in MATPOWER format.
        """
        file.write("function mpc = %s\n" % self._fcn_name)
        file.write('\n%%%% MATPOWER Case Format : Version %d\n' % 2)
        file.write("mpc.version = '%d';\n" % 2)

        file.write("\n%%%%-----  Power Flow Data  -----%%%%\n")
        file.write("%%%% system MVA base\n")
        file.write("%sbaseMVA = %g;\n" % (self._prefix, self.case.base_mva))


    def write_bus_data(self, file):
        """ Writes bus data in MATPOWER format.
        """
#        labels = ["bus_id", "type", "Pd", "Qd", "Gs", "Bs", "area", "Vm", "Va",
#            "baseKV", "Vmax", "Vmin"]

        bus_attrs = ["_i", "type", "p_demand", "q_demand", "g_shunt","b_shunt",
            "area", "v_magnitude_guess", "v_angle_guess", "v_base", "zone",
            "v_max", "v_min", "p_lmbda", "q_lmbda", "mu_vmin", "mu_vmax"]

        file.write("\n%%%% bus data\n")
        file.write("%%\tbus_i\ttype\tPd\tQd\tGs\tBs\tarea\tVm\tVa\tbaseKV"
                   "\tzone\tVmax\tVmin\tlam_P\tlam_Q\tmu_Vmax\tmu_Vmin")
        file.write("\n%sbus = [\n" % self._prefix)


        for bus in self.case.buses:
            vals = [getattr(bus, a) for a in bus_attrs]
            d = {PQ: 1, PV: 2, REFERENCE: 3, ISOLATED: 4}
            vals[1] = d[vals[1]]

            assert len(vals) == 17

            file.write("\t%d\t%d\t%g\t%g\t%g\t%g\t%d\t%.8g\t%.8g\t%g\t%d\t%g"
                       "\t%g\t%.4f\t%.4f\t%.4f\t%.4f;\n" % tuple(vals[:]))
        file.write("];\n")



    def write_generator_data(self, file):
        """ Writes generator data in MATPOWER format.
        """
        gen_attr = ["p", "q", "q_max", "q_min", "v_magnitude",
            "base_mva", "online", "p_max", "p_min", "mu_pmax", "mu_pmin",
            "mu_qmax", "mu_qmin"]

        file.write("\n%%%% generator data\n")
        file.write("%%\tbus\tPg\tQg\tQmax\tQmin\tVg\tmBase\tstatus\tPmax\tPmin")
        file.write("\tmu_Pmax\tmu_Pmin\tmu_Qmax\tmu_Qmin")
        file.write("\n%sgen = [\n" % self._prefix)

        for generator in self.case.generators:
            vals = [getattr(generator, a) for a in gen_attr]
            vals.insert(0, generator.bus._i)
            assert len(vals) == 14
            file.write("\t%d\t%g\t%g\t%g\t%g\t%.8g\t%g\t%d\t%g\t%g\t%g\t%g"
                       "\t%g\t%g;\n" % tuple(vals))
        file.write("];\n")


    def write_branch_data(self, file):
        """ Writes branch data to file.
        """
        branch_attr = ["r", "x", "b", "rate_a", "rate_b", "rate_c",
            "ratio", "phase_shift", "online", "ang_min", "ang_max", "p_from",
            "q_from", "p_to", "q_to", "mu_s_from", "mu_s_to", "mu_angmin",
            "mu_angmax"]

        file.write("\n%%%% branch data\n")
        file.write("%%\tfbus\ttbus\tr\tx\tb\trateA\trateB\trateC\tratio"
                   "\tangle\tstatus")
        file.write("\tangmin\tangmax")
        file.write("\tPf\tQf\tPt\tQt")
        file.write("\tmu_Sf\tmu_St")
        file.write("\tmu_angmin\tmu_angmax")
        file.write("\n%sbranch = [\n" % self._prefix)

        for branch in self.case.branches:
            vals = [getattr(branch, a) for a in branch_attr]

            vals.insert(0, branch.to_bus._i)
            vals.insert(0, branch.from_bus._i)

            file.write("\t%d\t%d\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%g\t%d\t%g\t%g"
                       "\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f;\n" %
                       tuple(vals))
        file.write("];\n")


    def write_generator_cost_data(self, file):
        """ Writes generator cost data to file.
        """
        file.write("\n%%%% generator cost data\n")
        file.write("%%\t1\tstartup\tshutdown\tn\tx1\ty1\t...\txn\tyn\n")
        file.write("%%\t2\tstartup\tshutdown\tn\tc(n-1)\t...\tc0\n")
        file.write("%sgencost = [\n" % self._prefix)

        for generator in self.case.generators:
            n = len(generator.p_cost)
            template = '\t%d\t%g\t%g\t%d'
            for _ in range(n):
                template = '%s\t%%g' % template
            template = '%s;\n' % template

            if generator.pcost_model == PW_LINEAR:
                t = 2
#                cp = [p for p, q in generator.p_cost]
#                cq = [q for p, q in generator.p_cost]
#                c = zip(cp, cq)
                c = [v for pc in generator.p_cost for v in pc]
            elif generator.pcost_model == POLYNOMIAL:
                t = 1
                c = list(generator.p_cost)
            else:
                raise

            vals = [t, generator.c_startup, generator.c_shutdown, n] + c

            file.write(template % tuple(vals))
        file.write("];\n")


#        file.write("%% generator cost data" + "\n")
#        file.write("%\n")
#        file.write("% Piecewise linear:" + "\n")
#        file.write("%\t1\tstartup\tshutdwn\tn_point\tx1\ty1\t...\txn\tyn\n")
#        file.write("%\n")
#        file.write("% Polynomial:" + "\n")
#        file.write("%\t2\tstartup\tshutdwn\tn_coeff\tc(n-1)\t...\tc0\n")
#
#        file.write("gencost = [" + "\n")
#        file.write("];" + "\n")

    #--------------------------------------------------------------------------
    #  "MatpowerWriter" interface:
    #--------------------------------------------------------------------------

    def write_area_data(self, file):
        """ Writes area data to file.
        """
        file.write("%% area data" + "\n")
        file.write("%\tno.\tprice_ref_bus" + "\n")
        file.write("areas = [" + "\n")
        # TODO: Implement areas
        file.write("\t1\t1;" + "\n")

        file.write("];" + "\n")

# EOF -------------------------------------------------------------------------
