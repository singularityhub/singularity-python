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

container_name = 'vsoch/singularity-hello-world'

# Let's keep images in a temporary folder
base = "/home/vanessa/Documents/Work/singularity/hub"
storage = "%s/containers" %base
clones = "%s/clones" %storage # same image downloaded multiple times
replicates = "%s/replicates" %storage # these are quasi replicates
                                      # had to change runscripts to commit
replication = "%s/quasi_replicates" %storage # these are exact replicates, from same
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

os.chdir(replication)
with open('Singularity','w') as filey:
    filey.writelines(runscript)

from singularity.cli import Singularity
cli = Singularity()

for num in range(0,100):
    container_name = 'ubuntu-hello-world-%s.img' %(num)
    cli.create(container_name)
    cli.bootstrap(container_name,'Singularity')
    
    container_uri = '%s-%s' %(container_name,manifest['version'])
   containers[container_uri] = manifest


# ALL SINGULARITY HUB
containers = shub.get_containers()
os.chdir(hub)
for container_name,container in containers.items():
    for branch, manifest in container.items():        
       name = manifest['name'].replace('/','-')
       image = shub.pull_container(manifest,
                                   download_folder=hub,
                                   name="%s-%s.img.gz" %(name,branch))       

pickle.dump(containers,open('%s/container_manifests.pkl' %(hub),'wb'))


#############################################################################
# Task 2: Develop levels of reproducibility
#############################################################################

from singularity.reproduce import (
    assess_differences,
    get_content_hashes,
    get_image_hash,
    get_levels
)

levels = get_levels()
result_file = '%s/results-%s.pkl' %(base,container_name.replace('/','-'))
results = pickle.load(open(result_file,'rb'))


# Let's assess what files are identical across pairs of images in different sets

# Quasi Replicate: meaning same base os, different build host, slightly different runscript
os.chdir(replication)
image_files = glob('*.img')
diffs = assess_differences(image_files[0],image_files[1],levels=levels)
pickle.dump(diffs,open('%s/diff_quasi_replicate_pair.pkl' %base,'wb'))

# Replicate: if we produce an equivalent image at a different time, we might have
#            variance in package directories (anything involving variable with mirrors, etc)

os.chdir(replicates)
image_files = glob('*.img')
diffs = assess_differences(image_files[0],image_files[1],levels=levels)
pickle.dump(diffs,open('%s/diff_replicate_pair.pkl' %base,'wb'))

# Identical: all files are the same

os.chdir(clones)
image_files = glob('*.img')
diffs = assess_differences(image_files[0],image_files[1],levels=levels)
pickle.dump(diffs,open('%s/diff_clone_pair.pkl' %base,'wb'))

# Different images, same OS

#############################################################################
# Task 3: Assess levels of reproducibility
#############################################################################

# The first thing we want to do is evaluate our metrics for reproducibility.
dfs = dict()

# ASSESS IDENTICAL IMAGES ACROSS ALL LEVELS

os.chdir(clones)
image_files = glob("*.img")
levels = get_levels(version=2.2)

hashes = pandas.DataFrame(columns=list(levels.keys()))

for image_file in image_files:
    print('Processing %s' %(image_file))
    hashy = get_image_hashes(image_file,levels=levels)
    hashes.loc[image_file,:] = hashy


dfs['IDENTICAL'] = hashes
for col in hashes.columns.tolist():
    print("%s: %s" %(col,hashes[col].unique().tolist()))

# IDENTICAL: ['364715054c17c29338787bd231e58d90caff154b']
# RUNSCRIPT: ['da39a3ee5e6b4b0d3255bfef95601890afd80709']
# ENVIRONMENT: ['22ff3c5c5fa63d3f08a48669d90fcb1459e6e74b']
# RECIPE: ['0e0efcb05fb4727f77b999d135c8a58a8ce468d5']


# Question 2: What files are consistent across the same image, different builds?
# An image that is a replicate should be assessed as identical using the "REPLICATE"
# criteria, but not identical

# RECIPES

os.chdir(replication)
image_files = glob('*.img')
hashes = pandas.DataFrame(columns=list(levels.keys()))

for image_file in image_files:
    print('Processing %s' %(image_file))
    hashy = get_image_hashes(image_file,levels=levels)
    hashes.loc[image_file,:] = hashy


dfs['RECIPES'] = hashes
for col in hashes.columns.tolist():
    print("%s: %s" %(col,len(hashes[col].unique().tolist())))



# QUASI REPLICATES
# These have the same base, but different metadata folders.

os.chdir(replicates)
image_files = glob("*.img")
levels = get_levels(version=2.2)

hashes = pandas.DataFrame(columns=list(levels.keys()))

for image_file in image_files:
    print('Processing %s' %(image_file))
    hashy = get_image_hashes(image_file,levels=levels)
    hashes.loc[image_file,:] = hashy

dfs['QUASI_REPLICATE'] = hashes
for col in hashes.columns.tolist():
    print("%s: %s" %(col,len(hashes[col].unique().tolist())))



pickle.dump(dfs,open('reproducibility_dfs.pkl','wb'))


# Let's assess what files are identical across the images. We can use this to develop
# our subsequent levels.
# Here we will use the 100 files in the folder, and find files/folders consistent across
# we will not include the runscript, since we know this was changed.



def generate_replication_df(level_name,image_files,version,skip_files=None):

    print("CALCULATING COMPARISONS FOR LEVEL %s" %level_name)
    df = pandas.DataFrame(0,index=image_files,columns=image_files)
    for image_file1 in image_files:
        for image_file2 in image_files:
            hash1 = get_image_hash(image_file1,level=level_name,version=version)
            hash2 = get_image_hash(image_file2,level=level_name,version=version)
            if hash1 == hash2:
                df.loc[image_file1,image_file2] = 1
                df.loc[image_file2,image_file1] = 1
    return df


dfs['IDENTICAL'] = generate_replication_df('IDENTICAL',image_files,version=2.2)
dfs['REPLICATE'] = generate_replication_df('REPLICATE',image_files,version=2.2, skip_files=['/singularity'])


# Outputs:
# A function that exports, reads tarfile into memory (or disk?) and generates a list of
# key (file) and value (sha1 sum)
 0) I'll first experiment with different patterns of files/folders and figure out which are consistent across images. I'll probably do this by doing a content hash of all individual files, and then finding the set that is consistent across 1) the same exact image, and 2) different images but same builds, and 3) different images different builds. We could even give each some kind of score to determine the right set it belongs in.
 1) at the highest level of reproduciblity (eg same file) we get equivalent hashes - to do this I'll just download exactly the same image
 2) at a "working" (aka, reasonable to use) level of reproducibility, we should get equivalent hashes given the same build, but different files (eg, I built my thing twice from the same spec)
 3) at the lowest level of reproducibility (eg, base operating system) we should see some identicalness if the operating systems base are largely the same.
 
We can then allow the user to use our functions, and go a bit deeper into image comparison and asses, given equal file paths, which are actually equal in content across two images. The user could even save a definition of "how they are assessing reproducibility" of the image by way of a list of regular expressions, and a hash for their image generated from it. I think it would be interesting, given this algorithm, to parse all singularity hub public images and assess the total level of redundancy!



from glob import glob
image_files=glob('*.img')    
sums = []
for image_file in image_files:
   os.system('sudo singularity export %s > tmp.tar' %(image_file))
   summy = tarsum('tmp.tar')
   print(summy)
   sums.append(summy)

