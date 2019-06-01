#!/usr/bin/env python

# This is an example of counting files using an image diff

from singularity.analysis.classify import (
    file_counts,
    extension_counts
)

# singularity pull docker://busybox
container = "busybox_latest.sif"

# Now we might be interested in counting different things
bin_count = file_counts(container, patterns=['bin'])

# Or getting a complete dict of extensions
extensions = extension_counts(container)

# Return files instead of counts
extensions = extension_counts(container, return_counts=False)
