#-------------------------------------------------------------------------------
# Name:        materialAddOn.py
# Purpose:     Add Material Names and IDs to LD Graph
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     10/05/2016
# Copyright:   (c) Holly Tina Ferguson 2016
# Licence:     The University of Notre Dame


# 1) where I pull all instances of materials (for gbxml is MaterialID tag), so this is the
#    same address location as is recorded in the passed in dictionary
# 2) match that to passed dictionary address entry to set the graph name and element type
# 3) for each of these three below, search for data

# from there where I go to get Name        (or the couple possibilities)
# from there where I go to get ID          (or the couple possibilities)
# from there where I go to get Thickness   (or the couple possibilities)

# 4) add data in these three as graph attributes to the respective graph named element


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


class Add_Materials():
    # Input parameters
    # May change as additional file options get entered into the mix
    #namespaces = {'gb': "http://www.gbxml.org/schema", 'city': "http://www.opengis.net/citygml/2.0"}
    USObase = "http://www.sw.org/UBO#"  # Change back to full: "http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"
    Vocab_base = "http://www.myuso.exp#"
    rdfs_base = "http://www.w3.org/2000/01/rdf-schema#"
    xslt_base = "https://www.w3.org/TR/xslt-30/schema-for-xslt30#"
    geo_base = "http://www.opengis.net/ont/geosparql#"
    xslt_element = URIRef(xslt_base + "element")
    xslt_attribute = URIRef(xslt_base + "attribute")
    xslt_list = URIRef(xslt_base + "list")
    rdfs_isDefinedBy = URIRef(rdfs_base + "isDefinedBy")
    geo_hasGeometry = URIRef(geo_base + "hasGeometry")

    def add_mat_name_and_id(self, tree, namespaces, material_dict, this_file_type, inputfile, USO_New, current_addOn_vocab, property_counter):

        print "Reaching Add Materials Function"
        #print "then", material_dict

        # What I am starting with as existing in the USO_New Graph
        #for i in material_dict:
        #    print i, material_dict[i]

        # Set up schema base for SPARQL Queries
        subject = ""
        if this_file_type == "gbxml":
            subject = URIRef("http://www.gbxml.org/schema#Material")
        if this_file_type == "ifcxml":
            subject = URIRef("http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#IfcMaterialLayer")
        if this_file_type == "citygml":
            subject = URIRef("http://www.citygml.org/index.php?id=1540#Appearance") # This one needs additional information

        # Set up new LD View File
        curr_vocab_empty_graph = Graph()
        current_vocab_parsed = curr_vocab_empty_graph.parse(current_addOn_vocab, format="turtle") # Vocabulary Structure in TTL form parsed
        self.querySetUp(current_vocab_parsed, self.USObase) # Set-up Query Checks

        # Process LD View to add Material Name, Thickness, and ID Triples to existing LD Graph
        materials_startpoint_list = self.get_material_instnace_locations(current_vocab_parsed, inputfile, tree, namespaces, subject)
        material_dict = self.match_addresses(material_dict, materials_startpoint_list, current_vocab_parsed, subject)
        material_dict = self.search_for_material_data(material_dict, current_vocab_parsed, tree, namespaces, subject)
        USO_New, property_counter = self.add_material_graph_triples(material_dict, USO_New, property_counter)

        return USO_New, property_counter

    def get_material_instnace_locations(self, current_vocab_parsed, inputfile, tree, namespaces, subject):

        materials_startpoint_list = list()
        for row in current_vocab_parsed.query("""SELECT ?p ?o
                 WHERE { ?s ?p ?o .}""",
            initBindings={'s' : subject}):
            #print "row: ", row
            if str(row[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#element":
                path_to_materials = str(row[1])
                root = tree.getroot()
                print root.getchildren()
                if path_to_materials[0] == "*":
                    materials_startpoint_list = tree.xpath("." + path_to_materials, namespaces=namespaces)
                else:
                    materials_startpoint_list = tree.xpath(path_to_materials, namespaces=namespaces)
                break

        return materials_startpoint_list  # All material addresses in instance inputfile

    def match_addresses(self, material_dict, materials_startpoint_list, current_vocab_parsed, subject):

        start_id_type = ""
        match_id_type = ""
        rel_path_to_materials_startpoint_list = ""

        #print subject
        for row in current_vocab_parsed.query("""SELECT ?p ?o ?x ?y
                 WHERE { ?s ?p ?o .
                         ?o ?x ?y .}""",
            initBindings={'s' : subject}):
            #print "row: ", row
            if str(row[0]) == str(self.rdfs_isDefinedBy):
                find_end_of_list_now = 0
                data_list = list()
                if str(row[2]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                    #print BNode(row[3])
                    data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row[3]), current_vocab_parsed, data_list, find_end_of_list_now)
                    rel_path_to_materials_startpoint_list = data_list[0]  # So far, have not needed this relationship...
                if str(row[2]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute":
                    #print BNode(row[3])
                    data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row[3]), current_vocab_parsed, data_list, find_end_of_list_now)
                    start_id_type = data_list[0]
                    match_id_type = data_list[1]

        #print "look", start_id_type, match_id_type, rel_path_to_materials_startpoint_list
        match_dict = dict()
        for material in materials_startpoint_list:
            start_id = material.get(str(start_id_type).split("#")[1])
            match_dict[start_id] = material
            #print start_id, material

        for entry in material_dict:
            dict_id = material_dict[entry][0].get(str(match_id_type).split("#")[1])
            if dict_id in match_dict:  # Sometimes all materials gives more than we want, so if it is in this dictionary
                new_mat_loc = match_dict[dict_id]
                pull_existing_entry = material_dict[entry]
                new_entry = [pull_existing_entry[0], pull_existing_entry[1], new_mat_loc]
                material_dict[entry] = new_entry
                #print "stored ", dict_id, new_entry

        return material_dict # So set the graph name and the graph SGA element type

    def search_for_material_data(self, material_dict, current_vocab_parsed, tree, namespaces, subject):
        list_of_data_tuples = list()  # Should be sets of [ Node Name, Associated Data ]
        # List data which is the list of relevant data items from this point ------------------------------------------------------------
        list_type = 0
        l_data_list = list()
        for row in current_vocab_parsed.query("""SELECT ?x ?y
                WHERE { ?s ?l ?o .
                        ?o ?x ?y .}""",
            initBindings={'s' : subject, 'l' : URIRef(str(self.xslt_list))}):
            # Set the element_type in case there are more list types later on...
            if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "material_paths":
                list_type = 1

        for row in current_vocab_parsed.query("""SELECT ?x ?y
                WHERE { ?s ?l ?o .
                        ?o ?x ?y .}""",
            initBindings={'s' : subject, 'l' : URIRef(str(self.xslt_list))}):
            # If this list starts with "start" it is the start Path type of list
            if list_type == 1:
                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                    print "empty"
                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                    print "end of list"
                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[1]) != "material_paths":
                    data = str(row[1])
                if str(row[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row[1]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
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
                    if check_for_sub_nodes > 0:
                        l_data_list, l_find_end_of_list_now, last_blank_node = self.collect_list_items(sub_row[0], current_vocab_parsed, l_data_list, find_end_of_list)
            else:
                print "Type is not an Info, check parent list types in RDF file"   # Actually, this means its another type of element than start if this structure is used

        print l_data_list  # This many sets of data lists (so gbxml has three blank nodes from _:b1, _:b2, and _:b3)
        for l_data in l_data_list:
            paths_to_follow = list()
            start_attr = ""
            match_attr = ""
            element_type = ""
            for row3 in current_vocab_parsed.query("""SELECT ?p ?o ?l_data
                 WHERE { ?l_data ?p ?o .
                         ?o ?x ?y .}""",
                initBindings={'l_data' : BNode(str(l_data))}):
                find_end_of_list_now = 0
                data_list = list()
                for row4 in current_vocab_parsed.query("""SELECT ?l_data ?p ?g
                     WHERE { ?l_data ?p ?g .}""",
                    initBindings={'l_data' : BNode(str(l_data))}):
                    if str(row4[1]) == "http://www.w3.org/2000/01/rdf-schema#label" and str(row4[0]) == str(row3[2]):
                        element_type = row4[2]
                if str(row3[0]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                    data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row3[1]), current_vocab_parsed, data_list, find_end_of_list_now)
                    if len(data_list) == 1:
                        if data_list[0] not in paths_to_follow:
                            paths_to_follow.append(data_list[0])
                    else:
                        # So far this is like where we have to back up and continue somewhere else as in IFC...or use the paths function in other module f gets too complex
                        paths_to_follow = data_list
                if str(row3[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute":
                    data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row3[1]), current_vocab_parsed, data_list, find_end_of_list_now)
                    if len(data_list) == 2:
                        start_attr = data_list[0]
                        match_attr = data_list[1]
                    elif len(data_list) == 1:
                        start_attr = data_list[0]
                        match_attr = data_list[0]
                    else:
                        print "! attributes has 2+ steps...add code here", len(data_list)  # Start with if the next value is another blank node...then there is a next step...or use the paths function in other module

            # For each one of these sets, I need to use material_dict[2](gbxml ex. <Element {http://www.gbxml.org/schema}Material at 0x6247558>) to follow for data
            # We should now have a list of path steps, start attr, and a match attr
            # no * is continue down branches
            # * is start over from root
            # n* is go up n levels and continue on path
            if paths_to_follow != "" and start_attr != "" and match_attr != "" and element_type != "": # We have values for everything for the LD View
                print "working with: ", paths_to_follow, start_attr, match_attr
                # So, use the materials_dict[2] - matching node address to start with - and follow path_to_follow
                #print material_dict
                for graph_node_entry in material_dict:
                    print graph_node_entry, material_dict[graph_node_entry]
                    address_to_start_from = material_dict[graph_node_entry][2]
                    print "length", len(paths_to_follow)
                    for p in paths_to_follow:
                        if p[0] == "*":
                            p = p.replace("*","")
                            address_to_start_from = tree
                        elif "*" in p:
                            p = p.split("*")[1]
                            levels_up = int(p.split("*")[0])
                            while levels_up != 0:
                                p = "../" + p
                                levels_up -= 1
                            p.replace("//","/")
                        else:
                            p = p
                        if str(start_attr.split("#")[1]) == "none" and str(match_attr.split("#")[1]) == "none":
                            # Then this means that there are no attributes and thus only a direct simple path to follow to data:
                            data_locations = address_to_start_from.xpath(str("." + p), namespaces=namespaces)
                            for text_item in data_locations:
                                data_tuple = [ element_type, text_item.text ]
                                pull_existing_entry = material_dict[graph_node_entry]
                                pull_existing_entry.append(data_tuple)
                                material_dict[graph_node_entry] = pull_existing_entry
                        if str(element_type) == "Relative_ID" and str(p) == "none":
                            # Then this is a case of one attribute to find as data ID for Relative_ID case, no other paths needed thus p.split("#")[1] == "none"
                            new_data_from_loc = address_to_start_from.get(str(start_attr).split("#")[1])
                            data_tuple = [ element_type, new_data_from_loc ]
                            pull_existing_entry = material_dict[graph_node_entry]
                            pull_existing_entry.append(data_tuple)
                            material_dict[graph_node_entry] = pull_existing_entry

        return material_dict # Found Name, ID, and Thickness

    def add_material_graph_triples(self, material_dict, USO_New, property_counter):
        # Add triple based on what was entered into the material_dict as tuples after value[2]

        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")
        triple_counter = 0

        for i in material_dict:
            counter = 3
            while len(material_dict[i]) > counter: # While there is still another tuple in the dictionary row
                USO_New.add( (URIRef(i), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal(str(material_dict[i][counter][0]) ) ) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(material_dict[i][counter][1])) ) )
                #print "Added Triple: ", URIRef(i), hasProperty, "Property" + str(property_counter), "with Type and Value: ", str(material_dict[i][counter][0]), str(material_dict[i][counter][1])
                property_counter += 1
                counter += 1
                triple_counter += 1

        print "Added ", triple_counter, " New Triples"
        return USO_New, property_counter  # USO_New but updated with material information

    def querySetUp(self, graph, base):
        for subject,predicate,obj in graph:
           if not (subject,predicate,obj) in graph:
              raise Exception("Iterator / Container Protocols are Broken!!")
        return 0

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








