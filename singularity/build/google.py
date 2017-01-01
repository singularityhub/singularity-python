#!/usr/bin/env python

'''
build/google.py: build functions for singularity hub google compute engine

'''

from singularity.api import (
    api_get, 
    api_put, 
    api_post
)

from singularity.build.utils import get_singularity_version

from singularity.package import (
    build_from_spec, 
    estimate_image_size,
    package
)

from singularity.utils import (
    get_installdir, 
    read_file, 
    write_file, 
    download_repo
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
import re
import requests
import shutil
import subprocess
import sys
import tempfile
import uuid
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
              repo_id=None,commit=None,verbose=True,response_url=None,secret=None,branch=None):
    '''run_build will generate the Singularity build from a spec_file from a repo_url. 
    If no arguments are required, the metadata api is queried for the values.
    :param build_dir: directory to do the build in. If not specified,
    will use temporary.   
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
                {'key': 'container_id', 'value': None, 'return_text': True },
                {'key': 'spec_file', 'value': spec_file, 'return_text': True }]

    # Default spec file is Singularity
    if spec_file == None:
        spec_file = "Singularity"

    if bucket_name == None:
        bucket_name = "singularity-hub"

    # Obtain values from build
    params = get_build_params(metadata)

    # Download the repo and image
    repo = download_repo(repo_url=params['repo_url'],
                         destination=build_dir)

    os.chdir(build_dir)
    if params['branch'] != None:
        bot.logger.info('Checking out branch %s',params['branch'])
        os.system('git checkout %s' %(params['branch']))

    if params['commit'] != None:
        bot.logger.info('Checking out commit %s',params['commit'])
        os.system('git checkout %s .' %(params['commit']))

    # From here on out commit is used as a unique id, if we don't have one, we use current
    else:
        params['commit'] = repo.commit().__str__()
        bot.logger.warning("commit not specified, setting to current %s", params['commit'])


    if os.path.exists(spec_file):
        bot.logger.info("Found spec file %s in repository",spec_file)

        # If size is None, get from image + 200 padding
        if params['size'] == None:
            bot.logger.info("Size not detected for build. Will estimate with 200MB padding.")
            params['size'] = estimate_image_size(spec_file=spec_file,
                                                 sudopw='')

        image = build_from_spec(spec_file=spec_file, # default will package the image
                                size=params['size'],
                                sudopw='', # with root should not need sudo
                                output_folder=build_dir,
                                build_dir=build_dir)

        # Compress image
        compressed_image = "%s.img.gz" %image
        os.system('gzip -c -9 %s > %s' %(image,compressed_image))
        
        # Package the image metadata (files, folders, etc)
        image_package = package(image_path=image,
                                spec_path=spec_file,
                                output_folder=build_dir,
                                sudopw='',
                                remove_image=True,
                                verbose=True)

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
            bucket = get_bucket(storage_service,bucket_name)

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
                        "container_id": params['container_id']}

            # Did the user specify a specific log file?
            logfile = get_build_metadata(key='logfile')
            if logfile != None:
                response['logfile'] = logfile

            if params['branch'] != None:
                response['branch'] = params['branch']


            if params['token'] != None:
                response['token'] = params['token']

            # Send it back!
            if params['response_url'] != None:
                finish = requests.post(params['response_url'],data=response)
    
    else:
        # Tell the user what is actually there
        present_files = glob("*")
        bot.logger.error("Build file %s not found in repository",spec_file)
        bot.logger.info("Found files are %s","\n".join(present_files))


    # Clean up
    shutil.rmtree(build_dir)


def finish_build(logfile,singularity_version=None,repo_url=None,bucket_name=None,commit=None,verbose=True,repo_id=None,
                 logging_response_url=None,secret=None,token=None):
    '''finish_build will finish the build by way of sending the log to the same bucket.
    :param build_dir: directory to do the build in. If not specified,
    will use temporary.   
    :param logfile: the logfile to send.
    :param repo_url: the url to download the repo from
    :param repo_id: the repo_id to uniquely identify the repo (in case name changes)
    :param commit: the commit to checkout. If none provided, will use most recent.
    :param bucket_name: the name of the bucket to send files to
    :param singularity_version: the version of singularity installed
    :param verbose: print out extra details as we go (default True)    
    :param secret: a secret to match to the correct container
    :param logging_response_url: the logging response url to send the response back to.
    :: note: this function is currently configured to work with Google Compute
    Engine metadata api, and should (will) be customized if needed to work elsewhere 
    '''
    # If we are building the image, this will not be set
    go = get_build_metadata(key='dobuild')
    if go == None:
        sys.exit(0)

    if singularity_version == None:
        singularity_version = get_singularity_version(singularity_version)

    # Get variables from the instance metadata API
    metadata = [{'key': 'logging_url', 'value': logging_response_url, 'return_text': True },
                {'key': 'repo_url', 'value': repo_url, 'return_text': False },
                {'key': 'repo_id', 'value': repo_id, 'return_text': True },
                {'key': 'token', 'value': token, 'return_text': False },
                {'key': 'commit', 'value': commit, 'return_text': True },
                {'key': 'bucket_name', 'value': bucket_name, 'return_text': True },
                {'key': 'secret', 'value': secret, 'return_text': True }]

    if bucket_name == None:
        bucket_name = "singularity-hub"

    # Obtain values from build
    params = get_build_params(metadata)

    # Start the storage service, retrieve the bucket
    storage_service = get_storage_service()
    bucket = get_bucket(storage_service,bucket_name)
    image_path = "%s/%s" %(re.sub('^http.+//www[.]','',params['repo_url']),params['commit'])

    # Upload the log file
    log_file = upload_file(storage_service,
                           bucket=bucket,
                           bucket_path=image_path,
                           file_name=logfile)
                
    # Finally, package everything to send back to shub
    response = {"log": json.dumps(log_file),
                "repo_url": params['repo_url'],
                "commit": params['commit'],
                "repo_id": params['repo_id'],
                "secret": params['secret']}


    if params['token'] != None:
        response['token'] = params['token']

    # Send it back!
    if params['logging_url'] != None:
        finish = requests.post(params['logging_url'],data=response)
    

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


def sniff_extension(file_path,verbose=True):
    '''sniff_extension will attempt to determine the file type based on the extension,
    and return the proper mimetype
    :param file_path: the full path to the file to sniff
    :param verbose: print stuff out
    '''
    mime_types =    { "xls": 'application/vnd.ms-excel',
                      "xlsx": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      "xml": 'text/xml',
                      "ods": 'application/vnd.oasis.opendocument.spreadsheet',
                      "csv": 'text/plain',
                      "tmpl": 'text/plain',
                      "pdf":  'application/pdf',
                      "php": 'application/x-httpd-php',
                      "jpg": 'image/jpeg',
                      "png": 'image/png',
                      "gif": 'image/gif',
                      "bmp": 'image/bmp',
                      "txt": 'text/plain',
                      "doc": 'application/msword',
                      "js": 'text/js',
                      "swf": 'application/x-shockwave-flash',
                      "mp3": 'audio/mpeg',
                      "zip": 'application/zip',
                      "rar": 'application/rar',
                      "tar": 'application/tar',
                      "arj": 'application/arj',
                      "cab": 'application/cab',
                      "html": 'text/html',
                      "htm": 'text/html',
                      "default": 'application/octet-stream',
                      "folder": 'application/vnd.google-apps.folder',
                      "img" : "application/octet-stream" }

    ext = os.path.basename(file_path).split('.')[-1]

    mime_type = mime_types.get(ext,None)

    if mime_type == None:
        mime_type = mime_types['txt']

    if verbose==True:
        bot.logger.info("%s --> %s", file_path, mime_type)

    return mime_type
