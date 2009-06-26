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

""" Defines the entry point for Pylon.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging

from optparse \
    import OptionParser

from pylon.api \
    import Network

from pylon.readwrite.api \
    import read_matpower, read_psat, read_psse, MATPOWERWriter, ReSTWriter, \
    CSVWriter, ExcelWriter

from pylon.routine.api \
    import DCPFRoutine, DCOPFRoutine, NewtonPFRoutine, ACOPFRoutine, \
    FastDecoupledPFRoutine

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------
#  Format detection:
#------------------------------------------------------------------------------

def detect_network_type(input, file_name=""):
    """ Detects the format of a network data file according to the
        file extension and the header.
    """
    if file_name.endswith(".m"):
        line = input.readline()

        if line.startswith("Bus.con" or line.startswith("%")):
            type = "psat"
            logger.info("Recognised PSAT data file.")

        elif line.startswith("function"):
            type = "matpower"
            logger.info("Recognised MATPOWER data file.")

        else:
            type = "matlab"
            
        # Seek to buffer start for correct parsing.
        input.seek(0)

    elif file_name.endswith(".raw") or file_name.endswith(".psse"):
        type = "psse"
        logger.info("Recognised PSS/E data file.")

    else:
        type = "unrecognised"

    return type

#------------------------------------------------------------------------------
#  "PylonApplication" class:
#------------------------------------------------------------------------------

class PylonApplication(object):
    """ Simulates energy networks.
    """
    # Name of the input file.
    file_name = ""
    
    # Format in which the network is stored.  Possible values are: 'any',
    # 'matpower', 'psat', 'matlab' and 'psse'.
    type = "any"

    # Routine type used to solve the network. Possible values are: 'acpf',
    # 'dcpf', 'acopf' and 'dcopf'.
    routine = "acpf"

    # Algorithm to be used in the routine. Possible values are: 'newton'
    algorithm = "newton"

    # Output format type. Possible values are: 'rst', 'matpower', 'excel' and
    # 'csv'.
    output_type = "rst"

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, file_name="", type="any", routine="acpf",
            algorithm="newton", output_type="rst"):
        self.file_name   = file_name
        self.routine     = routine
        self.algorithm   = algorithm
        self.output_type = output_type

    #--------------------------------------------------------------------------
    #  Solve the network:
    #--------------------------------------------------------------------------

    def solve(self, input, output):
        """ Forms a network from the input text, obtains a solution using the
            specified routine and writes a report to the output.
        """
        # Get the network from the input.
        network = self._get_network(input)
        
        if network is not None:
            # Pass network to the routine.
            r = self._get_routine(self.routine, network)

            if r is None:
                logger.critical("Unrecognised routine type.")
                return False

            # Run the routine.
            success = r.solve()

            # Solution output.
            writer = None
            if self.output_type == "matpower":
                writer = MATPOWERWriter(network, output)
            elif self.output_type == "rst":
                writer = ReSTWriter(network, output)
            elif self.output_type == "csv":
                writer = CSVWriter(network, output)
            elif self.output_type == "excel":
                writer = ExcelWriter(network, output)
            else:
                logger.critical("Unrecognised output type")
                return False

            # Write the solution.
            if writer is not None:
                writer.write()
                
            return True
        else:
            logger.critical("Unrecognised data file.")
            return False


    def _get_network(self, input):
        """ Returns the network from the input.
        """
        type    = self.type
        network = None

        if type == "any":
            type = detect_network_type(input, self.file_name)

        if type == "matpower":
            network = read_matpower(input)

        elif type == "psat":
            network = read_psat(input)

        elif type == "psse":
            network = read_psse(input)

        elif type == "matlab":
            # MATPOWER or PSAT data file.
            network = read_matpower(input)
            if network is None:
                network = read_psat(input)
            if network is None:
                network = input.read()

        elif type == "unrecognised":
            # Try all filters.
            network = read_matpower(input)
            if network is None:
                network = read_psat(input)
            if network is None:
                network = read_psse(input)
            if network is None:
                network = input.read()
        else:
            network = input.read()

        return network


    def _get_routine(self, routine, network):
        """ Returns the routine to which to pass the network.
        """
        if routine == "dcpf":
            r = DCPFRoutine(network)
        elif routine == "acpf":
            if self.algorithm == "newton":
                r = NewtonPFRoutine(network)
            elif self.algorithm == "decoupled":
                r = FastDecoupledPFRoutine(network)
            else:
                r = None
        elif routine == "dcopf":
            r = DCOPFRoutine(network)
        elif routine == "acopf":
            r = ACOPFRoutine(network)
        else:
            r = None
        return r

#------------------------------------------------------------------------------
#  "main" function:
#------------------------------------------------------------------------------

def main():
    """ Parse command line and call Pylon with the correct data.
    """    
    parser = OptionParser("usage: pylon [options] input_file")

    parser.add_option("-o", "--output", dest="output", metavar="FILE",
        help="Write the solution report to FILE.")

    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
        default=False, help="Print less information.")

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        default=False, help="Print debug information.")

    parser.add_option("-n", "--no-report", action="store_true",
        dest="no_report", default=False, help="Suppress report output.")

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
        default=False, help="Print debug information.")

    parser.add_option("-t", "--input-type", dest="type", metavar="TYPE",
        default="any", help="The argument following the -t is used to "
        "indicate the format type of the input data file. The types which are "
        "currently supported include: matpower, psat, psse.  If not "
        "specified Pylon will try to determine the type according to the "
        "file name extension and the file header.")

    parser.add_option("-r", "--routine", dest="routine", metavar="ROUTINE",
        default="acpf", help="The argument following the -r is used to"
        "indicate the type of routine to use in solving. The types which are "
        "currently supported include: 'dcpf', 'acpf', 'dcopf', 'acopf'.")

    parser.add_option("-a", "--algorithm", action="store_true",
        metavar="ALGORITHM", dest="algorithm", default="newton",
        help="Indicates the algorithm type to be used for AC power flow. The "
        "types which are currently supported are: 'newton' and 'decoupled'.")

    parser.add_option("-T", "--output-type", dest="otype",
        metavar="OUTPUT_TYPE", default="rst", help="Indicates the output "
        "format type.  The type swhich are currently supported include: rst, "
        "matpower, csv and excel.")

    (options, args) = parser.parse_args()

    if options.quiet:
        logger.setLevel(logging.CRITICAL)
    elif options.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Output.
    if options.output:
        outfile = options.output
        if outfile == "-":
            outfile = sys.stdout
            logger.setLevel(logging.CRITICAL) # we must stay quiet

    else:
        outfile = sys.stdout
        if not options.no_report:
            logger.setLevel(logging.CRITICAL) # we must stay quiet

    # Input.
    if len(args) > 1:
        parser.print_help()
        sys.exit(1)
        
    elif len(args) == 0 or args[0] == "-":
        filename = ""
        print "IS A TTY:", sys.stdin.isatty()
        if sys.stdin.isatty():
            # True if the file is connected to a tty device, and False
            # otherwise (pipeline or file redirection).
            parser.print_help()
            sys.exit(1)
        else:
            # Handle piped input ($ cat ehv3.raw | pylon | rst2pdf -o ans.pdf).
            infile = sys.stdin

    else:
        filename = args[0]
        infile   = open(filename)

    print "OPTIONS:", options

    app = PylonApplication(file_name   = filename,
                           type        = options.type,
                           routine     = options.routine,
                           algorithm   = options.algorithm,
                           output_type = options.otype)

    app.solve(input=infile, output=outfile)

    try:
        infile.close() # Clean-up
    except:
        pass

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
