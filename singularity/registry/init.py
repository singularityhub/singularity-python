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

from singularity.logger import bot
from singularity.utils import (
    mkdir_p,
    write_json
)
from .template import get_template
from glob import glob
import sys
import os


def generate_registry(base,
                      uri,
                      name,
                      storage=None):

    '''initalize a registry, meaning generating the root folder with
    subfolders for containers and recipes, along with the config file
    at the root
    '''
    if storage is None:
        storage = "%s/storage" %(base) 

    container_base = "%s/containers" %storage

    if os.path.exists(base) or os.path.exists(storage):
        bot.error("%s or %s already exists, will not overwrite." %(base,storage))
        sys.exit(1)

    # Make directories for containers, builder, recipes
    mkdir_p(container_base)
    os.mkdir("%s/bin" %base)
    mkdir_p('%s/builder/recipes' %base)
    os.mkdir("%s/builder/templates" %base)

    bot.newline()
    bot.info("BASE: %s" %base)
    bot.info(" --> MANAGER: %s/bin\n" %base)
    bot.info(" --> BUILDER: %s/builder\n" %base)
    bot.info(" --> RECIPES: %s/builder/recipes" %base)
    bot.info("STORAGE: %s" %storage)
    bot.info(" --> CONTAINERS: %s/containers" %storage)
    bot.newline()

    config_file = generate_config(base=base,
                                  uri=uri,
                                  name=name,
                                  storage=storage)

    # Recipe templates
    templates=['ci/.travis.yml','vc/README.md']
    bot.debug("Adding templates and helpers...")
    copied = get_template(templates=templates,
                          output_folder="%s/builder/recipes" %base)

    # Executable helpers
    copied = get_template(templates=['bin'],
                          output_folder="%s/bin" %base)

    return config_file


def generate_config(base,
                    uri,
                    name,
                    storage,
                    filename=None):

    '''generate config will write a config file at the registry
    base. The default filename is .shub
    '''

    if filename is None:
        filename = 'config.json'
    filename = os.path.basename(filename)

    config = { 
                "REGISTRY_BASE":  base,
                "STORAGE_BASE": storage,
                "REGISTRY_URI": uri,
                "REGISTRY_NAME": name 
             }

    config_file = "%s/%s" %(base,filename)
    bot.debug("Generating config file %s" %config_file)
    write_json(config,config_file)
    return config_file
