'''
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

from singularity.utils import (
    mkdir_p,
    write_json
)
from glob import glob
import sys
import os


def generate_registry(base,
                      uri,
                      name,
                      container_base=None,
                      recipe_base=None):
    '''initalize a registry, meaning generating the root folder with
    subfolders for containers and recipes, along with the config file
    at the root
    '''

    if container_base is None:
        container_base = "containers"
    if recipe_base is None:
        recipe_base = "recipes"

    if os.path.exists(base):
        bot.error("%s already exists, will not overwrite." %base)
        sys.exit(1)

    mkdir_p(container_base)
    mkdir_p(recipe_base)
    bot.info("Created container and recipe home at %s" %base)

    config_file = generate_config(base=base,
                                  uri=uri,
                                  name=name,
                                  container_base=container_base,
                                  recipe_base=recipe_base)
    return config_file


def generate_config(base,
                    uri,
                    name,
                    container_base,
                    recipe_base,
                    filename=None):

    '''generate config will write a config file at the registry
    base. The default filename is .shub
    '''

    if filename is None:
        filename = '.shub'

    config = { 
                "STORAGE_BASE": container_base,
                "RECIPE_BASE":  recipe_base,
                "REGISTRY_URI": uri,
                "REGISTRY_NAME": name 
             }

    config_file = "%s/%s" %(base,filename)
    write_json(config,config_file)
    return config_file
