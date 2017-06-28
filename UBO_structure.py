#-------------------------------------------------------------------------------
# Name:        UBO_structure.py
# Purpose:     Retrieve UBO structure to be filled with values
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
import pprint


class UBO_structure():
    # Input parameters
    #variable = ""
    # Named Graph may be how to fill graph and maybe role chains

    def pull_graph_structure(self):
        """
        Get an empty graph structure from the UBO ontology structure
        #http://rdflib.readthedocs.org/en/latest/
        #http://rdflib.readthedocs.org/en/latest/intro_to_graphs.html
        #http://rdflib.readthedocs.org/en/latest/intro_to_parsing.html
        """

        UBO = Graph()
        # Differnet parser types: http://rdflib.readthedocs.org/en/latest/plugin_parsers.html
        #UBO.parse("UBOfromProtege/UBO_Protege_TTL.ttl", format="turtle")
        UBO.parse("UBOfromProtege/UBO_Protege_TTL.ttl", format="turtle")
        #for stmt in UBO:
        #    pprint.pprint(stmt)
        #print "Number of Triples in UBO OWL: ", len(UBO)

        return UBO
