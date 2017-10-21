'''

push.py: push functions for sregistry client

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
from singularity.registry.utils import parse_image_name

import sys
import os

from singularity.registry.auth import (
    generate_signature,
    generate_credential,
    generate_timestamp
)


def remove(self, image, force=False):
    '''delete an image to Singularity Registry'''

    q = parse_image_name(image)
    url = '%s/container/%s/%s:%s' % (self.base, q["collection"], q["image"], q["tag"])

    SREGISTRY_EVENT = self.authorize(request_type="delete", names=q)
    headers = {'Authorization': SREGISTRY_EVENT }
    self.update_headers(fields=headers)

    continue_delete = True
    if force is False:
        response = input("Are you sure you want to delete %s?" % q['uri'])
        while len(response) < 1 or response[0].lower().strip() not in "ynyesno":
            response = input("Please answer yes or no: ")
        if response[0].lower().strip() in "no":
            continue_delete = False

    if continue_delete is True:
        response = self.delete(url)
        message = self.read_response(response)
        bot.info("Response %s, %s" %(response.status_code, message))

    else:
        bot.info("Delete cancelled.")
