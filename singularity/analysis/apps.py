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

from spython.main import Client
from singularity.logger import bot
import sys
import os
import re
import json



def extract_apps(image, app_names):
    ''' extract app will extract metadata for one or more apps
        Parameters
        ==========
        image: the absolute path to the image
        app_name: the name of the app under /scif/apps

    '''
    apps = dict()

    if isinstance(app_names, tuple):
        app_names = list(app_names)
    if not isinstance(app_names, list):
        app_names = [app_names]
    if len(app_names) == 0:
        return apps

    for app_name in app_names:
        metadata = dict()

        # Inspect: labels, env, runscript, tests, help
        try:
            inspection = json.loads(Client.inspect(image, app=app_name))
            del inspection['data']['attributes']['deffile']
            metadata['inspect'] = inspection

        # If illegal characters prevent load, not much we can do
        except:
            pass
        apps[app_name] = metadata
    return apps
