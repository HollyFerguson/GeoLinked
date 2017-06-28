#-------------------------------------------------------------------------------
# Name:        OGCtemplate2.py
# Purpose:     Create OGC GeoSPARQL File Template using UBO classes and properties
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     07/31/2015
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


class OGCtemplate2():
    # Input parameters
    #variable = ""


    def createOGCtemplate2(self, base):
        """
        Define parts of the file and how they correspond to the UBO ontology in a dictionary
        Based on definitions in PDF document for Figure 3: Illustration of spatial data
        From Figure 3 in standard documentation: http://www.opengeospatial.org/standards/geosparql and the simple feature documentation
        OGC Simple features uses x,y,z,m = lat,long,elev,measures
        """

        # Create the header for the OGC RDF file
        OGC_RDF_header = self.createHeader2(base)

        # Create OGC_file_parts = dict()
        OGC_file_parts = self.file_parts2()

        return OGC_RDF_header, OGC_file_parts

    def createHeader2(self, base):
        header = (
        '<rdf:RDF\n'
        '\txmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
        '\txmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n'
        '\txmlns:owl="http://www.w3.org/2002/07/owl#"\n'
        '\txmlns:sf="http://www.opengis.net/ont/sf#"\n'
        '\txmlns:geo="http://www.opengis.net/ont/geosparql#"\n'
        '\txmlns:my="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#"\n' # Using UBO as the schema...
        '\txmlns:ubo=' + base + '>\n\n')

        properties = (
        '<!-- Integration with GeoSPARQL classes and properties: Check and Revise Later! -->\n'
        '<rdfs:Class rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#ASpatialObject">\n'
            '\t<rdfs:subClassOf rdf:resource="http://www.opengis.net/ont/geosparql#Feature"/>\n'
        '</rdfs:Class>\n'
        '<rdfs:Class rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollectionLocation">\n'
            '\t<rdfs:subClassOf rdf:resource="http://www.opengis.net/ont/geosparql#Feature"/>\n'
        '</rdfs:Class>\n'
        '<rdfs:Class rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceCollection">\n'
            '\t<rdfs:subClassOf rdf:resource="http://www.opengis.net/ont/geosparql#Feature"/>\n'
        '</rdfs:Class>\n'
        '<rdfs:Class rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#Space">\n'
            '\t<rdfs:subClassOf rdf:resource="http://www.opengis.net/ont/geosparql#Feature"/>\n'
        '</rdfs:Class>\n'
        '<rdfs:Class rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundary">\n'
            '\t<rdfs:subClassOf rdf:resource="http://www.opengis.net/ont/geosparql#Feature"/>\n'
        '</rdfs:Class>\n'
        '<rdfs:Class rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#SpaceBoundaryElement">\n'
            '\t<rdfs:subClassOf rdf:resource="http://www.opengis.net/ont/geosparql#Feature"/>\n'
        '</rdfs:Class>\n'

        '<rdf:Property rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#hasSpatialCollectionLocationMember">\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasDefaultGeometry"/>\n'
        '</rdf:Property>\n'
        '<rdf:Property rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#hasSpaceCollectionMember">\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasDefaultGeometry"/>\n'
        '</rdf:Property>\n'
        '<rdf:Property rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#hasSpaceMember">\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasDefaultGeometry"/>\n'
        '</rdf:Property>\n'
        '<rdf:Property rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#hasSpaceBoundaryMember">\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasDefaultGeometry"/>\n'
        '</rdf:Property>\n'
        '<rdf:Property rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#hasSpaceBoundaryElementMember">\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasDefaultGeometry"/>\n'
        '</rdf:Property>\n'

        '<rdf:Property rdf:about="http://example.org/ApplicationSchema#hasExactGeometry">\n'
        '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>\n'
        '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasDefaultGeometry"/>\n'
        '</rdf:Property>\n'
        '<rdf:Property rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#hasPointGeometry">\n'
            '\t<rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>\n'
        '</rdf:Property>\n\n'
        )

        beginWriting = ('\n<!--beginWriting-->\n')

        footer = ('</rdf:RDF>\n')

        OGC_RDF_file = header + properties + beginWriting + footer
        #print OGC_RDF_file

        return OGC_RDF_file

    def file_parts2(self):

        #OGC_file_parts contains file sections for the known types of geometries that can include:
        pnt = "Point"
        ln = "LineString"
        poly = "Polygon"
        comment = "comment"
        variable = "variable"
        processedCoors = "processedCoors"

        """
        <!-- Comment -->
        <my:PlaceOfInterest rdf:about="http://example.org/ApplicationSchema#C">
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#CExactGeom"/>
            <my:hasPointGeometry rdf:resource="http://example.org/ApplicationSchema#CPointGeom"/>
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#EExactGeom"/>
        </my:PlaceOfInterest>
        """
        top1 = "top1"
        top2 = "top2"
        top3 = "top3"
        topstart = ('<!-- Comment -->\n', '<my:ASpatialObject rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#', variable, variable, '">\n')
        topmid = ('\t<my:', variable, ' rdf:resource="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#', variable,  '\n')
        topend = ('</my:ASpatialObject>\n')

        polygon = (
        '<sf:Polygon', ' rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#', variable, variable, '">\n'
            '\t<geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">\n'
                '\t\t<![CDATA[\n'
                    '\t\t\t<http://www.opengis.net/def/crs/OGC/1.3/CRS84>\n'
                    '\t\t', 'Polygon', processedCoors, '\n'
                '\t\t]]>\n'
            '\t</geo:asWKT>\n'
        '</sf:Polygon', '>\n')

        point = (
        '<sf:Point', ' rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#', variable, variable, '">\n'
            '\t<geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">\n'
                '\t\t<![CDATA[\n'
                    '\t\t\t<http://www.opengis.net/def/crs/OGC/1.3/CRS84>\n'
                    '\t\t\t', 'Point', processedCoors, '\n'
                '\t\t]]>\n'
            '\t</geo:asWKT>\n'
        '</sf:Point', '>\n')

        line = (
        '<sf:Line', ' rdf:about="http://www.semanticweb.org/hfergus2/ontologies/2015/UBO#', variable, variable, '">\n'
            '\t<geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">\n'
                '\t\t<![CDATA[\n'
                    '\t\t\t<http://www.opengis.net/def/crs/OGC/1.3/CRS84>\n'
                    '\t\t\t', 'Line', processedCoors, '\n'
                '\t\t]]>\n'
            '\t</geo:asWKT>\n'
        '</sf:Line', '>\n')

        OGC_file_parts = dict()
        OGC_file_parts[pnt] = point
        OGC_file_parts[ln] = line
        OGC_file_parts[poly] = polygon
        OGC_file_parts[top1] = topstart
        OGC_file_parts[top2] = topmid
        OGC_file_parts[top3] = topend

        return OGC_file_parts

        """
        <!-- Other tags that may be useful:
        version: geor:sfEquals, geor:sfDisjoint, geor:sfIntersects, geor:sfTouches, geor:sfCrosses,
                 geor:sfWithin, geor:sfContains, and geor:sfOverlaps.
        -->

        <rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:owl="http://www.w3.org/2002/07/owl#"
            xmlns:sf="http://www.opengis.net/ont/sf#"
            xmlns:geo="http://www.opengis.net/ont/geosparql#"
            xmlns:my="http://example.org/ApplicationSchema#">

        <!-- Integration with GeoSPARQL classes and properties -->
        <rdfs:Class rdf:about="http://example.org/ApplicationSchema#PlaceOfInterest">
            <rdfs:subClassOf rdf:resource="http://www.opengis.net/ont/geosparql#Feature"/>
        </rdfs:Class>

        <rdf:Property rdf:about="http://example.org/ApplicationSchema#hasExactGeometry">
            <rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>
            <rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasDefaultGeometry"/>
        </rdf:Property>
        <rdf:Property rdf:about="http://example.org/ApplicationSchema#hasPointGeometry">
            <rdfs:subPropertyOf rdf:resource="http://www.opengis.net/ont/geosparql#hasGeometry"/>
        </rdf:Property>

        <!-- Instance-level statements -->
        <!-- A -->
        <my:PlaceOfInterest rdf:about="http://example.org/ApplicationSchema#A">
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#AExactGeom"/>
            <my:hasPointGeometry rdf:resource="http://example.org/ApplicationSchema#APointGeom"/>
        </my:PlaceOfInterest>
        <sf:Polygon rdf:about="http://example.org/ApplicationSchema#AExactGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Polygon((-83.6 34.1, -83.2 34.1, -83.2 34.5,-83.6 34.5, -83.6 34.1))
                ]]>
            </geo:asWKT>
        </sf:Polygon>
        <sf:Point rdf:about="http://example.org/ApplicationSchema#APointGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Point(-83.4 34.3)
                ]]>
            </geo:asWKT>
        </sf:Point>

        <!-- B -->
        <my:PlaceOfInterest rdf:about="http://example.org/ApplicationSchema#B">
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#BExactGeom"/>
            <my:hasPointGeometry rdf:resource="http://example.org/ApplicationSchema#BPointGeom"/>
        </my:PlaceOfInterest>
        <sf:Polygon rdf:about="http://example.org/ApplicationSchema#BExactGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Polygon((-83.6 34.1, -83.4 34.1, -83.4 34.3,-83.6 34.3, -83.6 34.1))
                ]]>
            </geo:asWKT>
        </sf:Polygon>
        <sf:Point rdf:about="http://example.org/ApplicationSchema#BPointGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Point(-83.5 34.2)
                ]]>
            </geo:asWKT>
        </sf:Point>

        <!-- C -->
        <my:PlaceOfInterest rdf:about="http://example.org/ApplicationSchema#C">
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#CExactGeom"/>
            <my:hasPointGeometry rdf:resource="http://example.org/ApplicationSchema#CPointGeom"/>
        </my:PlaceOfInterest>
        <sf:Polygon rdf:about="http://example.org/ApplicationSchema#CExactGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Polygon((-83.2 34.3, -83.0 34.3, -83.0 34.5,-83.2 34.5, -83.2 34.3))
                ]]>
            </geo:asWKT>
        </sf:Polygon>
        <sf:Point rdf:about="http://example.org/ApplicationSchema#CPointGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Point(-83.1 34.4)
                ]]>
            </geo:asWKT>
        </sf:Point>

        <!-- D -->
        <my:PlaceOfInterest rdf:about="http://example.org/ApplicationSchema#D">
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#DExactGeom"/>
            <my:hasPointGeometry rdf:resource="http://example.org/ApplicationSchema#DPointGeom"/>
        </my:PlaceOfInterest>
        <sf:Polygon rdf:about="http://example.org/ApplicationSchema#DExactGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Polygon((-83.3 34.0, -83.1 34.0, -83.1 34.2,-83.3 34.2, -83.3 34.0))
                ]]>
            </geo:asWKT>
        </sf:Polygon>
        <sf:Point rdf:about="http://example.org/ApplicationSchema#DPointGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Point(-83.2 34.1)
                ]]>
            </geo:asWKT>
        </sf:Point>

        <!-- E -->
        <my:PlaceOfInterest rdf:about="http://example.org/ApplicationSchema#E">
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#EExactGeom"/>
        </my:PlaceOfInterest>
        <sf:LineString rdf:about="http://example.org/ApplicationSchema#EExactGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    LineString((-83.4 34.0, -83.3 34.3))
                ]]>
            </geo:asWKT>
        </sf:LineString>

        <!-- F -->
        <my:PlaceOfInterest rdf:about="http://example.org/ApplicationSchema#F">
            <my:hasExactGeometry rdf:resource="http://example.org/ApplicationSchema#FExactGeom"/>
        </my:PlaceOfInterest>
        <sf:Point rdf:about="http://example.org/ApplicationSchema#FExactGeom">
            <geo:asWKT rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                <![CDATA[
                    <http://www.opengis.net/def/crs/OGC/1.3/CRS84>
                    Point(-83.4 34.4)
                ]]>
            </geo:asWKT>
        </sf:Point>

        </rdf:RDF>
        """



