# Compare Singularity Hub containers

# This is a simple script to use the singularity command line tool to obtain manifests
# and compare build specs (using Singularity Hub API) 

from singularity.hub.client import Client

import pickle
import os
import pandas
import shutil

shub = Client()    # Singularity Hub Client

container_name = 'vsoch/singularity-hello-world'

# Let's keep images in a temporary folder
base = "/home/vanessa/Documents/Work/singularity/hub"
storage = "%s/containers" %base
if not os.path.exists(storage):
    os.mkdir(storage)
os.chdir(storage)

# We will keep a table of information
columns = ['name','build_time_seconds','size','commit','estimated_os']
df = pandas.DataFrame(columns=columns)
containers = dict()
results = dict()

def get_top_os(x):
    return sorted(x.items(), key=lambda x: (x[1],x[0]), reverse=True)[0][0]

#############################################################################
# Task 1: Download the containers and metadata! (different images)
#############################################################################

# Retrieve the container based on the name
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
pickle.dump(results,open('%s/results.pkl' %storage,'wb'))


#############################################################################
# Task 2: Develop levels of reproducibility
#############################################################################

from singularity.reproduce import (
    get_content_hashes,
    get_levels
)

levels = get_levels()
results = pickle.load(open('%s/results.pkl' %storage,'rb'))

os.chdir(storage)
image_files = glob("*.img")

# Question 1: What files are consistent across the same image?
# LEVEL IDENTICAL
# Here we will download the same image 10 times, create a sha1 sum of the files,
# and determine which sets of files should be consistent for the same image file


# Question 2: What files are consistent across the same image, different downloads?
# LEVEL REPLICATE
# Here we will use the 100 files in the folder, and find files/folders consistent across
# we will not include the runscript, since we know this was changed.
identical_across = get_content_hashes(image_files[0],level='IDENTICAL')
image_files.pop(0)
not_identical = []

for image_file in image_files:
    hashes = get_content_hashes(image_file,level='IDENTICAL')
    for hash_path,hash_val in hashes.items():
        if hash_path in identical_across:
            if not identical_across[hash_path] == hashes[hash_path]:
                del identical_across[hash_path]
                not_identical.append(hash_path)


start = time.time()
hashy=get_image_hash(image_file)
end = time.time()

# Question 3: What files are consistent between the same operating systems?
# LEVEL BASE
# A base similarity means the base of the images (the OS) are likely the same


# Outputs:
# A function that exports, reads tarfile into memory (or disk?) and generates a list of
# key (file) and value (sha1 sum)
 0) I'll first experiment with different patterns of files/folders and figure out which are consistent across images. I'll probably do this by doing a content hash of all individual files, and then finding the set that is consistent across 1) the same exact image, and 2) different images but same builds, and 3) different images different builds. We could even give each some kind of score to determine the right set it belongs in.
 1) at the highest level of reproduciblity (eg same file) we get equivalent hashes - to do this I'll just download exactly the same image
 2) at a "working" (aka, reasonable to use) level of reproducibility, we should get equivalent hashes given the same build, but different files (eg, I built my thing twice from the same spec)
 3) at the lowest level of reproducibility (eg, base operating system) we should see some identicalness if the operating systems base are largely the same.
 
We can then allow the user to use our functions, and go a bit deeper into image comparison and asses, given equal file paths, which are actually equal in content across two images. The user could even save a definition of "how they are assessing reproducibility" of the image by way of a list of regular expressions, and a hash for their image generated from it. I think it would be interesting, given this algorithm, to parse all singularity hub public images and assess the total level of redundancy!

Anyhoo, I think I'm going to go to sleep now, I keep doing this not sleeping thing, lol.


from glob import glob
image_files=glob('*.img')    
sums = []
for image_file in image_files:
   os.system('sudo singularity export %s > tmp.tar' %(image_file))
   summy = tarsum('tmp.tar')
   print(summy)
   sums.append(summy)

