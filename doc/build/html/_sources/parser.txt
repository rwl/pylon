.. _parser:

*******
Parsers
*******

Pylon uses Pyparsing_ to parse power system data files.  The MATPOWER parser is
the most robust as it is used in test cases for the routines.  Parsers are
also available for:

* PSS/E raw files and
* PSAT_ .m files.

========
MATPOWER
========

Simply::

    >>> from pylon.readwrite.api import read_matpower
    >>> network = read_matpower('/path/to/casefile.m')

The parser class is in the API also::

    >>> from pylon.readwrite.api import MATPOWERReader
    >>> reader = MATPOWERReader('/path/to/casefile.m')
    >>> network = reader.network
    >>> network2 = reader.parse_file('/path/to/casefile2.m')

=========
PTI PSS/E
=========

The PSS/E parser is tested with RAW files from the UKGDS_ project::

    >>> from pylon.readwrite.api import read_psse
    >>> network = read_psse('ehv3.raw')

===========
CIM RDF/XML
===========

Pylon includes a parser for RDF/XML files with Common Information Model data. 
The parser builds a ``Model`` object with a list of instances of the classes
available in the ``CIM13`` package.  ``Model`` is not yet compatible with any
of the routines.

The parser can accept XML, Zip, Gzip and bzip2 files::

    >>> from pylon.readwrite.cim_reader import CIMReader
    >>> reader = CIMReader('/path/to/data.xml')
    >>> model = reader.parse_file()
    >>> model2 = reader.parse_file('/path/to/data.gz')

.. include:: ../links_names.txt
