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

""" Defines a reader for RDF/XML files with CIM data.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import gzip
import bz2
import zipfile

from os.path import basename, exists, splitext

from enthought.traits.api import Str, Int, Float, Bool, Instance, List

#from rdflib.Graph import ConjunctiveGraph
#from rdflib.Namespace import Namespace
#from rdflib import RDF

from CIM13 import Model
from CIM13.Core import Terminal
from CIM13.LoadModel import Load
from CIM13.Generation.Production import GeneratingUnit

import rdfxml

ns_cim = rdfxml.Namespace("http://iec.ch/TC57/2009/CIM-schema-cim14#")

#------------------------------------------------------------------------------
#  Split fragment from an URI:
#------------------------------------------------------------------------------

def split_uri(uri):
    """ Splits the fragment from an URI and returns a tuple.

        For example:
            <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
        returns:
            ('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'type')

            http://www.github.com/rwl/pylon
        returns:
            (http://www.github.com/rwl/pylon, "")
    """
    if (uri[0] == "<") and (uri[-1] == ">"):
        uri = uri[1:-1]

    head, sep, tail = uri.rpartition("#")
    if head and sep:
        print "PARTIONING:", (head + sep, tail)
        return (head + sep, tail)
    else:
        print "NOT PARTITIONING:", (tail, "")
        return (tail, "")

#------------------------------------------------------------------------------
#  "CIMAttributeSink" class:
#------------------------------------------------------------------------------

class CIMAttributeSink:
    """ Uses triples from the RDF parser to populate a dictionary that maps
        rdf:IDs to objects.  The objects are instantiated and their attributes
        are set, but any references are not.  This is done with a second pass
        using a CIMReferenceSink that is passed this sink.
    """

    def __init__(self):
        self.uri_object_map = {}

    def triple(self, sub, pred, obj):
        """ Handles triples from the RDF parser.
        """
        print "%s %s %s" % (sub, pred, obj)

        ns_sub, frag_sub = split_uri(sub)
        ns_pred, frag_pred = split_uri(pred)
        ns_obj, frag_obj = split_uri(obj)

        # Instantiate an object if the preicate is an RDF type and the object
        # is in the CIM namespace.
        if (ns_pred == rdfxml.rdf) and (frag_pred == "type") and \
            (ns_obj == ns_cim):

            cls_name = frag_obj
#            print "CLASS:", cls_name
            uri = frag_sub
#            print "URI:", uri

            try:
                klass = eval( cls_name )
            except NameError:
                print "FAILED TO IMPORT:", cls_name
                return

            element = klass(URI=uri)
            self.uri_object_map[uri] = element

        # Set object attributes.
        elif ns_pred == ns_cim:
            uri = frag_sub
            value = ns_obj

            # Split the class name and the attribute name.
            class_name, attr_name = frag_pred.rsplit(".", 1)

            try:
                obj = self.uri_object_map[uri]
            except KeyError:
                print "Object not found:", uri
                return

            trait = obj.trait( attr_name )
            if trait is None:
                print "ATTRIBUTE NOT FOUND:", class_name, attr_name
                return

            # Strip the double quotes that rdfxml adds to literals.
            value = value.strip('"')

            # Stitch together references later.
            if trait.is_trait_type( Instance ):
                return

            elif trait.is_trait_type( List ):
                # One to many and many to many references (List(Instance)).
                if trait.inner_traits[0].is_trait_type( Instance ):
                    return
                else:
                    value = list( frag_obj )

            if trait.is_trait_type( Int ):
                print "INT:", value
                value = int( value )

            elif trait.is_trait_type( Float ):
                print "FLOAT:", value, type(value)
                value = float( value )

            elif trait.is_trait_type( Bool ):
                print "BOOL:", value
                value = bool( value )

            else:
                value = value

            setattr(obj, attr_name, value)

#------------------------------------------------------------------------------
#  "CIMReferenceSink" class:
#------------------------------------------------------------------------------

class CIMReferenceSink:
    """ Handles setting the references for a CIM.
    """

    def __init__(self, attr_sink):
        assert isinstance(attr_sink, CIMAttributeSink)

        self.attr_sink = attr_sink
        self.model = Model()

    def triple(self, sub, pred, obj):
        """ Handles triples from the RDF parser.
        """
        ns_pred, frag_pred = split_uri(pred)

        # Set object references.
        if ns_pred == ns_cim:
            ns_sub, uri_subject = split_uri(sub)

            # Try to get the object with the reference being set.
            try:
                sub_obj = self.attr_sink.uri_object_map[uri_subject]
            except KeyError:
                print "SUBJECT OBJECT NOT FOUND:", uri_subject
                return

            # Split the predicate fragment into class name and attribute name.
            class_name, attr_name = frag_pred.rsplit(".", 1)
            # Assert that the object from the dictionary has the same type as
            # that specified in the predicate.
#            assert sub_obj.__class__.__name__ == class_name

            # Get the attribute object so the type can be determined.
            trait = sub_obj.trait( attr_name )
            if trait is None:
                print "TRAIT NOT FOUND:", class_name, attr_name
                return

            # Set reference traits.
            if trait.is_trait_type( Instance ):
                ns_obj, obj_uri = split_uri(obj)
                # Try to get the object being referenced.
                try:
                    obj_obj = self.attr_sink.uri_object_map[obj_uri]
                except KeyError:
                    print "OBJECT OBJECT NOT FOUND:", obj
                    return

                setattr(sub_obj, attr_name, obj_obj)

            # One to many and many to many references (List(Instance)).
            elif trait.is_trait_type( List ) and \
                trait.inner_traits[0].is_trait_type( Instance ):

                raise NotImplementedError

#------------------------------------------------------------------------------
#  "CIMReader" class:
#------------------------------------------------------------------------------

class CIMReader:
    """ Reads RDF/XML files with CIM data.
    """

    filename = ""

    model = None

    def __init__(self, filename):
        self.filename = filename


    def parse_file(self, filename=None, pwd=None):
        """ Parses an RDF/XML file and returns a model containing CIM elements.

            pwd is the password used for encrypted files.
        """
        filename = filename or self.filename
        assert exists(filename)

        # Split the extension from the pathname
        root, extension = splitext( filename )

        if isinstance(file_or_filename, file):
            s = file_or_filename.read()

        if extension == ".xml":
            fd = None
            try:
                fd = open(filename, "rb")
                s = fd.read()
            finally:
                if fd is not None:
                    fd.close()

        elif zipfile.is_zipfile(filename):
            zipdatafile = None
            try:
                zipdatafile = zipfile.ZipFile(filename)
                member_names = zipdatafile.namelist()
                if member_names:
                    member_name = member_names[0]
                else:
                    print "Zip file contains no members."
                    return

                # FIXME: Perhaps extract to a temporary directory.
                zipextdatafile = zipdatafile.open( member_name, "rb", pwd )
                s = zipextdatafile.read()
                zipextdatafile.close()
            finally:
                if zipdatafile is not None:
                    zipdatafile.close()

        elif extension == ".gz":
            fd = None
            try:
                fd = gzip.open(filename, "rb")
                s = f.read()
            finally:
                if fd is not None:
                    fd.close()

        elif extension == ".bz2":
            bz2datafile = None
            try:
                bz2file = bz2.BZ2File( filename )
                s = bz2file.read()
            finally:
                if bz2datafile is not None:
                    bz2datafile.close()

        # Instantiate CIM objects and set their attributes.
        attr_sink = CIMAttributeSink()
#        rdfxml.parseURI(filename, sink=attr_sink)
        rdfxml.parseRDF(s, base=filename, sink=attr_sink)

        # Second pass to set references.
        ref_sink = CIMReferenceSink(attr_sink)
#        rdfxml.parseURI(filename, sink=ref_sink)
        rdfxml.parseRDF(s, base=filename, sink=ref_sink)

        return Model( Contains = attr_sink.uri_object_map.values() )

#------------------------------------------------------------------------------
#  "CIMReader2" class:
#------------------------------------------------------------------------------

#class CIMReader2:
#    """ Reads RDF/XML files with CIM data.
#    """
#
#    filename = ""
#
#    model = None
#
#    def __init__(self, filename):
#        self.filename = filename
#
#
#    def parse_file(self, filename=None):
#        """ Parses an RDF/XML file and returns a model containing CIM elements.
#        """
#        filename = filename or self.filename
#
#        for obj in sink._uri_object_map.values():
#            obj.configure_traits()
#
#
#        if isinstance(file_or_filename, basestring):
#            file = open(file_or_filename, "wb")
#        else:
#            file = file_or_filename
#
#        ns_cim = Namespace("http://iec.ch/TC57/2009/CIM-schema-cim14#")
#        ns_ngt = Namespace("http://com.ngtuk/2005/NGT-schema-cim11#")
#
#        store = ConjunctiveGraph()
#
#        context = store.parse(filename)
#        print context.identifier
#        print dir(context)
#
#        for subject, predicate, object in store:
#            print "SUBJECT:", subject
#            print "PREDICATE:", predicate
#            print "OBJECT:", object
#
#        for s, o in store.subject_objects(ns_rdf["type"]):
#            print "NAME:", o
#
#        for s in store.subjects(RDF.type, ns_cim["GeneratingUnit"]):
#            print "SUBJECT:", type(s), s
#            unit = GeneratingUnit()
#
#            for p, o in store.predicate_objects(s):
#                print "PREDICATE:", type(p), p
#                print "OBJECT:", type(o), o
#
#            for obj in store.objects(s, ns_cim["GeneratingUnit.nominalP"]):
#                print "OBJ:", obj

#------------------------------------------------------------------------------
#  Function for reading CIM RDF/XML files:
#------------------------------------------------------------------------------

def read_cim(filename):
    """ Function for import of CIM RDF/XML data files given the file path.
    """
    return CIMReader(filename).parse_file()

# EOF -------------------------------------------------------------------------
