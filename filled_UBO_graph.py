#-------------------------------------------------------------------------------
# Name:        filled_UBO_graph.py
# Purpose:     Fill graph with mapping for given structure
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     06/10/2015
# Copyright:   (c) Holly Tina Ferguson 2015
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------

# #!/usr/bin/python
import sys
import getopt
import os
import rdflib
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF
from rdflib import Namespace
import pprint
from lxml import etree
from thickness_to_coordinates import thickness_to_coordinates


class filled_UBO_graph():
    # Input parameters
    #variable = ""
    namespaces = {'gb': "http://www.gbxml.org/schema"}


    def fill_graph(self, this_file_type, mapDict, UBOgraphStructure, inputfile):
        """
        Fill appropriate mapping dictionary
        #http://rdflib.readthedocs.org/en/latest/
        #http://rdflib.readthedocs.org/en/latest/intro_to_graphs.html
        #http://rdflib.readthedocs.org/en/latest/intro_to_parsing.html

        RDF is a graph where the nodes are URI references, Blank Nodes or Literals, in RDFLib represented by
        the classes URIRef, BNode, and Literal. URIRefs and BNodes can both be thought of as resources, such
        a person, a company, a web-site, etc. A BNode is a node where the exact URI is not known. URIRefs are
        also used to represent the properties/predicates in the RDF graph. Literals represent attribute values,
        such as a name, a date, a number, etc.
        """

        # Existing empty Graph Framework
        UBO_frame = UBOgraphStructure
        #for stmt in UBO_frame:
        #    pprint.pprint(stmt)

        # First Graph Layer
        UBO_New = Graph()
        UBO = Namespace("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#")
        GeoInstance1 = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#GeoInstance1")
        ASpatialObject = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#ASpatialObject")
        hasSpatialCollectionLocationMember = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#ASpatialObject:hasSpatialCollectionLocationMember")
        SpaceCollectionLocation = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollectionLocation")
        # Graph.add((s, p, o))
        UBO_New.add( (GeoInstance1, RDF.type, ASpatialObject) )
        UBO_New.add( (GeoInstance1, hasSpatialCollectionLocationMember, SpaceCollectionLocation) )
        #UBO_New.add( (UBO.SpatialObject1, ASpatialObject.hasSpatialCollectionLocationMember, SpaceCollectionLocation) )

        # Second Graph Layer
        base = "http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"
        # Currently assuming that each model is 1 building..........may be updated later
        tree = etree.parse(inputfile)

        # Find the corresponding surface to get the correct construction ID...pre-processing
        print "pre-process"
        SurfaceToMaterialList = self.preProcess(inputfile, mapDict, tree)
        #for item in SurfaceToMaterialList:
        #    print "SurfaceToMaterialList: ", item, SurfaceToMaterialList[item]
        flag = 0
        proportionDict = dict()
        hwtOrderDict = dict()
        material_counter = 1

        start = mapDict["SpaceCollectionLocation"][0]
        find = mapDict["SpaceCollectionLocation-Property"][0]
        loc = tree.xpath("/gb:gbXML/gb:" + start + "/gb:" + find, namespaces=self.namespaces)
        if not loc:
            elevation = None
            latitude = None
            longitude = None
        hasProperty = URIRef(base + "SpaceCollectionLocation:hasProperty")
        Property = URIRef(base + "Property")
        PropertyA = URIRef(base + "SpaceLocationData")
        UBO_New.add( (PropertyA, RDF.type, Property) )
        UBO_New.add( (SpaceCollectionLocation, hasProperty, PropertyA) )
        hasType = URIRef(base + "Property:hasType")
        hasValue = URIRef(base + "Property:hasValue")
        for l in loc:
            #e = str(mapDict[SpaceCollectionLocation][3])
            e = "Elevation"
            elevation = float(l.xpath("./gb:" + e, namespaces = self.namespaces)[0].text)
            Property1 = URIRef(base + "Property1")
            UBO_New.add( (Property1, RDF.type, PropertyA) )
            UBO_New.add( (Property1, hasType, Literal(e)) )
            UBO_New.add( (Property1, hasValue, Literal(elevation)) )
            lat = "Latitude"
            latitude = float(l.xpath("./gb:" + lat, namespaces = self.namespaces)[0].text)
            Property2 = URIRef(base + "Property2")
            UBO_New.add( (Property2, RDF.type, PropertyA) )
            UBO_New.add( (Property2, hasType, Literal(lat)) )
            UBO_New.add( (Property2, hasValue, Literal(latitude)) )
            lon = "Longitude"
            longitude = float(l.xpath("./gb:" + lon, namespaces = self.namespaces)[0].text)
            Property3 = URIRef(base + "Property3")
            UBO_New.add( (Property3, RDF.type, PropertyA) )
            UBO_New.add( (Property3, hasType, Literal(lon)) )
            UBO_New.add( (Property3, hasValue, Literal(longitude)) )

        # Third Graph Layer
        base = "http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"
        start = mapDict["SpaceCollectionLocation"][0]
        find = mapDict["SpaceCollection"][0]
        buildings = tree.xpath("/gb:gbXML/gb:" + start + "/gb:" + find, namespaces=self.namespaces)
        buildingsDict = dict()
        counter = 1
        property_counter = 4
        for b in buildings:
            # Will add Building1, Building2, etc.
            hasSpaceCollectionMember = URIRef(base + "SpaceCollectionLocation:hasSpaceCollectionMember")
            SpaceCollection = URIRef(base + "SpaceCollection")
            new_b = "SpaceCollection" + str(counter)
            new_b = URIRef(base + new_b)
            UBO_New.add( (new_b, RDF.type, SpaceCollection) )
            UBO_New.add( (SpaceCollectionLocation, hasSpaceCollectionMember, new_b) )
            hasProperty = URIRef(base + "SpaceCollection:hasProperty")
            Property = URIRef(base + "Property")
            PropertyB = URIRef(base + "SpaceMassingData")
            UBO_New.add( (PropertyB, RDF.type, Property) )
            UBO_New.add( (SpaceCollection, hasProperty, PropertyB) )
            hasType = URIRef(base + "Property:hasType")
            hasValue = URIRef(base + "Property:hasValue")
            a = "Area"
            area = float(b.xpath("./gb:" + a, namespaces = self.namespaces)[0].text)
            next_property = "Property" + str(property_counter)
            next_property = URIRef(base + next_property)
            UBO_New.add( (next_property, RDF.type, PropertyB) )
            UBO_New.add( (next_property, hasType, Literal(a)) )
            UBO_New.add( (next_property, hasValue, Literal(area)) )
            b_id = b.get("id")
            buildingsDict[new_b] = (b_id)
            property_counter += 1
            counter += 1
        space_counter = 1
        spacesDict = dict()
        overallUsedSurfaces = list()
        surf_counter = 1
        for b in buildings:
            # Will add respective Spaces to SpaceCollection1, etc.
            b_id = b.get("id")
            current_RDF_label = "none"
            current_b_id = "none"
            for item in buildingsDict:
                if b_id == buildingsDict[item]:
                    current_RDF_label = item
                    current_b_id = buildingsDict[item]

            #start = mapDict["SpaceCollectionLocation"][0]
            #find = mapDict["SpaceCollection"][0]
            spaces = b.xpath("./gb:Space", namespaces=self.namespaces)
            for s in spaces:
                hasSpaceMember = URIRef(base + "SpaceCollection:hasSpaceMember")
                Space = URIRef(base + "Space")
                new_s = "#Space" + str(space_counter)
                new_s = URIRef(new_s)
                SpaceCollection = URIRef(current_RDF_label)
                UBO_New.add( (new_s, RDF.type, Space) )
                UBO_New.add( (SpaceCollection, hasSpaceMember, new_s) )
                hasProperty = URIRef(base + "Space:hasProperty")
                Property = URIRef(base + "Property")
                PropertyC = URIRef(base + "SpaceData")
                UBO_New.add( (PropertyC, RDF.type, Property) )
                UBO_New.add( (Space, hasProperty, PropertyC) )
                hasType = URIRef(base + "Property:hasType")
                hasValue = URIRef(base + "Property:hasValue")
                c = "Coordinates"
                # This can later be better automated with the mapping dictionary, for now just using known path:
                space_coordinate_set = s.xpath("./gb:ShellGeometry/gb:ClosedShell/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
                scps = list()
                for coordinate_list in space_coordinate_set:
                    cp = list()
                    cartesian_points = coordinate_list.xpath("./gb:Coordinate", namespaces=self.namespaces)
                    #print "this should be 3 locations: ", cartesian_points
                    for point in cartesian_points:
                        cp.append(float(point.text))
                    coordinates = tuple(cp)
                    scps.append(coordinates)
                    #scps.append(cartesian_point)
                    #new_space.scps = scps  # now returning a list of tuples for non-square walls to get max/min heights
                next_property = "Property" + str(property_counter)
                next_property = URIRef(base + next_property)
                UBO_New.add( (next_property, RDF.type, PropertyC) )
                UBO_New.add( (new_s, hasProperty, next_property) )
                UBO_New.add( (next_property, hasType, Literal(c)) )
                UBO_New.add( (next_property, hasValue, Literal(str(scps))) )
                property_counter += 1

                s_id = s.get("id") ##---------------------------------------------------------------------------------------------------------------------------
                surf_id_list_for_this_space = list()
                surfaces = tree.xpath("/gb:gbXML/gb:Campus/gb:Surface", namespaces=self.namespaces)
                currentSpaceBoundaries = s.xpath("./gb:SpaceBoundary", namespaces=self.namespaces)
                for c in currentSpaceBoundaries:
                    su_id = c.get("surfaceIdRef")
                    for surf in surfaces:
                        surface_ID = surf.get("id")
                        if surface_ID == su_id:
                            surf_id_list_for_this_space.append(surf)
                            # This will ignore shading devices, however, so maybe the pattern needs a
                            # using hasSpaceBoundaryMember as seen in pattern with dashed lines (pptx)
                            # So, keep track of the surfaces that ARE used for spaces, and handle others afterwards...
                            overallUsedSurfaces.append(surf)
                #surfaces = tree.xpath("/gb:gbXML/gb:Campus/gb:Surface/gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
                #surfaces = s.xpath("./gb:SpaceBoundary/gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
                #surfaces = s.xpath("./gb:SpaceBoundary", namespaces=self.namespaces)

                for surf in surf_id_list_for_this_space:
                    sID = surf.get("id")
                    hasSpaceBoundaryMember = URIRef(base + "Space:hasSpaceBoundaryMember")
                    SpaceBoundary = URIRef(base + "SpaceBoundary")
                    new_sf = "#SpaceBoundary" + str(surf_counter)
                    #new_sf = URIRef(base + new_sf)
                    new_sf = URIRef(new_sf)
                    Space = URIRef(new_s)
                    UBO_New.add( (new_sf, RDF.type, SpaceBoundary) )
                    UBO_New.add( (Space, hasSpaceBoundaryMember, new_sf) )

                    hasProperty = URIRef(new_sf + ":hasProperty")
                    PropertyD = URIRef(new_sf + ":SurfaceData2D")
                    #UBO_New.add( (PropertyD, RDF.type, Property) )
                    hasType = URIRef(":hasType")  #new_sf +
                    hasValue = URIRef(":hasValue")
                    c = "2DSurfaceCoordinates"
                    surfc = list()
                    surf_coordinate_set = surf.xpath("./gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
                    for coordinate_list in surf_coordinate_set:
                        cp = list()
                        cartesian_points = coordinate_list.xpath("./gb:Coordinate", namespaces=self.namespaces)
                        #print "this should be 3 locations: ", cartesian_points
                        for point in cartesian_points:
                            cp.append(float(point.text))
                        coordinates = tuple(cp)
                        surfc.append(coordinates)
                    UBO_New.add( (new_sf, hasProperty, PropertyD) )
                    UBO_New.add( (PropertyD, hasType, Literal(c)) )
                    UBO_New.add( (PropertyD, hasValue, Literal(str(surfc))) )

                    # Call to use the thicknesses and calculate coordinates then add triples for those
                    thickness = tree.xpath("/gb:gbXML/gb:Material", namespaces=self.namespaces)
                    for item in thickness:
                        t = item.get("unit")
                    t = thickness_to_coordinates()
                    if flag == 0:
                        # Translate thickness meters into feet for each entry in SurfaceToMaterialList
                        SurfaceToMaterialList = t.unitTranslate(SurfaceToMaterialList)
                        # Organize lengths and coordinates proportionally to devise which on is the thickness coordinate
                        proportionDict, hwtOrderDict = t.organizeThicknessesProportionally(surf, SurfaceToMaterialList, surfc)
                    memberFlag = 1
                    UBO_New, surf_counter, property_counter, material_counter = t.materialLayers(UBO_New, surfc, tree, surf, flag, str(sID), surf_counter, property_counter, new_s, proportionDict, hwtOrderDict, memberFlag, this_file_type, new_sf, material_counter)
                    flag = 1
                    surf_counter += 1
                    property_counter += 1

                spacesDict[new_s] = (s_id, surf_id_list_for_this_space)
                # Will use spacesDict later when adding openings into the mix
                space_counter += 1

                # Process Extraneous Surfaces or other Boundaries that will still be from this Spatial Location Group
                #surfaces = tree.xpath("/gb:gbXML/gb:Campus/gb:Surface", namespaces=self.namespaces)
                for s in surfaces:
                    if s not in overallUsedSurfaces:
                        sID = s.get("id")
                        # Add triple that will go from SpatialCollectionLocation--hasSpaceBoundaryMember--SpaceBoundary
                        SpaceCollectionLocation = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollectionLocation") #?
                        hasSpaceBoundaryMember = URIRef(base + "SpaceCollectionLocation:hasSpaceBoundaryMember")
                        SpaceBoundary = URIRef(base + "SpaceBoundary")
                        # Still using surf_counter here will continue numbering surfaces
                        new_b = "#SpaceBoundary" + str(surf_counter)
                        #new_b = URIRef(base + new_b)
                        new_b = URIRef(new_b)
                        UBO_New.add( (new_b, RDF.type, SpaceBoundary) )
                        UBO_New.add( (SpaceCollectionLocation, hasSpaceBoundaryMember, new_b) )
                        hasProperty = URIRef(new_b + ":hasProperty")
                        #Property = URIRef(base + "Property")
                        PropertyD = URIRef(new_b + ":SurfaceData2D")
                        hasType = URIRef(":hasType") #new_b +
                        hasValue = URIRef(":hasValue")
                        c = "2DSurfaceCoordinates"
                        surfc = list()
                        surf_coordinate_set = s.xpath("./gb:PlanarGeometry/gb:PolyLoop/gb:CartesianPoint", namespaces=self.namespaces)
                        for coordinate_list in surf_coordinate_set:
                            cp = list()
                            cartesian_points = coordinate_list.xpath("./gb:Coordinate", namespaces=self.namespaces)
                            #print "this should be 3 locations: ", cartesian_points
                            for point in cartesian_points:
                                cp.append(float(point.text))
                            coordinates = tuple(cp)
                            surfc.append(coordinates)
                        UBO_New.add( (new_b, hasProperty, PropertyD) )
                        UBO_New.add( (PropertyD, hasType, Literal(c)) )
                        UBO_New.add( (PropertyD, hasValue, Literal(str(surfc))) )

                        # Call to use the thicknesses and calculate coordinates then add triples for those
                        t = thickness_to_coordinates()
                        if flag == 0:
                            # Translate thickness meters into feet for each entry in SurfaceToMaterialList
                            SurfaceToMaterialList = t.unitTranslate(SurfaceToMaterialList)
                            # Organize lengths and coordinates proportionally to devise which on is the thickness coordinate
                            proportionDict, hwtOrderDict = t.organizeThicknessesProportionally(s, SurfaceToMaterialList, surfc)
                        memberFlag = 0
                        UBO_New, surf_counter, property_counter, material_counter = t.materialLayers(UBO_New, surfc, tree, s, flag, str(sID), surf_counter, property_counter, new_b, proportionDict, hwtOrderDict, memberFlag, this_file_type, new_b, material_counter)
                        flag = 1
                        surf_counter += 1
                        property_counter += 1

        #print "Does this make sense?"
        #print UBO_New.serialize(format='turtle')

        return UBO_New, base

    def preProcess(self, inputfile, mapDict, tree):
        """
        Pre-Process gbXML based on known structure
        (add openings later as SpaceBoundaryElement)
        spacesDict[new_s] = (s_id, surf_id_list)
        """

        surfaceToConstr = dict()
        ConstrToMaterial = dict()
        #materialDict[surfaceID] = (material ID, thickness, material ID, thickness, etc.)
        SurfaceToMaterialList = dict()

        surfaces = tree.xpath("/gb:gbXML/gb:Campus/gb:Surface", namespaces=self.namespaces)
        constructions = tree.xpath("/gb:gbXML/gb:Construction", namespaces=self.namespaces)
        layers = tree.xpath("/gb:gbXML/gb:Layer", namespaces=self.namespaces)
        materials = tree.xpath("/gb:gbXML/gb:Material", namespaces=self.namespaces)

        # Map a Construction ID to each SurfaceID
        for s in surfaces:
            surfaceID = s.get("id")
            obj_constr = s.get("constructionIdRef")
            for c in constructions:
                constrID = c.get("id")
                if obj_constr == None:
                    obj_constr = constrID
                if constrID == obj_constr:
                    match = constrID
                    surfaceToConstr[surfaceID] = match
        #for surfaceID in surfaceToConstr:
        #    print "surfaceToConstr: ", surfaceID, surfaceToConstr[surfaceID]

        # Map a Material Name/ID? Set to each Construction ID
        for c in constructions:
            constrID = c.get("id")
            layerSet = c.xpath("./gb:LayerId", namespaces=self.namespaces)
            if not layerSet:
                layer_id = None
            else:
                for layer in layerSet:
                    layer_id = layer.get("layerIdRef")
                    #print "layerID: ", layer_id
                    matThicknessSet = list()
                    for layer in layers:
                        testLayerID = layer.get("id")
                        if testLayerID == layer_id:
                            elements = layer.xpath("./gb:MaterialId", namespaces=self.namespaces)
                            for element in elements:
                                material_id_num = element.get("materialIdRef")
                                for m in materials:
                                    singleMaterial = m.get("id")
                                    if singleMaterial == material_id_num:
                                        thickness = float(m.xpath("./gb:Thickness", namespaces=self.namespaces)[0].text)
                                        #thickness = m.xpath("./gb:Thickness", namespaces=self.namespaces)
                                        #for value in thickness:
                                            #new_material.thickness_unit = value.get("unit")
                                        if not thickness:
                                            thickness = None
                                            #thickness_unit = None
                                        mattuple = (singleMaterial, thickness)
                                        mtuple = tuple(mattuple)
                                        #print "new mTuple: ", mtuple
                                        matThicknessSet.append(mtuple)

            # Appended a list of tuples formatted: (material ID, thickness, material ID, thickness, etc.)
            ConstrToMaterial[constrID] = matThicknessSet
        #for constrID in ConstrToMaterial:
        #    print "ConstrToMaterial: ", constrID, ConstrToMaterial[constrID]

        # Fill SurfaceToMaterialList by matching a Surface ID to a Material Set
        for surfaceID in surfaceToConstr:
            construction = surfaceToConstr[surfaceID]
            tupleMaterialSet = ConstrToMaterial[construction]
            SurfaceToMaterialList[surfaceID] = tupleMaterialSet

        return SurfaceToMaterialList

    def lookup(self, mapDict, inputfile):
        """
        SpaceCollectionLocation                 ('Campus', ['x'])
        SpaceCollectionLocation-Property        ('Location', ['Location', '[Longitude]', '[Latitude]', '[Elevation]'])
        SpaceCollection                         ('Building', ['x'])
        SpaceCollection-Property                ('Coordinate', ['ShellGeometry', 'ClosedShell', 'PolyLoop', 'CartesianPoint', '[Coordinate]'])
        Space                                   ('Space', ['x'])
        Space-Property                          ('Coordinate', ['PlanarGeometry', 'PolyLoop', 'CartesianPoint', '[Coordinate]'])
        SpaceBoundary                           ('Surface', ['x'])
        SpaceBoundary-Property                  ('Coordinate', ['PlanarGeometry', 'PolyLoop', 'CartesianPoint', '[Coordinate]'])
        SpaceBoundaryElement                    ('Material', ['x'])
        SpaceBoundaryElement-Property           ('Thickness', ['Construction', 'Layer', '[Thickness]'])
        """

        return None


