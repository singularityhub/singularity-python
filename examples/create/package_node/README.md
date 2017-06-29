# Package a Node

This is a test for functions that will package a node, meaning sitting on it, and then having it packaged and built into a singularity image (on a host with Singularity). This is only relevant for `vsoch/singularity-python` development branch.

```
git clone -b development https://www.github.com/vsoch/singularity-python
cd singularity-python
python3 setup.py sdist
python3 setup.py install
```

Then in python3 (this is what the builder on Singularity Hub uses, so I am using that image to test)

```
from singularity.package import (
    package_node,
    unpack_node
)

package=package_node()

package
'/tmp/tmp06ww_8_n/vanessa-testing-self-cloning.tgz'
```

Then this file can be turned into a Singularity image:

```
# If output folder not specified, will be same as the image
# If name not specified, same as image with .img
image = unpack_node(image_path=package,
                     size=2000)

DEBUG Preparing to unpack vanessa-testing-self-cloning.tgz to vanessa-testing-self-cloning.img.
Initializing Singularity image subsystem
Opening image file: vanessa-testing-self-cloning.img
Creating 2000MiB image
Binding image to loop
Creating file system within image
Image is done: /vanessa-testing-self-cloning.img

image
$ '/home/vanessa/Desktop/vanessa-testing-self-cloning.img'

```

Then on the host, there isn't a run driver so we can't run, but we can shell:

```
./vanessa-testing-self-cloning.img 
ERROR  : No run driver found inside container
ABORT  : Retval = 255

$ sudo singularity shell vanessa-testing-self-cloning.
Singularity: Invoking an interactive shell within container..
#
ls /
# ls /
bin   home	      lib64	  opt	sbin  tmp      vmlinuz.old
boot  initrd.img      lost+found  proc	snap  usr
dev   initrd.img.old  media	  root	srv   var
etc   lib	      mnt	  run	sys   vmlinuz
```


