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

from spython.main import Client
from singularity.logger import bot
from singularity.analysis.reproduce.criteria import *
from singularity.analysis.reproduce.levels import *
from singularity.analysis.reproduce.utils import (
    get_image_tar,
    extract_content,
    delete_image_tar,
    extract_guts
)
import datetime
import hashlib
import sys
import os
import io
import re


Client.quiet = True

def get_image_hashes(image_path, version=None, levels=None):
    '''get_image_hashes returns the hash for an image across all levels. This is the quickest,
    easiest way to define a container's reproducibility on each level.
    '''
    if levels is None:
        levels = get_levels(version=version)
    hashes = dict()
    for level_name,level_filter in levels.items():
        hashes[level_name] = get_image_hash(image_path,
                                            level_filter=level_filter)
    return hashes



def get_image_hash(image_path,
                   level=None,level_filter=None,
                   include_files=None,
                   skip_files=None,
                   version=None):

    '''get_image_hash will generate a sha1 hash of an image, depending on a level
    of reproducibility specified by the user. (see function get_levels for descriptions)
    the user can also provide a level_filter manually with level_filter (for custom levels)
    :param level: the level of reproducibility to use, which maps to a set regular
    expression to match particular files/folders in the image. Choices are in notes.
    :param skip_files: an optional list of files to skip
    :param include_files: an optional list of files to keep (only if level not defined)
    :param version: the version to use. If not defined, default is 2.3

    ::notes

    LEVEL DEFINITIONS
    The level definitions come down to including folders/files in the comparison. For files
    that Singularity produces on the fly that might be different (timestamps) but equal content
    (eg for a replication) we hash the content ("assess_content") instead of the file.
    '''    

    # First get a level dictionary, with description and regexp
    if level_filter is not None:
        file_filter = level_filter

    elif level is None:
        file_filter = get_level("RECIPE",
                                version=version,
                                include_files=include_files,
                                skip_files=skip_files)

    else:
        file_filter = get_level(level,version=version,
                                skip_files=skip_files,
                                include_files=include_files)
                
    file_obj, tar = get_image_tar(image_path)
    hasher = hashlib.md5()

    for member in tar:
        member_name = member.name.replace('.','',1)

        # For files, we either assess content, or include the file
        if member.isdir() or member.issym():
            continue
        elif assess_content(member,file_filter):
            content = extract_content(image_path,member.name)
            hasher.update(content)
        elif include_file(member,file_filter):
            buf = member.tobuf()
            hasher.update(buf)

    digest = hasher.hexdigest()

    # Close up / remove files
    try:
        file_obj.close()
    except:
        tar.close()
 
    if os.path.exists(file_obj):
        os.remove(file_obj)

    return digest


def get_content_hashes(image_path,
                       level=None,
                       regexp=None,
                       include_files=None,
                       tag_root=True,
                       level_filter=None,
                       skip_files=None,
                       version=None,
                       include_sizes=True):

    '''get_content_hashes is like get_image_hash, but it returns a complete dictionary 
    of file names (keys) and their respective hashes (values). This function is intended
    for more research purposes and was used to generate the levels in the first place.
    If include_sizes is True, we include a second data structure with sizes
    '''    

    if level_filter is not None:
        file_filter = level_filter

    elif level is None:
        file_filter = get_level("REPLICATE",version=version,
                                skip_files=skip_files,
                                include_files=include_files)

    else:
        file_filter = get_level(level,version=version,
                                skip_files=skip_files,
                                include_files=include_files)

    file_obj,tar = get_image_tar(image_path)

    results = extract_guts(image_path=image_path,
                           tar=tar,
                           file_filter=file_filter,
                           tag_root=tag_root,
                           include_sizes=include_sizes)

    delete_image_tar(file_obj, tar)
    return results



def get_image_file_hash(image_path):
    '''get_image_hash will return an md5 hash of the file based on a criteria level.
    :param level: one of LOW, MEDIUM, HIGH
    :param image_path: full path to the singularity image
    '''
    hasher = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
