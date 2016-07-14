#!/usr/bin/env python

# This shows how to use the Singularity (python wrapper) client

from singularity.cli import Singularity

# The default will ask for your sudo password, and then not ask again to
# run commands. It is not stored anywhere, however you should not save / pickle
# the object as it will expose your password. 
S = Singularity()

# Get general help:
S.help()

# These are the defaults, which can be specified
S = Singularity(sudo=True,verbose=False)

# Let's define a path to an image
# wget http://www.vbmis.com/bmi/project/singularity/package_image/ubuntu:latest-2016-04-06.img
image_path = 'ubuntu:latest-2016-04-06.img'

# Run singularity --exec
S.execute(image_path=image_path,command='ls')
# $'docker2singularity.sh\nget_docker_container_id.sh\nget_docker_meta.py\nmakeBases.py\nsingularity\nubuntu:latest-2016-04-06.img\n'
# These are the defaults, which can be specified

# For any function you can get the docs:
S.help(command="exec")

# or return as string
help = S.help(command="exec",stdout=False)

# export an image, default export_type="tar" , pipe=False , output_file = None will produce file in tmp
tmptar = S.export(image_path=image_path)

# create an empty image
S.create(image_path='test.img')

# import a docker image - no need to specify the file, the image name works
# still under development
docker_image = S.docker2singularity("ubuntu:latest")
