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
from singularity.analysis.compare import (
    compare_packages,
    compare_containers,
    container_similarity_vector
)

from singularity.package import (
    get_container_contents,
    package as make_package,
    get_package_base
)
from singularity.utils import (
    get_installdir,
    remove_uri,
    read_file
)

from singularity.analysis.utils import (
    update_dict,
    update_dict_sum
)

import sys



def get_diff(container=None,image_package=None):
    '''get diff will return a dictionary of folder paths and files that
    are in an image or package vs. all standard operating systems. The
    algorithm is explained below. 
    :param container: if provided, will use container as image. Can also provide
    :param image_package: if provided, can be used instead of container

    ::notes
  
    The algorithm works as follows:
      1) first compare package to set of base OS (provided with shub)
      2) subtract the most similar os from image, leaving "custom" files
      3) organize custom files into dict based on folder name

    '''
    
    # Find the most similar os
    most_similar = estimate_os(image_package=image_package,container=container)
    similar_package = "%s/docker-os/%s.img.zip" %(get_package_base(),most_similar)

    comparison = compare_containers(image_package1=image_package,
                                    container1=container,
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
# OPERATING SYSTEMS ###############################################################
###################################################################################


def estimate_os(container=None,image_package=None,return_top=True):
    '''estimate os will compare a package to singularity python's database of
    operating system images, and return the docker image most similar
    :param return_top: return only the most similar (estimated os) default True
    :param image_package: the package created from the image to estimate.
    FIGURE OUT WHAT DATA WE NEED
    '''
    if image_package == None:

        SINGULARITY_HUB = os.environ.get('SINGULARITY_HUB',"False")

        # Visualization deployed local or elsewhere
        if SINGULARITY_HUB == "False":
            image_package = make_package(container,remove_image=True)
            comparison = compare_packages(packages_set1=[image_package])['files.txt'].transpose()
        else:
            comparison = container_similarity_vector(container1=container)['files.txt'].transpose()

    else:
        comparison = compare_packages(packages_set1=[image_package])['files.txt'].transpose()

    comparison.columns = ['SCORE']
    try:
        most_similar = comparison['SCORE'].idxmax()
    except:
        most_similar = comparison['SCORE'].values.argmax()
        most_similar = comparison.index.tolist()[most_similar]

    print("Most similar OS found to be ", most_similar)    
    if return_top == True:
        return most_similar
    return comparison



###################################################################################
# TAGGING #########################################################################
###################################################################################


def get_tags(container=None,image_package=None,search_folders=None,diff=None,
             return_unique=True):
    '''get tags will return a list of tags that describe the software in an image,
    meaning inside of a paricular folder. If search_folder is not defined, uses lib
    :param container: if provided, will use container as image. Can also provide
    :param image_package: if provided, can be used instead of container
    :param search_folders: specify one or more folders to look for tags 
    :param diff: the difference between a container and it's parent OS from get_diff
    if None, will be derived.
    :param return_unique: return unique files in folders. Default True.
    Default is 'bin'

    ::notes
  
    The algorithm works as follows:
      1) first compare package to set of base OS (provided with shub)
      2) subtract the most similar os from image, leaving "custom" files
      3) organize custom files into dict based on folder name
      4) return search_folders as tags
    '''
    if diff == None:
        diff = get_diff(container=container,
                        image_package=image_package)

    if search_folders == None:
        search_folders = 'bin'

    if not isinstance(search_folders,list):
        search_folders = [search_folders]

    tags = []
    for search_folder in search_folders:
        if search_folder in diff:
            bot.info("Adding tags for folder %s" %search_folder)
            tags = tags + diff[search_folder]
        else:
            bot.info("Did not find folder %s in difference." %search_folder)

    if return_unique == True:
        tags = list(set(tags))
    return tags


###################################################################################
# COUNTING ########################################################################
###################################################################################

        
def file_counts(container=None,patterns=None,image_package=None,diff=None):
    '''file counts will return a list of files that match one or more regular expressions.
    if no patterns is defined, a default of readme is used. All patterns and files are made
    case insensitive.
    :param container: if provided, will use container as image. Can also provide
    :param image_package: if provided, can be used instead of container
    :param patterns: one or more patterns (str or list) of files to search for.
    :param diff: the difference between a container and it's parent OS from get_diff
    if not provided, will be generated.
    '''
    if diff == None:
        diff = get_diff(container=container,
                        image_package=image_package)

    if patterns == None:
        patterns = 'readme'

    if not isinstance(patterns,list):
        patterns = [patterns]

    count = 0
    for folder, items in diff.items():
        for pattern in patterns:
            count += len([x for x in items if re.search(pattern.lower(),x.lower())])
    bot.info("Total files matching patterns is %s" %count)
    return count


def extension_counts(container=None,image_package=None,diff=None,return_counts=True):
    '''extension counts will return a dictionary with counts of file extensions for
    an image.
    :param container: if provided, will use container as image. Can also provide
    :param image_package: if provided, can be used instead of container
    :param diff: the difference between a container and it's parent OS from get_diff
    :param return_counts: return counts over dict with files. Default True
    '''
    if diff == None:
        diff = get_diff(container=container,
                        image_package=image_package)

    extensions = dict()
    for folder, items in diff.items():
        for item in items:
            filename,ext = os.path.splitext(item)
            if ext == '':
                if return_counts == False:
                    extensions = update_dict(extensions,'no-extension',item)
                else:
                    extensions = update_dict_sum(extensions,'no-extension')
            else:
                if return_counts == False:
                    extensions = update_dict(extensions,ext,item)
                else:
                    extensions = update_dict_sum(extensions,ext)

    return extensions
