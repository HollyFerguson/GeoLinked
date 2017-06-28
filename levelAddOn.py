#-------------------------------------------------------------------------------
# Name:        levelAddOn.py
# Purpose:     Add Building Level Names and IDs to LD Graph
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     11/01/2016
# Copyright:   (c) Holly Tina Ferguson 2016
# Licence:     The University of Notre Dame


# 1) where I pull all instances of building storeys (for ifcxml is IfcBuildingLevel tag), so this is the
#    same address location as is recorded in the passed in dictionary...this is a pre-processing list to
#    pull info into a dict() to save processing later
# 2) pull all instnaces of surfaces that are already in the graph which will now be assigned a level & elevation
# 3) match that to passed dictionary address entry to set the graph name and element type
# 4) for each of these three below, search for data in pre-processed dictionary

# from there where I go to get Name        (or the couple possibilities)
# from there where I go to get ID          (or the couple possibilities)
# from there where I go to get Thickness   (or the couple possibilities)

# CityGML has slightly different processing because you are matching data to spaces from possibly several different buildings at once

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


class Add_Levels():
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

    def add_level_name_and_id(self, tree, namespaces, level_dict_spaces, level_dict_surfaces, this_file_type, inputfile, USO_New, current_addOn_vocab, property_counter, missing_link_dict_for_citygml):

        # What I am starting with as existing in the USO_New Graph
        print "Reaching Levels..."
        #for i in missing_link_dict_for_citygml:
        #    print "?", i, missing_link_dict_for_citygml[i]  # When handling CityGML, pre-parsing is done, [SpaceAddress, parent and child links]
        #    print "path ", tree.getpath(i)
        #    print "from this can get the interior room distinction" #, is "interiorRoom" or "Room" in tree.getpath(i), if so then it has a relatinship to capture...good example for paper with CartCoorSys

        # Set up schema base for SPARQL Queries
        subject = ""
        if this_file_type == "gbxml":
            subject = URIRef("http://www.gbxml.org/schema#Surface")
        if this_file_type == "ifcxml":
            subject = URIRef("http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#IfcRelSpaceBoundary")
        if this_file_type == "citygml":
            subject = URIRef("http://www.citygml.org/index.php?id=1540#surfaceMember") # This one needs additional information

        # Set up new LD View File
        curr_vocab_empty_graph = Graph()
        current_vocab_parsed = curr_vocab_empty_graph.parse(current_addOn_vocab, format="turtle") # Vocabulary Structure in TTL form parsed
        self.querySetUp(current_vocab_parsed, self.USObase) # Set-up Query Checks

        # Pre-processing of the Levels
        pre_process_dict, pre_process_dict_city = self.pre_process(current_vocab_parsed, inputfile, tree, namespaces, subject, this_file_type)

        if this_file_type == "citygml":
            # Process Mined and Pre-Processed Data to add Material Name, Thickness, and ID Triples to existing LD Graph
            USO_New, property_counter = self.add_citygml_triples(missing_link_dict_for_citygml, USO_New, property_counter, pre_process_dict_city)
        else:
            # Levels can, at least so far in gbxml, be associated with less steps by processing the existing level_dict to add spaces for each surface, though does not effect ifcxml
            level_dict_surfaces = self.add_parent_nodes(USO_New, level_dict_spaces, level_dict_surfaces)

            # Find connections of each graph surface to building level dict information, using spaces or surfaces
            level_dict_surfaces = self.search_for_level_data(level_dict_surfaces, level_dict_spaces, current_vocab_parsed, tree, namespaces, subject, pre_process_dict)

            # Process Mined and Pre-Processed Data to add Material Name, Thickness, and ID Triples to existing LD Graph
            USO_New, property_counter = self.add_level_graph_triples(level_dict_surfaces, USO_New, property_counter, pre_process_dict)

        return USO_New, property_counter

    def add_citygml_triples(self, missing_link_dict_for_citygml, USO_New, property_counter, pre_process_dict_city):
        # Similar to what add_level_graph_triples is doing, but here is at the space level and if there are multiple buildings, as is the case often in CityGML
        triple_counter = 0

        for each_space_key in missing_link_dict_for_citygml:  # For each possible space in the whole set
            # Want to go up nodes to match address of node with either pre_process_dict[1] OR pre_process_dict_city[1]
            no_match = 0
            direct_parent = ""
            look_at_parent = each_space_key
            while no_match == 0:
                direct_parent = look_at_parent.getparent()
                if direct_parent is None:
                    break
                else:
                    #print "ok: ", each_space_key, direct_parent
                    # So check until the upper building node is a possibility and use that if nothing else was found
                    BuildingTag = 0
                    #if str(each_space_key.tag) == "{http://www.opengis.net/citygml/building/2.0}Building" or str(each_space_key.tag) == "{http://www.opengis.net/citygml/relief/2.0}ReliefFeature":
                    for key in pre_process_dict_city:
                        if direct_parent == pre_process_dict_city[key][0]:
                            #then get this data 1, 2, 3
                            #last_item = pre_process_dict_city[key][-1]
                            name = pre_process_dict_city[key][1]
                            elevation = pre_process_dict_city[key][2]
                            relative_id = key
                            no_match = 1
                            #print "came here", name, elevation, relative_id, direct_parent
                            # Then make Triples from here...
                            USO_New, property_counter, triple_counter = self.city_triples(USO_New, property_counter, triple_counter, name, elevation, relative_id, each_space_key, missing_link_dict_for_citygml)
                            break
                        if str(direct_parent.tag) == "{http://www.opengis.net/citygml/building/2.0}Building":
                            BuildingTag = direct_parent
                            break
                    if BuildingTag != 0 or str(each_space_key.tag) == "{http://www.opengis.net/citygml/building/2.0}Building":  # Now BuildingTag should be the respective Building Element
                        #then set the data from pre_process_dict 1, 2, 3
                        #print "ok till here", pre_process_dict_city
                        for key in pre_process_dict_city:
                            if BuildingTag == pre_process_dict_city[key][0] or each_space_key == pre_process_dict_city[key][0]:
                                #last_item = pre_process_dict_city[key][-1]
                                name = pre_process_dict_city[key][1]
                                elevation = pre_process_dict_city[key][2]
                                relative_id = key
                                no_match = 1
                                print "or here", name, elevation, relative_id, direct_parent
                                # Then make Triples from here...
                                USO_New, property_counter, triple_counter = self.city_triples(USO_New, property_counter, triple_counter, name, elevation, relative_id, each_space_key, missing_link_dict_for_citygml)
                                break
                    look_at_parent = direct_parent

        print "Added ", triple_counter, " New Triples"

        return USO_New, property_counter

    def city_triples(self, USO_New, property_counter, triple_counter, name, elevation, relative_id, each_space_key, missing_link_dict_for_citygml):

        #print "key?", each_space_key
        #for v in missing_link_dict_for_citygml:
        #    print "v: ", v, missing_link_dict_for_citygml[v]
        i = missing_link_dict_for_citygml[each_space_key][1]

        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")

        USO_New.add( (URIRef(i), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Name") ) )
        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(name) ) ) )
        print "Added Triple A: ", URIRef(i), hasProperty, "Property" + str(property_counter), "with Type and Value: Name ", str(name)
        property_counter += 1
        triple_counter += 1

        USO_New.add( (URIRef(i), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Elevation") ) )
        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(elevation)) ) )
        print "Added Triple B: ", URIRef(i), hasProperty, "Property" + str(property_counter), "with Type and Value: Elevation ", str(elevation)
        property_counter += 1
        triple_counter += 1

        USO_New.add( (URIRef(i), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Relative_ID") ) )
        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(relative_id)) ) )
        print "Added Triple C: ", URIRef(i), hasProperty, "Property" + str(property_counter), "with Type and Value: Relative_ID", str(relative_id)
        property_counter += 1
        triple_counter += 1

        return USO_New, property_counter, triple_counter

    def add_level_graph_triples(self, level_dict_surfaces, USO_New, property_counter, pre_process_dict):
        # Add triple based on what was entered into the pre_process_dict with key being the last entry in the level_dict_surfaces
        # Using last entry where it is not "none" because differences depending on where the nodes were matched and what parents could be added to each row

        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")
        triple_counter = 0

        for i in level_dict_surfaces: # For each "surface"
            last_item = level_dict_surfaces[i][-1]
            if str(last_item) != "none": # So will only add triple where the surface was able to be associated with a building level, else will add nothing
                name = pre_process_dict[last_item][1]
                elevation = pre_process_dict[last_item][2]
                relative_id = last_item

                USO_New.add( (URIRef(i), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Name") ) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(name) ) ) )
                print "Added Triple A: ", URIRef(i), hasProperty, "Property" + str(property_counter), "with Type and Value: Name ", str(name)
                property_counter += 1
                triple_counter += 1

                USO_New.add( (URIRef(i), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Elevation") ) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(elevation)) ) )
                print "Added Triple B: ", URIRef(i), hasProperty, "Property" + str(property_counter), "with Type and Value: Elevation ", str(elevation)
                property_counter += 1
                triple_counter += 1

                USO_New.add( (URIRef(i), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Relative_ID") ) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(relative_id)) ) )
                print "Added Triple C: ", URIRef(i), hasProperty, "Property" + str(property_counter), "with Type and Value: Relative_ID", str(relative_id)
                property_counter += 1
                triple_counter += 1


        print "Added ", triple_counter, " New Triples"

        return USO_New, property_counter

    def search_for_level_data(self, level_dict_surfaces, level_dict_spaces, current_vocab_parsed, tree, namespaces, subject, pre_process_dict):

        # This is where the handling happens for the isDefinedBy nodes from the top level of triples
        # _:b0 is the starting point set of nodes, so depending on what that is (Space or SpaceBoundary) use different matching index from level_dict_surfaces to pre_process_dict
        type_of_search = ""
        start_node_list = list()
        for row in current_vocab_parsed.query("""SELECT ?s ?l ?o ?a ?b
                WHERE { ?s ?l ?o .
                        ?o ?a ?b .}""",
            initBindings={'s' : subject, 'l' : URIRef(str(self.rdfs_base+"isDefinedBy"))}):
            #print "now try", row[3], row[4]
            find_end_of_list_now = 0
            data_list_isDefinedBy = list()
            data_list = list()
            start_node = ""
            start_attr = ""
            match_attr = ""
            match_attr2 = ""
            if str(row[3]) == "http://www.w3.org/2000/01/rdf-schema#isDefinedBy":
                type_of_search = row[4]
            if str(row[3]) == "https://www.w3.org/2003/g/data-view#transformationProperty":
                data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row[4]), current_vocab_parsed, data_list, find_end_of_list_now)
                start_node = data_list[0]
                if str(start_node[0]) == "*":
                    start_node = str(start_node)[1:]
                else:
                    print "add path case when not starting with *"
                    #tree = ?
                start_node_list = tree.xpath(start_node, namespaces=namespaces)
                data_list_isDefinedBy = data_list
            if str(row[3]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute":
                data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row[4]), current_vocab_parsed, data_list, find_end_of_list_now)
                start_attr = data_list[0]
                match_attr = data_list[1]
                if len(data_list) == 3:
                    match_attr2 = data_list[2]

        # This is where the handling happens for the xslt:list("level_paths"^^xsd:string, etc.) nodes from the top level of triples
        l_data_list = list()
        right_blank = ""
        for row in current_vocab_parsed.query("""SELECT ?s ?l ?o ?a ?b
                WHERE { ?s ?l ?o .
                        ?o ?a ?b .}""",
            initBindings={'s' : subject, 'l' : URIRef(str(self.xslt_list))}):
            #print "now try"  #, row[0], row[1], row[2], row[3], row[4]
            if str(row[3]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[4]) == "level_paths":
                correct_pair = row[2]
                for row2 in current_vocab_parsed.query("""SELECT ?o ?x ?y
                        WHERE { ?o ?x ?y .}""",
                    initBindings={'o' : BNode(correct_pair)}):
                    if str(row2[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row2[2]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                        find_end_of_list = 0
                        next_blank_node = BNode(row2[2])
                        # If there are sub lists nested, then there will be results from this:
                        check_for_sub_nodes = 0
                        sub_row = BNode("000")
                        for sub_row in current_vocab_parsed.query("""SELECT ?x ?a ?b
                                WHERE { ?blank ?first ?x .
                                        ?x ?a ?b .}""",
                            initBindings={'blank' : next_blank_node, 'first' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first") }):
                            check_for_sub_nodes += 1
                        if check_for_sub_nodes > 0:
                            l_data_list, l_find_end_of_list_now, last_blank_node = self.collect_list_items(sub_row[0], current_vocab_parsed, l_data_list, find_end_of_list)

        print "l_data_list: ", l_data_list  # This many sets of data lists (so gbxml has three blank nodes from _:b4)
        data_list_paths = list()
        data_list_attrs = list()
        for l_data in l_data_list:
            initial_rel_id_attr = ""
            name_attr = ""
            level_attr = ""
            for row3 in current_vocab_parsed.query("""SELECT ?p ?o ?x ?y
                 WHERE { ?l_data ?p ?o .
                         ?o ?x ?y .}""",
                initBindings={'l_data' : BNode(str(l_data))}):
                find_end_of_list_now = 0
                data_list = list()
                if str(row3[0]) == "https://www.w3.org/2003/g/data-view#transformationProperty" and str(row3[2]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest":
                    data_list_paths, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row3[1]), current_vocab_parsed, data_list, find_end_of_list_now)
                if str(row3[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute" and str(row3[2]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest":  # First one is the Relative_ID for this Building Level
                    data_list_attrs, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row3[1]), current_vocab_parsed, data_list, find_end_of_list_now)

        index_to_match = 0
        if str(type_of_search) == "Space":
            # Then the buildinglevel node (pre_process_dict[0]) matches to level_dict_surface[2], the space node
            index_to_match = 3
        elif str(type_of_search) == "SpaceBoundary":
            # Then the buildinglevel node (pre_process_dict[0]) matches to level_dict_surface[0], the surface node
            index_to_match = 0
        else:
            print "index_to_match _____left at 0 since not matching Space or SpaceBoundary"
        print "type_of_search", type_of_search, index_to_match, data_list_paths, data_list_attrs

        # Have now pulled all LD View Information so make the match to like a BuildingLevel to a level_dict_surfaces entry
        for level_dict_surface in level_dict_surfaces:
            # Handling currently if attr is none or if transprop is none
            correct_pre_process_key = "none"
            if str(data_list_paths[0]) == "none": # Then there are no paths to search so process with data_list_attrs
                if len(data_list_attrs) == 1:
                    attr = data_list_attrs[0].split("#")[1]
                    if len(level_dict_surfaces[level_dict_surface]) >= index_to_match+1:
                        relevant_attr = level_dict_surfaces[level_dict_surface][index_to_match].get(str(attr))
                        correct_pre_process_key = relevant_attr
                else:
                    print "data_list_attrs is more than 1"
            elif str(data_list_attrs[0]) == "none": # Then there are no attrs to search so process with data_list_paths
                if len(data_list_paths) == 1:
                    print "data_list_paths is 1"
                else:
                    print "data_list_paths is more than 1"
            else: # We assume that there is data for both and some other type of processing needs to happen
                # To make connection: "2*/doc:iso_10303_28/ifc:uos/ifc:IfcRelSpaceBoundary/ifc:RelatedBuildingElement*" Go to this place and take ref of child[0] then go back 2 levels and match that to level_dict_surface[0]
                # "2*/ifc:RelatedBuildingElement*" can be reduced to this because we already know what surface we are starting at: level_dict_surface[0]
                if len(data_list_paths) == 1 and len(data_list_attrs) == 1:
                    # So follow path directions and see what pre_process_dict[4] the data_list_attrs[0] (or ref) belongs to
                    any_backtracking = 0  # So far this has not been needed since we are at and using the current graph node entry
                    get_child = 0
                    reconstructed_path = data_list_paths[0]
                    if reconstructed_path[-1:] == "*":
                        reconstructed_path = reconstructed_path[:-1]
                        get_child = 1
                    if "*" in reconstructed_path:
                        # Then probably at the beginning or at beginning with backtracking
                        reconstructed_pathA = reconstructed_path.split("*")[0]
                        reconstructed_pathB = reconstructed_path.split("*")[1]
                        if reconstructed_pathA != "" :
                            any_backtracking = int(reconstructed_pathA)
                            reconstructed_path = reconstructed_pathB

                    match_attr = data_list_attrs[0].split("#")[1]
                    if get_child == 1:
                        child_node_fill_in_point = level_dict_surfaces[level_dict_surface][index_to_match].xpath("."+reconstructed_path, namespaces=namespaces)
                        if len(child_node_fill_in_point) > 0: # Some cases, Surfaces do not have a /ifc:RelatedBuildingElement set of tags so skip
                            child_node_fill_ins = child_node_fill_in_point[0].getchildren()
                            reconstructed_path = reconstructed_path + "/ifc:" + str(child_node_fill_ins[0].tag).split("}")[1]
                            match_attr_to_preprocessdict = child_node_fill_ins[0].get(str(match_attr))
                            print "sss", match_attr_to_preprocessdict
                        else:
                            print "Cases where RelSpaceBoundary is missing child tags so is skipped: ", match_attr_to_preprocessdict
                            print level_dict_surface
                            print index_to_match
                    else:
                        # Look for the data_list_attrs[0] in existing reconstructed_path variable
                        child_node_fill_in_passed = level_dict_surfaces[level_dict_surface][index_to_match].xpath("."+reconstructed_path, namespaces=namespaces)
                        match_attr_to_preprocessdict = child_node_fill_in_passed[0].get(match_attr)

                    # Use match_attr_to_preprocessdict which is some ID tag and match it to one of the pre_process_dict[4] entries, this index is a list
                    for pre_process_item in pre_process_dict:
                        for attr_entry in pre_process_dict[pre_process_item][4]:
                            if attr_entry == match_attr_to_preprocessdict:
                                # This Building Level belongs with the current surface entry of level_dict_surface
                                correct_pre_process_key = pre_process_item
                else:
                    print "data in both data_list_paths and data_list_attrs, add processing type"

            # Add the correct_pre_process_key to the level_dict_surfaces so lookups in next module will be based on level_dict_surfaces[3]
            # This is where some Surfaces are associated with a Spaces, unlike gbxml Shading Devices
            # So, if there is a building level to associate, then it will, else the building level set will be none, as with shading devices
            current_entry = level_dict_surfaces[level_dict_surface]
            if len(level_dict_surfaces[level_dict_surface]) == 4:
                new_entry = current_entry[0], current_entry[1], current_entry[2], current_entry[3], correct_pre_process_key
                level_dict_surfaces[level_dict_surface] = new_entry
            if len(level_dict_surfaces[level_dict_surface]) == 2:
                new_entry = current_entry[0], current_entry[1], correct_pre_process_key
                level_dict_surfaces[level_dict_surface] = new_entry

        #for level_dict_surface in level_dict_surfaces:
        #    print level_dict_surface, level_dict_surfaces[level_dict_surface]

        return level_dict_surfaces

    def add_parent_nodes(self, USO_New, level_dict_spaces, level_dict_surfaces):
        #for s in level_dict_spaces:
        #    print s, level_dict_spaces[s]
        for l in level_dict_spaces:
            for row in USO_New.query("""SELECT ?l ?m ?n
                    WHERE { ?l ?m ?n .}""",
                initBindings={'m' : URIRef(str(self.USObase)+"hasSpaceBoundaryMember"), 'l' : URIRef(l)}):
                for su in level_dict_surfaces:
                    if su == row[2]:
                        current_entry = level_dict_surfaces[su]
                        new_entry = current_entry[0], current_entry[1], l, level_dict_spaces[l][0]
                        #print new_entry
                        level_dict_surfaces[su] = new_entry

        return level_dict_surfaces # Now with spaces appended

    def pre_process(self, current_vocab_parsed, inputfile, tree, namespaces, subject, this_file_type):
        # Get the list of paths leading to the types of nodes to pre-process data and locations from in the instance
        pre_process_dict = dict()
        pre_process_dict_city = dict()
        l_data_list = list()
        for row in current_vocab_parsed.query("""SELECT ?s ?l ?o ?a ?b
                WHERE { ?s ?l ?o .
                        ?o ?a ?b .}""",
            initBindings={'s' : subject, 'l' : URIRef(str(self.xslt_list))}):
            #print "now try", row[0], row[1], row[2], row[3], row[4]
            if str(row[3]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#first" and str(row[4]) == "pre_process_paths":
                correct_pair = row[2]
                for row2 in current_vocab_parsed.query("""SELECT ?o ?x ?y
                        WHERE { ?o ?x ?y .}""",
                    initBindings={'o' : BNode(correct_pair)}):
                    if str(row2[1]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest" and str(row2[2]) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil":
                        find_end_of_list = 0
                        next_blank_node = BNode(row2[2])
                        # If there are sub lists nested, then there will be results from this:
                        check_for_sub_nodes = 0
                        sub_row = BNode("000")
                        for sub_row in current_vocab_parsed.query("""SELECT ?x ?a ?b
                                WHERE { ?blank ?first ?x .
                                        ?x ?a ?b .}""",
                            initBindings={'blank' : next_blank_node, 'first' : URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first") }):
                            check_for_sub_nodes += 1
                        if check_for_sub_nodes > 0:
                            l_data_list, l_find_end_of_list_now, last_blank_node = self.collect_list_items(sub_row[0], current_vocab_parsed, l_data_list, find_end_of_list)

        print "l_data_list: ", l_data_list  # This many sets of data lists (so gbxml has three blank nodes from _:b4)
        for l_data in l_data_list:
            initial_rel_id_attr = ""
            name_attr = ""
            level_attr = ""
            match_attr = ""
            name_path = ""
            level_path = ""
            match_path = ""
            building_level_nodes = list()
            for row3 in current_vocab_parsed.query("""SELECT ?p ?o
                 WHERE { ?l_data ?p ?o .}""",
                initBindings={'l_data' : BNode(str(l_data))}):
                if str(row3[0]) == "http://www.w3.org/2000/01/rdf-schema#isDefinedBy":
                    building_level_nodes = tree.xpath(str(row3[1]), namespaces=namespaces)
            city_nesting = 0
            for row3 in current_vocab_parsed.query("""SELECT ?p ?o ?x ?y
                 WHERE { ?l_data ?p ?o .
                         ?o ?x ?y .}""",
                initBindings={'l_data' : BNode(str(l_data))}):
                find_end_of_list_now = 0
                data_list = list()
                if str(row3[0]) == "https://www.w3.org/2003/g/data-view#transformationProperty" and str(row3[2]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest":
                    data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row3[1]), current_vocab_parsed, data_list, find_end_of_list_now)
                    name_path = data_list[0]
                    if data_list[1]:
                        level_path = data_list[1]
                    print "data_list", data_list
                    if data_list[2]:
                        match_path = data_list[2]
                if str(row3[0]) == "https://www.w3.org/TR/xslt-30/schema-for-xslt30#attribute" and str(row3[2]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest":  # First one is the Relative_ID for this Building Level
                    data_list, find_end_of_list_now, last_blank_node = self.collect_list_items(BNode(row3[1]), current_vocab_parsed, data_list, find_end_of_list_now)
                    initial_rel_id_attr = data_list[0]
                    name_attr = data_list[1]
                    level_attr = data_list[2]
                    if data_list[3]:
                        match_attr = data_list[3]
                        if match_attr == "fill_rest_with_parent_data":
                            city_nesting = 1

            #print "pulled_data: ", name_path, level_path, match_path, initial_rel_id_attr, name_attr, level_attr, match_attr
            if city_nesting == 1:
                # In CityGML there spaces are nested so we need to check for additional building parts with their IDs
                building_level_nodes2 = list()
                for b in building_level_nodes:
                    # For IFC and GBXML this is a list of Building Levels, for CityGML this is a list of separate Buildings
                    # Therefor we need to check how these breakdown into levels, if at all, then entry is (building, other levels in building)
                    b_parts_in_this_building = b.xpath("." + match_path, namespaces=namespaces)
                    building_level_nodes2.append([b, b_parts_in_this_building])
                building_level_nodes = building_level_nodes2

            for l in building_level_nodes:
                # making entries: pre_process_dict[b_id] = building_level_node_address(b), name_data, level_data(elevation from ground))
                b = l
                if this_file_type == "citygml":
                    b = l[0]
                    attrs = list(b.attrib)
                    for i in attrs:
                        if str(i.split("}")[1]) == "id":
                            b_id = b.get(str(i))
                else:
                    b_id = b.get(str(initial_rel_id_attr.split("#")[1]))

                name_paths = b.xpath("." + name_path, namespaces=namespaces)
                name_data = name_paths[0].text
                level_paths = b.xpath("." + level_path, namespaces=namespaces)
                #print "level_paths", level_paths
                level_data = ""
                if len(level_paths) > 0:
                    level_data = level_paths[0].text
                if str(name_attr.split("#")[1]) != "none":
                    name_data = name_paths[0].get(str(name_attr.split("#")[1]))
                if str(level_attr.split("#")[1]) != "none":
                    level_data = level_paths[0].get(str(level_attr.split("#")[1]))

                # Where there needs to have an additional match to make node matches (ifcxml) find match in match_path
                extended_match_nodes = list()
                extended_match_ids = list()
                if len(match_path.split("*")) == 2:
                    # Then this is a case where a match needs to happen since have to go back levels
                    # Ex.: 1*/ifc:IfcRelContainedInSpatialStructure/ifc:RelatingStructure/ifc:IfcBuildingStorey
                    amount_back = int(match_path.split("*")[0])
                    back_path = match_path.split("*")[1]
                    while (amount_back != 0):
                        back_path = "/.." + back_path
                        amount_back -= 1
                    back_path = "." + back_path
                    possible_matches = b.xpath(back_path, namespaces=namespaces)
                    for option in possible_matches:
                        match_ref = option.get(match_attr.split("#")[1])
                        if str(b_id) == str(match_ref):
                            if this_file_type == "ifcxml":
                                extended_match_nodes = option.xpath("../../ifc:RelatedElements", namespaces=namespaces) # This is a set of surface elements
                                extended_match_nodes = extended_match_nodes[0].getchildren()
                                for e in extended_match_nodes:
                                    ext_ref = e.get("ref")
                                    extended_match_ids.append(ext_ref)
                                #print "extended_match_node", extended_match_nodes, extended_match_ids
                            else:
                                print "Add a node match path for citygml if needed..."
                pre_process_dict[b_id] = [b, name_data, level_data, extended_match_nodes, extended_match_ids]

                pre_process_dict_ref = b_id
                if len(l) > 1:
                    # Then handling a set of buildings and with options for nested level data
                    for lev in l[1]:
                        # CityGML: So this would get all BuildingParts from under each building node with a reference ID to a pre_process_dict key
                        name_paths = lev.xpath("." + name_path, namespaces=namespaces)
                        if len(name_paths) != 0:
                            name_data = name_paths[0].text
                        level_paths = lev.xpath("." + level_path, namespaces=namespaces)
                        if len(level_paths) != 0:
                            level_data = level_paths[0].text
                        lev_id = "non_unique_key"
                        if this_file_type == "citygml":
                            attrs = list(lev.attrib)
                            for i in attrs:
                                if str(i.split("}")[1]) == "id":
                                    lev_id = lev.get(str(i))
                        pre_process_dict_city[lev_id] = [lev, name_data, level_data, extended_match_nodes, extended_match_ids, pre_process_dict_ref]

        print "pre-process-dict"
        for b in pre_process_dict:  # Make sure all possibilities are in pre_process_dict_city
            pre_process_dict_city[b] = pre_process_dict[b]
        '''
        for b in pre_process_dict:
            print b, pre_process_dict[b]
            pre_process_dict_city[b] = pre_process_dict[b]
        for c in pre_process_dict_city:
            print c, pre_process_dict_city[c]
        '''

        return pre_process_dict, pre_process_dict_city

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
