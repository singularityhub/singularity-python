'''
auth.py: authentication functions for singularity hub api
         currently no token / auth for private collections

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
    ts = datetime.now()
    ts = ts.replace(tzinfo=timezone.utc)
    return ts.strftime('%Y%m%dT%HZ')


def generate_credential(s):
    '''basic_auth_header will return a base64 encoded header object to
    :param username: the username
    '''
    if sys.version_info[0] >= 3:
        s = bytes(s, 'utf-8')
        credentials = base64.b64encode(s).decode('utf-8')
    else:
        credentials = base64.b64encode(s)
    return credentials


def read_client_secrets(secrets=None,required=True):

    # If token file not provided, check environment
    if secrets is None:
        secrets = os.environ.get("SREGISTRY_CLIENT_SECRETS")

    # Fall back to default
    if secrets is None:
        userhome = pwd.getpwuid(os.getuid())[5]
        secrets = "%s/.sregistry" % (userhome)

    if secrets is not None:
        if os.path.exists(secrets):
            return read_json(secrets)

    message = 'Client secrets file not found at %s or $SREGISTRY_CLIENT_SECRETS.' %secrets
    if required:
        bot.error(message)
        sys.exit(1)

    bot.warning(message)
    return None


def generate_header_signature(secret, payload, request_type):
    '''Authorize a client based on encrypting the payload with the client
       secret, timestamp, and other metadata
     '''

    # Use the payload to generate a digest   push|collection|name|tag|user
    timestamp = generate_timestamp()
    credential = "%s/%s" %(request_type,timestamp)

    signature = generate_signature(payload,secret)
    return "SREGISTRY-HMAC-SHA256 Credential=%s,Signature=%s" %(credential,signature)
