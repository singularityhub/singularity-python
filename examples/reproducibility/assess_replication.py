from glob import glob

from singularity.reproduce import (
    assess_replication, 
    assess_differences
)

image_files=glob('*.img')

# ASSESS REPLICATION #######################################
# returns booleans for if the hashes for levels are the same

assess_replication(image_files[0],image_files[1])

{'BASE': False,
 'ENVIRONMENT': False,
 'IDENTICAL': False,
 'LABELS': True,
 'RECIPE': False,
 'REPLICATE': False,
 'RUNSCRIPT': False}

assess_replication(image_files[0],image_files[0])

{'BASE': True,
 'ENVIRONMENT': True,
 'IDENTICAL': True,
 'LABELS': True,
 'RECIPE': True,
 'REPLICATE': True,
 'RUNSCRIPT': True}

# ASSESS DIFFERENCES #######################################
# returns dictionary with 

report = assess_differences(image_files[0],image_files[1])

report.keys()
# dict_keys(['different', 'missing', 'same'])

# These files are equivalent between the images
print(len(report['same']))
5663

# These files are present in both, but different
print(report['different'])
['./etc/hosts', 
 './.exec', 
 './environment', 
 './etc/mtab', 
 './etc/resolv.conf', 
 './.run', 
 './.shell', 
 './singularity']

# These files are found in the first image, but not the second
print(report['missing'])
['./var/lib/apt/lists/.wh.archive.ubuntu.com_ubuntu_dists_xenial-updates_main_i18n_Translation-en', 
 './bin/gunzip']

