'''

auth.py: authorization functions for client

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
