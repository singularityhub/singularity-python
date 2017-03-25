# Compare Singularity Hub containers

# This is a simple script to use the singularity command line tool to obtain manifests
# and compare build specs (using Singularity Hub API) 

from singularity.hub.client import Client

from glob import glob
import os
import pandas
import pickle
import shutil

shub = Client()    # Singularity Hub Client

container_names = ['vsoch/singularity-hello-world',
                   'researchapps/quantum_state_diffusion',
                   'vsoch/pe-predictive']

# Let's keep images in a temporary folder
base = "/home/vanessa/Documents/Work/singularity/hub"
storage = "%s/containers" %base
if not os.path.exists(storage):
    os.mkdir(storage)
os.chdir(storage)

# We will keep a table of information
columns = ['name','build_time_seconds','size','commit','estimated_os']
df = pandas.DataFrame(columns=columns)
results = dict()

def get_top_os(x):
    return sorted(x.items(), key=lambda x: (x[1],x[0]), reverse=True)[0][0]

#############################################################################
# Task 1: Download the containers and metadata! (different images)
#############################################################################

# Retrieve the container based on the name
for container_name in container_names:
    result = dict()
    collection = shub.get_collection(container_name)
    containers = dict()
    result['collection'] = collection
    container_ids = collection['container_set']
    cids = []
    for c in range(0,len(container_ids)):
        container_id = container_ids[c]
        cids.append(container_id)
        manifest = shub.get_container(container_id)
        container_uri = '%s-%s' %(container_name,manifest['version'])
        containers[container_uri] = manifest
        image = shub.pull_container(manifest,
                                   download_folder=storage,
                                   name="%s.img.gz" %(manifest['version']))       
        metrics = shub.load_metrics(manifest)
        top_os = get_top_os(metrics['os_sims'])       
        entry = [container_name,
                 metrics['build_time_seconds'],
                 metrics['size'],
                 manifest['version'],
                top_os]
        df.loc[container_uri] = entry
    
    result['containers'] = containers    
    results[container_name] = result
    
results['df'] = df
result_file = '%s/results.pkl' %(base)
pickle.dump(results,open(result_file),'wb'))
