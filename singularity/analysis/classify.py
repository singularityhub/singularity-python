#!/usr/bin/env python

'''
classify.py: part of singularity package
functions to tag and classify images

'''

from glob import glob
import json
import os
import re
import requests
from singularity.logman import bot
from singularity.analysis.compare import (
    compare_packages,
    compare_containers
)
from singularity.analysis.utils import get_package_base
from singularity.package import package as make_package
from singularity.utils import get_installdir
from singularity.views.utils import get_container_contents

from singularity.package import (
    load_package,
    package
)

import numpy
import pandas
import shutil
import sys
import tempfile
import zipfile



def get_diff(container=None,package=None,sudopw=None):
    '''get diff will return a dictionary of folder paths and files that
    are in an image or package vs. all standard operating systems. The
    algorithm is explained below. 
    :param container: if provided, will use container as image. Can also provide
    :param package: if provided, can be used instead of container
    :param sudopw: needed if a package isn't provided (will prompt user)

    ::notes
  
    The algorithm works as follows:
      1) first compare package to set of base OS (provided with shub)
      2) subtract the most similar os from image, leaving "custom" files
      3) organize custom files into dict based on folder name

    '''
    if package == None:
        package = make_package(container,remove_image=True,sudopw=sudopw)
    
    # Find the most similar os
    most_similar = estimate_os(package=package,sudopw=sudopw)    
    similar_package = "%s/docker-os/%s.img.zip" %(get_package_base(),most_similar)

    comparison = compare_containers(image_package1=package,
                                    image_package2=similar_package,
                                    by='files.txt')['files.txt']
 
    container_unique = comparison['unique1']

    # Try to organize files based on common folders:
    folders = dict()
    for file_path in container_unique:
        fileparts = file_path.split('/')
        if len(fileparts) >= 2:
            folder = fileparts[-2]
        else:
            folder = '/'
        filey = fileparts[-1]
        if folder in folders:
            folders[folder].append(filey)
        else:
            folders[folder] = [filey]

    return folders


###################################################################################
# TAGGING #########################################################################
###################################################################################


def estimate_os(container=None,package=None,sudopw=None,return_top=True):
    '''estimate os will compare a package to singularity python's database of
    operating system images, and return the docker image most similar
    :param return_top: return only the most similar (estimated os) default True
    :param package: the package created from the image to estimate.
    '''
    if package == None:
        package = make_package(container,remove_image=True,sudopw=sudopw)
    
    comparison = compare_packages(packages_set1=[package])['files.txt'].transpose()
    comparison.columns = ['SCORE']
    most_similar = comparison['SCORE'].idxmax()
    print("Most similar OS found to be ",most_similar)    
    if return_top == True:
        return most_similar
    return comparison


def get_tags(container=None,package=None,sudopw=None,search_folders=None):
    '''get tags will return a list of tags that describe the software in an image,
    meaning inside of a paricular folder. If search_folder is not defined, uses lib
    :param container: if provided, will use container as image. Can also provide
    :param package: if provided, can be used instead of container
    :param search_folders: specify one or more folders to look for tags 
    Default is 'bin'

    ::notes
  
    The algorithm works as follows:
      1) first compare package to set of base OS (provided with shub)
      2) subtract the most similar os from image, leaving "custom" files
      3) organize custom files into dict based on folder name
      4) return search_folders as tags
    '''
    folders = get_diff(container=container,
                       package=package,
                       sudopw=sudopw)

    if search_folders == None:
        search_folders = 'bin'

    if not isinstance(search_folders,list):
        search_folders = [search_folders]

    tags = []
    for search_folder in search_folders:
        if search_folder in folders:
            bot.logger.info("Adding tags for folder %s",search_folder)
            tags = tags + folders[search_folder]
        else:
            bot.logger.info("Did not find folder %s in difference.",search_folder)
    tags = numpy.unique(tags).tolist()
    return tags
