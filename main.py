#-------------------------------------------------------------------------------
# Name:        main.py
# Purpose:     GeoLinked App to Facilitate Mappings and Processing
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     06/10/2015
# Copyright:   (c) Holly Tina Ferguson 2015
# License:     The University of Notre Dame
#-------------------------------------------------------------------------------

# #!/usr/bin/python
import sys
import getopt
import os
from Geo_Link import Geo_Link
from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput
import cProfile, pstats, StringIO
import re


def main(argv, inputfile='C:/Users/hfergus2/Desktop/Orchestration/TempXMLs/bRC_FRAME_Concrete_allComponents.ifcxml', outputpath='output.csv', material_flag=1, level_flag=1, structure_flag=1, puncture_flag=1, test_query_sequence_flag=0):
    #C:/Users/Holly2012/Desktop/GeoLinked/sample_files/
    #C:/Users/hfergus2/Desktop/GeoLinked/sample_files/
    #C:/Users/hfergus2/Desktop/GeoLinked/sample_files/gbxml/Single_Room_GBXML.xml
        #gbxml/Single_Room_GBXML.xml              #  4.61 s
        #gbxml/4_Room_GBXML.xml                   #  5.36 s
        #gbxml/Vet_Center_GBXML.xml               #  15.35 s
        #gbxml/L_1Floor_GBXML.xml                 #  20.21 s
        #gbxml/L_2Floor_GBXML.xml                 #  1 m 18.95 s
    #C:/Users/hfergus2/Desktop/GeoLinked/sample_files/ifcxml/Single_Room_IFCxml.ifcxml
        #ifcxml/Single_Room_IFCxml.ifcxml          #  13.91 s
        #ifcxml/4Room.ifcxml                       #  34.59 s
        #ifcxml/Vet_Center_Model.ifcxml            #  17 m 9.21 s     But IFC turns this into 300+ surfaces and is over 100,000 lines compared to gbxml 23,000+ lines and 182 Surfaces
        #ifcxml/L_1Floor.ifcxml                    #  40 m 11.06 s
        #ifcxml/L_2Floor.ifcxml                    # was at 1h24m at 3:41
    #C:/Users/hfergus2/Desktop/GeoLinked/sample_files/citygml/Bldg_LOD0.gml
        #citygml/Bldg_LOD0.gml                      #  ? s
        #citygml/Bldg_LOD1.gml
        #citygml/Bldg_LOD2.gml
        #citygml/Bldg_LOD2_Garage.gml
        #citygml/Bldg_LOD3.gml
        #citygml/Bldg_LOD4.gml
    #OSM/OMS_Building_1stFloor.ifcxml

    #Orchestration Tests
    #bRC_FRAME_Concrete_allComponents
    #cRC_FRAME_Concrete_ReinforcementCheck

    # RSA Tests:
    #C:\Users\hfergus2\Desktop\RSA_Files/RC_FRAME.ifcxml

    # These last three start to get into more complexity and would be a great place to continue adding upon expansion of the project as a whole...(i.e. namespace and schema versioning...)
    # This is because these are from version 1.0 and this code is designed for the updated version 2.0
        #citygml/1Level_MultiRoom_LOD4
        #citygml/CitySmallHouseA_LOD4
        #citygml/CitySmallHouseB_LOD3-4

    # For Structure:
        #gbxml/4Room_RoundColumns_GBXML.xml
        #gbxml/4Room_SquareColumns_GBXML.xml
        ####################################
        #ifcxml/4Room_SquareColumns_IFCXML.ifcxml
        #ifcxml/4Room_WFlangeColumns_IFCXML.ifcxml
        #ifcxml/4Room2016_Square.ifcxml
        #ifcxml/4Room2016_WFlange.ifcxml

    print "Main Started"

    # Get the input file
    #inputfile = sys.argv[0]
    #Single_Room_GBXML
    #Single_Room_IFCxml
    mypath = os.path.abspath(inputfile)
    #print "inputfile", mypath, type(inputfile).__name__

    geo_link = Geo_Link()
    geo_link.inputfile = mypath
    #   These are additional graph add-ons that can be set to one based on what the model needs to mine, if available in the schema instance: ---------------------------------------------
    # For models that can provide Sub-Assembly level spatial Elements (SpaceBoundaryElements), material_flag will add Properties for Local Material Name and Local Material ID
    # For models that can provide Surface level spatial Elements (SpaceBoundary), level_flag will add Properties for Building Level Relative to the Ground Level (Thus Space Level Inferred)
    # For models that can provide Structural level spatial Elements (SpaceBoundary/Elements), structure_flag will add Properties for Beams, Columns, Probably Coordinates of those
    geo_link.material_flag = material_flag
    geo_link.level_flag = level_flag
    geo_link.structure_flag = structure_flag
    geo_link.puncture_flag = puncture_flag
    geo_link.test_query_sequence_flag = test_query_sequence_flag


    geo_link.run()
    #cProfile.runctx('geo_link.run()', None, locals())


    #graphviz = GraphvizOutput()
    #graphviz.output_file = 'profile.png'
    #with PyCallGraph(output=graphviz):
    #    geo_link.run()


    #outputfile = open(outputpath) #output.csv in the main folder
    #with open(outputpath, 'r') as f:
        #Add whatever stuff
        #for line in f:
        #    outputfile.write(line)
    #outputfile.close()
    sys.stdout.write("Main Finished")

if __name__ == "__main__":
    #logging.basicConfig()
    main(sys.argv[1:])
    #main(inputfile, outputfile)




