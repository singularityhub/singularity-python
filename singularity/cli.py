#!/usr/bin/env python

'''
cli.py: part of singularity package

Last updated: Singularity version 2.1

'''

from singularity.utils import (
    getsudo, 
    run_command, 
    check_install, 
    write_json, 
    write_file
)

from singularity.logman import bot

from glob import glob
import subprocess
import tempfile
import shutil
import json
import os
import re

class Singularity:
    
    def __init__(self,sudo=True,verbose=False,sudopw=None):
       '''upon init, store user password to not ask for it again'''

       self.sudopw = sudopw

       # Try getting from environment
       if self.sudopw == None:
           self.sudopw = os.environ.get('pancakes',None)

       if sudo == True and self.sudopw == None:
           self.sudopw = getsudo()
           self.verbose = verbose



    def run_command(self,cmd,sudo=False,suppress=False):
        '''run_command is a wrapper for the global run_command, checking first
        for sudo (and asking for it to store) if sudo is needed.
        :param cmd: the command to run
        :param sudo: does the command require sudo?
        :param suppress: run os.system instead of os.popen if sudo required
        '''
        if sudo==True:
            if self.sudopw == None:
                self.sudopw = getsudo()
            output = run_command(cmd,sudopw=self.sudopw,suppress=suppress)
        else:
            output = run_command(cmd,suppress=suppress) # suppress doesn't make difference here
        return output



    def help(self,command=None,stdout=True):
        '''help prints the general function help, or help for a specific command
        :param command: the command to get help for, if none, prints general help
        '''
        cmd = ['singularity','--help']
        if command != None:
            cmd.append(command)
        help = self.run_command(cmd)

        # Print to console, or return string to user
        if stdout == True:
            print(help)
        else:
            return help



    def create(self,image_path,size=None):
        '''create will create a a new image
        :param image_path: full path to image
        :param size: image sizein MiB, default is 1024MiB
        :param filesystem: supported file systems ext3/ext4 (ext[2/3]: default ext3
        '''        
        if size == None:
            size=1024

        cmd = ['singularity','create','--size',str(size),image_path]
        self.run_command(cmd,sudo=True)



    def bootstrap(self,image_path,spec_path):
        '''create will bootstrap an image using a spec
        :param image_path: full path to image
        :param spec_path: full path to the spec file (Singularity)
        '''        

        cmd = ['singularity','bootstrap',image_path,spec_path]
        return self.run_command(cmd,sudo=True)



    def execute(self,image_path,command,writable=False,contain=False):
        '''execute: send a command to a container
        :param image_path: full path to singularity image
        :param command: command to send to container
        :param writable: This option makes the file system accessible as read/write
        :param contain: This option disables the automatic sharing of writable
                        filesystems on your host
        :param verbose: add --verbose option (default is false) 
        '''
        sudo = False    
        cmd = ["singularity","exec"]
        cmd = self.add_flags(cmd,writable=writable,contain=contain)

        # Needing sudo?
        if writable == True:
            sudo = True

        cmd = cmd + [image_path,command]

        # Run the command
        return self.run_command(cmd,sudo=sudo)



    def export(self,image_path,pipe=False,output_file=None,command=None,export_format="tar"):
        '''export will export an image, sudo must be used.
        :param image_path: full path to image
        :param pipe: export to pipe and not file (default, False)
        :param output_file: if pipe=False, export tar to this file. If not specified, 
        will generate temporary directory.
        :param export_format: the export format (only tar currently supported)
        '''
        sudo = True
        cmd = ['singularity','export']

        if export_format != "tar":
            print("Currently only supported export format is tar.")
            return None
    
        # If the user has specified export to pipe, we don't need a file
        if pipe == True:
            cmd.append(image_path)
        else:
            _,tmptar = tempfile.mkstemp(suffix=".%s" %export_format)
            os.remove(tmptar)
            cmd = cmd + ["-f",tmptar,image_path]
            self.run_command(cmd,sudo=sudo)

            # Was there an error?            
            if not os.path.exists(tmptar):
                print('Error generating image tar')
                return None

            # if user has specified output file, move it there, return path
            if output_file != None:
                shutil.copyfile(tmptar,output_file)
                return output_file
            else:
                return tmptar

        # Otherwise, return output of pipe    
        return self.run_command(cmd,sudo=sudo)



    def importcmd(self,image_path,input_source,import_type=None,command=None):
        '''import will import (stdin) to the image
        :param image_path: path to image to import to. 
        :param input_source: input source or file
        :param import_type: if not specified, imports whatever function is given
        :param command: replace "tar" command
        '''
        sudo = True
        if import_type == "tar":
            cmd = ['singularity','import','--file',input_source]
            if command != None:
                cmd = cmd + ["--command",command]
            cmd.append(image_path)
            return self.run_command(cmd,sudo=sudo)
        else:
            cmd = ['singularity','import',image_path,input_source]
            return self.run_command(cmd,sudo=sudo)

        return None



    def run(self,image_path,command,writable=False,contain=False):
        '''run will run a command inside the container, probably not intended for within python
        :param image_path: full path to singularity image
        :param command: command to send to container
        '''
        sudo = False
        cmd = ["singularity","run"]
        cmd = self.add_flags(cmd,writable=writable,contain=contain)

        # Conditions for needing sudo
        if writable == True:
            sudo = True

        cmd = cmd + [image_path,command]

        # Run the command
        return self.run_command(cmd,sudo=sudo)

    def start(self,image_path,writable=False,contain=False):
        '''start will start a container
        '''
        sudo = False
        cmd = ['singularity','start']
        cmd = self.add_flags(cmd,writable=writable,contain=contain)
        if writable == True:
            sudo = True

        cmd.append(image_path)
        return self.run_command(cmd,sudo=sudo)


    def stop(self,image_path):
        '''stop will stop a container
        '''
        cmd = ['singularity','stop',image_path]
        return self.run_command(cmd)



    def add_flags(self,cmd,writable,contain):
        '''check_args is a general function for adding flags to a command list
        :param writable: adds --writable
        :param contain: adds --contain
        '''

        # Does the user want verbose output?
        if self.verbose == True:
            cmd.append('--verbose')       

        # Does the user want to make the container writeable?
        if writable == True:
            cmd.append('--writable')       

        if contain == True:
            cmd.append('--contain')       

        return cmd


######################################################################################################
# HELPER FUNCTIONS
######################################################################################################

def get_image(image,return_existed=False,sudopw=None,size=None):
    '''get_image will return the file, if it exists, or if it's docker or
    shub, will use the Singularity command line tool to generate a temporary image
    :param image: the image file or path (eg, docker://)
    :param return_existed: if True, will return image_path,existed to tell if
    an image is temporary (if existed==False)
    :param sudopw: needed to create an image, if docker:// provided
    '''
    existed = True

    # Is the image a docker image?
    if re.search('^docker://',image):
        existed = False
        if sudopw == None:
            sudopw = os.environ.get('pancakes',None)

        if sudopw != None:
            cli = Singularity(sudopw=sudopw)
        else:
            cli = Singularity() # This command will ask the user for sudo

        tmpdir = tempfile.mkdtemp()
        image_name = "%s.img" %image.replace("docker://","") 
        bot.logger.info("Found docker image %s, creating and importing...",image_name)
        image_path = "%s/%s" %(tmpdir,image_name)
        cli.create(image_path,size=size)
        cli.importcmd(image_path=image_path,
                      input_source=image)
        image = image_path

    if os.path.exists(image):
        image = os.path.abspath(image)
        if return_existed == True:
            return image,existed
        return image
    return None
