#!/usr/bin/env python

'''
cli.py: part of singularity package

GENERAL COMMANDS:
    help          Show additional help for a command

CONTAINER USAGE COMMANDS:
    exec          Execute a command within container
    run           Launch a runscript within container
    shell         Run a Bourne shell within container
    start         Start a namespace daemon process in a container
    stop          Stop the namespace daemon process for a container

CONTAINER MANAGEMENT COMMANDS (requires root):
    bootstrap     Bootstrap a new Singularity image from scratch
    copy          Copy files from your host into the container
    create        Create a new container image
    expand        Grow the container image
    export        Export the contents of a container via a tar pipe
    import        Import/add container contents via a tar pipe
    mount         Mount a Singularity container image

Last updated: Singularity version 2.1

'''

from singularity.utils import getsudo, run_command, check_install, write_json, write_file
from glob import glob
import subprocess
import tempfile
import shutil
import json
import os


class Singularity:
    
    def __init__(self,sudo=True,verbose=False):
       '''upon init, store user password to not ask for it again'''

       self.sudopw = None 
       if sudo == True:
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


    def create(self,image_path,size=1024,filesystem="ext3"):
        '''create will create a a new image
        :param image_path: full path to image
        :param size: image sizein MiB, default is 1024MiB
        :param filesystem: supported file systems ext3/ext4 (ext[2/3]: default ext3

        USAGE: singularity [...] create [create options...] <container path>

        Create a new Singularity formatted blank image.

        CREATE OPTIONS:
            -s/--size   Specify a size for an operation in MiB, i.e. 1024*1024B
                        (default 1024MiB)
            -f/--fs     Supported File systems: ext3/ext4 (ext[2/3]: default ext3)

        EXAMPLES:

            $ sudo singularity create /tmp/Debian.img
            $ sudo singularity create -s 4096 /tmp/Debian.img
        '''        
        supported_fs = ["ext3","ext4","ext2"]
        if filesystem not in supported_fs:
            print("%s is not supported, options are %s" %(filesystem,",".join(supported_fs)))

        cmd = ['singularity','create','--size',str(size),'--fs',filesystem,image_path]
        self.run_command(cmd,sudo=True)


    def execute(self,image_path,command,writable=False,contain=False):
        '''execute: send a command to a container
        :param image_path: full path to singularity image
        :param command: command to send to container
        :param writable: This option makes the file system accessible as read/write
        :param contain: This option disables the automatic sharing of writable
                        filesystems on your host
        :param verbose: add --verbose option (default is false)
 
        ::notes
 
           USAGE: singularity [...] exec [exec options...] <container path> <command>
 
           This command will allow you to execute any program within the given
           container image.

           EXEC OPTIONS:
              -w/--writable   By default all Singularity containers are available as
                              read only. This option makes the file system accessible
                              as read/write.
              -C/--contain    This option disables the automatic sharing of writable
                              filesystems on your host (e.g. $HOME and /tmp).

 
          NOTE:
              If there is a daemon process running inside the container, then 
              subsequent container commands will all run within the same namespaces.
              This means that the --writable and --contain options will not be
              honored as the namespaces have already been configured by the
              'singularity start' command.

          EXAMPLES:
      
              $ singularity exec /tmp/Debian.img cat /etc/debian_version
              $ singularity exec /tmp/Debian.img python ./hello_world.py
              $ cat hello_world.py | singularity exec /tmp/Debian.img python
              $ sudo singularity exec --writable /tmp/Debian.img apt-get update

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

        USAGE: singularity [...] export [export options...] <container path>

        Export will dump a tar stream of the container image contents to standard
        out (stdout). 

        note: This command must be executed as root.

        EXPORT OPTIONS:
            -f/--file       Output to a file instead of a pipe
               --command    Replace the tar command (DEFAULT: 'tar cf - .')

        EXAMPLES:

            $ sudo singularity export /tmp/Debian.img > /tmp/Debian.tar
            $ sudo singularity export /tmp/Debian.img | gzip -9 > /tmp/Debian.tar.gz
            $ sudo singularity export -f Debian.tar /tmp/Debian.img
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


    def docker2singularity(self,docker_image,output_dir=None):
        '''docker2singularity will convert a docker image to singularity
        :param docker_image: the name of the docker image, doesn't have to be on local machine (eg, ubuntu:latest) 
        '''
        if check_install('docker') == True:

            sudo = True
            cmd = ['docker','run','-d',docker_image,'tail','-f','/dev/null']
            runningid = self.run_command(cmd,sudo=sudo)
            # sha256:d59bdb51bb5c4fb7b2c8d90ae445e0720c169c553bcf553f67cb9dd208a4ec15
        
            # Take the first 12 characters to get id of container
            container_id=runningid[0:12]

            # Network address, if needed
            cmd = ['docker','inspect','--format="{{.NetworkSettings.IPAddress}}"',container_id]
            network_addr = self.run_command(cmd,sudo=sudo)

            # Get image name
            cmd = ['docker','inspect','--format="{{.Config.Image}}"',container_id]
            image_name = self.run_command(cmd,sudo=sudo)

            # Get creation date
            cmd = ['docker','inspect','--format="{{.Created}}"',docker_image]
            creation_date = self.run_command(cmd,sudo=sudo)[0:10]
 
            # Estimate image size
            cmd = ['docker','inspect','--format="{{.Size}}"',docker_image] 
            size = int(self.run_command(cmd,sudo=sudo))
            # convert size in MB (it seems too small for singularity containers ...?). Add 1MB and round up (minimum).
            size=int(round(size/1000000.0)+1.0)
            # adding half of the container size seems to work (do not know why exactly...?)
            # I think it would be Ok by adding 1/3 of the size.
            size=size+size/2

            # Create the image
            new_container_name = "%s-%s.img" %(image_name,creation_date)
            json_file = "singularity.json"
            runscript = "singularity"
            if output_dir != None:
                new_container_name = "%s/%s" %(output_dir,new_container_name)
                json_file = "%s/%s" %(output_dir,json_file)
                runscript = "%s/%s" %(output_dir,runscript)
            self.create(image_path=new_container_name,size=size)

            # export running docker container 
            cmd = ['docker','export',container_id,'|','sudo','singularity','import',new_container_name,'--debug']
            self.run_command(cmd,sudo=sudo,suppress=True)

            # Add stuff about the container to it
            cmd = ['docker','inspect', container_id]
            json_data = json.loads(self.run_command(cmd,sudo=sudo))
            write_json(json_data,json_file)           

            #TODO: we might be able to extract boutique / make package here

            # Add singularity.json to container
            cmd = ['singularity','copy',new_container_name,json_file,'/']
            self.run_command(cmd,sudo=sudo)

            # Merge the /etc/group file, and add to container
            self.run_command(['docker','cp',"%s:/etc/group" %(container_id),'grouphost'],sudo=sudo)
            self.run_command(['sort','/etc/group','grouphost','|','uniq','-u','>','group'],sudo=sudo)
            self.run_command(['singularity','copy',new_container_name,'group','/etc/group'],sudo=sudo)
            os.remove(json_file)
            os.remove('grouphost')
            os.remove('group')

            # Runscript!
            cmd = ['docker','inspect',"--format='{{json .Config.Cmd}}'",docker_image]
            command = self.run_command(cmd,sudo=sudo)
            command = command.replace('["',"").replace('"]',"")
            if command != "none":
                write_file(runscript,command)
                cmd = ['chmod','+x',runscript]
                self.run_command(cmd,sudo=sudo)
                cmd = ['singularity','copy',new_container_name,runscript,'/']
                self.run_command(cmd,sudo=sudo)
                os.remove(runscript)
            print("Stopping container... please wait!")
            cmd = ['docker','stop',container_id]
            self.run_command(cmd,sudo=sudo)
            return new_container_name
        else:
            return None


    def importcmd(self,image_path,input_file,import_type="tar",command=None):
        '''import will import (stdin) to the image
        :param image_path: path to image to import to. 
        :param input_file: tar file only current supported
        :param import_type: only supported is "tar." For docker use S.docker2singularity, the
          command line util is not used, but instead an internal script by this author (@vsoch)
          that has better functionality.
        :param command: replace "tar" command

        USAGE: singularity [...] import [import options...] <container path>

        By default import opens standard input (stdin) and will accept tar
        streams to import into a container. Note that the stream MUST be in
        uncompressed tar format or the command will fail.

        The tar archive can be anything from a root file system, to a layer you
        wish to add to a container, to an existing docker image.

        The size of the container you need to create to import a complete system
        may be significantly larger than the size of the tar file/stream due to
        overheads of the container filesystem.

        It is also possible to import from a Docker image specified with -f by
        using the format option; that actually creates the container.  Docker
        conversion hides substantial complexity and is relatively slow.  It
        creates /singularity in the container if the Docker image defines a
        Cmd and/or Entrypoint.

        note: This command must be executed as root.

        IMPORT OPTIONS:
            -f/--file       Use an input file instead of a pipe for tar, or
                            name an image of the specified format to import
            -t/--type       Source type ('tar' or 'docker', default: tar)
               --command    Replace the tar command (DEFAULT: 'tar xvf -')

        EXAMPLES:

            Once you have created the base image template:

            $ sudo singularity create /tmp/Debian.img

            You can then import from a tar pipe

            $ gunzip -c debian.tar.gz | sudo singularity import /tmp/Debian
            $ cat debian.tar | sudo singularity import /tmp/Debian.img
            $ sudo singularity import /tmp/Debian.img < debian.tar
            $ sudo singularity import -f Debian.tar /tmp/Debian.img
            $ docker export [container] | sudo singularity import [container].img

            Converting a Docker Fedora image:

            $ sudo singularity import -t docker fedora /tmp/fedora.img
        '''
        sudo = True
        if import_type == "docker":
            print('Please use S.docker2singularity("repo:name")')
        elif import_type == "tar":
            cmd = ['singularity','import','--file',input_file]
            if command != None:
                cmd = cmd + ["--command",command]
            cmd.append(image_path)
            return self.run_command(cmd,sudo=sudo)
        return None


    def run(self,image_path,command,writable=False,contain=False):
        '''run will run a command inside the container, probably not intended for within python
        :param image_path: full path to singularity image
        :param command: command to send to container
            
        ::notes

        USAGE: singularity [...] run [run options...] <container path> [...]

        This command will launch a Singularity container and execute a runscript
        if one is defined for that container. The runscript is a file at
        '/singularity'. If this file is present (and executable) then this
        command will execute that file within the container automatically. All
        arguments following the container name will be passed directly to the
        runscript.


        RUN OPTIONS:
            -w/--writable   By default all Singularity containers are available as
                            read only. This option makes the file system accessible
                            as read/write.
            -C/--contain    This option disables the automatic sharing of writable
                            filesystems on your host (e.g. $HOME and /tmp).

        NOTE:
            If there is a daemon process running inside the container, then
            subsequent container commands will all run within the same namespaces.
            This means that the --writable and --contain options will not be
            honored as the namespaces have already been configured by the
            'singularity start' command.

        EXAMPLES:

            $ singularity exec /tmp/Debian.img cat /singularity
            #!/bin/sh
            echo "Hello world: $@"
            $ singularity run /tmp/Debian.img one two three
            Hello world: one two three

        For additional help, please visit our public documentation pages which are
        found at:
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
        
        USAGE: singularity [...] start [start options...] <container path>

        This command will start a namespace daemon process inside the container so
        all subsequent Singularity commands will automatically join this existing
        namespace. The daemon process is specific for user and container file.

        START OPTIONS:
            -w/--writable   By default all Singularity containers are available as
                            read only. This option makes the file system accessible
                            as read/write.
            -C/--contain    This option disables the automatic sharing of writable
                            filesystems on your host (e.g. $HOME and /tmp).

        '''
        sudo = False
        cmd = ['singularity','start']
        cmd = self.add_flags(cmd,writable=writable,contain=contain)
        if writable == True:
            sudo = True

        cmd.append(image_path)
        return self.run_command(cmd,sudo=sudo)


    def stop(self,image_path):
        '''stp[ will stop a container
        
        USAGE: singularity [...] stop <container path>
        Stop a given container namespace daemon process.
        EXAMPLES:

            $ singularity stop /tmp/Debian.img
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
