#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" For solving networks """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import sys
import logging
from optparse import OptionParser

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "main" function:
#------------------------------------------------------------------------------

def main():
    """ Parse command line and call run_pf() with the correct data """

    parser = OptionParser()
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

    parser.add_option("-t", "--type", dest="type", metavar="TYPE",
        default="any", help="The argument following the -t is used to "
        "indicate the format type of the input data file. The types which are "
        "currently supported include: matpower, psat, psse, m3.  If not "
        "specified Pylon will try to determine the type according to the "
        "file name extension and the file header.")

    parser.add_option("-r", "--routine", dest="routine", metavar="ROUTINE",
        default="pf", help="The argument following the -r is used to"
        "indicate the type of routine to use in solving. The types which are "
        "currently supported include: pf, opf.")

#    parser.add_option("-f", "--formulation", action="store_true",
#        dest="formulation", default="ac", help="Indicates the algorithm"
#        "formulation type to be used.  The types which are currently "
#        "supported include: dc and ac.")

    parser.add_option("-a", "--algorithm", action="store_true",
        dest="algorithm", default="newton", help="Indicates the algorithm "
    "type to be used.  The types which are currently supported include: "
    "newton, gauss, decoupled.")

    parser.add_option("-p", "--paginate", action="store_true", default=False,
        help="Pipe all output into less (or if set, $PAGER).")

    parser.add_option("-h", "--help", dest="help", default=False,
        help="Prints the synopsis and a list of the commands.")

    parser.add_option("-V", "--version", dest="version", default=False,
        help="Output version.")

    (options,args)=parser.parse_args()

    if options.quiet:
        logger.setLevel(logging.CRITICAL)
    elif options.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    filename = False

    if len(args) == 0 or args[0]=="-":
        infile = sys.stdin
    elif len(args) > 1:
        logger.critical("Usage: %s file.txt [ -o file.rst ] "
            "[ -r dcpf|acpf|dcopf|acopf ] [ -t matpower|psat|psse ]",
            sys.argv[0]
        )
        sys.exit(1)
    else:
        filename = args[0]
        infile=open(filename)

    if options.output:
        outfile=options.output
        if outfile == "-":
            outfile = sys.stdout
            logger.setLevel(logging.CRITICAL) # we must stay quiet
    else:
        outfile = sys.stdout
        if not options.no_report:
            log.setLevel(logging.CRITICAL) # we must stay quiet


    pylon = Pylon(forulation=options.formulation, algorithm=options.alg)
    pylon.solve(text=infile.read(), output=outfile)

if __name__ == "__main__":
    main()

# EOF -------------------------------------------------------------------------
