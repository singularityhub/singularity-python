'''
utils.py: part of singularity package, functions to assess
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

from singularity.cli import Singularity
from singularity.logger import bot
import hashlib
import tarfile
import sys
import os
import re
import io


def extract_guts(image_path,tar,file_filter,tag_root=True,include_sizes=True):
    '''extract the file guts from an in memory tarfile. The file is not closed.
       This should not be done for large images.
    :TODO: this should have a switch for a function to decide if we should
    read the memory in tar, or from fileystem
    '''

    cli = Singularity()
    results = dict()
    digest = dict()

    if tag_root:
        roots = dict()

    if include_sizes: 
        sizes = dict()

    for member in tar:
        member_name = member.name.replace('.','',1)
        included = False
        if member.isdir() or member.issym():
            continue
        elif assess_content(member,file_filter):
            digest[member_name] = extract_content(image_path,member.name,cli,return_hash=True)
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

    results['hashes'] = digest
    if include_sizes:
        results['sizes'] = sizes
    if tag_root:
        results['root_owned'] = roots
    return results



def get_memory_tar(image_path):
    '''get an in memory tar of an image (does not require sudo!)'''
    cli = Singularity()
    if "pancakes" in os.environ:
        del os.environ['pancakes']
    byte_array = cli.export(image_path)
    file_object = io.BytesIO(byte_array)
    tar = tarfile.open(mode="r|*", fileobj=file_object)
    return (file_object,tar)


def get_image_tar(image_path,write_file=True,S=None)
    '''get an image tar, either written in memory or to
    the file system.
    '''
    file_obj = None

    # Singularity 2.3 and up
    if not write_file False:
        file_obj,tar = get_memory_tar(image_path)

    # Singularity < version 2.3
    else:
        if S is None:
            S = Singularity()
        tmptar = S.export(image_path=image_path,old_version=True)
        tar = tarfile.open(tmptar)

    return file_obj, tar


def extract_content(image_path,member_name,cli=None,return_hash=False):
    '''extract_content will extract content from an image using cat.
    If hash=True, a hash sum is returned instead
    '''
    if member_name.startswith('./'):
        member_name = member_name.replace('.','',1)
    if return_hash:
        hashy = hashlib.md5()
    if cli == None:
        cli = Singularity()
    content = cli.execute(image_path,'cat %s' %(member_name))
    if not isinstance(content,bytes):
        content = bytes(content)
    # If permissions don't allow read, return None
    if len(content) == 0:
        return None
    if return_hash:
        hashy.update(content)
        return hashy.hexdigest()
    return content
