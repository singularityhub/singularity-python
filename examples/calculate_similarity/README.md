# Calculate similarity of two packages

We can calculate a simple similarity metric, the files or folders that a Singularity image (within a package is currently supported), have in common over the total between the two images:

      score = 2.0*len(`intersect`) / (len(`pkg1`)+len(`pkg2`))

Where the intersect is exactly that, the list of (files, folders, or both) that the images have in common, and we are dividing by the total between the two sets. Thus, if two images are exactly the same, they will have a similarity of 1.0. If they have nothing in common, we will have zero over some denominator, and the similarity is 0.0. It's a simple, intuitive metric, and that's why I chose it.

First, you should import the function and make sure you have Singularity installed. If you haven't packaged your image (currently required for this function, since we need the `folders.txt` and `files.txt` in the package), see [this tutorial](../package_image). I also [made a crapton](https://drive.google.com/folderview?id=0BztoBeg6_L7OYjZlRmVmWmVvamM&usp=sharing) that you can download from the [Docker official-images library](https://github.com/docker-library/official-images/tree/master/library) and [I did it like this](https://github.com/vsoch/singularity-tools/blob/master/docker/makeBases.py) if you want to play with those instead.


      from singularity.package import calculate_similarity
      from singularity.utils import check_install
      import pickle
      import sys
      import os

      pkg1 = 'jetty-2016-07-11.img.zip'
      pkg2 = 'mariadb-2016-06-10.img.zip'

      print("Calculating similarity for %s vs. %s..." %(pkg1,pkg2))

      # Calculate similarities
      folder_similarity = calculate_similarity(pkg1,pkg2) # default uses just folders
      files_similarity = calculate_similarity(pkg1,pkg2,include_folders=False,include_files=True)
      both_similarity = calculate_similarity(pkg1,pkg2,include_files=True)

I haven't looked at the scores in detail yet (still doing a lot of development) but it looks like the folders (alone) metric tends to produce higher scores (as we might expect) and there is nice structure in the data. For example, here is an early plot of scores for the folders metric across 109 of these base images:

<iframe width="900" height="800" frameborder="0" scrolling="no" src="https://plot.ly/~vsoch/5.embed"></iframe>

I haven't yet added this calculation as any kind of command line tool (using `shub`), mainly because I'm developing visualizations to go with this, and I also want to be able to get better details about the exact differences between two images (on the level of files). This, however, is a simple metric and a good start to understanding this space of images!
