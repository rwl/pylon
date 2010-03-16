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

""" Defines the entry point for Pylon.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import os
import sys
import logging
import optparse

from pylon.readwrite import MATPOWERReader, PSSEReader, PSATReader, \
    MATPOWERWriter, ReSTWriter, CSVWriter, PickleReader, PickleWriter

from pylon import DCPF, NewtonPF, FastDecoupledPF, OPF, UDOPF

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
    format="%(levelname)s: %(message)s")

logger = logging.getLogger("pylon")

#------------------------------------------------------------------------------
#  Read data file:
#------------------------------------------------------------------------------

def read_case(input, format=None):
    """ Returns a case object from the given input file object. The data
        format may be optionally specified.
    """
    # Map of data file types to readers.
    format_map = {"matpower": MATPOWERReader, "psat": PSATReader,
        "psse": PSSEReader, "pickle": PickleReader}

    # Read case data.
    if format_map.has_key(format):
        reader_klass = format_map[format]
        reader = reader_klass()
        case = reader.read(input)
    else:
        # Try each of the readers at random.
        for reader_klass in format_map.values():
            reader = reader_klass()
            try:
                case = reader.read(input)
                if case is not None:
                    break
            except:
                pass
        else:
            case = None

    return case

#------------------------------------------------------------------------------
#  Format detection:
#------------------------------------------------------------------------------

def detect_data_file(input, file_name=""):
    """ Detects the format of a network data file according to the
        file extension and the header.
    """
    _, ext = os.path.splitext(file_name)

    if ext == ".m":
        line = input.readline() # first line
        if line.startswith("function"):
            type = "matpower"
            logger.info("Recognised MATPOWER data file.")
        elif line.startswith("Bus.con" or line.startswith("%")):
            type = "psat"
            logger.info("Recognised PSAT data file.")
        else:
            type = "unrecognised"
        input.seek(0) # reset buffer for parsing

    elif (ext == ".raw") or (ext == ".psse"):
        type = "psse"
        logger.info("Recognised PSS/E data file.")

    elif (ext == ".pkl") or (ext == ".pickle"):
        type = "pickle"
        logger.info("Recognised pickled case.")

    else:
        type = None

    return type

#------------------------------------------------------------------------------
#  "main" function:
#------------------------------------------------------------------------------

def main():
    """ Parses the command line and call Pylon with the correct data.
    """
    parser = optparse.OptionParser(usage="usage: pylon [options] input_file",
                                   version="%prog 0.3.3")

    parser.add_option("-o", "--output", dest="output", metavar="FILE",
        help="Write the solution report to FILE.")

    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
        default=False, help="Print less information.")

#    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
#        default=False, help="Print debug information.")

#    parser.add_option("-g", "--gui", action="store_true", dest="gui",
#        default=False, help="Use the portable graphical interface to Pylon.")

    parser.add_option("-n", "--no-report", action="store_true",
        dest="no_report", default=False, help="Suppress report output.")

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
        default=False, help="Print debug information.")

    parser.add_option("-t", "--input-type", dest="type", metavar="TYPE",
        default="any", help="The argument following the -t is used to "
        "indicate the format type of the input data file. The types which are "
        "currently supported include: matpower, psat, psse [default: %default]"
        " If not specified Pylon will try to determine the type according to "
        "the file name extension and the file header.")

    parser.add_option("-s", "--solver", dest="solver", metavar="SOLVER",
        default="acpf", help="The argument following the -s is used to"
        "indicate the type of routine to use in solving. The types which are "
        "currently supported are: 'dcpf', 'acpf', 'dcopf', 'acopf', 'udopf' "
        "and 'none' [default: %default].")

    parser.add_option("-a", "--algorithm", action="store_true",
        metavar="ALGORITHM", dest="algorithm", default="newton",
        help="Indicates the algorithm type to be used for AC power flow. The "
        "types which are currently supported are: 'newton' and 'fdpf' "
        "[default: %default].")

    parser.add_option("-T", "--output-type", dest="output_type",
        metavar="OUTPUT_TYPE", default="rst", help="Indicates the output "
        "format type.  The type swhich are currently supported include: rst, "
        "matpower, csv and excel [default: %default].")

    (options, args) = parser.parse_args()

    if options.quiet:
        logger.setLevel(logging.CRITICAL)
    elif options.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Output.
    if options.output:
        if options.output == "-":
            outfile = sys.stdout
            logger.setLevel(logging.CRITICAL) # must stay quiet
        else:
            outfile = open(options.output, "wb")
    else:
        outfile = sys.stdout
#        if not options.no_report:
#            logger.setLevel(logging.CRITICAL) # must stay quiet

    # Input.
    if len(args) > 1:
        parser.print_help()
        sys.exit(1)
    elif (len(args) == 0) or (args[0] == "-"):
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
        infile = open(filename, "rb")

    if options.type == "any":
        type = detect_data_file(infile, filename)
    else:
        type = options.type

    # Get the case from the input file-like object.
    case = read_case(infile, type)

    if case is not None:
        # Routine (and algorithm) selection.
        if options.solver == "dcpf":
            solver = DCPF(case)
        elif options.solver == "acpf":
            if options.algorithm == "newton":
                solver = NewtonPF(case)
            elif options.algorithm == "fdpf":
                solver = FastDecoupledPF(case)
            else:
                logger.critical("Invalid algorithm [%s]." % options.algorithm)
                sys.exit(1)
        elif options.solver == "dcopf":
            solver = OPF(case, True)
        elif options.solver == "acopf":
            solver = OPF(case, False)
        elif options.solver == "udopf":
            solver = UDOPF(case)
        else:
            logger.critical("Invalid solver [%s]." % options.solver)
            sys.exit(1)

        # Output writer selection.
        if options.output_type == "matpower":
            writer = MATPOWERWriter(case)
        elif options.output_type == "rst":
            writer = ReSTWriter(case)
        elif options.output_type == "csv":
            writer = CSVWriter(case)
        elif options.output_type == "excel":
            from pylon.readwrite.excel_writer import ExcelWriter
            writer = ExcelWriter(case)
        elif options.output_type == "pickle":
            writer = PickleWriter(case)
        else:
            logger.critical("Invalid output type [%s]." % options.output_type)
            sys.exit(1)

        solver.solve()
        if not options.no_report:
            writer.write(outfile)
    else:
        logger.critical("Unable to read case data.")

    # Don't close stdin or stdout.
    if len(args) == 1:
        infile.close()
    if options.output and not (options.output == "-"):
        outfile.close()

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
