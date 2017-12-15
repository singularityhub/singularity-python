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

from singularity.logger import bot
from singularity.utils import clean_up
from singularity.hub import ApiConnection
from singularity.hub.utils import (
    get_image_name,
    prepare_url
)

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
        url = prepare_url(container_name, "container/details")
        return self.get('%s/%s' %(self.base,url))


    def get_container(self,uri,name=None,download_folder=None):
        '''download singularity image from singularity hub to a download_folder, 
        named based on the image version or a custom name
        '''
        manifest = self.get_manifest(uri)

        image_file = get_image_name(manifest)
        if name is not None:
            image_file = name
 
        print("Found image %s:%s" %(manifest['name'],manifest['tag']))
        print("Downloading image... %s" %(image_file))

        if download_folder is not None:
            image_file = "%s/%s" %(download_folder,image_file)
        url = manifest['image']

        image_file = self.download(url,file_name=image_file)
        return image_file


    def get_collection(self, name):
        '''get a container collection or return None.
        '''
        url = prepare_url(name, "collection")
        return self.get("%s/%s" %(self.base, url))


    def get_collections(self):
        '''get all container collections
        '''
        results = self.paginate_get(url='%s/collections/?format=json' %(self.base))
        print("Found %s collections." %(len(results)))
        return results
