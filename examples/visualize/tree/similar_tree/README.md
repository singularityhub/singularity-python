# Container Similar Tree

The functions in analysis allow us to generate a similarity tree:

![simtree.png](simtree.png)

An [interactive demo](https://singularityware.github.io/singularity-python/examples/similar_tree/) is also available.

### Questions

**Why do I see some of the same folders as I saw for [../difference_tree](../difference_tree)**

In order to parse lower levels of the tree, we have to include parents. So, for example, the folder `home` would obviously be shared by two images, however if there are subfolders that exist for one image but not the other, we must render `home` in the difference tree. Thus, you might see `home` appear in both visualizations that show the intersect and difference.

