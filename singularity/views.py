#!/usr/bin/env python

'''
views.py: part of singularity package

'''

import json
import os
import re
import requests
from singularity.logman import bot

from singularity.package import (
    load_package,
    package
)

import shutil
import tempfile
import zipfile


###################################################################################
# COMPARISON FUNCTIONS ############################################################
###################################################################################

def compare_containers(container1,container2,by=None):
    '''compare_containers will generate a data structure with common and unique files to
    two images. If environmental variable SINGULARITY_HUB is set, will use container
    database objects.
    :param container1: first container for comparison
    :param container2: second container for comparison
    :param shub: If true, will 
    :param by: what to compare, one or more of 'files.txt' or 'folders.txt'
    default compares just files
    '''
    if by == None:
        by = ["files.txt"]
    if not isinstance(by,list):
        by = [by]

    # Get files and folders for each
    container1_guts = get_container_contents(container1,
                                             gets=by,
                                             split_delim="\n")
    container2_guts = get_container_contents(container2,
                                             gets=by,
                                             split_delim="\n")

    # Do the comparison for each metric
    comparisons = dict()
    for b in by:
        intersect = [x for x in container1_guts[b] if x in container2_guts[b]]
        unique1 = [x for x in container1_guts[b] if x not in container2_guts[b]]
        unique2 = [x for x in container2_guts[b] if x not in container1_guts[b]]

        # Return data structure
        comparison = {"intersect":intersect,
                      "unique1": unique1,
                      "unique2": unique2}
        bot.logger.info("Intersect has length %s",len(intersect))
        bot.logger.info("Unique to %s: %s",container1,len(unique1))
        bot.logger.info("Unique to %s: %s",container2,len(unique2))
        comparisons[b] = comparison 

    return comparisons
    


def calculate_similarity(container1,container2,by="files.txt",comparison=None):
    '''calculate_similarity will calculate similarity of two containers by files content, default will calculate
    2.0*len(intersect) / total package1 + total package2
    :param container1: container 1
    :param container2: container 2
    :param by: the one or more metrics (eg files.txt) list to use to compare
     valid are currently files.txt or folders.txt
    :param comparison: the comparison result object for the tree. If provided,
    will skip over function to obtain it.
    '''
    if not isinstance(by,list):
        by = [by]

    if comparison == None:
        comparison = compare_containers(container1,container2,by=by)
    scores = dict()

    for b in by:
        total_unique = len(comparison[b]['unique1']) + len(comparison[b]['unique2'])

        # If neither has equal files, denominator is 0, similarity is 1
        if total_unique == 0:
            scores[b] = 1.0     
        else:
            scores[b] = 2.0*len(comparison[b]["intersect"]) / total_unique
    return scores


def get_container_contents(container,gets=None,split_delim=None):
    '''get_container_contents will return a list of folders and or files
    for a container. The environmental variable SINGULARITY_HUB being set
    means that container objects are referenced instead of packages
    :param container: the container to get content for
    :param gets: a list of file names to return, without parent folders
    :param split_delim: if defined, will split text by split delimiter
    '''
    # Default returns are the list of files and folders
    if gets == None:
        gets = ['files.txt','folders.txt']
    if not isinstance(gets,list):
        gets = [gets]

    # We will look for everything in guts, then return it
    guts = dict()

    SINGULARITY_HUB = os.environ.get('SINGULARITY_HUB',"False")

    # Visualization deployed local or elsewhere
    if SINGULARITY_HUB == "False":
        bot.logger.debug("Not running from Singularity Hub.")
        tmpdir = tempfile.mkdtemp()
        image_package = package(image_path=container,
                                output_folder=tmpdir,
                                runscript=False,
                                software=True,
                                remove_image=True)
     
        guts = load_package(image_package,get=gets)
        shutil.rmtree(tmpdir)
        return guts

    # Visualization deployed by singularity hub
    else:   
        bot.logger.debug("Running from Singularity Hub.")
        for sfile in container.files:
            for gut_key in gets:        
                if os.path.basename(sfile['name']) == gut_key:
                    if split_delim == None:
                        guts[gut_key] = requests.get(sfile['mediaLink']).text
                    else:
                        guts[gut_key] = requests.get(sfile['mediaLink']).text.split(split_delim)

    return guts


###################################################################################
# COMPARISON TREES
###################################################################################


