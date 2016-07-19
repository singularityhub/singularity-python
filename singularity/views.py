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


def make_package_tree(folders,files,path_delim="/"):
    '''make_package_tree will convert a list of folders and files into a json structure that represents a graph.
    :param folders: a list of folders in the image
    :param files: a list of files in the folder
    :param path_delim: the path delimiter, default is '/'
    '''
    graph = {} # graph will be a dictionary structure of nodes
    nodes = {} # nodes will be a lookup for each folder containing files 
    count = 0  # count will hold an id for nodes
    for folder in folders:
        if folder != ".":
            folder = re.sub("^[.]/","",folder)
            index = graph
            path_components = folder.split(path_delim)
            for p in range(len(path_components)):
                path_component = path_components[p]
                if path_component not in index:
                    index[path_component] = {"id":count,"children":{}}
                    fullpath = path_delim.join(path_components[0:p+1])
                    nodes[fullpath] = count
                    count+=1
                index = index[path_component]["children"]
                
    # Files are endnodes
    endnodes = {}
    for file_path in files:
        file_path = re.sub("^[.]/","",file_path)
        file_parts = file_path.split(path_delim)
        file_name = file_parts.pop(-1)
        fullpath = path_delim.join(file_parts)
        if fullpath in nodes:
            uid = nodes[fullpath]
            if uid in endnodes:
                endnodes[uid].append(file_name)
            else:
                endnodes[uid] = [file_name]
 
    result = {"nodes":endnodes,"lookup":nodes,"graph":graph}
    return result

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
