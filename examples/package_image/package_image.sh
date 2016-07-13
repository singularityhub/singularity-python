#!/bin/sh

# use the `--package` argument to package your image:
shub --image ubuntu:latest-2016-04-06.img --package

# If no output folder is specified, the resulting image (named in the format `ubuntu:latest-2016-04-06.img.zip` will be output in the present working directory. You can also specify an output folder:

shub --image ubuntu:latest-2016-04-06.img --package --outfolder /home/vanessa/Desktop

# For the package command, you will need to put in your password to grant sudo priviledges, as packaging requires using the singularity `export` functionality.

