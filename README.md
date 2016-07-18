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


#### Export Docker to Singularity

This tool currently has command line and (functions) to convert a Docker image to Singularity. Currently, we don't add any sort of runscript from the CMD, as this needs to be better developed. To use on the command line:


     shub --docker ubuntu:latest

 
will export the image `ubuntu:latest-2016-04-06.img` into your current working directory. If you want to export to a different folder:


      shub --docker ubuntu:latest --outfolder /home/vanessa/Desktop


#### Package your container

A package is a zipped up file that contains the image, the singularity runscript as `runscript`, a [boutique schema descriptor](https://github.com/boutiques/schema) with acceptable input arguments, a `VERSION` file, and a list of files `files.txt` and folders `folders.txt` in the container. 

![img/singularity-package.png](img/singularity-package.png)

The example package can be [downloaded for inspection](http://www.vbmis.com/bmi/project/singularity/package_image/ubuntu:latest-2016-04-06.img.zip), as can the [image used to create it](http://www.vbmis.com/bmi/project/singularity/package_image/ubuntu:latest-2016-04-06.img). The reason to create this package is that a higher level application might want to extract meta data about the container without needing to mount it. 

  - **files.txt** and **folders.txt**: are simple text file lists with paths in the container, and this choice is currently done to provide the rawest form of the container contents. 
  - **VERSION**: is a text file with one line, an md5 hash generated for the image when it was packaged. This version is also included with the boutiques schema. This is to ensure that the meta data about an image matches the current image, to the best of our knowledge.
  - **{{image}}.img**: is of course the original singularity container (usually a .img file)
  - **{{image}}.img.json**: is the boutiques schema describing the inputs ([more detail here](examples/package_image))


First, go to where you have some images:

      cd singularity-images
      ls
      ubuntu:latest-2016-04-06.img
      

You can now use the `shub` command line tool to package your image. Note that you must have [singularity installed](https://singularityware.github.io/#install), and depending on the function you use, you will likely need to use sudo. We can use the `--package` argument to package our image:

      shub --image ubuntu:latest-2016-04-06.img --package

If no output folder is specified, the resulting image (named in the format `ubuntu:latest-2016-04-06.img.zip` will be output in the present working directory. You can also specify an output folder:

      shub --image ubuntu:latest-2016-04-06.img --package --outfolder /home/vanessa/Desktop

For the package command, you will need to put in your password to grant sudo priviledges, as packaging requires using the singularity `export` functionality.

For more details, and a walkthrough with sample data, please see [examples/package_image](examples/package_image)

#### Calculate similarity of packages

I am currently developing methods and visualizations to calculate similarity of packages, meaning similarity of Singularity image based on the guts inside. For an example, see [examples/calculate_similarity](examples/calculate_similarity) and for an example of a full pipeline (to run in parallel on a cluster) see [here](https://github.com/vsoch/singularity-tools/tree/master/similarity).


#### Generate a runscript template

A `runscript` is a file that sits in the base of a singularity image (at `/`) and gets executed when the container is called. This script is essentially the portal from your local machine to the bits in the container, and so being able to programatically extract command line arguments and allowable options is essential for an application to be able to (somewhat intelligently) use your containers. Toward this goal, we are providing runscript templates, or simple scripts (in various languages) that use standards that can be easily parsed (also by the shub tool). You can use the command line tool to generate these starter templates as follows:

      # Generate a python run script in the present working directory
      shub --runscript py

      # Generate a python run script somewhere else
      shub --runscript py --outfolder /home/vanessa/Desktop

The only supported language is currently python (specify "py" as in the example above) and we will have more included as the software is developed. If you are a debutante for your favorite language(s) of choice, please contribute to the repo! Contribution means adding a runscript.{{ext}} to the [templates](singularity/templates) folder, and a function to the [runscript.py](singularity/runscript.py) module to parse it into a data structure to be included in the image package. More details coming soon, as the python verison of this (the first) is still under development.


### shub --help

      package Singularity containers for singularity hub.

      optional arguments:
        -h, --help            show this help message and exit
        --image IMAGE         full path to singularity image (for use with
                              --package)
        --docker2singularity DOCKER
                              name of Docker image to export to Singularity (does
                              not include runscript cmd)
        --outfolder OUTFOLDER
                              full path to folder for output, if not specified, will
                              go to pwd
        --runscript RUNSCRIPT
                              specify extension to generate a runscript template in
                              the PWD, or include --outfolder to change output
                              directory. Currently supported types are py (python).
        --package             package a singularity container for singularity hub


        usage: shub [-h] [--image IMAGE] [--docker2singularity DOCKER]
                    [--outfolder OUTFOLDER] [--runscript RUNSCRIPT] [--package]


### Functions Provided
You can also use the library as a module, and import singularity-python functions into your application.  We will provide example scripts and further documentation soon.
