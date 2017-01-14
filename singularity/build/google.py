#!/usr/bin/env python

'''
build/google.py: build functions for singularity hub google compute engine

'''

from singularity.api import (
    api_get, 
    api_put
)

from singularity.build.utils import sniff_extension

from singularity.build.main import (
    run_build as run_build_main,
    send_build_data,
    send_build_close
)

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from googleapiclient import http

from glob import glob
import httplib2
import inspect
import imp
import json

from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

import io
import os
import pickle
import re
import requests
import sys
import tempfile
import time
import zipfile

shub_api = "http://www.singularity-hub.org/api"

# Log everything to stdout
from singularity.logman import bot

##########################################################################################
# GOOGLE STORAGE API #####################################################################
##########################################################################################

def get_storage_service():
    credentials = GoogleCredentials.get_application_default()
    return build('storage', 'v1', credentials=credentials)


def get_compute_service():
    credentials = GoogleCredentials.get_application_default()
    return build('compute', 'v1', credentials=credentials)
    

def get_bucket(storage_service,bucket_name):
    req = storage_service.buckets().get(bucket=bucket_name)
    return req.execute()


def delete_object(storage_service,bucket_name,object_name):
    '''delete_file will delete a file from a bucket
    :param storage_service: the service obtained with get_storage_service
    :param bucket_name: the name of the bucket (eg singularity-hub)
    :param object_name: the "name" parameter of the object.
    '''
    return storage_service.objects().delete(bucket=bucket_name,
                                            object=object_name).execute()


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
    mimetype = sniff_extension(file_name,verbose=verbose)
    media = http.MediaFileUpload(file_name,
                                 mimetype=mimetype,
                                 resumable=True)
    request = storage_service.objects().insert(bucket=bucket['id'], 
                                               body=body,
                                               predefinedAcl="publicRead",
                                               media_body=media)
    return request.execute()


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



