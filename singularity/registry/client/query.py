'''

ls: search and query functions for client

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
from singularity.registry.utils import parse_image_name
from singularity.hub import ApiConnection

import json
import sys
import os


def ls(self, query=None):
    '''query a Singularity registry for a list of images. 
     If query is None, collections are listed. 

    EXAMPLE QUERIES:

    [empty]             list all collections in registry
    vsoch               do a general search for the expression "vsoch"
    vsoch/              list all containers in collection vsoch
    /dinosaur           list containers across collections called "dinosaur"
    vsoch/dinosaur      list details of container vsoch/dinosaur
                          tag "latest" is used by default, and then the most recent
    vsoch/dinosaur:tag  list details for specific container
    
    '''

    if query is not None:

        # List all containers in collection query/
        if query.endswith('/'):  # collection search
            return self.collection_search(query)

        # List containers across collections called /query
        elif query.startswith('/'):  
            return self.container_search(query, across_collections=True)

        # List details of a specific collection container
        elif "/" in query or ":" in query:  
            return self.container_search(query)

        # Call custom search
        else:
            return self.search(query)

    else:
        # List all collections
        return self.collection_search()


def search(self, query):
    '''find containers based on a query, this will search containers
    across collections, but return collections
    '''
    url = '%s/collection/search/%s' %(self.base,query.lower())
    results = self.get(url)
    #TODO: test and parse result!


##################################################################
# Search Helpers
##################################################################

def collection_search(self, query):
    '''collection search will list all containers for a specific
    collection. We assume query is the name of a collection'''

    query = query.lower().strip('/')
    url = '%s/collections/%s' % (self.base, collection_name)

    result = self.get(url)
    if len(result) == 0:
        bot.info("No collections found.")
        sys.exit(1)

    bot.info("Collection %s" %query)
    if 'containers' not in result:
        bot.info("No containers found.")
        sys.exit(0)

    rows = []
    for container in result['containers']:
        rows.append([ container['uri'],
                      container['detail'] ])

    bot.table(rows)


def label_search(self, key=None, value=None):
    '''search across labels'''

    key = key.lower()
    value = value.lower()

    # If both key and value are None, the user wants all Labels
    if key is None and value is None:
        url = '%s/labels/search' % (self.base)
    elif key is not None and value is not None:
        url = '%s/labels/search/%s/key/%s/value' % (self.base, key, value)
    elif key is None:
        url = '%s/labels/search/%s/value' % (self.base, value)
    else:
        url = '%s/labels/search/%s/key' % (self.base, key)

    result = self.get(url)
    # TODO: test out


def container_search(self, query, across_collections=True):
    '''search for a specific container. If across collections is False,
    the query is parsed as a full container name and a specific container
    is returned. If across_collections is True, the container is searched
    for across collections'''

    query = query.lower().strip('/')
    url = '%s/container/search/%s' % (self.base, query, int(across_collections))

    result = self.get(url)
    if len(result) == 0:
        bot.info("No containers found.")
        sys.exit(1)

    bot.info("Containers %s" %query)
    if "containers" not in result:
        bot.info("No containers found.")
        sys.exit(0)

    rows = []
    for container in result["containers"]:        
        rows.append([ container['uri'],
                      container['detail'] ])

    bot.table(rows)
