#!/usr/bin/env python

'''
docker.py: part of singularity package

'''

from singularity.utils import check_install, getsudo, run_command
from singularity.package import get_image_hash
from singularity.cli import Singularity
import tempfile
import tarfile
import requests
import shutil
import os

dockerhub = ""

def docker2singularity(docker_image,output_folder=None):
    '''docker2singulrity is a wrapper for the Singularity.docker2singularity
    client function. Does not currently include runscript (/singularity) in image,
    but does export full docker image spec under /singularity.json
    :param docker_image: the full docker repo/image,eg "ubuntu:latest"
    :param output_folder: the output folder to create the image in. If not 
    specified, will use pwd.
    '''

    S = Singularity()
    docker_image = S.docker2singularity(docker_image=docker_image,
                                        output_dir=output_folder)
    return docker_image


def get_docker_guts(docker_image,sudopw=None):
    '''get_docker_guts will get the files and folders within a docker image by converting to tar first.
    :param docker_image: the name of the docker image, doesn't have to be on local machine (eg, ubuntu:latest) 
    :param sudopw: sudopw to use in function.
    '''
    if check_install('docker') == True:

        # get sudopwd once to send to all following commands
        if sudopw == None:
            print("\nYOU MUST ENTER PASSWORD TO CONTINUE AND USE DOCKER:")
            sudopw = getsudo() 

        cmd = ['docker','run','-d',docker_image,'tail','-f','/dev/null']
        runningid = run_command(cmd=cmd,sudopw=sudopw)
        # sha256:d59bdb51bb5c4fb7b2c8d90ae445e0720c169c553bcf553f67cb9dd208a4ec15
        
        # Take the first 12 characters to get id of container
        container_id=runningid[0:12]
 
        # Get image name
        cmd = ['docker','inspect','--format="{{.Config.Image}}"',container_id]
        image_name = run_command(cmd=cmd,sudopw=sudopw)

        # Export tar to get files and folders
        print("Extracting filesystem from %s, please wait..." %(docker_image))
        tmpdir = tempfile.mkdtemp()
        tmptar = "%s/%s.tar" %(tmpdir,container_id)
        cmd = ['docker','export',container_id,'>',tmptar]
        run_command(cmd=cmd,sudopw=sudopw,suppress=True)

        # Give the list a VERSION based on the tarfile
        version = get_image_hash(tmptar)
        dockerstuffs = {"VERSION": version,
                        "image":image_name}

        # Read in files and folders from the tar!
        tar = tarfile.open(tmptar)
        members = tar.getmembers()
        files = [x.path for x in members if x.isfile()]
        folders = [x.path for x in members if x.isdir()]
        dockerstuffs["files.txt"] = files
        dockerstuffs["folders.txt"] = folders

        # Finally,stop the container
        print("Stopping container... please wait!")
        run_command(cmd=['docker','stop',container_id],sudopw=sudopw)

        # clean up the temporary directory
        shutil.rmtree(tmpdir)
 
        return dockerstuffs
