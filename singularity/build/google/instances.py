'''

Copyright (C) 2017-2019 Vanessa Sochat.

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

from singularity.build.main import (
    run_build as run_build_main,
    send_build_data,
    send_build_close
)

import json
import uuid
import os
import pickle
import requests
import tempfile

# Log everything to stdout
from singularity.logger import bot

from .utils import get_google_service
from .storage import (
    get_image_path,
    upload_file
)

def run_build(logfile='/tmp/.shub-log'):

    '''run_build will generate the Singularity build from a spec_file from a repo_url.

    If no arguments are required, the metadata api is queried for the values.

    :param build_dir: directory to do the build in. If not specified, will use temporary.   
    :param spec_file: the spec_file name to use, assumed to be in git repo
    :param repo_url: the url to download the repo from
    :param repo_id: the repo_id to uniquely identify the repo (in case name changes)
    :param commit: the commit to checkout. If none provided, will use most recent.
    :param bucket_name: the name of the bucket to send files to
    :param verbose: print out extra details as we go (default True)    
    :param token: a token to send back to the server to authenticate the collection
    :param secret: a secret to match to the correct container
    :param response_url: the build url to send the response back to. Should also come
    from metadata. If not specified, no response is sent
    :param branch: the branch to checkout for the build.

    :: note: this function is currently configured to work with Google Compute
    Engine metadata api, and should (will) be customized if needed to work elsewhere 

    '''

    # If we are building the image, this will not be set
    go = get_build_metadata(key='dobuild')
    if go == None:
        sys.exit(0)

    # If the user wants debug, this will be set
    debug = True
    enable_debug = get_build_metadata(key='debug')
    if enable_debug == None:
        debug = False
    bot.info('DEBUG %s' %debug)

    # Uaw /tmp for build directory
    build_dir = tempfile.mkdtemp()

    # Get variables from the instance metadata API
    metadata = [{'key': 'repo_url', 'value': None },
                {'key': 'repo_id', 'value': None },
                {'key': 'response_url', 'value': None },
                {'key': 'bucket_name', 'value': None },
                {'key': 'tag', 'value': None },
                {'key': 'container_id', 'value': None },
                {'key': 'commit', 'value': None },
                {'key': 'token', 'value': None},
                {'key': 'branch', 'value': None },
                {'key': 'spec_file', 'value': None},
                {'key': 'logging_url', 'value': None },
                {'key': 'logfile', 'value': logfile }]

    # Obtain values from build
    bot.log("BUILD PARAMETERS:")
    params = get_build_params(metadata)
    params['debug'] = debug
    
    # Default spec file is Singularity
    if params['spec_file'] == None:
        params['spec_file'] = "Singularity"
        
    if params['bucket_name'] == None:
        params['bucket_name'] = "singularityhub"

    if params['tag'] == None:
        params['tag'] = "latest"

    output = run_build_main(build_dir=build_dir,
                            params=params)

    # Output includes:
    finished_image = output['image']
    metadata = output['metadata']
    params = output['params']  

    # Upload image package files to Google Storage
    if os.path.exists(finished_image):
        bot.info("%s successfully built" %finished_image)
        dest_dir = tempfile.mkdtemp(prefix='build')

        # The path to the images on google drive will be the github url/commit folder
        trailing_path = "%s/%s" %(params['commit'], params['version'])
        image_path = get_image_path(params['repo_url'], trailing_path) 
                                                         # commits are no longer unique
                                                         # storage is by commit

        build_files = [finished_image]
        bot.info("Sending image to storage:") 
        bot.info('\n'.join(build_files))

        # Start the storage service, retrieve the bucket
        storage_service = get_google_service() # default is "storage" "v1"
        bucket = get_bucket(storage_service,params["bucket_name"])

        # For each file, upload to storage
        files = []
        for build_file in build_files:
            bot.info("Uploading %s to storage..." %build_file)
            storage_file = upload_file(storage_service,
                                       bucket=bucket,
                                       bucket_path=image_path,
                                       file_name=build_file)  
            files.append(storage_file)
                
        # Finally, package everything to send back to shub
        response = {"files": json.dumps(files),
                    "repo_url": params['repo_url'],
                    "commit": params['commit'],
                    "repo_id": params['repo_id'],
                    "branch": params['branch'],
                    "tag": params['tag'],
                    "container_id": params['container_id'],
                    "spec_file":params['spec_file'],
                    "token": params['token'],
                    "metadata": json.dumps(metadata)}

        # Did the user specify a specific log file?
        custom_logfile = get_build_metadata('logfile')
        if custom_logfile is not None:
            logfile = custom_logfile    
        response['logfile'] = logfile

        # Send final build data to instance
        send_build_data(build_dir=build_dir,
                        response_url=params['response_url'],
                        secret=params['token'],
                        data=response)

        # Dump final params, for logger to retrieve
        passing_params = "/tmp/params.pkl"
        pickle.dump(params,open(passing_params,'wb'))


def finish_build(verbose=True):
    '''finish_build will finish the build by way of sending the log to the same bucket.
    the params are loaded from the previous function that built the image, expected in
    $HOME/params.pkl
    :: note: this function is currently configured to work with Google Compute
    Engine metadata api, and should (will) be customized if needed to work elsewhere 
    '''
    # If we are building the image, this will not be set
    go = get_build_metadata(key='dobuild')
    if go == None:
        sys.exit(0)

    # Load metadata
    passing_params = "/tmp/params.pkl"
    params = pickle.load(open(passing_params,'rb'))

    # Start the storage service, retrieve the bucket
    storage_service = get_google_service()
    bucket = get_bucket(storage_service,params['bucket_name'])

    # If version isn't in params, build failed
    version = 'error-%s' % str(uuid.uuid4())
    if 'version' in params:
        version = params['version']
    trailing_path = "%s/%s" %(params['commit'], version)
    image_path = get_image_path(params['repo_url'], trailing_path) 

    # Upload the log file
    params['log_file'] = upload_file(storage_service,
                                     bucket=bucket,
                                     bucket_path=image_path,
                                     file_name=params['logfile'])
                
    # Close up shop
    send_build_close(params=params,
                     response_url=params['logging_url'])


################################################################################
# METADATA
################################################################################


def get_build_metadata(key):
    '''get_build_metadata will return metadata about an instance from within it.
    :param key: the key to look up
    '''
    headers = {"Metadata-Flavor":"Google"}
    url = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/%s" % key  
    response = requests.get(url=url,headers=headers)
    if response.status_code == 200:
        return response.text
    return None


def get_build_params(metadata):
    '''get_build_params uses get_build_metadata to retrieve corresponding meta data values for a build
    :param metadata: a list, each item a dictionary of metadata, in format:
    metadata = [{'key': 'repo_url', 'value': repo_url },
                {'key': 'repo_id', 'value': repo_id },
                {'key': 'credential', 'value': credential },
                {'key': 'response_url', 'value': response_url },
                {'key': 'token', 'value': token},
                {'key': 'commit', 'value': commit }]

    '''
    params = dict()
    for item in metadata:
        if item['value'] == None:
            response = get_build_metadata(key=item['key'])
            item['value'] = response
        params[item['key']] = item['value']
        if item['key'] not in ['token', 'secret', 'credential']:
            bot.info('%s is set to %s' %(item['key'],item['value']))        
    return params
