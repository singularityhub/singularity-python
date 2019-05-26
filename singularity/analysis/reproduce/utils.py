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
from spython.utils import get_singularity_version
from .criteria import (
    assess_content, 
    include_file,
    is_root_owned
)
from .levels import get_level
from singularity.logger import bot
import hashlib
import tarfile
import tempfile
import sys
import os
import re
import io

Client.quiet = True

def extract_guts(image_path,
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

    # Export the image
    sandbox = Client.export(image_path)

    # If it's tar, extract
    if sandbox.endswith('tar'):
        with tarfile.open(sandbox) as tar:
            sandbox = os.path.join(os.path.dirname(sandbox), 'sandbox') 
            tar.extractall(path=sandbox)

    # Recursively walk through sandbox
    for root, dirnames, filenames in os.walk(sandbox):
        for filename in filenames:
            member_name = os.path.join(root, filename)
            allfiles.append(member_name)
            included = False

            # Skip over directories and symbolic links
            if os.path.isdir(member_name) or os.path.islink(member_name):
                continue

            # If we have flagged to include, and not flagged to skip
            elif assess_content(member_name, file_filter):
                digest[member_name] = extract_content(member_name, return_hash=True)
                included = True
            elif include_file(member_name, file_filter):
                hasher = hashlib.md5()
                with open(member_name, 'rb') as filey:
                    buf = filey.read()
                    hasher.update(buf)
                digest[member_name] = hasher.hexdigest()
                included = True

            # Derive size, and if root owned
            if included:
                if include_sizes:
                    sizes[member_name] = os.stat(member_name).st_size
                if tag_root:
                    roots[member_name] = is_root_owned(member_name)

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
    byte_array = Client.export(image_path)
    file_object = io.BytesIO(byte_array)
    tar = tarfile.open(mode="r|*", fileobj=file_object)
    return (file_object, tar)

def create_tarfile(source_dir, output_filename=None):
    ''' create a tarfile from a source directory'''
    if output_filename == None:
        output_filename = "%s/tmptar.tar" %(tempfile.mkdtemp())
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    return output_filename


def get_image_tar(image_path):
    '''get an image tar, either written in memory or to
    the file system. file_obj will either be the file object,
    or the file itself.
    '''
    bot.debug('Generate file system tar...')

    if 'version 3' in get_singularity_version():
        sandbox = Client.export(image_path)
        file_obj = create_tarfile(sandbox)
    else:
        file_obj = Client.image.export(image_path=image_path)
        if file_obj is None:
            bot.exit("Error generating tar, exiting.")
            
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


def extract_content(member_name, return_hash=False):
    '''extract_content will extract content from an image using cat.
    If hash=True, a hash sum is returned instead
    '''
    if return_hash:
        hashy = hashlib.md5()

    # First try reading regular
    try:
        with open(member_name, 'r') as filey:
            content = filey.read()
    except:

        # Then try binary
        try:
            with open(member_name, 'rb') as filey:
                content = filey.read()
        except:
            return None

    if not isinstance(content, bytes):
        content = content.encode('utf-8')
        content = bytes(content)

    # If permissions don't allow read, return None
    if len(content) == 0:
        return None
    if return_hash:
        hashy.update(content)
        return hashy.hexdigest()
    return content
