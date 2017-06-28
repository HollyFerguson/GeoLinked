#-------------------------------------------------------------------------------
# Name:        file_type.py
# Purpose:     Query vocab to get Structure needed to build Query for gbxml instance
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     02/01/2016
# Copyright:   (c) Holly Tina Ferguson 2016
# License:     The University of Notre Dame
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
from renest import ReNest
import time
from IFC_SpeedUp import Faster_IFC

class QueryCurrentVocab():
    # Input parameters
    tree = None
    # May change as additional file options get entered into the mix
    namespaces = {}
    top_root = ""
    use_top_computed_node = 0

    # object_order and pred_order shoul dbe consistent for each vocab, although not all predicates may be used always
    #object_order = ["GeoInstance", "SpaceCollectionLocation"]
    #MyLDGraph = Graph()
    graphPieces = list()  # list of Graph elements that refuse to nest properly in json serializations

    object_order = ["GeoInstance", "SpaceCollectionLocation", "SpaceCollection", "Space", "SpaceBoundary", "SpaceBoundaryElement"]
    pred_order = {'GeoInstance':["hasSpatialCollectionLocationMember"],
                  'SpaceCollectionLocation':["hasSpaceCollectionMember", "hasSpaceMember", "hasSpaceBoundaryMember", "hasSpaceBoundaryElementMember"],
                  'SpaceCollection':["hasSpaceMember", "hasSpaceBoundaryMember", "hasSpaceBoundaryElementMember", "belongsToSpaceCollectionLocation"],
                  'Space':["hasSpaceBoundaryMember", "hasSpaceBoundaryElementMember", "belongsToSpaceCollection", "belongsToSpaceCollectionLocation"],
                  'SpaceBoundary':["hasSpaceBoundaryElementMember", "belongsToSpace", "belongsToSpaceCollection", "belongsToSpaceCollectionLocation"],
                  'SpaceBoundaryElement':["belongsToSpaceBoundary", "belongsToSpace", "belongsToSpaceCollection", "belongsToSpaceCollectionLocation"] }
    Vocab_base = "http://www.myuso.exp#"
    USObase = "http://www.sw.org/UBO#"  # Change back to full: "http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"
    rdfs_base = "http://www.w3.org/2000/01/rdf-schema#"
    xslt_base = "https://www.w3.org/TR/xslt-30/schema-for-xslt30#"
    geo_base = "http://www.opengis.net/ont/geosparql#"
    xslt_element = URIRef(xslt_base + "element")
    xslt_attribute = URIRef(xslt_base + "attribute")
    xslt_list = URIRef(xslt_base + "list")
    rdfs_isDefinedBy = URIRef(rdfs_base + "isDefinedBy")
    geo_hasGeometry = URIRef(geo_base + "hasGeometry")

    forward_Edge_Order = ["hasSpatialCollectionLocationMember", "hasSpaceCollectionMember", "hasSpaceMember", "hasSpaceBoundaryMember", "hasSpaceBoundaryElementMember", "lastDataSet"]

    # The hard-coded version uses the key term, the LD one will use the dataType form for generality
    prop_types = {"SpaceCollectionLocation":"DataType1",
                  "SpaceCollection":"DataType2",
                  "Space":"DataType3",
                  "SpaceBoundary":"DataType4",
                  "SpaceBoundaryElement":"DataType5" }
    property_counter = 1
    currentSpaceCollection = "blah"
    sub_holder = URIRef( "set_sub_holder" )
    pre_holder = URIRef( "set_pre_holder" )
    previous_trackingDict = dict()
    #previous_previous_trackingDict = dict()
    xml_instance_tracking = dict()
    parent2Ddata = ""
    parent3Ddata = ""
    current_predicateAbove = ""
    currentSpaceCollectionAbove = ""
    previous_branch_instance_count = 0
    branch_instance_counter_spaces = 0
    parent_branch_count = dict()
    missing_link = dict()  # Tracking for when you have to make geometry node when not identified in the schema (like citygml space:set of surface ids)
                           # So needed when you can get parent and grandchildren set of references so used to later infer how to assign the children
    missing_link2 = dict()
    LODis = ""
    test_dict_setup2 = dict() # Second part to missing_link, where the child data is found at one of several locations under the memory address of the child node

    # For Graph Add-Ons (trying to organize based upon where ):
    Add_On_Dict = dict()   # [Address] = [GraphName, SGA/UBO_ElementType]


    def querySetUp(self, graph, base):
        for subject,predicate,obj in graph:
           if not (subject,predicate,obj) in graph:
              raise Exception("Iterator / Container Protocols are Broken!!")
        return 0

    def query_current_vocab(self, current_vocab, inputfile, UBOgraphStructure, this_file_type):
        # Parse Model Instance
        if this_file_type == "gbxml":
            self.namespaces = {'gb': "http://www.gbxml.org/schema"}
            tree = etree.parse(inputfile)
        elif this_file_type == "ifcxml":
            self.namespaces = {'ifc': "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm", 'exp': "urn:oid:1.0.10303.28.2.1.1"}
            tree = etree.parse(inputfile)
            root = tree.getroot()
            if "}" in str(root.tag):
                #print "root.tag:", root.tag
                new_ifc_link1 = str(root.tag).split("}")[0]
                new_ifc_link = new_ifc_link1.split("{")[1]
                self.namespaces['doc'] = str(new_ifc_link)
            for child_of_root in root:
                if "}" in str(child_of_root.tag):
                    new_ifc_link1 = str(child_of_root.tag).split("}")[0]
                    new_ifc_link = new_ifc_link1.split("{")[1]
                    new_ifc = str(child_of_root.tag).split("}")[1]
                    self.namespaces[str(new_ifc)] = str(new_ifc_link)
                    if str(new_ifc) == "uos":
                        self.namespaces['ifc'] = str( new_ifc_link)
            this_root = str(root.tag).split("}")[1]
            self.top_root = "/doc:" + this_root + "/ifc:uos"
            print "self.top_root", self.top_root
        elif this_file_type == "citygml":
            self.namespaces = {'xmlns': "http://www.opengis.net/citygml/2.0", 'xlink': "http://www.w3.org/1999/xlink", 'city': "http://www.opengis.net/citygml/2.0", 'gml': "http://www.opengis.net/gml", 'bldg': "http://www.opengis.net/citygml/building/2.0", 'dem': "http://www.opengis.net/citygml/relief/1.0"}
            tree = etree.parse(inputfile)
        elif this_file_type == "xml":
            self.namespaces = {'xml': "something"}
            tree = etree.parse(inputfile)
            print "add lines to check for root condition and to set root.tag as first GeoInstance element (if starts with *)"
        else:
            print "File Type not yet handled for initial parsing..."
            return

        USO_New = Graph() # This is where instance trips will be stored into once querying is over
        MyLDGraph = Graph() # To make adjstments to the nesting when outputting JSONLD for visualizations
        UBOframe = UBOgraphStructure.serialize(destination='RDFout/myUBOframe.ttl', format='turtle') # Empty USO of OWL file
        curr_vocab_empty_graph = Graph()
        current_vocab_parsed = curr_vocab_empty_graph.parse(current_vocab, format="turtle") # Vocabulary Structure in TTL form parsed
        #serializedVocab = current_vocab_parsed.serialize(destination='RDFout/myVocabframe.ttl', format='turtle') # Serialized Vocab TTL File
        #print "current_vocab_parsed: ", current_vocab_parsed
        self.querySetUp(current_vocab_parsed, self.USObase) # Set-up Query Checks

        # Types of consistent USO vocab terms to query for any schema type (all should be based on these = one parser)
        SpatialObject = "http://www.opengis.net/ont/geosparql#SpatialObject"
        ASpatialObject = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#ASpatialObject")
        Vocab_GeoInstance = URIRef("http://www.myuso.exp#GeoInstance")
        Vocab_SpaceCollectionLocation = URIRef("http://www.myuso.exp#SpaceCollectionLocation")
        Vocab_SpaceCollection = URIRef("http://www.myuso.exp#SpaceCollection")
        Vocab_Space = URIRef("http://www.myuso.exp#Space")
        Vocab_SpaceBoundary = URIRef("http://www.myuso.exp#SpaceBoundary")
        Vocab_SpaceBoundaryElement = URIRef("http://www.myuso.exp#SpaceBoundaryElement")
        #----------------
        Vocab_hasSpatialCollectionLocationMember = URIRef("http://www.myuso.exp#hasSpatialCollectionLocationMember")
        Vocab_hasSpaceCollectionMember = URIRef("http://www.myuso.exp#hasSpaceCollectionMember")
        Vocab_hasSpaceMember = URIRef("http://www.myuso.exp#hasSpaceMember")
        Vocab_hasSpaceBoundaryMember = URIRef("http://www.myuso.exp#hasSpaceBoundaryMember")
        Vocab_hasSpaceBoundaryElementMember = URIRef("http://www.myuso.exp#hasSpaceBoundaryElementMember")
        #----------------
        Vocab_belongsToSpaceCollectionMember = URIRef("http://www.myuso.exp#belongsToSpaceCollectionMember")
        Vocab_belongsToSpaceCollection = URIRef("http://www.myuso.exp#belongsToSpaceCollection")
        Vocab_belongsToSpace = URIRef("http://www.myuso.exp#belongsToSpace")
        Vocab_belongsToSpaceBoundary = URIRef("http://www.myuso.exp#belongsToSpaceBoundary")
        Vocab_belongsToSpatialObject = URIRef("http://www.myuso.exp#belongsToSpatialObject")

        ################################################################
        # Query for types of uso:GeoInstance which are geo:SpatialObject
        print "-----------------top"
        #print current_vocab_parsed.serialize(format='turtle')

        start = time.clock()
        new_start1 = 0
        new_start2 = 0
        new_start3 = 0
        before_spaces = 0
        spaces = 0
        surfaces = 0
        materials = 0

        for item in self.object_order:
            geo_count = 1
            layer_check = URIRef( str(self.Vocab_base) + str(item) )
            print "########################################################################################################"
            print "Now using: ", item, layer_check



            for s,p,o in current_vocab_parsed.triples( (None,  RDF.type, layer_check) ):
                print "%s is a %s"%(s,o)
                a = URIRef( str(self.USObase) + str(item) + str(geo_count) )
                geo_count += 1
                Spatial_Instance_new = URIRef(a)

                predicate_list = self.pred_order[str(item)]
                print "predicate_list ", predicate_list
                for a_predicate in predicate_list:
                    # For each potential triple relationship, search this level for matching predicates and
                    # Then get associated object to use as subject to find in next graph level
                    full_predicate = URIRef(self.Vocab_base + a_predicate)
                    subpart_counter = 1
                    for row in current_vocab_parsed.query("""SELECT ?p ?o
                             WHERE { ?s ?p ?o .}""",
                        initBindings={'p' : full_predicate, 's' : s}):
                        #print "row: ", row
                        hasPredicate = URIRef( str(self.USObase + str(row[0].split(self.Vocab_base)[1])) )
                        Vocab_Item_object = URIRef( str(self.USObase + str(row[1].split(self.Vocab_base)[1])) )
                        Vocab_Item_current = URIRef( str(self.USObase + str(row[1].split(self.Vocab_base)[1]) + str(subpart_counter) ) )
                        #print "b and c: ", hasPredicate, Vocab_Item_object, Vocab_Item_current

                        if item == "GeoInstance":
                            if str(s) == "":
                                self.use_top_computed_node = 1
                            USO_New.add( (Spatial_Instance_new, RDF.type, layer_check) )
                            MyLDGraph.add( (Spatial_Instance_new, RDF.type, layer_check) )
                            print "-----------ADDED-----------", Spatial_Instance_new, RDF.type, layer_check
                            # This should be one instance...other GeoInstances would be a separate graph
                            USO_New.add( (Spatial_Instance_new, hasPredicate, Vocab_Item_current) )
                            print "-----------ADDED-----------", Spatial_Instance_new, hasPredicate, Vocab_Item_current
                            MyLDGraph.add( (Spatial_Instance_new, hasPredicate, Vocab_Item_current) )
                            print "Spatial_Instance_new:,", Spatial_Instance_new
                        else:
                            if item == "Space":
                                before_spaces = (time.clock() - start)
                                new_start1 = time.clock()
                            if item == "SpaceBoundary":
                                spaces = (time.clock() - new_start1)
                                new_start2 = time.clock()
                            self.next_level_search(USO_New, current_vocab_parsed, o, subpart_counter, this_file_type, tree, MyLDGraph)

                        subpart_counter += 1
                        #print "bottom"
                if item == "SpaceBoundaryElement":
                    surfaces = (time.clock() - new_start2)
                    new_start3 = time.clock()
                    self.next_level_search(USO_New, current_vocab_parsed, o, 0, this_file_type, tree, MyLDGraph)
                    materials = (time.clock() - new_start3)

        print "########################################################################################################"
        print "Does this make sense?"

        print USO_New.serialize(format='turtle')
        #print MyLDGraph.serialize(format='turtle')
        #print USO_New.serialize(format='json-ld') # MyLDGraph
        print""

        print "before_spaces: ", before_spaces
        print "spaces:        ", spaces
        print "surfaces:      ", surfaces
        print "materials:     ", materials
        print "total:         ", (time.clock() - start)

        #print "Does this make sense for the JSON-LD part of the processing?"
        #nest = ReNest()
        #nest.startReNest(USO_New, MyLDGraph)

        #print "self.LODis", self.LODis
        if self.LODis == 0:
            self.missing_link = self.missing_link2
        return USO_New, self.Add_On_Dict, tree, self.namespaces, self.property_counter, self.missing_link

    def next_level_search(self, USO_New, current_vocab_parsed, current_subject, subpart_counter, this_file_type, tree, MyLDGraph):

        # These several lines are to redirect the ifcxml processing for faster graph creation
        # If omitted, the program will run as normal with the more generalized LD View solution
        a = str(current_subject)
        a_lookup = a.split(self.Vocab_base)[1]
        if this_file_type == "ifcxml":
            if a_lookup == "Space" or a_lookup == "SpaceBoundary" or a_lookup == "SpaceBoundaryElement":
                fasterifc = Faster_IFC()
                USO_New, self.property_counter, Add_On_Dict = fasterifc.add_spaces_surfaces_and_materials(USO_New, current_subject, this_file_type, tree, self.namespaces, self.Add_On_Dict, self.property_counter)
                return

        print "-----------------next_level_search"
        current_subject = URIRef(self.Vocab_base + current_subject.split("#")[1])
        #print current_subject
        for s,p,o in current_vocab_parsed.triples( (None,  RDF.type, current_subject) ):
            print "%s is a %s"%(s,o)
            a = str(current_subject)
            a_lookup = a.split(self.Vocab_base)[1]
            a = self.USObase + a.split(self.Vocab_base)[1] + str(subpart_counter)
            current_subject = URIRef(a)
            #predicate_list = self.pred_order[a_lookup]
            #subpart_counter = 0

            # Find index of current_subject (a_lookup for just the last part of the string) in object_order
            i = 0
            for n in self.object_order:
                if str(n) == str(a_lookup):
                    break
                i += 1
            # Match object_order to forward_Edge_Order
            #print "i", i, a_lookup
            if a_lookup == "SpaceBoundaryElement":
                predicate_list = ["hasLastDataSet"]
            else:
                predicate_list = self.pred_order[a_lookup]
            matching_predicate = self.forward_Edge_Order[i]
            #print "saying this is self.forward_Edge_Order[1]: ", self.forward_Edge_Order[1]

            for a_predicate in predicate_list:
                # For each potential triple relationship, search this level for matching predicates and
                # Then get associated object to use as subject to find in next graph level
                full_predicate = URIRef(self.Vocab_base + a_predicate)
                #print "full_predicate ", full_predicate
                for row in current_vocab_parsed.query("""SELECT ?p ?o
                          WHERE { ?s ?p ?o .}""",
                    initBindings={'p' : full_predicate, 's' : s}):
                    #print "rowV: ", row[0], row[1]

                    # This is what needs to be added as 1, 2, 3, etc. for each thing found in the instance XML file
                    hasPredicate = URIRef( str(self.USObase) + str(row[0].split(self.Vocab_base)[1]) )

                    # Use matching_predicate to proceed through the tree
                    # For the current_subject, collect the relevant relationships and paths from vocabulary file
                    e = self.xslt_element
                    att = self.xslt_attribute
                    l = self.xslt_list
                    d = self.rdfs_isDefinedBy
                    g = self.geo_hasGeometry
                    e_data_list = list()
                    l_data_list = list()
                    isDefinedBy = ""
                    hasGeometry = ""
                    root_att_data_list = list()
                    defined_data_list = list()
                    geo_data_list = list()
                    #print "added here: ", matching_predicate, a_predicate

                    if matching_predicate == a_predicate or matching_predicate == "lastDataSet":

                        # Attributes for current subject
                        my_full_predicate = URIRef(self.Vocab_base + a_predicate)
                        #hasObject = URIRef( str(self.USObase) + str(row[1].split(self.Vocab_base)[1]) + str(subpart_counter) )
                        hasObject = str(row[1])

                        print "reaching parts sequence"
                        # Root Attribute data
                        for row in current_vocab_parsed.query("""SELECT ?x ?y
                                WHERE { ?s ?att ?o .
                                        ?o ?x ?y .}""",
                            initBindings={'s' : s, 'e' : e, 'att' : att, 'l' : l, 'd' : d}):
                            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                #print "xslt_attribute: ", str(row[1])
                                root_att_data_list.append(str(row[1]))
                            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                find_end_of_list = 0
                                next_blank_node = BNode(row[1])
                                root_att_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, root_att_data_list, find_end_of_list)
                                #print "root_att_data_list:", root_att_data_list


                        # Root idDefinedBy Data ---> Three types: Assuming only will see option 1 or 2 for now since only used to create child nodes
                        #1) rdf:nil none to process so can ignore
                        #2) single blank node which can be one or a sequence of steps as in gbxml (depth to collect) which gets te child relationships
                        #3) can be a list in the parent set of data meaning there are multiple paths to different pieces of data (breadth to collect and reassemble) which gets the parent geometries beyond
                        print "isDefinedBy data:", s, d  #d = self.rdfs_isDefinedBy
                        list_type_definedBy = 0
                        for row in current_vocab_parsed.query("""SELECT ?o ?x ?y
                                WHERE { ?s ?d ?o .
                                        ?o ?x ?y .}""",
                            initBindings={'s' : s, 'e' : e, 'att' : att, 'l' : l, 'd' : d}):
                            #thistype = type(row[0]).__name__
                            print "checking the rows: ", row
                            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                print "DefinedBy is nil...passed since types are processed already alter on"
                            else:
                                print "DefinedBy is not nil...but at this point has been handled by l_list_data in deeper function"
                                defined_data_list = [ BNode(row[0]) ]

                                '''
                                # Then there is a list of defined by data, at this point should be for geometry data
                                print "thistype", thistype
                                find_end_of_list = 0
                                next_blank_node = BNode(row[0])
                                defined_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, defined_data_list, find_end_of_list)
                                if len(defined_data_list) > 1:
                                    if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                        defined_data_list.append(str(row[1]))
                                    if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                        find_end_of_list = 0
                                        next_blank_node = BNode(row[1])
                                        defined_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, defined_data_list, find_end_of_list)
                                    list_type_definedBy = 1
                                '''

                        # hasGeometry data   g = self.geo_hasGeometry
                        for row in current_vocab_parsed.query("""SELECT ?x ?y ?o
                                WHERE { ?s ?g ?o .
                                        ?o ?x ?y .}""",
                            initBindings={'s' : s, 'g' : g}):
                            #print "checking the rows: ", row
                            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                #print "geo_hasGeometry: ", str(row[1])
                                geo_data_list = [ str(row[1]) ]
                            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                # This should always just be one blank node describing where to get the geometry info
                                #print "xslt_attribute: ", str(row[1])
                                find_end_of_list = 0
                                next_blank_node = BNode(row[2])
                                geo_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, geo_data_list, find_end_of_list)

                        # Start path point
                        element_type = 0
                        myPath = ""
                        for row in current_vocab_parsed.query("""SELECT ?x ?y
                                WHERE { ?s ?e ?o .
                                        ?o ?x ?y .}""",
                            initBindings={'s' : s, 'e' : e}):
                            #print "-----------rows: ", row, s
                            # Set the element_type in case there are more list types later on...
                            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "start":
                                element_type = 1
                        #print "element_type", element_type
                        for row in current_vocab_parsed.query("""SELECT ?x ?y
                                WHERE { ?s ?e ?o .
                                        ?o ?x ?y .}""",
                            initBindings={'s' : s, 'e' : e}):
                            # If this list starts with "start" it is the start Path type of list
                            if element_type == 1:
                                #print "e_here"
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                    print "empty" # No start path here, probably because it is the first root
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                    print "end of list"
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) != "start":
                                    data = str(row[1])
                                    print "data to collect", data
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                    #print "list continues with blank node", str(row[1])
                                    find_end_of_list = 0
                                    next_blank_node = BNode(row[1])
                                    e_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, e_data_list, find_end_of_list)
                                    #print "e_data_list:", e_data_list, s
                            else:
                                #print "Type is not a Start Path, needs attention"   # Actually, this means its another type of element than start if this structure is used
                                e_data_list = ["non_address_type"]

                        # List data which is the list of relevant data items from this point
                        list_type = 0
                        myPath = ""
                        for row in current_vocab_parsed.query("""SELECT ?x ?y
                                WHERE { ?s ?l ?o .
                                        ?o ?x ?y .}""",
                            initBindings={'s' : s, 'e' : e, 'att' : att, 'l' : l, 'd' : d}):
                            #print "-----------rows: ", row
                            # Set the element_type in case there are more list types later on...
                            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "info":
                                list_type = 1

                        for row in current_vocab_parsed.query("""SELECT ?x ?y
                                WHERE { ?s ?l ?o .
                                        ?o ?x ?y .}""",
                            initBindings={'s' : s, 'e' : e, 'att' : att, 'l' : l, 'd' : d}):
                            # If this list starts with "start" it is the start Path type of list
                            if list_type == 1:
                                #print "l_here"
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                    print "empty"
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                    print "end of list"
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) != "info":
                                    data = str(row[1])
                                    #print "data to collect", data
                                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                    #print "list continues with blank node", str(row[1])
                                    find_end_of_list = 0
                                    next_blank_node = BNode(row[1])
                                    # If there are sub lists nested, then there will be results from this:
                                    check_for_sub_nodes = 0
                                    sub_row = BNode("000")
                                    for sub_row in current_vocab_parsed.query("""SELECT ?x ?a ?b
                                            WHERE { ?blank ?first ?x .
                                                    ?x ?a ?b .}""",
                                        initBindings={'blank' : next_blank_node, 'first' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first"), 'rest' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest") }):
                                        check_for_sub_nodes += 1
                                        #print "this sub_row: ", sub_row
                                    #print "check_for_sub_nodes: ", check_for_sub_nodes
                                    if check_for_sub_nodes > 0:
                                        l_data_list, l_find_end_of_list_now, last_blank_node = self.collect_list_items(sub_row[0], current_vocab_parsed, l_data_list, find_end_of_list)
                                        print "l_data_list:", l_data_list
                                        #print "l_find_end_of_list_now: ", l_find_end_of_list_now
                            else:
                                print "Type is not an Info, check parent list types in RDF file"   # Actually, this means its another type of element than start if this structure is used

                        self.collect_deeper_data(current_vocab_parsed, root_att_data_list, geo_data_list, e_data_list, l_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, MyLDGraph, defined_data_list, list_type_definedBy)
                        # match object_order to forward_Edge_Order
        return

    def collect_list_items(self, next_blank_node, current_vocab_parsed, data_list, find_end_of_list_now):
        # Until the end of this list, query for next blank node:
        new_blank_node = ""
        for sub_row in current_vocab_parsed.query("""SELECT ?x ?y
                WHERE { ?blank ?first ?x .
                        ?blank ?rest ?y .}""",
            initBindings={'blank' : next_blank_node, 'first' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first"), 'rest' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest") }):
            #print "-----------list rows: ", sub_row
            if str(sub_row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                new_blank_node = BNode(sub_row[1])
                #print "My new_blank_node: ", new_blank_node, sub_row[1]
                find_end_of_list_now += 1
            if str(sub_row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                #print "end of sub list"
                find_end_of_list_now += 1
            if str(sub_row[0]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                data = str(sub_row[0])
                data_list.append(data)
                #print "data for this row: ", data
            if str(sub_row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                print "first is reading as nil..."
        #print "The new vs current nodes: ", next_blank_node, new_blank_node
        #last_blank_node = ""
        if str(next_blank_node) != str(new_blank_node):
            # Then there was another blank node found to follow so repeat
            # Cannot repeat within the loop since the rows do not get checked in order each time, so still need to do checking on the rest before new call
            #print "getting to the recursion"
            data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(new_blank_node, current_vocab_parsed, data_list, find_end_of_list_now)

        return data_list, find_end_of_list_now, new_blank_node

    def find_next_in_list(self, current_data, current_vocab_parsed, blank_data_list, more_flag):
        # Gets a list of root blank nodes
        data = ""
        rest = ""
        #print "current_data", current_data
        for this_row in current_vocab_parsed.query("""SELECT ?x ?y
                WHERE { ?r ?x ?y .}""",
            initBindings={'r' : BNode(current_data), 'rest' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#rest"), 'first' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first") }):
            #print "new function: ", this_row

            if str(this_row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first":
                data = str(this_row[1])

            if this_row[0] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest":
                if this_row[1] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                    more_flag = 0
                    rest = str(this_row[1])
                else:
                    more_flag = 1
                    rest = str(this_row[1])

        return data, more_flag, rest

    def collect_deeper_data(self, current_vocab_parsed, root_att_data_list, hasRootGeometry, e_data_list, l_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, MyLDGraph, defined_data_list, list_type_definedBy):
        gbxml_base = "http://www.gbxml.org/schema#"
        startPath = ""

        #if str(root_att_data_list) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
        #    print "root_att_data_list needs attention: ", root_att_data_list

        if str(e_data_list) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
            #print "startPathDeeperData: ", e_data_list
            startPath = str(e_data_list[0])

        if str(l_data_list) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil" and str(l_data_list) != "[]":
            #print "l_data_list : ", l_data_list
            itemsToQuery = list()
            for item in l_data_list:
                itemsToQuery.append(item.split("#")[1])
            #print "itemsToQuery ", itemsToQuery
            calledA = 0
            calledB = 0
            for item in l_data_list:
                #print "item in l_data_list: ", item
                # Each Item rdfs:isDefinedBy ( some list of blank nodes )
                data_list = list()
                for row in current_vocab_parsed.query("""SELECT ?item ?x ?y ?z
                        WHERE { ?item ?d ?x .
                                ?x ?y ?z .}""",
                    initBindings={'d' : self.rdfs_isDefinedBy, 'item' : URIRef(item) }):
                    #print "this second level row: ", row[3]
                    current_data = str(row[3])
                    if str(row[2]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first":
                        data_list.append(str(row[3]))
                    elif str(row[2]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest":
                        if str(row[3]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                            continue
                        else:
                            # Not nil so there is more to the list to collect the blank data nodes:
                            blank_data_list = list()
                            more_flag = 1
                            next_list_item, more_flag, rest = self.find_next_in_list(current_data, current_vocab_parsed, blank_data_list, more_flag)
                            data_list.append(str(next_list_item))
                    print "data_list_set", data_list

                    for d in data_list:
                        # For each blank node (seems to be structuring in sets of two blanks chained together) find the associated blank node (data is after that)
                        #xslt:element "bdata"^^xsd:string ;         string - 1 of 3 types
                        #xslt:attribute rdf:nil ;                   next two are list of tag attributes to query until nil
                        #grddl:transformationProperty [ rdf:first "/gb:gbXML/gb:Campus/gb:Location/gb:Elevation"^^xsd:string ; #rdf:rest rdf:nil ] .

                        attribute_data_list = list()
                        transformationProperty_data_list = list()
                        current_data_type = list()
                        a = 0
                        b = 0
                        c = 0
                        for row in current_vocab_parsed.query("""SELECT ?x ?y
                                WHERE { ?d ?x ?y .}""",
                            initBindings={'d' : BNode(d)}):
                            #print "data - attribute - transProperty: ", row
                            find_end_of_list_now = 0
                            if row[0] == URIRef("https://www.w3.org/TR/xslt-30/schema-for-xslt30#element"):
                                current_data_type = str(row[1])
                                a = 1
                            if row[0] == URIRef("https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute"):
                                attribute_data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(row[1], current_vocab_parsed, attribute_data_list, find_end_of_list_now)
                                b = 1
                            if row[0] == URIRef("https://www.w3.org/2003/g/data-view#transformationProperty"):
                                transformationProperty_data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(row[1], current_vocab_parsed, transformationProperty_data_list, find_end_of_list_now)
                                c = 1

                            if a == 1 and b == 1 and c == 1:
                                # String List List
                                #print "Now: ", current_data_type, attribute_data_list, transformationProperty_data_list
                                a = 0
                                b = 0
                                c = 0
                                currentDataPathsList = list()
                                list_type_definedBy = 0
                                set_types_information = list()
                                # Call both functions becuase there is potential for parent geometry data collection child relationship data
                                self.query_xml_instance_to_make_triples(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph, currentDataPathsList, defined_data_list, l_data_list)
                                self.addCoordinateData(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph)

                                #if str(hasRootGeometry) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                #    # Otherwise this call will be redundant, but need hasRootGeom call seperate when l_data_list is empty so does not get here
                                #    self.addCoordinateData(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph)

            if this_file_type == "citygml":   # Like when you see a Building(s) and ReliefFeatures described in same Location
                attribute_data_list = list()
                transformationProperty_data_list = list()
                current_data_type = list()
                currentDataPathsList = list()
                self.query_xml_instance_to_make_triples(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph, currentDataPathsList, defined_data_list, l_data_list)
                self.addCoordinateData(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph)


        else:  # str(l_data_list) == "[]":
            #     then call this here becuase the children were not set up above because there were no l_data_list items...so set up children here before adding the associated geo data by defined
            current_data_type = ""
            transformationProperty_data_list = list()
            currentDataPathsList = list()
            attribute_data_list = root_att_data_list
            #print "entering"
            self.query_xml_instance_to_make_triples(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph, currentDataPathsList, defined_data_list, l_data_list)

        if str(hasRootGeometry) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
            if str(l_data_list) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil" or str(l_data_list) == "[]":
                #print "hasRootGeometry is list of: ", hasRootGeometry
                # For when the data is found through a set of paths but has nothing to list in the "list" part of the vocab
                # Also, assuming hasRootGeometry is a list of blank node that hold paths to data parts required to create the element geometry
                current_data_type = ""
                attribute_data_list = list()
                transformationProperty_data_list = list()
                # Just set up geometry for parent because this tells nothing about the child relationships
                self.addCoordinateData(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph)

        #else:
        #    print "Other type of this level condition..."

        """
        if this_file_type == "citygml":   # Like when you see a Building(s) and ReliefFeatures described in same Location
            if str(l_data_list) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil" and str(l_data_list) != "[]":
                #print "hasRootGeometry is list of: ", hasRootGeometry
                # For when the data is found through a set of paths but has nothing to list in the "list" part of the vocab
                # Also, assuming hasRootGeometry is a list of blank node that hold paths to data parts required to create the element geometry
                for item in l_data_list:
                    current_data_type = ""
                    attribute_data_list = list()
                    transformationProperty_data_list = list()
                    # Just set up geometry for parent because this tells nothing about the child relationships
                    print "used that one"
                    self.addCoordinateData(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph)
                    self.query_xml_instance_to_make_triples(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph, currentDataPathsList, defined_data_list, l_data_list)
        """
        return

    def query_xml_instance_to_make_triples(self, current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph, currentDataPathsList, defined_data_list, l_data_list):
        print  "Use these different pieces to query xml instance"

        trackingDict = dict()
        trackingDict2 = dict()
        levelInstanceDict = dict()
        branch = dict()

        if self.currentSpaceCollection == "blah":
            self.sub_holder = URIRef( str( current_subject ) )  # SpaceCollectionLocation1
            self.pre_holder = URIRef( str(self.USObase) + str(my_full_predicate.split("#")[1]) )  # hasSpaceCollectionMember
            self.currentSpaceCollection = "set"

        if str(a_lookup) == "SpaceBoundaryElement":
            xml_instances = list()
        else:
            if str(startPath[0]) == "*":
                startPath = str(self.top_root + startPath.split("*")[1])
            xml_instances = tree.xpath(startPath, namespaces=self.namespaces)
            #print "start path 1-----", startPath, xml_instances
        if this_file_type == "citygml": # Becuase to get all city elements we have to set it such that we will need to use the next level to id as Building or other type
            if str(a_lookup) == "SpaceCollection" or str(a_lookup) == "Space":
                xml_instance_sets = tree.xpath(startPath, namespaces=self.namespaces)
                xml_instances = list()
                for category in xml_instance_sets:
                    category = category.getchildren()
                    for c_nest in category:
                        xml_instances.append(c_nest)
        if str(startPath) == "non_address_type":  # So this is cases where previous_parent is the complexity type
            # This happens when there is a set of relationships to parents that need creating all at once, as with citygml
            parent_cases = list() # So one would be added, for example, for each building or relief feature in citygml
            #print "non_address_type"
            for m in self.missing_link:
                if self.missing_link[m][0] not in parent_cases:
                    parent_cases.append(self.missing_link[m][0])
            xml_instances = parent_cases
            #print "new xml_instances: ", xml_instances
        #print "startPath", startPath, current_data_type, len(xml_instances), hasObject, str(a_lookup)
        last_added_element = 1
        geo_count = 1
        processing_flag_SBE = 0
        element_bound_counter = 1
        level_processing_pieces = dict()
        #print "and", xml_instances
        for xml_instance in xml_instances:
            print "at what level", xml_instance
            # CityGML is the odd ball where Spaces are not defined on their own, so these instances and parent/child links are done in their own catch case because all spaces are not at the same level
            if this_file_type == "citygml" and str(a_lookup) == "Space":
                layer = URIRef( str(self.USObase) + str(a_lookup) )
                Spatial_Instance_new = URIRef( str(self.USObase) + str(a_lookup) + str(geo_count) )
                geo_count += 1
                print "passed citygml spaces type for intial setup"
            else:
                layer = URIRef( str(self.USObase) + str(a_lookup) )
                Spatial_Instance_new = URIRef( str(self.USObase) + str(a_lookup) + str(geo_count) )
                if this_file_type != "citygml" or str(a_lookup) != "SpaceBoundary":
                    USO_New.add( (Spatial_Instance_new, RDF.type, layer) )
                    print "-----------ADDED-T----------", Spatial_Instance_new, RDF.type, layer, "from", xml_instance
                    MyLDGraph.add( (Spatial_Instance_new, RDF.type, layer) )
                    print "with", xml_instance, [Spatial_Instance_new, layer]
                    self.Add_On_Dict[Spatial_Instance_new] = [xml_instance, layer]
                    geo_count += 1
                if this_file_type == "citygml" and str(a_lookup) == "SpaceCollection":
                    self.missing_link2[xml_instance] = [xml_instance, Spatial_Instance_new, 0, [0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0], [0,0,0,0,0,0]]
                    print "missinglink fill in for LOD_0: ", xml_instance, Spatial_Instance_new

            if str(a_lookup) == "SpaceCollection":
                self.currentSpaceCollection = str( Spatial_Instance_new.split("#")[1] )
                # Add connecting triple that is missing linking this Space Collection to Space Collection Location Above
                #print "check me", self.sub_holder, self.pre_holder, Spatial_Instance_new, current_subject
                USO_New.add( (self.sub_holder, self.pre_holder, Spatial_Instance_new) )
                print "-----------ADDED-SC----------", self.sub_holder, self.pre_holder, Spatial_Instance_new
                MyLDGraph.add( (self.sub_holder, self.pre_holder, Spatial_Instance_new) )

            #if str(a_lookup) == "SpaceBoundary" or str(a_lookup) == "SpaceBoundaryElement":
            #    self.currentSpaceCollection = "set"

            ####if attribute_data_list != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                # Means there is attribute data to collect and match for the list of relevant instance items
            branch_count = 1
            branch_instance_counter = 1
            e = self.xslt_element
            a = self.xslt_attribute
            d = self.rdfs_isDefinedBy
            g = self.geo_hasGeometry

            branch_instances = list()
            search_complexity = ""
            if this_file_type == "gbxml" or this_file_type == "ifcxml" or this_file_type == "citygml":
                next_type = URIRef( str(self.Vocab_base) + str(layer.split("#")[1]) )
                co = URIRef( str(self.Vocab_base) + str(hasObject.split("#")[1]) )
                relationType = URIRef( "https://www.w3.org/TR/xslt-30/schema-for-xslt30#complexType" )
                for r in current_vocab_parsed.query("""SELECT ?literal
                        WHERE { ?item ?r ?obj .
                                ?item ?relationType ?literal . }""",
                    initBindings={'r' : RDF.type, 'obj' : next_type, 'relationType' : relationType, 'co' : co }):
                    search_complexity = r[0]

                for row in current_vocab_parsed.query("""SELECT ?item ?this ?co
                        WHERE { ?item ?r ?obj .
                                ?item ?this ?co . }""",
                    initBindings={'r' : RDF.type, 'obj' : next_type, 'relationType' : relationType, 'co' : co }):
                    #print "obj check: ", row  # Parent * hasMember * Child

                    e_data_list = list()
                    a_data_list = list()
                    s0List = list()
                    s1List = list()
                    # Get child Type
                    for rowb in current_vocab_parsed.query("""SELECT ?child ?o
                            WHERE { ?child ?r ?s .
                                    ?child ?e ?o . }""",
                        initBindings={'s' : row[2], 'e' : e, 'r' : RDF.type}):
                        #print "rowb...", rowb
                        s0List = rowb[0]
                        s1List = rowb[1]

                    # Get child attributes
                    child_attributes = list()
                    for rowf in current_vocab_parsed.query("""SELECT ?x ?y
                            WHERE { ?child ?a ?o .
                                    ?o ?x ?y . }""",
                        initBindings={'child' : s0List, 'a' : a, 'r' : RDF.type}):
                        if str(rowf[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(rowf[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                            a_data_list.append(str(rowf[1]))
                        if str(rowf[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(rowf[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                            find_end_of_list = 0
                            next_blank_node = BNode(rowf[1])
                            child_attributes, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, a_data_list, find_end_of_list)

                    # Get child start point
                    #print "HERE!"
                    for rowc in current_vocab_parsed.query("""SELECT ?x ?y
                            WHERE { ?child ?e ?o .
                                    ?o ?x ?y . }""",
                        initBindings={'child' : s0List, 'e' : e, 'r' : RDF.type}):
                        if str(rowc[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(rowc[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                            find_end_of_list = 0
                            next_blank_node = BNode(rowc[1])
                            e_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, e_data_list, find_end_of_list)
                            #print "pulling start paths:", startPath, e_data_list[0]

                            #print "start path 2", str(e_data_list[0])
                            if str(e_data_list[0][0]) == "*" and self.use_top_computed_node == 1:
                                e_data_list[0] = str(self.top_root + str(e_data_list[0]))
                            if this_file_type == "citygml" and a_lookup == "SpaceCollection":
                                branch_instances = xml_instance.getchildren()
                            else:
                                branch_instances = tree.xpath(e_data_list[0], namespaces=self.namespaces)
                            #print "branch_instances", branch_instances

                            _index = self.object_order.index(a_lookup)
                            self.parent_branch_count[str(self.object_order[_index + 1])] = len(branch_instances)
                            #print "just stored: ", self.object_order[_index + 1], len(branch_instances)

                            self.xml_instance_tracking[Spatial_Instance_new] = [ xml_instance, Spatial_Instance_new, str(a_lookup), branch_instances, None, 0, 0 ]

                            if str(search_complexity) == "unnecessary":
                                # Relation between this level and the next level not needed in this schema
                                print "unnecessary"

                            if str(search_complexity) == "simple":
                                # Relation between this level and the next level found by basic attribute matching...works more like an "add all children" solution
                                trackingDict = dict()
                                levelInstanceDict = dict()
                                print "simple"
                                print "NEEDS a couple of elements like the tracking dictionary added in for this type!!"
                                # Collect all the child nodes that belong to this parent
                                for branch_instance in branch_instances:
                                    for eachAttr in root_att_data_list:
                                        #print "matching these: ", eachAttr, attribute_data_list
                                        if eachAttr in attribute_data_list:
                                            # Then this child must be related to this parent node, so add a triple
                                            #print "found this to belong by matching: ", eachAttr
                                            next_level = URIRef( str(self.USObase) + str(row[2].split("#")[1]) + str(branch_count) )
                                            current_predicate = URIRef( str(self.USObase) + str(my_full_predicate.split("#")[1]) )
                                            USO_New.add( (Spatial_Instance_new, current_predicate, next_level) )
                                            print "-----------ADDED_HERE-----------", Spatial_Instance_new, current_predicate, next_level
                                            MyLDGraph.add( (Spatial_Instance_new, current_predicate, next_level) )
                                            #print "XXXXXXXXXXXXXXXX added this: ", Spatial_Instance_new, current_predicate, next_level
                                            branch_count += 1
                                            trackingDict[next_level] = branch_instance, child_attributes
                                            trackingDict2[next_level] = branch_instance, child_attributes
                                            levelInstanceDict[branch_instance] = next_level
                                #self.previous_previous_trackingDict = self.previous_trackingDict
                                self.previous_trackingDict = trackingDict

                            if str(search_complexity) == "fill_in_parents":
                                test_dict_setup = dict()
                                test_dict_setup_upOneLayerCase = dict()
                                if this_file_type == "citygml":
                                    for node in tree.findall('.//{http://www.opengis.net/gml}Polygon'):
                                        p_url = node.attrib.get('{http://www.opengis.net/gml}id')
                                        if p_url:
                                            test_dict_setup["#" + str(p_url)] = node
                                    for node in tree.findall('.//{http://www.opengis.net/gml}CompositeSurface'):
                                        p_url = node.attrib.get('{http://www.opengis.net/gml}id')
                                        if p_url:
                                            test_dict_setup_upOneLayerCase["#" + str(p_url)] = node
                                else:
                                    print "test_dict_setup and test_dict_setup_upOneLayerCase need case for type other than citygml pattern" # Where Sets of surfaces are found

                                # hasGeometry data from above, but tried here in a different assembly approach
                                geo_data_list = list()
                                for row in current_vocab_parsed.query("""SELECT ?x ?y ?o
                                        WHERE { ?s ?g ?o .
                                                ?o ?x ?y .}""",
                                    initBindings={'s' : URIRef("http://www.citygml.org/index.php?id=1540#Surface"), 'g' : URIRef(g)}):
                                    #print "checking the rows: ", row
                                    if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                        #print "geo_hasGeometry: ", str(row[1])
                                        geo_data_list = [ str(row[1]) ]
                                    if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                        # This should always just be one blank node describing where to get the geometry info
                                        #print "xslt_attribute: ", str(row[1])
                                        find_end_of_list = 0
                                        next_blank_node = BNode(row[2])
                                        geo_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, geo_data_list, find_end_of_list)
                                        #print "geo_data_list", geo_data_list

                                trackingDict = dict()
                                levelInstanceDict = dict()
                                # For cityGML pattern, it is at the SpaceBoundary Level that all the parents can finally be filled in
                                if a_lookup == "SpaceBoundary":  # So far this case has only been seen at the SpaceBoundary level needing parents adn spaces filled in (catch to verify future occurrences)
                                    # print "at SpaceBoundary Level...use missing_link"
                                    branch_count = 1
                                    element_counter = 1
                                    for link_set in self.missing_link:
                                        print "link_set", link_set, self.missing_link[link_set] # self.missing_link[space] = [gr.parent addr, gr.parent graph_name, LOD, set_of_surface_ids, set_of_surface_datas, hrefs if there]
                                        if self.missing_link[link_set][0] == xml_instance:
                                            self.test_dict_setup2 = dict()  # Zero out so will have a new collection of surfaces for each space
                                            # So, for each space listing in missing_link, see if that space is part of the current xml_instance
                                            # Should now be handling a set of spaces pertaining to an existing building or SpaceCollection
                                            hasProperty = URIRef(str(self.USObase) + "hasProperty")
                                            hasType = URIRef(str(self.USObase) + "hasType")
                                            hasValue = URIRef(str(self.USObase) + "hasValue")
                                            for graph_row in USO_New.query("""SELECT ?x
                                                    WHERE { ?x ?a ?b .
                                                            ?b ?v ?xml . }""",
                                                initBindings={'xml' : Literal(str(xml_instance)), 'a' : hasProperty, 'v' : hasValue}):
                                                print "graph_row", graph_row[0]
                                                if len(graph_row) > 0:
                                                    Spatial_Instance_new = URIRef(str(self.USObase) + graph_row[0].split("#")[1])
                                                else:
                                                    print "in fill_in_parents there are no groups found"
                                            current_predicate = URIRef( str(self.USObase) + str("hasSpaceMember") )
                                            curr_level = URIRef( str(self.USObase) + "Space" + str(branch_count) )
                                            USO_New.add( (Spatial_Instance_new, current_predicate, curr_level) )
                                            USO_New.add( (curr_level, RDF.type, URIRef(str(self.USObase + "Space") )) )
                                            print "Link_Added F: ", curr_level, RDF.type, str(self.USObase + "Space")
                                            print "Link_Added F: ", Spatial_Instance_new, current_predicate, curr_level

                                            if curr_level != link_set[1]:
                                                temp_link_set = self.missing_link[link_set]
                                                temp_link_set[1] = curr_level
                                                self.missing_link[link_set] = temp_link_set
                                            self.Add_On_Dict[curr_level] = [link_set, URIRef(str(self.USObase + "Space") )]
                                            print "Now link_set is:", link_set, self.missing_link[link_set]

                                            set_of_surface_datas = list()
                                            current_subject = URIRef(self.Vocab_base + "SpaceBoundary")
                                            my_full_predicate = URIRef(self.Vocab_base + "hasSpaceBoundaryMember")
                                            # Fill set_of_surface_datas by following sub-paths and add datas as found there
                                            if str(self.missing_link[link_set][4][0]) == "" or len(self.missing_link[link_set][4]) == 0 or str(self.missing_link[link_set][4][0]) == "None":
                                                # Then we have to use IDs to pull data from a set of GML-IDs that would have been in self.missing_link[link_set][5]
                                                # Since set_of_surface_datas is empty, will fill it now using the results from other functions or given data if LOD1

                                                sub_test_dict_setup = dict() # Create a sub_dict() since we do not want to add all building surfaces every space
                                                print test_dict_setup
                                                for GMLid in self.missing_link[link_set][5]:
                                                    if GMLid not in test_dict_setup:
                                                        # Use path to get set of polygons ids and locations
                                                        upper_location = test_dict_setup_upOneLayerCase[GMLid]
                                                        print upper_location, GMLid
                                                        lower_locations = upper_location.xpath("./gml:surfaceMember/gml:Polygon", namespaces=self.namespaces) # Look for sub polygons now
                                                        print "lower_locations", len(lower_locations), lower_locations
                                                        for lower_location in lower_locations:
                                                            ll_id = lower_location.get("{http://www.opengis.net/gml}id")
                                                            print "ll_id", ll_id
                                                            sub_test_dict_setup[ll_id] = lower_location
                                                    else:
                                                        sub_test_dict_setup[GMLid] = test_dict_setup[GMLid]
                                                print "so this space has:", len(sub_test_dict_setup)
                                                for u in sub_test_dict_setup:
                                                    print u, sub_test_dict_setup[u]
                                                currentDataPathsList, set_types_information = self.findCurrentDataPathsList(current_vocab_parsed, "", "", attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, "SpaceBoundary", USO_New, current_subject, my_full_predicate, hasObject, geo_data_list, MyLDGraph)
                                                data_for_surface_dict, next_p_list, LOD_node = self.processCurrentDataPathsList(currentDataPathsList, set_types_information, a_lookup, tree, this_file_type, sub_test_dict_setup)

                                                if self.missing_link[link_set][6] == 1:
                                                    USO_New.add( (curr_level, hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("interior_space") ) )
                                                    #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(self.missing_link[link_set][6])) ) )
                                                    print "Added Int. Space: ", curr_level, "interior_space"
                                                    self.property_counter += 1
                                                for city_val in self.test_dict_setup2:
                                                    for individual_item in self.test_dict_setup2[city_val]:
                                                        ind_type = individual_item[1]
                                                        ind_coors = individual_item[2]
                                                        #print "individual_item[0], ", individual_item[0]
                                                        if individual_item[2]:
                                                            # Add SpaceBoundaryN and that it is a type of SpaceBoundary
                                                            USO_New.add( (curr_level, URIRef( str(self.USObase) + str("hasSpaceBoundaryMember") ), URIRef( str(self.USObase) + "SpaceBoundary" + str(element_counter) ) ) )
                                                            USO_New.add( (URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), RDF.type, URIRef( str(self.USObase + "SpaceBoundary") ) ) )
                                                            USO_New.add( (URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))))
                                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(ind_type) ) )
                                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(ind_coors) ) )
                                                            self.Add_On_Dict[URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter)))] = [individual_item[0], URIRef( str(self.USObase + "SpaceBoundary") )]
                                                            self.property_counter += 1
                                                            # Add LOD detail
                                                            if str(self.missing_link[link_set][2]) != "no_LOD":
                                                                USO_New.add( (URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("LOD") ) )
                                                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(self.missing_link[link_set][2])) ) )
                                                                print "Added in SB LOD Area: ", URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), "LOD", str(self.missing_link[link_set][2]), individual_item[1]
                                                                self.property_counter += 1
                                                            element_counter += 1
                                            else: # Such as LOD-1
                                                set_of_surface_datas = self.missing_link[link_set][4]
                                                for city_val in set_of_surface_datas:
                                                    _index = set_of_surface_datas.index(city_val)
                                                    add_on_index = self.missing_link[link_set][3][_index]
                                                    add_on = add_on_index.xpath("../../..", namespaces=self.namespaces)
                                                    # Add SpaceBoundaryN and that it is a type of SpaceBoundary
                                                    USO_New.add( (curr_level, URIRef( str(self.USObase) + str("hasSpaceBoundaryMember") ), URIRef( str(self.USObase) + "SpaceBoundary" + str(element_counter) ) ) )
                                                    USO_New.add( (URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), RDF.type, URIRef( str(self.USObase + "SpaceBoundary") ) ) )
                                                    USO_New.add( (URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))))
                                                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("Coordinates") ) )
                                                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(city_val) ) )
                                                    self.Add_On_Dict[URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter)))] = [add_on, URIRef( str(self.USObase + "SpaceBoundary") )]
                                                    self.property_counter += 1
                                                    # Add LOD detail
                                                    if str(self.missing_link[link_set][2]) != "no_LOD":
                                                        USO_New.add( (URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("LOD") ) )
                                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(self.missing_link[link_set][2])) ) )
                                                        print "Added in SB LOD Area: ", URIRef(str(self.USObase + "SpaceBoundary" + str(element_counter))), "LOD", str(self.missing_link[link_set][2])
                                                        self.property_counter += 1
                                                    element_counter += 1
                                            branch_count += 1
                                else:
                                    print "Reaching str(search_complexity) == fill_in_parents but a_lookup is NOT SpaceBoundary...Add case."







                            complexity_flag = 0
                            if str(search_complexity) == "complex":
                                # "complex" indicates matches found from parent sub-level node to child root, storing child root
                                complexity_flag = 1
                            if str(search_complexity) == "complex_":
                                # "complex_" indicates matches found from parent root to sub-level of child node, storing child root
                                complexity_flag = 2
                                search_complexity = "complex"

                            if str(search_complexity) == "complex":
                                # Relation between this level and the next level found by sub-path to sub-attribute matching, so far following the list_data
                                trackingDict = dict()
                                levelInstanceDict = dict()
                                print "complex", row[0]
                                adjusted_attribute_data_list = list()
                                path_adjustor = ""
                                adjustor_direction = ""
                                for rowd in current_vocab_parsed.query("""SELECT ?o ?x ?y
                                        WHERE { ?s ?d ?o .
                                                ?o ?x ?y. }""",
                                    initBindings={'s' : row[0], 'd' : URIRef(self.rdfs_isDefinedBy)}):
                                    print "rowd: ", rowd
                                    find_end_of_list = 0
                                    if str(rowd[1]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute":
                                        next_blank_node = BNode(rowd[2])
                                        adjusted_attribute_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, adjusted_attribute_data_list, find_end_of_list)
                                        print "adjusted_attribute_data_list ", adjusted_attribute_data_list
                                    elif str(rowd[1]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                                        path_adjustor = str(rowd[2])
                                        #path_adjustor = str( "." + (rowd[2]) )
                                        #print "path_adjustor", path_adjustor
                                    elif str(rowd[1]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#element":
                                        adjustor_direction = str(rowd[2])
                                        #print "adjustor_direction", adjustor_direction
                                    else:
                                        continue

                                if str(path_adjustor[0]) == "*" and self.use_top_computed_node == 1:
                                    path_adjustor = str(self.top_root + path_adjustor.replace("*",""))
                                elif str(path_adjustor[0]) == "*":
                                    path_adjustor = str(self.top_root + path_adjustor.replace("*",""))
                                elif str(path_adjustor[0]) != "*":
                                    path_adjustor = str( "." + path_adjustor )
                                else:
                                    print "path_adjustor case not covered yet"

                                if adjustor_direction == "fdata":
                                    sub_set_for_current_parent = xml_instance.xpath(path_adjustor, namespaces=self.namespaces)
                                    print "1"
                                elif adjustor_direction == "bdata":
                                    sub_set_for_current_parent = tree.xpath(path_adjustor, namespaces=self.namespaces)
                                    print "2"
                                else:
                                    print "add new type of start path adjustment"
                                    sub_set_for_current_parent = list()
                                    sub_set_for_current_parent.append(xml_instance)
                                    print "3"
                                #print "adjustor_direction: ", adjustor_direction, path_adjustor
                                print sub_set_for_current_parent

                                # Collect all the child nodes that belong to this parent
                                # Example: for each Surface
                                branch = dict()
                                att_to_remove = ""
                                next_level = URIRef("")
                                branch_instance_counter = 1
                                for branch_instance in branch_instances:
                                    #print branch_instance
                                    # Example: for each Attribute in Surface
                                    my_instances = list()
                                    for eachAttr in child_attributes:
                                        my_attribute_list = list()
                                        #this_attribute = branch_instance.get(eachAttr.split("#")[1])
                                        if complexity_flag == 1:
                                            this_attribute = branch_instance.get(eachAttr.split("#")[1])
                                        elif complexity_flag == 2:
                                            this_attribute = xml_instance.get(eachAttr.split("#")[1])  # At space level, should be the space id, above should be the surface id
                                        else:
                                            this_attribute = ""
                                            print "this_attribute = 'empty' still"
                                        my_attribute_list.append(eachAttr)
                                        my_attribute_list.append(this_attribute)
                                        my_instances.append(my_attribute_list)
                                        #print "my_instances", my_instances
                                    branch[branch_instance] = my_instances
                                    #print "this branch: ", branch[branch_instance]

                                    for eachAttr in child_attributes:     # For each attribute noted about the child, ex. surface id
                                        if complexity_flag == 1:
                                            this_attribute = branch_instance.get(eachAttr.split("#")[1])
                                            #print "matching theseA: ", eachAttr, branch_instance
                                            #print this_attribute
                                        elif complexity_flag == 2:
                                            this_attribute = xml_instance.get(eachAttr.split("#")[1])  # At space level, should be the space id, above should be the surface id
                                            #print "matching theseB: ", eachAttr, branch_instance
                                            #print "matching theseB: ", this_attribute
                                        else:
                                            this_attribute = ""
                                            print "this_attribute = 'empty' still"

                                        for ajusted_parent_node in sub_set_for_current_parent:  # This compares the attribute tag for child (surface) to where you said the match can be found
                                                                                                # for gbxml gets the id to match to branch from parent path, ifc gets the id to match from child path
                                            # Example: for each Adjusted Space....gbxml is SpaceBoundary
                                            for nextAttr in adjusted_attribute_data_list:
                                                if complexity_flag == 2:
                                                    ajusted_parent_nodes = ajusted_parent_node.xpath("../..", namespaces=self.namespaces)
                                                    ajusted_parent_node2 = ajusted_parent_nodes[0]
                                                    check_attribute1 = ajusted_parent_node2.get(eachAttr.split("#")[1])
                                                    check_attribute2 = branch_instance.get(eachAttr.split("#")[1])
                                                    print "check_attribute1", check_attribute1, check_attribute2

                                                    if check_attribute1 == check_attribute2:  # Talking about the current branch instance
                                                        next_attribute = ajusted_parent_node.get(nextAttr.split("#")[1])
                                                    else:
                                                        next_attribute = ""  # So this should be where the it will ignore or pass if not matched for the current branch instance
                                                else:
                                                    next_attribute = ajusted_parent_node.get(nextAttr.split("#")[1])

                                                #print "matching theseC: ", nextAttr, ajusted_parent_node
                                                print "next_attribute", next_attribute, "and", this_attribute

                                                if this_attribute == next_attribute and next_attribute != None:
                                                    #unused_attribute_instances.remove(this_attribute)
                                                    # Then this child must be related to this parent node, so add a triple
                                                    print "found this to belong by matching: ", this_attribute, next_attribute
                                                    next_level = URIRef( str(self.USObase) + str(row[2].split("#")[1]) + str(branch_instance_counter) )
                                                    current_predicate = URIRef( str(self.USObase) + str(my_full_predicate.split("#")[1]) )
                                                    USO_New.add( (Spatial_Instance_new, current_predicate, next_level) )
                                                    print "-----------ADDED-Comp----------", Spatial_Instance_new, current_predicate, next_level
                                                    MyLDGraph.add( (Spatial_Instance_new, current_predicate, next_level) )
                                                    #print "XXXXXXXXXXXXXXXX added this: ", Spatial_Instance_new, current_predicate, next_level
                                                    # Look thorugh this branch instance and remove all tuples associated with this attr
                                                    att_to_remove = eachAttr
                                                    # After adding the correct next level, track this level in a dict to get relations for next level...
                                                    trackingDict[next_level] = branch_instance, child_attributes
                                                    trackingDict2[next_level] = branch_instance, child_attributes
                                                    levelInstanceDict[branch_instance] = next_level
                                                else:
                                                    next_levelb = URIRef( str(self.USObase) + str(row[2].split("#")[1]) + str(branch_instance_counter) )
                                                    levelInstanceDict[branch_instance] = next_levelb
                                    #print "branch here", len(branch)
                                    #print "trackingDict", len(trackingDict)
                                    #print "levelInstanceDict", len(levelInstanceDict)

                                    for entries in branch[branch_instance]:
                                        if entries[0] == att_to_remove:
                                            #print "to remove", att_to_remove, entries
                                            ent = branch[branch_instance]
                                            ent.remove(entries)
                                            branch[branch_instance] = ent
                                            extra_level = levelInstanceDict[branch_instance]
                                            trackingDict[extra_level] = branch_instance, child_attributes, branch[branch_instance]
                                        else:
                                            #print "skipped ", att_to_remove, entries
                                            extra_level = levelInstanceDict[branch_instance]
                                            trackingDict[extra_level] = branch_instance, child_attributes, branch[branch_instance]
                                    branch_instance_counter += 1
                                #print "branch this is removing certain ones...start here", len(branch)
                                #print "trackingDict", len(trackingDict)
                                #print "after levelInstanceDict", len(levelInstanceDict)
                                self.previous_trackingDict = trackingDict

                            if str(search_complexity) == "linkedP":
                                # Relation between this level and the next level is a set of parent links and matching an existing child path
                                trackingDict = dict()
                                levelInstanceDict = dict()
                                print "linkedP and set tracking dictionary"
                                self.previous_trackingDict = trackingDict

                            if str(search_complexity) == "linkedC":
                                trackingDict = dict()
                                levelInstanceDict = dict()
                                level_processing_pieces_index = 0
                                new_index = 0
                                # Relation between this level and the next level is a set of child links and matching and existing parent path
                                print "linkedC"   #, row[0], d

                                # Get parent definedBy data
                                new_blank_node = URIRef(row[0])
                                round_number = 1
                                temp_d = URIRef( str(d) )
                                if processing_flag_SBE == 0:
                                    while str(new_blank_node) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                        p1a = 0
                                        p2a = 0
                                        p3a = 0
                                        p4a = 0
                                        p1 = ""
                                        p2_list = list()
                                        p3_list = list()
                                        #print "using: new_blank_node ", new_blank_node
                                        if round_number == 1:
                                            for rowg in current_vocab_parsed.query("""SELECT ?x ?y
                                                    WHERE { ?parent ?d ?o .
                                                            ?o ?x ?y . }""",
                                                initBindings={'parent' : new_blank_node, 'd' : temp_d, 'r' : RDF.type}):
                                                #print "rowg", rowg
                                                end = 0
                                                if str(rowg[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#element":
                                                    p1 = str(rowg[1])
                                                    p1a = 1
                                                    #print "p1", p1
                                                if str(rowg[0]) == str(self.rdfs_isDefinedBy):
                                                    p4a = 1
                                                    if str(rowg[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                                        new_blank_node = BNode(rowg[1])
                                                        #print "next blank: ", new_blank_node
                                                        new_index = level_processing_pieces_index + 1
                                                    else:
                                                        new_blank_node = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#nil")
                                                        new_index = None
                                                if str(rowg[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute":
                                                    p2 = BNode(rowg[1])
                                                    p2a = 1
                                                    p2_list, e_find_end_of_list_now, node = self.collect_list_items(p2, current_vocab_parsed, p2_list, end)
                                                    #print "p2_list", p2_list
                                                if str(rowg[0]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                                                    p3 = BNode(rowg[1])
                                                    p3a = 1
                                                    p3_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(p3, current_vocab_parsed, p3_list, end)
                                                    #print "p3_list", p3_list
                                            round_number = 2
                                            if p1a == 1 and p2a == 1 and p3a == 1 and p4a == 1:
                                                #print "whatdaweget:", p1, p2_list, p3_list, new_index
                                                level_processing_pieces[level_processing_pieces_index] = (p1, p2_list, p3_list, new_index)
                                                level_processing_pieces_index += 1
                                            continue
                                        if round_number == 2:
                                            for rowh in current_vocab_parsed.query("""SELECT ?x ?y
                                                    WHERE { ?parent ?x ?y . }""",
                                                initBindings={'parent' : new_blank_node, 'd' : temp_d, 'r' : RDF.type}):
                                                #print "rowg", rowh
                                                end = 0
                                                if str(rowh[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#element":
                                                    p1 = str(rowh[1])
                                                    p1a = 1
                                                    #print "p1", p1
                                                if str(rowh[0]) == str(self.rdfs_isDefinedBy):
                                                    p4a = 1
                                                    if str(rowh[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                                        new_blank_node = BNode(rowh[1])
                                                        #print "next blank: ", new_blank_node
                                                        new_index = level_processing_pieces_index + 1
                                                    else:
                                                        new_blank_node = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#nil")
                                                        new_index = None
                                                if str(rowh[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute":
                                                    p2 = BNode(rowh[1])
                                                    p2a = 1
                                                    p2_list, e_find_end_of_list_now, node = self.collect_list_items(p2, current_vocab_parsed, p2_list, end)
                                                    #print "p2_list", p2_list
                                                if str(rowh[0]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                                                    p3 = BNode(rowh[1])
                                                    p3a = 1
                                                    p3_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(p3, current_vocab_parsed, p3_list, end)
                                                    #print "p3_list", p3_list
                                            if p1a == 1 and p2a == 1 and p3a == 1 and p4a == 1:
                                                #print "whatdaweget:", p1, p2_list, p3_list, new_index
                                                level_processing_pieces[level_processing_pieces_index] = (p1, p2_list, p3_list, new_index)
                                                level_processing_pieces_index += 1

                                #print "level_processing_pieces", len(level_processing_pieces)
                                #for i in level_processing_pieces:
                                #    print i, level_processing_pieces[i]

                                #xml_instance        # The Surface for example...<Element {http://www.gbxml.org/schema}Surface at 0x6489168>
                                #root_att_data_list  # From Vocabulary file: If Surface then it is: ['http://www.gbxml.org/schema#id', 'http://www.gbxml.org/schema#constructionIdRef']
                                #child_attributes    # From Vocabulary file: Set of vocabulary attributes to use to query tree
                                #branch_instances    #
                                #previous_trackingDict[next_level]  # Info from previous graph iteration

                                #print "now handling", xml_instance
                                original_level_data = list()
                                current_vocab_term = ""
                                #print "length ", len(self.previous_trackingDict)
                                for i in self.previous_trackingDict:
                                    #print "previous_trackingDict: ", i, self.previous_trackingDict[i]
                                    #print xml_instance
                                    if self.previous_trackingDict[i][0] == xml_instance:
                                        #print "getting data from :", self.previous_trackingDict[i][0]
                                        #matching_tree_instance = self.previous_trackingDict[i][0]
                                        current_vocab_term = str(i).split("#")[1]
                                        #parent_attribute_instance_list = self.previous_trackingDict[i][2]
                                        original_level_data = self.previous_trackingDict[i]
                                # Now loop through level_processing_pieces and match layer to layer
                                entry_check = 0
                                first_flag = 0
                                entry_counter = 0
                                #print "original_level_data", original_level_data
                                current_level_data = original_level_data[2]
                                new_level_data = list()
                                prev_current_level_data = list()
                                while entry_check != None:
                                    if first_flag == 0:
                                        entry_check = level_processing_pieces[entry_check][3]  # First is always the [0][last-item] for this processing
                                        first_flag = 1
                                        entry_counter += 1
                                    else:
                                        entry_check = level_processing_pieces[entry_check][3]  # Rest is always the [0][last-item] for this processing
                                        entry_counter += 1
                                    if level_processing_pieces[entry_counter-1][0] == "fdata":
                                        print "add fdata part to the LinkedC type of processing where data is nested"
                                    elif level_processing_pieces[entry_counter-1][0] == "bdata":
                                        # Leave original_level_data and use current_level_data to make new_level_data
                                        new_level_data = list()
                                        cpath = str(level_processing_pieces[entry_counter-1][2][0])
                                        if str(cpath[0]) == "*" and self.use_top_computed_node == 1:
                                            cpath = str(self.top_root + str(cpath))
                                        child_paths = tree.xpath(cpath, namespaces=self.namespaces)
                                        for child_path in child_paths:
                                            collect_associated_attribute = str(level_processing_pieces[entry_counter-1][1][0])
                                            next_attribute = child_path.get(collect_associated_attribute.split("#")[1])
                                            for possibilities in current_level_data:
                                                #if possibilities[1] == None:
                                                #    print "Added nothing at this time due to xml error type None for next layer..."
                                                if str(next_attribute) == str(possibilities[1]):
                                                    next_path = str(".") + str(level_processing_pieces[entry_counter-1][2][1])
                                                    if str(next_path[0]) == "*" and self.use_top_computed_node == 1:
                                                        next_path = str(self.top_root + str(next_path))
                                                    next_instance_set_to_follow = child_path.xpath(next_path, namespaces=self.namespaces)
                                                    for each_instance in next_instance_set_to_follow:
                                                        new_collect_associated_attribute = str(level_processing_pieces[entry_counter-1][1][1])
                                                        new_attribute = each_instance.get(new_collect_associated_attribute.split("#")[1])
                                                        x = new_collect_associated_attribute
                                                        y = new_attribute
                                                        z = each_instance
                                                        new_level_data.append((x,y,z))
                                                        #print "added: ", new_level_data
                                        prev_current_level_data = current_level_data
                                        current_level_data = new_level_data
                                    else:
                                        print "add ?? part to the LinkedC type of processing where data is nested"
                                #print "original_level_data: ", original_level_data
                                #print "prev_current_level_data: ", prev_current_level_data
                                #print "current_level_data: ", current_level_data
                                if not prev_current_level_data:
                                    print "No next level data available so not adding triples"
                                else:
                                    print "current_level_data"
                                    #print current_level_data
                                    for a_boundary_element in prev_current_level_data:
                                        print "a_boundary_element", a_boundary_element
                                        sbe_s = URIRef( str(self.USObase) + current_vocab_term )
                                        sbe_o = URIRef( str(self.USObase) + str(row[2].split("#")[1]) + str(element_bound_counter) )
                                        sbe_p = URIRef( str(self.USObase) + str(my_full_predicate.split("#")[1]) )
                                        sbe_o2 = URIRef( str(self.USObase) + str(hasObject.split("#")[1]) )
                                        USO_New.add( (sbe_s, sbe_p, sbe_o) )
                                        USO_New.add( (sbe_o, RDF.type, sbe_o2) )
                                        self.Add_On_Dict[sbe_o] = [a_boundary_element[2], sbe_o2]
                                        print "testing to add1", a_boundary_element
                                        print "-----------ADDED-sbe----------", sbe_s, sbe_p, sbe_o
                                        print "-----------ADDED-sbe----------", sbe_o, RDF.type, sbe_o2
                                        MyLDGraph.add( (sbe_s, sbe_p, sbe_o) )
                                        MyLDGraph.add( (sbe_o, RDF.type, sbe_o2) )
                                        #print "XXXXXXXXXXXXXXXX added this: ", sbe_s, sbe_p, sbe_o
                                        # If at SpaceBoundary then add the remaining level for the xml_instance_tracking dictionary
                                        if str(a_lookup) == "SpaceBoundary":
                                            self.xml_instance_tracking[sbe_o] = [ a_boundary_element[1], sbe_o, "SpaceBoundaryElement", prev_current_level_data, original_level_data[0], 0, 0 ]
                                        element_bound_counter += 1


                            if str(search_complexity) == "LinkedG":
                                # When you need the geometry processing methods to find children matches cannot be found otherwise
                                # Plus need to do this in IFC for SpaceBoundaryElements becasue else will not have
                                # updated self.xml_instance_tracking[] when go to assemble geometry information
                                #print "getting to str(search_complexity) == LinkedG", branch_instances
                                levelInstanceDict = dict()

                                currentDataPathsList, set_types_information = self.findCurrentDataPathsList(current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, defined_data_list, MyLDGraph) # Sending defined_data_list instead of root geometry because set direction does not come from geometry here
                                #print set_types_information
                                test_dict_setup = dict()
                                data_dict_to_generate_next_tree_layer, next_p_list, LOD_node = self.processCurrentDataPathsList(currentDataPathsList, set_types_information, a_lookup, tree, this_file_type, test_dict_setup)
                                #print "next_p_list: ", next_p_list
                                #print "1st Run Output:", set_types_information, a_lookup, tree
                                #for d in data_dict_to_generate_next_tree_layer:
                                #    print d, data_dict_to_generate_next_tree_layer[d]
                                #-----------------------------------------------------------------------------------------------

                                if this_file_type == "citygml" and a_lookup == "Space": # Because this is a pattern where spaces have to be created based on missing_link that gives parents and children
                                    data_dict_to_generate_next_tree_layer = dict()
                                #print "data_for_surface_dict from Run1: "  # Seen so far: ['center_point', 'x_center_offset', 'y_center_offset', 'depth']
                                original_level_data = ""
                                # Use data_for_surface_dict of assemblies per parent to make child connections
                                if len(xml_instances) == len(data_dict_to_generate_next_tree_layer):
                                    for i in data_dict_to_generate_next_tree_layer:
                                        #original_level_data = self.previous_trackingDict[i]
                                        for material_listed in data_dict_to_generate_next_tree_layer[i]:
                                            if material_listed[1] != []:
                                                for each_material in material_listed[1]:
                                                    current_vocab_term = material_listed[2]
                                                    if str(self.USObase) in str(current_vocab_term):
                                                        sbe_s = URIRef(current_vocab_term )
                                                    else:
                                                        sbe_s = URIRef( str(self.USObase) + current_vocab_term )
                                                    sbe_o = URIRef( str(self.USObase) + str(row[2].split("#")[1]) + str(element_bound_counter) )
                                                    sbe_p = URIRef( str(self.USObase) + str(my_full_predicate.split("#")[1]) )
                                                    sbe_o2 = URIRef( str(self.USObase) + str(hasObject.split("#")[1]) )
                                                    USO_New.add( (sbe_s, sbe_p, sbe_o) )
                                                    USO_New.add( (sbe_o, RDF.type, sbe_o2) )
                                                    if str(type(each_material[0]).__name__) != "list":  # We see cases like this where ther eis one material in the surface so one set returned instead a list of sets
                                                        self.Add_On_Dict[sbe_o] = [each_material[1], sbe_o2]
                                                        print "testing to add2", each_material
                                                        trackingDict[sbe_o] = [each_material], child_attributes
                                                    else:
                                                        self.Add_On_Dict[sbe_o] = [each_material[0][1], sbe_o2]
                                                        print "testing to add2", each_material[0]
                                                        trackingDict[sbe_o] = each_material, child_attributes
                                                    print "-----------ADDED-WILL----------", sbe_s, sbe_p, sbe_o
                                                    print "-----------ADDED-WILL----------", sbe_o, RDF.type, sbe_o2
                                                    MyLDGraph.add( (sbe_s, sbe_p, sbe_o) )
                                                    MyLDGraph.add( (sbe_o, RDF.type, sbe_o2) )
                                                    element_bound_counter += 1
                                                    # If at SpaceBoundary then add the remaining level for the xml_instance_tracking dictionary
                                                    if len(material_listed[1]) == 1:
                                                        new_child_loc = each_material[1]
                                                    else:
                                                        new_child_loc = each_material[0][1]
                                                    if str(a_lookup) == "SpaceBoundary":
                                                        #print "added each_material[0][1] to self.xml_instnace_tracking", material_listed
                                                        #print "saving ", new_child_loc
                                                        self.xml_instance_tracking[sbe_o] = [ new_child_loc, sbe_o, "SpaceBoundaryElement", i, original_level_data, 0, 0 ]

                                                    #trackingDict[sbe_o] = each_material, child_attributes
                                                    #levelInstanceDict[branch_instance] = next_level

                                                    # Leaving here cause it is an instance of the processCurrentDataPathsList function but may not be needed here
                                                    #if a_lookup == "SpaceCollection":
                                                        #Then adding an extra triple to define between the Buildings, ReliefFeatures, and so on...(just descriptive else will be lost info)
                                                        #USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                                        #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("Collection_Type") ) )
                                                        #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(spatialThingUsing)) ) )
                                                        #print "Added: ", self.property_counter, "Collection_Type", str(spatialThingUsing)
                                                        #self.property_counter += 1
                                                    #print "LOD_node", LOD_node
                                                    #if LOD_node != "no_LOD":
                                                    #    print "reaching the lod triples1"
                                                    #    # Then there was a LOD to collect so add it as a triple for context later
                                                    #    USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(element_bound_counter))) )
                                                    #    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(element_bound_counter)), hasType, Literal("LOD") ) )
                                                    #    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(element_bound_counter)), hasValue, Literal(str(LOD_node)) ) )
                                                    #    element_bound_counter += 1
                                self.previous_trackingDict = trackingDict


                    new_tracking_dict = dict()
                    find_differences = list()
                    temp_instances = branch_instances
                    #print "before:...", self.parent_branch_count
                    if self.currentSpaceCollection != "blah" and self.currentSpaceCollection != "set":
                        if str(a_lookup) == "Space" and this_file_type != "citygml":
                            for t in trackingDict2:
                                if trackingDict2[t][0] in branch_instances:
                                    find_differences.append(trackingDict2[t][0])
                            for instance in find_differences:
                                for b in temp_instances:
                                    if b == instance:
                                        _index = temp_instances.index(b)
                                        del temp_instances[_index]
                            #print "last_added_element", last_added_element, len(branch_instances), self.parent_branch_count[a_lookup]
                            if last_added_element == self.parent_branch_count[a_lookup]:
                                #print "yEs"
                                for rest in temp_instances:
                                    #print "YeS", len(temp_instances), temp_instances
                                    _indexB = temp_instances.index(rest)
                                    #print "indexB: ", temp_instances[_indexB], len(levelInstanceDict)

                                    indexB = levelInstanceDict[temp_instances[_indexB]]

                                    next_level = URIRef( str(self.USObase) + str(indexB.split("#")[1]) )
                                    current_predicate = URIRef( str(self.USObase) + str(my_full_predicate.split("#")[1]) )
                                    currentSpaceCollection = URIRef( str(self.USObase) + self.currentSpaceCollection )
                                    USO_New.add( (currentSpaceCollection, current_predicate, next_level) )
                                    print "-----------ADDED--A---------", currentSpaceCollection, current_predicate, next_level
                                    MyLDGraph.add( (currentSpaceCollection, current_predicate, next_level) )
                                    #print "renest issue: ", currentSpaceCollection, current_predicate, next_level
                                    #last_added_element += 1
                            if self.current_predicateAbove != "" and self.currentSpaceCollectionAbove != "":
                                self.branch_instance_counter_spaces += 1
                                next_lev = URIRef( str(self.USObase) + str(a_lookup) + str(self.branch_instance_counter_spaces) )
                                USO_New.add( (self.currentSpaceCollectionAbove, self.current_predicateAbove, next_lev) )
                                print "-----------ADDED--B---------", self.currentSpaceCollectionAbove, self.current_predicateAbove, next_lev
                                MyLDGraph.add( (self.currentSpaceCollectionAbove, self.current_predicateAbove, next_lev) )
                                #print "renest issue: ", self.currentSpaceCollectionAbove, self.current_predicateAbove, next_lev
                                #print "self.branch_instance_counter_spaces", self.branch_instance_counter_spaces
                            else:
                                print "current_predicateAbove and currentSpaceCollectionAbove not set..."
                            last_added_element += 1

                        elif str(a_lookup) == "SpaceCollection":
                            self.current_predicateAbove = URIRef( str(self.USObase) + str(my_full_predicate.split("#")[1]) )
                            self.currentSpaceCollectionAbove = URIRef( str(self.USObase) + self.currentSpaceCollection )
                            self.previous_branch_instance_count = len(branch_instances)
                        else:
                            print "passed"
            else:
                print "Instance querying needs additional data type catch"
            processing_flag_SBE = 1
            #at this current level spatial-part, need to look at some attribute to match to previous level spatial thing
        return

    def addCoordinateData(self, current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometry, MyLDGraph):
        # Add Coordinate data based on types of 2D, 3D, and fromCalc (ex, where the coordinates need to be generated from external calculations based on values in the instance XML)

        Property = URIRef(str(self.USObase) + "Property")
        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")
        #print "testing current_data_type", a_lookup, current_data_type

        if a_lookup == "SpaceBoundary" and this_file_type == "citygml":
            # This case was handled by a fill_parents approach
            return

        # Check for the existence of geometry data for this level
        #print "hasRootGeometry in addCoordinateData", hasRootGeometry
        #print "self.xml_instance_tracking ", len(self.xml_instance_tracking), self.xml_instance_tracking     # self.xml_instance_tracking[xml_instance] = [ xml_instance, Spatial_Instance_new, str(a_lookup), branch_instances ]

        hasGeometryComponents = 0
        if hasRootGeometry != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
            #print "processing root geometries"
            hasGeometryComponents = 1
            # For each geometry type in hasRootGeometry list get data
            for eachGeometryType in hasRootGeometry:
                coorPaths = list()
                coorInfo = list()
                a = 0
                b = 0
                c = 0
                dimension = ""
                full_dimension = ""
                currentDataPathsList = list()
                for rowj in current_vocab_parsed.query("""SELECT ?x ?y
                        WHERE { ?geom ?x ?y . }""",
                    initBindings={'geom' : BNode(eachGeometryType), 't' : RDF.type, 'G' : URIRef(self.geo_base + "Geometry")}):
                    # Foregoing fdata and bdata element types and assume all will be a follow the current path method
                    end = 0
                    if str(rowj[0]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                        g2 = BNode(rowj[1])
                        a = 1
                        coorPaths, e_find_end_of_list_now, node = self.collect_list_items(g2, current_vocab_parsed, coorPaths, end)
                    if str(rowj[0]) == "http://www.w3.org/2000/01/rdf-schema#label":
                        b = 1
                        full_dimension = str(rowj[1])
                        if "3D" in full_dimension:
                            dimension = "3D"
                        if "2D" in full_dimension:
                            dimension = "2D"
                    if str(rowj[0]) == "http://www.w3.org/2000/01/rdf-schema#isDefinedBy":
                        c = 1
                        list_type_definedBy = 0
                        # Then there is a list of defined by data, at this point should be for geometry data
                        find_end_of_list = 0
                        next_blank_node = BNode(rowj[1])
                        defined_data_list = list()
                        defined_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, defined_data_list, find_end_of_list)
                        #print "defined_data_list here", defined_data_list, next_blank_node
                        if len(defined_data_list) > 1:
                            if str(rowj[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(rowj[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                defined_data_list.append(str(rowj[1]))
                            if str(rowj[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(rowj[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                find_end_of_list = 0
                                next_blank_node = BNode(rowj[1])
                                defined_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, defined_data_list, find_end_of_list)
                            list_type_definedBy = 1
                        currentDataPathsListA = list()
                        current_data_type_list = list() # To give the set to pass to the function, can be used individually or can use currentDataPathsList instead
                        attribute_data_list_list = list() # To give the set to pass to the function, can be used individually or can use currentDataPathsList instead
                        transformationProperty_data_list_list = list() # To give the set to pass to the function, can be used individually or can use currentDataPathsList instead
                        set_types_information = list()
                        #print "defined_data_list", defined_data_list
                        for d in defined_data_list:
                            # For each contributing blank node to the set of geometry features (typical so far for ifcxml querying)
                            attribute_data_list = list()
                            transformationProperty_data_list = list()
                            current_data_type = ""
                            IsDefinedByNext = ""
                            temp_IsDefinedByNext = ""
                            a = 0
                            b = 0
                            c = 0
                            de = 0
                            while str(IsDefinedByNext) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                for row in current_vocab_parsed.query("""SELECT ?x ?y
                                        WHERE { ?d ?x ?y .}""",
                                    initBindings={'d' : BNode(d)}):
                                    #print "other data - attribute - transProperty making set_types: ", row
                                    find_end_of_list_now = 0
                                    if row[0] == URIRef(str(RDF.type)):  # So this should only be recorded or required if it exists
                                        # So systematically should only include at the end of a set of paths leading to data
                                        set_types_information.append(str(row[1]))
                                        #print "added set_types_information", str(row[1])
                                    if row[0] == URIRef(str(self.rdfs_isDefinedBy)):
                                        temp_IsDefinedByNext = str(row[1])
                                        de = 1
                                    if row[0] == URIRef("https://www.w3.org/TR/xslt-30/schema-for-xslt30#element"):
                                        current_data_type = str(row[1])
                                        a = 1
                                    if row[0] == URIRef("https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute"):
                                        attribute_data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(row[1], current_vocab_parsed, attribute_data_list, find_end_of_list_now)
                                        b = 1
                                    if row[0] == URIRef("https://www.w3.org/2003/g/data-view#transformationProperty"):
                                        transformationProperty_data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(row[1], current_vocab_parsed, transformationProperty_data_list, find_end_of_list_now)
                                        #transformationProperty_data_list_list.append(transformationProperty_data_list)
                                        #transformationProperty_data_list = list()

                                        # The last element here needs to be checked for being string or some other blank node
                                        # If string just collect and continue, but if a blank node, then use the set underneath that to fill in this path part from a set of options
                                        # For example, path to surface geometries could be one of several path options so have to check (ex. IfcSlab, IfcWall, IfcRoof versus GBXML:surface-coordiantes)

                                        #1)
                                        # Check if the first is "replace", means last round was a blank node, match was found and need to replace to continue searching
                                        # replace transformationProperty_data_list[first("replace")] with previous path definition
                                        #2)
                                        # So if it is a blank node, need to first get list of possibilities
                                        # Then test each to see what was present in the IFC for this surface
                                        # Once found, replace transformationProperty_data_list[last(the blank node)] with the found path string
                                        # If this happens then also need a solution to next iteration because the start path will change as well.....
                                        # Possibly hold onto the matching path and use "replace" in the next RDF description

                                        c = 1
                                    if a == 1 and b == 1 and c == 1 and de == 1:
                                        # String List List
                                        #print "Now: ", IsDefinedByNext, current_data_type, attribute_data_list, transformationProperty_data_list
                                        IsDefinedByNext = temp_IsDefinedByNext
                                        currentDataPathsListA.append([IsDefinedByNext, current_data_type, attribute_data_list, transformationProperty_data_list])
                                        current_data_type_list = list()
                                        attribute_data_list = list()
                                        transformationProperty_data_list = list()
                                        a = 0
                                        b = 0
                                        c = 0
                                        de = 0
                                        d = IsDefinedByNext
                                        if str(IsDefinedByNext) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                            currentDataPathsList.append(currentDataPathsListA)
                                            currentDataPathsListA = list()
                                            #print "currentDataPathsList", len(currentDataPathsList), currentDataPathsList
                    #if a == 1 and b == 1 and c == 1:
                    #    coorInfo = (dimension, coorPaths)


                # Call appropriate functions or collect coordinate data directly as
                this_level = 0
                that_level = 0
                if "some_function_this_level" in coorPaths:
                    this_level = 1
                if "some_function_next_level" in coorPaths:
                    that_level = 1

                if this_level == 1 and dimension == "2D":  # 2D data within this level using this level values and external function
                    #print "case 1  ...same processing as for 3D, but need to add here in case there is case with no 3D option"
                    #currentDataPathsList ---> List of sets of: (IsDefinedByNext, current_data_type, attribute_data_list, transformationProperty_data_list)
                    # For each data that makes up a multi-part set of measurements for example: IFC gives orientation/centerpoint/XDim/YDim...maybe ZDim
                    #print "reaching the depth-search version, len(currentDataPathsList): ", len(currentDataPathsList)

                    print "2nd Run this_level == 1 and dimension == 2D"
                    test_dict_setup = dict()
                    data_dict_to_generate_next_tree_layer, next_p_list, LOD_node = self.processCurrentDataPathsList(currentDataPathsList, set_types_information, a_lookup, tree, this_file_type, test_dict_setup)

                    #print "2nd Run Output:", set_types_information, a_lookup, tree
                    #for d in data_dict_to_generate_next_tree_layer:
                    #    print d, data_dict_to_generate_next_tree_layer[d]

                    #-----------------------------------------------------------------------------------------------

                    if this_file_type == "citygml" and a_lookup == "Space": # Because this is a pattern where spaces have to be created based on missing_link that gives parents and children
                        data_dict_to_generate_next_tree_layer = dict()
                    #print "after data_for_surface_dict 2nd Run: "  # Seen so far: ['center_point', 'x_center_offset', 'y_center_offset', 'depth']
                    for i in data_dict_to_generate_next_tree_layer:
                        #print i, data_dict_to_generate_next_tree_layer[i]
                        #print self.xml_instance_tracking
                        dataType, re_made_data = self.find__external_function(data_dict_to_generate_next_tree_layer[i], dimension, a_lookup, this_file_type)

                        for aSpatialThing in self.xml_instance_tracking:
                            if a_lookup == self.xml_instance_tracking[aSpatialThing][2]:
                                spatialThingUsing = self.xml_instance_tracking[aSpatialThing][0]
                                if self.xml_instance_tracking[aSpatialThing][0] == i:
                                    # Add Triples Now
                                    #print "test: ", self.xml_instance_tracking[aSpatialThing], spatialThingUsing
                                    with_subject = str(self.xml_instance_tracking[aSpatialThing][1])
                                    if str(re_made_data) != "":
                                        USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                        MyLDGraph.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(re_made_data)) ) )
                                        self.property_counter += 1
                                        print "-----------ADDED--E---------", (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter)))
                                        print "-----------ADDED--E---------", (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) )
                                        print "-----------ADDED--E---------", (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(re_made_data)) )
                                        elem = self.xml_instance_tracking[aSpatialThing]
                                        elem[5] = re_made_data  # Place left to track [2D is [5], 3D is [6]] parent coordinate data
                                        self.xml_instance_tracking[aSpatialThing] = elem
                                    #print "stored ", self.xml_instance_tracking[aSpatialThing]
                                    if a_lookup == "SpaceCollection" and this_file_type == "citygml":
                                        #Then adding an extra triple to define between the Buildings, ReliefFeatures, and so on...(just descriptive else will be lost info)
                                        USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("Collection_Type") ) )
                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(spatialThingUsing)) ) )
                                        print "Added: ", self.property_counter, "Collection_Type", str(spatialThingUsing)
                                        self.property_counter += 1
                                    #print "LOD_node", LOD_node
                                    if LOD_node != "no_LOD":
                                        print "reaching the lod triples2"
                                        # Then there was a LOD to collect so add it as a triple for context later
                                        USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("LOD") ) )
                                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(LOD_node)) ) )
                                        print "Added: ", URIRef(with_subject), "LOD", str(LOD_node)
                                        self.property_counter += 1
                        print "self.property_counter A",self.property_counter
                    '''
                    for i in data_dict_to_generate_next_tree_layer:
                        print i, data_dict_to_generate_next_tree_layer[i]
                        print self.xml_instance_tracking

                        for aSpatialThing in self.xml_instance_tracking:
                            if i == self.xml_instance_tracking[aSpatialThing][0]:
                                spatialThingUsing = self.xml_instance_tracking[aSpatialThing][1]
                                print "spatialThingUsing", spatialThingUsing

                        dataType, re_made_data = self.find__external_function(data_dict_to_generate_next_tree_layer[i], dimension, a_lookup, this_file_type)

                        # Add Triples Now
                        #print "test: ", self.xml_instance_tracking[spatialThingUsing], spatialThingUsing
                        with_subject = str(self.xml_instance_tracking[spatialThingUsing][1])
                        USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                        MyLDGraph.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(re_made_data)) ) )
                        self.property_counter += 1
                        print "-----------ADDED-----------", (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter)))
                        print "-----------ADDED-----------", (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) )
                        print "-----------ADDED-----------", (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(re_made_data)) )
                        elem = self.xml_instance_tracking[spatialThingUsing]
                        elem[5] = re_made_data  # Place left to track [2D is [5], 3D is [6]] coordinate data
                        self.xml_instance_tracking[spatialThingUsing] = elem
                        #print "stored ", self.xml_instance_tracking[aSpatialThing]
                    '''

                elif this_level == 1 and dimension == "3D":  # 3D data within this level using this level values and external function
                    #print "somewhere see if 2D data exists for this thing then can recall to get 3D when data is insufficient to make 3D from what is given but indicated needs external function"
                    print "case 2a", len(currentDataPathsList)
                    #if full_dimension == "3DM":
                    #    print "new condition: 3DM"
                    if currentDataPathsList == None or len(currentDataPathsList) == 0:
                        process_structure = dict()
                        for aSpatialThing in self.xml_instance_tracking:
                            if a_lookup == self.xml_instance_tracking[aSpatialThing][2]:
                                new_list = list()
                                # The last list item in transformationProperty_data_list should be the item that holds the value data in the xml
                                if str(transformationProperty_data_list[0][0]) == "*" and self.use_top_computed_node == 1:
                                    transformationProperty_data_list[0] = str(self.top_root + str(transformationProperty_data_list[0]))
                                branch_instances = tree.xpath(str(transformationProperty_data_list[0]), namespaces=self.namespaces)
                                for item in branch_instances:
                                    item_id = item.get(attribute_data_list[0].split("#")[1])
                                    if str(item_id) == str(self.xml_instance_tracking[aSpatialThing][0]):
                                        prop_needed = "." + str(transformationProperty_data_list[-1])
                                        if str(prop_needed[0]) == "*" and self.use_top_computed_node == 1:
                                            prop_needed = str(self.top_root + prop_needed)
                                        prop_value = float(item.xpath(prop_needed, namespaces=self.namespaces)[0].text)
                                        prev_parent_instance = self.xml_instance_tracking[aSpatialThing][4]
                                        parent_id = prev_parent_instance.get(attribute_data_list[0].split("#")[1])
                                        if str(prop_needed[0]) == "*" and self.use_top_computed_node == 1:
                                            prop_needed = str(self.top_root + prop_needed)
                                        myProp = item.xpath(prop_needed, namespaces=self.namespaces)
                                        for value in myProp:
                                            prop_unit = value.get(attribute_data_list[1].split("#")[1])

                                        spatial_testing_item = ""
                                        for i in self.previous_trackingDict:
                                            if self.previous_trackingDict[i][0] == prev_parent_instance:
                                                spatial_testing_item = URIRef( str(i) )
                                        # See what 2D or 3D data exists in xml_instance_tracking to use external modules
                                        if self.xml_instance_tracking[spatial_testing_item][6] != 0:
                                            # Then 3D data exists for this parent, and this function should work:
                                            print "3D case for needing external function not yet entered for same-level data"
                                        if self.xml_instance_tracking[spatial_testing_item][5] != 0:
                                            # Then 2D data exists for this parent, and this function should work:
                                            parent_coors = self.xml_instance_tracking[spatial_testing_item][5]
                                            #print "parent_coors", parent_coors
                                            if parent_id in process_structure:
                                                ent = process_structure[parent_id]
                                                new_tuple = [item_id, prop_value, ent[0][2], prev_parent_instance]
                                                ent.append(new_tuple)
                                                process_structure[parent_id] = ent
                                            else:
                                                new_tuple = [item_id, prop_value, parent_coors, prev_parent_instance]
                                                new_list.append(new_tuple)
                                                process_structure[parent_id] = new_list
                        for i in process_structure:
                            print "o", process_structure[i]
                            t = coorsFromVocabs()
                            curr_parent_coors = process_structure[i][0][2]
                            prev_parent_instance = process_structure[i][0][3]
                            # Translate thickness meters into feet for each entry in SurfaceToMaterialList
                            thicknessesFromMetersToFeet = t.unitTranslate(process_structure[i], i)
                            tempi = process_structure[i]
                            tempi.append(thicknessesFromMetersToFeet)
                            process_structure[i] = tempi

                            # Organize lengths and coordinates proportionally to devise which on is the thickness coordinate
                            proportionDict, hwtOrderDict = t.organizeThicknessesProportionally(prev_parent_instance, thicknessesFromMetersToFeet, curr_parent_coors, self.namespaces)

                            surface3D, MaterialLayerCoodinateSet = t.materialLayers(USO_New, curr_parent_coors, str(i), proportionDict, hwtOrderDict, this_file_type)

                            #if parent still does not have 3D data, then add triples for
                            #    print "surface3D", surface3D

                            #print "par" , process_structure[i][0][3]  # parent coordinates
                            spatial_testing_item = ""
                            for i in self.previous_trackingDict:
                                if self.previous_trackingDict[i][0] == prev_parent_instance:
                                    spatial_testing_item = URIRef( str(i) )

                            _index = self.object_order.index(a_lookup)  # Temporarily get the previous type of Node to do this processing here
                            temp_parent_sub = self.object_order[_index-1]
                            if self.xml_instance_tracking[spatial_testing_item][6] == 0:
                                # Then no spatial data for parent for 3D coordinates
                                with_subject = str(self.xml_instance_tracking[spatial_testing_item][1])
                                triple_data_type = URIRef( str(self.USObase) + str(str(dimension) + "Data" + str(with_subject).split("#")[1]) )
                                dataType = "unset"
                                if full_dimension == "3DC":
                                    dataType = str(dimension) + str(temp_parent_sub) + "Coordinates"  # Ex. "3DSpaceCoordinates"
                                elif full_dimension == "3DM":
                                    dataType = str(dimension) + str(temp_parent_sub) + "Measurements"  # Ex. "3DSpaceMeasurements"
                                else:
                                    print "need to set dataType better"
                                #USO_New.add( (URIRef(with_subject), hasProperty, triple_data_type) )
                                #USO_New.add( (triple_data_type, RDF.type, Property) )
                                #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), RDF.type, triple_data_type) )
                                USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                MyLDGraph.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(surface3D)) ) )
                                print "-----------Added_3D_Case----------", URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))
                                print "-----------Added_3D_Case----------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, dataType
                                print "-----------Added_3D_Case----------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, str(surface3D)
                                self.property_counter += 1
                                elem = self.xml_instance_tracking[spatial_testing_item]
                                elem[6] = surface3D  # Place left to track [2D, 3D] parent coordinate data
                                self.xml_instance_tracking[spatial_testing_item] = elem
                            print "self.property_counter G",self.property_counter

                            #print "dealing with ", thicknessesFromMetersToFeet
                            # Add element layer data, which is the main addition for this condition
                            for aSpatialThing in self.xml_instance_tracking:
                                for j in thicknessesFromMetersToFeet:
                                    #print "j", thicknessesFromMetersToFeet[j]
                                    for k in thicknessesFromMetersToFeet[j]:
                                        if k[0] == self.xml_instance_tracking[aSpatialThing][0]:
                                            #print "matched by # ", k[0], aSpatialThing # then add each of material coor sets to this aSpatialThing # aSpatialThing == SpaceBoundaryElement12
                                            for x in MaterialLayerCoodinateSet:
                                                if self.xml_instance_tracking[aSpatialThing][6] == 0:
                                                    # Then no spatial data for current element for 3D coordinates so add them
                                                    with_subject = str(self.xml_instance_tracking[aSpatialThing][1])
                                                    triple_data_type = URIRef( str(self.USObase) + str(str(dimension) + "Data" + str(with_subject).split("#")[1]) )
                                                    dataType = "unset"
                                                    if full_dimension == "3DC":
                                                        dataType = str(dimension) + str(a_lookup) + "Coordinates"  # Ex. "3DSpaceCoordinates"
                                                    elif full_dimension == "3DM":
                                                        dataType = str(dimension) + str(a_lookup) + "Measurements"  # Ex. "3DSpaceMeasurements"
                                                    else:
                                                        print "need to set dataType better"
                                                    #USO_New.add( (URIRef(with_subject), hasProperty, triple_data_type) )
                                                    #USO_New.add( (triple_data_type, RDF.type, Property) )
                                                    #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), RDF.type, triple_data_type) )
                                                    USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                                    MyLDGraph.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                                                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(x)) ) )
                                                    print "-----------Added_3D_Case--R--------", URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))
                                                    print "-----------Added_3D_Case--R--------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, dataType
                                                    print "-----------Added_3D_Case--R--------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, str(x)
                                                    self.property_counter += 1
                                                    elem = self.xml_instance_tracking[aSpatialThing]
                                                    elem[6] = x  # Place left to track [2D, 3D] parent coordinate data
                                                    self.xml_instance_tracking[aSpatialThing] = elem
                            print "self.property_counter F",self.property_counter

                    else:
                        #currentDataPathsList ---> List of sets of: (IsDefinedByNext, current_data_type, attribute_data_list, transformationProperty_data_list)
                        # For each data that makes up a multi-part set of measurements for example: IFC gives orientation/centerpoint/XDim/YDim...maybe ZDim
                        #print "reaching the depth-search version, len(currentDataPathsList): ", len(currentDataPathsList)
                        print "citygml building footprint from here so far...", currentDataPathsList, set_types_information, a_lookup
                        test_dict_setup = dict()
                        data_dict_to_generate_next_tree_layer, next_p_list, LOD_node = self.processCurrentDataPathsList(currentDataPathsList, set_types_information, a_lookup, tree, this_file_type, test_dict_setup)

                        #print "3rd Run Output:", set_types_information, a_lookup, tree
                        #for d in data_dict_to_generate_next_tree_layer:
                        #    print d, data_dict_to_generate_next_tree_layer[d]

                        #-----------------------------------------------------------------------------------------------

                        if this_file_type == "citygml" and a_lookup == "Space": # Because this is a pattern where spaces have to be created based on missing_link that gives parents and children
                            data_dict_to_generate_next_tree_layer = dict()
                        #print "after data_for_surface_dict 3rd Run: "  # Seen so far: ['center_point', 'x_center_offset', 'y_center_offset', 'depth']
                        for i in data_dict_to_generate_next_tree_layer:
                            #print "checking", i, data_dict_to_generate_next_tree_layer[i]
                            #print self.xml_instance_tracking
                            dataType, re_made_data = self.find__external_function(data_dict_to_generate_next_tree_layer[i], dimension, a_lookup, this_file_type)
                            print "trying to find the coors to add", re_made_data
                            for aSpatialThing in self.xml_instance_tracking:
                                if a_lookup == self.xml_instance_tracking[aSpatialThing][2]:
                                    spatialThingUsing = self.xml_instance_tracking[aSpatialThing][0]
                                    if self.xml_instance_tracking[aSpatialThing][0] == i:
                                        # Add Triples Now
                                        #print "test: ", self.xml_instance_tracking[aSpatialThing], spatialThingUsing
                                        with_subject = str(self.xml_instance_tracking[aSpatialThing][1])
                                        if str(re_made_data) != "":
                                            USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                            MyLDGraph.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(re_made_data)) ) )
                                            self.property_counter += 1
                                            print "-----------ADDED--E---------", (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter)))
                                            print "-----------ADDED--E---------", (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) )
                                            print "-----------ADDED--E---------", (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(re_made_data)) )
                                            elem = self.xml_instance_tracking[aSpatialThing]
                                            elem[6] = re_made_data  # Place left to track [2D is [5], 3D is [6]] parent coordinate data
                                            self.xml_instance_tracking[aSpatialThing] = elem
                                        #print "stored ", self.xml_instance_tracking[aSpatialThing]
                                        # If we are dealing with city gml, we want to add an additional property that contains the LOD tag
                                        #print "LOD_node", LOD_node
                                        if a_lookup == "SpaceCollection" and this_file_type == "citygml":
                                            #Then adding an extra triple to define between the Buildings, ReliefFeatures, and so on...(just descriptive else will be lost info)
                                            USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("Collection_Type") ) )
                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(spatialThingUsing)) ) )
                                            print "Added: ", self.property_counter, "Collection_Type", str(spatialThingUsing),
                                            self.property_counter += 1
                                        if LOD_node != "no_LOD":
                                            print "reaching the lod triples3"
                                            # Then there was a LOD to collect so add it as a triple for context later
                                            USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal("LOD") ) )
                                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(LOD_node)) ) )
                                            print "Added: ", self.property_counter, "LOD", str(LOD_node)
                                            self.property_counter += 1
                            print "self.property_counter E",self.property_counter

                elif that_level == 1 and dimension == "2D":  # 2D data within this level using next level values and external function
                    print "case 3 has not been encountered yet...add lines"
                elif that_level == 1 and dimension == "3D":  # 3D data within this level using next level values and external function
                    print "case 4, temporarily solved by case 2, since for gbxml thus far these levels are interdependent..."
                elif this_level == 0 and that_level == 0 and dimension == "2D":  # 2D data within this level using direct coordinates, 2D assumes 2 pieces of path data even if blank
                    print "case 5"  # Assumes 2D Data is found in two levels of gbXML style, leaving the first of the three vocab spaces empty

                    for aSpatialThing in self.xml_instance_tracking:
                        if a_lookup == self.xml_instance_tracking[aSpatialThing][2]:
                            scps = list()
                            mypath = "." + str(coorPaths[1])
                            coordinate_set = self.xml_instance_tracking[aSpatialThing][0].xpath(mypath, namespaces=self.namespaces)
                            scps2 = list()
                            for coordinate_list in coordinate_set:
                                mypath = "." + str(coorPaths[2])
                                cp = list()
                                cartesian_points = coordinate_list.xpath(mypath, namespaces=self.namespaces)
                                for point in cartesian_points:
                                    cp.append(float(point.text))
                                cartesian_point = tuple(cp)
                                scps2.append(cartesian_point)
                            scps.append(scps2)
                            with_subject = str(self.xml_instance_tracking[aSpatialThing][1])
                            triple_data_type = URIRef( str(self.USObase) + str(str(dimension) + "Data" + str(with_subject).split("#")[1]) )
                            dataType = str(dimension) + str(a_lookup) + "Coordinates"  # Ex. "3DSpaceCoordinates"
                            #USO_New.add( (URIRef(with_subject), hasProperty, triple_data_type) )
                            #USO_New.add( (triple_data_type, RDF.type, Property) )
                            #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), RDF.type, triple_data_type) )
                            USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                            MyLDGraph.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(scps)) ) )
                            print "-------Added_2D-------", str(with_subject), dataType, str(scps)
                            self.property_counter += 1
                            elem = self.xml_instance_tracking[aSpatialThing]
                            elem[5] = scps  # Place left to track [2D, 3D] parent coordinate data
                            self.xml_instance_tracking[aSpatialThing] = elem
                            print "stored ", self.xml_instance_tracking[aSpatialThing][5]
                    print "self.property_counter D",self.property_counter

                elif this_level == 0 and that_level == 0 and dimension == "3D":  # 3D data within this level using direct coordinates, 3D assumes 3 pieces of path data even if blank
                    print "case 6"  # Assumes 3D Data is found using three levels of gbXML style, filling all of the three vocab spaces empty
                    scps = list()
                    for aSpatialThing in self.xml_instance_tracking:
                        if a_lookup == self.xml_instance_tracking[aSpatialThing][2]:
                            scps = list()
                            mypath = "." + str(coorPaths[0])
                            space_coordinate_set = self.xml_instance_tracking[aSpatialThing][0].xpath(mypath, namespaces=self.namespaces)
                            for polyloop_list in space_coordinate_set:
                                mypath = "." + str(coorPaths[1])
                                space_coordinate_set = polyloop_list.xpath(mypath, namespaces=self.namespaces)
                                scps2 = list()
                                for coordinate_list in space_coordinate_set:
                                    mypath = "." + str(coorPaths[2])
                                    cp = list()
                                    cartesian_points = coordinate_list.xpath(mypath, namespaces=self.namespaces)
                                    for point in cartesian_points:
                                        cp.append(float(point.text))
                                    cartesian_point = tuple(cp)
                                    scps2.append(cartesian_point)
                                scps.append(scps2)
                            with_subject = str(self.xml_instance_tracking[aSpatialThing][1])
                            triple_data_type = URIRef( str(self.USObase) + str(str(dimension) + "Data" + str(with_subject).split("#")[1]) )
                            dataType = str(dimension) + str(a_lookup) + "Coordinates"  # Ex. "3DSpaceCoordinates"
                            #USO_New.add( (URIRef(with_subject), hasProperty, triple_data_type) )
                            #USO_New.add( (triple_data_type, RDF.type, Property) )
                            #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), RDF.type, triple_data_type) )
                            USO_New.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                            MyLDGraph.add( (URIRef(with_subject), hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(str(scps)) ) )
                            print "-------Added_2D--Other-----", str(with_subject), dataType, str(scps)
                            self.property_counter += 1
                            elem = self.xml_instance_tracking[aSpatialThing]
                            elem[6] = scps  # Place left to track [2D, 3D] parent coordinate data
                            self.xml_instance_tracking[aSpatialThing] = elem
                            print "stored ", self.xml_instance_tracking[aSpatialThing][6]
                    print "self.property_counter C",self.property_counter
                else:
                    print "case 7", this_level, that_level, dimension

        # Use the above data to query for gbxml tree data depending on file type: "this_file_type", for now assuming an xml structure
        if current_data_type == "bdata":
            # Use the transformationProperty and attribute lists a certain way then add needed triples to UBO
            # xslt:list->"bdata" means from current href start over at main root
            #attributeCount = 0
            processing_method = len(transformationProperty_data_list)

            # GeoInstance, SpaceCollectionLocation, and SpaceCollection levels look for non-coordinate data, so we can group them
            if a_lookup == "GeoInstance" or a_lookup == "SpaceCollectionLocation" or a_lookup == "SpaceCollection":
                # 1 means there is just one path and so a single data to collect
                for prop in transformationProperty_data_list:
                    if str(prop[0]) == "*":
                        prop = str(self.top_root + prop.split("*")[1])

                    #print "handling prop: ", prop
                    spatial_piece = tree.xpath(str(prop), namespaces=self.namespaces)
                    #print spatial_piece
                    dataType = prop.rsplit('/', 1)[1]
                    latlongelev_check = 0
                    spatial_pieceB = list()
                    if dataType == "exp:integer-wrapper":  # This is assuming this case is ifc long/lat/elev (so far what has been seen)
                        b1 = ("/" + dataType)
                        b2 = prop.split(b1)[0]
                        b3 = b2.split("/")[-1]
                        dataType = b3
                        len_spatial_piece = len(spatial_piece)
                        spatial_p = list()
                        for p in spatial_piece:
                            this_p = float(p.text)
                            spatial_p.append(this_p)
                        spatial_pieceB.append(spatial_p)  # So this should be the set of degrees'minutes'seconds'nanoseconds
                        latlongelev_check = 1
                    for piece in spatial_piece:
                        #att_dict = self.get_current_attribute_dict(attribute_data_list, piece, tree)
                        print "piece: ", piece, dataType
                        if latlongelev_check == 1:
                            this_piece_data = str(spatial_pieceB)
                        elif this_file_type == "citygml":
                            # Then we are handed OGC style coordinates in the given CRS
                            # Later on this will have to be a handled data type that deliniates by space instead of commas
                            this_piece_data = str(piece.text)
                        else:
                            this_piece_data = float(piece.text)
                        #print "Making triple with: ", dataType, this_piece_data, self.prop_types[a_lookup], self.property_counter

                        #s = URIRef(str(self.USObase) + str(self.prop_types[a_lookup]))
                        #USO_New.add( (current_subject, hasProperty, s) )
                        #USO_New.add( (s, RDF.type, Property) )
                        #USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), RDF.type, s) )
                        USO_New.add( (current_subject, hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                        MyLDGraph.add( (current_subject, hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType) ) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(this_piece_data) ) )
                        print "-----------ADDED-----------", current_subject, hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))
                        print "-----------ADDED-----------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(dataType)
                        print "-----------ADDED-----------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(this_piece_data)
                        self.property_counter += 1

                        if latlongelev_check == 1:
                            break
                print "self.property_counter B",self.property_counter

            # Space, SpaceBoundary, and SpaceBoundaryElement levels look for 2D and 3D coordinate data, so processing is different
            if a_lookup == "Space" or a_lookup == "SpaceBoundary" or a_lookup == "SpaceBoundaryElement":
                print "Add stuff for: ", a_lookup


        if current_data_type == "bklevel":
            # Use the transformationProperty and attribute lists a certain way then add needed triples to UBO
            # xslt:list->"fdata" means at this level follow this path further
            # GeoInstance, SpaceCollectionLocation, and SpaceCollection levels look for non-coordinate data, so we can group them
            if a_lookup == "GeoInstance" or a_lookup == "SpaceCollectionLocation" or a_lookup == "SpaceCollection":
                # 1 means there is just one path and so a single data to collect
                if str(transformationProperty_data_list[0][0]) == "*":
                     prop = str(self.top_root + transformationProperty_data_list[0].split("*")[1])
                else:
                    prop = transformationProperty_data_list[0]
                #print "handling bklevel: ", prop
                spatial_piece = tree.xpath(str(prop), namespaces=self.namespaces)
                dataType = prop.rsplit(':', 1)[1]
                for piece in spatial_piece:
                    sub_list = piece.xpath(str("." + transformationProperty_data_list[1]), namespaces=self.namespaces)
                    for data in sub_list:
                        this_piece_data = data.text
                        if this_piece_data == str(transformationProperty_data_list[2]):
                            other_data = piece.xpath(str("." + transformationProperty_data_list[3]), namespaces=self.namespaces)
                            for num in other_data:
                                new_area_value = float(num.text)
                                #print "Making triple with: ", dataType, this_piece_data, self.prop_types[a_lookup], self.property_counter, new_area_value
                                USO_New.add( (current_subject, hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                MyLDGraph.add( (current_subject, hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))) )
                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(this_piece_data) ) )
                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(new_area_value) ) )
                                print "-----------ADDED-----------", current_subject, hasProperty, URIRef(str(self.USObase) + "Property" + str(self.property_counter))
                                print "-----------ADDED-----------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasType, Literal(this_piece_data)
                                print "-----------ADDED-----------", URIRef(str(self.USObase) + "Property" + str(self.property_counter)), hasValue, Literal(new_area_value)
                                self.property_counter += 1













        if current_data_type == "fdata":
            # Use the transformationProperty and attribute lists a certain way then add needed triples to UBO
            # xslt:list->"fdata" means at this level follow this path further
            print "fdata section needs attention"

        if current_data_type == "idata":
            # Use the transformationProperty and attribute lists a certain way then add needed triples to UBO
            # xslt:list->"idata" means collect these data at current level
            print "idata section needs attention"

        #need to pass back if transformationProperty_data_list has a blank node to repeat processes or is nil
        return

    def get_current_attribute_dict(self, attribute_data_list, piece, tree):
        att_dict = dict()
        attributeCount = 0
        for attribute in attribute_data_list:
            attribute = attribute.split("#")[1]
            curr_attribute = str(attribute) + str(attributeCount)
            att = str(attribute)
            curr_attribute_data = piece.get(att)
            att_dict[curr_attribute] = curr_attribute_data
            attributeCount += 1

        return att_dict

    def find__external_function(self, collected_data, dimension, a_lookup, this_file_type):
        re_made_data = "noneyet"  # Will be the coordinates we process
        dataType = ""  # Ex. "3DSpaceCoordinates"
        print "Reaching the find__external_function function...", collected_data
        #print "Based on collected_data find appropriate external processing function if desired"
        typesDict = dict()
        data_list = list()
        for i in collected_data:
            data_list = list()
            for j in i[1]:
                data_list.append(j[0])
            #print "pre_data list", data_list
            typesDict[i[0]] = [ data_list, i[1] ]

        calculateCoors = coorsFromVocabs()
        if "center_point" in typesDict and "x_center_offset" in typesDict and "y_center_offset" in typesDict and "depth" not in typesDict:
            #print "2D Geometry can be created may need to add orientation"
            dataType = str(dimension) + str(a_lookup) + "Coordinates"  # Ex. "3DSpaceCoordinates"
            #calculateCoors = coorsFromVocabs()
            re_made_data = calculateCoors.devCoorsBasedOn_typeA(dimension, typesDict["center_point"][0], typesDict["x_center_offset"][0], typesDict["y_center_offset"][0], "", "")
        elif "center_point" in typesDict and "x_center_offset" in typesDict and "y_center_offset" in typesDict and "depth" in typesDict:
            #print "3D Geometry can be created may need to add orientation"
            dataType = str(dimension) + str(a_lookup) + "Coordinates"  # Ex. "3DSpaceCoordinates"
            #calculateCoors = coorsFromVocabs()
            #print "typesDict", typesDict["center_point"]
            re_made_data = calculateCoors.devCoorsBasedOn_typeA(dimension, typesDict["center_point"][0], typesDict["x_center_offset"][0], typesDict["y_center_offset"][0], "", typesDict["depth"][0])
            #print "re_made_data", re_made_data  # Will be the coordinates we process
        elif "ogc_coordinates" in typesDict:
            #print "typesDict has ground_surface_footprint"
            dataType = str(dimension) + str(a_lookup) + "Coordinates"  # Ex. "3DSpaceCoordinates"
            #calculateCoors = coorsFromVocabs()
            re_made_data = ""
            #print "here", typesDict["ogc_coordinates"][0]
            for entry in typesDict["ogc_coordinates"][0]:
                #print "entry", entry
                if this_file_type == "citygml":
                    if re_made_data == "":
                        re_made_data = entry[0]
                    else:
                        re_made_data = re_made_data + "," + entry[0]
                else:
                    next_data = calculateCoors.OGC_to_Comma_Delimited(dimension, entry[0])
                    re_made_data = re_made_data + next_data
        else:
            # Will have to store measurements since no current way to translate into coordinates
            print "default data processing"
            dataType = str(dimension) + str(a_lookup) + "Measurements"  # Ex. "3DSpaceCoordinates"
            re_made_data = str(collected_data)

        print "Exiting values", dataType, re_made_data
        return dataType, re_made_data

    def findCurrentDataPathsList(self, current_vocab_parsed, current_data_type, startPath, attribute_data_list, root_att_data_list, transformationProperty_data_list, this_file_type, tree, a_lookup, USO_New, current_subject, my_full_predicate, hasObject, hasRootGeometryORdefined_data_list, MyLDGraph):
        # Used to find child relationships based upon the need for a geometry search type set of queries and matching
        # Check for the existence of geometry data for this level
        #print "hasRootGeometry in addCoordinateData", hasRootGeometryORdefined_data_list
        #print "self.xml_instance_tracking ", len(self.xml_instance_tracking), self.xml_instance_tracking     # self.xml_instance_tracking[xml_instance] = [ xml_instance, Spatial_Instance_new, str(a_lookup), branch_instances ]
        currentDataPathsList = list()
        set_types_information = list()
        hasGeometryComponents = 0
        #print "what is this:", hasRootGeometryORdefined_data_list
        if hasRootGeometryORdefined_data_list != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
            #print "processing root geometries"
            hasGeometryComponents = 1
            # For each geometry type in hasRootGeometry list get data
            for eachGeometryType in hasRootGeometryORdefined_data_list:  # In certain cases, defined_data_list is actually sent in place of hasRootGeometry, depending on structure
                coorPaths = list()
                coorInfo = list()
                a = 0
                b = 0
                c = 0
                dimension = ""
                full_dimension = ""
                currentDataPathsList = list()
                for rowj in current_vocab_parsed.query("""SELECT ?x ?y
                        WHERE { ?geom ?x ?y . }""",
                    initBindings={'geom' : BNode(eachGeometryType), 't' : RDF.type, 'G' : URIRef(self.geo_base + "Geometry")}):
                    # Foregoing fdata and bdata element types and assume all will be a follow the current path method
                    end = 0
                    if str(rowj[0]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                        g2 = BNode(rowj[1])
                        a = 1
                        coorPaths, e_find_end_of_list_now, node = self.collect_list_items(g2, current_vocab_parsed, coorPaths, end)
                    if str(rowj[0]) == "http://www.w3.org/2000/01/rdf-schema#label":
                        b = 1
                        full_dimension = str(rowj[1])
                        if "3D" in full_dimension:
                            dimension = "3D"
                        if "2D" in full_dimension:
                            dimension = "2D"
                    if str(rowj[0]) == "http://www.w3.org/2000/01/rdf-schema#isDefinedBy":
                        c = 1
                        list_type_definedBy = 0
                        # Then there is a list of defined by data, at this point should be for geometry data
                        find_end_of_list = 0
                        next_blank_node = BNode(rowj[1])
                        defined_data_list = list()
                        defined_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, defined_data_list, find_end_of_list)
                        #print "other defined_data_list here", defined_data_list, next_blank_node
                        if len(defined_data_list) > 1:
                            if str(rowj[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(rowj[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                defined_data_list.append(str(rowj[1]))
                            if str(rowj[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(rowj[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                find_end_of_list = 0
                                next_blank_node = BNode(rowj[1])
                                defined_data_list, e_find_end_of_list_now, last_blank_node = self.collect_list_items(next_blank_node, current_vocab_parsed, defined_data_list, find_end_of_list)
                            list_type_definedBy = 1
                        currentDataPathsListA = list()
                        current_data_type_list = list() # To give the set to pass to the function, can be used individually or can use currentDataPathsList instead
                        attribute_data_list_list = list() # To give the set to pass to the function, can be used individually or can use currentDataPathsList instead
                        transformationProperty_data_list_list = list() # To give the set to pass to the function, can be used individually or can use currentDataPathsList instead
                        #print "set_types_information", set_types_information
                        set_types_information = list()
                        for d in defined_data_list:
                            # For each contributing blank node to the set of geometry features (typical so far for ifcxml querying)
                            attribute_data_list = list()
                            transformationProperty_data_list = list()
                            current_data_type = ""
                            IsDefinedByNext = ""
                            temp_IsDefinedByNext = ""
                            a = 0
                            b = 0
                            c = 0
                            de = 0
                            while str(IsDefinedByNext) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                for row in current_vocab_parsed.query("""SELECT ?x ?y
                                        WHERE { ?d ?x ?y .}""",
                                    initBindings={'d' : BNode(d)}):
                                    #print "other data - attribute - transProperty: ", row
                                    find_end_of_list_now = 0
                                    if row[0] == URIRef(str(RDF.type)):  # So this should only be recorded or required if it exists
                                        # So systematically should only include at the end of a set of paths leading to data
                                        set_types_information.append(str(row[1]))
                                        #print "added set_types_information 2", str(row[1])
                                    if row[0] == URIRef(str(self.rdfs_isDefinedBy)):
                                        temp_IsDefinedByNext = str(row[1])
                                        de = 1
                                    if row[0] == URIRef("https://www.w3.org/TR/xslt-30/schema-for-xslt30#element"):
                                        current_data_type = str(row[1])
                                        #current_data_type_list.append(current_data_type)
                                        #current_data_type_list = list()
                                        a = 1
                                    if row[0] == URIRef("https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute"):
                                        attribute_data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(row[1], current_vocab_parsed, attribute_data_list, find_end_of_list_now)
                                        #attribute_data_list_list.append(attribute_data_list)
                                        #attribute_data_list = list()
                                        b = 1
                                    if row[0] == URIRef("https://www.w3.org/2003/g/data-view#transformationProperty"):
                                        transformationProperty_data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(row[1], current_vocab_parsed, transformationProperty_data_list, find_end_of_list_now)
                                        c = 1
                                    if a == 1 and b == 1 and c == 1 and de == 1:
                                        # String List List
                                        #print "Now: ", IsDefinedByNext, current_data_type, attribute_data_list, transformationProperty_data_list
                                        IsDefinedByNext = temp_IsDefinedByNext
                                        currentDataPathsListA.append([IsDefinedByNext, current_data_type, attribute_data_list, transformationProperty_data_list])
                                        current_data_type_list = list()
                                        attribute_data_list = list()
                                        transformationProperty_data_list = list()
                                        a = 0
                                        b = 0
                                        c = 0
                                        de = 0
                                        d = IsDefinedByNext
                                        if str(IsDefinedByNext) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                                            currentDataPathsList.append(currentDataPathsListA)
                                            currentDataPathsListA = list()
                                            #print "currentDataPathsList", len(currentDataPathsList), currentDataPathsList
                            #print "set_types_information 2: ", set_types_information
        return currentDataPathsList, set_types_information

    def processCurrentDataPathsList(self, currentDataPathsList, set_types_information, a_lookup, tree, this_file_type, test_dict_setup):
        # Collect all the child nodes that belong to this parent
        # Given each branch instance, see what children can be found (so far works for what Sp.Bound.Elements belong to which IFC Surfaces)
        collected_data = dict()
        collected_data_revised = dict()
        data_for_surface_dict = dict()
        sets_counter = 0
        next_p = ""
        next_p_list = list()
        spatialThingUsing = ""
        LOD_node = "no_LOD"
        for c in currentDataPathsList:
            #print "How many parts of geometry type?", a_lookup, len(currentDataPathsList), c  # Printing c here will show the lookup structure
            process_structure = dict()
            for aSpatialThing in self.xml_instance_tracking:
                if a_lookup == self.xml_instance_tracking[aSpatialThing][2]:
                    #print "info pertaining to element:", self.xml_instance_tracking[aSpatialThing][1] #, self.xml_instance_tracking[aSpatialThing][1]
                    #child =  self.xml_instance_tracking[aSpatialThing][0]
                    current_node = self.xml_instance_tracking[aSpatialThing][0]
                    #print "current_node", current_node #I think its saving the second space collection type over the existing self.xml_instance_tracking[aSpatialThing][0] above...where branch_instance are
                    if a_lookup == "SpaceBoundaryElement":
                        path_for_loc = 3
                    else:
                        path_for_loc = 0
                    new_list = list()
                    spatialThingUsing = aSpatialThing
                    # The last list item in currentDataPathsList is transformationProperty_data_list should be the item that holds the value data in the xml
                    place_counter = 0
                    rootID = ""
                    nextREF = ""
                    collected_branch_refs = list()
                    collected_branch_refs.append("placeholder")
                    ref_counter = 0
                    temp_c = c
                    go_back_to_here = ""
                    go_back_to_here_set_flag = 0
                    test_ref_list = ()
                    set_new_flag = 0
                    prev_len_collected_branch_refs = 0
                    data_list2 = list()
                    data_list1 = list()
                    prev_path_stars = ""
                    sub_instances = list()
                    iToSave = ""
                    curr_materials = list()
                    while collected_branch_refs != test_ref_list:
                        ref_counter = 0
                        test_ref_list = list()
                        for nextREF in collected_branch_refs:  # so even for one, the nextREF is a list, and assuming one set of multiples for now
                            #test_ref_list.append(nextREF)
                            #prev_len_collected_branch_refs = len(collected_branch_refs)
                            prev_nextREF = nextREF
                            if nextREF == "placeholder":
                                collected_branch_refs.remove(nextREF)

                            ref_counter += 1
                            if c > 1 and set_new_flag == 0:  # Will have to come back to a start point, so adjust c
                                for p in temp_c:
                                    if str(p) == str(go_back_to_here):
                                        _index = temp_c.index(p)
                                        temp_c = temp_c[_index:]
                                        set_new_flag = 1
                            for path_part in temp_c: # For each step of current path set follow it until end and get geo data piece
                                # Assuming start and find (2) pieces here for each step....could be expanded later on if need be
                                place_counter += 1
                                step_start_attr = path_part[2][0]
                                step_find_attr = path_part[2][1]
                                step_start_path = path_part[3][0]
                                step_find_path = path_part[3][1]
                                org_step_start_path = step_start_path
                                org_step_find_path = step_find_path
                                #print "Evaluating", step_start_path, step_find_path

                                ext = step_start_path.split(":")[0] + ":"
                                if ext[0] == "*" or ext[0] == ".":
                                    ext = ext[1:]

                                if str(step_start_path[0]) == "*":
                                    # This section assumes first path_part[3] is start point
                                    step_start_path = str(self.top_root + step_start_path[1:])
                                if str(step_find_path[0]) == "*":
                                    # This section assumes first path_part[3] is start point
                                    step_find_path = str(self.top_root + step_find_path[1:])
                                # Last in set so collect data---------------------------------------------------

                                if str(path_part[1]) == "fdata":
                                    next_p = "." + str(step_find_path)
                                    #next_p_list.append(next_p)
                                elif str(path_part[1]) == "bdata":
                                    next_p = str(step_find_path)
                                    #next_p_list.append(next_p)
                                else:
                                    #print "Add path following type for IFC-like processing...Typical set"
                                    next_p = "X"

                                # Adjust current start path if needed
                                #print "going in here with before paths", prev_path_stars, step_start_path, step_find_path
                                #print "Test for placeholder: ", step_start_attr
                                if prev_path_stars != "":
                                    if str(step_start_attr) == "http://www.citygml.org/index.php?id=1540#placeholder":
                                        # Placeholder means that it is structured like geometry processing, but can skip id matching since just collecting data such as citygml LOD
                                        # Then check if there is a "***" for adding the given path (i.e. some lod) and then add it
                                        print "Add next level of stuff for citygml processing when: if prev_path_stars != '':"
                                    else:
                                        add_back_to_beg = ""
                                        if ext[0] == ".":
                                            add_back_to_beg = "."
                                        # Means I added new path to the previous
                                        # you have to add in this to the beginning of the start path
                                        if prev_path_stars == "***":
                                            # Add child tag to beginning of the step_start_path but between first * if there is one and the rest of the step_start_path
                                            #print "Need to adjust the current start path because previous find path changed at the end to get a ref"
                                            #step_start_path = step_start_path[:-3]  # May need to add this back if the case comes up...has not yet
                                            step_start_path = str(step_start_path + ext + sur)
                                        if prev_path_stars == "**":
                                            # Add child tag to end of the step_start_path but between step_start_path and stars if there are any at the end
                                            #print "Did not need to alter the beginning of the current start path because previous change happened at beginning previous find path"
                                            if str(self.top_root) in step_start_path:
                                                temp_p = step_start_path.split(self.top_root)[1]
                                                step_start_path = str(self.top_root + ext + sur + temp_p)
                                            if step_start_path[0] == ".":
                                                step_start_path = str(add_back_to_beg + ext + sur + step_start_path)

                                # Adjust current find path if needed
                                parent_level = 0
                                if str(step_find_path[-2:]) == "**" or str(step_find_path[-3:]) == "***" or str(step_find_path[-1:]) == "*":
                                    #print "curr next_p", next_p
                                    # Then there are many possibilities for what the last child tag will be (Ifc Wall, IfcSlab, etc.)
                                    # To aviod having to do a lot of string matching, find child tag in tree and use that to fill in this part of this path
                                    #print next_p
                                    add_back_to_beg = ""
                                    if ext[0] == ".":
                                        add_back_to_beg = "."
                                    #print "ext", ext
                                    next_pt = ""
                                    int_list = ""
                                    #print "next_p", next_p
                                    if str(next_p[-3:]) == "***":
                                        prev_path_stars = "***"
                                    elif str(next_p[-2:]) == "**":
                                        prev_path_stars = "**"
                                    elif str(next_p[-1:]) == "*":
                                        # Then this is a nested integer indicating how many levels back up we will need to go
                                        int_list = ""
                                        bound_counter = 0
                                        for charact in next_p[::-1]:
                                            if charact == "*" and bound_counter < 2:
                                                bound_counter += 1
                                            else:
                                                int_list = int_list + charact
                                            if bound_counter == 2:
                                                break
                                        next_p = next_p.replace(str("*"+int_list+"*"),"")
                                        parent_level = int(int_list)
                                        prev_path_stars = ""
                                    else:
                                        prev_path_stars = ""
                                    for char in '*':
                                        next_pt = next_p.replace(char,'')

                                    if org_step_start_path[0] == "*" and org_step_start_path != "*/ifc:IfcRelSpaceBoundary":
                                        #org_step_start_path = org_step_start_path.replace(str("*"+int_list+"*"),"")
                                        #org_step_find_path = org_step_find_path.replace(str("*"+int_list+"*"),"")
                                        #next_pt = ".." + org_step_start_path.replace("*","") + org_step_find_path.replace("*","")
                                        next_pt = ".." + org_step_start_path.replace("*","") + org_step_find_path.replace("*","")
                                    #elif org_step_start_path[0] != "*" and org_step_start_path != "*/ifc:IfcRelSpaceBoundary":
                                    #    next_pt = next_pt
                                    #    print "yes here"
                                    else:
                                        next_pt = next_pt.replace(".","./")

                                    #print "Testing from here...", self.xml_instance_tracking[aSpatialThing]
                                    #tester = str("." + str(self.top_root))
                                    #if tester in next_p:
                                    #    next_p = next_p[1:]
                                    #print "next_pt", next_pt
                                    temp_instances = self.xml_instance_tracking[aSpatialThing][path_for_loc].xpath(next_pt, namespaces=self.namespaces)
                                    #print "temp_instances in setup", temp_instances

                                    sur = ""
                                    for t in temp_instances:
                                        #get parent id up one level and see if this matches
                                        par_instances = t.xpath("..", namespaces=self.namespaces)
                                        closest_parent_id = ""
                                        for p in par_instances:
                                            closest_parent_id = p.get("id")
                                            break
                                        su = t.getchildren()
                                        #print "comparing ", closest_parent_id, nextREF, len(t)
                                        if len(temp_instances) > 1:
                                            if str(closest_parent_id) == str(nextREF):
                                                #print "matched this parent ID", nextREF
                                                for chil in su:
                                                    sur = str(chil.tag).split("}")[1]
                                                    #print "t.tag", sur
                                                    break
                                        if len(temp_instances) == 1:
                                            for chil in su:
                                                sur = str(chil.tag).split("}")[1]
                                                #print "t.tag", sur, len(su)
                                        if sur != "":
                                            break

                                    #print "sur", sur, next_p
                                    if str(next_p[-3:]) == "***":
                                        next_p = next_p[:-3]
                                    if str(next_p[-2:]) == "**":
                                        next_p = next_p[:-2]
                                    if sur == "":
                                        next_p = str(next_p)
                                    else:
                                        next_p = str(next_p + ext + sur)

                                    if str(self.top_root) in next_p:
                                        # Last check to remove . where should start back at beginning
                                        if next_p[0] == ".":
                                            next_p = next_p[1:]
                                else:
                                    prev_path_stars = ""

                                # Need a way around unordered processing (Wall should use one type but not the other, etc.) So give an escape case that should never find a match
                                if str(step_start_path[-5:]) == "/ifc:":  # Removing this where a child was not found so will continue to run
                                    step_start_path = step_start_path[:-5]

                                #print "paths going in:", step_start_path, next_p, parent_level, ext, nextREF
                                # Note: next_p_list will associate Geo name# (Surface1, etc.) with the schema name (IfcRelSpaceBoundary, etc.)
                                next_p_list.append((self.xml_instance_tracking[aSpatialThing][1], step_start_path))

                                # If the attr here are Placeholder then this is a case where we do not need to do attr matching, so combine start and find and pull coors (possibly for each instance of find_path)
                                # Will be slightly different because will have to work for getting one set of coors in nesting AND
                                # Will have to work for spaces that have several members each with coordinates, like below where we see: curr_data = [i.text, i]
                                # Also might need to set: collected_data or data_list2
                                #LOD_node = "no_LOD"
                                ext_type = str(current_node).split(" ")[1]
                                ext_type = ext_type.split("}")[1]
                                if ext_type == "Building":
                                    LOD_type = "bldg:"
                                elif ext_type == "ReliefFeature":
                                    LOD_type = "dem:"
                                else:
                                    LOD_type = "LOD_type needed in set"
                                if str(step_start_attr) == "http://www.citygml.org/index.php?id=1540#placeholder" and str(step_find_attr) == "http://www.citygml.org/index.php?id=1540#placeholder":
                                    # "Placeholder" means that it is structured like geometry processing, but can skip id matching since just collecting data such as citygml LOD
                                    # Then check if there is a "***" for adding the given path (i.e. some lod) and then add it
                                    if str(step_start_path[-3:]) == "***":
                                        #print "step_start_path i think", step_start_path, step_find_path, next_p
                                        #print "starting path with", current_node
                                        data_list = list()
                                        get_children_list = current_node.getchildren()
                                        if a_lookup == "SpaceCollection":
                                            # Need to account for this condition where all collections are children and we actually need to query the grand-children
                                            for i in get_children_list:
                                                i2 = str(i)
                                                #print "get_children_list", current_node, get_children_list, i
                                                if "lod" in i2 and a_lookup == "SpaceCollection":
                                                    if "Ground" in i2 or "Foot" in i2 or "Roof" in i2 or "MultiSurface" in i2:
                                                        correct_child = i2.split("}")[1]
                                                        # Now find the one that will have lod in name and the next path set to get coors then add that to data list
                                                        correct_child = correct_child.split(" ")[0]
                                                        new_path = str("./" + LOD_type + correct_child + step_find_path)
                                                        datas = current_node.xpath(new_path, namespaces=self.namespaces)
                                                        data_list = list()
                                                        for d in datas:
                                                            #print "d.text: ", d.text
                                                            d_text = str(d.text)
                                                            if d_text != "":
                                                                d_text = d_text.replace('\t', '')
                                                                d_text = d_text.replace('\n', ' ')
                                                                curr_data = [d_text, d]
                                                                data_list.append(curr_data)
                                                                collected_data[set_types_information[sets_counter]] = data_list
                                                            #print "data_list", data_list
                                                            LOD_node = str(i.tag).split("}")[1]
                                                            print "setting_LOD_node", LOD_node
                                                            self.LODis = int(LOD_node[3:4])
                                                        data_list2.append(data_list)
                                        else:
                                            print "else found so needs a condition for citygml type using placeholder but is not the SpaceCollection Case..."
                                elif str(step_start_attr) == "http://www.citygml.org/index.php?id=1540#placeholder" and str(step_find_attr) != "http://www.citygml.org/index.php?id=1540#placeholder":
                                    # Now use see if for this find path if there is the find_attr at this location
                                    # If yes, then add them all to this list and see if this is in the missing_link, add it if not with parent key or append new set of hrefs if there already
                                    # This means we are dealing with a spatial element that does not yet have connections to parents, geometry of its own, or id of its own apart from address
                                    # But here is not to make those connections but instead record current node (space), parent, and child ids (surface member ids)
                                    if this_file_type == "citygml":  # Then we are looking for CompositeSurface
                                        if a_lookup == "Space":
                                            # For this pattern type, the Space level is just where we set up the missing_link dict()
                                            #if I am parsing paths and find a CompositeSurface, then store in the missing_link dict() with its parent address which should be the xml_instance
                                            #missing _link[this CompositeSurface address (current geom so space id)] = [xml_instance, LOD, set_type(LOD1 is ), (set of surface ids) (data if exists i.e. LOD-1)]
                                            current_node_children = current_node.getchildren()
                                            set_parent = 0
                                            parent = ""
                                            for curr_node in current_node_children:
                                                curr_node = curr_node.tag.split("}")[1]
                                                if str(org_step_start_path[-3:]) == "***":
                                                    if str(org_step_start_path) == "***":
                                                        new_path = str("./" + LOD_type + curr_node + step_find_path)
                                                    else:
                                                        new_path = str("." + org_step_start_path[:-3] + "/" + LOD_type + curr_node + step_find_path)
                                                else:
                                                    new_path = str("." + org_step_start_path + "/" + LOD_type + curr_node + step_find_path)
                                                check_LOD_node = curr_node
                                                see_if_instances_exist = current_node.xpath(new_path, namespaces=self.namespaces)

                                                if len(see_if_instances_exist) != 0 and set_parent == 0: # then there is a set here
                                                    #print "new_path is this", new_path
                                                    if "CompositeSurface" in new_path:
                                                        cs_path = new_path.split("CompositeSurface")[0] + "CompositeSurface"
                                                        rest_of_path = new_path.split("CompositeSurface")[1]
                                                        paths_up_to_CompositeSurface = current_node.xpath(cs_path, namespaces=self.namespaces)
                                                        #print "paths_up_to_CompositeSurface", paths_up_to_CompositeSurface
                                                        for option in paths_up_to_CompositeSurface:
                                                            test_children = option.xpath("." + rest_of_path, namespaces=self.namespaces)
                                                            parent = option
                                                            set_parent = 1
                                                            #print "finding parent", parent
                                                            # Now we have the current space (= parent) and the previous collection node (= current_node) and LOD_node
                                                            # So now, if LOD_node is LOD-1 then collect coors, else collect all the ids based on view-given step_find_path
                                                            set_of_surface_ids = list()
                                                            set_of_surface_datas = list()
                                                            set_of_surface_hrefs = list()
                                                            set_surf_ids = list()
                                                            for each_found_child in test_children:
                                                                #print "each_found_child", each_found_child
                                                                d_text = ""
                                                                if "lod" in check_LOD_node:
                                                                    LOD_node = curr_node
                                                                    d_text = str(each_found_child.text)  # Then collect data from here
                                                                    if d_text != "":
                                                                        d_text = d_text.replace('\t', '')
                                                                        d_text = d_text.replace('\n', ' ')

                                                                    set_of_surface_datas.append(d_text)  # Append data to set_of_surface_datas
                                                                    set_of_surface_ids.append(each_found_child)  # Append surfaceMember address to set_of_surface_ids or last in list

                                                                if d_text == "" or str(d_text) == "None":
                                                                    # Rest of LOD so far have sets of hrefs so collect those from each_found_child
                                                                    if each_found_child not in set_of_surface_ids:
                                                                        set_of_surface_ids.append(each_found_child)  # Append surfaceMember address to set_of_surface_ids or last in list
                                                                    href_link_member = each_found_child.get("{http://www.w3.org/1999/xlink}href")
                                                                    set_of_surface_hrefs.append(href_link_member)
                                                            #print "set_of_surface_hrefs", set_of_surface_hrefs

                                                            interior_room_flag = 0
                                                            if "interiorRoom" in str(new_path):
                                                                interior_room_flag = 1

                                                            # Found available data, add it to the missing_link dict()
                                                            if parent in self.missing_link:
                                                                has_data = 0
                                                                # Append Data to self.missing_link[parent][3] and self.missing_link[parent][5]
                                                                p_3_list = self.missing_link[parent][3]
                                                                for new_i in set_of_surface_ids:
                                                                    p_3_list.append(new_i)
                                                                set_of_surface_ids = p_3_list
                                                                p_4_list = self.missing_link[parent][4]
                                                                for new_i in set_of_surface_datas:
                                                                    p_4_list.append(new_i)
                                                                set_of_surface_datas = p_4_list
                                                                p_5_list = self.missing_link[parent][5]
                                                                for new_i in set_of_surface_hrefs:
                                                                     p_5_list.append(new_i)
                                                                set_of_surface_hrefs = p_5_list

                                                                for data_set in set_of_surface_datas:
                                                                    #print "data_set", type(data_set).__name__
                                                                    if data_set == "" or data_set == " ":
                                                                        has_data = 0
                                                                    else:
                                                                        if has_data == 0:
                                                                            has_data = 1
                                                                if has_data == 1:
                                                                    print "in up here", self.xml_instance_tracking[aSpatialThing][1], current_node
                                                                    self.missing_link[parent] = [current_node, self.xml_instance_tracking[aSpatialThing][1], LOD_node, set_of_surface_ids, set_of_surface_datas, set_of_surface_hrefs, interior_room_flag]
                                                            else:
                                                                print "out", self.xml_instance_tracking[aSpatialThing][1], current_node
                                                                self.missing_link[parent] = [current_node, self.xml_instance_tracking[aSpatialThing][1], LOD_node, set_of_surface_ids, set_of_surface_datas, set_of_surface_hrefs, interior_room_flag]
                                                            print "self.missing_link[parent]", self.missing_link[parent]
                                                    else:
                                                        print "no CompositeSurface, probably LOD-0"


                                        if a_lookup == "SpaceBoundary":  # Thus far, method only seen in CityGML
                                            # Reusing this function to find the next set of datas (coordinates), now we have a set of starting points, instead of searching and matching all from the start...testing the method
                                            # Pull all surface coordinate information and stor based on ID, then above lookup only ones in the given set you need
                                            set_of_surface_datas = list()
                                            print "test_dict_setup", test_dict_setup  # [GML_ID]->[TreeAddress] since level is known, these ids are for surfaceMembers
                                            print a_lookup
                                            print "step_find_path", step_find_path, org_step_start_path, step_start_path
                                            #see_if_instances_exist = current_node.xpath(new_path, namespaces=self.namespaces)
                                            #start here, and verify the use of *** and then pull whatever interior oe exterior coordinates there are...then add to missing link, now with SpaceBoundary as the key

                                            if org_step_start_path == "/":
                                                # Then just continue to follow this new path to collect data if any
                                                print "len", len(test_dict_setup)
                                                for s_member in test_dict_setup:
                                                    new_test_dict_setup_set = list()
                                                    new_test_dict_setup_set.append(test_dict_setup[s_member])
                                                    new_test_dict_setup_set.append(set_types_information[sets_counter])
                                                    any_datas = test_dict_setup[s_member].xpath("." + step_find_path, namespaces=self.namespaces)
                                                    collect_any_datas = list()
                                                    for any_data in any_datas:
                                                        d_text = str(any_data.text)  # Then collect data from here
                                                        if d_text != "":
                                                            d_text = d_text.replace('\t', '')
                                                            d_text = d_text.replace('\n', ' ')
                                                            collect_any_datas.append(d_text)
                                                    new_test_dict_setup_set.append(collect_any_datas)

                                                    if s_member in self.test_dict_setup2:
                                                        self.test_dict_setup2[s_member].append(new_test_dict_setup_set)
                                                    else:
                                                        self.test_dict_setup2[s_member] = [ new_test_dict_setup_set ]  # Now has [surf_address, type_coors(intORext), coors]
                                                    #print "test_dict_setup2[s_member]", self.test_dict_setup2[s_member]
                                            else:
                                                print "path was something other than / to start in SpaceBoundary"

                                else:
                                    if place_counter == 1:  # First set and more to come
                                        rootID = self.xml_instance_tracking[aSpatialThing][path_for_loc].get(step_start_attr.split("#")[1])
                                        instances = self.xml_instance_tracking[aSpatialThing][path_for_loc].xpath(next_p, namespaces=self.namespaces)
                                        #print "instancesT", instances, self.xml_instance_tracking[aSpatialThing][0], next_p
                                        #if len(instances) != 1:
                                        #    print "going to have to add the list case for multiple sub_instances in loop on next line"
                                        data_list = list()
                                        for i in instances:
                                            nextREF = i.get(step_find_attr.split("#")[1])
                                            if len(instances) > 1 and nextREF != None:
                                                collected_branch_refs.append(nextREF)
                                            if len(c) == 1:  # First set and only set so need nextREF and data here
                                                #print "I"
                                                curr_data = [i.text, i]
                                                data_list.append(curr_data)
                                                collected_data[set_types_information[sets_counter]] = data_list
                                                #print "current if data", data_list
                                                #data_list1.append(data_list)
                                        if len(instances) > 1 and go_back_to_here_set_flag == 0:
                                            go_back_to_here = path_part
                                            go_back_to_here_set_flag = 1
                                    else:  # Somewhere in the middle of the list (or end) so find new IDs and reset for next loop
                                        data_list = list()
                                        instances = tree.xpath(str(step_start_path), namespaces=self.namespaces)
                                        #REFfound = ""
                                        for i in instances:
                                            tempREF = i.get(step_start_attr.split("#")[1])
                                            if str(tempREF) == str(nextREF):                      #if tempREF in collected_branch_refs:
                                                #print "match of stuff", i, tempREF, step_start_path, next_p
                                                rootID = tempREF

                                                if parent_level == 0:
                                                    sub_instances = i.xpath(str(next_p), namespaces=self.namespaces)
                                                    #iToSave = i
                                                else:
                                                    look_back = ""
                                                    while parent_level != 0:
                                                        if parent_level-1 == 0:
                                                            look_back = look_back + ".."
                                                        else:
                                                            look_back = look_back + "../"
                                                        parent_level = parent_level - 1
                                                    #print look_back
                                                    sub_instances = i.xpath(look_back, namespaces=self.namespaces)

                                                for s in sub_instances:
                                                    nextREF = s.get(step_find_attr.split("#")[1])
                                                    curr_data = [s.text, i]  #s
                                                    data_list.append( curr_data )
                                                    if len(sub_instances) > 1 and nextREF != None:
                                                        collected_branch_refs.append(nextREF)

                                                if prev_len_collected_branch_refs > 1:
                                                    data_list2.append(data_list)
                                                #else:
                                                #    data_list1.append(data_list)
                                                if len(sub_instances) > 1 and go_back_to_here_set_flag == 0:
                                                    go_back_to_here = path_part
                                                    go_back_to_here_set_flag = 1
                                                #print "curr_data else", data_list

                                        if place_counter == len(temp_c): #and len(collected_branch_refs) == 1:  # Last set in normal case
                                            place_counter = 0
                                            #data_list = data_list1.append(data_list)  # This became necessary because the groups of materials are being added to an additional list it caused issues getting data out uniformly
                                            #collected_data[set_types_information[sets_counter]] = data_list
                                            # Never found this type of data before for this element
                                            if self.xml_instance_tracking[aSpatialThing][0] not in data_for_surface_dict:
                                                data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]] = [(set_types_information[sets_counter], data_list, self.xml_instance_tracking[aSpatialThing][1])]
                                                #print "added on this", (set_types_information[sets_counter], data_list)
                                            else:
                                                if data_list != []:
                                                    #print "set_types_information[sets_counter] above", str(set_types_information[sets_counter])
                                                    addon = data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]]
                                                    found_flag = 0
                                                    for j in addon:
                                                        # For each tuple, see if set_types_information[sets_counter] is same as j[0]
                                                        # If this data type already exists, replace it with new data_list
                                                        if set_types_information[sets_counter] == j[0]:
                                                            new_addon = (j[0], data_list, self.xml_instance_tracking[aSpatialThing][1])
                                                            _index = addon.index(j)
                                                            addon[_index] = new_addon
                                                            #print "new_addon", new_addon
                                                            data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]] = addon
                                                            found_flag = 1
                                                    # If not in list at all, just add it in as single data info (sets handled after the fact below)
                                                    if found_flag == 0:
                                                        addon.append((set_types_information[sets_counter], data_list, self.xml_instance_tracking[aSpatialThing][1]))
                                                        data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]] = addon
                                            break

                            prev_len_collected_branch_refs = len(collected_branch_refs)
                            if len(collected_branch_refs) > 1 and prev_nextREF in collected_branch_refs:
                                collected_branch_refs.remove(prev_nextREF)
                            test_ref_list.append(prev_nextREF)
                            break

                    #self.xml_instance_tracking[aSpatialThing][0] = child
                    #print "saved this instead-----------------", child
                    if self.xml_instance_tracking[aSpatialThing][0] not in data_for_surface_dict:
                        print "check set_types_information", set_types_information
                        data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]] = [(set_types_information[sets_counter], data_list2, self.xml_instance_tracking[aSpatialThing][1])]
                    else:
                        if data_list2 != []:
                            #print "set_types_information[sets_counter] below", str(set_types_information[sets_counter]), data_list2
                            addon = data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]]
                            found_flag = 0
                            for j in addon:
                                # For each tuple, see if set_types_information[sets_counter] is same as j[0]
                                # If this data type already exists, replace it with new data_list
                                if set_types_information[sets_counter] == j[0]:
                                    new_addon = (j[0], data_list2, self.xml_instance_tracking[aSpatialThing][1])
                                    _index = addon.index(j)
                                    addon[_index] = new_addon
                                    #print "new_addon", new_addon
                                    data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]] = addon
                                    found_flag = 1
                            # If not in list at all, just add it in for a data "set"
                            if found_flag == 0:
                                addon.append((set_types_information[sets_counter], data_list2, self.xml_instance_tracking[aSpatialThing][1]))
                                data_for_surface_dict[self.xml_instance_tracking[aSpatialThing][0]] = addon
            sets_counter += 1
            #print "data_for_surface_dict NOW:", data_for_surface_dict

        return data_for_surface_dict, next_p_list, LOD_node


