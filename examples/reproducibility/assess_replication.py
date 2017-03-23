from glob import glob

image_files=glob('*.img')
from singularity.reproduce import *
Environment message level found to be DEBUG

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
