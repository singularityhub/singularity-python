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
oses = "%s/os" %base
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
from singularity.analysis.reproduce import (
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


#############################################################################
# Task 3: Compare replication level of reproducibility to file metric
#############################################################################


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
#http://www.vanessasaur.us/singularity-python/examples/singularity_hub/index.html
write_file('%s/index.html' %base,template)

# Make a heatmap
import plotly.plotly as py
import plotly.graph_objs as go
from scipy.cluster.hierarchy import linkage, dendrogram

Z = linkage(diffs, 'ward')

d=dendrogram(Z,
             leaf_rotation=90.,  # rotates the x axis labels
             leaf_font_size=font_size,  # font size for the x axis l
             labels=labels)

index = d['leaves']
D = numpy.array(diffs)
D=D[index,:]
D=D[:,index]
labels = ["-".join(x.replace('.img','').split('-')[:-1]) for x in diffs.index.tolist()]
labs = [labels[x] for x in index]
data = [
    go.Heatmap(
        z=D,
        x=labs,
        y=labs
    )
]
py.iplot(data,filename='replicate_hub_diffs2')

# Generate equivalent file path comparison
from singularity.analysis.compare import compare_singularity_images 
from singularity.analysis.metrics import RSA

diffs_files = compare_singularity_images(image_paths1=image_files)
diffs_files.to_csv('%s/analysis_compare_singularity_images.tsv' %base,sep='\t')

# How do the matrices compare?
pearsonr_sim = RSA(diffs,diffs_files)
# 0.74136458648818637



#############################################################################
# Task 4: Analyses to assess levels of reproducibility
#############################################################################

from singularity.utils import write_json, write_file
from singularity.analysis.reproduce import (
    assess_differences,
    get_levels
)

levels = get_levels()
level_names = list(levels.keys())

# Singularity Hub (replicate): meaning same base os, different build host
# These should be equal for base, environment, runscript, replicate, but
# not identical.
os.chdir(replication)
print("SINGULARITY HUB REPLICATES")
image_files = glob('*.img')
chosen_one = image_files[10]
diffs = pandas.DataFrame(columns=level_names,index=image_files)
for i in range(len(image_files)):
    image_file = image_files[i]
    print("Processing %s of %s" %(i,len(image_files)))
    diff = assess_differences(image_file,chosen_one,levels=levels)
    diffs.loc[image_file,list(diff['scores'].keys())] = list(diff['scores'].values())


diffs.to_csv('%s/analysis_hub_replicates.tsv' %base,sep='\t')


# Singularity Hub (replicate) for replicate level
os.chdir(replication)
print("SINGULARITY HUB REPLICATES -- REPLICATE")
image_files = glob('*.img')
replicate_level = {'REPLICATE':levels['REPLICATE']}
diffs = pandas.DataFrame(columns=image_files,index=image_files)
done = []
for i in range(len(image_files)):
    image_file1 = image_files[i]
    print("Processing %s of %s" %(i,len(image_files)))
    for image_file2 in image_files:    
        identifier = [image_file1,image_file2]
        identifier.sort()
        identifier = "-".join(identifier)
        if identifier not in done:
            diff = assess_differences(image_file1,image_file2,levels=replicate_level)
            diffs.loc[image_file1,image_file2] = diff['scores']['REPLICATE']
            diffs.loc[image_file2,image_file1] = diff['scores']['REPLICATE']
            done.append(identifier)

diffs.to_csv('%s/analysis_hub_replicates_REPLICATE.tsv' %base,sep='\t')


# Identical image (downloaded multiple times from shub)

os.chdir(clones)
print("SINGULARITY HUB CLONE")
image_files = glob("*.img")
chosen_one = image_files[10]
diffs = pandas.DataFrame(columns=level_names,index=image_files)
for i in range(len(image_files)):
    image_file = image_files[i]
    print("Processing %s of %s" %(i,len(image_files)))
    diff = assess_differences(image_file,chosen_one,levels=levels)
    diffs.loc[image_file,list(diff['scores'].keys())] = list(diff['scores'].values())


diffs.to_csv('%s/analysis_hub_clones.tsv' %base,sep='\t')


# LOCAL REPLICATES
# These were built from the same spec file, same host, but different times
# Again, we will see differences on most levels.

os.chdir(replicates)
image_files = glob("*.img")
print("LOCAL REPLICATES")
image_files = glob("*.img")
chosen_one = image_files[10]
diffs = pandas.DataFrame(columns=level_names,index=image_files)
for i in range(len(image_files)):
    image_file = image_files[i]
    print("Processing %s of %s" %(i,len(image_files)))
    diff = assess_differences(image_file,chosen_one,levels=levels)
    diffs.loc[image_file,list(diff['scores'].keys())] = list(diff['scores'].values())


diffs.to_csv('%s/analysis_local_replicates.tsv' %base,sep='\t')


#############################################################################
# Task 5: Assess dimension of reproducibility 
#############################################################################

# ALGORITHM
# 1. define a phantom operating system as the intersection of files between the
# base set of all operating systems  (ubuntu, debian, centos, busybox)
# 2. For each, calculate the "base" as the entire OS minus this actual
# 3. Generate an image for the base, calculate it's similarity to
# itself minus one file
# 4. show that the score goes from 0 (the phantom) to the OS (1)

from singularity.analysis.reproduce import (
    get_memory_tar,
    extract_guts
)

# First extract file objects
os.chdir(oses)
os_bases = [x for x in glob("%s/*" %oses) if os.path.isdir(x)]
bases = dict()
for os_base in os_bases:
    os_name = os.path.basename(os_base)
    if os_name not in bases:
        image_path = "%s/%s.img" %(os_base,os_name)
        file_obj,tar = get_memory_tar(image_path)
        bases[os_name] = {'fileobj':file_obj,'tar':tar,'image_path':image_path}
    
results = dict()

# Now get shared files
shared = [x.name for x in bases['ubuntu']['tar']]
for os_name,infos in bases.items():
    members = [x.name for x in bases[os_name]['tar']]
    shared = [x for x in shared if x in members]

# For each operating system, remove one file randomly, calculate 

# For each operating system, remove one file randomly, calculate 
# similarity for each level
skip_file_bases = dict()
for level_name, level_filter in levels.items():
    if "skip_files" in level_filter:
        skip_file_bases[level_name] = level_filter['skip_files']
    else:
        skip_file_bases[level_name] = set()

results['shared'] = shared

for os_name,infos in bases.items():
    levels = get_levels()
    members = [x for x in bases[os_name]['tar']]
    # We will sort based on modified date - like an ancestry!
    mtimes = lambda member: member.mtime
    sorted_members = list(sorted(members, key=mtimes))
    scores = pandas.DataFrame(columns=list(levels.keys()))
    denoms = pandas.DataFrame(columns=list(levels.keys()))
    # Calculate guts for all levels, all members
    guts = dict()
    removed = set()
    for level_name,level_filter in levels.items():
        guts[level_name] = extract_guts(bases[os_name]['image_path'],bases[os_name]["tar"],level_filter)
    while len(sorted_members) > 0:
        label = "%s_REDUCED" %len(sorted_members)
        print("Comparing base vs. %s files" %(len(sorted_members)))
        for level_name,level_filter in levels.items():
            clone = levels[level_name].copy()
            custom_level = {label: clone}
            guts1 = guts[level_name]
            custom_level[label]['skip_files'] = skip_file_bases[level_name].union(removed)
            diff = assess_differences(infos['image_path'],infos['image_path'],levels=custom_level,guts1=guts1)
            scores.loc[label,level_name] = diff['scores'][label]
            denoms.loc[label,level_name] = diff[label]['union']
        removed_member = sorted_members.pop()
        removed_member = removed_member.name.replace('.','',1)
        removed = removed.union([removed_member])
        print(scores.loc[label].tolist())
    # Do for final (this is unelegant, it's ok)
    label = "%s_REDUCED" %len(sorted_members)
    #print("Comparing base vs. %s files" %(len(sorted_members)))
    for level_name,level_filter in levels.items():
        clone = levels[level_name]
        custom_level = {label: clone}
        guts1 = guts[level_name]
        custom_level[label]['skip_files'] = skip_file_bases[level_name].union(removed)
        diff = assess_differences(infos['image_path'],infos['image_path'],levels=custom_level,guts1=guts1)
        scores.loc[label,level_name] = diff['scores'][label]
        denoms.loc[label,level_name] = diff[label]['union']


    results[os_name] = {'scores':scores,'removed':removed,'denoms':denoms}
    pickle.dump(results,open('%s/analysis_os.pkl' %oses,'wb'))

# Close all file handles
for os_name,infos in bases.items():
    infos['file_obj'].close()


phantom_results = dict()

del levels['ENVIRONMENT']
del levels['RUNSCRIPT']
del levels['LABELS']

# Now we want to calculate the dimension of each os from the phantom base to full
for os_name,infos in bases.items():
    print("Starting %s" %(os_name))
    members = [x for x in bases[os_name]['tar'] if x not in shared]
    scores = pandas.DataFrame(columns=list(levels.keys()))
    denoms = pandas.DataFrame(columns=list(levels.keys()))
    # Calculate guts for all levels, all members
    guts = dict()
    removed = []
    for level_name,level_filter in levels.items():
        guts[level_name] = extract_guts(bases[os_name]['image_path'],bases[os_name]["tar"],level_filter)
    while len(members) > 0:
        label = "%s_REDUCED" %len(members)
        print("Comparing base vs. %s files" %(len(members)))
        for level_name,level_filter in levels.items():
            custom_level = {label: levels[level_name]}
            guts1 = guts[level_name]
            custom_level[label]['skip_files'] = skip_file_bases[level_name] + removed + results['shared']
            diff = assess_differences(infos['image_path'],infos['image_path'],levels=custom_level,guts1=guts1)
            scores.loc[label,level_name] = diff['scores'][label]
            denoms.loc[label,level_name] = diff[label]['union']
        removed_member = members.pop()
        removed.append(removed_member.replace('.','',1))
    phantom_results[os_name] = {'scores':scores,'removed':removed}
    pickle.dump(phantom_results,open('%s/analysis_phantom_os.pkl' %oses,'wb'))


# Plotting of results
results = pickle.load(open('%s/analysis_os.pkl' %oses,'rb'))
#plotdf = pandas.read_csv("%s/analysis_os_flat.tsv" %oses,sep="\t",index_col=0)
import seaborn as sns

# Flatten the data
idx = 0
plotdf = pandas.DataFrame(columns=['os','score','level','files','idx'])
for os_name,result in results.items():
    if os_name in ["centos"]:
        scores = result['scores']
        denoms = result['denoms']
        for row in scores.iterrows():
            files_present = denoms.loc[row[0]].copy()
            for level_name in list(row[1].keys()):
                files_value = files_present[level_name]
                files_index = int(row[0].split('_')[0])
                plotdf.loc[idx] = [os_name,row[1][level_name],level_name,files_value,files_index]
                idx+=1


plotdf.to_csv("%s/analysis_os_flat.tsv" %oses,sep="\t")
#plotdf = pandas.read_csv("%s/analysis_os_flat.tsv" %oses,sep="\t",index_col=0)

debian = plotdf[plotdf.os=='debian']
debian = debian[debian.level.isin(['BASE', 'IDENTICAL', 'LABELS', 'REPLICATE','RUNSCRIPT'])]
# Plot the response with standard error
sns.tsplot(data=debian, time="idx", unit="os",
                 condition="level", value="score")

sns.plt.show()


busybox = plotdf[plotdf.os=='busybox']
busybox = busybox[busybox.level.isin(['BASE', 'IDENTICAL', 'LABELS', 'REPLICATE','RUNSCRIPT'])]
# Plot the response with standard error
sns.tsplot(data=busybox, time="idx", unit="os",
           condition="level", value="score")

sns.plt.show()


centos = plotdf[plotdf.os=='centos']
centos = centos[centos.level.isin(['BASE', 'IDENTICAL', 'LABELS', 'REPLICATE','RUNSCRIPT'])]
# Plot the response with standard error
sns.tsplot(data=centos, time="idx", unit="os",
           condition="level", value="score")

sns.plt.show()


ubuntu = plotdf[plotdf.os=='ubuntu']
ubuntu = ubuntu[ubuntu.level.isin(['BASE', 'IDENTICAL', 'LABELS', 'REPLICATE','RUNSCRIPT'])]
# Plot the response with standard error
sns.tsplot(data=ubuntu, time="idx", unit="os",
           condition="level", value="score")

sns.plt.show()


alpine = plotdf[plotdf.os=='alpine']
alpine = alpine[alpine.level.isin(['BASE', 'IDENTICAL', 'LABELS', 'REPLICATE','RUNSCRIPT'])]
# Plot the response with standard error
sns.tsplot(data=alpine, time="idx", unit="os",
           condition="level", value="score")

sns.plt.show()



alpine = plotdf[plotdf.os=='alpine']
alpine = alpine[alpine.level.isin(['BASE', 'IDENTICAL', 'LABELS', 'REPLICATE','RUNSCRIPT'])]

import matplotlib.pyplot as plt
fig, axs = plt.subplots(ncols=5,sharey=True)

for l in range(len(alpine.level.unique().tolist())):
    level = alpine.level.unique().tolist()[l]
    subset = alpine[alpine.level==level]
    sns.tsplot(data=subset, time="idx", unit="os",
               condition="level", value="score",ax=axs[l])


g = sns.FacetGrid(alpine, col="level", ylim=(0, 1))
for level in alpine.level.unique().tolist():
    subset = alpine[alpine.level==level]
    g.map(sns.tsplot, data=subset, time="idx", unit="os", condition="level", value="score")

sns.plt.show()


#############################################################################
# Task 3: Assess levels of reproducibility
#############################################################################

# The first thing we want to do is evaluate our metrics for reproducibility.
dfs = dict()
levels = get_levels()

from singularity.analysis.reproduce import (
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
