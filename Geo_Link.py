#-------------------------------------------------------------------------------
# Name:        Geo_Link.py
# Purpose:     Start program to process geometry data for hard-coding and vocabs
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
from os import path
from file_type import file_type
from term_mapping import term_mapping
from UBO_structure import UBO_structure
from filled_UBO_graph import filled_UBO_graph
from OGCtemplate import OGCtemplate
from OGCtemplate2 import OGCtemplate2
from OGCqueryNfill import OGCqueryNfill
from QueryCurrentVocab import QueryCurrentVocab
from testing import SchemaTest
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
import cProfile
from materialAddOn import Add_Materials
from levelAddOn import Add_Levels
from punctureAddOn import Add_Punctures
from structureAddOn import Add_Structures
#from Virtuoso_Module import Virtuoso_Data


class Geo_Link():
    # Input parameters
    inputfile = ""
    material_flag = ""
    level_flag = ""
    structure_flag = ""
    puncture_flag = ""
    test_query_sequence_flag = ""


    def run(self):
        """
        Main run function
        """

        USO_New = self.process_schemas()

        return USO_New


    def process_schemas(self):
        """
        Main Processing Function
        """

        # Only GBXML is filled at this time
        vocab_dict = { "gbxml":'SmartVocabs/gbxmlVocab.ttl', "ifcxml":'SmartVocabs/ifcxmlVocab.ttl', "citygml":'SmartVocabs/citygmlVocab.ttl' }
        add_on_material_vocabs = { "gbxml":'SmartVocabs/gbxmlVocabMaterials.ttl', "ifcxml":'SmartVocabs/ifcxmlVocabMaterials.ttl', "citygml":'SmartVocabs/citygmlVocabMaterials.ttl' }
        add_on_level_vocabs = { "gbxml":'SmartVocabs/gbxmlVocabLevels.ttl', "ifcxml":'SmartVocabs/ifcxmlVocabLevels.ttl', "citygml":'SmartVocabs/citygmlVocabLevels.ttl' }
        add_on_pun_vocabs = { "gbxml":'SmartVocabs/gbxmlVocabPuns.ttl', "ifcxml":'SmartVocabs/ifcxmlVocabPuns.ttl' }
        add_on_struct_vocabs = { "gbxml":'SmartVocabs/gbxmlVocabStructure.ttl', "ifcxml":'SmartVocabs/ifcxmlVocabStructure.ttl' }

        # Send file type and return respective term mapping between it and the UBO
        # Also find the source app that created this particular gbXML (use to lift to ontology later)
        step1a = file_type()
        this_file_type, Company, Product, Platform, Dimension, CRS, ProjectName = step1a.schema_type(self.inputfile)
        print "this_file_type and Data Extracted: ", this_file_type, Company, Product, Platform, Dimension, CRS, ProjectName

        # Retrieve the UBO empty structure to fill with the values from the input file
        step2 = UBO_structure()
        UBOgraphStructure = step2.pull_graph_structure()


        ##################################################
        # First Phase of Project Translating To OGC Format

         # Send file type and return respective term mapping between it and the UBO
        step3 = term_mapping()
        mapDict = step3.get_mapping(this_file_type)
        #print "mapDict: ", mapDict

        """
        # Use mapping and the UBO structure to fill the UBO with geometry data
        step3 = filled_UBO_graph()
        UBO_filled, base = step3.fill_graph(this_file_type, mapDict, UBOgraphStructure, self.inputfile)

        # Setup ISO/OGC GeoSPARQL File Template...from: http://www.opengeospatial.org/standards/geosparql
        # Also uses the OGC simple feature documentation (both pdfs in sample_files folder)
        # States that the file type is RDF/XML encoded geometry data, in GeoSPARQL format)
        step4 = OGCtemplate2()
        OGC_RDF_header, OGC_file_parts = step4.createOGCtemplate2(base)
        #step4 = OGCtemplate()
        #OGC_RDF_header, OGC_file_parts = step4.createOGCtemplate(base)

        # Query UBO for data based on map, process coordinates into OGC format, use answers to fill OGC RDF file for output
        step5 = OGCqueryNfill()
        stuff = step5.processUBOforOGC(UBO_filled, base, OGC_RDF_header, OGC_file_parts)

        # Use UBO_filled to answer queries for data within to create respective ISO/OGC GeoSPARQL File
        """
        ##################################################

        ##################################################
        # Second Phase of Project Using Smart Vocabularies

        # Get the associated vocabualry
        current_vocab = vocab_dict[this_file_type]
        print "current_vocab ", current_vocab

        # Commented out to work on adding IFC type
        stepb = QueryCurrentVocab()
        USO_New, Add_On_Dict, tree, namespaces, property_counter, missing_link_dict_for_citygml = stepb.query_current_vocab(current_vocab, self.inputfile, UBOgraphStructure, this_file_type)
        if this_file_type == "ifcxml" or this_file_type == "gbxml":
            missing_link_dict_for_citygml = dict() # This way it is empty unless we are handling it for CityGML

        ##################################################

        ##################################################

        # For Graph Add-Ons:

        print "Processing Graph Add-Ons"
        material_dict = dict()             # Address:(GraphName, SGA_Element_Type) [basically all SBElements in Model]
        level_dict_spaces = dict()         # Address:(GraphName, SGA_Element_Type) [basically all Spaces in Model]
        level_dict_surfaces = dict()       # Address:(GraphName, SGA_Element_Type) [basically all SpaceBoundaries in Model]
        structure_dict_surfaces = dict()   #?
        structure_dict_materials = dict()  # Address:(GraphName, SGA_Element_Type) [basically all SpaceBoundaries and SBElements in Model]
        puncture_dict_surfaces = dict()    #?
        structure_dict_spaces = dict()
        structure_dict_spacecollection = dict()
        building_ids_dict = dict()
        #puncture_dict_materials = dict()   #?
        for entry in Add_On_Dict:
            #print "see....", entry, Add_On_Dict[entry]
            if str(Add_On_Dict[entry][1].split("#")[1]) == "SpaceCollection":
                structure_dict_spacecollection[entry] = Add_On_Dict[entry]
                building_ids_dict[entry] = Add_On_Dict[entry]
            if str(Add_On_Dict[entry][1].split("#")[1]) == "Space":
                level_dict_spaces[entry] = Add_On_Dict[entry]
                structure_dict_spaces[entry] = Add_On_Dict[entry]
            if str(Add_On_Dict[entry][1].split("#")[1]) == "SpaceBoundary":
                level_dict_surfaces[entry] = Add_On_Dict[entry]
                structure_dict_surfaces[entry] = Add_On_Dict[entry]
                puncture_dict_surfaces[entry] = Add_On_Dict[entry]
            if str(Add_On_Dict[entry][1].split("#")[1]) == "SpaceBoundaryElement":
                material_dict[entry] = Add_On_Dict[entry]
                print "checking here AND start working here!!!", entry, Add_On_Dict[entry]
                structure_dict_materials[entry] = Add_On_Dict[entry]
                #puncture_dict_materials[entry] = Add_On_Dict[entry]
        #============================================================== Add Materials If Requested
        if self.material_flag == 1:
            # User Wants to Add Materials
            current_addOn_vocab = add_on_material_vocabs[this_file_type]
            mat = Add_Materials()
            USO_New, property_counter = mat.add_mat_name_and_id(tree, namespaces, material_dict, this_file_type, self.inputfile, USO_New, current_addOn_vocab, property_counter)
        else:
            print "self.material_flag not requested"
        #============================================================== Add Levels If Requested
        if self.level_flag == 1:
            # User Wants to Add Storey Levels
            current_addOn_vocab = add_on_level_vocabs[this_file_type]
            lev = Add_Levels()
            USO_New, property_counter = lev.add_level_name_and_id(tree, namespaces, level_dict_spaces, level_dict_surfaces, this_file_type, self.inputfile, USO_New, current_addOn_vocab, property_counter, missing_link_dict_for_citygml)
        else:
            print "self.level_flag not requested"
        #============================================================== Add Structures If Requested
        if self.structure_flag == 1:
            # User Wants to Add Structural Components such as Beams and Columns and so on as project progresses
            if this_file_type == "citygml":
                print "self.structure_flag is == 1 but this not set up for citygml so passed..."
            else:
                current_addOn_vocab = add_on_struct_vocabs[this_file_type]
                struct = Add_Structures()
                USO_New, property_counter = struct.add_struct_geometries(tree, namespaces, structure_dict_spacecollection, structure_dict_spaces, structure_dict_surfaces, structure_dict_materials, this_file_type, self.inputfile, USO_New, current_addOn_vocab, property_counter)
        else:
            print "self.structure_dict not requested"
        #============================================================== Add Punctures (Win/Doors) If Requested
        if self.puncture_flag == 1:
            # User Wants to Add Puncture Components such as Windows and Doors
            if this_file_type == "citygml":
                print "self.puncture_flag is == 1 but this not set up for citygml so passed..."
            else:
                current_addOn_vocab = add_on_pun_vocabs[this_file_type]
                pun = Add_Punctures()
                USO_New, property_counter = pun.add_pun_geometries(tree, namespaces, puncture_dict_surfaces, this_file_type, self.inputfile, USO_New, current_addOn_vocab, property_counter)
        else:
            print "self.puncture_dict not requested"


        ##################################################

        ##################################################

        # Ask for data that will be relevant to these tests:
        if self.test_query_sequence_flag == 1 and self.level_flag == 0:
            # Then the Level information is not there so we need to add it still
            current_addOn_vocab = add_on_level_vocabs[this_file_type]
            lev = Add_Levels()
            #USO_New, property_counter = lev.add_level_name_and_id(tree, namespaces, level_dict_spaces, level_dict_surfaces, this_file_type, self.inputfile, USO_New, current_addOn_vocab, property_counter, missing_link_dict_for_citygml)
            # Use the USO_New graph to transform GML data for Virtuoso/GraphDB queries
            #vd = Virtuoso_Data()
            #vd.format_data(USO_New, CRS, Dimension, building_ids_dict, tree, namespaces)
            # Then there wil be something to add on to the graph for other parts of schema alignment or to handle two graphs at once...
            # All the backward relationships could also be added...perhaps
            print "MAY NEED TO UNCOMMENT GRAPHDB SECTIONS"
        if self.test_query_sequence_flag == 1 and self.level_flag == 1:
            # Use the USO_New graph to transform GML data for Virtuoso/GraphDB queries
            #vd = Virtuoso_Data()
            #vd.format_data(USO_New, CRS, Dimension, building_ids_dict, tree, namespaces)
            # Then there wil be something to add on to the graph for other parts of schema alignment or to handle two graphs at once...
            # All the backward relationships could also be added...perhaps
            print "MAY NEED TO UNCOMMENT GRAPHDB SECTIONS"

        ##################################################

        ##################################################

        # Testing tags in schema types:
        mytest = SchemaTest()
        #mytest.testing(current_vocab, self.inputfile, this_file_type)
        # Nothing to return since just printing tags to check handling

        # Then print or save the final USO_New for use back in the Orchestration Modules:
        #print USO_New

        return USO_New



