#!/usr/bin/env python

'''
utils.py: part of singularity package

'''
from exceptions import OSError
import subprocess
import tempfile
import os

def check_install():
    '''check_install will attempt to run the singularity command, and return an error
    if not installed. The command line utils will not run without this check.
    '''    

    try:
        process = subprocess.Popen(["singularity", "--version"],stdout=subprocess.PIPE)
        version, err = process.communicate()
    except OSError as error: 
        if error.errno == os.errno.ENOENT:
            print('Cannot find singularity. Is it installed?')
        else:
            print('Another error')
        return False
    print("Found Singularity version %s" %version)
    return True


def export_image(image,export_format="tar"):
    '''export_image uses singularity command line (bash) tool to export tar to a temporary directory
    :param export_format: the export format, currently only supported type is tar
    '''

    if export_format != "tar":
        print("Currently only supported export format is tar.")
        return None

    # We need sudo to export
    sudopw = raw_input('[sudo] password for %s: ' %(os.environ['USER']))
    
    _,tmptar = tempfile.mkstemp(suffix=".%s" %export_format)
    os.remove(tmptar)
    cmd = ' '.join(["echo", sudopw,"|","sudo","-S","singularity","export","-f",tmptar,image])
    os.system(cmd)
    if not os.path.exists(tmptar):
        print('Error generating image tar')
        return None
    return tmptar


def zip_up(file_list):
    '''zip_up will zip up some list of files into a package (.zip)
    :param file_list: a list of files to include in the zip.
    '''
    print("WRITE ME!")
