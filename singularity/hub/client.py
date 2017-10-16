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

from singularity.logger import bot
from singularity.utils import clean_up
from singularity.hub import ApiConnection
from singularity.hub.utils import prepare_url

import demjson
import json
import sys


api_base = "https://singularity-hub.org/api"

class Client(ApiConnection):

    def __init__(self, **kwargs):
        super(ApiConnection, self).__init__(**kwargs)

        self.base = api_base
        if "registry" in kwargs:
            self.base = kwargs['registry']
            if not self.base.endswith('/api'):
                self.base = "%s/api" %self.base

        self.headers = None
        if "token" in kwargs:
            self.token = authenticate()
        self.update_headers()
        
    def __str__(self):
        return "<singularity-hub-client>"        

    def __repr__(self):
        return "<singularity-hub-client>"        


    def get_manifest(self,container_name):
        '''get manifest
        '''
        url = prepare_url(container_name, "container")
        manifest = self.get(url)
        if manifest is not None:      
            manifest['metrics'] = demjson.decode(manifest['metrics'])
        return manifest


    def get_container(self,container_id,download_folder=None,extract=True,name=None):
        '''download singularity image from singularity hub to a download_folder, 
        named based on the image version (commit id)
        '''
        manifest = self.get_manifest(container_id)

        image_file = get_image_name(manifest)
        if name is not None:
            image_file = name
 
        print("Found image %s:%s" %(manifest['name'],manifest['branch']))
        print("Downloading image... %s" %(image_file))

        if download_folder is not None:
            image_file = "%s/%s" %(download_folder,image_file)
        url = manifest['image']

        image_file = self.download(url,file_name=image_file)
    
        if extract == True:
            if not bot.is_quiet():
                print("Decompressing %s" %image_file)
            output = run_command(['gzip','-d','-f',image_file])
            image_file = image_file.replace('.gz','')

            # Any error in extraction (return code not 0) will return None
            if output is None:
                bot.error('Error extracting image, cleaning up.')
                clean_up([image_file,"%s.gz" %image_file])

        return image_file


    def get_collection(self,container_name):
        '''get a container collection or return None.
        '''
        url = prepare_url(container_name,"collection")
        return self.get(url)


    def get_collections(self):
        '''get all container collections
        '''
        results = paginate_get(url='%s/collections/?format=json' %(self.base))
        print("Found %s collections." %(len(results)))
        # TODO: The shub API needs to have this endpoint expanded
        return results


    def get_containers(self,latest=True):
        '''get all containers'''
        results = paginate_get(url='%s/containers/?format=json' %(self.base))
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

