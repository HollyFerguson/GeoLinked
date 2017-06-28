#-------------------------------------------------------------------------------
# Name:        IFC_SpeedUp.py
# Purpose:     Less general solution for adding IFC triples to run faster
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     02/01/2017
# Copyright:   (c) Holly Tina Ferguson 2017
# License:     The University of Notre Dame
#-------------------------------------------------------------------------------

# #!/usr/bin/python
import sys
import getopt
import os
from os import path
from lxml import etree
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF


class Faster_IFC():
    # Input parameters
    inputfile = ""
    material_flag = ""
    level_flag = ""
    structure_flag = ""
    puncture_flag = ""
    test_query_sequence_flag = ""
    USObase = "http://www.sw.org/UBO#"  # Change back to full: "http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"


    def add_spaces_surfaces_and_materials(self, USO_New, current_subject, this_file_type, tree, namespaces, Add_On_Dict, property_counter):
        """
        Main run function
        """

        print "New method, ", current_subject
        curr_vocab_empty_graph = Graph()
        current_vocab_parsed = curr_vocab_empty_graph.parse('SmartVocabs/ifcSpeedUp.ttl', format="turtle") # Vocabulary Structure in TTL form parsed

        if str(current_subject) == "http://www.myuso.exp#Space":
            USO_New, property_counter, Add_On_Dict = self.addSpaces(USO_New, tree, namespaces, Add_On_Dict, property_counter, current_vocab_parsed)

        if str(current_subject) == "http://www.myuso.exp#SpaceBoundary":
            USO_New, property_counter, Add_On_Dict = self.addSurfaces(USO_New, tree, namespaces, Add_On_Dict, property_counter, current_vocab_parsed)

        if str(current_subject) == "http://www.myuso.exp#SpaceBoundaryElement":
            USO_New, property_counter, Add_On_Dict = self.addMaterials(USO_New, tree, namespaces, Add_On_Dict, property_counter, current_vocab_parsed)

        return USO_New, property_counter, Add_On_Dict


    def addSpaces(self, USO_New, tree, namespaces, Add_On_Dict, property_counter, current_vocab_parsed):

        my_root = "http://www.sw.org/UBO#"
        collections_to_spaces = dict()
        Add_On_Dict_newEntries = dict()
        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")

        for a in Add_On_Dict:
            # http://www.sw.org/UBO#SpaceCollection1 : [<Element {http://www.iai-tech.org/ifcXML/IFC2x2/FINAL}IfcBuilding at 0x8397e58>, rdflib.term.URIRef(u'http://www.sw.org/UBO#SpaceCollection')]
            if Add_On_Dict[a][1] == URIRef('http://www.sw.org/UBO#SpaceCollection'):
                collections_to_spaces[a] = Add_On_Dict[a][0]

        space_match = dict()
        space_poss = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelAggregates/ifc:RelatedObjects/ifc:IfcSpace", namespaces=namespaces)
        for sp in space_poss:
            sp_ref = sp.get("ref")
            level_poss = sp.xpath("../../ifc:RelatingObject/ifc:IfcBuildingStorey", namespaces=namespaces)
            space_match[sp_ref] = level_poss[0].get("ref")
        lev_poss = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelAggregates/ifc:RelatedObjects/ifc:IfcBuildingStorey", namespaces=namespaces)
        for lv in lev_poss:
            lv_ref = lv.get("ref")
            bldg_poss = lv.xpath("../../ifc:RelatingObject/ifc:IfcBuilding", namespaces=namespaces)
            building_ref = bldg_poss[0].get("ref")
            for space_entry in space_match:
                if space_match[space_entry] == lv_ref:
                    space_match[space_entry] = building_ref

        level_counter = 1
        for s,p,o in current_vocab_parsed.triples( (None, None, None) ):
            if str(s) == "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm#Spaces":
                if str(p) == "spaces":
                    spaces = tree.xpath(str(o), namespaces=namespaces)
                    # Now match each Space with the collections_to_spaces entries (this will be each building in the current graph)
                    for s in spaces:
                        sid = s.get("id")
                        buildID = space_match[sid]
                        for a in Add_On_Dict:
                            dict_bldg = Add_On_Dict[a][0].get("id")
                            if buildID == dict_bldg:
                                #print "YES", a, " has space ", s

                                Add_On_Dict_newEntries[URIRef(my_root + "Space" + str(level_counter))] = [s, URIRef(my_root + "Space")]

                                # Add actual triples for general spaces and types : STEP 1 of 2
                                #some building ns1:hasSpaceMember space1    where ns1 is URIRef(str(self.USObase) + "hasValue")
                                #space1 is a type of space
                                curr_space = URIRef( str(self.USObase) + "Space" + str(level_counter) )
                                USO_New.add( (URIRef(a), URIRef( str(self.USObase) + str("hasSpaceMember") ), curr_space) )
                                USO_New.add( (curr_space, RDF.type, URIRef(str(self.USObase + "Space") )) )
                                level_counter += 1

                                # Get and add coor info for spaces and types : STEP 2 of 2
                                center_point = ""
                                x_center_offset = ""
                                y_center_offset = ""
                                depth = ""
                                poly_line_outline = ""
                                datas1 = s.xpath("./ifc:Representation/ifc:IfcProductDefinitionShape", namespaces=namespaces)
                                ref_of_datas1 = datas1[0].get("ref")
                                datas2 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcProductDefinitionShape", namespaces=namespaces)
                                next_start_point = ""
                                for d in datas2:
                                    if d.get("id") == ref_of_datas1:
                                        next_start_point = d
                                datas3 = next_start_point.xpath("./ifc:Representations/ifc:IfcShapeRepresentation", namespaces=namespaces)
                                ref_of_datas3 = datas3[0].get("ref")
                                datas4 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcShapeRepresentation", namespaces=namespaces)
                                for d in datas4:
                                    if d.get("id") == ref_of_datas3:
                                        next_start_point = d
                                datas5 = next_start_point.xpath("./ifc:Items/ifc:IfcExtrudedAreaSolid", namespaces=namespaces)

                                if datas5 != []:
                                    # This will pull basic rectangular data, additional data point need adding in the future
                                    ref_of_datas5 = datas5[0].get("ref")
                                    datas6 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcExtrudedAreaSolid", namespaces=namespaces)
                                    for d in datas6:
                                        if d.get("id") == ref_of_datas5:
                                            next_start_point = d  # IfcExtrudedAreaSolid then to four different places
                                    depth = next_start_point.xpath("./ifc:Depth", namespaces=namespaces)
                                    depth = depth[0].text
                                    datas7 = next_start_point.xpath("./ifc:SweptArea/ifc:IfcRectangleProfileDef", namespaces=namespaces)
                                    print "check", ref_of_datas5, datas7
                                    if datas7 != []:
                                        ref_of_datas7 = datas7[0].get("ref")
                                        datas8 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRectangleProfileDef", namespaces=namespaces)
                                        for d in datas8:
                                            if d.get("id") == ref_of_datas7:
                                                x_center_offset = d.xpath("./ifc:XDim", namespaces=namespaces)
                                                x_center_offset = x_center_offset[0].text
                                                y_center_offset = d.xpath("./ifc:YDim", namespaces=namespaces)
                                                y_center_offset = y_center_offset[0].text
                                    else:
                                        datas7 = next_start_point.xpath("./ifc:SweptArea/ifc:IfcArbitraryClosedProfileDef", namespaces=namespaces)
                                        ref_of_datas7 = datas7[0].get("ref")
                                        datas8 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcArbitraryClosedProfileDef", namespaces=namespaces)
                                        newstart = ""
                                        for d in datas8:
                                            if d.get("id") == ref_of_datas7:
                                                newstart = d
                                        datasgg = newstart.xpath("./ifc:OuterCurve/ifc:IfcPolyline", namespaces=namespaces)
                                        if datasgg == []:
                                            # Then these are sets of curves, etc. so ignoring for now until need these specifically
                                            poly_line_outline = "needs_curve_segments_added"
                                        else:
                                            ref_of_datasgg = datasgg[0].get("ref")
                                            datashh = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcPolyline", namespaces=namespaces)
                                            for d in datashh:
                                                if d.get("id") == ref_of_datasgg:
                                                    newstart = d
                                            datastt = newstart.xpath("./ifc:Points/ifc:IfcCartesianPoint", namespaces=namespaces)
                                            coor_points_poly = list()
                                            for t in datastt:
                                                ref_of_datastt = t.get("ref")
                                                datasyy = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcCartesianPoint", namespaces=namespaces)
                                                for d in datasyy:
                                                    if d.get("id") == ref_of_datastt:
                                                        coorsets = d.xpath("./ifc:Coordinates/ifc:IfcLengthMeasure", namespaces=namespaces)
                                                        apoint = list()
                                                        for c in coorsets:
                                                            apoint.append(c.text)
                                                        coor_points_poly.append(apoint)

                                            poly_line_outline = coor_points_poly
                                            #print len(poly_line_outline), poly_line_outline

                                    datas9 = next_start_point.xpath("./ifc:Position/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                                    ref_of_datas9 = datas9[0].get("ref")
                                    datas10 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                                    for d in datas10:
                                        if d.get("id") == ref_of_datas9:
                                            next_start_point = d
                                    datas11 = next_start_point.xpath("./ifc:Location/ifc:IfcCartesianPoint", namespaces=namespaces)
                                    ref_of_datas11 = datas11[0].get("ref")
                                    datas12 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcCartesianPoint", namespaces=namespaces)
                                    for d in datas12:
                                        if d.get("id") == ref_of_datas11:
                                            next_start_point = d
                                    datas13 = next_start_point.xpath("./ifc:Coordinates/ifc:IfcLengthMeasure", namespaces=namespaces) # From here, collect the set of coor points
                                    coor_set = list()
                                    for coor in datas13:
                                        coor_set.append(coor.text)
                                    center_point = coor_set

                                if poly_line_outline == "":
                                    valueNow = [ ("center_point", center_point), ("depth", depth), ("x_center_offset", x_center_offset), ("y_center_offset", y_center_offset) ]
                                else:
                                    valueNow = [ ("center_point", center_point), ("depth", depth), ("poly_line_outline", poly_line_outline) ]
                                USO_New.add( (URIRef(curr_space), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("3DSpaceCoordinates") ) )
                                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(valueNow) ) ) )
                                #print "Added: ", valueNow
                                property_counter += 1

        #print "Add_On_Dict"
        for n in Add_On_Dict_newEntries:
            Add_On_Dict[n] = Add_On_Dict_newEntries[n]
            # Now when I process the Surfaces, the Spaces will be in here to match
            #print n, Add_On_Dict[n]

        return USO_New, property_counter, Add_On_Dict

    def addSurfaces(self, USO_New, tree, namespaces, Add_On_Dict, property_counter, current_vocab_parsed):

        my_root = "http://www.sw.org/UBO#"
        spaces_to_surfaces = dict()
        Add_On_Dict_newEntries = dict()
        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")
        space_match = dict()

        for a in Add_On_Dict:
            # http://www.sw.org/UBO#SpaceCollection1 : [<Element {http://www.iai-tech.org/ifcXML/IFC2x2/FINAL}IfcBuilding at 0x8397e58>, rdflib.term.URIRef(u'http://www.sw.org/UBO#SpaceCollection')]
            if Add_On_Dict[a][1] == URIRef('http://www.sw.org/UBO#Space'):
                spaces_to_surfaces[a] = Add_On_Dict[a][0]
                space_match[a] = Add_On_Dict[a][0].get("id")

        space_to_list = dict()
        surf_poss = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelSpaceBoundary", namespaces=namespaces)
        for su in surf_poss:
            spaces_under_this_surface = su.xpath("./ifc:RelatingSpace/ifc:IfcSpace", namespaces=namespaces)
            # We have only seen one space assigned to each surface in this schema, so:
            matching_space = spaces_under_this_surface[0].get("ref")

            for i in space_match:
                if space_match[i] == matching_space:
                    #this_surface_id = su.get("id")
                    if matching_space in space_to_list:
                        existing = space_to_list[matching_space]
                        e_list = [su]
                        for item in existing:
                            e_list.append(item)
                        space_to_list[matching_space] = e_list
                    else:
                        space_to_list[matching_space] = [su]

        #print "space_match"
        for n in space_match:
            set_of_surfaces = space_to_list[space_match[n]]
            space_match[n] = set_of_surfaces
            #print n, space_match[n]

        level_counter = 1
        for space in space_match:
            for surface in space_match[space]:
                #print "YES", space, " has surface ", surface

                Add_On_Dict_newEntries[URIRef(my_root + "SpaceBoundary" + str(level_counter))] = [surface, URIRef(my_root + "SpaceBoundary")]


                # Add actual triples for general spaces and types : STEP 1 of 2
                #some building ns1:hasSpaceMember space1    where ns1 is URIRef(str(self.USObase) + "hasValue")
                #space1 is a type of space
                curr_surface = URIRef( str(self.USObase) + "SpaceBoundary" + str(level_counter) )
                USO_New.add( (URIRef(space), URIRef( str(self.USObase) + str("hasSpaceBoundaryMember") ), curr_surface) )
                USO_New.add( (curr_surface, RDF.type, URIRef(str(self.USObase + "SpaceBoundary") )) )
                level_counter += 1

                # Get and add coor info for spaces and types : STEP 2 of 2
                plane_coordinates = ""
                x_axis_relative = ""
                z_axis_relative = ""
                relative_origin = ""
                datas1 = surface.xpath("./ifc:ConnectionGeometry/ifc:IfcConnectionSurfaceGeometry", namespaces=namespaces)
                ref_of_datas1 = datas1[0].get("ref")
                datas2 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcConnectionSurfaceGeometry", namespaces=namespaces)
                next_start_point = ""
                for d in datas2:
                    if d.get("id") == ref_of_datas1:
                        next_start_point = d
                datas3 = next_start_point.xpath("./ifc:SurfaceOnRelatingElement/ifc:IfcCurveBoundedPlane", namespaces=namespaces)
                ref_of_datas3 = datas3[0].get("ref")
                datas4 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcCurveBoundedPlane", namespaces=namespaces)
                gen_next_start_point = ""
                for d in datas4:
                    if d.get("id") == ref_of_datas3:
                        gen_next_start_point = d
                #-------------------------------------------------------------------------------------------------------
                datas20 = gen_next_start_point.xpath("./ifc:BasisSurface/ifc:IfcPlane", namespaces=namespaces)
                ref_of_datas20 = datas20[0].get("ref")
                datas21 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcPlane", namespaces=namespaces)
                next_start_point = ""
                for d in datas21:
                    if d.get("id") == ref_of_datas20:
                        next_start_point = d
                datas22 = next_start_point.xpath("./ifc:Position/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                ref_of_datas22 = datas22[0].get("ref")
                datas23 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                next_start_point = ""
                for d in datas23:
                    if d.get("id") == ref_of_datas22:
                        next_start_point = d
                datas24 = next_start_point.xpath("./ifc:Location/ifc:IfcCartesianPoint", namespaces=namespaces)
                ref_of_datas24 = datas24[0].get("ref")
                datas25 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcCartesianPoint", namespaces=namespaces)
                next_start_point = ""
                for d in datas25:
                    if d.get("id") == ref_of_datas24:
                        next_start_point = d
                datas26 = next_start_point.xpath("./ifc:Coordinates/ifc:IfcLengthMeasure", namespaces=namespaces)
                relative_origin_list = list()
                for d in datas26:
                    relative_origin_list.append(d.text)
                relative_origin = relative_origin_list
                #-------------------------------------------------------------------------------------------------------
                datas5 = gen_next_start_point.xpath("./ifc:OuterBoundary/ifc:IfcPolyline", namespaces=namespaces)
                ref_of_datas5 = datas5[0].get("ref")
                datas6 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcPolyline", namespaces=namespaces)
                next_start_point = ""
                for d in datas6:
                    if d.get("id") == ref_of_datas5:
                        next_start_point = d
                datas7 = next_start_point.xpath("./ifc:Points/ifc:IfcCartesianPoint", namespaces=namespaces)
                point_set = list()
                for pnt in datas7:
                    ref_of_datas7 = pnt.get("ref")
                    datas8 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcCartesianPoint", namespaces=namespaces)
                    next_start_point = ""
                    for d in datas8:
                        if d.get("id") == ref_of_datas7:
                            next_start_point = d
                    plane_coors = list()
                    datas9 = next_start_point.xpath("./ifc:Coordinates/ifc:IfcLengthMeasure", namespaces=namespaces)
                    for d in datas9:
                        plane_coors.append(d.text)
                    point_set.append(plane_coors)
                plane_coordinates = point_set
                #print "plane_coordinates", plane_coordinates
                #-------------------------------------------------------------------------------------------------------
                datas10 = gen_next_start_point.xpath("./ifc:BasisSurface/ifc:IfcPlane", namespaces=namespaces)
                ref_of_datas10 = datas10[0].get("ref")
                datas11 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcPlane", namespaces=namespaces)
                next_start_point = ""
                for d in datas11:
                    if d.get("id") == ref_of_datas10:
                        next_start_point = d
                datas12 = next_start_point.xpath("./ifc:Position/ifc:IfcAxis2Placement3D", namespaces=namespaces)

                ref_of_datas12 = datas12[0].get("ref")
                datas13 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                xz_next_start_point = ""
                for d in datas13:
                    if d.get("id") == ref_of_datas12:
                        xz_next_start_point = d
                #-------------------------------------------------------------------------------------------------------
                datas14 = xz_next_start_point.xpath("./ifc:RefDirection/ifc:IfcDirection", namespaces=namespaces)
                ref_of_datas14 = datas14[0].get("ref")
                datas15 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcDirection", namespaces=namespaces)
                next_start_point = ""
                for d in datas15:
                    if d.get("id") == ref_of_datas14:
                        next_start_point = d
                datas16 = next_start_point.xpath("./ifc:DirectionRatios/exp:double-wrapper", namespaces=namespaces)
                x_axis_relative_list = list()
                for d in datas16:
                    x_axis_relative_list.append(d.text)
                x_axis_relative = x_axis_relative_list
                #-------------------------------------------------------------------------------------------------------
                datas17 = xz_next_start_point.xpath("./ifc:Axis/ifc:IfcDirection", namespaces=namespaces)
                ref_of_datas17 = datas17[0].get("ref")
                datas18 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcDirection", namespaces=namespaces)
                next_start_point = ""
                for d in datas18:
                    if d.get("id") == ref_of_datas17:
                        next_start_point = d
                datas19 = next_start_point.xpath("./ifc:DirectionRatios/exp:double-wrapper", namespaces=namespaces)
                z_axis_relative_list = list()
                for d in datas19:
                    z_axis_relative_list.append(d.text)
                z_axis_relative = z_axis_relative_list

                valueNow = [ ("plane_coordinates", plane_coordinates), ("x_axis_relative", x_axis_relative), ("z_axis_relative", z_axis_relative), ("y_center_offset", relative_origin) ]
                USO_New.add( (URIRef(curr_surface), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("2DSpaceBoundaryMeasurements") ) )
                USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(valueNow) ) ) )
                print "Added: ", valueNow
                property_counter += 1




        #print "Add_On_Dict"
        for n in Add_On_Dict_newEntries:
            Add_On_Dict[n] = Add_On_Dict_newEntries[n]
            # Now when I process the Surfaces, the Spaces will be in here to match
            #print n, Add_On_Dict[n]

        return USO_New, property_counter, Add_On_Dict

    def addMaterials(self, USO_New, tree, namespaces, Add_On_Dict, property_counter, current_vocab_parsed):

        my_root = "http://www.sw.org/UBO#"
        Add_On_Dict_newEntries = dict()
        hasProperty = URIRef(str(self.USObase) + "hasProperty")
        hasType = URIRef(str(self.USObase) + "hasType")
        hasValue = URIRef(str(self.USObase) + "hasValue")

        surf_to_layers = dict()
        surface_match = dict()
        for a in Add_On_Dict:
            # http://www.sw.org/UBO#SpaceCollection1 : [<Element {http://www.iai-tech.org/ifcXML/IFC2x2/FINAL}IfcBuilding at 0x8397e58>, rdflib.term.URIRef(u'http://www.sw.org/UBO#SpaceCollection')]
            if Add_On_Dict[a][1] == URIRef('http://www.sw.org/UBO#SpaceBoundary'):
                surf_to_layers[a] = Add_On_Dict[a][0]
                surface_match[a] = Add_On_Dict[a][0].get("id")  # So key:value on graph_surface_name:surface_id

        thickness = ""
        direction_sense = ""
        reference_line_offset = ""
        layer_direction = ""
        axis_2_placement_relPlace = ""
        axis_2_placement_relTo = ""

        surface_to_list_of_layers = dict()
        level_counter = 1
        extra_set = list()
        for surf_addr in surf_to_layers:
            # Changing surf_to_layers to have a value of list of materials layers # Skipping IfcWindow and IfcDoor
            print "surf_addr", surf_to_layers[surf_addr], surf_to_layers[surf_addr].get("id")
            ss = surf_to_layers[surf_addr].xpath("./ifc:RelatedBuildingElement", namespaces=namespaces)
            #print "ss", ss, len(surf_to_layers), level_counter
            if ss == [] :
                extra_set.append( (surf_to_layers[surf_addr].get("id"), surf_to_layers[surf_addr]) )
                continue
            kids = ss[0].getchildren()
            child = kids[0].tag
            childname = str(child.split("}")[1])
            if str(child).split("}")[1] != "IfcDoor" and str(child).split("}")[1] != "IfcWindow":
                ref_of_surface_types = kids[0].get("ref")
                wall_matches = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelAssociatesMaterial/ifc:RelatedObjects/ifc:"+str(child.split("}")[1]), namespaces=namespaces)
                if len(wall_matches) != 0:
                    new_usage_set_ref = ""
                    new_usage_set = []
                    new_usage_set2 = []
                    for w in wall_matches:
                        if w.get("ref") == ref_of_surface_types:
                            wp = w.getparent().getparent()
                            RelAssocID = wp.get("id")
                            new_usage_set = wp.xpath("./ifc:RelatingMaterial/ifc:IfcMaterialLayerSetUsage", namespaces=namespaces)
                            new_usage_set2 = wp.xpath("./ifc:RelatingMaterial/ifc:IfcMaterialLayerSet", namespaces=namespaces)
                            if new_usage_set != []:
                                new_usage_set_ref = new_usage_set[0].get("ref")
                                if new_usage_set_ref == None:
                                    new_usage_set_ref = new_usage_set[0].get("id")
                    if new_usage_set != []:
                        new_start_node = ""
                        datas1 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcMaterialLayerSetUsage", namespaces=namespaces)
                        print "datas1", new_usage_set_ref, datas1
                        for d in datas1:
                            if d.get("id") == new_usage_set_ref:
                                new_start_node = d
                        if not new_start_node:
                            for d in new_usage_set:
                                if d.get("id") == new_usage_set_ref:
                                    new_start_node = d
                        print "new_start_node", new_start_node


                        #check that the graph makes sense now!!!


                        datas2 = new_start_node.xpath("./ifc:ForLayerSet/ifc:IfcMaterialLayerSet", namespaces=namespaces)
                        direction_sense = new_start_node.xpath("./ifc:DirectionSense", namespaces=namespaces)[0].text
                        reference_line_offset = new_start_node.xpath("./ifc:OffsetFromReferenceLine", namespaces=namespaces)[0].text
                        layer_direction = new_start_node.xpath("./ifc:LayerSetDirection", namespaces=namespaces)[0].text
                        ref1 = datas2[0].get("ref")
                    else:
                        ref1 = new_usage_set2[0].get("ref")
                        match_backwards = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcMaterialLayerSetUsage/ifc:ForLayerSet/ifc:IfcMaterialLayerSet", namespaces=namespaces)
                        for m in match_backwards:
                            if m.get("ref") == ref1:
                                start_now = m.getparent().getparent()
                                direction_sense = start_now.xpath("./ifc:DirectionSense", namespaces=namespaces)[0].text
                                reference_line_offset = start_now.xpath("./ifc:OffsetFromReferenceLine", namespaces=namespaces)[0].text
                                layer_direction = start_now.xpath("./ifc:LayerSetDirection", namespaces=namespaces)[0].text

                    #-------------------------------------------------------------------------------------------------------
                    #ref1 = datas2[0].get("ref")
                    datas3 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcMaterialLayerSet", namespaces=namespaces)
                    for d in datas3:
                        if d.get("id") == ref1:
                            new_start_node = d
                    datas4 = new_start_node.xpath("./ifc:MaterialLayers/ifc:IfcMaterialLayer", namespaces=namespaces)
                    for da in datas4:
                        ref2 = da.get("ref")
                        datas5 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcMaterialLayer", namespaces=namespaces)
                        for d in datas5:
                            if d.get("id") == ref2:
                                new_start_node = d

                        Add_On_Dict_newEntries[URIRef(my_root + "SpaceBoundaryElement" + str(level_counter))] = [new_start_node, URIRef(my_root + "SpaceBoundaryElement")]
                        curr_layer = URIRef( str(self.USObase) + "SpaceBoundaryElement" + str(level_counter) )
                        USO_New.add( (URIRef(surf_addr), URIRef( str(self.USObase) + str("hasSpaceBoundaryElementMember") ), curr_layer) )
                        USO_New.add( (curr_layer, RDF.type, URIRef(str(self.USObase + "SpaceBoundaryElement") )) )
                        level_counter += 1

                        datas6 = new_start_node.xpath("./ifc:LayerThickness", namespaces=namespaces)
                        ref3 = datas6[0].get("ref")
                        thickness = datas6[0].text
                        #print "thickness: ", thickness
                        #print direction_sense, reference_line_offset, layer_direction

                        valueNow = [ ("thickness", thickness), ("direction_sense", direction_sense), ("reference_line_offset", reference_line_offset), ("layer_direction", layer_direction) ]
                        USO_New.add( (URIRef(curr_layer), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("3DSpaceBoundaryElementMeasurements") ) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(valueNow) ) ) )
                        #print "Added: ", valueNow
                        property_counter += 1

                else:
                    wall_matches = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelAggregates/ifc:RelatingObject/ifc:"+str(child.split("}")[1]), namespaces=namespaces)
                    new_usage_set_ref = ""
                    new_start = ""
                    new_beg_roof = ""
                    for w in wall_matches:
                        if w.get("ref") == ref_of_surface_types:
                            wp = w.getparent().getparent()
                            ss = wp.xpath("./ifc:RelatedObjects", namespaces=namespaces)
                            kids = ss[0].getchildren()
                            child = kids[0].tag
                            new_usage_set = wp.xpath("./ifc:RelatedObjects/ifc:"+str(child.split("}")[1]), namespaces=namespaces)
                            if new_usage_set != []:
                                new_usage_set_ref = new_usage_set[0].get("ref")
                                if len(new_usage_set) > 1:
                                    print "new_usage_set --- There is a set of members here, only seen so far for curtain walls with several plates and members but using overall thickness for now..."
                    datas1 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcRelAssociatesMaterial/ifc:RelatedObjects/ifc:"+str(child.split("}")[1]), namespaces=namespaces)
                    for d in datas1:
                        if d.get("ref") == new_usage_set_ref:
                            new_start = d
                            new_start = new_start.getparent().getparent()
                    #-------------------------------------------------------------------------------------------------------
                    if childname == "IfcRoof":
                        wall_type = "/doc:iso_10303_28/ifc:uos/ifc:IfcRoof"
                    elif childname == "IfcCurtainWall":
                        wall_type = "/doc:iso_10303_28/ifc:uos/ifc:IfcCurtainWall"
                    else:
                        print "Some Type Not Yet Seen..."
                        wall_type = ""
                    datasa = tree.xpath(wall_type, namespaces=namespaces)
                    new_beg = ""
                    for da in datasa:
                        if da.get("id") == ref_of_surface_types:
                            new_beg_roof = da

                    datasb = new_beg_roof.xpath("./ifc:ObjectPlacement/ifc:IfcLocalPlacement", namespaces=namespaces)
                    loc_ref = datasb[0].get("ref")
                    datasc = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcLocalPlacement", namespaces=namespaces)
                    for da in datasc:
                        if da.get("id") == loc_ref:
                            new_beg_now = da
                    datasd = new_beg_now.xpath("./ifc:RelativePlacement/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                    loc_refa = datasd[0].get("ref")
                    if loc_refa == None:
                        loc_refa = datasd[0].get("id")
                        datasd = new_beg_now.xpath("./ifc:RelativePlacement/ifc:IfcAxis2Placement3D/ifc:Location/ifc:IfcCartesianPoint/ifc:Coordinates/ifc:IfcLengthMeasure", namespaces=namespaces)
                        coor_set_g = list()
                        for da in datasd:
                            coor_set_g.append(da.text)
                        axis_2_placement_relPlace = coor_set_g
                    else:
                        datasf = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                        for da in datasf:
                            if da.get("id") == loc_refa:
                                new_beg = da
                        datasg = new_beg.xpath("./ifc:Location/ifc:IfcCartesianPoint/ifc:Coordinates/ifc:IfcLengthMeasure", namespaces=namespaces)
                        coor_set_g = list()
                        for da in datasg:
                            coor_set_g.append(da.text)
                        axis_2_placement_relPlace = coor_set_g
                    #-------------------------------------------------------------------------------------------------------
                    datass = new_beg_now.xpath("./ifc:PlacementRelTo/ifc:IfcLocalPlacement", namespaces=namespaces)
                    loc_refb = datass[0].get("ref")
                    for d in datasc:
                        if d.get("id") == loc_refb:
                            new_beg = d
                    datasd = new_beg.xpath("./ifc:RelativePlacement/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                    loc_refa = datasd[0].get("ref")
                    #print "test", loc_refa
                    datasf = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcAxis2Placement3D", namespaces=namespaces)
                    for da in datasf:
                        if da.get("id") == loc_refa:
                            new_beg = da
                    datasg = new_beg.xpath("./ifc:Location/ifc:IfcCartesianPoint", namespaces=namespaces)
                    next_ref = datasg[0].get("ref")
                    datash = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcCartesianPoint", namespaces=namespaces)
                    for da in datash:
                        if da.get("id") == next_ref:
                            new_beg = da
                    datasi = new_beg.xpath("./ifc:Coordinates/ifc:IfcLengthMeasure", namespaces=namespaces)
                    coor_set_h = list()
                    for da in datasi:
                        coor_set_h.append(da.text)
                    axis_2_placement_relTo = coor_set_h
                    #-------------------------------------------------------------------------------------------------------
                    datas2 = new_start.xpath("./ifc:RelatingMaterial/ifc:IfcMaterialLayerSet", namespaces=namespaces)
                    if datas2 == []:
                        Add_On_Dict_newEntries[URIRef(my_root + "SpaceBoundaryElement" + str(level_counter))] = [new_start_node, URIRef(my_root + "SpaceBoundaryElement")]
                        curr_layer = URIRef( str(self.USObase) + "SpaceBoundaryElement" + str(level_counter) )
                        USO_New.add( (URIRef(surf_addr), URIRef( str(self.USObase) + str("hasSpaceBoundaryElementMember") ), curr_layer) )
                        USO_New.add( (curr_layer, RDF.type, URIRef(str(self.USObase + "SpaceBoundaryElement") )) )
                        level_counter += 1
                        thickness = '1"'  # Hard coding this for now because these walls in our example building are all 1"Glass
                        valueNow = [ ("thickness", thickness), ("axis_2_placement_relPlace", axis_2_placement_relPlace), ("axis_2_placement_relTo", axis_2_placement_relTo) ]
                        USO_New.add( (URIRef(curr_layer), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("3DSpaceBoundaryElementMeasurements") ) )
                        USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(valueNow) ) ) )
                        #print "Added: ", valueNow
                        property_counter += 1
                    else:
                        ref1 = datas2[0].get("ref")
                        datas3 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcMaterialLayerSet", namespaces=namespaces)
                        for d in datas3:
                            if d.get("id") == ref1:
                                new_start_node = d
                        datas4 = new_start_node.xpath("./ifc:MaterialLayers/ifc:IfcMaterialLayer", namespaces=namespaces)
                        for da in datas4:
                            ref2 = da.get("ref")
                            datas5 = tree.xpath("/doc:iso_10303_28/ifc:uos/ifc:IfcMaterialLayer", namespaces=namespaces)
                            for d in datas5:
                                if d.get("id") == ref2:
                                    new_start_node = d

                            Add_On_Dict_newEntries[URIRef(my_root + "SpaceBoundaryElement" + str(level_counter))] = [new_start_node, URIRef(my_root + "SpaceBoundaryElement")]
                            curr_layer = URIRef( str(self.USObase) + "SpaceBoundaryElement" + str(level_counter) )
                            USO_New.add( (URIRef(surf_addr), URIRef( str(self.USObase) + str("hasSpaceBoundaryElementMember") ), curr_layer) )
                            USO_New.add( (curr_layer, RDF.type, URIRef(str(self.USObase + "SpaceBoundaryElement") )) )
                            level_counter += 1

                            datas6 = new_start_node.xpath("./ifc:LayerThickness", namespaces=namespaces)
                            ref3 = datas6[0].get("ref")
                            thickness = datas6[0].text
                            #print "thickness2: ", thickness
                            #print "ttt", axis_2_placement_relPlace, axis_2_placement_relTo

                            valueNow = [ ("thickness", thickness), ("axis_2_placement_relPlace", axis_2_placement_relPlace), ("axis_2_placement_relTo", axis_2_placement_relTo) ]
                            USO_New.add( (URIRef(curr_layer), hasProperty, URIRef(str(self.USObase) + "Property" + str(property_counter))) )
                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasType, Literal("3DSpaceBoundaryElementMeasurements") ) )
                            USO_New.add( (URIRef(str(self.USObase) + "Property" + str(property_counter)), hasValue, Literal(str(valueNow) ) ) )
                            #print "Added: ", valueNow
                            property_counter += 1

        #print "This is the set of Surfaces (ex. Vet Center has about 8/600 that do not break down in to Materials, so they are skipped in the material level of this graph construction)"
        print "extra_set", extra_set

        #print "Add_On_Dict"
        for n in Add_On_Dict_newEntries:
            Add_On_Dict[n] = Add_On_Dict_newEntries[n]
            # Now when I process the Surfaces, the Spaces will be in here to match
        #for n in Add_On_Dict:
        #    print n, Add_On_Dict[n]

        return USO_New, property_counter, Add_On_Dict

