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
