'''

Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2018 Vanessa Sochat.

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

from singularity.build.utils import sniff_extension

from singularity.build.main import (
    run_build as run_build_main,
    send_build_data,
    send_build_close
)

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from googleapiclient.errors import HttpError
from googleapiclient import http

from glob import glob
import httplib2
import inspect
import imp
import json
import uuid

from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

import io
import os
import pickle
import re
import requests
from retrying import retry
import sys
import tempfile
import time
import zipfile

# Log everything to stdout
from singularity.logger import bot

##########################################################################################
# GOOGLE GENERAL API #####################################################################
##########################################################################################

def get_google_service(service_type=None,version=None):
    '''
    get_url will use the requests library to get a url
    :param service_type: the service to get (default is storage)
    :param version: version to use (default is v1)
    '''
    if service_type == None:
        service_type = "storage"
    if version == None:
        version = "v1"

    credentials = GoogleCredentials.get_application_default()
    return build(service_type, version, credentials=credentials) 


##########################################################################################
# GOOGLE STORAGE API #####################################################################
##########################################################################################
    
@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def get_bucket(storage_service,bucket_name):
    req = storage_service.buckets().get(bucket=bucket_name)
    return req.execute()


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,stop_max_attempt_number=10)
def delete_object(storage_service,bucket_name,object_name):
    '''delete_file will delete a file from a bucket
    :param storage_service: the service obtained with get_storage_service
    :param bucket_name: the name of the bucket (eg singularity-hub)
    :param object_name: the "name" parameter of the object.
    '''
    try:
        operation = storage_service.objects().delete(bucket=bucket_name,
                                                     object=object_name).execute()
    except HttpError as e:
        pass
        operation = e
    return operation


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def upload_file(storage_service,bucket,bucket_path,file_name,verbose=True):
    '''get_folder will return the folder with folder_name, and if create=True,
    will create it if not found. If folder is found or created, the metadata is
    returned, otherwise None is returned
    :param storage_service: the drive_service created from get_storage_service
    :param bucket: the bucket object from get_bucket
    :param file_name: the name of the file to upload
    :param bucket_path: the path to upload to
    '''
    # Set up path on bucket
    upload_path = "%s/%s" %(bucket['id'],bucket_path)
    if upload_path[-1] != '/':
        upload_path = "%s/" %(upload_path)
    upload_path = "%s%s" %(upload_path,os.path.basename(file_name))
    body = {'name': upload_path }
    # Create media object with correct mimetype
    if os.path.exists(file_name):
        mimetype = sniff_extension(file_name,verbose=verbose)
        media = http.MediaFileUpload(file_name,
                                     mimetype=mimetype,
                                     resumable=True)
        request = storage_service.objects().insert(bucket=bucket['id'], 
                                                   body=body,
                                                   predefinedAcl="publicRead",
                                                   media_body=media)
        result = request.execute()
        return result
    bot.warning('%s requested for upload does not exist, skipping' %file_name)

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def list_bucket(bucket,storage_service):
    # Create a request to objects.list to retrieve a list of objects.        
    request = storage_service.objects().list(bucket=bucket['id'], 
                                             fields='nextPageToken,items(name,size,contentType)')
    # Go through the request and look for the folder
    objects = []
    while request:
        response = request.execute()
        objects = objects + response['items']
    return objects


def get_image_path(repo_url, trailing_path):
    '''get_image_path will determine an image path based on a repo url, removing
    any token, and taking into account urls that end with .git.
    :param repo_url: the repo url to parse:
    :param trailing_path: the trailing path (commit then hash is common)
    '''
    repo_url = repo_url.split('@')[-1].strip()
    if repo_url.endswith('.git'):
        repo_url =  repo_url[:-4]
    return "%s/%s" %(re.sub('^http.+//www[.]','',repo_url), trailing_path)



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


#####################################################################################
# METADATA
#####################################################################################


def get_build_metadata(key):
    '''get_build_metadata will return metadata about an instance from within it.
    :param key: the key to look up
    '''
    headers = {"Metadata-Flavor":"Google"}
    url = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/%s" %(key)        
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
