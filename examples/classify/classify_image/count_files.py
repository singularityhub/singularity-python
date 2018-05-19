#!/usr/bin/env python

# This is an example of counting files using an image diff

from singularity.analysis.classify import (
    file_counts,
    extension_counts
)

container = "ubuntu.simg"

# Now we might be interested in counting different things
readme_count = file_counts(container)
copyright_count = file_counts(container, patterns=['copyright'])
authors_count = file_counts(container, patterns=['authors','thanks','credit'])
todo_count = file_counts(container, patterns=['todo'])

# Or getting a complete dict of extensions
extensions = extension_counts(container)

# Return files instead of counts
extensions = extension_counts(container, return_counts=False)
