# docker2singularity

You have several options for converting docker images to singularity. 

## shub command line
This tool currently has command line and (functions) to convert a Docker image to Singularity. Currently, we don't add any sort of runscript from the CMD, as this needs to be better developed. To use on the command line:


      shub --docker ubuntu:latest

 
will export the image `ubuntu:latest-2016-04-06.img` into your current working directory. If you want to export to a different folder:


      shub --docker ubuntu:latest --outfolder /home/vanessa/Desktop


## docker2singularity bash
Using the script in this folder, you can run:

       docker2singularity.sh ubuntu:14.04


## singularity bash
You can also use the singularity (bash) command line tool, which requires you to specify the --file location of your Docker image. This method is not ideal because most people don't know where these images are on their computer!


       sudo singularity create /tmp/fedora.img
       sudo singularity import -t docker fedora /tmp/fedora.img


## singularity-python
You can finally use this command line tool to create an image in the same manner as the above script.

      from singularity.cli import Singularity
      S = Singularity()
      docker_image = S.docker2singularity("ubuntu:latest")
