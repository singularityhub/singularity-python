#!/usr/bin/env python

'''
client.py: simple client for singularity hub api

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

from singularity.hub.auth import (
    get_headers
)

from singularity.logman import bot
from singularity.hub.base import (
    api_base,
    get_template,
    download_image
)

from singularity.hub.utils import paginate_get


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


    def get_collections(self):
        '''get all container collections
        '''
        results = paginate_get(url='%s/collections/?format=json' %(api_base))
        print("Found %s collections." %(len(results)))
        # TODO: The shub API needs to have this endpoint expanded
        return results


    def get_containers(self,latest=True):
        '''get all containers'''
        results = paginate_get(url='%s/containers/?format=json' %(api_base))
        print("Found %s containers." %(len(results)))
        containers = dict()
        if latest == True:
            for container in results:
                if container['name'] in containers:
                    if container['branch'] in containers[container['name']]:
                        if containers[container['name']][container['branch']]['id'] < container['id']:
                            containers[container['name']][container['branch']] = container
                    else:
                        containers[container['name']][container['branch']] = container
                else:
                    containers[container['name']] = {container['branch']: container}
        return containers

