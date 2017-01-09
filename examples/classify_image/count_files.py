#!/usr/bin/env python

# This is an example of counting files using an image diff

from singularity.analysis.classify import (
    get_diff,
    file_counts,
    extension_counts
)

image_package = "python:3.6.0.img.zip"

# The diff is a dict of folders --> files that differ between 
# image and it's closest OS
diff = get_diff(image_package=image_package)

# Now we might be interested in counting different things
readme_count = file_counts(diff=diff)
copyright_count = file_counts(diff=diff,patterns=['copyright'])
authors_count = file_counts(diff=diff,patterns=['authors','thanks','credit'])
todo_count = file_counts(diff=diff,patterns=['todo'])

# Or getting a complete dict of extensions
extensions = extension_counts(diff=diff)

# Return files instead of counts
extensions = extension_counts(diff=diff,return_counts=False)
