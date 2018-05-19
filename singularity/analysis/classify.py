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
    compare_containers,
    container_similarity_vector
)

from singularity.package import get_container_contents
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


###################################################################################
# TAGGING #########################################################################
###################################################################################


def get_tags(container=None,
             search_folders=None,
             file_list=None,
             return_unique=True):

    '''get tags will return a list of tags that describe the software in an image,
    meaning inside of a paricular folder. If search_folder is not defined, uses lib
    :param container: if provided, will use container as image. Can also provide
    :param image_package: if provided, can be used instead of container
    :param search_folders: specify one or more folders to look for tags 
    :param file_list: the list of files
    :param return_unique: return unique files in folders. Default True.
    Default is 'bin'

    ::notes
  
    The algorithm works as follows:
      1) first compare package to set of base OS (provided with shub)
      2) subtract the most similar os from image, leaving "custom" files
      3) organize custom files into dict based on folder name
      4) return search_folders as tags

    '''
    if file_list is None:
        file_list = get_container_contents(container, split_delim='\n')['all']

    if search_folders == None:
        search_folders = 'bin'

    if not isinstance(search_folders,list):
        search_folders = [search_folders]

    tags = []
    for search_folder in search_folders:
        for file_name in file_list:
            if search_folder in file_name:
                tags.append(file_name)

    if return_unique == True:
        tags = list(set(tags))
    return tags


###################################################################################
# COUNTING ########################################################################
###################################################################################

        
def file_counts(container=None, 
                patterns=None, 
                image_package=None, 
                file_list=None):

    '''file counts will return a list of files that match one or more regular expressions.
    if no patterns is defined, a default of readme is used. All patterns and files are made
    case insensitive.

    Parameters
    ==========
    :param container: if provided, will use container as image. Can also provide
    :param image_package: if provided, can be used instead of container
    :param patterns: one or more patterns (str or list) of files to search for.
    :param diff: the difference between a container and it's parent OS from get_diff
    if not provided, will be generated.

    '''
    if file_list is None:
        file_list = get_container_contents(container, split_delim='\n')['all']

    if patterns == None:
        patterns = 'readme'

    if not isinstance(patterns,list):
        patterns = [patterns]

    count = 0
    for pattern in patterns:
        count += len([x for x in file_list if re.search(pattern.lower(),x.lower())])
    bot.info("Total files matching patterns is %s" %count)
    return count


def extension_counts(container=None, file_list=None, return_counts=True):
    '''extension counts will return a dictionary with counts of file extensions for
    an image.
    :param container: if provided, will use container as image. Can also provide
    :param image_package: if provided, can be used instead of container
    :param file_list: the complete list of files
    :param return_counts: return counts over dict with files. Default True
    '''
    if file_list is None:
        file_list = get_container_contents(container, split_delim='\n')['all']

    extensions = dict()
    for item in file_list:
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
