#!/usr/bin/env python

'''
build/main.py: main runner for Singularity Hub builds

'''

from singularity.version import (
    __version__ as singularity_python_version
)

from singularity.package import (
    build_from_spec, 
    estimate_image_size,
    package
)

from singularity.build.utils import (
    get_singularity_version,
    stop_if_result_none,
    test_container
)

from singularity.utils import download_repo
from singularity.analysis.classify import (
    get_tags,
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

from retrying import retry
# https://cloud.google.com/storage/docs/exponential-backoff

import shutil
import sys
import tempfile
import time

shub_api = "http://www.singularity-hub.org/api"

from singularity.logman import bot

def run_build(build_dir,params,verbose=True):
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
        bot.logger.info('Checking out branch %s',params['branch'])
        os.system('git checkout %s' %(params['branch']))

    # Commit
    if params['commit'] not in [None,'']:
        bot.logger.info('Checking out commit %s',params['commit'])
        os.system('git checkout %s .' %(params['commit']))

    # From here on out commit is used as a unique id, if we don't have one, we use current
    else:
        params['commit'] = os.popen('git log -n 1 --pretty=format:"%H"').read()
        bot.logger.warning("commit not specified, setting to current %s", params['commit'])

    # Dump some params for the builder, in case it fails after this
    passing_params = "/tmp/params.pkl"
    pickle.dump(params,open(passing_params,'wb'))

    if os.path.exists(params['spec_file']):
        bot.logger.info("Found spec file %s in repository",params['spec_file'])

        # If size is None, set default of 800
        if params['size'] in [None,'']:
            bot.logger.info("""\n
                            --------------------------------------------------------------
                            Size not detected for build. Will use default of 800MB padding. If 
                            your build fails due to running out of disk space, you can adjust the
                            size under collection --> edit builder
                            ---------------------------------------------------------------------
                            \n""")

            # Testing estimation of size
            try:
                params['size'] = estimate_image_size(spec_file=os.path.abspath(params['spec_file']),
                                                     sudopw='',
                                                     padding=params['padding'])
                bot.logger.info("Size estimated as %s",params['size'])  
            except:
                params['size'] = 800
                bot.logger.info("Size estimation didn't work, using default %s",params['size'])  

        # START TIMING
        start_time = datetime.now()
        image = build_from_spec(spec_file=params['spec_file'], # default will package the image
                                size=params['size'],
                                sudopw='', # with root should not need sudo
                                build_dir=build_dir,
                                debug=params['debug'])

        final_time = (datetime.now() - start_time).seconds
        bot.logger.info("Final time of build %s seconds.",final_time)  

        # Did the container build successfully?
        test_result = test_container(image)
        if test_result['return_code'] == 255:
            bot.logger.error("Image failed to bootstrap, cancelling build.")
            sys.exit(1)

        # Compress image
        compressed_image = "%s.img.gz" %image
        os.system('gzip -c -9 %s > %s' %(image,compressed_image))
        
        # Package the image metadata (files, folders, etc)
        image_package = package(image_path=image,
                                spec_path=params['spec_file'],
                                output_folder=build_dir,
                                sudopw='',
                                remove_image=True,
                                verbose=True)

        # Derive software tags by subtracting similar OS
        diff = get_diff(image_package=image_package)

        # Get singularity version
        singularity_version = get_singularity_version()

        # Get tags for services, executables
        interesting_folders = ['init','init.d','bin','systemd']
        tags = get_tags(search_folders=interesting_folders,
                        diff=diff)

        # Count file types, and extensions
        counts = dict()
        counts['readme'] = file_counts(diff=diff)
        counts['copyright'] = file_counts(diff=diff,patterns=['copyright'])
        counts['authors-thanks-credit'] = file_counts(diff=diff,
                                                      patterns=['authors','thanks','credit'])
        counts['todo'] = file_counts(diff=diff,patterns=['todo'])
        extensions = extension_counts(diff=diff)

        os_sims = estimate_os(image_package=image_package,return_top=False)
        most_similar = os_sims['SCORE'].idxmax()

        metrics = {'size': params['size'],
                   'build_time_seconds':final_time,
                   'singularity_version':singularity_version,
                   'singularity_python_version':singularity_python_version, 
                   'estimated_os': most_similar,
                   'os_sims':os_sims['SCORE'].to_dict(),
                   'tags':tags,
                   'file_counts':counts,
                   'file_ext':extensions }
      
        output = {'image':compressed_image,
                  'image_package':image_package,
                  'metadata':metrics,
                  'params':params }

        return output

    else:
        # Tell the user what is actually there
        present_files = glob("*")
        bot.logger.error("Build file %s not found in repository",params['spec_file'])
        bot.logger.info("Found files are %s","\n".join(present_files))
        # Params have been exported, will be found by log
        sys.exit(1)


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def send_build_data(build_dir,data,response_url=None,clean_up=True):
    '''finish build sends the build and data (response) to a response url
    :param build_dir: the directory of the build
    :response_url: where to send the response. If None, won't send
    :param data: the data object to send as a post
    :param clean_up: If true (default) removes build directory
    '''
    if response_url != None:
        finish = requests.post(response_url,data=data)    
    else:
        bot.logger.warning("response_url set to None, skipping sending of build.")

    if clean_up == True:
        shutil.rmtree(build_dir)

    # Delay a bit, to give buffer between bringing instance down
    time.sleep(20)



@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,retry_on_result=stop_if_result_none)
def send_build_close(params,response_url=None):
    '''send build close sends a final response (post) to the server to bring down
    the instance. The following must be included in params:

    repo_url, logfile, repo_id, secret, log_file, token

    if response_url is None, this is skipped entirely.
    '''

    if response_url != None:

        # Finally, package everything to send back to shub
        response = {"log": json.dumps(params['log_file']),
                    "repo_url": params['repo_url'],
                    "logfile": params['logfile'],
                    "repo_id": params['repo_id'],
                    "secret": params['secret']}

        if params['token'] != None:
            response['token'] = params['token']

        # Send it back!
        return requests.post(response_url,data=response)
    
    bot.logger.warning("Response url set to none, cannot send build close.")
    return None
