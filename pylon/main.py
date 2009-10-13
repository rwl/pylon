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
import optparse

from pylon.readwrite import MATPOWERReader, PSSEReader, PSATReader, \
    MATPOWERWriter, ReSTWriter, CSVWriter, PickleReader, PickleWriter

from pylon import DCPF, DCOPF, NewtonRaphson, ACOPF, FastDecoupled

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
    format="%(levelname)s: %(message)s")

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "PylonApplication" class:
#------------------------------------------------------------------------------

class PylonApplication(object):
    """ Simulates power systems.
    """

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, file_name="", type="any", routine="acpf",
            algorithm="newton", output_type="rst", gui=False):
        """ Initialises a new PylonApplication instance.
        """
        # Name of the input file.
        self.file_name = file_name
        # Format in which the case is stored.  Possible values are: 'any',
        # 'matpower', 'psat', 'matlab' and 'psse'.
        self.type = type
        # Routine type used to solve the case. Possible values are: 'acpf',
        # 'dcpf', 'acopf' and 'dcopf'.
        self.routine = routine
        # Algorithm to be used in the routine. Possible values are: 'newton'
        # and decoupled
        self.algorithm = algorithm
        # Output format type. Possible values are: 'rst', 'matpower', 'excel'
        # and 'csv'.
        self.output_type = output_type
        # Use the portiable graphical interface to Pylon.
        self.gui = gui

    #--------------------------------------------------------------------------
    #  Runs the application:
    #--------------------------------------------------------------------------

    def __call__(self, input, output):
        """ Forms a case from the input text, obtains a solution using the
            specified routine and writes a report to the output.
        """
        # Get the case from the input.
        case = read_case(input, self.type, self.file_name)

        if case is not None:
            # Portable graphical interface.
            if self.gui:
                from pylon.tk import main
                main(case)
            elif self.routine != "none":
                # Get the routine and pass the case to it.
                routine = self._get_routine(self.routine)

                if routine is None:
                    logger.critical("Unrecognised routine type [%s]." %
                        self.routine)
                    return False

                success = routine(case)

            # Solution output.
            writer = None
            if self.output_type == "matpower":
                writer = MATPOWERWriter()
            elif self.output_type == "rst":
                writer = ReSTWriter()
            elif self.output_type == "csv":
                writer = CSVWriter()
            elif self.output_type == "excel":
                from pylon.readwrite.excel_writer import ExcelWriter
                writer = ExcelWriter()
            elif self.output_type == "pickle":
                writer = PickleWriter()
            else:
                logger.critical("Unrecognised output type")
                return False

            # Write the solution.
            if writer is not None:
                writer(case, output)

            return True
        else:
            logger.critical("Unrecognised data file.")
            return False


    def _get_routine(self, routine):
        """ Returns the routine to which to pass the case.
        """
        if routine == "dcpf":
            r = DCPF()
        elif routine == "acpf":
            if self.algorithm == "newton":
                r = NewtonRaphson()
            elif self.algorithm == "decoupled":
                r = FastDecoupled()
            else:
                r = None
        elif routine == "dcopf":
            r = DCOPF()
        elif routine == "acopf":
            r = ACOPF()
        else:
            r = None

        return r


def read_case(input, type, file_name):
    """ Returns a case object from the given input and file name.
    """
    case = None

    if type == "any":
        type = detect_data_file(input, file_name)

    readers = {"matpower": MATPOWERReader,
               "psat": PSATReader,
               "psse": PSSEReader,
               "pickle": PickleReader}

    # Read case data.
    if readers.has_key(type):
        reader_klass = readers[type]
        reader = reader_klass()
        case = reader(input)
    else:
        for reader_klass in readers.values():
            reader = reader_klass()
            try:
                case = reader(input)
                if case is not None:
                    break
            except:
                pass
        else:
            case = input.read()
            case = None

    return case

#------------------------------------------------------------------------------
#  Format detection:
#------------------------------------------------------------------------------

def detect_data_file(input, file_name=""):
    """ Detects the format of a network data file according to the
        file extension and the header.
    """
    if file_name.endswith(".m"):
        # Read the first line.
        line = input.readline()

        if line.startswith("function"):
            type = "matpower"
            logger.info("Recognised MATPOWER data file.")

        elif line.startswith("Bus.con" or line.startswith("%")):
            type = "psat"
            logger.info("Recognised PSAT data file.")

        else:
            type = "unrecognised"

        # Seek to buffer start for correct parsing.
        input.seek(0)

    elif file_name.endswith((".raw", ".psse")):
        type = "psse"
        logger.info("Recognised PSS/E data file.")

    elif file_name.endswith(".pkl"):
        type = "pickle"
        logger.info("Recognised pickled case.")

    else:
        type = "unrecognised"

    return type

#------------------------------------------------------------------------------
#  "main" function:
#------------------------------------------------------------------------------

def main():
    """ Parses the command line and call Pylon with the correct data.
    """
    parser = optparse.OptionParser("usage: pylon [options] input_file")

    parser.add_option("-o", "--output", dest="output", metavar="FILE",
        help="Write the solution report to FILE.")

    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
        default=False, help="Print less information.")

#    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
#        default=False, help="Print debug information.")

    parser.add_option("-g", "--gui", action="store_true", dest="gui",
        default=False, help="Use the portable graphical interface to Pylon.")

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
        "currently supported are: 'dcpf', 'acpf', 'dcopf', 'acopf' 'none'.")

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

    app = PylonApplication(file_name   = filename,
                           type        = options.type,
                           routine     = options.routine,
                           algorithm   = options.algorithm,
                           output_type = options.otype,
                           gui         = options.gui)

    app(input=infile, output=outfile)

    try:
        infile.close() # Clean-up
    except:
        pass

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
