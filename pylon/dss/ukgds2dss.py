#------------------------------------------------------------------------------
#  Copyright (c) 2008 Richard W. Lincoln
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#------------------------------------------------------------------------------

""" Defines a parser for extracting network data stored according to the United
    Kingdom Generic Distribution System (UKGDS) format in an Excel spreadsheet.

    @see: Foote C., Djapic P,. Ault G., Mutale J., Burt G., Strbac G., "United
    Kingdom Generic Distribution System (UKGDS) Software Tools", The Centre for
    Distributed Generation and Sustainable Electrical Energy, February 2006
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

# Operating system routines.
import os

# Python "xlrd" package for extracting data from Excel files.
import xlrd

#------------------------------------------------------------------------------
#  "ukgds2dss" function:
#------------------------------------------------------------------------------

def ukgds2dss(infile, outfile):
    """ Extracts UKGDS data from an Excel spreadsheet and write it to a text
        file in OpenDSS format.
    """

    # Check that the path to the inputfile is valid.
    if not os.path.isfile(infile):
        raise NameError, "%s is not a valid filename" % infile

    # Open the Excel workbook.
    book = xlrd.open_workbook(infile)

    # String to be extended with OpenDSS format data and written to file.
    s = ""

    # Expected spreadsheet names in the Excel workbook.
    sheet_names = ["System", "Buses", "Loads", "Generators", "Transformers",
        "IndGenerators", "Shunts", "Branches", "Taps"]

    # Provide warning if an expected sheet is not found in the workbook.
    # Ignore case for comparison.
    lower_names = [name.lower() for name in book.sheet_names()]
    for sheet_name in sheet_names:
        if sheet_name.lower() not in lower_names:
            print "Sheet named '%s' not found." % sheet_name

    # System sheet ------------------------------------------------------------

    # Only proceed if the "System" sheet exists in the workbook.
    if "system" in lower_names:

        # Get the individual spreadsheet from the workbook.
        sys_sheet = book.sheet_by_name("System")
        system_data = {}

        # Loop through the rows of the spreadsheet starting at row 30.
        for row_idx in range(29, sys_sheet.nrows):
            # Coerce and format row values according to type.
            pretty_values = get_row_values(sys_sheet, row_idx)

            symbols = ['smb', 'std', 'ssb', 'spt']
            # Dictionary mapping symbols to values (Skip first column).
            # @see: http://en.wikibooks.org/wiki/Python_Programming/Dictionaries
            system_data[symbols[row_idx-29]] = pretty_values[2]

        s += "! %s\n" % system_data["std"]
        s += "new object=circuit.%s\n" % "name" # FIXME: Circuit name.
        s += "~ basekv=%.3f" % system_data["smb"]
        s += "\n\n"


    # Branch sheet ------------------------------------------------------------

    if "branches" in lower_names:
        # Get the individual spreadsheet from the workbook.
        branch_sheet = book.sheet_by_name("Branches")

        for row_idx in range(29, branch_sheet.nrows):
            # Coerce and format row values according to type.
            pretty_values = get_row_values(branch_sheet, row_idx)
            # Column symbols as defined on row 29 of the spreadsheet.
            symbols = ['cfb', 'ctb', 'cid', 'cr1', 'cx1', 'cb1', 'cr0', 'cx0',
                'cb0', 'cm1', 'cm2', 'cm3', 'cle', 'cst']
            branch_data = dict(zip(symbols, pretty_values[1:]))

            s += "New Line.L%d " % (row_idx-29)
            s += "Bus1=%d Bus2=%d " % (branch_data["cfb"], branch_data["ctb"])
            s += "R1=%.3f X1=%.3f " % (branch_data["cr1"], branch_data["cx1"])
            s += "C1=%.3f R0=%.3f " % (branch_data["cb1"], branch_data["cr0"])
            s += "X0=%.3f C0=%.3f " % (branch_data["cx0"], branch_data["cb0"])
            s += "Emergamps=%.3f " % branch_data["cm1"] # FIXME: Line ratings
            s += "Length=%.3f Units=km" % branch_data["cle"]
            s += "\n" # New line.
        else:
            s += "\n"


    # Bus sheet ---------------------------------------------------------------

    if "buses" in lower_names:
        # OpenDSS has no Bus class so we build a dictionary for later use.
        buses_data = {}

        bus_sheet = book.sheet_by_name("Buses")
        for row_idx in range(29, bus_sheet.nrows):
            # Coerce and format row values according to type.
            pretty_values = get_row_values(bus_sheet, row_idx)
            # Column symbols as defined on row 29 of the spreadsheet.
            symbols = ["bnu", "bna", "bxc", "byc", "bbv", "bty", "bst", "btv",
                "bvn", "bvx", "bva"]
            bus_data = dict(zip(symbols, pretty_values[1:]))

            # Map buses according to their number.
            buses_data[bus_data["bnu"]] = bus_data


    # Transformer sheet -------------------------------------------------------

    if "transformers" in lower_names:
        # Get the individual spreadsheet from the workbook.
        tx_sheet = book.sheet_by_name("Transformers")

        for row_idx in range(29, tx_sheet.nrows):
            # Coerce and format row values according to type.
            pretty_values = get_row_values(tx_sheet, row_idx)
            # Column symbols as defined on row 29 of the spreadsheet.
            symbols = ['tfb', 'ttb', 'tid', 'tr1', 'tx1', 'tr0', 'tx0', 'tre',
                'txe', 'til', 'tmc', 'tm1', 'tm2', 'tm3', 'tst', 'ttr', 'ttx',
                'ttn', 'ttp', 'twc', 'tps', 'tcb']
            tx_data = dict(zip(symbols, pretty_values[1:]))

            fbus_data = buses_data[tx_data["tfb"]]
            tbus_data = buses_data[tx_data["ttb"]]

            s += "New Transformer.T%d" % (row_idx-29)
            s += "\n"

            s += "~ wdg=1 bus=%d conn=Delta " % tx_data["tfb"]
            s += "kv=%.3f kva=%.3f " % (fbus_data["bbv"], tx_data["tm1"]/1000)
            s += "tap=%.2f " % tx_data["ttr"]
            s += "\n"

            s += "~ wdg=2 bus=%d conn=Wye " % tx_data["ttb"]
            s += "kv=%.3f kva=%.3f " % (tbus_data["bbv"], tx_data["tm2"]/1000)
            s += "tap=%.2f " % tx_data["ttr"]
            s += "\n"
        else:
            s += "\n"


    # Generator sheet ---------------------------------------------------------

    if "generators" in lower_names:
        # Get the individual spreadsheet from the workbook.
        gen_sheet = book.sheet_by_name("Generators")

        for row_idx in range(29, gen_sheet.nrows):
            pretty_values = get_row_values(gen_sheet, row_idx)
            symbols = ['gbn', 'gid', 'gpo', 'gpx', 'gpn', 'gqa', 'gqx', 'gqn',
                'gty', 'gst', 'gcb', 'gmb', 'gr1', 'gx1', 'gr0', 'gx0']
            gen_data = dict(zip(symbols, pretty_values[1:]))

            bus_data = buses_data[gen_data["gbn"]]

            s += "New Generator.G%d " % (row_idx-29)
            s += "bus1=%d kv=%.3f " % (gen_data["gbn"], bus_data["bbv"])
            s += "\n"
        else:
            s += "\n"


    # Load sheet --------------------------------------------------------------

    if "loads" in lower_names:
        # Get the individual spreadsheet from the workbook.
        load_sheet = book.sheet_by_name("Loads")

        for row_idx in range(29, load_sheet.nrows):
            pretty_values = get_row_values(load_sheet, row_idx)
            symbols = ["lbn", "lid", "lpo", "lqa", "lty", "lst"]
            load_data = dict(zip(symbols, pretty_values[1:]))

    #        print "LOAD:", load_data

            bus_data = buses_data[load_data["lbn"]]

            s += "New Load.L%d " % (row_idx-29)
            s += "bus1=%d kv=%.3f " % (load_data["lbn"], bus_data["bbv"])
            s += "kw=%.3f kvar=%.3f " % (load_data["lpo"], load_data["lqa"])
            s += "\n"
        else:
            s += "\n"


    # Shunt sheet -------------------------------------------------------------

    if "shunts" in lower_names:
        shunt_sheet = book.sheet_by_name("Shunts")
        for row_idx in range(29, shunt_sheet.nrows):
            pretty_values = get_row_values(shunt_sheet, row_idx)
            symbols = ["shb", "shi", "shr", "shx", "shs"]
            shunt_data = dict(zip(symbols, pretty_values[1:]))

#            print "SHUNT:", shunt_data

    #--------------------------------------------------------------------------
    #  Write the text to the output file:
    #--------------------------------------------------------------------------

    fd = None
    try:
        fd = open(outfile, "wb")
        fd.write(s)
#    except:
#        print "An error was encountered writing to the OpenDSS file."
    finally:
        if fd is not None:
            fd.close()

#------------------------------------------------------------------------------
#  Coerce and format row values according to their type:
#------------------------------------------------------------------------------

#def format_row(types, values):
def get_row_values(sheet, row_idx):
    """ Coerces and formats row values according to their type. """

    # Data types for each cell in the row. @see: format_row() below.
    types = sheet.row_types(row_idx)
    # Values for each cell in the row.
    values = sheet.row_values(row_idx)

    # Quick sanity check for input arguments.
    if len(types) != len(values):
        raise ValueError, "Length of 'type' and 'value' not equal."

    # Coerce and formet values accordingly.
    return_row = []
    for i, value in enumerate(values):

        # Mapping of codes used by xlrd to types.
        type_codes = {0: "empty", 1: "str", 2: "float", 3: "date",
            4: "bool", 5: "error"}

        # The type associated with the value.
        value_type = type_codes[types[i]]

        # Coerce float value types.
        if value_type is "float":
            # Coerce to integers.
            if value == int(value):
                value = int(value)

        # Format dates as a tuple.
        elif value_type is "date":
            value = xlrd.xldate_as_tuple(value, book.datemode)

        # Extract error text.
        elif value_type is "error":
            value = xlrd.error_text_from_code[value]

        return_row.append(value)

    return return_row

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    # Define the path to the Excel input file.
    UKGDS_FILE = "/tmp/ehv3.xls"
    # Define the path to which the output should be written.
    OPENDSS_FILE = "/tmp/ehv3.dss"

    # Call the conversion function.
    ukgds2dss(UKGDS_FILE, OPENDSS_FILE)

# EOF -------------------------------------------------------------------------
