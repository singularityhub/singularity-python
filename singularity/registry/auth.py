'''
auth.py: authentication functions for singularity hub api
         currently no token / auth for private collections

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
