'''

client: simple client for singularity registry api

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
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL TyHE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from singularity.cli import Singularity
from singularity.logger import bot
from singularity.hub import ApiConnection
import json
import sys
import os

from singularity.registry.auth import read_client_secrets

from .auth import authorize
from .pull import pull
from .push import push
from .delete import remove
from .query import (
    ls, search,
    label_search,
    collection_search, 
    container_search
)

api_base = "http://127.0.0.1"

class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, **kwargs):
 
        self.headers = None
        self.base = base
        self.secrets = read_client_secrets(secrets)
        self.update_headers()
 
        # Credentials base takes 1st preference
        if "base" in self.secrets:
            self.base = self.secrets['base']

        # If not defined, default to localhost
        if self.base is None:
            self.base = api_base
        self.base = self.base.strip('/') 

        # Make sure the api base is specified
        if not self.base.endswith('/api'):
            self.base =  "%s/api" %self.base

        super(ApiConnection, self).__init__(**kwargs)


    def update_secrets(secrets=None):
        '''update secrets will take a secrets credential file
        and update the current client secrets
        '''
        if secrets not in [None,'']:
            self.secrets = read_client_secrets(secrets)

    def __str__(self):
        return "singularity.registry.client.%s" %(self.base)
    

    def read_response(self,response, field="detail"):
        '''attempt to read the detail provided by the response. If none, 
        default to using the reason'''

        try:
            message = json.loads(response._content.decode('utf-8'))[field]
        except:
            message = response.reason
        return message


Client.authorize = authorize
Client.ls = ls
Client.remove = remove
Client.pull = pull
Client.push = push
Client.search = search
Client.collection_search = collection_search
Client.container_search = container_search
Client.label_search = label_search
