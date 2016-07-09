# Singularity Python

This is a python command line tool for working with [Singularity](singularityware.github.io) containers, specifically providing functions to package containers for import of meta data into [singularity-hub](https://github.com/singularityware/singularity-hub). Testing, and examples are coming soon, and while the package is under development, notes will be provided in this README. Please contribute to the package, or post feedback and questions as [issues](https://github.com/singularityware/singularity-python). For points that require discussion of the larger group, please use the [Singularity List](https://groups.google.com/a/lbl.gov/forum/#!forum/singularity).

The Singularity-Python code is licensed under the MIT open source license, which is a highly permissive license that places few limits upon reuse. This ensures that the code will be usable by the greatest number of researchers, in both academia and industry. 


### Installation (current)

      pip install singularity


### Installation (dev)

      pip install git+git://github.com/singularityware/singularity-python.git


### Quick Start

Installation will place an executable, `shub` in your bin folder. 


#### Test your installation

After installation, you should be able to run `shub` on the command line, without any input args, to see if you have Singularity installed (and test the package):

      $ shub
      Found Singularity version 2.1

      Please specify a singularity image with --image.


#### Package your container

A package is a zipped up file that contains the image, the singularity runscript as runscript, and a list of files `files.txt` and folders `folders.txt` in the container. 

![img/singularity-package.png](img/singularity-package.png)

The reason to create this package is that a higher level application might want to extract meta data about the container without needing to mount it. These are simple text file lists with paths in the container, and this choice is currently done to provide the rawest form of the container contents. First, go to where you have some images:

      cd singularity-images
      ls
      ubuntu:latest-2016-04-06.img
      

You can now use the `shub` command line tool to package your image. Note that you must have [singularity installed](https://singularityware.github.io/#install), and depending on the function you use, you will likely need to use sudo. We can use the `--package` argument to package our image:

      shub --image ubuntu:latest-2016-04-06.img --package

If no output folder is specified, the resulting image (named in the format `ubuntu:latest-2016-04-06.img.zip` will be output in the present working directory. You can also specify an output folder:

      shub --image ubuntu:latest-2016-04-06.img --package --outfolder /home/vanessa/Desktop

For the package command, you will need to put in your password to grant sudo priviledges, as packaging requires using the singularity `export` functionality.


### shub --help

      usage: shub [-h] [--image IMAGE] [--outfolder OUTFOLDER] [--package]

      package Singularity containers for singularity hub.

      optional arguments:
        -h, --help            show this help message and exit
        --image IMAGE         full path to singularity image (for use with
                              --package)
        --outfolder OUTFOLDER
                              full path to folder for output, if not specified, will
                              go to pwd
        --package             package a singularity container for singularity hub



### Functions Provided
You can also use the library as a module, and import singularity-python functions into your application.  We will provide example scripts and further documentation soon.
