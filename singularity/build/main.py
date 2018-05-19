'''

Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from singularity.version import (
    __version__ as singularity_python_version
)

from spython.main import Client

from singularity.analysis.apps import extract_apps
from singularity.build.utils import (
    stop_if_result_none,
    get_singularity_version,
    test_container
)

from singularity.analysis.reproduce import get_image_file_hash
from singularity.utils import download_repo

from datetime import datetime
from glob import glob
import io
import json
import os
import pickle
import re
import requests

from singularity.build.auth import generate_header_signature
from retrying import retry
# https://cloud.google.com/storage/docs/exponential-backoff

import shutil
import sys
import tempfile
import time

from singularity.logger import bot

def run_build(build_dir, params, verbose=True):
    '''run_build takes a build directory and params dictionary, and does the following:
      - downloads repo to a temporary directory
      - changes branch or commit, if needed
      - creates and bootstraps singularity image from Singularity file
      - returns a dictionary with: 
          image (path), metadata (dict)

    The following must be included in params: 
       spec_file, repo_url, branch, commit

    '''

    # Download the repository

    download_repo(repo_url=params['repo_url'],
                  destination=build_dir)

    os.chdir(build_dir)

    if params['branch'] != None:
        bot.info('Checking out branch %s' %params['branch'])
        os.system('git checkout %s' %(params['branch']))
    else:
        params['branch'] = "master"


    # Set the debug level

    Client.debug = params['debug']

    # Commit

    if params['commit'] not in [None,'']:
        bot.info('Checking out commit %s' %params['commit'])
        os.system('git checkout %s .' %(params['commit']))

    # From here on out commit is used as a unique id, if we don't have one, we use current
    else:
        params['commit'] = os.popen('git log -n 1 --pretty=format:"%H"').read()
        bot.warning("commit not specified, setting to current %s" %params['commit'])

    # Dump some params for the builder, in case it fails after this
    passing_params = "/tmp/params.pkl"
    pickle.dump(params, open(passing_params,'wb'))

    # Now look for spec file
    if os.path.exists(params['spec_file']):
        bot.info("Found spec file %s in repository" %params['spec_file'])

        # If the user has a symbolic link
        if os.path.islink(params['spec_file']):
            bot.info("%s is a symbolic link." %params['spec_file'])
            params['spec_file'] = os.path.realpath(params['spec_file'])

        # START TIMING
        start_time = datetime.now()

        # Secure Build
        image = Client.build(recipe=params['spec_file'],
                             build_folder=build_dir,
                             isolated=True)

        # Save has for metadata (also is image name)
        version = get_image_file_hash(image)
        params['version'] = version
        pickle.dump(params, open(passing_params,'wb'))

        # Rename image to be hash
        finished_image = "%s/%s.simg" %(os.path.dirname(image), version)
        image = shutil.move(image, finished_image)

        final_time = (datetime.now() - start_time).seconds
        bot.info("Final time of build %s seconds." %final_time)  

        # Did the container build successfully?
        test_result = test_container(image)
        if test_result['return_code'] != 0:
            bot.error("Image failed to build, cancelling.")
            sys.exit(1)

        # Get singularity version
        singularity_version = Client.version()
        Client.debug = False
        inspect = Client.inspect(image) # this is a string
        Client.debug = params['debug']

        # Get information on apps
        Client.debug = False
        app_names = Client.apps(image)
        Client.debug = params['debug']
        apps = extract_apps(image, app_names)
        
        metrics = {'build_time_seconds': final_time,
                   'singularity_version': singularity_version,
                   'singularity_python_version': singularity_python_version, 
                   'inspect': inspect,
                   'version': version,
                   'apps': apps}
  
        output = {'image':image,
                  'metadata':metrics,
                  'params':params }

        return output

    else:

        # Tell the user what is actually there
        present_files = glob("*")
        bot.error("Build file %s not found in repository" %params['spec_file'])
        bot.info("Found files are %s" %"\n".join(present_files))
        # Params have been exported, will be found by log
        sys.exit(1)


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def send_build_data(build_dir, data, secret, 
                    response_url=None,clean_up=True):
    '''finish build sends the build and data (response) to a response url
    :param build_dir: the directory of the build
    :response_url: where to send the response. If None, won't send
    :param data: the data object to send as a post
    :param clean_up: If true (default) removes build directory
    '''
    # Send with Authentication header
    body = '%s|%s|%s|%s|%s' %(data['container_id'],
                              data['commit'],
                              data['branch'],
                              data['token'],
                              data['tag']) 

    signature = generate_header_signature(secret=secret,
                                          payload=body,
                                          request_type="push")

    headers = {'Authorization': signature }

    if response_url is not None:
        finish = requests.post(response_url,data=data, headers=headers)
        bot.debug("RECEIVE POST TO SINGULARITY HUB ---------------------")
        bot.debug(finish.status_code)
        bot.debug(finish.reason)
    else:
        bot.warning("response_url set to None, skipping sending of build.")

    if clean_up == True:
        shutil.rmtree(build_dir)

    # Delay a bit, to give buffer between bringing instance down
    time.sleep(20)



@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,retry_on_result=stop_if_result_none)
def send_build_close(params,response_url):
    '''send build close sends a final response (post) to the server to bring down
    the instance. The following must be included in params:

    repo_url, logfile, repo_id, secret, log_file, token
    '''
    # Finally, package everything to send back to shub
    response = {"log": json.dumps(params['log_file']),
                "repo_url": params['repo_url'],
                "logfile": params['logfile'],
                "repo_id": params['repo_id'],
                "container_id": params['container_id']}

    body = '%s|%s|%s|%s|%s' %(params['container_id'],
                              params['commit'],
                              params['branch'],
                              params['token'],
                              params['tag']) 

    signature = generate_header_signature(secret=params['token'],
                                          payload=body,
                                          request_type="finish")

    headers = {'Authorization': signature }

    finish = requests.post(response_url,data=response, headers=headers)
    bot.debug("FINISH POST TO SINGULARITY HUB ---------------------")
    bot.debug(finish.status_code)
    bot.debug(finish.reason)
    return finish
