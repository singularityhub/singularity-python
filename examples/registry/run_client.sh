#!/bin/bash

# Interact with Singularity Registry, bash

# This is a simple script to use the singularity command line tool to 
# obtain a manifest and download an image. You will need to install first

singularity pull shub://vsoch/hello-world

which sregistry


###################################################################
# Push
###################################################################

sregistry push vsoch-hello-world-master.img --name dinosaur/avocado --tag delicious
sregistry push vsoch-hello-world-master.img --name meowmeow/avocado --tag nomnomnom
sregistry push vsoch-hello-world-master.img --name dinosaur/avocado --tag whatinthe


###################################################################
# List
###################################################################

# All collections
sregistry list

# A particular collection
sregistry list dinosaur

# A particular container name across collections
sregistry list /avocado

# A named container, no tag
sregistry list dinosaur/avocado

# A named container, with tag
sregistry list dinosaur/avocado:delicious

# Show me environment
sregistry list dinosaur/tacos:delicious --env

# Add runscript
sregistry list dinosaur/tacos:delicious --e --r

# Definition recipe (Singularity) and test
sregistry list dinosaur/tacos:delicious --d --t

# All of them
sregistry list dinosaur/tacos:delicious --e --r --d --t

###################################################################
# Delete
###################################################################

sregistry delete dinosaur/tacos:delicious
sregistry list

###################################################################
# Pull
###################################################################

sregistry pull dinosaur/avocado:delicious


###################################################################
# Labels
###################################################################

# All labels
sregistry labels

# A specific key
sregistry labels --key maintainer

# A specific value
sregistry labels --value vanessasaur

# A specific key and value
sregistry labels --key maintainer --value vanessasaur
