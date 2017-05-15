# Compare Singularity Hub containers

# This is a simple script to use the singularity command line tool to obtain manifests
# and compare build specs (using Singularity Hub API) 

from singularity.hub.client import Client

shub = Client()    # Singularity Hub Client


#############################################
# Task 1: Download a container
#############################################


container_name = 'vsoch/singularity-hello-world'
collection = shub.get_collection(container_name)
container_ids = collection['container_set']

# Here is one we are interested in
container_id = container_ids.pop()

# The container manifest has all information about container
manifest = shub.get_container(container_id)

# Default will download to present working directory, 
# but we can also set download_folder to something:
image = shub.pull_container(manifest)

# You can also set the download_folder or name, eg:
image = shub.pull_container(manifest,
                            download_folder='/tmp',
                            name='container.img.gz')
