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
        libs = [x.path for x in members if "%s/lib" %base in x.path]
        bins = [x.path for x in members if "%s/bin" %base in x.path]
        metadata['files'] = libs + bins
        apps[app_name] = metadata

    return apps
