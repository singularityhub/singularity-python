from glob import glob

from singularity.analysis.reproduce import (
    get_image_hash,
    get_levels,
    get_content_hashes,
    get_image_file_hash    
)

image_files = glob("*.sif")
image_path = image_files[0]

########################################################
# Get Image Hash (Single Container --> Single Value)
########################################################

# This function will return a hash specific to a level of 
# reproducibility, meaning a subset  of files within the 
# image. You can see the levels for selection:

levels = get_levels()

levels.keys()
# dict_keys(['IDENTICAL', 'BASE', 'REPLICATE', 'RECIPE', 'RUNSCRIPT', 'ENVIRONMENT', 'LABELS'])

# or specify a different version:

levels = get_levels(version=2.3)

# We can, then generate an image hash, and by default the level "REPLICATION" will be used:

get_image_hash(image_path)
# '4c252c8fb818e4b854a478a1a0df5991'

# But we can also specify a level that we want:
get_image_hash(image_path,level="IDENTICAL")
#'3f4dcf64b58d314ac9ef0c02f641cd2109a07d64'

########################################################
# Get Image Content Digest (One Container --> Multiple)
########################################################


# We might want to get a dictionary of content hashes for all files
# of one container at one level!
digest = get_content_hashes(image_path)
digest['hashes']['/usr/bin/chfn']
# '4b5ee4db88c3b8bfb0cb7cb3a90a7793'

# We can also get a hash of the entire image file, this is done on the
# binary file and not contents inside.

file_hash = get_image_file_hash(image_path)
# 'd5349c37fdc2e6f2dca8793732e1c420'
