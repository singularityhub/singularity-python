#!/usr/bin/env python

'''
utils.py: general http functions (utils) for som api

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

import requests
import os
import tempfile
import sys


def prepare_url(name, get_type='container'):
    '''get a container/collection or return None.
    '''
    get_type = get_type.lower().replace(' ','')

    result = None
    image = parse_container_name(name)

    if image['user'] is not None and image['repo_name'] is not None:        
        url = "%s/%s/%s" %(get_type,
                           image['user'],
                           image['repo_name'])

        # Only add tag for containers, not collections
        if image['repo_tag'] is not None and get_type != "collection":
            url = "%s:%s" %(url,image['repo_tag'])

    return url


######################################################################
# OS/IO and Formatting Functions
######################################################################


def is_number(container_name):
    '''is_number determines if the user is providing a singularity hub
    number (meaning the id of an image to download) vs a full name)
    '''
    if isinstance(container_name,dict):
        return False
    try:
        float(container_name)
        return True
    except ValueError:
        return False


def parse_container_name(image):
    '''parse_container_name will return a json structure with a repo name, tag, user.
    '''
    container_name = image
    if not is_number(image):
        image = image.replace(' ','')

    # If the user provided a number (unique id for an image), return it
    if is_number(image) == True:
        bot.info("Numeric image ID %s found.", image)
        return int(image)

    image = image.split('/')

    # If there are two parts, we have username with repo (and maybe tag)
    if len(image) >= 2:
        user = image[0]
        image = image[1]

    # Otherwise, we trigger error (not supported just usernames yet)
    else:
        bot.error('You must specify a repo name and username, %s is not valid' %container_name)
        sys.exit(1)

    # Now split the name by : in case there is a tag
    image = image.split(':')
    if len(image) == 2:
        repo_name = image[0]
        repo_tag = image[1]

    # Otherwise, assume latest of an image
    else:
        repo_name = image[0]
        repo_tag = "latest"

    bot.info("User: %s" %user)
    bot.info("Repo Name: %s" %repo_name)
    bot.info("Repo Tag: %s" %repo_tag)

    parsed = {'repo_name':repo_name,
              'repo_tag':repo_tag,
              'user':user }

    return parsed



def get_image_name(manifest,extension='simg', use_commit=False, use_hash=False):
    '''get_image_name will return the image name for a manifest. The user
       can name based on a hash or commit, or a name with the collection,
       namespace, branch, and tag.
    '''
    if use_hash:
        image_name = "%s.%s" %(manifest['version'], extension)

    elif use_commit:
        image_name = "%s.%s" %(manifest['commit'], extension)

    else:
        image_name = "%s-%s-%s.%s" %(manifest['name'].replace('/','-'),
                                     manifest['branch'].replace('/','-'),
                                     manifest['tag'].replace('/',''),
                                     extension)
            
    bot.info("Singularity Hub Image: %s" %image_name)
    return image_name
