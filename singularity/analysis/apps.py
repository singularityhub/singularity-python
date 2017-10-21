
'''
apps.py: part of singularity package
functions to assess SCI-F apps

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

from singularity.analysis.reproduce import (
    delete_image_tar,
    get_image_tar,
    get_image_file_hash,
    get_image_hashes,
    extract_content
)

from singularity.cli import Singularity
from singularity.package import (
    get_container_contents,
    package as make_package,
    get_package_base
)

import sys
import os
import re
import json



def extract_apps(image_path, app_names, S=None, verbose=True):
    ''' extract app will extract metadata for one or more apps
     
    Parameters
    ==========
    image_path: the absolute path to the image
    app_name: the name of the app under /scif/apps
    '''
    if S is None:
        S = Singularity(debug=verbose,sudo=True)

    if not isinstance(app_names,list):
        app_names = [app_names]

    file_obj, tar = get_image_tar(image_path, S=S)
    members = tar.getmembers()
    apps = dict()

    for app_name in app_names:
        metadata = dict()
        # Inspect: labels, env, runscript, tests, help
        try:
            inspection = json.loads(S.inspect(image_path, app=app_name))
            del inspection['data']['attributes']['deffile']
            metadata['inspect'] = inspection
        # If illegal characters prevent load, not much we can do
        except:
            pass
        base = '/scif/apps/%s' %app_name
        metadata['files'] = [x.path for x in members if base in x.path]
        apps[app_name] = metadata

    return apps
