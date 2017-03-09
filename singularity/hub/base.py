#!/usr/bin/env python

'''
base.py: base module for working with singularity hub api. Right
         now serves to hold defaults.

'''

from singularity.hub.utils import (
    parse_container_name,
    is_number,
    api_get,
    api_post
)

api_base = "https://singularity-hub.org/api"

def get_template(container_name,get_type=None):
    '''get a container/collection or return None.
    '''
    if get_type == None:
        get_type = "container"
    get_type = get_type.lower().replace(' ','')

    result = None
    image = parse_container_name(container_name)
    if is_number(image):
        url = "%s/%ss/%s" %(api_base,get_type,image)

    elif image['user'] is not None and image['repo_name'] is not None:        
        url = "%s/%s/%s/%s" %(api_base,
                              get_type,
                              image['user'],
                              image['repo_name'])

        if image['repo_tag'] is not None and get_type is not "collection":
            url = "%s:%s" %(url,image['repo_tag'])
 
        result = api_get(url)

    return result
