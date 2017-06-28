#-------------------------------------------------------------------------------
# Name:        term_mapping.py
# Purpose:     Retrieve mapping for file type input
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


class term_mapping():
    # Input parameters
    #mapDict = dict()
    schemaFile = 'sample_files/SchemaMapReduced.csv'


    def get_mapping(self, this_file_type):
        """
        Return appropriate mapping dictionary
        Current mapping is {UBO_term, gbXML_term, gbXML_geometryPath, IFC_term, IFC_geometryPath}
        Term breakdown by "-" within CSV term
        """

        mapDict = dict()
        mapping = self.schemaFile
        count = 0

        if this_file_type == "gbxml":
            with open(mapping, 'r') as f:
                for line in f:
                    if 2 <= count <= 11:
                        # Create the dictionary {UBO_term, gbXML_term, gbXML_geometryPath_List}
                        mapDict = self.create_gbxml_map(line, mapDict)
                    count += 1
            #mapping.close()

        if this_file_type == "ifcxml":
            x = 0

        #for item in mapDict:
        #    print item, mapDict[item]

        return mapDict

    def create_gbxml_map(self, line, mapDict):
        """
        Create Map Entries
        """
        line_split1 = line.split(',')
        UBO_term = line_split1[0]
        gbXML_term = line_split1[1]
        gbXML_geometryPath_List = line_split1[2]

        line_split2 = gbXML_geometryPath_List.split('-')
        #print "line_split: ", line_split2

        path_list = list()
        test = ("1", "2", "3")
        for i in line_split2:
            add_term = str(i)
            path_list.append(add_term)
        #print "path_list: ", path_list, type(path_list).__name__

        mapDict[UBO_term] = (gbXML_term, path_list)

        return mapDict