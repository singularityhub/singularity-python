# Compare Singularity Hub containers

# This is a simple script to use the singularity command line tool to download containers
# (using Singularity, Section 1) and compare build specs (using Singularity Hub API, Section 2) and to
# compare the containers themselves using singularity python (Section 3)

container_names = ['vsoch/singularity-hello-world',
                   'researchapps/quantum_state_diffusion',
                   'vsoch/pefinder']

from singularity.hub.client import Client

client = Client()
results = dict()

for container_name in container_names:
    
    # Retrieve the container based on the name
    collection = client.get_collection(container_name)
    container_ids = collection['container_set']
    containers = []
    for container_id in container_ids:
       container = client.get_container(container_id)
       containers.append(container)
