#!/usr/bin/env python

# This shows how to use the Singularity (python wrapper) client

from singularity.cli import Singularity

# Create a client
S = Singularity()

# Get general help:
S.help()

# These are the defaults, which can be specified
S = Singularity(sudo=False,debug=False)

# Note that the "create" and "import" workflow is deprecated in favor of build
# https://singularityware.github.io/docs-build

image = S.build('myimage.simg', 'docker://ubuntu:latest') # requires sudo

# (Deprecated) create an image and import into it
image = S.create('myimage.simg')
S.importcmd(image,'docker://ubuntu:latest')

# Execute command to container
result = S.execute(image,command='cat /singularity')
print(result)
'''
'#!/bin/sh\n\nexec "/bin/bash"\n'
'''

# For any function you can get the docs:
S.help(command="exec")

# export an image to tar
tar = S.export(image)

# Show apps and inspect
S.apps(image)
S.inspect(image)

'''
{
    "data": {
        "attributes": {
            "deffile": null,
            "help": null,
            "labels": null,
            "environment": "# Custom environment shell code should follow\n\n",
            "runscript": "#!/bin/sh\n\nexec \"/bin/bash\"\n",
            "test": null
        },
        "type": "container"
    }
}
'''
