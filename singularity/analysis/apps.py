
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
