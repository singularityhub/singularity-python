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
from dateutil import parser

import json
import sys
import os


def ls(self, query=None, args=None):
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
            if args is not None:
                return self.container_search(query, deffile=args.deffile,
                                                    environment=args.environ,
                                                    runscript=args.runscript,
                                                    test=args.test)
            return self.container_search(query)

        # Search collections across all fields
        return self.collection_search(query=query)


    # Search collections across all fields
    return self.search()



##################################################################
# Search Helpers
##################################################################

def search(self):
    '''a "show all" search that doesn't require a query'''

    url = '%s/collections/' %self.base

    results = self.paginate_get(url)
   
    if len(results) == 0:
        bot.info("No container collections found.")
        sys.exit(1)

    bot.info("Collections")

    rows = []
    for result in results:
        if "containers" in result:
            for c in result['containers']:
                rows.append([ c['uri'],
                              c['detail'] ])

    bot.table(rows)


def collection_search(self, query):
    '''collection search will list all containers for a specific
    collection. We assume query is the name of a collection'''

    query = query.lower().strip('/')
    url = '%s/collection/%s' %(self.base, query)

    result = self.get(url)
    if len(result) == 0:
        bot.info("No collections found.")
        sys.exit(1)

    bot.custom(prefix="COLLECTION", message=query)

    rows = []
    for container in result['containers']:
        rows.append([ container['uri'],
                      container['detail'] ])

    bot.table(rows)


def label_search(self, key=None, value=None):
    '''search across labels'''

    if key is not None:
        key = key.lower()

    if value is not None:
        value = value.lower()

    show_details = True
    if key is None and value is None:
        url = '%s/labels/search' % (self.base)
        show_details = False

    elif key is not None and value is not None:
        url = '%s/labels/search/%s/key/%s/value' % (self.base, key, value)

    elif key is None:
        url = '%s/labels/search/%s/value' % (self.base, value)

    else:
        url = '%s/labels/search/%s/key' % (self.base, key)

    result = self.get(url)
    if len(result) == 0:
        bot.info("No labels found.")
        sys.exit(0)

    bot.info("Labels\n")

    rows = []
    for l in result:        
        if show_details is True:
            entry = ["%s:%s" %(l['key'],l['value']),
                     "\n%s\n\n" %"\n".join(l['containers'])]
        else:
            entry = ["N=%s" %len(l['containers']),
                    "%s:%s" %(l['key'],l['value']) ]
        rows.append(entry)
    bot.table(rows)



def container_search(self, query, across_collections=False, environment=False,
                     deffile=False, runscript=False, test=False):
    '''search for a specific container. If across collections is False,
    the query is parsed as a full container name and a specific container
    is returned. If across_collections is True, the container is searched
    for across collections. If across collections is True, details are
    not shown'''

    query = query.lower().strip('/')

    q = parse_image_name(query, defaults=False)

    if q['tag'] is not None:
        if across_collections is True:
            url = '%s/container/search/name/%s/tag/%s' % (self.base, q['image'], q['tag'])
        else:
            url = '%s/container/search/collection/%s/name/%s/tag/%s' % (self.base, q['collection'], q['image'], q['tag'])

    elif q['tag'] is None: 
        if across_collections is True:
            url = '%s/container/search/name/%s' % (self.base, q['image'])
        else:
            url = '%s/container/search/collection/%s/name/%s' % (self.base, q['collection'], q['image'])

    result = self.get(url)
    if "containers" in result:
        result = result['containers']

    if len(result) == 0:
        bot.info("No containers found.")
        sys.exit(1)

    bot.info("Containers %s" %query)

    rows = []
    for c in result:        

        # Convert date to readable thing
        datetime_object = parser.parse(c['add_date'])
        print_date = datetime_object.strftime('%b %d, %Y %I:%M%p')
        rows.append([ '%s/%s' %(c['collection'], c['name']),
                      c['tag'],
                      print_date ])

    bot.table(rows)

    # Finally, show metadata and other values
    if test is True or deffile is True or environment is True or runscript is True:
        bot.newline() 
        for c in result:
            metadata = c['metadata']

            if test is True:
                bot.custom(prefix='%test', message=metadata['test'], color="CYAN")
                bot.newline()
            if deffile is True:
                bot.custom(prefix='Singularity', message=metadata['deffile'], color="CYAN")
                bot.newline()
            if environment is True:
                bot.custom(prefix='%environment', message=metadata['environment'], color="CYAN")
                bot.newline()
            if runscript is True:
                bot.custom(prefix='%runscript', message=metadata['runscript'], color="CYAN")
                bot.newline()
