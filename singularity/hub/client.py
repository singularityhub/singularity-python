#!/usr/bin/env python

'''
client.py: simple client for singularity hub api

'''

from singularity.hub.auth import (
    get_headers
)

from singularity.logman import bot
from singularity.hub.base import (
    get_template,
    download_image
)

import demjson

class Client(object):


    def __init__(self, token=None):
 
        if token is not None:
            self.token = token
        # currently not used
        self.headers = get_headers(token=token)


    def update_headers(self, headers):
        '''update_headers will add headers to the client
        :param headers: should be a dictionary of key,value to update/add to header
        '''
        for key,value in headers.items():
            self.client.headers[key] = item

    def load_metrics(self,manifest):
        '''load metrics about a container build from the manifest
        '''
        return demjson.decode(manifest['metrics'])


    def get_container(self,container_name):
        '''get a container or return None.
        '''
        return get_template(container_name,"container")


    def pull_container(self,manifest,download_folder=None,extract=True,name=None):
        '''pull a container to the local machine'''
        return download_image(manifest=manifest,
                              download_folder=download_folder,
                              extract=extract,
                              name=name)



    def get_collection(self,container_name):
        '''get a container collection or return None.
        '''
        return get_template(container_name,"collection")
