#-------------------------------------------------------------------------------
# Name:        file_type.py
# Purpose:     Determine the XML schema data that was just passed as program input
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     06/10/2015
# Copyright:   (c) Holly Tina Ferguson 2015
# Licence:     The University of Notre Dame


# At this point, there are a few test mining examples, later, this can be where we pull out CRS and similar data
#-------------------------------------------------------------------------------

# #!/usr/bin/python
from lxml import etree
import sys
import os


class file_type():
    # Input parameters
    tree = None
    # May change as additional file options get entered into the mix
    #namespaces = {'gb': "http://www.gbxml.org/schema", 'city': "http://www.opengis.net/citygml/2.0"}


    def schema_type(self, inputfile):
        """
        Check file extensions to determine schema type
        """
        fileType = None
        struct = None

        fileExtension = inputfile.split(".")[-1]
        #print "ext: ", fileExtension

        if fileExtension == "ifcxml":
            namespaces = {'ifc': "http://www.buildingsmart-tech.org/ifc/IFC4/final/html/index.htm", 'exp': "urn:oid:1.0.10303.28.2.1.1"}
            fileType = "ifcxml"
        elif fileExtension == "gml":
            print "should be here"
            namespaces = {'city': "http://www.opengis.net/citygml/2.0", 'gml': "http://www.opengis.net/gml", 'bldg': "http://www.opengis.net/citygml/building/2.0", 'dem': "http://www.opengis.net/citygml/relief/1.0"}
            self.tree = etree.parse(inputfile)
            struct = self.tree
            gmlxmls = self.tree.xpath("/city:CityModel", namespaces=namespaces)
            if not gmlxmls:
                print "1"
                namespaces = {'city': "http://www.citygml.org/citygml/1/0/0", 'gml': "http://www.opengis.net/gml", 'bldg': "http://www.opengis.net/citygml/building/2.0", 'dem': "http://www.opengis.net/citygml/relief/1.0"}
                gmlxmls = self.tree.xpath("/city:CityModel", namespaces=namespaces)
            if not gmlxmls:
                print "2"
                namespaces = {'city': "http://www.opengis.net/gml", 'gml': "http://www.opengis.net/gml", 'bldg': "http://www.opengis.net/citygml/building/2.0", 'dem': "http://www.opengis.net/citygml/relief/1.0"}
                gmlxmls = self.tree.xpath("/city:CityModel", namespaces=namespaces)

            if not gmlxmls:
                fileType = None
            else:
                fileType = "citygml"
        elif fileExtension == "xml":
            # File is an xml but may still be a gbxml since those extensions are just xml
            # Open/parse the file to check if it is still a gbxml or unhandled type at this time
            namespaces = {'gb': "http://www.gbxml.org/schema"}
            self.tree = etree.parse(inputfile)
            struct = self.tree
            gbxmls = self.tree.xpath("/gb:gbXML", namespaces=namespaces)
            if not gbxmls:
                fileType = None
            else:
                fileType = "gbxml"
        else:
            fileType = "not yet handled"
            namespaces = {}

        Company, Product, Platform, Dimension, CRS, ProjectName = self.souce_application_data(struct, fileType, namespaces)
        print "SourceDetials: ", Company, Product, Platform, Dimension, CRS, ProjectName, "source file type: ", fileType

        return fileType, Company, Product, Platform, Dimension, CRS, ProjectName

    def souce_application_data(self, struct, this_file_type, namespaces):
        """
        Check gbxml for source OS, Company, and Generating Application
        """
        Company = ""
        Product = ""
        Platform = ""
        CRS = "" # Coordinate Reference System for processing additions later on...
        Dimension = ""
        ProjectName = ""

        #surfaces = struct.xpath("/gb:gbXML/gb:Campus/gb:Surface", namespaces=self.namespaces)
        #for surface in surfaces:
        #    cad = str(surface.xpath("./gb:CADObjectId", namespaces=self.namespaces)[0].text)
        #    print "cad: ", cad

        if this_file_type == "gbxml":
            DocumentHistory = struct.xpath("/gb:gbXML/gb:DocumentHistory/gb:ProgramInfo", namespaces=namespaces)
            for item in DocumentHistory:
                Company = str(item.xpath("./gb:CompanyName", namespaces=namespaces)[0].text)
                Product = str(item.xpath("./gb:ProductName", namespaces=namespaces)[0].text)
                Platform = str(item.xpath("./gb:Platform", namespaces=namespaces)[0].text)

        if this_file_type == "citygml":
            DocumentInfo = struct.xpath("/city:CityModel/gml:boundedBy/gml:Envelope", namespaces=namespaces)
            if DocumentInfo:
                for item in DocumentInfo:
                    Dimension = item.get("srsDimension")
                    CRS = item.get("srsName")
                DocumentInfo = struct.xpath("/city:CityModel", namespaces=namespaces)
                for item in DocumentInfo:
                    ProjectName = str(item.xpath("./gml:name", namespaces=namespaces)[0].text)

        #print "Data Pulled :", this_file_type, Company, Product, Platform, Dimension, CRS, ProjectName

        return Company, Product, Platform, Dimension, CRS, ProjectName


