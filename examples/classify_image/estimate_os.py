#!/usr/bin/env python

# This is an example of generating image packages from within python

from singularity.analysis.classify import estimate_os

package = "python:3.6.0.img.zip"

# We can obtain the estimated os (top match)
estimated_os = estimate_os(package=package)
# Most similar OS found to be %s debian:7.11

# We can also get the whole list and values
os_similarity = estimate_os(package=package,return_top=False)


