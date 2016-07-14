# docker2singularity

You have several options for converting docker images to singularity. Using this script, you can run:

       docker2singularity.sh ubuntu:14.04

You can also use the singularity (bash) command line tool, which requires you to specify the --file location of your Docker image. This method is not ideal because most people don't know where these images are on their computer!


       sudo singularity create /tmp/fedora.img
       sudo singularity import -t docker fedora /tmp/fedora.img


You can finally use this command line tool to create an image in the same manner as the above script (still under development).

      from singularity.cli import Singularity
      S = Singularity()
      docker_image = S.docker2singularity("ubuntu:latest")
