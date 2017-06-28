#-------------------------------------------------------------------------------
# Name:        OGCqueryNfill.py
# Purpose:     Create OGC GeoSPARQL File Filled with UBO Data
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     07/28/2015
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
import string


class OGCqueryNfill():
    # Input parameters
    #variable = ""


    def processUBOforOGC(self, myUBO, base, OGC_RDF_header, OGC_file_parts):
        """
        Define how OGC corresponds to the UBO ontology in a dictionary
        Query UBO for data based on map,
        process coordinates into OGC format,
        and use answers to fill OGC RDF file for output
        """

        # Create the triples in a readable file to pass
        UBO_RDF = self.getRDF(myUBO)

        #OGC_RDF_file = header + properties + beginWriting + footer
        self.querySetUp(myUBO, base) # Set-up Query Checks

        # Note
        current_OGC_RDF = OGC_RDF_header

        self.queryUBO(myUBO, base, UBO_RDF, current_OGC_RDF, OGC_file_parts)

        # Note
        #? = self.?()

        return 0

    def getRDF(self, myUBO):

        #UBO_RDF = myUBO.serialize(destination='RDFout/myRDF.txt', format='turtle')
        UBO_RDF = myUBO.serialize(destination='RDFout/myRDF.rdf', format='turtle')

        return UBO_RDF

    def querySetUp(self, myUBO, base):

        for subject,predicate,obj in myUBO:
           if not (subject,predicate,obj) in myUBO:
              raise Exception("Iterator / Container Protocols are Broken!!")

        return 0

    def queryUBO(self, myUBO, base, UBO_RDF, current_OGC_RDF, OGC_file_parts):
        # objects(), subjects(), predicates(), predicates_objects(), etc
        #for person in g.subjects(RDF.type, FOAF.Person):
        #    print "%s is a person"%person
        #Graph.subjects(predicate=None, object=None)[source]: A generator of subjects with the given predicate and object
        #Graph.objects(subject=None, predicate=None)[source]: A generator of objects with the given subject and predicate
        #Graph.predicates(subject=None, object=None)[source]: A generator of predicates with the given subject and object
        #Graph.subject_objects(predicate=None)[source]: A generator of (subject, object) tuples for the given predicate
        #Graph.subject_predicates(object=None)[source]: A generator of (subject, predicate) tuples for the given object
        #Graph.predicate_objects(subject=None)[source]: A generator of (predicate, object) tuples for the given subject
        #
        #testProperty = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasType")
        #for s, p, o in myUBO.triples( (None,  testProperty, None) ):
        #    print "%s hasType %s"%(s,o)
        # Get all triples
        for s, p, o in myUBO.triples( (None,  None, None) ):
            print "%s + %s + %s"%(s,p,o)

        #This is how you get the different types of spatial objects in the graph:
        print "queryUBO:"
        #myUBO.load("RDFout/UBO_RDF.rdf")
        ASpatialObject = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#ASpatialObject")
        SpaceCollectionLocation = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollectionLocation")
        SpaceCollection = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollection")
        Space = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space")
        SpaceBoundary = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundary")
        SpaceBoundaryElement = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundaryElement")
        #for s,p,o in myUBO.triples( (None,  RDF.type, ASpatialObject) ):
        #    print "%s is a %s"%(s,o)
        #for s,p,o in myUBO.triples( (None,  RDF.type, SpaceCollectionLocation) ):
        #    print "%s is a %s"%(s,o)
        #for s,p,o in myUBO.triples( (None,  RDF.type, SpaceCollection) ):
        #    print "%s is a %s"%(s,o)
        #for s,p,o in myUBO.triples( (None,  RDF.type, Space) ):
        #    print "%s is a %s"%(s,o)
        #for s,p,o in myUBO.triples( (None,  RDF.type, SpaceBoundary) ):
        #    print "%s is a %s"%(s,o)
        #for s,p,o in myUBO.triples( (None,  RDF.type, SpaceBoundaryElement) ):
        #    print "%s is a %s"%(s,o)
        #for s, p, o in myUBO.triples( (None,  None, None) ):
        #    # Map to UBO to know what shape to transform this into:
        #    print "%s + %s + %s"%(s,p,o)



        # Trying to get "Lat, Long, Elevation" for now for first level, second will be area, rest will be normal
        #print "\nTry to get test coordinates for 3D string processing:"
        #SBE1 = URIRef("SpaceBoundaryElement1:MaterialData3D")
        #SBE1hasValue = URIRef(":hasValue")
        #SBE1hasType = URIRef(":hasType")
        #for s, p, o in myUBO.triples( (None,  SBE1hasType, None) ):
        #    print "%s + %s + %s"%(s,p,o)\

        #test1 = Literal("Latitude")
        #for s, p, o in myUBO.triples( (None,  None, test1) ):
        #    print "%s + %s + %s"%(s,p,o)

        # Lat, Long, and Elev are a special case of this ontology, they occur once per root spatial thing, or more if ontology changes
        LatLongElev = "("
        turi = URIRef('http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasValue')
        for row in myUBO.query("""SELECT ?name
                      WHERE { ?x ?p ?name .
                              ?x ?y "Latitude" .}""",
                   initBindings={'p' : turi}):
            #print row[0]
            value = str(row[0])
            LatLongElev += (value + ", ")
        for row in myUBO.query("""SELECT ?name
                      WHERE { ?x ?p ?name .
                              ?x ?y "Longitude" .}""",
                   initBindings={'p' : turi}):
            #print row[0]
            value = str(row[0])
            LatLongElev += (value + ", ")
        for row in myUBO.query("""SELECT ?name
                      WHERE { ?x ?p ?name .
                              ?x ?y "Elevation" .}""",
                   initBindings={'p' : turi}):
            #print row[0]
            value = str(row[0])
            LatLongElev += (value + ")")
        #print "LatLongElev ", LatLongElev

        # SpaceCollectionLocation Level Data Collection, assuming all polygons at this time (Add Location Lat, Long, Elev)
        shapeType = "point"
        p1 = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#ASpatialObject:hasSpatialCollectionLocationMember")
        instanceCountForCollectionA = 0
        for s, p, o in myUBO.triples( (None,  p1, None) ):
            instanceCountForCollectionA += 1
        #print "instanceCountForCollection", instanceCountForCollectionA
        instanceCountForCollectionB = 0
        for s, p, o in myUBO.triples( (None,  p1, None) ):
            #print "%s + %s + %s"%(s,p,o)

            # Map to UBO to know what shape to transform this into:
            coors = self.processUBOtoOGCcoordinates(LatLongElev, "LatLongElev", "OGC_polygon")
            #print "coors", coors

            # Then Assemble OGC file parts with those coordinates
            instanceCountForCollectionB += 1
            aso = "ASpatialObject:"
            s = str(s)
            p = str(p)
            o = str(o)
            sList = s.split(base)
            sList = sList[1].split(aso)
            #print "sList ",sList[0]
            pList = p.split(base)
            pList = pList[1].split(aso)
            #print "pList ",pList[1]
            oList = o.split(base)
            oList = oList[1].split(aso)
            #print "oList ",oList[0]
            #print "Lists:", sList[0], pList[1], oList[0]
            OGCsectionTop = ""
            OGCsectionEnd = ""
            if instanceCountForCollectionB == 1:
                OGCsectionTop = self.makeOGCtop(sList[0], OGC_file_parts, instanceCountForCollectionB)
                OGCsectionEnd = self.makeOGCend(OGC_file_parts, instanceCountForCollectionB)
            OGCsectionMid = self.makeOGCmid(OGC_file_parts, instanceCountForCollectionB, pList[1], oList[0])
            OGCsectionShapes = self.makeOGCshp(OGC_file_parts, instanceCountForCollectionB, shapeType, oList[0], coors)
            #print "test shapes: ", OGCsectionShapes

            # Add parts to the OGC file in the proper order
            current_OGC_RDF = self.addOGCSection(current_OGC_RDF, OGCsectionTop, OGCsectionMid, OGCsectionEnd, OGCsectionShapes)
            #print "current_OGC_RDF: ", current_OGC_RDF


        # SpaceCollection Level Data Collection, assuming all polygons at this time
        shapeType = "point"
        p3 = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollectionLocation:hasSpaceCollectionMember")
        typ = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasType")
        val = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasValue")
        tp = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        p2 = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollection:hasProperty")
        smd = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceMassingData")
        SpaceMassingDataCount = 0

        # Query myUBO for this Element's Data
        for s, p, o in myUBO.triples( (None,  p3, None) ):
            #print "%s + %s + %s"%(s,p,o)
            SpaceMassingDataCount += 1
            #http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollection + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollection:hasProperty + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceMassingData
            #http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property4 + http://www.w3.org/1999/02/22-rdf-syntax-ns#type + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceMassingData
            #http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property4 + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasType + Area; hasValue + 200.0
            prop_val_str = ""
            if SpaceMassingDataCount > 1:
                print "SpaceMassingDataCount > 1, and is assumed to be a single instance!"
            else:
                for row in myUBO.query("""SELECT ?name ?t1 ?v1
                          WHERE { ?name ?tp ?smd .
                                  ?name ?typ ?t1 .
                                  ?name ?val ?v1 .}""",
                       initBindings={'tp' : tp, 'smd' : smd, 'typ' : typ, 'val' : val}):
                    #print "myrow: ", row
                    prop = row[0]
                    prop_type = row[1]  # Area for this schema is assumed to be sq. ft for now
                    prop_val = row[2]
                    #prop_unit = row[2][0]  # ?
                    prop_val_str = "(" + str(prop_val) + ", 0, 0)"
                    #print "prop_val_str: ", prop_val_str

            # Map to UBO to know what shape to transform this into:
            coors = self.processUBOtoOGCcoordinates(prop_val_str, "Area", "OGC_polygon")
            #print "coors", coors

            # Then Assemble OGC file parts with those coordinates
            aso = ":"
            s = str(s)
            p = str(p)
            o = str(o)
            sList = s.split(base)
            sList = sList[1].split(aso)
            #print "sList ",sList[0]
            pList = p.split(base)
            pList = pList[1].split(aso)
            #print "pList ",pList[1]
            oList = o.split(base)
            oList = oList[1].split(aso)
            #print "oList ",oList[0]
            #print "Lists:", sList[0], pList[1], oList[0]

            OGCsectionTop = ""
            OGCsectionEnd = ""
            if SpaceMassingDataCount == 1:
                OGCsectionTop = self.makeOGCtop(sList[0], OGC_file_parts, SpaceMassingDataCount)
                OGCsectionEnd = self.makeOGCend(OGC_file_parts, SpaceMassingDataCount)
            OGCsectionMid = self.makeOGCmid(OGC_file_parts, SpaceMassingDataCount, pList[1], oList[0])
            OGCsectionShapes = self.makeOGCshp(OGC_file_parts, SpaceMassingDataCount, shapeType, oList[0], coors)
            #print OGCsectionShapes

            # Add parts to the OGC file in the proper order
            current_OGC_RDF = self.addOGCSection(current_OGC_RDF, OGCsectionTop, OGCsectionMid, OGCsectionEnd, OGCsectionShapes)
            #print "current_OGC_RDF: ", current_OGC_RDF


        # Space Level Data Collection, assuming all polygons at this time
        # #SpaceCollectionLocation + #SpaceCollectionLocation:hasSpaceCollectionMember + #SpaceCollection1
        # #SpaceCollection1 + #SpaceCollection:hasSpaceMember + #Space1
        #print "Trying next level: "
        shapeType = "polygon"
        p4 = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollection:hasSpaceMember")
        typ = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasType")
        val = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasValue")
        tp = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        spc = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space")
        prp = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space:hasProperty")
        SpaceDataCount = 0

        # Query myUBO for this Element's Data
        curr_sp_set = list()
        for s, p, o in myUBO.triples( (None,  p4, None) ):
            #print "%s + %s + %s"%(s,p,o)
            SpaceDataCount += 1
            # #SpaceCollection1 + #SpaceCollection:hasSpaceMember + #Space1
            # #Space1 + http://www.w3.org/1999/02/22-rdf-syntax-ns#type + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space
            # #Space + #Space:hasProperty + #SpaceData
            # #Property5 + http://www.w3.org/1999/02/22-rdf-syntax-ns#type + #SpaceData
            # #Space1 + #Space:hasProperty + #Property5
            # #Property5 + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Property:hasType + Coordinates
            # #Property5 + #Property:hasValue + [(-18.0722, 2.497701, 0.0), (-22.48886, 10.14759, 0.0), ...

            prop_val_str = ""
            OGCsectionTop = ""
            OGCsectionEnd = ""
            OGCsectionMid = ""
            OGCsectionShapes = ""
            # Loop for each Defined Space found:
            for row in myUBO.query("""SELECT ?name ?propNum ?t1 ?v1
                    WHERE { ?name ?tp ?spc .
                            ?name ?prp ?propNum .
                            ?propNum ?typ ?t1 .
                            ?propNum ?val ?v1 .}""",
                    initBindings={'p4' : p4, 'typ' : typ, 'val' : val, 'tp' : tp}):
                #print "myrow: ", row
                # For each Space entity found, create an entry for the OGC
                cur_space = row[0]
                cur_space_prop_num = row[1]
                cur_space_data_type = str(row[2])
                prop_val_str = str(row[3])

                # Map to UBO to know what shape to transform this into:
                coors = self.processUBOtoOGCcoordinates(prop_val_str, "UBO_polygon", "OGC_polygon")
                #print "coors", coors

                # Then Assemble OGC file parts with those coordinates
                aso = ":"
                s = str(s)
                p = str(p)
                o = str(o)
                sList = s.split(base)
                sList = sList[1].split(aso)
                #print "sList ",sList[0]
                pList = p.split(base)
                pList = pList[1].split(aso)
                #print "pList ",pList[1]
                oList = o.split(base)
                oList = o.split("#")
                oList = oList[1].split(aso)
                #print "oList ",oList[0]
                #print "Lists:", sList[0], pList[1], oList[0]

                if SpaceDataCount == 1:
                    OGCsectionTop = self.makeOGCtop(sList[0], OGC_file_parts, SpaceDataCount)
                    OGCsectionEnd = self.makeOGCend(OGC_file_parts, SpaceDataCount)
                    OGCsectionMid = self.makeOGCmid(OGC_file_parts, SpaceDataCount, pList[1], oList[0])
                    OGCsectionShapes = self.makeOGCshp(OGC_file_parts, SpaceDataCount, shapeType, oList[0], coors)
                else:
                    OGCsectionMid = OGCsectionMid + self.makeOGCmid(OGC_file_parts, SpaceDataCount, pList[1], oList[0])
                    OGCsectionShapes = OGCsectionShapes + self.makeOGCshp(OGC_file_parts, SpaceDataCount, shapeType, oList[0], coors)
                    #print OGCsectionShapes

                # Also want to keep an in-memory list of levels of graph additions for reference in next collections
                curr_sp_set.append(base + oList[0])
                #print "OGC_file_parts", base + oList[0]
                # Now next level data can be in a different section instead of nested loops

            # Add parts to the OGC file in the proper order
            current_OGC_RDF = self.addOGCSection(current_OGC_RDF, OGCsectionTop, OGCsectionMid, OGCsectionEnd, OGCsectionShapes)
            #print "current_OGC_RDF: ", current_OGC_RDF


        # Surface Level Data Collection, assuming all polygons at this time
        # #Space1 + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space:hasSpaceBoundaryMember + #SpaceBoundary2
        #print "Trying next level: "
        shapeType = "polygon"
        p5 = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space:hasSpaceBoundaryMember")
        typ = URIRef(":hasType")
        val = URIRef(":hasValue")
        tp = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        sb = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundary")
        prp = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space:hasProperty")
        spc = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space")
        sthreed = URIRef("3DSurfaceCoordinates")
        stwod = URIRef("2DSurfaceCoordinates")
        SurfDataCount2d = 0
        SurfDataCount3d = 0
        foundSurfFlag = 0
        #SpaceDataCount = 0

        # Query myUBO for this Element's Data
        curr_su2d_set = list()
        curr_su3d_set = list()
        #for s, p, o in myUBO.triples( (None,  p5, None) ):
        #print "curr set from above: ", curr_sp_set
        for curr_sp in curr_sp_set:
            curr_sp = "#" + curr_sp.split(base)[1]
            OGCsectionTop = ""
            OGCsectionEnd = ""
            OGCsectionMid = ""
            OGCsectionShapes = ""
            #SpaceDataCount += 1
            prop_val_str = ""
            # Loop for each Defined Space found:
            # #SpaceBoundary2 + #SpaceBoundary2:hasProperty + #SpaceBoundary2:SurfaceData3D
            # #SpaceBoundary2 + #SpaceBoundary2:hasProperty + #SpaceBoundary2:SurfaceData2D
            # #SpaceBoundary2:SurfaceData3D + :hasValue + [(-24.853176930510426, 9.4561328552625969, 0.0), ...]
            # #SpaceBoundary2:SurfaceData3D + :hasType + 3DSurfaceCoordinates
            # #SpaceBoundary2:SurfaceData2D + :hasValue + [(-4.853176930510426, 3.4561328552625969, 0.0), ...]
            # #SpaceBoundary2:SurfaceData2D + :hasType + 2DSurfaceCoordinates
            for row in myUBO.query("""SELECT ?name ?x
                    WHERE { ?x ?p5 ?name .
                           }""",
                    initBindings={'p5' : p5}):
                # Pull the polygons associated with the current space
                if str(row[1]) == str(curr_sp):
                    SurfDataCount2d += 1
                    SurfDataCount3d += 1
                    #print "myrow: ", row
                    #su = str(row[0]).split("#")[1]
                    #sp = str(row[1]).split("#")[1]
                    r0 = str(row[0])  # Surface number
                    r1 = str(row[1])  # Space number
                    twoDData = str(r0 + ":SurfaceData2D")
                    twoDData = URIRef(twoDData)
                    threeDData = str(r0 + ":SurfaceData3D")
                    threeDData = URIRef(threeDData)
                    propt = URIRef(r0 + ":hasProperty")
                    for rowb in myUBO.query("""SELECT ?name ?twoDData ?x ?vals
                            WHERE { ?name ?tp ?sb .
                                    ?name ?propt ?twoDData .
                                    ?twoDData ?typ ?x .
                                    ?twoDData ?val ?vals .
                                   }""",
                            initBindings={'typ' : typ, 'val' : val, 'tp' : tp, 'propt' : propt, 'twoDData' : twoDData,'threeDData' : threeDData}):
                        #print "rowb", rowb
                        # 0 = surf, 1 = surfData2D, 2 = 2DsurfCoor, 3 = coor2Dvals

                        # Map to UBO to know what shape to transform this into:
                        coors = self.processUBOtoOGCcoordinates(rowb[3], "UBO_polygon", "OGC_polygon")
                        #print "coors", coors

                        # Then Assemble OGC file parts with those coordinates
                        aso = ":"
                        asp = "#"
                        s = str(r1)
                        p = str(p5)
                        o = str(rowb[1])
                        sList = s.split(base)
                        sList = sList[0].split(asp)
                        sList = sList[1].split(aso)
                        #print "sList ",sList[0]
                        pList = p.split(base)
                        pList = pList[1].split(aso)
                        #print "pList ",pList[1]
                        oList = o.split(base)
                        oList = oList[0].split(asp)
                        #print "oList ",oList[0]
                        #print "Lists:", sList[0], pList[1], oList[1]

                        if SurfDataCount2d == 1 and foundSurfFlag == 0:
                            OGCsectionTop = self.makeOGCtop(sList[0], OGC_file_parts, SurfDataCount2d)
                            OGCsectionEnd = self.makeOGCend(OGC_file_parts, SurfDataCount2d)
                            OGCsectionMid = self.makeOGCmid(OGC_file_parts, SurfDataCount2d, pList[1], oList[1])
                            OGCsectionShapes = self.makeOGCshp(OGC_file_parts, SurfDataCount2d, shapeType, oList[1], coors)
                            foundSurfFlag = 1
                        else:
                            OGCsectionMid = str(OGCsectionMid + self.makeOGCmid(OGC_file_parts, SurfDataCount2d, pList[1], oList[1]))
                            OGCsectionShapes = str(OGCsectionShapes + self.makeOGCshp(OGC_file_parts, SurfDataCount2d, shapeType, oList[1], coors))

                        # Also want to keep an in-memory list of levels of graph additions for reference in next collections
                        new_pair = str(r1), str(base + oList[1])
                        curr_su2d_set.append(new_pair)
                        #print "OGC_file_parts", base + oList[0]
                        # Now next level data can be in a different section instead of nested loops


                    for rowc in myUBO.query("""SELECT ?name ?threeDData ?x ?vals
                            WHERE { ?name ?tp ?sb .
                                    ?name ?propt ?threeDData .
                                    ?threeDData ?typ ?x .
                                    ?threeDData ?val ?vals .
                                   }""",
                            initBindings={'typ' : typ, 'val' : val, 'tp' : tp, 'propt' : propt, 'twoDData' : twoDData,'threeDData' : threeDData}):
                        #print "rowc", rowc
                        # 0 = surf, 1 = surfData3D, 2 = 3DsurfCoor, 3 = coor3Dvals

                        # Map to UBO to know what shape to transform this into:
                        coors = self.processUBOtoOGCcoordinates(rowc[3], "UBO_polygon", "OGC_polygon")
                        #print "coors", coors

                        # Then Assemble OGC file parts with those coordinates
                        aso = ":"
                        asp = "#"
                        s = str(r1)
                        p = str(p5)
                        o = str(rowc[1])
                        sList = s.split(base)
                        sList = sList[0].split(asp)
                        sList = sList[1].split(aso)
                        #print "sList ",sList[0]
                        pList = p.split(base)
                        pList = pList[1].split(aso)
                        #print "pList ",pList[1]
                        oList = o.split(base)
                        oList = oList[0].split(asp)
                        #print "oList ",oList[0]
                        #print "Lists:", sList[0], pList[1], oList[1]

                        if SurfDataCount3d == 1 and foundSurfFlag == 0:
                            OGCsectionTop = self.makeOGCtop(sList[0], OGC_file_parts, SurfDataCount3d)
                            OGCsectionEnd = self.makeOGCend(OGC_file_parts, SurfDataCount3d)
                            OGCsectionMid = self.makeOGCmid(OGC_file_parts, SurfDataCount3d, pList[1], oList[1])
                            OGCsectionShapes = self.makeOGCshp(OGC_file_parts, SurfDataCount3d, shapeType, oList[1], coors)
                            foundSurfFlag = 1
                        else:
                            OGCsectionMid = str(OGCsectionMid + self.makeOGCmid(OGC_file_parts, SurfDataCount3d, pList[1], oList[1]))
                            OGCsectionShapes = str(OGCsectionShapes + self.makeOGCshp(OGC_file_parts, SurfDataCount3d, shapeType, oList[1], coors))
                            #print OGCsectionShapes

                        # Also want to keep an in-memory list of levels of graph additions for reference in next collections
                        new_pair = str(r1), str(base + oList[1])
                        curr_su3d_set.append(new_pair)
                        #print "OGC_file_parts", base + oList[0]
                        # Now next level data can be in a different section instead of nested loops

            # Add parts to the OGC file in the proper order
            current_OGC_RDF = self.addOGCSection(current_OGC_RDF, OGCsectionTop, OGCsectionMid, OGCsectionEnd, OGCsectionShapes)
            #print "current_OGC_RDF: ", current_OGC_RDF


        # Sub-Surface Level Data Collection, assuming all polygons at this time (i.e. material data in the gbxml case)
        # #SpaceBoundary5 + http:...#Space:hasSpaceBoundaryElementMember + #SpaceBoundaryElement19
        # #SpaceBoundaryElement19 + http://www.w3.org/1999/02/22-rdf-syntax-ns#type + http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundaryElement
        # #SpaceBoundaryElement19 + #SpaceBoundaryElement22:hasProperty + #SpaceBoundaryElement22:MaterialData3D
        # #SpaceBoundaryElement22:MaterialData3D + :hasType + 3DElementCoordinates
        # #SpaceBoundaryElement22:MaterialData3D + :hasValue + [(-24.082560000000001, 10.574619999999999,...]
        print "Trying next level: "
        shapeType = "polygon"
        p6 = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space:hasSpaceBoundaryElementMember")
        typ = URIRef(":hasType")
        val = URIRef(":hasValue")
        tp = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        sb = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundary")
        sbe = URIRef("http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundaryElement")
        elem = URIRef("3DElementCoordinates")

        # Query myUBO for this Element's Data
        #curr_su2d_set2 = list()
        #curr_su3d_set2 = list()
        ElementCount = 0
        element_set = list()
        # This is the set of previous 3D surface data, so each will break down into further elements
        for b in curr_su3d_set:
            # For each boundary, get associated elements
            curr_b = "#" + b[1].split(base)[1]
            curr_b = curr_b.split(":")[0]
            curr_b = URIRef(curr_b)
            #SpaceDataCount += 1
            prop_val_str = ""
            OGCsectionTop = ""
            OGCsectionEnd = ""
            OGCsectionMid = ""
            OGCsectionShapes = ""
            ElementCount = 0
            # Loop for each Element found:
            for row in myUBO.query("""SELECT ?x
                    WHERE { ?curr_b ?p6 ?x .
                           }""",
                    initBindings={'p6' : p6, 'curr_b' : curr_b}):
                #print "rows here", curr_b, row
                ElementCount += 1
                r0 = str(row[0])  # row[0] = SpaceBoundaryElement#
                r0 = URIRef(r0)
                curr_b = str(curr_b)  # SpaceBoundary number
                curr_b = URIRef(curr_b)
                threeDData = str(r0 + ":MaterialData3D")
                threeDData = URIRef(threeDData)
                propt = URIRef(r0 + ":hasProperty")
                for rowb in myUBO.query("""SELECT ?vals
                        WHERE { ?r0 ?propt ?threeDData .
                                ?threeDData ?typ ?x .
                                ?threeDData ?val ?vals .
                               }""",
                        initBindings={'typ' : typ, 'val' : val, 'tp' : tp, 'propt' : propt, 'threeDData' : threeDData, 'sbe' : sbe, 'curr_b' : curr_b, 'r0' : r0}):
                    # 0 = surf, 1 = surfData2D, 2 = 2DsurfCoor, 3 = coor2Dvals
                    #print "rowb", rowb[0]

                    # Map to UBO to know what shape to transform this into:
                    coors = self.processUBOtoOGCcoordinates(rowb[0], "UBO_polygon", "OGC_polygon")
                    #print "coors", coors

                    # Then Assemble OGC file parts with those coordinates
                    aso = ":"
                    asp = "#"
                    s = str(curr_b)
                    p = str(p6)
                    o = str(r0)
                    sList = s.split(base)
                    sList = sList[0].split(asp)
                    sList = sList[1].split(aso)
                    #print "sList ",sList[0]
                    pList = p.split(base)
                    pList = pList[1].split(aso)
                    #print "pList ",pList[1]
                    oList = o.split(base)
                    oList = oList[0].split(asp)
                    #print "oList ",oList[0]
                    #print "Lists:", sList[0], pList[1], oList[1]

                    if ElementCount == 1:
                        OGCsectionTop = self.makeOGCtop(sList[0], OGC_file_parts, ElementCount)
                        OGCsectionEnd = self.makeOGCend(OGC_file_parts, ElementCount)
                        OGCsectionMid = self.makeOGCmid(OGC_file_parts, ElementCount, pList[1], oList[1])
                        OGCsectionShapes = self.makeOGCshp(OGC_file_parts, ElementCount, shapeType, oList[1], coors)
                    else:
                        OGCsectionMid = str(OGCsectionMid + self.makeOGCmid(OGC_file_parts, ElementCount, pList[1], oList[1]))
                        OGCsectionShapes = str(OGCsectionShapes + self.makeOGCshp(OGC_file_parts, ElementCount, shapeType, oList[1], coors))
                        #print OGCsectionShapes

                    # Also want to keep an in-memory list of levels of graph additions for reference in next collections
                    element_set.append(base + oList[1])
                    #print element_set
                    # Now next level data can be in a different section instead of nested loops

            # Add parts to the OGC file in the proper order
            current_OGC_RDF = self.addOGCSection(current_OGC_RDF, OGCsectionTop, OGCsectionMid, OGCsectionEnd, OGCsectionShapes)
            #print "current_OGC_RDF: ", current_OGC_RDF


        # Note: There will be adjustments to this processing as other models are tested
        self.create_OGC_rdf_file(current_OGC_RDF)

        return current_OGC_RDF

    def addOGCSection(self, current_OGC_RDF, OGCsectionTop, OGCsectionMid, OGCsectionEnd, OGCsectionShapes):
        # Construct this file section with these keys and insert it here:'<!--beginWriting-->\n'

        newSection = str(OGCsectionTop + OGCsectionMid + OGCsectionEnd + OGCsectionShapes + '\n<!--beginWriting-->\n')
        current_OGC_RDF = current_OGC_RDF.replace('<!--beginWriting-->', newSection)
        #print "current_OGC_RDF: ", current_OGC_RDF

        return current_OGC_RDF

    def processUBOtoOGCcoordinates(self, CoorSetIN, shapeIN, shapeOUT):
        """
        UBOCoorSet = Receive UBOCoorSet in the form of: Literal[(1, 2, 3), (1, 2, 3), (1, 2, 3), (1, 2, 3)]
        shapeIN = type of shape to process into OGC: one of (UBOpolygon, or others added at a later time)
        shapeOUT = type of shape send back: one of (UBOpolygon, or others added at a later time)
        For exmaple, at some point, I may be passing several OGC polygons to make a collection and assume that CoorSetIN is a list of lists instead...etc.
        Need to be in the form of: MultiPolygon(  ((x y z, x y z, x y z, x y z)), ((x y z, x y z, x y z, x y z)), ((x y z, x y z, x y z, x y z))  )
                             GeometryCollection(  POLYGON ((x y z, x y z, x y z, x y z)), POLYGON ((x y z, x y z, x y z, x y z)), POLYGON ((x y z, x y z, x y z, x y z))  )
                                        Polygon(  ((x y z, x y z, x y z, x y z))  )
        """
        #shape = "UBO_polygon"
        #CoorSetIN = "[(1, 2, 3), (4, 5, 6), (7, 8, 9), (1, 4, 8)]"
        OGCtemp = ""
        OGCCoorSet = ""
        CoorSetIN = str(CoorSetIN) # Typecast Literal to make sure it is a String
        foundFlag = 0

        if shapeIN == "UBO_polygon" and shapeOUT == "OGC_polygon":
            foundFlag = 1
            # So it will assume that the coordinate set passed in is a list of x,y,z points
            x = None
            y = None
            z = None
            l = len(CoorSetIN)
            CoorSetIN = CoorSetIN[2:l-2]
            coorList = CoorSetIN.split('), (')
            for item in coorList:
                xyzList = item.split(',')
                if not xyzList[0] in item:
                    raise Exception("x Value not found in Polygon from OGCqueryNfill.py!!")
                if not xyzList[1] in item:
                    raise Exception("y Value not found in Polygon from OGCqueryNfill.py!!")
                if not xyzList[2] in item:
                    raise Exception("z Value not found in Polygon from OGCqueryNfill.py!!")
                x = xyzList[0]
                y = xyzList[1]
                z = xyzList[2]
                CoorSet = str( x + " " + y + " " + z + ", ")
                OGCtemp = OGCtemp + CoorSet
            g = len(OGCtemp)
            OGCtemp = OGCtemp[0:g-2]
            OGCCoorSet = ( "((" + OGCtemp + "))" )
            #print OGCCoorSet

        if shapeIN == "LatLongElev" and shapeOUT == "OGC_polygon":
            # This means at the top level we are recording the one time instance of triples for lat, long, and elev
            foundFlag = 1
            OGCCoorSet = CoorSetIN

        if shapeIN == "Area" and shapeOUT == "OGC_polygon":
            # This means at the top level we are recording the one time instance of triples for lat, long, and elev
            foundFlag = 1
            OGCCoorSet = CoorSetIN

        if foundFlag == 0:
            OGCCoorSet = None
            print "Shape type not yet handled from OGCqueryNfill.py!!"

        return OGCCoorSet

    def makeOGCshp(self, OGC_file_parts, i, shapeType, oList, coors):
        # OGC_file_parts[] : Polygon, Point, LineString, top1, top2, top3
        # Set up the beginning tags by replacing variable portions of the tuple
        newShp1 = ''
        counter = 0
        #print top1, type(top1).__name__
        if shapeType == "point":
            point = OGC_file_parts['Point']
            for x in point:
                if x == 'variable' and counter == 0:
                    counter = 1
                    #x = str(i)
                    x = ""
                if x == 'variable' and counter == 1:
                    x = oList
                if x == 'processedCoors':
                    x = coors
                newShp1 = newShp1 + x
        elif shapeType == "polygon":
            point = OGC_file_parts['Polygon']
            for x in point:
                if x == 'variable' and counter == 0:
                    counter = 1
                    #x = str(i)
                    x = ""
                if x == 'variable' and counter == 1:
                    x = oList
                if x == 'processedCoors':
                    x = coors
                newShp1 = newShp1 + x
        else:
            print "Shape Type Not Yet Handled"
        newShp1 = str(newShp1)
        #print newShp1

        return newShp1

    def makeOGCmid(self, OGC_file_parts, i, pList, oList):
        # OGC_file_parts[] : Polygon, Point, LineString, top1, top2, top3
        # Set up the middle tags by replacing variable portions of the tuple
        #topmid = ('\t<my:', variable, ' rdf:resource="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#', variable,  '\n')
        newMid1 = ''
        counter = 0
        top2 = OGC_file_parts['top2']
        #print top1, type(top1).__name__
        for x in top2:
            if x == 'variable' and counter == 0:
                counter = 1
                x = pList
            if x == 'variable' and counter == 1:
                #x = (str(i) + oList)
                x = (oList)
            newMid1 = newMid1 + x
        #print newMid1

        return newMid1

    def makeOGCend(self, OGC_file_parts, i):
        # Set up the ending tags by replacing variable portions of the tuple
        #topend = ('</my:ASpatialObject>\n')
        newEnd1 = OGC_file_parts['top3']
        #print newEnd1

        return newEnd1

    def makeOGCtop(self, sList, OGC_file_parts, i):
        # Set up the beginning tags by replacing variable portions of the tuple
        #topstart = ('<!-- Comment -->\n', '<my:ASpatialObject rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#', variable, variable, '">\n')
        newTop1 = ''
        counter = 0
        top1 = OGC_file_parts['top1']
        #print top1, type(top1).__name__
        for x in top1:
            if x == 'variable' and counter == 0:
                counter = 1
                #x = str(i)
                x = ""
            if x == 'variable' and counter == 1:
                x = sList
            newTop1 = newTop1 + x
        #print newTop1

        return newTop1

    def create_OGC_rdf_file(self, current_OGC_RDF):
        with open('OGC_output.rdf','w') as myfile:
            myfile.write(current_OGC_RDF)

        return

