# #!/usr/bin/python
from lxml import etree
import sys
import os
import rdflib
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF
from rdflib import Namespace
import pprint
from coorsFromVocabs import coorsFromVocabs
from rdflib import *
from rdflib import plugin
from rdflib import serializer
from rdflib import parser
from rdflib import Graph, plugin
from rdflib.serializer import Serializer

class SchemaTest():
    # Input parameters
    tree = None
    # May change as additional file options get entered into the mix
    namespaces = {}

    def testing(self, vocab_dict, inputfile, this_file_type):
        print "...reaching testing.py module..."
        # Parse Model Instance
        if this_file_type == "gbxml":
            self.namespaces = {'gb': "http://www.gbxml.org/schema"}
            tree = etree.parse(inputfile)
        elif this_file_type == "ifcxml":
            self.namespaces = {'ifc': "http://www.buildingsmart-tech.org/ifc"}
            tree = etree.parse(inputfile)
        elif this_file_type == "citygml":
            self.namespaces = {'city': "http://www.citygml.org/index.php?id=1540"}
            tree = etree.parse(inputfile)
        else:
            print "File Type not yet handled for initial parsing..."
            return

        root = tree.getroot()
        print "XML Tree Namespace Parsing"
        if "}" in str(root.tag):
            #print "root.tag: ", root.tag
            new_ifc_link1 = str(root.tag).split("}")[0]
            new_ifc_link = new_ifc_link1.split("{")[1]
            self.namespaces['doc'] = str(new_ifc_link)
        for child_of_root in root:
            #print "child_of_root...", child_of_root.attrib
            if "}" in str(child_of_root.tag):
                new_ifc_link1 = str(child_of_root.tag).split("}")[0]
                new_ifc_link = new_ifc_link1.split("{")[1]
                new_ifc = str(child_of_root.tag).split("}")[1]
                self.namespaces[str(new_ifc)] = str(new_ifc_link)
                if str(new_ifc) == "uos":
                    self.namespaces['ifc'] = str( new_ifc_link)
        #print "rrr", root.attributes["xmlns:exp"] #pause for now


        this_root = str(root.tag).split("}")[1]
        top_root = "/doc:" + this_root + "/ifc:uos"
        print "top_root", top_root
        for i in self.namespaces:
            print i, self.namespaces[i]


        spatial_piece = tree.xpath(top_root, namespaces=self.namespaces)
        for piece in spatial_piece:
            #this_piece_data = float(piece.text)
            att = "id"
            curr_attribute_data = piece.get(att)
            print "Making triple with: ", curr_attribute_data, piece  #, this_piece_data


