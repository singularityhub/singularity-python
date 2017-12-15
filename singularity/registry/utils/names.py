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


def parse_image_name(image_name, tag=None, defaults=True, ext="img"):
    '''return a collection and repo name and tag
    for an image file.
    
    Parameters
    =========
    image_name: a user provided string indicating a collection,
                image, and optionally a tag.
    tag: optionally specify tag as its own argument
         over-rides parsed image tag
    defaults: use defaults "latest" for tag and "library"
              for collection. 
    '''
    result = dict()
    image_name = image_name.replace('.img', '').lower()
    image_name = re.split('/', image_name, 1)

    # User only provided an image
    if len(image_name) == 1:
        collection = ''
        if defaults is True:
            collection = "library"
        image_name = image_name[0]

    # Collection and image provided
    elif len(image_name) >= 2:
        collection = image_name[0]
        image_name = image_name[1]
    
    # Is there a tag?
    image_name = image_name.split(':')

    # No tag in provided string
    if len(image_name) > 1: 
        tag = image_name[1]
    image_name = image_name[0]
    
    # If still no tag, use default or blank
    if tag is None and defaults is True:
        tag = "latest"
    
    if tag is not None:
        uri = "%s/%s:%s" % (collection, image_name, tag)
        storage = "%s/%s-%s.%s" % (collection, image_name, tag, ext)
    else:
        uri = "%s/%s" % (collection, image_name)
        storage = "%s/%s.%s" % (collection, image_name, ext)

    result = {"collection": collection,
              "image": image_name,
              "tag": tag,
              "storage": storage,
              "uri": uri}
    return result
