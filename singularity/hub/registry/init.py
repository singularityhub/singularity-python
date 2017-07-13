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

from glob import glob
import sys
import os


def generate_registry(base,storage=None):

    '''initalize a registry, meaning generating the root folder with
    subfolders for containers and recipes.
    '''

    if storage is None:
        storage = "%s/storage" %(base) 

    container_base = "%s/containers" %storage

    if os.path.exists(base) or os.path.exists(container_base):
        bot.error("%s or %s already exists, will not overwrite." %(base,container_base))
        sys.exit(1)

    # Make directories for containers, builder, recipes
    mkdir_p(container_base)
    mkdir_p('%s/builder/recipes' %base)
    os.mkdir("%s/builder/templates" %base)

    bot.newline()
    bot.info("BASE: %s" %base)
    bot.info(" --> BUILDER: %s/builder\n" %base)
    bot.info(" --> RECIPES: %s/builder/recipes" %base)
    bot.info("STORAGE: %s" %storage)
    bot.info(" --> CONTAINERS: %s/containers" %storage)
    bot.newline()

    return container_base
