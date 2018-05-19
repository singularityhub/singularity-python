'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

import os
import re
from singularity.logger import bot
from singularity.utils import get_installdir
from singularity.package import get_container_contents
from singularity.analysis.reproduce import (
    get_image_tar,
    delete_image_tar
)

from .metrics import information_coefficient

import pandas


###################################################################################
# CONTAINER COMPARISONS ###########################################################
###################################################################################

def container_similarity_vector(container1=None,packages_set=None,by=None):
    '''container similarity_vector is similar to compare_packages, but intended
    to compare a container object (singularity image or singularity hub container)
    to a list of packages. If packages_set is not provided, the default used is 
    'docker-os'. This can be changed to 'docker-library', or if the user wants a custom
    list, should define custom_set.
    :param container1: singularity image or singularity hub container.
    :param packages_set: a name of a package set, provided are docker-os and docker-library
    :by: metrics to compare by (files.txt and or folders.txt)
    '''

    if by == None:
        by = ['files.txt']

    if not isinstance(by,list):
        by = [by]
    if not isinstance(packages_set,list):
        packages_set = [packages_set]

    comparisons = dict()

    for b in by:
        bot.debug("Starting comparisons for %s" %b)
        df = pandas.DataFrame(columns=packages_set)
        for package2 in packages_set:
            sim = calculate_similarity(container1=container1,
                                       image_package2=package2,
                                       by=b)[b]
           
            name1 = os.path.basename(package2).replace('.img.zip','')
            bot.debug("container vs. %s: %s" %(name1,sim))
            df.loc["container",package2] = sim
        df.columns = [os.path.basename(x).replace('.img.zip','') for x in df.columns.tolist()]
        comparisons[b] = df
    return comparisons


def compare_singularity_images(image_paths1,image_paths2=None):
    '''compare_singularity_images is a wrapper for compare_containers to compare
    singularity containers. If image_paths2 is not defined, pairwise comparison is done
    with image_paths1
    '''
    repeat = False
    if image_paths2 is None:
        image_paths2 = image_paths1
        repeat = True

    if not isinstance(image_paths1,list):
        image_paths1 = [image_paths1]

    if not isinstance(image_paths2,list):
        image_paths2 = [image_paths2]

    dfs = pandas.DataFrame(index=image_paths1,columns=image_paths2)

    comparisons_done = []
    for image1 in image_paths1:
        fileobj1,tar1 = get_image_tar(image1)

        members1 = [x.name for x in tar1]
        for image2 in image_paths2:
            comparison_id = [image1,image2]
            comparison_id.sort()
            comparison_id = "".join(comparison_id)
            if comparison_id not in comparisons_done:
                if image1 == image2:
                    sim = 1.0
                else:
                    fileobj2,tar2 = get_image_tar(image2)
                    members2 = [x.name for x in tar2]
                    c = compare_lists(members1,members2)
                    sim = information_coefficient(c['total1'],c['total2'],c['intersect'])
                    delete_image_tar(fileobj2, tar2)
                        
                dfs.loc[image1,image2] = sim
                if repeat:
                    dfs.loc[image2,image1] = sim
                comparisons_done.append(comparison_id)
        delete_image_tar(fileobj1, tar1)
    return dfs


def compare_containers(container1=None,container2=None,by=None,
                       image_package1=None,image_package2=None):
    '''compare_containers will generate a data structure with common and unique files to
    two images. If environmental variable SINGULARITY_HUB is set, will use container
    database objects.
    :param container1: first container for comparison
    :param container2: second container for comparison if either not defined must include
    :param image_package1: a packaged container1 (produced by package)
    :param image_package2: a packaged container2 (produced by package)
    :param by: what to compare, one or more of 'files.txt' or 'folders.txt'
    default compares just files
    '''
    if by == None:
        by = ["files.txt"]
    if not isinstance(by,list):
        by = [by]

    # Get files and folders for each
    container1_guts = get_container_contents(gets=by,
                                             split_delim="\n",
                                             container=container1,
                                             image_package=image_package1)
    container2_guts = get_container_contents(gets=by,
                                             split_delim="\n",
                                             container=container2,
                                             image_package=image_package2)

    # Do the comparison for each metric
    comparisons = dict()
    for b in by:
        if b in container1_guts and b in container2_guts:
            comparisons[b] = compare_lists(container1_guts[b],container2_guts[b])

    return comparisons


