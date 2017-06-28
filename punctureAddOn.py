#-------------------------------------------------------------------------------
# Name:        punctureAddOn.py
# Purpose:     Add Puncture Geometries and IDs to LD Graph
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     1/02/2017
# Copyright:   (c) Holly Tina Ferguson 2017
# Licence:     The University of Notre Dame


# 1) pre-process all possible windows and doors
# 2) match that to passed dictionary address entry to set the graph name and element type
# 3) for each element, search for geometries
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


class Add_Punctures():
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

    def add_pun_geometries(self, tree, namespaces, puncture_dict_surfaces, this_file_type, inputfile, USO_New, current_addOn_vocab, property_counter):

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
        #print "current_addOn_vocab", current_addOn_vocab
        curr_vocab_empty_graph = Graph()
        current_vocab_parsed = curr_vocab_empty_graph.parse(current_addOn_vocab, format="turtle") # Vocabulary Structure in TTL form parsed
        self.querySetUp(current_vocab_parsed, self.USObase) # Set-up Query Checks
        print "current_pun_vocab_parsed: "
        SurfaceOpenings1 = list()
        SurfaceOpenings2 = list()
        opening_data_list = list()

        for s,p,o in current_vocab_parsed.triples( (None, None, None) ):
            if str(s) == "http://www.gbxml.org/schema#Surface1" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface1":
                if str(p) == "start":
                    SurfaceOpenings1 = tree.xpath(str(o), namespaces=namespaces)
            if str(s) == "http://www.gbxml.org/schema#Surface2" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface2":
                if str(p) == "start":
                    SurfaceOpenings2 = tree.xpath(str(o), namespaces=namespaces)

        coor_order_list1 = ["x", "x", "x"]
        coor_order_list2 = ["x", "x", "x"]
        new_possibile_sets1 = list()
        new_possibile_sets2 = list()
        other_list1 = list()
        other_list2 = list()
        for s,p,o in current_vocab_parsed.triples( (None, None, None) ):
            if str(s) == "http://www.gbxml.org/schema#Surface1" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface1":
                if str(p) == "id":
                    opening_data_list = self.handle_ids(o, SurfaceOpenings1, opening_data_list, namespaces)
                if str(p) == "name":
                    opening_data_list, new_possibile_sets1 = self.handle_name(o, SurfaceOpenings1, opening_data_list, namespaces)
                if str(p) == "coors":
                    coor_order_list1, other_list1 = self.order_coors(o, coor_order_list1, other_list1)
                    #opening_data_list = self.handle_coors_nonset(SurfaceOpenings1, opening_data_list, namespaces, coor_order_list1, new_possibile_sets1, other_list)
            if str(s) == "http://www.gbxml.org/schema#Surface2" or str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Surface2":
                if str(p) == "id":
                    opening_data_list = self.handle_ids(o, SurfaceOpenings2, opening_data_list, namespaces)
                if str(p) == "name":
                    opening_data_list, new_possibile_sets2 = self.handle_name(o, SurfaceOpenings2, opening_data_list, namespaces)
                if str(p) == "coors":
                    coor_order_list2, other_list2 = self.order_coors(o, coor_order_list2, other_list2)
                    #opening_data_list = self.handle_coors_nonset(SurfaceOpenings2, opening_data_list, namespaces, coor_order_list2, new_possibile_sets2, other_list)

        # For coordinate information we do this function call after so we have the correct path order
        opening_data_list = self.handle_coors_nonset(SurfaceOpenings1, opening_data_list, namespaces, coor_order_list1, new_possibile_sets1, other_list1)
        opening_data_list = self.handle_coors(SurfaceOpenings1, opening_data_list, namespaces, coor_order_list1, new_possibile_sets1)
        if this_file_type == "ifcxml":
            opening_data_list = self.handle_coors(SurfaceOpenings2, opening_data_list, namespaces, coor_order_list2, new_possibile_sets2)
            opening_data_list = self.handle_coors_nonset(SurfaceOpenings2, opening_data_list, namespaces, coor_order_list2, new_possibile_sets2, other_list2)

        triple_counter = 0
        USO_New, property_counter, triple_counter = self.add_pun_triples(USO_New, property_counter, triple_counter, opening_data_list, puncture_dict_surfaces, this_file_type)

        return USO_New, property_counter

    def add_pun_triples(self, USO_New, property_counter, triple_counter, opening_data_list, puncture_dict_surfaces, this_file_type):

        address_groupings = dict()
        for v in opening_data_list:
            if v[0] in address_groupings:
                temp = address_groupings[v[0]]
                temp.append(((v[1],v[2])))
                address_groupings[v[0]] = temp
            else:
                address_groupings[v[0]] = [(v[1],v[2])]
        # Group Coor Information if IFC
        for v in address_groupings:
            set_coors = list()
            for item in address_groupings[v]:
                if item[1] == "coors":
                    set_coors.append(item[0])
            temp = address_groupings[v]
            temp.append(((set_coors, "puncture_coors")))
            address_groupings[v] = temp

        # Add Triples
        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")

        for v in address_groupings:  # Effectively assigning one of these openings to a respective surface
            idtag = ""
            name = ""
            coors = ""
            # Get the correct Data
            for item in address_groupings[v]:
                if item[1] == "puncture_coors":
                    coors = item[0]
                if item[1] == "id":
                    idtag = item[0]
                if item[1] == "name":
                    name = item[0]
            #print "row:", idtag, name, coors

            # Get correct Parent to verify and match
            mynode = ""
            if this_file_type == "ifcxml":
                mynode = v.getparent()
                mynode = mynode.getparent()
            if this_file_type == "gbxml":
                mynode = v.getparent()

            # Now find the Graph surface these belong to in puncture_dict_surfaces
            semantic_graph_name = ""
            for i in puncture_dict_surfaces:
                if puncture_dict_surfaces[i][0] == mynode:
                    semantic_graph_name = i

            USO_New.add( (URIRef(semantic_graph_name), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Name") ) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(name) ) ) )
            print "Added Triple A: ", URIRef(semantic_graph_name), hasProperty, "Property" + str(property_counter), "with Type and Value: Name ", str(name)
            property_counter += 1
            triple_counter += 1

            USO_New.add( (URIRef(semantic_graph_name), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Coordinates") ) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(coors)) ) )
            print "Added Triple B: ", URIRef(semantic_graph_name), hasProperty, "Property" + str(property_counter), "with Type and Value: Elevation ", str(coors)
            property_counter += 1
            triple_counter += 1

            USO_New.add( (URIRef(semantic_graph_name), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("Relative_ID") ) )
            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(idtag)) ) )
            print "Added Triple C: ", URIRef(semantic_graph_name), hasProperty, "Property" + str(property_counter), "with Type and Value: Relative_ID", str(idtag)
            property_counter += 1
            triple_counter += 1

        return USO_New, property_counter, triple_counter

    def handle_ids(self, o, SurfaceOpenings, opening_data_list, namespaces):

        if str(o)[:4] == "ref:":
            ref = str(o)[4:]
            for o in SurfaceOpenings:
                this_id = o.get(ref)
                if this_id is not None:
                    opening_data_list.append((o, this_id, "id"))
                    #print "appended: ", (o, this_id, "id")

        return opening_data_list

    def handle_name(self, o, SurfaceOpenings, opening_data_list, namespaces):

        new_possibile_sets = list()
        if str(o)[:5] == "path:":
            path_to_name = str(o)[5:]
            if str(path_to_name)[1] == ":":  # This case needs to be added where there are several steps to find data
                print "here add lines to handle several parts to the path"
            elif str(path_to_name)[1] == "*":  # Check if it is a back-up, match, & continue path indicated with an *
                path_to_name = str(o)[7:]
                levels_back_up = int(str(o)[5])
                for os in SurfaceOpenings:
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
                                    opening_data_list.append((os, name_options, "name"))
                                    #print "appended: ", (os, name_options, "name")
            else:  # So it must be a direct path
                for o in SurfaceOpenings:
                    name_options = str(o.xpath("."+path_to_name, namespaces=namespaces)[0].text)
                    if name_options is not None:
                        opening_data_list.append((o, name_options, "name"))
                        #print "appended: ", (o, name_options, "name")

        return opening_data_list, new_possibile_sets

    def order_coors(self, o, coor_order_list, other_list):
        if str(o)[5] != "/":
            index_value = int(str(o)[5])
            if index_value == 1:
                coor_order_list[index_value-1] = str(o)[7:]
            if index_value == 2:
                coor_order_list[index_value-1] = str(o)[7:]
            if index_value == 3:
                coor_order_list[index_value-1] = str(o)[7:]
        else:
            if o not in other_list:
                other_list.append(o)

        return coor_order_list, other_list

    def handle_coors_nonset(self, SurfaceOpenings, opening_data_list, namespaces, coor_order_list, new_possibilities, other_list):
        # For non-ordered sets of data
        for n in new_possibilities:  # These are pairs of (surfaceAddr, dataLocationAddr)
            coor_data = list()
            for t in other_list:
                t = t[5:]
                coor_d = n[1].xpath("."+t, namespaces=namespaces)
                co = ""
                for c in coor_d:
                    co = str(c.text)
                    coor_data.append(co)
                #coor_data_set.append(coor_data)
                #print "coor_data", coor_data
            if coor_data is not None and (n[0], coor_data, "coors") not in opening_data_list:
                opening_data_list.append((n[0], coor_data, "coors"))
                #print "here I appended, ", (n[0], coor_data, "coors")
                #print "n[0]", n[0].get("ref")

        return opening_data_list

    def handle_coors(self, SurfaceOpenings, opening_data_list, namespaces, coor_order_list, new_possibilities):

        if coor_order_list[2] == "x": # Then gbxml
            for o in SurfaceOpenings:
                cart_point_sets = o.xpath("."+coor_order_list[0], namespaces=namespaces)
                coor_data_set = list()
                for each in cart_point_sets:
                    coor_points = each.xpath("."+coor_order_list[1], namespaces=namespaces)
                    coor_pts = list()
                    for coor in coor_points:
                        pt = str(coor.text)
                        coor_pts.append(pt)
                    coor_data_set.append(coor_pts)
                opening_data_list.append((o, coor_data_set, "coors"))
        else:  # Assume all three entry spots are full and is ifcxml
            # For the ordered sets of data in coor_order_list
            for n in new_possibilities:  # Using n[1] since that is the temp start point...for each opening
                #for co in coor_order_list:                                               # match for complete path set
                if coor_order_list[0][1] == "*":
                    counter = coor_order_list[0][0]
                    adj_path = coor_order_list[0][2:]
                    up = ""
                    while counter > 0:
                        up += "../"
                        counter -= 1
                    up = up[0:-1]
                    new_path_options = n[1].xpath(up+adj_path, namespaces=namespaces)
                else:
                    new_path_options = n[1].xpath("."+coor_order_list[0], namespaces=namespaces)
                coor_set_long = list()
                for new_op in new_path_options:
                    test_match = new_op.get("ref")
                    if coor_order_list[1][1] == "*":
                        counter = int(coor_order_list[1][0])
                        adj_path = coor_order_list[1][2:]
                        up = ""
                        while counter > 0:
                            up += "../"
                            counter -= 1
                        up = up[0:-1]
                        second_path_options = n[1].xpath(up+adj_path, namespaces=namespaces)
                    else:
                        second_path_options = n[1].xpath("."+coor_order_list[1], namespaces=namespaces)

                    for sec in second_path_options:
                        direct_parent1 = sec.getparent()
                        direct_parent2 = direct_parent1.getparent()
                        other_match = direct_parent2.get("id")
                        if test_match == other_match:
                            if coor_order_list[2][1] == "*":
                                counter = int(coor_order_list[2][0])
                                adj_path = coor_order_list[2][2:]
                                up = ""
                                while counter > 0:
                                    up += "../"
                                    counter -= 1
                                up = up[0:-1]
                                third_path_options = n[1].xpath(up+adj_path, namespaces=namespaces)
                            else:
                                third_path_options = n[1].xpath("."+coor_order_list[2], namespaces=namespaces)

                            new_match = sec.get("ref")
                            coor_set_long = list()
                            for third in third_path_options:
                                d1 = third.getparent()
                                d2 = d1.getparent()
                                d3 = d2.getparent()
                                d4 = d3.getparent()
                                last_match = d4.get("id")
                                if new_match == last_match:
                                    coor_set_long.append(str(third.text))
                            #print "got to here", coor_set_long, n[0]
                opening_data_list.append((n[0], coor_set_long, "coors"))
                #print "and there I appended, ", (n[0], coor_set_long, "coors")

        return opening_data_list

    def querySetUp(self, graph, base):
        for subject,predicate,obj in graph:
           if not (subject,predicate,obj) in graph:
              raise Exception("Iterator / Container Protocols are Broken!!")
        return 0



