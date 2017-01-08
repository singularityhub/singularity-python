# A quick example of making a package tree with data derived from calculate_similarity.py
# Set environment variable MESSAGELEVEL to CRITICAL to disable debug output

from singularity.views.trees import make_package_tree
from singularity.analysis.compare import compare_packages
from singularity.analysis.utils import get_packages

# Compare your own data
data = pickle.load(open('comparisons.pkl','rb'))['files.txt']
plt = make_package_tree(matrix=data)

# Compare docker-os to docker-os
package_set1 = get_packages(family='docker-os')
package_set2 = get_packages(family='docker-os')
data = compare_packages(packages_set1=package_set1,
                        packages_set2=package_set2)['files.txt']

plt = make_package_tree(matrix=data)


# Show the plot
plt.show()

# or save to file
plt.savefig('examples/package_tree/docker-os.png')
