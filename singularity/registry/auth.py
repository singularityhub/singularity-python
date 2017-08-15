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
import os
import sys

from singularity.utils import (
    read_json,
    write_json
)

import os
import json
import pwd
import requests
import datetime
import hashlib
import hmac
import sys


def generate_signature(payload, secret):
    '''use an endpoint specific payload and client secret to generate
    a signature for the request'''
    timestamp = datetime.datetime.utcnow().strftime('%b-%d-%G-%H-%M')
    payload = ("%s|%s|%s" %(payload,secret,timestamp)).encode('utf-8')
    return hmac.new(payload, digestmod=hashlib.sha256,
                    msg=payload).hexdigest()

def generate_timestamp():
    return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


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
        secrets = os.environ.get("SREGISTRY_CLIENT_SECRETS", None)

    # Fall back to default
    if secrets is None:
        userhome = pwd.getpwuid(os.getuid())[5]
        secrets = "%s/.sregistry" % (userhome)

    if secrets is not None:
        if os.path.exists(secrets):
            return read_json(secrets)

    message = 'Client secrets file not found at %s or $SREGISTRY_CLIENT_SECRETS.'
    if required:
        bot.error(message)
        sys.exit(1)

    bot.warning(message)
    return None


def refresh_access_token():
    '''refresh access token reads in the client secrets from
    the token file, and update the tokens, and save back to file
    '''
    token_file = os.environ.get("SINGULARITY_CLIENT_SECRETS", None)
    secrets = read_client_secrets()
    token = None

    # Query to update the token
    if secrets is not None:
        response = requests.post(secrets['token_uri'],
                                 data=json.dumps(
                                     {'refreshToken': secrets['refreshToken']}),
                                 headers={'Content-Type': "application/json"})

        if response.status_code == 200:

            response = response.json()
            secrets["accessToken"] = response['accessToken']
            secrets["refreshToken"] = response['refreshToken']
            print("Successfully refreshed access token.")
            token_file = write_json(secrets, token_file)
            token = secrets['accessToken']

    return token
