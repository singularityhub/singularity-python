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

import os
import sys
from singularity.logman import bot

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


def download_image(manifest,download_folder=None,extract=True,name=None):
    '''download_image will download a singularity image from singularity
    hub to a download_folder, named based on the image version (commit id)
    :param manifest: the manifest obtained with get_manifest
    :param download_folder: the folder to download to, if None, will be pwd
    :param extract: if True, will extract image to .img and return that.
    :param name: if defined, use custom set image name instead of default
    '''    
    if name is not None:
        image_file = name
    else:
        image_file = get_image_name(manifest)

    print("Found image %s:%s" %(manifest['name'],manifest['branch']))
    print("Downloading image... %s" %(image_file))

    if download_folder != None:
        image_file = "%s/%s" %(download_folder,image_file)
    url = manifest['image']
    image_file = api_get(url,stream_to=image_file)
    if extract == True:
        print("Decompressing %s" %image_file)
        os.system('gzip -d -f %s' %(image_file))
        image_file = image_file.replace('.gz','')
    return image_file


# Various Helpers ---------------------------------------------------------------------------------
def get_image_name(manifest,extension='img.gz',use_hash=False):
    '''get_image_name will return the image name for a manifest
    :param manifest: the image manifest with 'image' as key with download link
    :param use_hash: use the image hash instead of name
    '''
    if not use_hash:
        image_name = "%s-%s.%s" %(manifest['name'].replace('/','-'),
                                  manifest['branch'].replace('/','-'),
                                  extension)
    else:
        image_url = os.path.basename(unquote(manifest['image']))
        image_name = re.findall(".+[.]%s" %(extension),image_url)
        if len(image_name) > 0:
            image_name = image_name[0]
        else:
            bot.logger.error("Singularity Hub Image not found with expected extension %s, exiting.",extension)
            sys.exit(1)
            
    bot.logger.info("Singularity Hub Image: %s", image_name)
    return image_name
