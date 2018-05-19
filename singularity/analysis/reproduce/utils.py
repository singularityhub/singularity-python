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
from .criteria import (
    assess_content, 
    include_file,
    is_root_owned
)
from .levels import get_level
from singularity.logger import bot
import hashlib
import tarfile
import sys
import os
import re
import io

Client.quiet = True

def extract_guts(image_path,
                 tar,
                 file_filter=None,
                 tag_root=True,
                 include_sizes=True):

    '''extract the file guts from an in memory tarfile. The file is not closed.
       This should not be done for large images.
    '''
    if file_filter is None:
        file_filter = get_level('IDENTICAL')

    results = dict()
    digest = dict()
    allfiles = []

    if tag_root:
        roots = dict()

    if include_sizes: 
        sizes = dict()

    for member in tar:
        member_name = member.name.replace('.','',1)
        allfiles.append(member_name)
        included = False
        if member.isdir() or member.issym():
            continue
        elif assess_content(member,file_filter):
            digest[member_name] = extract_content(image_path, member.name, return_hash=True)
            included = True
        elif include_file(member,file_filter):
            hasher = hashlib.md5()
            buf = member.tobuf()
            hasher.update(buf)
            digest[member_name] = hasher.hexdigest()
            included = True
        if included:
            if include_sizes:
                sizes[member_name] = member.size
            if tag_root:
                roots[member_name] = is_root_owned(member)

    results['all'] = allfiles
    results['hashes'] = digest
    if include_sizes:
        results['sizes'] = sizes
    if tag_root:
        results['root_owned'] = roots
    return results



def get_memory_tar(image_path):
    '''get an in memory tar of an image. Use carefully, not as reliable
       as get_image_tar
    '''
    byte_array = Client.image.export(image_path)
    file_object = io.BytesIO(byte_array)
    tar = tarfile.open(mode="r|*", fileobj=file_object)
    return (file_object,tar)


def get_image_tar(image_path):
    '''get an image tar, either written in memory or to
    the file system. file_obj will either be the file object,
    or the file itself.
    '''
    bot.debug('Generate file system tar...')   
    file_obj = Client.image.export(image_path=image_path)
    if file_obj is None:
        bot.error("Error generating tar, exiting.")
        sys.exit(1)
    tar = tarfile.open(file_obj)
    return file_obj, tar


def delete_image_tar(file_obj, tar):
    '''delete image tar will close a file object (if extracted into
    memory) or delete from the file system (if saved to disk)'''
    try:
        file_obj.close()
    except:
        tar.close()
    if os.path.exists(file_obj):
        os.remove(file_obj)
        deleted = True
        bot.debug('Deleted temporary tar.')   
    return deleted


def extract_content(image_path, member_name, return_hash=False):
    '''extract_content will extract content from an image using cat.
    If hash=True, a hash sum is returned instead
    '''
    if member_name.startswith('./'):
        member_name = member_name.replace('.','',1)
    if return_hash:
        hashy = hashlib.md5()

    try:
        content = Client.execute(image_path,'cat %s' %(member_name))
    except:
        return None

    if not isinstance(content,bytes):
        content = content.encode('utf-8')
        content = bytes(content)

    # If permissions don't allow read, return None
    if len(content) == 0:
        return None
    if return_hash:
        hashy.update(content)
        return hashy.hexdigest()
    return content
