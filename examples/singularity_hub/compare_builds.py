# Compare Singularity Hub containers

# This is a simple script to use the singularity command line tool to download containers
# (using Singularity, Section 1) and compare build specs (using Singularity Hub API, Section 2) and to
# compare the containers themselves using singularity python (Section 3)

container_names = ['vsoch/singularity-hello-world',
                   'researchapps/quantum_state_diffusion',
                   'vsoch/pefinder']

from singularity.hub.client import Client
from singularity.package import get_image_hash

import tempfile
import os
import demjson
import pandas
import shutil

shub = Client()    # Singularity Hub Client
results = dict()

# Let's keep images in a temporary folder
storage = tempfile.mkdtemp()
os.chdir(storage)

# We will keep a table of information
columns = ['name','build_time_seconds','hash','size','commit','estimated_os']
df = pandas.DataFrame(columns=columns)

for container_name in container_names:
    
    # Retrieve the container based on the name
    collection = shub.get_collection(container_name)
    container_ids = collection['container_set']
    containers = []
    for container_id in container_ids:
       manifest = shub.get_container(container_id)
       containers.append(manifest)
       image = shub.pull_container(manifest,
                                   download_folder=storage,
                                   name="%s.img.gz" %(manifest['version']))       
       # Get hash of file
       hashes.append(get_image_hash(image))
       df.loc['%s-%s' %(container_name,manifest['version'])]

    results[container_name] = {'collection':collection,
                               'containers':containers}

shutil.rmtree(storage)
