from glob import glob

from singularity.analysis.reproduce import assess_differences

image_files=glob('*.img')

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

