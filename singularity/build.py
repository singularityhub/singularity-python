#!/usr/bin/env python

'''
build.py: functions for singularity hub builders

'''

from singularity.api import api_get, api_put
from singularity.boutiques import get_boutiques_json
from singularity.package import build_from_spec
from singularity.utils import get_installdir, read_file, write_file, download_repo

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from glob import glob
import inspect
import imp
import json
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials
from glob import glob
import os
import re
import requests
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile


api_base = "http://www.singularity-hub.org/api"


def google_drive_connect(credential):

    # If it's a dict, assume json and load into credential
    if isinstance(credential,dict):
        credential = client.Credentials.new_from_json(json.dumps(credential))

    # If the user has a credential object, check if it's good
    if credential.invalid is True:
        # This probably won't work, needs to be redone on shub server
        credential.refresh()

    # Authorize with http
    http_auth = credential.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=http_auth)
    return drive_service


def create_folder(drive_service,folder_name,parent_folders=None):
    '''create_folder will create a folder (folder_name) in optional parent_folder
    if no parent_folder is specified, will be placed at base of drive
    :param drive_service: drive service created by google_drive_connect
    :param folder_name: the name of the folder to create
    :param parent_folders: one or more parent folder names, either a string or list 
    '''
    file_metadata = {
        'name' : folder_name,
        'mimeType' : 'application/vnd.google-apps.folder'
    }
    # Do we have one or more parent folders?
    if parent_folders != None:
        if not isinstance(parent_folders,list):
            parent_folders = [parent_folders]
        file_metadata ['parents'] = parent_folders    
    folder = drive_service.files().create(body=file_metadata,
                                          fields='id').execute()
    return folder


def create_file(drive_service,folder_id,file_path,file_name=None,verbose=True):
    '''create_folder will create a folder (folder_name) in optional parent_folder
    if no parent_folder is specified, will be placed at base of drive
    :param drive_service: drive service created by google_drive_connect
    :param folder_id: the id of the folder to upload to
    :param file_path: the path of the file to add
    :param file_name: the name for the file. If not specified, will use current file name
    :param parent_folders: one or more parent folder names, either a string or list 
    :param verbose: print out the file type assigned to the file_path
    '''
    if file_name == None:
        file_name = os.path.basename(file_path)

    mimetype = sniff_extension(file_path,verbose=verbose)

    file_metadata = {
        'name' : file_name,
        'parents': [ folder_id ]
    }

    media = MediaFileUpload(file_path,
                        mimetype=mimetype,
                        resumable=True)
    return drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()


def permissions_callback(request_id, response, exception):
    if exception:
        print(exception)
    else:
        print("Permission Id: %s" % response.get('id'))


def set_reader_permissions(drive_service,file_ids):
    '''set_permission will set a permission level (default is reader) for one
    or more files. If anything other than "reader" is used for permission, 
    email must be provided
    :param drive_service: the drive service created with google_drive_connect
    :param file_ids: one or more file_ids, should be string or list
    '''

    new_permission = { 'type': "anyone",
                       'role': "reader",
                       'withLink': True }

    if isinstance(file_ids,list) == False:
        file_ids = [file_ids]

    batch = drive_service.new_batch_http_request(callback=permissions_callback)

    for file_id in file_ids:
        batch.add(drive_service.permissions().create(
                  fileId=file_id['id'],
                  body=new_permission))

    batch.execute()


def get_folder(drive_service,folder_name=None,create=True):
    '''get_folder will return the folder with folder_name, and if create=True,
    will create it if not found. If folder is found or created, the metadata is
    returned, otherwise None is returned
    :param drive_service: the drive_service created from google_drive_connect
    :param folder_name: the name of the folder to search for, item ['title'] field
    '''
    if folder_name == None:
        folder_name = 'singularity-hub'

    folders = drive_service.files().list(q='mimeType="application/vnd.google-apps.folder"').execute()

    for folder in folders['files']:
        if folder['name'] == folder_name:
            return folder

    folder = None

    if create == True:
        folder = create_folder(drive_service,folder_name)

    return folder


def get_download_links(build_files):
    '''get_files will use a drive_service to return a list of build file objects
    :param build_files: a list of build_files, each a dictionary with an id for the file
    '''
    links = []
    for build_file in build_files:
        link = "https://drive.google.com/uc?export=download&id=%s" %(build_file['id'])
        build_file['link'] = link
        links.append(build_file)
    return links


