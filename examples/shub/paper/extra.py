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
