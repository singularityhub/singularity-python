# Compare Singularity Hub containers

# This is a simple script to use the singularity command line tool to obtain manifests
# and compare build specs (using Singularity Hub API) 

from singularity.hub.client import Client

from glob import glob
import os
import json
import pandas
import pickle
import shutil

shub = Client()    # Singularity Hub Client

container_name = 'vsoch/singularity-hello-world'

# Let's keep images in a temporary folder
base = "/home/vanessa/Documents/Work/singularity/hub"
storage = "%s/containers" %base
clones = "%s/clones" %storage # same image downloaded multiple times
replicates = "%s/replicates" %storage # these are replicates from singularity hub
                                      # had to change runscripts to commit
replication = "%s/quasi_replicates" %storage # these are replicates produced on same host
hub = "%s/collections" %storage 

# Create all folders for images
paths = [storage,replicates,clones,replication,hub]
for pathy in paths:
    if not os.path.exists(pathy):
        os.mkdir(pathy)

# We will keep a table of information
columns = ['name','build_time_seconds','size','commit','estimated_os']
df = pandas.DataFrame(columns=columns)
containers = dict()
results = dict()

def get_top_os(x):
    return sorted(x.items(), key=lambda x: (x[1],x[0]), reverse=True)[0][0]

#############################################################################
# Task 1: Get Containers 
#############################################################################

# SINGULARITY HUB HAS QUASI REPLICATES, complete metadata

# Retrieve the container based on the name
os.chdir(replicates)
collection = shub.get_collection(container_name)
results['repo_name'] = container_name
results['collection'] = collection
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
    
results['containers'] = containers    
results['df'] = df
result_file = '%s/results-%s.pkl' %(base,container_name.replace('/','-'))
pickle.dump(results,open(result_file),'wb'))


# IDENTICAL

os.chdir(clones)
chosen_one = results['df'].index[10]
manifest = results['containers'][chosen_one]
for num in range(0,100):
    clone_name = "%s-%s" %(manifest['name'].replace('/','-'),num)
    image = shub.pull_container(manifest,
                                download_folder=clones,
                                name="%s.img.gz" %(clone_name))


# EXACT REPLICATES

runscript = '''Bootstrap:docker
From: ubuntu:latest

%runscript
exec "Hello World!"
'''

os.chdir(replicates)
with open('Singularity','w') as filey:
    filey.writelines(runscript)

from singularity.cli import Singularity
cli = Singularity()

for num in range(0,100):
    container_name = 'ubuntu-hello-world-%s.img' %(num)
    cli.create(container_name)
    cli.bootstrap(container_name,'Singularity')
    


# ALL SINGULARITY HUB
containers = shub.get_containers()
os.chdir(hub)
for container_name,container in containers.items():
    for branch, manifest in container.items():        
       name = manifest['name'].replace('/','-')
       uncompressed = "%s-%s.img" %(name,branch)
       if not os.path.exists(uncompressed):
           try:
               image = shub.pull_container(manifest,
                                           download_folder=hub,
                                           name="%s-%s.img.gz" %(name,branch))       
           except:
               print("error downloading %s" %name)

pickle.dump(containers,open('%s/container_manifests.pkl' %(hub),'wb'))


#############################################################################
# Task 2: Develop levels of reproducibility
#############################################################################

from singularity.utils import write_json, write_file
from singularity.reproduce import (
    assess_differences,
    get_levels
)

levels = get_levels()


# Let's assess what files are identical across pairs of images in different sets

# Singularity Hub (replicate): meaning same base os, different build host
# These should be equal for base, environment, runscript, replicate, but
# not identical.
os.chdir(replication)
image_files = glob('*.img')
diffs = assess_differences(image_files[0],image_files[1],levels=levels)
print("SINGULARITY HUB REPLICATES")
print(diffs)
write_json(diffs,'%s/diff_hub_replicates_pair.json' %base)

# Local Replicate: if we produce an equivalent image at a different time, we might have
# variance in package directories (anything involving variable with mirrors, etc)
# these images should also be assessed as equivalent on the level of runscript,
# environment, base, replicate, labels, but not identical. They should be MORE
# identical than the Singularity Hub replicate by way of being produced on the same host.

os.chdir(replicates)
image_files = glob('*.img')
diffs = assess_differences(image_files[0],image_files[1],levels=levels)
print("LOCAL REPLICATES")
print(diffs)
write_json(diffs,'%s/diff_local_replicates_pair.json' %base)

# Identical: all files are the same

os.chdir(clones)
image_files = glob('*.img')
diffs = assess_differences(image_files[0],image_files[1],levels=levels)
print("CLONES")
print(diffs)
write_json(diffs,'%s/diff_clone_pair.json' %base)


# Singularity Hub
# This is the real world use case, because these are real images on Singularity Hub
# Let's compare each image on the level of REPLICATE
os.chdir(hub)
image_files = glob('*.img')

# len(image_files) 
# 79

total = len(image_files)*len(image_files)
counter = 1
diffs = pandas.DataFrame(0,columns=image_files,index=image_files)
diff_files = dict()
replicate_level = {'REPLICATE':levels['REPLICATE']}