def google_drive_setup(drive_service,image_path=None):
    '''google_drive_setup will connect to a Google drive, check for the singularity 
    folder, and if it doesn't exist, create it, along with other collection and image
    metadata. The final upload folder for the image and other stuffs is returned
    :param image_path: should be the path to the image, from within the singularity-hub folder
    (eg, www.github.com/vsoch/singularity-images). If not defined, a folder with the commit id
    will be created in the base of the singularity-hub google drive folder
    '''
    singularity_folder = get_folder(drive_service,folder_name='singularity-hub')

    # If the user wants a more custom path
    if image_path != None:

        folders = [x.strip(" ") for x in image_path.split("/")]
        parent_folder = singularity_folder['id']

        for folder in folders:
            # The last folder created, the destination for our files, will be returned
            singularity_folder = create_folder(drive_service=drive_service,
                                               folder_name=folder,
                                               parent_folders=parent_folder)
            parent_folder = singularity_folder['id']

    return singularity_folder    
    

def run_build(build_dir=None,spec_file=None,repo_url=None,token=None,
              repo_id=None,commit=None,credential=None,verbose=True,response_url=None):
    '''run_build will generate the Singularity build from a spec_file from a repo_url. 
    If no arguments are required, the metadata api is queried for the values.
    :param build_dir: directory to do the build in. If not specified,
    will use temporary.   
    :param spec_file: the spec_file name to use, assumed to be in git repo
    :param repo_url: the url to download the repo from
    :param repo_id: the repo_id to uniquely identify the repo (in case name changes)
    :param commit: the commit to checkout
    :param credential: the credential to send the image to.
    :param verbose: print out extra details as we go (default True)    
    :param token: a token to send back to the server to authenticate adding the build
    :param response_url: the build url to send the response back to. Should also come
    from metadata. If not specified, no response is sent
    :: note: this function is currently configured to work with Google Compute
    Engine metadata api, and should (will) be customized if needed to work elsewhere 
    '''
    
    if build_dir == None:
        build_dir = tempfile.mkdtemp()

    # Get variables from the environment
    if commit == None:
        commit = get_build_metadata(key='commit')
    if repo_url == None:
        repo_url = get_build_metadata(key='repo_url')
    if repo_id == None:
        repo_url = get_build_metadata(key='repo_id')
    if credential == None:
        credential = get_build_metadata(key='credential',
                                        return_text=False)
    if build_url == None:
        response_url = get_build_metadata(key='response_url')

    # Token is a secret to send back to server to accept response
    if token == None:  
        token = get_build_metadata(key='token',
                                   return_text=False)

    # Download the repo and image
    repo = download_repo(repo_url=repo_url,
                         destination=build_dir)

    os.chdir(build_dir)
    if commit != None:
        os.system('git checkout %s .' %(commit))

    # From here on out commit is used as a unique id, if we don't have one, randomly make one
    if commit == None:
        commit = uuid.uuid4().__str__()

    if os.path.exists(spec_file):

        image_package = build_from_spec(spec=spec_file,
                                        name=commit,
                                        size=None,
                                        sudopw='', # with root should not need sudo
                                        output_folder=build_dir)

        # If doesn't error, run google_drive_setup and upload image
        if os.path.exists(image_package):
            dest_dir = "%s/build" %(build_dir)
            os.mkdir(dest_dir)
            with zipfile.ZipFile(image_package) as zf:
                zf.extractall(dest_dir)

            # The path to the images on google drive will be the github url/commit folder
            image_path = "%s/%s" %(re.sub('^http.+//www[.]','',repo_url),commit)
            build_files = glob("%s/*" %(dest_dir))
            drive_service = google_drive_connect(credential)
            upload_folder = google_drive_setup(drive_service=drive_service,
                                               image_path=image_path)    

            # For each file, upload to drive
            files = []
            for build_file in build_files:
                drive_file = create_file(drive_service,
                                         folder_id=upload_folder['id'],
                                         file_path=build_file)
                drive_file['name'] = os.path.basename(build_file)
                files.append(drive_file)

            # Set readable permissions
            set_reader_permissions(drive_service,files)
            
            # Get metadata to return to singularity-hub
            download_links = get_download_links(build_files=files)
         
            # Finally, package everything to send back to shub
            response = {"files":download_links,
                        "repo_url":repo_url,
                        "commit":commit,
                        "repo_id":repo_id}

            if token != None:
                response['token'] = token

            # Send it back!
            if response_url != None:
                response = api_put(url=response_url,
                                   data=response,
                                   token=token)


#####################################################################################
# METADATA
#####################################################################################


def get_build_metadata(key,return_text=True):
    '''get_build_metadata will return metadata about an instance from within it.
    :param key: the key to look upu
    :param return_text: return text (appropriate for one value, or if needs custom parsing. Otherwise, will return json
    '''
    headers = {"Metadata-Flavor":"Google"}
    url = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/%s" %(key)        
    response = api_get(url=url,headers=headers)
    # Successful query returns the result
    if response.status_code == 200:
        if return_text == True:
            return api_get(url=url,headers=headers).text
        return api_get(url=url,headers=headers).json()
    return None


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
        print("%s --> %s" %(file_path,mime_type))

    return mime_type
