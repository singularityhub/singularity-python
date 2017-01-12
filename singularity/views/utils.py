#!/usr/bin/env python

'''
singularity: views/utils.py: part of singularity package
utility functions for views

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
import sys
import tempfile


def get_container_contents(container=None,gets=None,split_delim=None,image_package=None):
    '''get_container_contents will return a list of folders and or files
    for a container. The environmental variable SINGULARITY_HUB being set
    means that container objects are referenced instead of packages
    :param container: the container to get content for
    :param gets: a list of file names to return, without parent folders
    :param split_delim: if defined, will split text by split delimiter
    :param image_package: if defined, user has provided an image_package
    '''
    if container == None and image_package == None:
        bot.logger.error("You must define an image package or container.")
        sys.exit(1)

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
        tmpdir = tempfile.mkdtemp()
        if image_package == None:
            image_package = package(image_path=container,
                                    output_folder=tmpdir,
                                    runscript=False,
                                    software=True,
                                    remove_image=True)
     
        guts = load_package(image_package,get=gets)
        shutil.rmtree(tmpdir)

    # Visualization deployed by singularity hub
    else:   
        
        # user has provided a package, but not a container
        if container == None:
            guts = load_package(image_package,get=gets)

        # user has provided a container, but not a package
        else:
            for sfile in container.files:
                for gut_key in gets:        
                    if os.path.basename(sfile['name']) == gut_key:
                        if split_delim == None:
                            guts[gut_key] = requests.get(sfile['mediaLink']).text
                        else:
                            guts[gut_key] = requests.get(sfile['mediaLink']).text.split(split_delim)

    return guts