'''
Material Paths Examples:

thickness
*/ifc:IfcRelSpaceBoundary		                     to 	/ifc:RelatedBuildingElement***
*/ifc:IfcRelAssociatesMaterial/ifc:RelatedObjects    to 	*/ifc:IfcRelAssociatesMaterial*2*
*/ifc:IfcRelAssociatesMaterial						 to		/ifc:RelatingMaterial/ifc:IfcMaterialLayerSetUsage
*/ifc:IfcMaterialLayerSetUsage						 to 	/ifc:ForLayerSet/ifc:IfcMaterialLayerSet
*/ifc:IfcMaterialLayerSet							 to		/ifc:MaterialLayers/ifc:IfcMaterialLayer
*/ifc:IfcMaterialLayer								 to 	/ifc:LayerThickness

thickness
*/ifc:IfcRelSpaceBoundary							 to		/ifc:RelatedBuildingElement***
*/ifc:IfcRelAggregates/ifc:RelatingObject 			 to 	.*2*
*/ifc:IfcRelAggregates								 to 	/ifc:RelatedObjects***
*/ifc:IfcRelAssociatesMaterial/ifc:RelatedObjects    to 	/ifc:IfcRelAssociatesMaterial*2*
*/ifc:IfcRelAssociatesMaterial						 to		/ifc:RelatingMaterial/ifc:IfcMaterialLayerSet
*/ifc:IfcMaterialLayerSet							 to 	/ifc:MaterialLayers/ifc:IfcMaterialLayer
*/ifc:IfcMaterialLayer								 to		/ifc:LayerThickness

direction_sense
*/ifc:IfcRelSpaceBoundary         					  to    /ifc:RelatedBuildingElement***
*/ifc:IfcRelAssociatesMaterial/ifc:RelatedObjects     to 	*/ifc:IfcRelAssociatesMaterial*2*
*/ifc:IfcRelAssociatesMaterial						  to 	/ifc:RelatingMaterial/ifc:IfcMaterialLayerSetUsage
*/ifc:IfcMaterialLayerSetUsage						  to 	/ifc:DirectionSense

reference_line_offset
*/ifc:IfcRelSpaceBoundary         					  to    /ifc:RelatedBuildingElement***
*/ifc:IfcRelAssociatesMaterial/ifc:RelatedObjects     to 	*/ifc:IfcRelAssociatesMaterial*2*
*/ifc:IfcRelAssociatesMaterial						  to 	/ifc:RelatingMaterial/ifc:IfcMaterialLayerSetUsage
*/ifc:IfcMaterialLayerSetUsage						  to 	/ifc:OffsetFromReferenceLine

layer_direction
*/ifc:IfcRelSpaceBoundary         					  to    /ifc:RelatedBuildingElement***
*/ifc:IfcRelAssociatesMaterial/ifc:RelatedObjects     to 	*/ifc:IfcRelAssociatesMaterial*2*
*/ifc:IfcRelAssociatesMaterial						  to 	/ifc:RelatingMaterial/ifc:IfcMaterialLayerSetUsage
*/ifc:IfcMaterialLayerSetUsage						  to 	/ifc:LayerSetDirection
'''