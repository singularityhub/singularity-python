from glob import glob

from singularity.analysis.reproduce import assess_differences, get_level

# singularity pull docker://ubuntu:14.04
# singularity pull docker://ubuntu:12.04

image_files = glob('ubuntu*.sif')


# Choose a level that you want to assess based on
level_filter = {"RECIPE": get_level('RECIPE')}

# ASSESS DIFFERENCES #######################################

# Running for all levels, this will take a few minutes
report = assess_differences(image_files[0], image_files[1], levels=level_filter)

# {'RECIPE': {'difference': [],
#  'intersect_different': [],
#  'same': 7,
#  'union': 14},
# 'scores': {'RECIPE': 1.0}}