def run_build(build_dir=None,spec_file=None,repo_url=None,token=None,size=None,bucket_name=None,
              repo_id=None,commit=None,verbose=True,response_url=None,secret=None,branch=None,
              padding=None,logfile=None,logging_url=None):

    '''run_build will generate the Singularity build from a spec_file from a repo_url.

    If no arguments are required, the metadata api is queried for the values.

    :param build_dir: directory to do the build in. If not specified, will use temporary.   
    :param spec_file: the spec_file name to use, assumed to be in git repo
    :param repo_url: the url to download the repo from
    :param repo_id: the repo_id to uniquely identify the repo (in case name changes)
    :param commit: the commit to checkout. If none provided, will use most recent.
    :param size: the size of the image to build. If none set, builds folder size + 200MB padding
    :param bucket_name: the name of the bucket to send files to
    :param verbose: print out extra details as we go (default True)    
    :param token: a token to send back to the server to authenticate the collection
    :param secret: a secret to match to the correct container
    :param response_url: the build url to send the response back to. Should also come
    from metadata. If not specified, no response is sent
    :param branch: the branch to checkout for the build.
    :param padding: size (in MB) to add to image for padding. If not defined, 200

    :: note: this function is currently configured to work with Google Compute
    Engine metadata api, and should (will) be customized if needed to work elsewhere 

    '''

    # If we are building the image, this will not be set
    go = get_build_metadata(key='dobuild')
    if go == None:
        sys.exit(0)

    # If no build directory is specified, make a temporary one
    if build_dir == None:
        build_dir = tempfile.mkdtemp()
        bot.logger.warning('Build directory not set, using %s',build_dir)
    else:
        bot.logger.info('Build directory set to %s', build_dir)

    # Get variables from the instance metadata API
    metadata = [{'key': 'repo_url', 'value': repo_url, 'return_text': False },
                {'key': 'repo_id', 'value': repo_id, 'return_text': True },
                {'key': 'response_url', 'value': response_url, 'return_text': True },
                {'key': 'bucket_name', 'value': bucket_name, 'return_text': True },
                {'key': 'token', 'value': token, 'return_text': False },
                {'key': 'commit', 'value': commit, 'return_text': True },
                {'key': 'secret', 'value': secret, 'return_text': True },
                {'key': 'size', 'value': size, 'return_text': True },
                {'key': 'branch', 'value': branch, 'return_text': True },
                {'key': 'spec_file', 'value': spec_file, 'return_text': True },
                {'key': 'padding', 'value': padding, 'return_text': True },
                {'key': 'logging_url', 'value': logging_url, 'return_text': True },
                {'key': 'logfile', 'value': logfile, 'return_text': True }]


    # Obtain values from build
    params = get_build_params(metadata)
    
    # Default spec file is Singularity
    if params['spec_file'] == None:
        params['spec_file'] = "Singularity"
        
    if params['bucket_name'] == None:
        params['bucket_name'] = "singularity-hub"

    if params['padding'] == None:
        params['padding'] = 200

    output = run_build_main(build_dir=build_dir,
                            params=params)

    # Output includes:
    image_package = output['image_package']
    compressed_image = output['image']
    metadata = output['metadata']  
    params = output['params']  

    # Upload image package files to Google Storage
    if os.path.exists(image_package):
        bot.logger.info("Package %s successfully built",image_package)
        dest_dir = "%s/build" %(build_dir)
        os.mkdir(dest_dir)
        with zipfile.ZipFile(image_package) as zf:
            zf.extractall(dest_dir)

        # The path to the images on google drive will be the github url/commit folder
        image_path = "%s/%s" %(re.sub('^http.+//www[.]','',params['repo_url']),params['commit'])
        build_files = glob("%s/*" %(dest_dir))
        build_files.append(compressed_image)
        bot.logger.info("Sending build files %s to storage",'\n'.join(build_files))

        # Start the storage service, retrieve the bucket
        storage_service = get_storage_service()
        bucket = get_bucket(storage_service,params["bucket_name"])

        # For each file, upload to storage
        files = []
        for build_file in build_files:
            storage_file = upload_file(storage_service,
                                       bucket=bucket,
                                       bucket_path=image_path,
                                       file_name=build_file)  
            files.append(storage_file)

        # Upload the package as well
        package_file = upload_file(storage_service,
                                   bucket=bucket,
                                   bucket_path=image_path,
                                   file_name=image_package)
        files.append(package_file)
                
        # Finally, package everything to send back to shub
        response = {"files": json.dumps(files),
                    "repo_url": params['repo_url'],
                    "commit": params['commit'],
                    "repo_id": params['repo_id'],
                    "secret": params['secret'],
                    "metadata": json.dumps(metadata)}

        # Did the user specify a specific log file?
        logfile = get_build_metadata(key='logfile')
        if logfile != None:
            response['logfile'] = logfile

        if params['branch'] != None:
            response['branch'] = params['branch']

        if params['token'] != None:
            response['token'] = params['token']

        # Send final build data to instance
        send_build_data(build_dir=build_dir,
                        response_url=params['response_url'],
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
    storage_service = get_storage_service()
    bucket = get_bucket(storage_service,params['bucket_name'])
    image_path = "%s/%s" %(re.sub('^http.+//www[.]','',params['repo_url']),params['commit'])

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
    :param key: the key to look upu
    :param return_text: return text (appropriate for one value, or if needs custom parsing. Otherwise, will return json
    '''
    headers = {"Metadata-Flavor":"Google"}
    url = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/%s" %(key)        
    response = api_get(url=url,headers=headers)

    # Successful query returns the result
    if response.status_code == 200:
        if key != "credential":
            bot.logger.info('Metadata response is %s',response.text)
        return response.text
    else:
        bot.logger.error("Error retrieving metadata %s, returned response %s", key,
                                                                            response.status_code)
    return None


def get_build_params(metadata):
    '''get_build_params uses get_build_metadata to retrieve corresponding meta data values for a build
    :param metadata: a list, each item a dictionary of metadata, in format:
    metadata = [{'key': 'repo_url', 'value': repo_url, 'return_text': False },
                {'key': 'repo_id', 'value': repo_id, 'return_text': True },
                {'key': 'credential', 'value': credential, 'return_text': True },
                {'key': 'response_url', 'value': response_url, 'return_text': True },
                {'key': 'token', 'value': token, 'return_text': False },
                {'key': 'commit', 'value': commit, 'return_text': True }]

    '''
    params = dict()
    for item in metadata:
        if item['value'] == None:
            bot.logger.warning('%s not found in function call.',item['key'])        
            response = get_build_metadata(key=item['key'])
            item['value'] = response
        params[item['key']] = item['value']
        if item['key'] != 'credential':
            bot.logger.info('%s is set to %s',item['key'],item['value'])        
    return params
