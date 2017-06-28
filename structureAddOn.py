#-------------------------------------------------------------------------------
# Name:        structureAddOn.py
# Purpose:     Add Structure Geometries and IDs to LD Graph
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     1/04/2017
# Copyright:   (c) Holly Tina Ferguson 2017
# Licence:     The University of Notre Dame


# 1) pre-process all possible columns and beams
# 2) match that to passed dictionary address entry to set the graph name and element type
# 3) for each element, search for geometries
# 4) add data in these three as graph attributes to the respective graph named element

# Notes:
# Since structural elements are broken into their own subparts sometimes, we consider a stuctural element as a "surface_set"
# Thus, each surface_set (which may be one data piece) is assigned back to the semantic graph


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


class Add_Structures():
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

    def add_struct_geometries(self, tree, namespaces, structure_dict_spacecollection, structure_dict_spaces, structure_dict_surfaces, structure_dict_materials, this_file_type, inputfile, USO_New, current_addOn_vocab, property_counter):
        # Set up new LD View File
        #print "current_addOn_vocab", current_addOn_vocab
        curr_vocab_empty_graph = Graph()
        current_vocab_parsed = curr_vocab_empty_graph.parse(current_addOn_vocab, format="turtle") # Vocabulary Structure in TTL form parsed
        self.querySetUp(current_vocab_parsed, self.USObase) # Set-up Query Checks
        print "current_pun_vocab_parsed: "
        SurfaceCases1 = list()
        SurfaceCases2 = list()
        struct_data_list1 = list()
        struct_data_list2 = list()

        for s,p,o in current_vocab_parsed.triples( (None, None, None) ):
            if str(s) == "http://www.gbxml.org/schema#Surface1" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface1":
                if str(p) == "start":
                    SurfaceCases1 = tree.xpath(str(o), namespaces=namespaces)
            if str(s) == "http://www.gbxml.org/schema#Surface2" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface2":
                if str(p) == "start":
                    SurfaceCases2 = tree.xpath(str(o), namespaces=namespaces)

        coor_order_dict1 = dict()
        coor_order_dict2 = dict()
        new_possibile_sets1 = list()
        new_possibile_sets2 = list()
        other_list1 = list()
        other_list2 = list()
        struct_data_list_names1 = list()
        struct_data_list_names2 = list()

        for s,p,o in current_vocab_parsed.triples( (None, None, None) ):
            if str(s) == "http://www.gbxml.org/schema#Surface1" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface1":  # Columns
                if str(p) == "name":
                    struct_data_list1, new_possibile_sets1 = self.handle_name(o, SurfaceCases1, struct_data_list1, namespaces)
            if str(s) == "http://www.gbxml.org/schema#Surface2" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface2":  # Beams
                if str(p) == "name":
                    struct_data_list2, new_possibile_sets2 = self.handle_name(o, SurfaceCases2, struct_data_list2, namespaces)
        struct_data_list_names1 = struct_data_list1
        struct_data_list_names2 = struct_data_list2

        for s,p,o in current_vocab_parsed.triples( (None, None, None) ):
            if str(s) == "http://www.gbxml.org/schema#Surface1" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface1":  # Columns
                if str(p) == "id":
                    struct_data_list1 = self.handle_ids(o, struct_data_list1, namespaces)
            if str(s) == "http://www.gbxml.org/schema#Surface2" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface2":  # Beams
                if str(p) == "id":
                    struct_data_list2 = self.handle_ids(o, struct_data_list2, namespaces)

        # Parse the pieces of paths together so that the next steps know what order to execute the processing...
        for s,p,o in current_vocab_parsed.triples( (None, None, None) ):
            if str(s) == "http://www.gbxml.org/schema#Surface1" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface1":  # Columns
                if str(p) == "coors":
                    coor_order_dict1, other_list1 = self.order_coors(o, coor_order_dict1, other_list1, this_file_type)
            if str(s) == "http://www.gbxml.org/schema#Surface2" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface2":  # Beams
                if str(p) == "coors":
                    coor_order_dict2, other_list2 = self.order_coors(o, coor_order_dict2, other_list2, this_file_type)

        # For coordinate information we do this function call after so we have the correct path order
        #struct_data_list1 = self.handle_coors_nonset(struct_data_list_names1, struct_data_list1, namespaces, coor_order_list1, new_possibile_sets1, other_list1)
        struct_data_list1 = self.handle_coors(struct_data_list_names1, struct_data_list1, namespaces, coor_order_dict1, new_possibile_sets1, this_file_type, SurfaceCases1, tree)
        if len(struct_data_list2) != 0: # So far struct_data_list2 not filled because handling only columns, will be a part for each new type --- beams, etc.
            #struct_data_list2 = self.handle_coors_nonset(struct_data_list_names2, struct_data_list2, namespaces, coor_order_list2, new_possibile_sets2, other_list2)
            print "was not empty so doing beam part"
            struct_data_list2 = self.handle_coors(struct_data_list_names2, struct_data_list2, namespaces, coor_order_dict2, new_possibile_sets2, this_file_type, SurfaceCases2, tree)

        # Re-combine the different sets of data: So that means you woudl combine all the column information with the beam information, etc.
        for i in struct_data_list2:
            struct_data_list1.append(i)
        struct_data_list = struct_data_list1
        # Now everything should at least be in struct_data_list

        # Now we have gathered all of the data, but at least in gbxml the square columns often have all separate surfaces, so we need to group the sets of data to create each column
        # Additionally interesting is that since for gbxml they are called surfaces, these individual instances are already in the semantic graph
        # So for this type the space association is already done meaning we could just add (That surface, (hasProperty "structural_piece")[has Name (or Type if Column or Beam), has Rel_ID, part of Column X, CoorData])
        if this_file_type == "gbxml":
            struct_data_list, data_sets_by_struct_piece = self.makegroups(struct_data_list, this_file_type)
            triple_counter = 0
            USO_New, property_counter, triple_counter = self.add_gbxml_struct_triples(USO_New, property_counter, triple_counter, data_sets_by_struct_piece, structure_dict_surfaces)
            print "Added ", triple_counter, " new Triples from gbxml..."
        if this_file_type == "ifcxml":
            struct_data_list, data_sets_by_struct_piece = self.makegroups(struct_data_list, this_file_type)
            data_sets_by_struct_piece, levels, slabD = self.column_to_level(data_sets_by_struct_piece, namespaces, tree)
            triple_counter = 0
            USO_New, property_counter, triple_counter = self.add_ifcxml_struct_triples(USO_New, property_counter, triple_counter, data_sets_by_struct_piece, structure_dict_spacecollection, levels, slabD, structure_dict_surfaces, tree, namespaces)
            print "Added ", triple_counter, " new Triples from ifcxml..."

        return USO_New, property_counter

    def column_to_level(self, data_sets_by_struct_piece, namespaces, tree):
        print "column_to_level funciton"
        slabD = dict()
        building_levels = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcBuildingStorey", namespaces=namespaces)
        levels = list()
        for i in data_sets_by_struct_piece:
            struct_id = data_sets_by_struct_piece[i][0][0].get("id")
            level_markers = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelContainedInSpatialStructure/ifc:RelatingStructure/ifc:IfcBuildingStorey", namespaces=namespaces)
            possible_set = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelContainedInSpatialStructure/ifc:RelatedElements", namespaces=namespaces)
            possible_ids = list()
            for poss in possible_set:
                possible_idsa = poss.getchildren()
                for p in possible_idsa:
                    possible_ids.append(p)

                    if "Beam" in str(p):
                        par = p.getparent()
                        sl = par.xpath("./ifc:IfcSlab", namespaces=namespaces)
                        if len(sl) > 0 and p not in slabD:
                            slabD[p] = (p.get("ref"), sl[0].get("ref"))
                            print "added SLAB", p, slabD[p]

            for possible in possible_ids:
                possible_ref = possible.get("ref")
                if possible_ref == struct_id:
                    level_marker = level_markers[0].get("ref")
                    for lev in building_levels:
                        if lev.get("id") == level_marker:
                            level_name = lev.xpath("./ifc:Name", namespaces=namespaces)
                            temp = data_sets_by_struct_piece[i]
                            new_level_name = level_name[0].text
                            #print "new_level_name", new_level_name
                            new_set = ( ( temp, new_level_name ) )
                            data_sets_by_struct_piece[i] = new_set
                            if new_level_name not in levels:
                                levels.append(new_level_name)

        return data_sets_by_struct_piece, levels, slabD

    def add_ifcxml_struct_triples(self, USO_New, property_counter, triple_counter, data_sets_by_struct_piece, building_level_info, levels, slabD, structure_dict_surfaces, tree, namespaces):

        graph_building_name = ""
        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")

        for b in building_level_info:
            graph_building_name = b
            break

        #print "data_sets_by_struct_piece levs"
        #for b in data_sets_by_struct_piece:
        #    print b, data_sets_by_struct_piece[b]

        for l in levels:
            l_before = l
            l = "http://www.sw.org/UBO#"+l.replace(" ","_")
            USO_New.add( (URIRef("http://www.sw.org/UBO#"+graph_building_name), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Level") ) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, URIRef(l) ) )
            print "Added Building Level for Structure: ", URIRef(graph_building_name), hasProperty, "Property" + str(property_counter), "Level", l
            property_counter += 1
            triple_counter += 1
            beam_or_column = "MemberNotAssignedType"

            for j in data_sets_by_struct_piece:
                #print "now", j, data_sets_by_struct_piece[j][0][0][1][0]
                this_type = data_sets_by_struct_piece[j][0][0][1][0]
                if "column" in this_type or "Column" in this_type:
                    beam_or_column = "Column"
                if "beam" in this_type or "Beam" in this_type or "Beam" in str(data_sets_by_struct_piece[j][0][0][0]): # This gets back into Semantic Name matching, but for now assuming that Shapes are Beams
                    beam_or_column = "Beam"
                if l_before == data_sets_by_struct_piece[j][1]:
                    USO_New.add( (URIRef(l), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                    back_edge = URIRef(str(self.USObase) + "Property" + str(property_counter))
                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Structural_Set_ID") ) )
                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(j) ) ) )
                    print "Added Triple S1: ", URIRef(l), hasProperty, "Property" + str(property_counter), "Structural_Set_ID", str(j)
                    property_counter += 1
                    triple_counter += 1

                    USO_New.add( (URIRef(l), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal(beam_or_column) ) )
                    USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(data_sets_by_struct_piece[j][0])) ) )
                    print "Added Triple S2: ", URIRef(l), hasProperty, "Property" + str(property_counter), "with Struct Type", beam_or_column, data_sets_by_struct_piece[j][0]
                    property_counter += 1
                    triple_counter += 1

                    # Slab Add for Beams
                    if beam_or_column == "Beam":
                        curr_beam = data_sets_by_struct_piece[j][0][0][2][0] # Current Beam id
                        for s in slabD:
                            if str(curr_beam) == str(slabD[s][0]):
                                # Then it had an associated slab
                                surface_with_slab = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelSpaceBoundary/ifc:RelatedBuildingElement/ifc:IfcSlab", namespaces=namespaces)
                                for slab in surface_with_slab:
                                    if slab.get("ref") == slabD[s][1]:
                                        my_slab_surf = slab.getparent().getparent()
                                        for dfg in structure_dict_surfaces:
                                            if my_slab_surf == structure_dict_surfaces[dfg][0]:
                                                graph_name_for_slab = dfg
                                                USO_New.add( (back_edge,  URIRef(str(self.USObase) + "belongsToSpaceBoundary"), URIRef(graph_name_for_slab) ) )
                                                triple_counter += 1
                                                print "Added Slab", back_edge,  URIRef(str(self.USObase) + "belongsToSpaceBoundary"), URIRef(graph_name_for_slab)

        return USO_New, property_counter, triple_counter

    def add_gbxml_struct_triples(self, USO_New, property_counter, triple_counter, data_sets_by_struct_piece, structure_dict_surfaces):

        graph_surfaces = dict()
        for j in structure_dict_surfaces:
            graph_surfaces[structure_dict_surfaces[j][0]] = j
        #for j in graph_surfaces:
        #    print j, graph_surfaces[j]

        # Add Triples
        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")

        for struct_element in data_sets_by_struct_piece:
            this_type = str(data_sets_by_struct_piece[struct_element][0][1])
            if "column" in this_type or "Column" in this_type:
                beam_or_column = "Column"
            if "beam" in this_type or "Beam" in this_type:
                beam_or_column = "Beam"
            for surf_in_set in data_sets_by_struct_piece[struct_element]:
                surface_in_question = [surf_in_set][0][0]
                current_graph_name = graph_surfaces[surface_in_question]

                USO_New.add( (URIRef(current_graph_name), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Structural_Set_ID") ) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(struct_element) ) ) )
                print "Added Triple A: ", URIRef(current_graph_name), hasProperty, "Property" + str(property_counter), "Structural_Set_ID", str(struct_element)
                property_counter += 1
                triple_counter += 1

                USO_New.add( (URIRef(current_graph_name), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal(beam_or_column) ) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(data_sets_by_struct_piece[struct_element])) ) )
                print "Added Triple B: ", URIRef(current_graph_name), hasProperty, "Property" + str(property_counter), "with Struct Type", beam_or_column, str(data_sets_by_struct_piece[struct_element])
                property_counter += 1
                triple_counter += 1


        return USO_New, property_counter, triple_counter

    def makegroups(self, struct_data_list, this_file_type):

        data_sets_by_struct_piece = dict()  # Dict of tuples of data grouped by column/beam surface sets
        id_dict = dict()
        coor_dict = dict()

        for data in struct_data_list:
            if data[2] == "id":
                id_dict[data[0]] = [data[1], data[2]]
            if data[2] == "coors":
                coor_dict[data[0]] = [data[1], data[2]]

        for data in struct_data_list:
            if data[2] == "name":
                # Add Grouping info based upon CadObjectID number at end of Name string
                if this_file_type == "gbxml":
                    col_beam_group = data[1][-7:-1]
                if this_file_type == "ifcxml":
                    col_beam_group = data[1][-6:]
                new_tuple = (data[0], data[1], data[2], col_beam_group)
                this_index = struct_data_list.index(data)
                struct_data_list[this_index] = new_tuple

                if col_beam_group not in data_sets_by_struct_piece:
                    # This entry looks like: [column or beam ID number from gbxml] = [  (  address, (type name, "some name"), (type id, "some id tag"), (type coors, "coors")  ),
                    #                                                                   (then there is another set if broken into surface parts)
                    #                                                                ]
                    data_sets_by_struct_piece[col_beam_group] = [[ data[0], (data[1], data[2]), (id_dict[data[0]][0], id_dict[data[0]][1]), (coor_dict[data[0]][0], coor_dict[data[0]][1]) ]]
                else:
                    curr_set = data_sets_by_struct_piece[col_beam_group]
                    curr_set.append([ data[0], (data[1], data[2]), (id_dict[data[0]][0], id_dict[data[0]][1]), (coor_dict[data[0]][0], coor_dict[data[0]][1]) ])
                    data_sets_by_struct_piece[col_beam_group] = curr_set

        #print "data_sets_by_struct_piece"
        #for b in data_sets_by_struct_piece:
        #    print b, data_sets_by_struct_piece[b]
        return struct_data_list, data_sets_by_struct_piece

    def handle_ids(self, o, struct_data_list, namespaces):

        print "getting:", o, struct_data_list

        struct_data_list_ids = list()

        if str(o)[:4] == "ref:":
            ref = str(o)[4:]
            count = 0
            for n in struct_data_list:
                count += 1
                this_id = n[0].get(ref)
                if this_id is not None:
                    struct_data_list_ids.append((n[0], this_id, "id"))
                    #print "appendedIDk: ", (n[0], this_id, "id")
                if len(struct_data_list_ids) == len(struct_data_list):
                    break
        for i in struct_data_list_ids:
            struct_data_list.append(i)

        return struct_data_list

    def handle_name(self, o, SurfaceCases, struct_data_list, namespaces):

        new_possibile_sets = list()
        if str(o)[:5] == "path:":
            path_to_name = str(o)[5:]
            if str(path_to_name)[1] == ":":  # This case needs to be added where there are several steps to find data
                print "here add lines to handle several parts to the path"
            elif str(path_to_name)[1] == "*":  # Check if it is a back-up, match, & continue path indicated with an *
                path_to_name = str(o)[7:]
                levels_back_up = int(str(o)[5])
                for os in SurfaceCases:
                    ref_to_match = os.get("ref")
                    if ref_to_match is not None:
                        new_add_on = ""
                        counter = levels_back_up
                        while counter > 0:
                            new_add_on += "../"
                            counter -= 1
                        new_add_on = new_add_on[0:-1]
                        new_possibilities = os.xpath(new_add_on+path_to_name, namespaces=namespaces)
                        #print "new_possibilities", new_possibilities
                        #print new_add_on+path_to_name
                        for i in new_possibilities:
                            direct_parent = i.getparent()
                            #print direct_parent
                            if direct_parent.get("id") == ref_to_match:
                                #print "ref_to_match", ref_to_match
                                new_possibile_sets.append((os, direct_parent))
                                name_options = str(i.text)
                                if name_options is not None:
                                    if "Column" in name_options or "Beam" in str(str(o).split(" ")[1]).split("}")[1]:
                                        struct_data_list.append((os, name_options, "name"))
                                        #print "appendedNameA: ", (os, name_options, "name")
            else:  # So it must be a direct path
                for o in SurfaceCases:
                    name_options = str(o.xpath("."+path_to_name, namespaces=namespaces)[0].text)
                    if name_options is not None:
                        if "Column" in name_options or "Beam" in str(str(o).split(" ")[1]).split("}")[1]:
                            struct_data_list.append((o, name_options, "name"))
                            #print "appendedNameB: ", (o, name_options, "name")

        return struct_data_list, new_possibile_sets

    def order_coors(self, o, coor_order_dict, other_list, this_file_type):
        index_value = int(str(o)[5])
        if this_file_type == "gbxml":
            if str(o)[5] != "/":
                coor_order_dict[index_value-1] = str(o)[7:]
        if this_file_type == "ifcxml":
            set_thus_far = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            if str(o)[6] == ":":
                if int(index_value) in set_thus_far:
                    coor_order_dict[index_value] = str(o)[7:]

        return coor_order_dict, other_list

    def handle_coors(self, struct_data_list_names, struct_data_list, namespaces, coor_order_dict, new_possibilities, this_file_type, StartCases, tree):
        # This is where there is a set of paths for a data piece handled
        if this_file_type == "gbxml": # Then it is a gbxml
            counter = 0
            len_struct_data_list_names = len(struct_data_list_names)
            for o in struct_data_list_names:
                counter += 1
                cart_point_sets = o[0].xpath("."+coor_order_dict[0], namespaces=namespaces)
                coor_data_set = list()
                for each in cart_point_sets:
                    coor_points = each.xpath("."+coor_order_dict[1], namespaces=namespaces)
                    coor_pts = list()
                    for coor in coor_points:
                        pt = str(coor.text)
                        coor_pts.append(pt)
                    coor_data_set.append(coor_pts)
                if (o[0], coor_data_set, "coors") not in struct_data_list:
                    struct_data_list.append((o[0], coor_data_set, "coors"))
                    #print "Added Coors Set gbxml: ", o[0], coor_data_set, "coors"
                    if counter == len_struct_data_list_names:
                        return struct_data_list
        else:  # Assume all three entry spots are full and is ifcxml
            # For the ordered sets of data in coor_order_list
            for start_structure_point in StartCases:              # Example: For each column in building
                if "Column" in str(start_structure_point):
                    my_set = list()
                    start_point = ""
                    general_start_address = start_structure_point.getparent()
                    start_ref = "not yet found"
                    new_ref = "not yet matched"
                    for i in coor_order_dict:                         # Get each set of paths
                        path_set = coor_order_dict[i].split(",")
                        data_type = path_set[0]
                        if data_type != "begin":
                            new_ref = start_ref
                        if data_type == "CadID":
                            cadids = start_structure_point.xpath("."+path_set[1], namespaces=namespaces)
                            my_set.append((data_type, cadids[0].text))
                            continue
                        new_data_set = list()
                        for d in range(1, len(path_set), 1):          # At the end of the path set, collect the data
                            if data_type == "begin" and d == 1:
                                new_refs = start_structure_point.xpath("."+path_set[d], namespaces=namespaces)
                                new_ref = new_refs[0].get("ref")
                            else:
                                check_new_ids = general_start_address.xpath("./"+path_set[d].split("/")[1], namespaces=namespaces)
                                for an_id_addr in check_new_ids:
                                    curr_id = an_id_addr.get("id")
                                    if curr_id == new_ref:
                                        adj_path = path_set[d].split("/")[1:]
                                        count = 1
                                        new_adj_path = ""
                                        for a in adj_path:
                                            if count == 1:
                                                count = 0
                                                continue
                                            else:
                                                new_adj_path = new_adj_path + a + "/"
                                        new_adj_path = "./"+new_adj_path[:-1]
                                        end_of_path = an_id_addr.xpath(new_adj_path, namespaces=namespaces)
                                        #print curr_id, new_ref
                                        #print d, len(path_set)-1
                                        if d == len(path_set)-1: # Get actual data if reach the end of the path_set list
                                            if data_type == "begin":
                                                start_ref = end_of_path[0].get("ref")
                                            else:
                                                new_data_set = list()
                                                #print "reaching", end_of_path
                                                for e in end_of_path:
                                                    new_data_set.append(str(e.text))
                                                    if data_type == "XandYDim":
                                                        # Also add the YDim
                                                        e_parent = e.getparent()
                                                        new_addon = e_parent.xpath("./ifc:YDim", namespaces=namespaces)
                                                        new_data_set.append(str(new_addon[0].text))
                                        else:                  # Otherwise get the new most relevant ref
                                            if end_of_path != []:
                                                new_ref = end_of_path[0].get("ref")
                                            else:
                                                # Column is defined by a set of Composite Curves, which we will not waste processing on for now,
                                                # so use the set of IfcCompositeCurveSegment addresses as new_data_set
                                                #IfcExtrudedAreaSolid             to    /ifc:SweptArea/ifc:IfcArbitraryClosedProfileDef
                                                #IfcArbitraryClosedProfileDef	 to    /ifc:OuterCurve/ifc:IfcCompositeCurve
                                                #IfcCompositeCurve                to    /ifc:Segments/ifc:IfcCompositeCurveSegment and get a set of addresses
                                                end_of_path = an_id_addr.xpath("./ifc:SweptArea/ifc:IfcArbitraryClosedProfileDef", namespaces=namespaces)
                                                #print end_of_path
                                                if end_of_path != []:
                                                    new_ref = end_of_path[0].get("ref")
                                                    new_markers = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcArbitraryClosedProfileDef", namespaces=namespaces)
                        #print "new_data_set-----------------", data_type, new_data_set
                        my_set.append((data_type, new_data_set))
                    struct_data_list.append((start_structure_point, my_set[1:], "coors"))

                else:
                    # Instead for each Beam
                    my_set = list()
                    for i in coor_order_dict:                         # Get each of 6 paths to datas
                        path_set = coor_order_dict[i].split(",")
                        data_type = path_set[0]
                        if len(path_set) == 2 and data_type != "XandYDim":
                            points = start_structure_point.xpath("."+path_set[1], namespaces=namespaces)
                            new_data_set = list()
                            for p in points:
                                new_data_set.append(p.text)
                            #print "shrt data type", new_data_set
                            my_set.append((data_type, new_data_set))
                        elif len(path_set) == 2 and data_type == "XandYDim":
                            new_data_set = list()
                            # Trying to catch and edge case here, these can be added to LD View later when there is time to extend them, and this edge case seems to not have X,Y,Z values
                            if len(start_structure_point.xpath("."+path_set[1]+"/ifc:XDim", namespaces=namespaces)) == 0:
                                new_data_set = ['None', 'None', 'None']
                                my_set.append((data_type, new_data_set))
                            else:
                                xdims = new_data_set.append(start_structure_point.xpath("."+path_set[1]+"/ifc:XDim", namespaces=namespaces)[0].text)
                                ydims = new_data_set.append(start_structure_point.xpath("."+path_set[1]+"/ifc:YDim", namespaces=namespaces)[0].text)
                                zdims = new_data_set.append(start_structure_point.xpath("."+path_set[1]+"/ifc:ZDim", namespaces=namespaces)[0].text)
                                #print "xyz data type", new_data_set
                                my_set.append((data_type, new_data_set))
                        else:
                            points = start_structure_point.xpath("."+path_set[1], namespaces=namespaces)
                            if len(points) == 0:
                                # Trying to catch and edge case here, these can be added to LD View later when there is time to extend them, and this edge case seems to not have X,Y,Z values
                                if path_set[0] == 'local_direction_ratios':
                                    path_set = ['local_direction_ratios', '/ifc:Representation/ifc:IfcProductDefinitionShape', '/ifc:IfcProductDefinitionShape/ifc:Representations/ifc:IfcShapeRepresentation', '/ifc:IfcShapeRepresentation/ifc:ContextOfItems/ifc:IfcGeometricRepresentationSubContext', '/ifc:IfcGeometricRepresentationSubContext/ifc:ParentContext/ifc:IfcGeometricRepresentationContext', '/ifc:IfcGeometricRepresentationContext/ifc:TrueNorth/ifc:IfcDirection', '/ifc:IfcDirection/ifc:DirectionRatios/exp:double-wrapper']
                                    data_type = path_set[0]
                                elif path_set[0] == 'reference_direction':
                                    path_set = ['reference_direction', '/ifc:ObjectPlacement/ifc:IfcLocalPlacement', '/ifc:IfcLocalPlacement/ifc:PlacementRelTo/ifc:IfcLocalPlacement', '/ifc:IfcLocalPlacement/ifc:PlacementRelTo/ifc:IfcLocalPlacement', '/ifc:IfcLocalPlacement/ifc:RelativePlacement/ifc:IfcAxis2Placement3D', '/ifc:IfcAxis2Placement3D/ifc:Location/ifc:IfcCartesianPoint', '/ifc:IfcCartesianPoint/ifc:Coordinates/ifc:IfcLengthMeasure']
                                    data_type = path_set[0]
                                elif path_set[0] == 'position':
                                    path_set = ['position', '/ifc:ObjectPlacement/ifc:IfcLocalPlacement', '/ifc:IfcLocalPlacement/ifc:PlacementRelTo/ifc:IfcLocalPlacement', '/ifc:IfcLocalPlacement/ifc:RelativePlacement/ifc:IfcAxis2Placement3D', '/ifc:IfcAxis2Placement3D/ifc:Location/ifc:IfcCartesianPoint', '/ifc:IfcCartesianPoint/ifc:Coordinates/ifc:IfcLengthMeasure']
                                    data_type = path_set[0]
                                else:
                                    path_set = ['profile_location', '/ifc:ObjectPlacement/ifc:IfcLocalPlacement', '/ifc:IfcLocalPlacement/ifc:RelativePlacement/ifc:IfcAxis2Placement3D', '/ifc:IfcAxis2Placement3D/ifc:Location/ifc:IfcCartesianPoint', '/ifc:IfcCartesianPoint/ifc:Coordinates/ifc:IfcLengthMeasure']
                                    data_type = path_set[0]

                                points = start_structure_point.xpath("."+path_set[1], namespaces=namespaces)
                                ref = points[0].get("ref")
                                counter_edgecase = 0
                                for i in path_set:
                                    #print "i", i, counter_edgecase
                                    if counter_edgecase == 0 or counter_edgecase == 1:
                                        counter_edgecase += 1
                                        continue
                                    srt = "/ifc:" + i.split("/ifc:")[1]
                                    refpoints = []
                                    new_ids = tree.xpath("/doc:iso_10303_28/ifc:uos"+srt, namespaces=namespaces)
                                    for new_id in new_ids:
                                        if new_id.get("id") == ref:
                                            rst = "." + i[len(srt):]
                                            #print "rst", rst
                                            refpoints = new_ids[0].xpath(rst, namespaces=namespaces)
                                            ref = refpoints[0].get("ref")
                                            #print ref
                                    counter_edgecase += 1
                                    if counter_edgecase == len(path_set):
                                        #print "am processing ", i, ref
                                        new_data_set = list()
                                        for t in refpoints:
                                            new_data_set.append(t.text)
                                            #print t.text
                                        my_set.append((data_type, new_data_set))

                            else:
                                ref = points[0].get("ref")
                                last = path_set[2].split("/ifc:")[1]
                                rest = "./ifc:" + path_set[2].split("/ifc:")[2]
                                new_ids = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:"+last, namespaces=namespaces)
                                for i in new_ids:
                                    if i.get("id") == ref:
                                        ds = i.xpath(rest, namespaces=namespaces)
                                        new_data_set = list()
                                        for each in ds:
                                            new_data_set.append(each.text)
                                        #print "ext data type", new_data_set
                                        my_set.append((data_type, new_data_set))
                    struct_data_list.append((start_structure_point, my_set, "coors"))

        print "final", struct_data_list
        return struct_data_list

    def querySetUp(self, graph, base):
        for subject,predicate,obj in graph:
           if not (subject,predicate,obj) in graph:
              raise Exception("Iterator / Container Protocols are Broken!!")
        return 0


























