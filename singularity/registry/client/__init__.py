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
