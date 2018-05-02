#!/usr/bin/env python

'''
singularity views/trees.py: part of singularity package

The MIT License (MIT)

Copyright (c) 2016-2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from functools import reduce
import json

from singularity.logger import bot

import os
import pandas
import re
import requests
import shutil
import sys
import tempfile
import zipfile



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


def make_package_tree(matrix=None,labels=None,width=25,height=10,title=None,font_size=None):
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

    if font_size is None:
        font_size = 8.

    from scipy.cluster.hierarchy import cophenet
    from scipy.spatial.distance import pdist

    if not isinstance(matrix,pandas.DataFrame):
        bot.info("No pandas DataFrame (matrix) of similarities defined!")
        sys.exit(1)

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
               leaf_font_size=font_size,  # font size for the x axis labels
               labels=labels)
    return plt


def make_interactive_tree(matrix=None,labels=None):
    '''make interactive tree will return complete html for an interactive tree
    :param title: a title for the plot, if not defined, will be left out.
    '''
    from scipy.cluster.hierarchy import (
        dendrogram, 
        linkage,
        to_tree
    )

    d3 = None
    from scipy.cluster.hierarchy import cophenet
    from scipy.spatial.distance import pdist

    if isinstance(matrix,pandas.DataFrame):
        Z = linkage(matrix, 'ward') # clusters
        T = to_tree(Z, rd=False)

        if labels == None:
            labels = matrix.index.tolist()
        lookup = dict(zip(range(len(labels)), labels))

        # Create a dendrogram object without plotting
        dend = dendrogram(Z,no_plot=True,
                      orientation="right",
                      leaf_rotation=90.,  # rotates the x axis labels
                      leaf_font_size=8.,  # font size for the x axis labels
                      labels=labels)

        d3 = dict(children=[], name="root")
        add_node(T, d3)
        label_tree(d3["children"][0],lookup)
    else:
        bot.warning('Please provide data as pandas Data Frame.')
    return d3


def add_node(node, parent):
    '''add_node will add a node to it's parent
    '''
    newNode = dict(node_id=node.id, children=[])
    parent["children"].append(newNode)
    if node.left: add_node(node.left, newNode)
    if node.right: add_node(node.right, newNode)


def label_tree(n,lookup):
    '''label tree will again recursively label the tree
    :param n: the root node, usually d3['children'][0]
    :param lookup: the node/id lookup
    '''
    if len(n["children"]) == 0:
        leaves = [lookup[n["node_id"]]]
    else:
        leaves = reduce(lambda ls, c: ls + label_tree(c,lookup), n["children"], [])
    del n["node_id"]
    n["name"] = name = "|||".join(sorted(map(str, leaves)))
    return leaves
