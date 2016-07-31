# Container Difference Tree

What's the difference, in terms of files and folders, between those two containers? shub provides a command line function for rendering a view to (immediately) show what is left when you subtract one image from another:

      shub --difftree --images cirros-2016-01-04.img.zip,busybox-2016-02-16.img.zip

Note that we are specifying `images` for the argument instead of `image`, and it's a single string of image names separated by a comma. For this argument you can specify an image or package. What you are specifying is --images `base`,`subtracted`, meaning that we will show the `base` with `subtracted` files and folders removed.

![difftree.png](difftree.png)

An [interactive demo](https://singularityware.github.io/singularity-python/examples/difference_tree) is also available.

