#!/usr/bin/env python

'''
utils.py: part of singularity package

'''

import singularity.__init__ as hello
from exceptions import OSError
import subprocess
import simplejson
import tempfile
import zipfile
import shutil
import os


def check_install(software="singularity"):
    '''check_install will attempt to run the singularity command, and return an error
    if not installed. The command line utils will not run without this check.
    '''    
  
    cmd = [software,'--version']
    version = run_command(cmd,error_message="Cannot find singularity. Is it installed?")
    if version != None:
        print("Found %s version %s" %(software.upper(),version))
        return True
    else:
        return False


def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(hello.__file__))


def get_script(script_name):
    '''get_script will return a script_name, if it is included in singularity/scripts,
    otherwise will alert the user and return None
    :param script_name: the name of the script to look for
    '''
    install_dir = get_installdir()
    script_path = "%s/scripts/%s" %(install_dir,script_name)
    if os.path.exists(script_path):
        return script_path
    else:
        print("Script %s is not included in singularity-python!")
        return None

def getsudo():
    sudopw = raw_input('[sudo] password for %s: ' %(os.environ['USER']))
    return sudopw


def run_command(cmd,error_message=None,sudopw=None,suppress=False):
    '''run_command uses subprocess to send a command to the terminal.
    :param cmd: the command to send, should be a list for subprocess
    :param error_message: the error message to give to user if fails, 
    if none specified, will alert that command failed.
    :param execute: if True, will add `` around command (default is False)
    :param sudopw: if specified (not None) command will be run asking for sudo
    '''
    if sudopw != None:
        cmd = ' '.join(["echo", sudopw,"|","sudo","-S"] + cmd)
        if suppress == False:
            output = os.popen(cmd).read().strip('\n')
        else:
            output = cmd
            os.system(cmd)
    else:
        try:
            process = subprocess.Popen(cmd,stdout=subprocess.PIPE)
            output, err = process.communicate()
        except OSError as error: 
            if error.errno == os.errno.ENOENT:
                print(error_message)
            else:
                print(err)
            return None
    
    return output


############################################################################
## FILE OPERATIONS #########################################################
############################################################################

def zip_up(file_list,zip_name,output_folder=None):
    '''zip_up will zip up some list of files into a package (.zip)
    :param file_list: a list of files to include in the zip.
    :param output_folder: the output folder to create the zip in. If not 
    :param zip_name: the name of the zipfile to return.
    specified, a temporary folder will be given.
    '''
    tmpdir = tempfile.mkdtemp()
   
    # Make a new archive    
    output_zip = "%s/%s" %(tmpdir,zip_name)
    zf = zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED)

    # Write files to zip, depending on type
    for filename,content in file_list.iteritems():

        print("Adding %s to package..." %(filename))

        # If it's a list, write to new file, and save
        if isinstance(content,list):
            filey = write_file("%s/%s" %(tmpdir,filename),"\n".join(content))
            zf.write(filey,filename)
            os.remove(filey)
        # If it's a dict, save to json
        elif isinstance(content,dict):
            filey = write_json(content,"%s/%s" %(tmpdir,filename))
            zf.write(filey,filename)
            os.remove(filey)
        # If it's a string, do the same
        elif isinstance(content,str):
            filey = write_file("%s/%s" %(tmpdir,filename),content)
            zf.write(filey,filename)
            os.remove(filey)
        # If the file exists, just write it into a new archive
        elif os.path.exists(content):
            zf.write(content,filename)

    # Close the zip file    
    zf.close()

    if output_folder != None:
        shutil.copyfile(output_zip,"%s/%s"%(output_folder,zip_name))
        shutil.rmtree(tmpdir)
        output_zip = "%s/%s"%(output_folder,zip_name)

    return output_zip


def write_file(filename,content,mode="wb"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    filey = open(filename,mode)
    filey.writelines(content)
    filey.close()
    return filename


def write_json(json_obj,filename,mode="w",print_pretty=True):
    '''write_json will (optionally,pretty print) a json object to file
    :param json_obj: the dict to print to json
    :param filename: the output file to write to
    :param pretty_print: if True, will use nicer formatting   
    '''
    filey = open(filename,mode)
    if print_pretty == True:
        filey.writelines(simplejson.dumps(json_obj, indent=4, separators=(',', ': ')))
    else:
        filey.writelines(simplejson.dumps(json_obj))
    filey.close()
    return filename


def read_file(filename,mode="rb"):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    filey = open(filename,mode)
    content = filey.readlines()
    filey.close()
    return content

