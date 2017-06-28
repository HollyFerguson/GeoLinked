#-------------------------------------------------------------------------------
# Name:        Virtuoso_Module.py
# Purpose:     Prepare data for use in Virtuoso and GeoSparql Queries
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     01/15/2017
# Copyright:   (c) Holly Tina Ferguson 2017
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
from osgeo import gdal
from osgeo import ogr
import csv


class Virtuoso_Data():
    # Input parameters
    #variable = ""
    # Named Graph may be how to fill graph and maybe role chains

    def format_data(self, USO_New, CRS, cityGMLdimension, building_ids_dict, tree, namespaces):
        """
        Try to Translate GML Polygons to WKT since building footprints surrounding IFC/GBXML model is needed
        """

        # Example Coordinate Translation GML to WKT
        #gml = '''<gml:Polygon srsName="EPSG:28992" xmlns="http://www.opengis.net/citygml/2.0" gml="http://www.opengis.net/gml"><gml:exterior><gml:LinearRing><gml:posList srsDimension="3">0.0 0.0 0.0 49.0594415864 -22.5648219853 0.0 71.6242635717 26.4946196012 0.0 22.5648219853 49.0594415864 0.0 0.0 0.0 0.0</gml:posList></gml:LinearRing></gml:exterior></gml:Polygon>'''
        #gml = """<gml:Point xmlns:gml="http://www.opengis.net/gml"><gml:coordinates>108420.33,753808.59</gml:coordinates></gml:Point>"""
        #polygon = ogr.CreateGeometryFromGML(gml)
        #print "point: ", polygon
        #wkt = polygon.ExportToWkt()
        #print wkt

        # Clear existing triples for the new ones to be added below
        open("turtle_using_WKT.ttl", 'w').close()

        for row in USO_New.query("""SELECT ?s ?o ?prop ?v
                 WHERE { ?s ?rdf ?o .
                         ?s ?hasProperty ?prop .
                         ?prop ?hasType ?literal .
                         ?prop ?hasValue ?v }""",
            initBindings={'rdf' : RDF.type, 'o' : URIRef("http://www.sw.org/UBO#SpaceCollection"), 'hasProperty' : URIRef("http://www.sw.org/UBO#hasProperty"), 'hasType' : URIRef("http://www.sw.org/UBO#hasType"), 'literal' : Literal("3DSpaceCollectionCoordinates"), 'hasValue' : URIRef("http://www.sw.org/UBO#hasValue")}):
            if len(str(row[3]).split(",")) == 1:
                # Then you have footprint outlines, like square footage of Space Collection in IFC
                footprint = str(row[3]).split(",")[0]
                #if "300.0 240.0 0.0 353.981741438 238.595866361 0.0 355.385875077 292.5776078 0.0 301.404133639 293.981741438 0.0 300.0 240.0 0.0" in str(footprint):
                    #print "here", str(row[0])
                footprint = "<gml:Polygon srsName=" + '"' + CRS + '"' + ' xmlns="http://www.opengis.net/citygml/2.0" gml="http://www.opengis.net/gml"><gml:exterior><gml:LinearRing><gml:posList srsDimension="' + str(cityGMLdimension) + '">' + footprint + "</gml:posList></gml:LinearRing></gml:exterior></gml:Polygon>"
                #print "footprint", type(footprint), footprint
                GMLpolygon = ogr.CreateGeometryFromGML(footprint)
                #print "GMLpolygon", type(footprint), GMLpolygon
                WKTpolygon = GMLpolygon.ExportToWkt()

                # Now that we have a WKT polygon, we can create our Turtle file
                # Un-comment once results section is done, use results from turtle_query_Results.csv
                #turtle_using_WKT = self.WKT_to_TTL(WKTpolygon, str(row[0]))

            if len(str(row[3]).split(",")) == 2:
                # Then you have footprint outlines AND roof outlines
                print "can add semantics for roof line as well"

        # Go do the SPARQL query in GraphDB or Virtuoso
        # Working, but manually inserting into GraphDB and running queries from there for now...

        # Get back a subset of Buildings, hopefully, and based on that add in the GML_IDs and dig up the Elevations
        # Also build in the GML_IDs for each space collection to demo the cross-mapping to footprint
        query_results_file = "turtle_query_Results.csv"
        new_data_set_building_level = self.get_elevation_map(query_results_file, building_ids_dict, tree, namespaces, USO_New)

        # Visualize the differences here somehow with the given IFC used as one of the buildings
        # For now, will create a CityGML of the subset of buildings from the query to view - I used Aristoteles
        self.create_sub_citygml(new_data_set_building_level)

        # Cross mapping of semantics maybe?
        # Add this all to the SWJ paper

        return

    def get_elevation_map(self, query_results_file, building_ids_dict, tree, namespaces, USO_New):

        GMLdict = dict()
        bldg_possibilities = tree.xpath("/city:CityModel/city:cityObjectMember/bldg:Building", namespaces=namespaces)
        for d in bldg_possibilities:
            GMLdict[str(d)] = d.get('{http://www.opengis.net/gml}id')
            #print d, GMLdict[str(d)]

        # So from the query results, gather the data related to only the buildings that were within query radius
        # Manually omitting the first row of column headers
        new_data_set_building_level = dict()
        with open(query_results_file, 'rb') as csvfile:
            results_lines = csv.reader(csvfile, delimiter=',')
            for row in results_lines:
                my_key = URIRef(row[0])
                b_addr = str(building_ids_dict[my_key][0])
                GMLID =  GMLdict[b_addr]
                bldg_data = ( building_ids_dict[my_key][0], building_ids_dict[my_key][1], row[1], row[3], GMLID )
                new_data_set_building_level[my_key] = bldg_data

                #print "bldg_data", my_key, bldg_data

        # Added Triple A:  http://www.sw.org/UBO#SpaceCollection26 http://www.sw.org/UBO#hasProperty Property570 with Type and Value: Name  3
        # Added Triple B:  http://www.sw.org/UBO#SpaceCollection26 http://www.sw.org/UBO#hasProperty Property571 with Type and Value: Elevation
        # Added Triple C:  http://www.sw.org/UBO#SpaceCollection26 http://www.sw.org/UBO#hasProperty Property572 with Type and Value: Relative_ID 4c1d8b1a-b6f7-472b-b477-1c70f02e1675
        for entry in new_data_set_building_level:
            # For each one of the query results, we will use the Semantic Graph to pull all of the elevation data
            entry_flag = 0
            name = None
            elev = None
            for row_heights in USO_New.query("""SELECT ?propNum ?type ?value
                    WHERE { ?SpaceCollection ?hasProperty ?propNum .
                            ?propNum ?hasType ?type .
                            ?propNum ?hasValue ?value . }""",
                initBindings={'SpaceCollection' : entry, 'rdf' : RDF.type, 'o' : URIRef("http://www.sw.org/UBO#SpaceCollection"), 'hasProperty' : URIRef("http://www.sw.org/UBO#hasProperty"), 'hasType' : URIRef("http://www.sw.org/UBO#hasType"), 'literal' : Literal("3DSpaceCollectionCoordinates"), 'hasValue' : URIRef("http://www.sw.org/UBO#hasValue")}):
                #print "row 2 ", entry, row_heights
                if str(row_heights[1]) == "Elevation":
                    elev = row_heights[2]
                if str(row_heights[1]) == "Name":
                    name = row_heights[2]

            # Where Name is StoreysAboveGround and Elevation is Total MeasuredHeight in Meters
            if str(elev) != "":  # Elevation in Meters
                # Then can use direct Height in Meters
                height = int(elev)
            elif str(name) != "":  # Elevation in Levels
                # Name / Levels, if no other data assuming typical 3.048 Meters (10 feet) per Level
                height = int(name) * 3.048
            else:
                height = 0

            # Now add the elevation to the data set for each building
            temp = new_data_set_building_level[entry]
            new_data = [height, temp]
            new_data_set_building_level[entry] = new_data
            #print "now data is: ", new_data_set_building_level[entry][0], new_data_set_building_level[entry][1][4]

        return new_data_set_building_level

    def WKT_to_TTL(self, WKTpolygon, BuildingGraphName):

        # There are three triples added to the file for each
        #<http://www.mygraph.org#GMLID1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/geosparql#Geometry> .
        #<http://www.mygraph.org#GMLID1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/gml#Polygon> .
        #<http://www.mygraph.org#GMLID1> <http://www.opengis.net/ont/geosparql#asGML> "<gml:Polygon srsName=\"EPSG:28992\" xmlns=\"http://www.opengis.net/citygml/2.0\" gml=\"http://www.opengis.net/gml\"><gml:coordinates>0.0 0.0 0.0, 49.0594415864 -22.5648219853 0.0, 71.6242635717 26.4946196012 0.0, 22.5648219853 49.0594415864 0.0, 0.0 0.0 0.0</gml:coordinates></gml:Polygon>"^^<http://www.opengis.net/ont/geosparql#gmlLiteral> .

        # Prepare Namespaces and Data
        building = "<" + BuildingGraphName + "> "
        rdf = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "
        geometry = "<http://www.opengis.net/ont/geosparql#Geometry> ."
        wktPolygon = "<http://www.opengis.net/ont/sf#Polygon> ."
        asWKT = "<http://www.opengis.net/ont/geosparql#asWKT> "
        wkt = '"' + str(WKTpolygon) + '"' + "^^<http://www.opengis.net/ont/geosparql#wktLiteral> ."

        # Construct Turtle Lines
        line1 = building + rdf + geometry + "\n"
        line2 = building + rdf + wktPolygon + "\n"
        line3 = building + asWKT + wkt + "\n"

        #print line1
        #print line2
        #print line3
        #print "-------------"

        with open("turtle_using_WKT.ttl", "a") as myfile:
            myfile.write(line1)
            myfile.write(line2)
            myfile.write(line3)
            myfile.close()

        return

    def create_sub_citygml(self, new_data_set_building_level):

        # Made Manually Created GML file to test the answer, automated generation can be added later


        return