def compare_lists(list1,list2):
    '''compare lists is the lowest level that drives compare_containers and
    compare_packages. It returns a comparison object (dict) with the unique,
    total, and intersecting things between two lists
    :param list1: the list for container1
    :param list2: the list for container2
    '''
    intersect = list(set(list1).intersection(list2))
    unique1 = list(set(list1).difference(list2))
    unique2 = list(set(list2).difference(list1))

    # Return data structure
    comparison = {"intersect":intersect,
                  "unique1": unique1,
                  "unique2": unique2,
                  "total1": len(list1),
                  "total2": len(list2)}
    return comparison
    

def calculate_similarity(container1=None,container2=None,image_package1=None,
                         image_package2=None,by="files.txt",comparison=None,
                         metric=None):
    '''calculate_similarity will calculate similarity of two containers by files content, default will calculate
    2.0*len(intersect) / total package1 + total package2
    :param container1: container 1
    :param container2: container 2 must be defined or
    :param image_package1: a zipped package for image 1, created with package
    :param image_package2: a zipped package for image 2, created with package
    :param by: the one or more metrics (eg files.txt) list to use to compare
    :param metric: a function to take a total1, total2, and intersect count 
    (we can make this more general if / when more are added)
     valid are currently files.txt or folders.txt
    :param comparison: the comparison result object for the tree. If provided,
    will skip over function to obtain it.
    '''
    if not isinstance(by,list):
        by = [by]

    if metric is None:
        metric = information_coefficient

    if comparison == None:
        comparison = compare_containers(container1=container1,
                                        container2=container2,
                                        image_package1=image_package1,
                                        image_package2=image_package2,
                                        by=by)
    scores = dict()

    for b in by:
        scores[b] = metric(total1=comparison[b]['total1'],
                           total2=comparison[b]['total2'],
                           intersect=comparison[b]["intersect"])
    return scores


###################################################################################
# PACKAGE COMPARISONS #############################################################
###################################################################################

def compare_packages(packages_set1=None,packages_set2=None,by=None):
    '''compare_packages will compare one image or package to one image or package. If
    the folder isn't specified, the default singularity packages (included with install)
    will be used (os vs. docker library). Images will take preference over packages
    :param packages_set1: a list of package files not defined uses docker-library
    :param packages_set2: a list of package files, not defined uses docker-os
    :by: metrics to compare by (files.txt and or folders.txt)
    ''' 
    if packages_set1 == None:
        packages_set1 = get_packages('docker-library')
    if packages_set2 == None:
        packages_set2 = get_packages('docker-os')

    if by == None:
        by = ['files.txt']

    if not isinstance(by,list):
        by = [by]
    if not isinstance(packages_set1,list):
        packages_set1 = [packages_set1]
    if not isinstance(packages_set2,list):
        packages_set2 = [packages_set2]

    comparisons = dict()

    for b in by:
        bot.debug("Starting comparisons for %s" %b)
        df = pandas.DataFrame(index=packages_set1,columns=packages_set2)
        for package1 in packages_set1:
            for package2 in packages_set2:
                if package1 != package2:
                    sim = calculate_similarity(image_package1=package1,
                                               image_package2=package2,
                                               by=b)[b]
                else:
                    sim = 1.0

                name1 = os.path.basename(package1).replace('.img.zip','')
                name2 = os.path.basename(package2).replace('.img.zip','')
                bot.debug("%s vs. %s: %s" %(name1,name2,sim))
                df.loc[package1,package2] = sim
        df.index = [os.path.basename(x).replace('.img.zip','') for x in df.index.tolist()]
        df.columns = [os.path.basename(x).replace('.img.zip','') for x in df.columns.tolist()]
        comparisons[b] = df
    return comparisons

