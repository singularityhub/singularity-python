#!/usr/bin/python

# We want a metric to calculate similarity between images based on package folders.txt and files.txt
# This is the script used to generate container comparison base metrics for Singularity Hub

# We don't want ample debugging output (remove if you do)
os.environ['MESSAGELEVEL'] = 'CRITICAL'

from singularity.analysis.compare import (
    compare_packages
)

from singularity.analysis.utils import get_packages
from singularity.utils import check_install
from glob import glob
import os
import pandas
import pickle
import sys

base = '/home/vanessa/Documents/Dropbox/Code/singularity/singularity-python'
analysis_directory = "%s/examples/package_tree" %(base)

# Check for Singularity installation
if check_install() != True:
    print("You must have Singularity installed to use this script!")
    sys.exit(32)


###############################################################################
# Get paths to your package(s)
###############################################################################

# Option 1: Get a family manually
package_set1 = get_packages(family='docker-library')

# Option 2: Specify your own package directory (arg is packages=packages)
package_directory = '%s/examples/package_image/packages' %(base)
package_set1 = glob("%s/*.zip" %(package_directory))

# Option 3: provide no input args, and default (os) for package_set1 is used


###############################################################################
# Choose another set of packages to compare to
###############################################################################

# Option 1: specify another (same or different) family of packages
package_set2 = get_packages(family='docker-os')

# Option 2: Same as above
# Option 3: Don't specify any packages, use defaults


###############################################################################
# Run the analysis
###############################################################################


# Use your own input arguments...
comparisons = compare_packages(packages_set1=package_set1,
                               packages_set2=package_set2,
                               by="folders.txt") 

# Or use defaults
comparisons = compare_packages() # docker-library vs. docker-os, 
                                 # by files.txt

# Save to file
pickle.dump(result,open('comparisons.pkl','wb'))
