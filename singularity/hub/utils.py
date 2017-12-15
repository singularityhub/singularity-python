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
