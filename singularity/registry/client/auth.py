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
import sys
import os

from singularity.registry.auth import (
    generate_signature,
    generate_credential,
    generate_timestamp
)


def authorize(self, names, payload=None, request_type="push"):
    '''Authorize a client based on encrypting the payload with the client
       token, which should be matched on the receiving server'''

    if self.secrets is not None:

        # Use the payload to generate a digest   push|collection|name|tag|user
        timestamp = generate_timestamp()
        credential = generate_credential(self.secrets['username'])
        credential = "%s/%s/%s" %(request_type,credential,timestamp)

        if payload is None:
            payload = "%s|%s|%s|%s|%s|" %(request_type,
                                          names['collection'],
                                          timestamp,
                                          names['image'],
                                          names['tag'])

        signature = generate_signature(payload,self.secrets['token'])
        return "SREGISTRY-HMAC-SHA256 Credential=%s,Signature=%s" %(credential,signature)
