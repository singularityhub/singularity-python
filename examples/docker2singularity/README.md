# docker2singularity

These are no longer the recommended way/standard to get a Docker image into Singularity, but are provided for
reference if they might be useful to you. These methods rely upon having the Docker daemon installed, and the command line tool uses the native registry (meaning you don't need Docker). For the recommended way, see [http://singularity.lbl.gov/docs-docker](http://singularity.lbl.gov/docs-docker).


## docker2singularity.py
This python script has functions that could be used toward this goal. You could do:

      cd examples/docker2singularity
      from docker2singularity import *
      docker_image = 'ubuntu:latest'
      image = docker2singularity(docker_image,output_folder=None)


This example will export the image `ubuntu:latest-2016-04-06.img` into your current working directory. If you want to export to a different folder, set the output_folder to something else.


## docker2singularity bash
Using the script in this folder, you can run:

       docker2singularity.sh ubuntu:14.04
