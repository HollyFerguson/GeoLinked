#-------------------------------------------------------------------------------
# Name:        renest.py
# Purpose:     Renest the JSONLD serialization for better viz.
#              Will need adjusting when cycled graphs start to be used, DAGs are ok for now...
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     04/15/2016
# Copyright:   (c) Holly Tina Ferguson 2016
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------

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
import re

class ReNest():
    # Input parameters
    tree = None
    # May change as additional file options get entered into the mix
    namespaces = {}

    USO_hierarchy_order = ["Property", "SpaceBoundaryElement", "SpaceBoundary", "Space", "SpaceCollection", "SpaceCollectionLocation", "GeoInstance"]
    new_jsonld_file = ""


    def startReNest(self, USO_New, MyLDGraph):
        # Notes
        print "Begin Re-Nesting Triples to Better Visualize:"
        #print USO_New.serialize(format='turtle')
        print MyLDGraph.serialize(format='turtle')
        #print USO_New.serialize(format='json-ld')

        jsonldGraph = USO_New.serialize(format='json-ld')
        jsonld = jsonldGraph.split("},\n  {")
        top = "[\n  {"
        bottom = "}\n]"
        jsonld[0] = jsonld[0][5:]
        jsonld[-1] = jsonld[-1][:-3]
        #for i in jsonld:
        #    print i
        #    print "----------------------------"

        sortingDict = dict()
        new_sortingDict = dict()
        sortingDict["GeoInstance"] = list()
        sortingDict["SpaceCollectionLocation"] = list()
        sortingDict["SpaceCollection"] = list()
        sortingDict["Space"] = list()
        sortingDict["SpaceBoundary"] = list()
        sortingDict["SpaceBoundaryElement"] = list()
        sortingDict["Property"] = list()

        for ld in jsonld:
            #print "1st len(jsonld)", len(jsonld)
            counter = 0
            element_id = ""
            for i in ld:
                if i == '"':
                    counter += 1
                if counter == 3:
                    element_id += i
                if counter == 4:
                    element_id += i
                    counter = 5
                    break
            if ld.startswith('\n    "@id": "http://www.sw.org/UBO#Property'):
                # Add to the sortingDict
                currList = sortingDict["Property"]
                ld_tuple = (element_id, ld)
                currList.append(ld_tuple)
                sortingDict["Property"] = currList
            elif ld.startswith('\n    "@id": "http://www.sw.org/UBO#GeoInstance'):
                currList = sortingDict["GeoInstance"]
                ld_tuple = (element_id, ld)
                currList.append(ld_tuple)
                sortingDict["GeoInstance"] = currList
            elif ld.startswith('\n    "@id": "http://www.sw.org/UBO#SpaceCollectionLocation'):
                currList = sortingDict["SpaceCollectionLocation"]
                ld_tuple = (element_id, ld)
                currList.append(ld_tuple)
                sortingDict["SpaceCollectionLocation"] = currList
            elif ld.startswith('\n    "@id": "http://www.sw.org/UBO#SpaceCollection'):
                currList = sortingDict["SpaceCollection"]
                ld_tuple = (element_id, ld)
                currList.append(ld_tuple)
                sortingDict["SpaceCollection"] = currList
            elif ld.startswith('\n    "@id": "http://www.sw.org/UBO#SpaceBoundaryElement'):
                currList = sortingDict["SpaceBoundaryElement"]
                ld_tuple = (element_id, ld)
                currList.append(ld_tuple)
                sortingDict["SpaceBoundaryElement"] = currList
            elif ld.startswith('\n    "@id": "http://www.sw.org/UBO#SpaceBoundary'):
                currList = sortingDict["SpaceBoundary"]
                ld_tuple = (element_id, ld)
                currList.append(ld_tuple)
                sortingDict["SpaceBoundary"] = currList
            elif ld.startswith('\n    "@id": "http://www.sw.org/UBO#Space'):
                currList = sortingDict["Space"]
                ld_tuple = (element_id, ld)
                currList.append(ld_tuple)
                sortingDict["Space"] = currList
            else:
                print "Starts with something else..."
                print ld

        #for i in sortingDict["SpaceCollection"]:
        #    print i[1]
        #    print "-----------------"

        # Use Sorted Pieces in sortingDict
        # sortingDict now looks like sortingDict[USO element type] = list of tuples: [ (unique element ID), (whole jsonld piece of data) ... ]
        # Nest from Property -> SpaceBoundaryElement -> SpaceBoundary -> Space -> SpaceCollection -> SpaceCollectionLocation -> GeoInstance
        level_count = 0
        while level_count < 6:
            used = 0
            for t in sortingDict[self.USO_hierarchy_order[level_count]]:
                # First Assume this piece will nest into a piece from the hierarchy directly above, then if not check others
                if used == 0:
                    # Not yet nested so try the level directly above (most cases)
                    if level_count < 6:
                        for t2 in sortingDict[self.USO_hierarchy_order[level_count + 1]]:
                            if t[0] in t2[1]:
                                used = 1
                                sortingDict = self.nest(t, t2, sortingDict, self.USO_hierarchy_order[level_count + 1])
                        if used == 0:
                            # Not yet nested in level directly above so try the rest of graph (rest of cases)
                            n = level_count + 2
                            while n <= 6:
                                for t3 in sortingDict[self.USO_hierarchy_order[n]]:
                                    if t[0] in t3[1]:
                                        sortingDict = self.nest(t, t3, sortingDict, self.USO_hierarchy_order[n])
                                n += 1
                        used = 0
            level_count += 1

        # Add back in top and bottom parts
        nested_parts = sortingDict["GeoInstance"]
        nested_first_geo_instance = ""
        for geo_instance in nested_parts:
            nested_first_geo_instance = geo_instance[1]
            new_json = top + nested_first_geo_instance + bottom

            print "new json file:"
            #print new_json
            # Will replace the current file with new current jsonld data version
            with open('Viz_Output/myldfile.jsonld','w+') as myfile:
                myfile.write(new_json)
            break # Will change if we reach files with multiple geo_instances, but shouldn't

        return

    def nest(self, t, t2, sortingDict, upper_index):
        #print t[0], t2[0]
        #print"--------"

        # It may nest into the existing file being built
        if str(t[0]) in str(t2[1]):
            add = '"@id": ' + t[0] #+ ",\n"
            #new_file = self.new_jsonld_file
            nest = t2[1].replace(add,str(t[1]))
            new_set = list()
            for i in sortingDict[upper_index]:
                if i[0] == t2[0]:
                    #print "pre_insert"
                    #print i[1]
                    newNest = (i[0],nest)
                    new_set.append(newNest)
                    #print "post_insert"
                    #print nest
                else:
                    new_set.append(i)
            sortingDict[upper_index] = new_set
        # Or, it will nest into the current piece and then be a separate entry into the existing file
        else:
            print "not found but should have..."
        return sortingDict