for image_file1 in image_files:
    for image_file2 in image_files:
        print("%s of %s" %(counter,total))
        diff_id = [image_file1,image_file2]
        diff_id.sort()
        diff_id = '-'.join(diff_id)
        if diff_id not in diff_files:
            report = assess_differences(image_file1,image_file2,levels=replicate_level)
            diffs.loc[image_file1,image_file2] = report['scores']['REPLICATE']
            diffs.loc[image_file2,image_file1] = report['scores']['REPLICATE']
            print(diff_id)
            print(report['scores'])
            diff_files[diff_id] = report
        counter+=1

pickle.dump(diffs,open('%s/replicate_hubdiffs_dfs.pkl' %base,'wb'))
diffs = pickle.load(open('%s/replicate_hubdiffs_dfs.pkl' %base,'rb'))

# VISUALIZATION, interactive and static

from singularity.views.trees import (
    make_package_tree, 
    make_interactive_tree
)

from singularity.views.utils import get_template

# Static
labels = ['-'.join(x.split('-')[1:-1]) for x in diffs.index.tolist()]
fig = make_package_tree(matrix=diffs,labels=labels,title="Singularity Hub Replication Scores")
fig.savefig('%s/replicate_hubdiffs_dfs.png' %base)

# Interactive tree
tree = make_interactive_tree(matrix=diffs,labels=labels)
fields = {"{{ graph | safe }}",json.dumps(tree)}
template = get_template("comparison_tree",fields)
write_file('%s/index.html' %base,template)

#############################################################################
# Task 3: Assess levels of reproducibility
#############################################################################

# The first thing we want to do is evaluate our metrics for reproducibility.
dfs = dict()
levels = get_levels()

from singularity.reproduce import (
    get_content_hashes,
    get_image_hashes,
    get_image_hash
)


# ASSESS IDENTICAL IMAGES ACROSS ALL LEVELS

os.chdir(clones)
image_files = glob("*.img")
hashes = pandas.DataFrame(columns=list(levels.keys()))

for image_file in image_files:
    print('Processing %s' %(image_file))
    hashy = get_image_hashes(image_file,levels=levels)
    hashes.loc[image_file,:] = hashy


# HERE
dfs['IDENTICAL'] = hashes
for col in hashes.columns.tolist():
    print("%s: %s" %(col,hashes[col].unique().tolist()))


# REPLICATE: ['2776174919187e7007619ac74f082b90']
# ENVIRONMENT: ['2060c7583adf2545494bf76113f5d594']
# BASE: ['345d1d687fd0bed73528969d82dd5aa4']
# RUNSCRIPT: ['272844f479bfd9f83e7caf27e40146ea']
# IDENTICAL: ['8a2f03e6d846a1979b694b28c125a852']
# LABELS: ['d41d8cd98f00b204e9800998ecf8427e']
# RECIPE: ['89b5f94c70b261b463c914a4fbe628c5']


# SINGULARITY HUB "REPLICATES"

# These images, if compared pairwise, would be assessed as equivalent on all
# levels except for identical. This example will show differences on level
# of replicate and base, and this shows that these levels should not
# be calculated in advance.
os.chdir(replication)
image_files = glob('*.img')
hashes = pandas.DataFrame(columns=list(levels.keys()))

for image_file in image_files:
    print('Processing %s' %(image_file))
    hashy = get_image_hashes(image_file,levels=levels)
    hashes.loc[image_file,:] = hashy

# REPLICATE: 101
# ENVIRONMENT: 1
# BASE: 101
# RUNSCRIPT: 2
# IDENTICAL: 101
# LABELS: 1
# RECIPE: 85

# The above confirms our prediction - the levels (hashes alone) should not be used
# to assess an image beyond environment, labels, and runscript. Since these images were
# produced by trivially changing the runscript, we also see that reflected in this result.

dfs['QUASI_REPLICATE'] = hashes
for col in hashes.columns.tolist():
    print("%s: %s" %(col,len(hashes[col].unique().tolist())))



# REPLICATES
# These were built from the same spec file, same host, but different times
# Again, we will see differences on most levels.

os.chdir(replicates)
image_files = glob("*.img")
hashes = pandas.DataFrame(columns=list(levels.keys()))

for image_file in image_files:
    print('Processing %s' %(image_file))
    hashy = get_image_hashes(image_file,levels=levels)
    hashes.loc[image_file,:] = hashy

# REPLICATE: 100
# ENVIRONMENT: 100
# BASE: 100
# RUNSCRIPT: 1
# IDENTICAL: 100
# LABELS: 1
# RECIPE: 100


dfs['REPLICATES'] = hashes
for col in hashes.columns.tolist():
    print("%s: %s" %(col,len(hashes[col].unique().tolist())))



# Singularity Hub
# Are there any files that are identical across all images?
# Can we assess the level of reproducibility of each path?

os.chdir(hub)
image_files = glob("*.img")
hashes = pandas.DataFrame(columns=list(levels.keys()))

for image_file in image_files:
    print('Processing %s' %(image_file))
    hashy = get_image_hashes(image_file,levels=levels)
    hashes.loc[image_file,:] = hashy

dfs['HUB_COLLECTIONS'] = hashes
for col in hashes.columns.tolist():
    print("%s: %s" %(col,len(hashes[col].unique().tolist())))


pickle.dump(dfs,open('%s/reproducibility_dfs.pkl' %base,'wb'))
