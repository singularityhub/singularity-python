## View the inside of a container
What's inside that container? Right now, the main way to answer this question is to do some equivalent of ssh. shub provides a command line function for rendering a view to (immediately) show the contents of an image (folders and files) in your web browser. **Important** the browser will open, but you will need to use your password to use Singularity on the command line:


### Docker Image
shub will render the guts of any Docker image, even if it's not currently on your system. You don't need 

```
shub --image docker://ubuntu:latest --tree
```

### Singularity Package or Image

```
shub --image ubuntu.img --tree
```

This will open up something that looks like this:

![img/files.png](img/files.png)
An [interactive demo](https://singularityware.github.io/singularity-python/examples/container_tree) is also available, and see the [example](examples/container_tree) for updates.


### Visualize Containers

#### Container Similarity Clustering
Do you have sets of containers or packages, and want to cluster them based on similarities?

![examples/package_tree/docker-os.png](examples/package_tree/docker-os.png)

We have examples for both deriving scores and producing plots like the above, see [examples/package_tree](examples/package_tree)


#### Container Similarity Tree

![examples/similar_tree/simtree.png](examples/similar_tree/simtree.png)

What do two containers have in common, in terms of files and folders? shub provides a command line function for rendering a view to (immediately) show the similarity between to container images:


      shub --images centos.img,ubuntu.img --simtree --debug

      
We can also compare a local image to a Docker image:


      shub --images docker://ubuntu:latest,/home/vanessa/Desktop/ubuntu.img --simtree --debug


Or two Docker images:


      shub --images docker://ubuntu:latest,docker://centos:latest --simtree


If you need output for any of the following, you can add the `--debug` argument. Note that when generating docker comparisons, the back end is obtaining the layers, creating the images, importing and packaging, so the result is not instantanous.


An [interactive demo](https://singularityware.github.io/singularity-python/examples/similar_tree/) is also available.


#### Container Difference Tree
What files and folders differ between two containers? What does it look like if I subtract one image from the second? `shub` provides a command line tool to generate a visualization to do exactly this.


      shub --subtract --images docker://ubuntu:latest,docker://centos:latest

As with `simtree`, this function supports both docker and singularity images as inputs.

![examples/difference_tree/difftree.png](examples/difference_tree/difftree.png)

An [interactive demo](https://singularityware.github.io/singularity-python/examples/difference_tree/) is also available.


### Compare Containers
The same functions above can be used to show the exact similarities (intersect) and differences (files and/or folders unique to two images) between two images. You can get a data structure with this information as follows:


      from singularity.analysis.compare import compare_containers
  
      image1 = 'ubuntu.img'
      image2 = 'centos.img'
      by = "files.txt" # can also be "folders.txt", or a list with both

      comparison = compare_containers(image1,image2,by=by)


Note that you can also compare packages, or a container to a package:


      def compare_containers(container1=None,container2=None,by=None,
                             image_package1=None,image_package2=None)


#### Calculate similarity of images

We can calculate similarity of images based on the file content inside. For an example, see [examples/calculate_similarity](examples/calculate_similarity). We can compare two local images as follows:

      $ shub --images /home/vanessa/Desktop/ubuntu.img,/home/vanessa/Desktop/ubuntu.img --simcalc
      
and the same applies for specification of Docker images, as in the previous example. Note that we are specifying `images` for the argument instead of `image`, and it's a single string of image names separated by a comma. 



### Package your container
The driver of much of the above is the simple container package. A package is a zipped up file that contains the image, the singularity runscript as `runscript`, a `VERSION` file, and a list of files `files.txt` and folders `folders.txt` in the container. 

![img/singularity-package.png](img/singularity-package.png)

The example package can be [downloaded for inspection](http://www.vbmis.com/bmi/project/singularity/package_image/ubuntu:latest-2016-04-06.img.zip), as can the [image used to create it](http://www.vbmis.com/bmi/project/singularity/package_image/ubuntu:latest-2016-04-06.img). This is one of the drivers underlying [singularity hub](http://www.singularity-hub.org) (under development).

  - **files.txt** and **folders.txt**: are simple text file lists with paths in the container, and this choice is currently done to provide the rawest form of the container contents. These files also are used to generate interactive visualizations, and calculate similarity between containers.
  - **VERSION**: is a text file with one line, an md5 hash generated for the image when it was packaged. 
  - **{{image}}.img**: is of course the original singularity container (usually a .img file)

First, go to where you have some images:

      ls
      ubuntu.img
      

You can now use the `shub` command line tool to package your image. Note that you must have [singularity installed](https://singularityware.lbl.gov/install-linux), and depending on the function you use, you will likely need to use sudo. We can use the `--package` argument to package our image:

      shub --image ubuntu.img --package


If no output folder is specified, the resulting image (named in the format `ubuntu.img.zip` will be output in the present working directory. You can also specify an output folder:

      shub --image ubuntu.img --package --outfolder /tmp

For the package command, you will need to put in your password to grant sudo priviledges, as packaging requires using the singularity `export` functionality.

For more details, and a walkthrough with sample data, please see [examples/package_image](examples/package_image)



### Build your container
More information coming soon.


### Functions Provided
You can also use the library as a module, and import singularity-python functions into your application. If you would like to see specific examples for something, [please ask](https://github.com/singularityware/singularity-python)!


## Singularity
Most of these functions require
## Installation from Source

You can try the following two options:

### Option 1: Download latest stable release
You can always download the latest tarball release from <a href="{{ site.repo }}/releases" target="_blank">Github</a>

For example, here is how to download version `2.2.1` and install:

```bash
VERSION=2.2.1
wget https://github.com/singularityware/singularity/releases/download/$VERSION/singularity-$VERSION.tar.gz
tar xvf singularity-$VERSION.tar.gz
cd singularity-$VERSION
./configure --prefix=/usr/local
make
sudo make install
```

### Option 2: Download the latest development code
To download the most recent development code, you should use Git and do the following:

```bash
git clone {{ site.repo }}.git
cd singularity
./autogen.sh
./configure --prefix=/usr/local
make
sudo make install
```

note: The 'make install' is required to be run as root to get a properly installed Singularity implementation. If you do not run it as root, you will only be able to launch Singularity as root due to permission limitations.

{% include asciicast.html source='install-singularity.js' title='Install Singularity' author='vsochat@stanford.edu' %}


### Updating

To update your Singularity version, you might want to first delete the executables for the old version:

```bash
sudo rm -rf /usr/local/libexec/singularity
```
And then install using one of the methods above.


## Build an RPM from source
Like the above, you can build an RPM of Singularity so it can be more easily managed, upgraded and removed. From the base Singularity source directory do the following:

```bash
./autogen.sh
./configure
make dist
rpmbuild -ta singularity-*.tar.gz
sudo yum install ~/rpmbuild/RPMS/*/singularity-[0-9]*.rpm
```

Note: if you want to have the RPM install the files to an alternative location, you should define the environment variable 'PREFIX' to suit your needs, and use the following command to build:

```bash
PREFIX=/opt/singularity
rpmbuild -ta --define="_prefix $PREFIX" --define "_sysconfdir $PREFIX/etc" --define "_defaultdocdir $PREFIX/share" singularity-*.tar.gz
```

When using `autogen.sh` If you get an error that you have packages missing, for example on Ubuntu 16.04:

```bash
 ./autogen.sh
+libtoolize -c
./autogen.sh: 13: ./autogen.sh: libtoolize: not found
+aclocal
./autogen.sh: 14: ./autogen.sh: aclocal: not found
+autoheader
./autogen.sh: 15: ./autogen.sh: autoheader: not found
+autoconf
./autogen.sh: 16: ./autogen.sh: autoconf: not found
+automake -ca -Wno-portability
./autogen.sh: 17: ./autogen.sh: automake: not found
```

then you need to install dependencies:


```bash
sudo apt-get install -y build-essential libtool autotools-dev automake autoconf
```

## Build a DEB from source

To build a deb package for Debian/Ubuntu/LinuxMint invoke the following commands:

```bash
$ fakeroot dpkg-buildpackage -b -us -uc # sudo will ask for a password to run the tests
$ sudo dpkg -i ../singularity-container_2.2.1-1_amd64.deb
```
 
Note that the tests will fail if singularity is not already installed on your system. This is the case when you run this procedure for the first time.
In that case run the following sequence:

```bash
$ echo "echo SKIPPING TESTS THEYRE BROKEN" > ./test.sh
$ fakeroot dpkg-buildpackage -nc -b -us -uc # this will continue the previous build without an initial 'make clean'
```



## Support

Have a question, or need further information? <a href="/singularity-python/support">Reach out to us.</a>
