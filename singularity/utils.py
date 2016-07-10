#!/usr/bin/env python

'''
utils.py: part of singularity package

'''
import singularity.__init__ as hello
from exceptions import OSError
import subprocess
import tempfile
import zipfile
import shutil
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


def get_installdir():
    '''get_installdir returns the installation directory of the application
    '''
    return os.path.abspath(os.path.dirname(hello.__file__))


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
        # If it's a list, write to new file, and save
        if isinstance(content,list):
            filey = write_file("%s/%s" %(tmpdir,filename),"\n".join(content))
            print("Adding %s to package..." %(filename))
            zf.write(filey,filename)
            os.remove(filey)
        # If it's a string, do the same
        elif isinstance(content,str):
            filey = write_file("%s/%s" %(tmpdir,filename),content)
            print("Adding %s to package..." %(filename))
            zf.write(filey,filename)
            os.remove(filey)
        # If the file exists, just write it into a new archive
        elif os.path.exists(content):
            print("Adding %s to package..." %(filename))
            zf.write(content,filename)

    # Close the zip file    
    zf.close()

    if output_folder != None:
        shutil.copyfile(output_zip,"%s/%s"%(output_folder,zip_name))
        shutil.rmtree(tmpdir)
        output_zip = "%s/%s"%(output_folder,zip_name)

    return output_zip


def write_file(filename,content):
    '''write_file will open a file, "filename" and write content, "content"
    and properly close the file
    '''
    filey = open(filename,'wb')
    filey.writelines(content)
    filey.close()
    return filename
