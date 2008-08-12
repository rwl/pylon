#-----------------------------------------------------------------------------
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
#-----------------------------------------------------------------------------

"""
The main function for initialisation and running of Pylon.

"""

#-----------------------------------------------------------------------------
#  Imports:
#-----------------------------------------------------------------------------

import sys
import optparse
import logging
from os.path import join
from tempfile import gettempdir

from pylon.api import Network
from pylon.filter.api import MATPOWERImporter, PSSEImporter
from pylon.ui.model_view.network_mv import NetworkModelView

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger()

logger.addHandler(logging.StreamHandler(sys.stdout))

logger.setLevel(logging.DEBUG)

#-----------------------------------------------------------------------------
#  Usage strings:
#-----------------------------------------------------------------------------

filename_help = """The name (including path) of a file containing a pickled
representation of a NetworkViewModel object. When this parameter
is specified, the method reads the corresponding file (if it
exists) to restore the saved values of the object's traits
before displaying them. If the user confirms the dialog box
(by clicking **OK**), the new values are written to the file.
If this parameter is not specified, the values are loaded from
the in-memory object, and are not persisted when the dialog box
is closed."""

matpower_help = """The path to a MATPOWER network data file.  Refer to the
MATPOWER manual (http://www.pserc.cornell.edu/matpower/manual.pdf) for
further details on this format."""

pti_help = "The path to a PTI PSS/E network data file."

#-----------------------------------------------------------------------------
#  "main" function:
#-----------------------------------------------------------------------------

def main(argv=sys.argv):

    parser = optparse.OptionParser()

    parser.add_option(
        "-f", "--filename",
        dest="filename",
        default=None,
        help=filename_help,
        metavar="FILE"
    )

    parser.add_option(
        "-m", "--matpower",
        dest="matpower",
        default=None,
        help=matpower_help,
        type="str",
    )

    parser.add_option(
        "-p", "--psse",
        dest="psse",
        default=None,
        help=pti_help,
        type="str",
    )

    options, remainder = parser.parse_args()

    # Network importation:
    if options.matpower:
#        filter = MATPOWERImporter(file=options.matpower)
#        n = NetworkViewModel(network=filter.network)
        filter = MATPOWERImporter()
        n = filter.parse_file(options.matpower)
    elif options.psse:
#        filter = PSSEImporter(file=options.psse)
#        n = NetworkViewModel(network=filter.network)
        filter = PSSEImporter()
        n = filter.parse_file(options.psse)
    else:
        #n = NetworkViewModel()
        n= Network()

    # Persistence file:
    if not options.filename:
        filename = join(gettempdir(), "pylon.pkl")
    else:
        filename = options.filename

#    n.configure_traits(
#        filename=filename,
#    )

    model_view = NetworkModelView(model=n)

    model_view.configure_traits(file=filename)

#-----------------------------------------------------------------------------
#  Standalone call:
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF ------------------------------------------------------------------------
