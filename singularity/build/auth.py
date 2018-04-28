'''

The MIT License (MIT)

Copyright (c) 2016-2018 Vanessa Sochat

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
from singularity.utils import (
    read_json,
    write_json
)

from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
import os
import pwd
import requests
import sys


def encode(item):
    '''make sure an item is bytes for the digest
    '''
    if not isinstance(item,bytes):
        item = item.encode('utf-8')
    return item


def generate_signature(payload, secret):
    '''use an endpoint specific payload and client secret to generate
    a signature for the request'''
    payload = encode(payload)
    secret = encode(secret)
    return hmac.new(secret, digestmod=hashlib.sha256,
                    msg=payload).hexdigest()


def generate_timestamp():
    ts = datetime.now(timezone.utc)
    return ts.strftime('%Y%m%dT%HZ')


def generate_header_signature(secret, payload, request_type):
    '''Authorize a client based on encrypting the payload with the client
       secret, timestamp, and other metadata
     '''

    # Use the payload to generate a digest   push|collection|name|tag|user
    timestamp = generate_timestamp()
    credential = "%s/%s" %(request_type,timestamp)

    signature = generate_signature(payload,secret)
    return "SREGISTRY-HMAC-SHA256 Credential=%s,Signature=%s" %(credential, signature)
