'''

Copyright (c) 2017 Vanessa Sochat, All Rights Reserved

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

from singularity.utils import read_json

import os
import re
import requests
import fnmatch
import tempfile


def parse_header(recipe, header="from", remove_header=True):
    '''take a recipe, and return the complete header, line. If
    remove_header is True, only return the value.
    '''
    parsed_header = None
    fromline = [x for x in recipe.split('\n') if "%s:" %header in x.lower()]
    if len(fromline) > 0:
        fromline = fromline[0]
        parsed_header = fromline.strip()
    if remove_header is True:
        parsed_header = fromline.split(':', 1)[-1].strip()
    return parsed_header               



def find_recipes(folders,pattern=None, base=None):
    '''find recipes will use a list of base folders, files,
    or patterns over a subset of content to find recipe files
    (indicated by Starting with Singularity
    :param base: if defined, consider collection folders below
    this level.
    '''    
    if folders is None:
        folders = os.getcwd()

    if not isinstance(folders,list):
        folders = [folders]

    manifest = dict()
    for base_folder in folders:

        # For file, return the one file
        custom_pattern=None
        if os.path.isfile(base_folder):  # updates manifest
            manifest = find_single_recipe(filename=base_folder,
                                          pattern=pattern,
                                          manifest=manifest)
            continue

        # The user likely provided a custom pattern
        elif not os.path.isdir(base_folder):
            custom_pattern = base_folder.split('/')[-1:][0]
            base_folder = "/".join(base_folder.split('/')[0:-1])
        
        # If we don't trigger loop, we have directory
        manifest = find_folder_recipes(base_folder=base_folder,
                                       pattern=custom_pattern or pattern,
                                       manifest=manifest,
                                       base=base)
        
    return manifest


def find_folder_recipes(base_folder,pattern=None, manifest=None, base=None):
    '''find folder recipes will find recipes based on a particular pattern.
    If base is defined, consider folders under this level as contrainer collections
    '''
    if manifest is None:
        manifest = dict()

    if pattern is None:
        pattern = "Singularity*"

    for root, dirnames, filenames in os.walk(base_folder):

        for filename in fnmatch.filter(filenames, pattern):

            container_path = os.path.join(root, filename)
            if base is not None:
                container_base = container_path.replace(base,'').strip('/')
                collection = container_base.split('/')[0]
                recipe = os.path.basename(container_base)
                container_uri = "%s/%s" %(collection,recipe)
            else:
                container_uri = '/'.join(container_path.strip('/').split('/')[-2:])

            add_container = True

            # Add the most recently updated container
            if container_uri in manifest:
                if manifest[container_uri]['modified'] > os.path.getmtime(container_path):
                    add_container = False

            if add_container:
                manifest[container_uri] = {'path': os.path.abspath(container_path),
                                           'modified':os.path.getmtime(container_path)}

    return manifest


def find_single_recipe(filename,pattern=None,manifest=None):
    '''find_single_recipe will parse a single file, and if valid,
    return an updated manifest'''

    if pattern is None:
        pattern = "Singularity*"

    recipe = None
    file_basename = os.path.basename(filename)
    if fnmatch.fnmatch(file_basename,pattern):
        recipe = {'path': os.path.abspath(filename),
                  'modified':os.path.getmtime(filename)}

    if manifest is not None and recipe is not None:
        container_uri = '/'.join(filename.split('/')[-2:])
        if container_uri in manifest:
            if manifest[container_uri]['modified'] < os.path.getmtime(filename):
                manifest[container_uri] = recipe
        else:
            manifest[container_uri] = recipe
        return manifest
        
    return recipe
