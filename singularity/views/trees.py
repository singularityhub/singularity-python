#!/usr/bin/env python

'''
singularity views/trees.py: part of singularity package

'''

import json

from singularity.logman import bot

from singularity.views.utils import get_container_contents
from singularity.analysis.compare import (
    calculate_similarity,
    compare_containers,
    compare_packages
)


from singularity.package import (
    load_package,
    package
)

import os
import pandas
import re
import requests
import shutil
import sys
import tempfile
import zipfile


###################################################################################
# COMPARISON TREES
###################################################################################


def container_difference(container=None,container_subtract=None,image_package=None,
                         image_package_subtract=None,comparison=None):
    '''container_difference will return a data structure to render an html 
    tree (graph) of the differences between two images or packages. The second
    container is subtracted from the first
    :param container: the primary container object (to subtract from)
    :param container_subtract: the second container object to remove
    :param image_package: a zipped package for image 1, created with package
    :param image_package_subtract: a zipped package for subtraction image, created with package
    :param comparison: the comparison result object for the tree. If provided,
    will skip over function to obtain it.
    '''
    if comparison == None:
        comparison = compare_containers(container1=container,
                                        container2=container_subtract,
                                        image_package1=image_package,
                                        image_package2=image_package_subtract,
                                        by=['files.txt','folders.txt'])

    files = comparison["files.txt"]['unique1']
    folders = comparison['folders.txt']['unique1']
    tree = make_container_tree(folders=folders,
                               files=files)
    return tree



def container_similarity(container1=None,container2=None,image_package1=None,
                         image_package2=None,comparison=None):
    '''container_sim will return a data structure to render an html tree 
    (graph) of the intersection (commonalities) between two images or packages
    :param container1: the first container object
    :param container2: the second container object if either not defined, need
    :param image_package1: a packaged container1 (produced by package)
    :param image_package2: a packaged container2 (produced by package)
    :param comparison: the comparison result object for the tree. If provided,
    will skip over function to obtain it.
    '''
    if comparison == None:
        comparison = compare_containers(container1=container1,
                                        container2=container2,
                                        image_package1=image_package1,
                                        image_package2=image_package2,
                                        by=['files.txt','folders.txt'])
    files = comparison["files.txt"]['intersect']
    folders = comparison['folders.txt']['intersect']
    tree = make_container_tree(folders=folders,
                               files=files)
    return tree


def container_tree(container=None,image_package=None):
    '''tree will render an html tree (graph) of a container
    '''

    guts = get_container_contents(container=container,
                                  image_package=image_package,
                                  split_delim="\n")

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


###################################################################################
# DENDROGRAM
###################################################################################


def make_package_tree(matrix=None,labels=None,width=25,height=10,title=None):
    '''make package tree will make a dendrogram comparing a matrix of packages
    :param matrix: a pandas df of packages, with names in index and columns
    :param labels: a list of labels corresponding to row names, will be
    pulled from rows if not defined
    :param title: a title for the plot, if not defined, will be left out.
    :returns a plot that can be saved with savefig
    '''
    from matplotlib import pyplot as plt
    from scipy.cluster.hierarchy import (
        dendrogram, 
        linkage
    )

    from scipy.cluster.hierarchy import cophenet
    from scipy.spatial.distance import pdist

    if not isinstance(matrix,pandas.DataFrame):
        bot.logger.info("No pandas DataFrame (matrix) of similarities defined, will use default.")
        matrix = compare_packages()['files.txt']
        title = 'Docker Library Similarity to Base OS'

    Z = linkage(matrix, 'ward')
    c, coph_dists = cophenet(Z, pdist(matrix))

    if labels == None:
        labels = matrix.index.tolist()

    plt.figure(figsize=(width, height))

    if title != None:
        plt.title(title)

    plt.xlabel('image index')
    plt.ylabel('distance')
    dendrogram(Z,
               leaf_rotation=90.,  # rotates the x axis labels
               leaf_font_size=8.,  # font size for the x axis labels
               labels=labels)
    return plt
