'''
criteria.py: part of singularity package, functions to assess
  reproducibility of images

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
