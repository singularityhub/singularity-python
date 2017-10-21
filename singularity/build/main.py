'''
build/main.py: main runner for Singularity Hub builds

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

from singularity.version import (
    __version__ as singularity_python_version
)

from singularity.cli import Singularity

from singularity.package import (
    build_from_spec, 
    estimate_image_size,
    package
)

from singularity.analysis.apps import extract_apps
from singularity.build.utils import (
    get_singularity_version,
    stop_if_result_none,
    test_container
)


from singularity.analysis.reproduce import get_image_file_hash
from singularity.utils import download_repo
from singularity.analysis.classify import (
    get_diff,
    estimate_os,
    file_counts,
    extension_counts
)

from datetime import datetime
from glob import glob
import io
import json
import os
import pickle
import re
import requests
from urllib.parse import urlencode

from singularity.registry.auth import generate_header_signature
from retrying import retry
# https://cloud.google.com/storage/docs/exponential-backoff

import shutil
import sys
import tempfile
import time

shub_api = "http://www.singularity-hub.org/api"

from singularity.logger import bot

def run_build(build_dir,params,verbose=True, compress_image=False):
    '''run_build takes a build directory and params dictionary, and does the following:
      - downloads repo to a temporary directory
      - changes branch or commit, if needed
      - creates and bootstraps singularity image from Singularity file
      - returns a dictionary with: 
          image (path), image_package (path), metadata (dict)

    The following must be included in params: 
       spec_file, repo_url, branch, commit

    Optional parameters
       size 
    '''

    # Download the repo and image
    download_repo(repo_url=params['repo_url'],
                  destination=build_dir)

    os.chdir(build_dir)
    if params['branch'] != None:
        bot.info('Checking out branch %s' %params['branch'])
        os.system('git checkout %s' %(params['branch']))
    else:
        params['branch'] = "master"

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
    pickle.dump(params,open(passing_params,'wb'))

    # Now look for spec file
    if os.path.exists(params['spec_file']):
        bot.info("Found spec file %s in repository" %params['spec_file'])

        # START TIMING
        start_time = datetime.now()
        image = build_from_spec(spec_file=params['spec_file'], # default will package the image
                                build_dir=build_dir,
                                isolated=True,
                                sandbox=False,
                                debug=params['debug'])

        # Save has for metadata (also is image name)
        version = get_image_file_hash(image)
        params['version'] = version
        pickle.dump(params,open(passing_params,'wb'))

        final_time = (datetime.now() - start_time).seconds
        bot.info("Final time of build %s seconds." %final_time)  

        # Did the container build successfully?
        test_result = test_container(image)
        if test_result['return_code'] != 0:
            bot.error("Image failed to build, cancelling.")
            sys.exit(1)

        # Get singularity version
        singularity_version = get_singularity_version()
        
        # Package the image metadata (files, folders, etc)
        image_package = package(image_path=image,
                                spec_path=params['spec_file'],
                                output_folder=build_dir,
                                remove_image=True,
                                verbose=True)

        # Derive software tags by subtracting similar OS
        diff = get_diff(image_package=image_package)

        # Inspect to get labels and other metadata
        cli = Singularity(debug=params['debug'])
        inspect = cli.inspect(image_path=image)

        # Get information on apps
        app_names = cli.apps(image_path=image)
        apps = extract_apps(image_path=image, app_names=app_names)

        # Count file types, and extensions
        counts = dict()
        counts['readme'] = file_counts(diff=diff)
        counts['copyright'] = file_counts(diff=diff,patterns=['copyright'])
        counts['authors-thanks-credit'] = file_counts(diff=diff,
                                                      patterns=['authors','thanks','credit','contributors'])
        counts['todo'] = file_counts(diff=diff,patterns=['todo'])
        extensions = extension_counts(diff=diff)

        os_sims = estimate_os(image_package=image_package,return_top=False)
        most_similar = os_sims['SCORE'].idxmax()

        metrics = {'build_time_seconds':final_time,
                   'singularity_version':singularity_version,
                   'singularity_python_version':singularity_python_version, 
                   'estimated_os': most_similar,
                   'os_sims':os_sims['SCORE'].to_dict(),
                   'file_counts':counts,
                   'file_ext':extensions,
                   'inspect':inspect,
                   'version': version,
                   'apps': apps}
  
        # Compress Image
        if compress_image is True:
            compressed_image = "%s.gz" %image
            os.system('gzip -c -9 %s > %s' %(image,compressed_image))
            image = compressed_image

        output = {'image':image,
                  'image_package':image_package,
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

    # Send it back!
    return requests.post(response_url,data=response, headers=headers)