def container_difference(container,container_subtract,comparison=None):
    '''container_difference will return a data structure to render an html 
    tree (graph) of the differences between two images or packages. The second
    container is subtracted from the first
    :param container: the primary container object (to subtract from)
    :param container_subtract: the second container object to remove
    :param comparison: the comparison result object for the tree. If provided,
    will skip over function to obtain it.
    '''
    if comparison == None:
        comparison = compare_containers(container,container_subtract,
                                        by=['files.txt','folders.txt'])
    files = comparison["files.txt"]['unique1']
    folders = comparison['folders.txt']['unique1']
    tree = make_container_tree(folders=folders,
                               files=files)
    return tree



def container_similarity(container1,container2,comparison=None):
    '''container_sim will return a data structure to render an html tree 
    (graph) of the intersection (commonalities) between two images or packages
    :param container1: the first container object
    :param container2: the second container object
    :param comparison: the comparison result object for the tree. If provided,
    will skip over function to obtain it.
    '''
    if comparison == None:
        comparison = compare_containers(container1,container2,
                                        by=['files.txt','folders.txt'])
    files = comparison["files.txt"]['intersect']
    folders = comparison['folders.txt']['intersect']
    tree = make_container_tree(folders=folders,
                               files=files)
    return tree


def container_tree(container):
    '''tree will render an html tree (graph) of a container
    '''

    guts = get_container_contents(container,split_delim="\n")

    # Make the tree and return it
    tree = make_container_tree(folders = guts["folders.txt"],
                               files = guts['files.txt'])
    return tree


def make_container_tree(folders,files,path_delim="/",parse_files=True):
    '''make_container_tree will convert a list of folders and files into a json structure that represents a graph.
    :param folders: a list of folders in the image
    :param files: a list of files in the folder
    :param parse_files: return 'files' lookup in result, to associate ID of node with files (default True)
    :param path_delim: the path delimiter, default is '/'
    '''
    nodes = {}  # first we will make a list of nodes
    lookup = {}
    count = 1   # count will hold an id for nodes
    max_depth = 0
    for folder in folders:
        if folder != ".":
            folder = re.sub("^[.]/","",folder)
            path_components = folder.split(path_delim)
            for p in range(len(path_components)):
                path_component = path_components[p]
                fullpath = path_delim.join(path_components[0:p+1])
                # Have we created the node yet?
                if fullpath not in lookup:
                    lookup[fullpath] = count
                    node = {"id":count,"name":path_component,"path":fullpath,"level":p,"children":[]}
                    count +=1
                    # Did we find a deeper level?
                    if p > max_depth:
                        max_depth = p
                    # Does the node have a parent?
                    if p==0: # base node, no parent
                        parent_id = 0
                    else: # look up the parent id
                        parent_path = path_delim.join(path_components[0:p])
                        parent_id = lookup[parent_path]                   
                    node["parent"] = parent_id
                    nodes[node['id']] = node   
           
    # Now make the graph, we simply append children to their parents
    seen = []
    graph = []
    iters = list(range(max_depth+1)) # 0,1,2,3...
    iters.reverse()            # ...3,2,1,0
    iters.pop()                # remove 0
    for level in iters:
        children = {x:y for x,y in nodes.items() if y['level'] == level}
        seen = seen + [y['id'] for x,y in children.items()]
        nodes = {x:y for x,y in nodes.items() if y['id'] not in seen}
        for node_id,child_node in children.items():
            if node_id == 0: #base node
                graph[node_id] = child_node
            else:
                parent_id = child_node['parent']
                nodes[parent_id]["children"].append(child_node)

    # Now add the parents to graph, with name as main lookup
    for parent,parent_info in nodes.items():
        graph.append(parent_info)
    graph = {"name":"base","children":graph}
    result = {"graph":graph,"lookup":lookup,"depth":max_depth+1}

    # Parse files to include in tree
    if parse_files == True:
        file_lookup = {}
        for filey in files:
            filey = re.sub("^[.]/","",filey)
            filepath,filename = os.path.split(filey)
            if filepath in lookup:
                folder_id = lookup[filepath]
                if folder_id in file_lookup:
                    file_lookup[folder_id].append(filename)
                else:
                    file_lookup[folder_id] = [filename]
            elif filepath == '': # base folder
                if 0 in file_lookup:
                    file_lookup[0].append(filename)
                else:
                    file_lookup[0] = [filename]
        result['files'] = file_lookup

    return result
