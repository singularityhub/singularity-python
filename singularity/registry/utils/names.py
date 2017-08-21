'''

Copyright (c) 2017 Vanessa Sochat, All Rights Reserved

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to dot so, subject to the following conditions:

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
