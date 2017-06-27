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
    read_file,
    write_file,
    mkdir_p,
    get_installdir,
    write_json
)

import shutil
import sys
import os

here = get_installdir()

def get_template(templates,output_folder):
    '''get_template will copy one or more templates (based on filename off
    of templates) into an output folder.
    '''
    if not os.path.exists(output_folder):
        bot.error("%s does not exist, please create first." %output_folder)
        sys.exit(1)    

    templates_base = "%s/registry/templates" %here
    dirname = os.path.basename(output_folder)

    copied = []
    if not isinstance(templates,list):
        templates = [templates]

    for template in templates:
        path = "%s/%s" %(templates_base,template)
        filename = os.path.basename(template)
        finished = "%s/%s" %(output_folder,filename)
        if os.path.exists(path):
            if os.path.isdir(path):
                bot.debug("Copying folder %s to %s" %(filename,dirname))
                shutil.copytree(path,finished)
            else:
                bot.debug("Copying file %s to %s" %(filename,dirname))
                shutil.copyfile(path,finished)
            copied.append(finished)
        else:
            bot.warning("Could not find %s" %template)

    return copied
