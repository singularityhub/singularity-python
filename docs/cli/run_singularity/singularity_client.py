#!/usr/bin/env python

# This shows how to use the Singularity (python wrapper) client

from singularity.cli import Singularity

# Create a client
S = Singularity()

# Get general help:
S.help()

# These are the defaults, which can be specified
S = Singularity(sudo=False,sudopw=None,debug=False)

# Create an image
image = S.create('myimage.img')

# Import into it
S.importcmd(image,'docker://ubuntu:latest')

# Execute command to container
result = S.execute(image,command='cat /singularity')
print(result)
'''
#!/bin/sh

if test -x /bin/bash; then
    exec /bin/bash "$@"
elif test -x /bin/sh; then
    exec /bin/sh "$@"
else
    echo "ERROR: No valid shell within container"
    exit 255
fi
'''

# For any function you can get the docs:
S.help(command="exec")

# export an image as a byte array
byte_array = S.export(image,pipe=True)

# Get an in memory tar
from singularity.reproduce import get_memory_tar
tar = get_memory_tar(image)
