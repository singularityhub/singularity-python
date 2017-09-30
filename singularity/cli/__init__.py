'''

The MIT License (MIT)

Copyright (c) 2016-2017 Vanessa Sochat, All Rights Reserved

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from .utils import get_image
from singularity.utils import run_command
from singularity.logger import bot

from glob import glob
import json
import sys
import os
import re


class Singularity:
    

    def __init__(self,sudo=False,debug=False,quiet=False):
       '''upon init, store user password to not ask for it again'''

       self.debug = debug
       self.quiet = quiet


    def run_command(self, cmd, sudo=False, quiet=False):
        '''run_command is a wrapper for the global run_command, checking first
        for sudo and exiting on error if needed
        :param cmd: the command to run
        :param sudo: does the command require sudo?
        '''
        result = run_command(cmd,sudo=sudo)
        return_code = result['return_code']
        message = result['message']
        if return_code == 0:
            if isinstance(message,bytes):
                message=message.decode('utf-8')
            return message
        if quiet is False:
            bot.error("Return Code %s: %s" %(return_code,
                                             message))
        sys.exit(1)


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


    def println(self,output,quiet=False):
        '''print will print the output, given that quiet is not True. This
        function also serves to convert output in bytes to utf-8
        '''
        if isinstance(output,bytes):
            output = output.decode('utf-8')
        if self.quiet is False and quiet is False:
            print(output)
        

    def build(self, image_path, spec_path, paranoid=False):
        '''build a singularity image, optionally for a secure build
           (requires sudo)'''
        if self.debug is True:
            cmd = ['singularity','--debug','build']
        else:
            cmd = ['singularity','build']

        if paranoid is True:
            cmd.append('--paranoid')

        cmd = cmd + [image_path,spec_path]

        output = self.run_command(cmd,sudo=True)
        self.println(output)     
        return image_path


    def bootstrap(self,image_path,spec_path):
        '''create will bootstrap an image using a spec
        :param image_path: full path to image
        :param spec_path: full path to the spec file (Singularity)
        ''' 
        if self.debug is True:
            cmd = ['singularity','--debug','bootstrap',image_path,spec_path]
        else:
            cmd = ['singularity','bootstrap',image_path,spec_path]
        output = self.run_command(cmd,sudo=True)
        self.println(output)     
        return image_path


    def compress(self,image_path):
        '''compress will (properly) compress an image'''
        if os.path.exists(image_path):
            compressed_image = "%s.gz" %image_path
            os.system('gzip -c -6 %s > %s' %(image_path,compressed_image))
            return compressed_image
        else:
            bot.error("Cannot find image %s" %image_path)
            sys.exit(1)

    def create(self,image_path,size=None,sudo=False):
        '''create will create a a new image
        :param image_path: full path to image
        :param size: image sizein MiB, default is 1024MiB
        :param filesystem: supported file systems ext3/ext4 (ext[2/3]: default ext3
        '''        
        if size == None:
            size=1024

        if self.debug == True:
            cmd = ['singularity','--debug','create','--size',str(size),image_path]
        else:
            cmd = ['singularity','create','--size',str(size),image_path]
        output = self.run_command(cmd,sudo=sudo)
        self.println(output)

        if not os.path.exists(image_path):
            bot.error("Could not create image %s" %image_path)
            sys.exit(1)

        return image_path


    def decompress(self,image_path,quiet=True):
        '''decompress will (properly) decompress an image'''

        if not os.path.exists(image_path):
            bot.error("Cannot find image %s" %image_path)
            sys.exit(1)

        extracted_file = image_path.replace('.gz','')
        cmd = ['gzip','-d','-f', image_path]
        result = self.run_command(cmd, quiet=quiet) # exits if return code != 0
        return extracted_file
        

    def execute(self,image_path,command,writable=False,contain=False):
        '''execute: send a command to a container
        :param image_path: full path to singularity image
        :param command: command to send to container
        :param writable: This option makes the file system accessible as read/write
        :param contain: This option disables the automatic sharing of writable
                        filesystems on your host
        '''
        sudo = False    
        if self.debug == True:
            cmd = ["singularity",'--debug',"exec"]
        else:
            cmd = ["singularity",'--quiet',"exec"]

        cmd = self.add_flags(cmd,
                             writable=writable,
                             contain=contain)

        if writable is True:
            sudo = True

        if not isinstance(command,list):
            command = command.split(' ')

        cmd = cmd + [image_path] + command
        return self.run_command(cmd,sudo=sudo)



    def export(self,image_path,export_format="tar",old_version=False):
        '''export will export an image, sudo must be used.
        :param image_path: full path to image
        will generate temporary directory.
        :param export_format: the export format (only tar currently supported)
        '''
        if old_version == True:
            tmptar = "/tmp/tmptar.tar"
            cmd = ['singularity','export','-f','/tmp/tmptar.tar']
        else:
            cmd = ['singularity','export']

        if export_format is not "tar":
            print("Currently only supported export format is tar.")
            return None
    
        cmd.append(image_path)
        output = self.run_command(cmd)
        
        if old_version == True:
            return tmptar
        return output


    def importcmd(self,image_path,input_source):
        '''import will import (stdin) to the image
        :param image_path: path to image to import to. 
        :param input_source: input source or file
        :param import_type: if not specified, imports whatever function is given
        '''
        cmd = ['singularity','import',image_path,input_source]
        output = self.run_command(cmd,sudo=False)
        self.println(output)        
        return image_path


    def inspect(self,image_path,json=True,labels=True,
                runscript=True,test=True,deffile=True,
                environment=True,quiet=False):
        '''inspect will show labels, defile, runscript, and tests for an image
        :param image_path: path of image to inspect
        :param json: print json instead of raw text (default True)
        :param labels: show labels (default True):
        :param runscript: show runscript (default True)
        :param test: show test file (default True)
        :param environment: show environment (default True)
        '''
        cmd = ['singularity','--quiet','inspect']
        options = locals()
        acceptable = ['environment','json','deffile','labels','runscript','test']
        for key,option in options.items():
            if key in acceptable:
                if option is True:
                    cmd.append('--%s' %(key))

        cmd.append(image_path)
        output = self.run_command(cmd)
        self.println(output,quiet=quiet)    
        return output


    def pull(self,image_path,pull_folder=None,
                             name_by_hash=False,
                             name_by_commit=False,
                             image_name=None,
                             size=None):

        '''pull will pull a singularity hub image
        :param image_path: full path to image
        :param name_by: can be one of commit or hash, default is by image name
        ''' 

        if image_name is not None:
            name_by_hash=False
            name_by_commit=False

        if not image_path.startswith('shub://') and not image_path.startswith('docker://'):
            bot.error("pull is only valid for docker and shub, %s is invalid." %image_name)
            sys.exit(1)           

        if self.debug == True:
            cmd = ['singularity','--debug','pull']
        else:
            cmd = ['singularity','pull']

        if image_path.startswith('shub://'):
            if pull_folder is not None:
                os.environ['SINGULARITY_PULLFOLDER'] = pull_folder
            if image_name is not None:
                bot.debug("user specified naming pulled image %s" %image_name)
                cmd = cmd +["--name",image_name]
            elif name_by_commit is True:
                bot.debug("user specified naming by commit.")
                cmd.append("--commit")
            elif name_by_hash is True:
                bot.debug("user specified naming by hash.")
                cmd.append("--hash")
 
        elif image_path.startswith('docker://'):
            if size is not None:
                cmd = cmd + ["--size",size]
            if image_name is None:
                image_name = "%s.img" %image_path.replace("docker://","").replace("/","-")
            if pull_folder is not None:
                image_name = "%s/%s" %(pull_folder,image_name)
            cmd = cmd + ["--name",image_name]
 

        cmd.append(image_path)
        output = self.run_command(cmd)
        return output.split("Container is at:")[-1].strip('\n').strip()
        


    def run(self,image_path,args=None,writable=False,contain=False):
        '''run will run the container, with or withour arguments (which
        should be provided in a list)
        :param image_path: full path to singularity image
        :param args: args to include with the run
        '''
        sudo = False
        cmd = ["singularity",'--quiet',"run"]
        cmd = self.add_flags(cmd,writable=writable,contain=contain)
        cmd = cmd + [image_path]

        # Conditions for needing sudo
        if writable is True:
            sudo = True
        
        if args is not None:        
            if not isinstance(args,list):
                args = args.split(' ')
            cmd = cmd + args

        result = self.run_command(cmd,sudo=sudo)
        result = result.strip('\n')
        try:
            result = json.loads(result)
        except:
            pass
        return result


    def get_labels(self,image_path):
        '''get_labels will return all labels defined in the image
        '''
        cmd = ['singularity','exec',image_path,'cat','/.singularity/labels.json']
        labels = self.run_command(cmd)
        if len(labels) > 0:
            return json.loads(labels)
        return labels
        

    def get_args(self,image_path):
        '''get_args will return the subset of labels intended to be arguments
        (in format SINGULARITY_RUNSCRIPT_ARG_*
        '''
        labels = self.get_labels(image_path)
        args = dict()
        for label,values in labels.items():
            if re.search("^SINGULARITY_RUNSCRIPT_ARG",label):
                vartype = label.split('_')[-1].lower()
                if vartype in ["str","float","int","bool"]:
                    args[vartype] = values.split(',')
        return args


    def add_flags(self,cmd,writable=False,contain=False):
        '''check_args is a general function for adding flags to a command list
        :param writable: adds --writable
        :param contain: adds --contain
        ''' 
        if writable == True:
            cmd.append('--writable')       

        if contain == True:
            cmd.append('--contain')       

        return cmd
