# Package a Node

This is a test for functions that will package a node, meaning sitting on it, and then having it packaged and built into a singularity image (on a host with Singularity). This is only relevant for `vsoch/singularity-python` development branch.

## Install Development Singularity Python
```
git clone -b development https://www.github.com/vsoch/singularity-python
cd singularity-python
python3 setup.py sdist
python3 setup.py install
```

## Package Node
Then in python3 (this is what the builder on Singularity Hub uses, so I am using that image to test)

```
from singularity.package import package_node

package=package_node()

package
'/tmp/tmp06ww_8_n/vanessa-testing-self-cloning.tgz'
```

## Unpack Node into Container
Then this file can be turned into a Singularity image:


```
from singularity.package import unpack_node
image = unpack_node(image_path=package,size=9000)

```

We see unpack, image creation, and a break at the end when it's importing:

```
DEBUG Preparing to unpack vanessa-testing-self-cloning.tgz to vanessa-testing-self-cloning.img.
Initializing Singularity image subsystem
Opening image file: vanessa-testing-self-cloning.img
Creating 2000MiB image
Binding image to loop
Creating file system within image
Image is done: /vanessa-testing-self-cloning.img
```

The image is named the same as the original `.tgz` but with an `img` extension if `name` is not specified, and in the same folder as the host if `output_folder` is not specified.

```
image
$ '/home/vanessa/Desktop/vanessa-testing-self-cloning.img'

```

## Testing Image
Then on the host, there isn't a run driver so we can't run:

```
./vanessa-testing-self-cloning.img 
ERROR  : No run driver found inside container
ABORT  : Retval = 255
```

But we can shell!

```
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

Proposal: we would want to have security checks, and then generation of the needed commands (possibly via bootstrap functions) that would be needed to drive the image.
