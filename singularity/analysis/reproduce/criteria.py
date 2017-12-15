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

from singularity.logger import bot
import os
import re


def include_file(member,file_filter):
    '''include_file will look at a path and determine
    if it matches a regular expression from a level
    '''
    member_path = member.name.replace('.','',1)

    if len(member_path) == 0:
        return False

    # Does the filter skip it explicitly?
    if "skip_files" in file_filter:
        if member_path in file_filter['skip_files']:
            return False

    # Include explicitly?
    if "include_files" in file_filter:
        if member_path in file_filter['include_files']:
            return True

    # Regular expression?
    if "regexp" in file_filter:
        if re.search(file_filter["regexp"],member_path):
            return True
    return False


def is_root_owned(member):
    '''assess if a file is root owned, meaning "root" or user/group 
    id of 0'''
    if member.uid == 0 or member.gid == 0:
        return True
    elif member.uname == 'root' or member.gname == 'root':
        return True
    return False
    

def assess_content(member,file_filter):
    '''Determine if the filter wants the file to be read for content.
    In the case of yes, we would then want to add the content to the
    hash and not the file object.
    '''
    member_path = member.name.replace('.','',1)

    if len(member_path) == 0:
        return False

    # Does the filter skip it explicitly?
    if "skip_files" in file_filter:
        if member_path in file_filter['skip_files']:
            return False

    if "assess_content" in file_filter:
        if member_path in file_filter['assess_content']:
            return True
    return False
