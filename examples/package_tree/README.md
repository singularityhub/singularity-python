# How similar are my operating systems?
A question that has spun out of one of my projects that I suspect would be useful in many applications but hasn't been fully explored is comparison of operating systems. If you think about it, for the last few decades we've generated many methods for comparing differences between files. We have md5 sums to make sure our downloads didn't poop out, and command line tools to quickly look for differences. We now have to take this up a level, because our new level of operation isn't on a single "file", it's on an entire operating system. It's not just your Mom's computer, it's a container-based thing (e.g., Docker or Singularity that contains a base OS plus additional libraries and packages and then the special sauce, the application or analysis that the container was birthed into existence to carry out. It's not good enough to have message storage places to dump these containers, we need simple and consistent methods to computationally compare them, organize them, and let us explore them.

We have provided this simple method in Singularity Python, which can produce plots like the following

## Cluster Docker (Library) Images based on Base OS
![docker-os.library](docker-os.png)

## Cluster Base OS Versions
![docker-os.png](docker-os.png)

The derivation of the scores can be seen in [calculate_similarity.py](calculate_similarity.py), and the simple plot in [plot_similarity.py](plot_similarity.py).


# Similarity of File Paths
When I think about it, an entire understanding of an "image" (or more generally, a computer or operating system) comes down to the programs installed, and files included. Yes, there might be various environmental variables, but I would hypothesize that the environmental variables found in an image have a rather strong correlation with the software installed, and we would do pretty well to understand the guts of an image from the body without the electricity flowing through it. This would need to be tested, but not quite yet.

Thus, since we are working in linux land, our problem is simplified to comparing file and folder paths. We have lists of both of those things exported by [singularity-python](http://www.github.com/singularityware/singularity-python). 


### Comparison of two images
I would argue that this is the first level of comparison, meaning the rougher, higher level comparison that asks "how similar are these two things, broadly?" In this framework, I want to think about the image paths like features, and so a similarity calculation can come down to comparing two sets of things, and I've made a function (see analysis/compare.py) to do this. It comes down to a ratio between the things they have in common (intersect) over the entire set of things:

      score = 2.0*len(`intersect`) / (len(`pkg1`)+len(`pkg2`))

I wasn't sure if "the entire set of things" should include just folder paths, just files paths, or both, and so I decided to try all three approaches. It also would need to be determined if we can further streamline this approach by filtering down the paths first. For example, take a look at the paths below:

      ./usr/include/moar/6model',
      ./usr/include/moar/6model/reprs'

We are probably most interested in the fact that `6model` is present in the image, and the files in the subdirectory are being more used as weights, giving higher similarity to two images that might have the same larger software bases installed (with more folders). It's not clear to me if we should account for this.
