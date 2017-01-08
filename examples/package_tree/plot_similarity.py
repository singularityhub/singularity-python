# A quick example of making a package tree with data derived from calculate_similarity.py

from singularity.views.trees import make_package_tree

data = pickle.load(open('comparisons.pkl','rb'))['files.txt']
plt = make_package_tree(matrix=data)
plt.show()

# or save to file
plt.savefig('examples/package_tree/docker-library.png')
