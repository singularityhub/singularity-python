#!/bin/sh

# See help
shub create --help

'''
Usage: shub create [-h] [--recipe] [--app APP] [--from BOOTSTRAP_FROM]
                   [--bootstrap BOOTSTRAP] [--outfolder OUTFOLDER]

optional arguments:
  -h, --help            show this help message and exit
  --recipe              create template recipe
  --app APP             the name of an app to include in the recipe
  --from BOOTSTRAP_FROM
                        the bootstrap "from", should coincide with "bootstrap"
                        type
  --bootstrap BOOTSTRAP
                        the bootstrap type, default is docker
  --outfolder OUTFOLDER
                        full path to folder for output, stays in tmp (or pwd)
                        if not specified

'''

# Generate a relatively blank template, default bootstrap is docker
shub create
'''
DEBUG bootstrap: docker
Output file written to /home/vanessa/Documents/Dropbox/Code/singularity/singularity-python/examples/create/make_runscript/Singularity
'''

# Create a recipe template for an app
shub create --app foo
'''
DEBUG bootstrap: docker
Output file written to /home/vanessa/Documents/Dropbox/Code/singularity/singularity-python/examples/create/make_runscript/Singularity.foo
'''

# Specify a from, bootstrap
shub create --app foo --from ubuntu --bootstrap docker
