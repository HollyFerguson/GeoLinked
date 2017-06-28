#-------------------------------------------------------------------------------
# Name:        coorsFromVocabs.py  (version 2 for use with smartVocabs)
# Purpose:     Determine the 3rd Dimension for each 2D surface based on thickness
#              and Determine the divisions of coordinates in material layers
#              based on thickness proportions for each 3D surface and add triples
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     04/04/2016
# Copyright:   (c) Holly Tina Ferguson 2016
# Licence:     The University of Notre Dame
#-------------------------------------------------------------------------------

# #!/usr/bin/python
import sys
import os
import math
import string
import shapefile
#from shapely.geometry import Point
#from shapely.geometry import Polygon
from numpy import *
import scipy
import scipy.linalg
import numpy
from numpy import matrix
from numpy import linalg
import rdflib
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF
from rdflib import Namespace
#from scipy.spatial import ConvexHull


class coorsFromVocabs():
    # Input parameters
    # May change as additional file options get entered into the mix
    namespaces = {'gb': "http://www.gbxml.org/schema"}


    def materialLayers(self, UBO_New, currSurfCoordinates, sID, proportionDict, hwtOrderDict, this_file_type):
        """
        Determine the material layers from passed dictionary
        Assuming the gbxml standards of H and W in Feet and T in Meters, will add to this as file types are added
        """

        # For GBXML file type, used for now in the vocabs version
        #if flag == 0:
        #    self.unitCheck(tree)
        # Eventually if this is handling other schemas, direction will depend on coordinate ordering, now its the right-hand rule for gbxml
        direction = 0
        if this_file_type == "gbxml":
            direction = 1 # 1 Means counter-clockwise coordinate ordering with right-hand rule applied making + the normal direction for ordering materials
        else:
            print "processing previously unseen file type in coorsFromVocabs.py - needs right-hand rule flag"

        # For now working with the assumption that we will be calculating a 2D bounding box to match t, h, and w
        # For the time being, it is also necessary to assume that the largest two bounding lengths mean h and w, not t
        # since even with floors, for example, the h and w correspond to the surface area...but may still need a bounding box
        # There have to be certain assumptions because the coordinates are in the body frame and the h and w are in the
        # object frame, which is where the RR Pattern may become useful....(in order to solve adding thicknesses)

        # Find surface Bounding Box
        bbox, PT = self.findBoundingBox(currSurfCoordinates, sID)
        # Find Normal to this Surface to know how to Extrude for Thicknesses
        A, normal = self.findBBNormal(currSurfCoordinates, bbox, sID, PT)
        # Use normal to calculate the new set of points that include thickness (3D)
        surface3D, plus, minus = self.thicknessCoordinates(currSurfCoordinates, normal, hwtOrderDict, sID, direction)
        # Use function to create 3D surface triples
        #UBO_New, surf_counter, property_counter = self.add3DSurfacePoints(surface3D, UBO_New, surf_counter, property_counter, new_s, memberFlag)
        # For this surface, get all of the sets of coordinates for material layers
        MaterialLayerCoodinateSet = self.findMaterialCoorSet(A, normal, proportionDict, hwtOrderDict, sID, surface3D, direction, plus, minus)
        # Use function to create 3D material triples
        #UBO_Final, material_counter = self.addMaterialCoorTriples(UBO_New, MaterialLayerCoodinateSet, surf_counter, property_counter, new_sf, memberFlag, material_counter)

        # Now do this for each material
        # Next, use function to create triples

        return surface3D, MaterialLayerCoodinateSet    #UBO_New, surf_counter, property_counter, material_counter # Pass back the updated graph with the new material layer triples

    # Unused in the vocabs version
    """
    def unitCheck(self, tree):
        # Unit verification print statements, for referencing purposes and debugging
        hw = "None"
        t = "None"
        handw = tree.xpath("/gb:gbXML", namespaces=self.namespaces)
        for item in handw:
            hw = item.get("lengthUnit")
        thickness = tree.xpath("/gb:gbXML/gb:Material/gb:Thickness", namespaces=self.namespaces)
        for item in thickness:
            t = item.get("unit")
        #print "t in: ", t, ", h & w in: ", hw

        return
    """

    def unitTranslate(self, SurfaceToMaterialList, parent_id):
        # Adjust the material Thickness to be in Feet...(as long as the units all match)
        newDictEntry = list()
        newThicknessDict = dict()
        for item in SurfaceToMaterialList:
            # Change Meters to Feet
            newValue = 3.2808399 * item[1]
            eachList = (item[0], newValue)
            newDictEntry.append(eachList)
        newThicknessDict[parent_id] = newDictEntry

        return newThicknessDict

    def organizeThicknessesProportionally(self, surface, UpdatedSurfaceToMaterialList, currSurfCoordinates, namespaces):
        # Organize lengths and coordinates proportionally to devise which on is the thickness coordinate
        # Needs to be done proportionally due to the fact that there may not ba a way to tell h/w/t directions

        h = 0.0
        w = 0.0

        if namespaces == {'gb': "http://www.gbxml.org/schema"}:
            h = float(surface.xpath("./gb:RectangularGeometry/gb:Height",namespaces = self.namespaces)[0].text)
            w = float(surface.xpath("./gb:RectangularGeometry/gb:Width",namespaces = self.namespaces)[0].text)
        else:
            print "Need next set of namespaces to get height and width from in coorsFromVocabs...", "height: ", h, "width: ", w

        hwtOrderDict = dict()
        hwtList = list()
        hwtType = list()
        if (h > w):
            orderFeet = (h, w)
            orderType = ("h", "w")
        else:
            orderFeet = (w, h)
            orderType = ("w", "h")

        # proportionDict[same surface] = [(total, #total, prop-100(%)), (materialID, thickness, prop), (materialID, thickness, prop), etc.]
        total = 0
        proportionDict = dict()
        for entry in UpdatedSurfaceToMaterialList:
            total = 0
            entryList = list()
            #print "entry", entry
            #print UpdatedSurfaceToMaterialList[entry]
            for item in UpdatedSurfaceToMaterialList[entry]:
                current = float(item[1])
                total += current
            #print "total, ", total
            entryOne = ("total", total, 100)
            entryList.append(entryOne)
            for item in UpdatedSurfaceToMaterialList[entry]:
                tempList = list()
                prop = float(item[1]) * 100 / total
                #print "prop ", prop
                tempList = (item[0], float(item[1]), prop)
                entryList.append(tempList)
            proportionDict[entry] = entryList
            #print "total: ", total

            # Given orderFeet
            if total > orderFeet[0]:
                hwtList = (total, orderFeet[0], orderFeet[1])
                hwtType = ("t", orderType[0], orderType[1])
            elif total < orderFeet[1]:
                hwtList = (orderFeet[0], orderFeet[1], total)
                hwtType = (orderType[0], orderType[1], "t")
            else:
                # So in the middle or equal to one of them
                hwtList = (orderFeet[0], total, orderFeet[1])
                hwtType = (orderType[0], "t", orderType[1])
            # Record for each Surface
            hwtOrderDict[str(entry)] = (hwtList, hwtType)

        #for item in proportionDict:
        #    print "check old structure: ", item, UpdatedSurfaceToMaterialList[item]
        #    print "check new structure: ", item, proportionDict[item]
        #    print "check hwt order set: ", item, hwtOrderDict[item]

        return proportionDict, hwtOrderDict

    def findBoundingBox(self, currSurfCoordinates, sID):
        """
        Using Library from: https://pypi.python.org/pypi/pyshp
        From: https://pypi.python.org/pypi/pyshp
        """
        #gbxml standard 3D space:
        #y is north
        #z is vertical to the sky
        #x is east

        # Single Room Coordiantes for Surface 1:
        # [(-23.28571, 10.36111, 0.0), (-23.28571, 10.36111, 11.0625), (-5.965204, 20.36111, 11.0625), (-5.965204, 20.36111, 0.0)]
        w = shapefile.Writer(shapeType=shapefile.POLYGONZ)
        PT = []
        for i in currSurfCoordinates:
            for j in i:
                x = float(j[0])
                y = float(j[1])
                z = float(j[2])
                p = [x, y, z]
                PT.append(p)
        w.poly([PT], shapeType=15)
        #w.poly([[[x, y, z], [x, y, z], [x, y, z]]], shapeType=15)
        #w.autoBalance = 1  # Feature to make sure when you add either a shape or a record the two sides of the equation line up
        #print "MFPT: ", len(currSurfCoordinates), PT, type(PT).__name__ #, type(PT[1]).__name__, type(PT[1][0]).__name__
        w.field("currentSurfaceShapefile")
        w.record("currentSurfaceShapefile")
        w.save("shapefiles/currentSurfaceShapefile")

        #Example: w.poly([[[-89.0, 33, 12], [-90, 31, 11], [-91, 30, 12]]], shapeType=15)
        # xyz points are stored as xy and then z is seperate
        #r = shapefile.Reader("shapefiles/test/MyPolyZ")
        #s = r.shape(0)
        #s.points   outputs >>>[[-89.0, 33.0], [-90.0, 31.0], [-91.0, 30.0], [-89.0, 33.0]]
        #s.z        outputs >>>[12.0, 11.0, 12.0, 12.0]

        sf = shapefile.Reader("shapefiles/currentSurfaceShapefile.shp")
        shapes = sf.shapes()
        bbox = shapes[0].bbox # Retrieves the bounding box of the first shape

        #print "bbox: ,", bbox # Will print the bounding box coordinates

        # Remove the last shape in the polygon shapefile.
        e = shapefile.Editor(shapefile="shapefiles/currentSurfaceShapefile.shp")
        e.delete(-1)
        #e.save('shapefiles/currentSurfaceShapefile')
        e = None

        return bbox, PT

    def findBBNormal(self, currSurfCoordinates, bbox, sID, PT):
        """
        Find normal to surface to get thickness extrusion coordinates
        From: older GS shadow module
        """
        currSurfCoordinates = currSurfCoordinates[0]
        #print "keeping", currSurfCoordinates
        z = zeros((len(currSurfCoordinates), 1))
        poly = concatenate((currSurfCoordinates, z), 1)
        row = 0
        new_list = list()
        while row < len(poly):
            new_tuple = list()
            col = 0
            x = poly[row, col]
            new_tuple.append(x)
            y = poly[row, col + 1]
            new_tuple.append(y)
            z = poly[row, col + 2]
            new_tuple.append(z)
            new_set = tuple(new_tuple)
            new_list.append(new_set)
            row += 1
        poly = new_list
        if len(poly) < 3:
            # Just a line or point - no area so return o for total area
            return 0
        total = [0, 0, 0]
        N = len(poly)
        for i in range(N):
            vi1 = poly[i]
            vi2 = poly[(i+1) % N]
            prod = numpy.cross(vi1, vi2)
            total[0] += prod[0]
            total[1] += prod[1]
            total[2] += prod[2]
        result = numpy.dot(total, self.unit_normal(poly[0], poly[1], poly[2]))
        A = abs(result/2)
        normal = self.unit_normal(poly[0], poly[1], poly[2])
        #print "results: ", self.unit_normal(poly[0], poly[1], poly[2]), abs(result/2)

        return A, normal

    def unit_normal(self, a, b, c):
        # Unit normal vector of plane defined by points a, b, and c
        x = numpy.linalg.det([[1, a[1], a[2]], [1, b[1], b[2]], [1, c[1], c[2]]])
        y = numpy.linalg.det([[a[0], 1, a[2]], [b[0], 1, b[2]], [c[0], 1, c[2]]])
        z = numpy.linalg.det([[a[0], a[1], 1], [b[0], b[1], 1], [c[0], c[1], 1]])
        magnitude = (x**2 + y**2 + z**2)**.5

        return (x/magnitude, y/magnitude, z/magnitude)

    def thicknessCoordinates(self, currSurfCoordinates, normal, hwtOrderDict, sID, direction):
        # Find new Point Set for this surface based on existing points, thickness, and normal (x, y, z)
        # This routine is to get new points for surfaces connected on the center-line...will update upon new schemas
        #print "given", currSurfCoordinates, normal, hwtOrderDict, sID, direction
        currSurfCoordinates = currSurfCoordinates[0]
        surface3D = list()
        plus = list()
        minus = list()
        new_pts = list()

        if direction == 1:
            # Standard gbxml direction of center-line is assumed
            # Get tuple data associated with this surface type
            # Get data in format: ((20.0, 11.0625, 1.16), ('w', 'h', 't')), gives t percent of:  3.61990950757
            overallSurfaceInfo = list(hwtOrderDict[sID])
            num = overallSurfaceInfo[0]
            label = overallSurfaceInfo[1]
            sum_hwt = num[0] + num[1] + num[2]
            t = 0
            find = 0
            for item in label:
                if item == "t":
                    t = (num[find] * 100) / sum_hwt
                    #print "t (with is now the amount of units compared to height and width): ", t
                find += 1
            normal = numpy.array(normal)
            # Get new_coordinate_set for the geometry using +t/2 and -t/2
            for point in currSurfCoordinates:
                pt = numpy.array(point)
                #print "check types: ", type(pt).__name__, type(normal).__name__, type(t).__name__, pt, normal
                # Plus (P1 points away from the respective space) and Minus (P2 points toward the center of the space)
                P1 = pt + (float(t)/2)*(normal)
                P2 = pt - (float(t)/2)*(normal)
                plus.append(tuple(P1))
                minus.append(tuple(P2))
            #print "plus", plus
            #print "minus", minus
            for item in plus:
                new_pts.append(item)
            for item in minus:
                new_pts.append(item)
            surface3D = new_pts
            #print "3D: ", surface3D
        else:
            print "Direction flag is not yet handled!"

        return surface3D, plus, minus

    def add3DSurfacePoints(self, surface3D, UBO_New, surf_counter, property_counter, new_space, memberFlag):
        # Add triple that will go from SpatialCollectionLocation--hasSpaceBoundaryMember--SpaceBoundary
        base = "http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"

        # Enclosed-space pieces (i.e. regular surfaces)
        if memberFlag == 1:
            hasSpaceBoundaryMember = URIRef(base + "Space:hasSpaceBoundaryMember")
            SpaceBoundary = URIRef(base + "SpaceBoundary")
            new_sf = "#SpaceBoundary" + str(surf_counter)
            #new_sf = URIRef(base + new_sf)
            new_sf = URIRef(new_sf)
            Space = URIRef(new_space)
            UBO_New.add( (new_sf, RDF.type, SpaceBoundary) )
            UBO_New.add( (Space, hasSpaceBoundaryMember, new_sf) )
            hasProperty = URIRef(new_sf + ":hasProperty")
            PropertyD = URIRef( new_sf + ":SurfaceData3D")
            #Property = URIRef(base + "Property")
            #UBO_New.add( (PropertyD, RDF.type, Property) )
            hasType = URIRef(":hasType") #new_sf +
            hasValue = URIRef(":hasValue")
            c = "3DSurfaceCoordinates"
            UBO_New.add( (new_sf, hasProperty, PropertyD) )
            UBO_New.add( (PropertyD, hasType, Literal(c)) )
            UBO_New.add( (PropertyD, hasValue, Literal(str(surface3D))) )

        # Non-enclosed-space pieces (i.e. shade)
        if memberFlag == 0:
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
            PropertyD = URIRef(new_b + ":SurfaceData3D")
            hasType = URIRef(":hasType") #new_b +
            hasValue = URIRef(":hasValue")
            c = "3DSurfaceCoordinates"
            UBO_New.add( (new_b, hasProperty, PropertyD) )
            UBO_New.add( (PropertyD, hasType, Literal(c)) )
            UBO_New.add( (PropertyD, hasValue, Literal(str(surface3D))) )

        return UBO_New, surf_counter, property_counter

    def findMaterialCoorSet(self, A, normal, proportionDict, hwtOrderDict, sID, surface3D, direction, plus, minus):
        """
        # Use: thicknessCoordinates(currSurfCoordinates, normal, hwtOrderDict, sID, direction)
        # This can be used to get each material as a surface3D
        proportionDict[same surface] = [(total, #total, prop-100(%)), (materialID, thickness, prop), (materialID, thickness, prop), etc.]
        hwtOrderDict: ((20.0, 11.0625, 1.16), ('w', 'h', 't')), example: this gives t percent of:  3.61990950757
        surface3D: (for gbxml is plus, minus coordinates from center line)
        plus: for center line is half the thickness along normal in positive direction
        minus: for center line is half the thickness along normal in negative direction
        # *** Plus (P1 points away from the respective space) and Minus (P2 points toward the center of the space)
        # We believe the above standard for point ordering and normal for determining material coordinates below
        # Additionally, this method will work for surfaces that are part of a space and others
        """
        MaterialCoorSet = list()
        tempList = list()
        currentOutside = plus
        currentInside = minus
        #this_ID, thickness, proportionOfWhole = None
        counter = 0
        last = 0
        length = len(proportionDict[sID])
        lengthmo = (length - 1)
        #thicknessWhole = proportionDict[sID][0][1]
        #Whole = proportionDict[sID][0][2]
        for layer in proportionDict[sID]:
            if layer[0] != 'total':
                surface3D = list()
                #this_ID = layer[0]
                #thickness = layer[1]
                proportionOfWhole = layer[2]
                if counter == lengthmo:
                    last = 1
                if last == 1:
                    # Just append the minus set of coordinates to the previous
                    for item in currentInside:
                        currentOutside.append(item)
                    surf3D = currentOutside
                    surface3D = tuple(surf3D)
                    MaterialCoorSet.append(surface3D)
                else:
                    surf3D, currentOutsideNow = self.materialCoordinates(normal, direction, proportionOfWhole, currentOutside, currentInside)
                    currentOutside = currentOutsideNow
                    surface3D = tuple(surf3D)
                    MaterialCoorSet.append(surface3D)
            counter += 1

        #print len(MaterialCoorSet), MaterialCoorSet

        return MaterialCoorSet

    def materialCoordinates(self, normal, direction, t, currentOutside, previousOutside):
        # Find new Point Set for each material based on existing points, thickness, and normal (x, y, z)
        # This routine generic for pre-known t that can be passed here along with the normal
        # t == the proportion of the whole total thicknesses
        # In this module, direction of 1 == to positive or the plus direction, 0 == to the minus or negative direction
        # 1 Means counter-clockwise coordinate ordering with right-hand rule applied making + the normal direction for ordering materials
        surface3D = list()
        new_pts = list()
        newOutside = list()
        if direction == 1:
            outside = currentOutside
            normal = numpy.array(normal)
            # Get new_coordinate_set for the geometry
            for point in outside:
                pt = numpy.array(point)
                # Minus because we know normal points away from space and we need to go from outside to inside
                P1 = pt - (float(t))*(normal)
                new_pts.append(tuple(P1))
            for item in new_pts:
                newOutside.append(item)
            #print len(new_pts), len(newOutside), "a"
            for item in currentOutside:
                new_pts.append(item)
            surface3D = new_pts
            #print len(new_pts), len(outside), len(newOutside)
        else:
            print "Direction flag is not yet handled!"

        return surface3D, newOutside

    def addMaterialCoorTriples(self, UBO_New, MaterialLayerCoodinateSet, surf_counter, property_counter, new_sf, memberFlag, material_counter):
        # Add triples that will go from each Surface to all materials that make up that surface
        base = "http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"

        for m in MaterialLayerCoodinateSet:
            material = list(m) # Change type to have consistent
            #print "material", material, type(material).__name__

            # Where each material is a set of the 3D coordinates that describe it (i.e. 4-edge wall has 8 xyz points)
            # Enclosed-space pieces (i.e. regular surfaces)
            if memberFlag == 1:
                hasSpaceBoundaryElementMember = URIRef(base + "Space:hasSpaceBoundaryElementMember")
                SpaceBoundaryElement = URIRef(base + "SpaceBoundaryElement")
                new_m = "#SpaceBoundaryElement" + str(material_counter)
                #new_sf = URIRef(base + new_sf)
                new_m = URIRef(new_m)
                SpaceBoundary = URIRef(new_sf)
                UBO_New.add( (new_m, RDF.type, SpaceBoundaryElement) )
                UBO_New.add( (SpaceBoundary, hasSpaceBoundaryElementMember, new_m) )

                hasProperty = URIRef(new_m + ":hasProperty")
                PropertyE = URIRef( new_m + ":MaterialData3D")
                #Property = URIRef(base + "Property")
                #UBO_New.add( (PropertyD, RDF.type, Property) )
                hasType = URIRef(":hasType") #new_sf +
                hasValue = URIRef(":hasValue")
                c = "3DElementCoordinates"
                UBO_New.add( (new_m, hasProperty, PropertyE) )
                UBO_New.add( (PropertyE, hasType, Literal(c)) )
                UBO_New.add( (PropertyE, hasValue, Literal(str(material))) )

            # Non-enclosed-space pieces (i.e. shade)
            if memberFlag == 0:
                SpaceCollectionLocation = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollectionLocation") #?
                hasSpaceBoundaryElementMember = URIRef(base + "SpaceCollectionLocation:hasSpaceBoundaryElementMember")
                SpaceBoundaryElement = URIRef(base + "SpaceBoundaryElement")
                # Still using surf_counter here will continue numbering surfaces
                new_m = "#SpaceBoundaryElement" + str(material_counter)
                #new_b = URIRef(base + new_b)
                new_m = URIRef(new_m)
                SpaceBoundary = URIRef(new_sf)
                UBO_New.add( (new_m, RDF.type, SpaceBoundaryElement) )
                UBO_New.add( (SpaceBoundary, hasSpaceBoundaryElementMember, new_m) )

                hasProperty = URIRef(new_m + ":hasProperty")
                #Property = URIRef(base + "Property")
                PropertyE = URIRef(new_m + ":MaterialData3D")
                hasType = URIRef(":hasType")
                hasValue = URIRef(":hasValue")
                c = "3DElementCoordinates"
                UBO_New.add( (new_m, hasProperty, PropertyE) )
                UBO_New.add( (PropertyE, hasType, Literal(c)) )
                UBO_New.add( (PropertyE, hasValue, Literal(str(material))) )
            material_counter += 1

        return UBO_New, material_counter

    def devCoorsBasedOn_typeA(self, dim, center_point, x_center_offset, y_center_offset, z_center_offset, depth):
        #center_point is centroid, x_center_offset, y_center_offset, depth
        these_coors = ""
        x, y, z, add_sub_x, add_sub_y, add_sub_z = 0, 0, 0, 0, 0, 0
        x = float(center_point[0])
        y = float(center_point[1])
        z = float(center_point[2])
        if x_center_offset != "":
            add_sub_x = float(x_center_offset[0])/2
        if y_center_offset != "":
            add_sub_y = float(y_center_offset[0])/2
        if z_center_offset != "":
            add_sub_z = float(z_center_offset[0])/2

        # Assume to just set this up going around clockwise
        # And have to assume there are 4 points generated..typical simple box surface
        p1, p2, p3, p4 = (0,0,0), (0,0,0), (0,0,0), (0,0,0)
        if z_center_offset == "":
            # Just the base of a space so basic bounding box
            p1 = (x + add_sub_x, y + add_sub_y, z)
            p2 = (x - add_sub_x, y + add_sub_y, z)
            p3 = (x - add_sub_x, y - add_sub_y, z)
            p4 = (x + add_sub_x, y - add_sub_y, z)
        simple_bbox = (p1, p2, p3, p4)
        #print "simple_bbox 2D", simple_bbox

        if dim == "2D":
            these_coors = str(simple_bbox)
        p5, p6, p7, p8 = (0,0,0), (0,0,0), (0,0,0), (0,0,0)
        simple_3D_bbox = ()
        if dim == "3D":
            # Use simple_bbox and depth to add on the 3D version...for now assuming + is up, - is down...
            if str(depth[0][-1]) == ".":
                # Add 0 for proper float type
                depth = float(str(depth[0] + "0"))
                p5 = (p1[0], p1[1], p1[2] + depth)
                p6 = (p2[0], p2[1], p2[2] + depth)
                p7 = (p3[0], p3[1], p3[2] + depth)
                p8 = (p4[0], p4[1], p4[2] + depth)
                simple_3D_bbox = (p1, p2, p3, p4, p5, p6, p7, p8)
                #print "simple_bbox 3D", simple_3D_bbox
            these_coors =str(simple_3D_bbox)
            #print "these chars", these_coors

        return these_coors

    def OGC_to_Comma_Delimited(self, dimension, ground_surface_footprint_ogc):
        # Takes OGC formatted coordinates (space delimited) and returns standard comma delimited
        #print "ogc_coordinates", ground_surface_footprint_ogc
        ogc_coors = str(ground_surface_footprint_ogc)
        # turn " " into ", "
        #Remove blank spaces at beginning and end
        if ogc_coors.endswith(' '):
            ogc_coors = ogc_coors[0:-1]

        ogc_coors = "(" + ogc_coors.replace(" ", ", ") + ")"
        #print "last char", ogc_coors

        return ogc_coors












