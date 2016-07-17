#!/usr/bin/env python

'''
views.py: part of singularity package

'''

from singularity.utils import zip_up, read_file, load_image, write_file
from singularity.package import list_package, package
from singularity.cli import Singularity
import SimpleHTTPServer
import SocketServer
import webbrowser
import tempfile
import zipfile
import json
import os
import re


###################################################################################################
# PACKAGE TREE ####################################################################################
###################################################################################################


def tree(image_path,port=9999,S=None,view=True):
    '''tree will render an html tree (graph) of an image or package
    :param image_path: full path to the image, or package
    :param port: the port to open on the user local machine
    :param S: the Singularity object, will be generated if none provided
    :param view: if True (default) will open in web browser. Otherwise, just return html
    '''

    if S == None:
        S = Singularity()

    # Make a temporary directory for stuffs
    tmpdir = tempfile.mkdtemp()

    # If the user has provided an image, try to package it
    if re.search(".img$",image_path):
        image_path = package(image_path,output_folder=tmpdir,S=S)

    # If it's a package, look for folders.txt and files.txt
    if re.search(".zip$",image_path):
        guts = list_package(image_path)
        if "folders.txt" in guts and "files.txt" in guts:
            retrieved = load_package(get=["folders.txt","files.txt"])
            html_snippet = make_package_tree(folders=retrieved["folders"],
                                             files=retrieved["files"])

            # TODO: Write files and templates to output folder
            write_file("%s/index.html" %(tmpdir),html_snippet)

            # TODO: we may want to zip the stuffs for the user, and export to
            # some output folder

            # Does the user want to open the visualization in the browser?
            if view == True:
                webserver(tmpdir,port=port,description="image tree")

    else:
        print("Cannot find folders.txt and files.txt in package, cannot create visualization.")

    shutil.rmtree(tmpdir)


def make_package_tree(folders,files):
    '''make_package_tree will return the html snippet for a tree/graph with folders and files
    :param folders: a list of folders in the image
    :param files: a list of files in the folder
    '''
    print('WRITE ME')
    # stopped here -
    # 1) find a nice graph visualization for data, render into right output format, make graph
    # 2) add graph as template into singularity-python, test function with webserver
    # 3) add to command line tools something like "--viewtree"
    # 4) write function to generate an entire GROUP of graphs and an index to browse them
    # 5) make option in command line to take in comma separated list to produce the above.
    # 6) 

###################################################################################################
# WEBSERVER FUNCTIONS #############################################################################
###################################################################################################

def webserver(base_folder,port=None,description=None):
    '''webserver will generate a temporary webserver in some base_folder
    :param base_folder: the folder base to use
    :param description: description of the visualization, for the user
    '''
    if description == None:
        description = "visualization"

    try:
        if port == None:
            port = choice(range(8000,9999),1)[0]
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", port), Handler)
        print("View shub %s at localhost:%s" %(port,description))
        webbrowser.open("http://localhost:%s" %(port))
        httpd.serve_forever()
    except:
        print("Stopping web server...")
        httpd.server_close()
