
# Run Singularity

These functions are a wrapper for the bash command line tool, Singularity, to make functions programatically accessible from Python. You must have <a href="https://singularityware.github.io/install-linux" target="_blank">Singularity installed</a> to use these commands.

First, we need to import the Class in python

```python
from singularity.cli import Singularity
S = Singularity()
```

These are the defaults, which can be specified

```python
S = Singularity(sudo=False,sudopw=None,debug=False,quiet=False)
```

The default will ask not ask for your sudo password, and will prompt you once at the first called command that needs it (only bootstrap for 2.3 and up). 

- `sudopw`: If you provide the password upon initiation of the client, it won't ask you again. 
- `sudo`: If you require that sudo is True, it will ask the user given that it is not provided. This variable is not stored anywhere on the system other than in the class variable, however you should be careful about pickling or saving the client.
- `debug`: print statements from the logger, for debugging purposes
- `quiet`: silence the regular Singularity console / standard out statements


To get general help, there is a wrapper for the help command. When you run it without any arguments, you see the general `singularity --help`

```python
S.help()
```

You can also run with a command to get details for that command:

```python
S.help(command='run')
```

you can also return the help as string
help = S.help(command="exec",stdout=False)


# Working with Images

## Pull
If you need an image, you can choose any from <a href="https://singularity-hub.org" target="_blank">Singularity Hub</a> and retrieve it will get it from:

```python
image = S.pull('shub://vsoch/singularity-images')

Progress |===================================| 100.0% downloading imagee
Done. Container is at: ./vsoch-singularity-images-mongo.img

image
'./vsoch-singularity-images-mongo.img'

```

## Create

Here is how to create a simple empty image.

```python
image = S.create(image_path='/tmp/test.img')

# or specify a custom size
image = S.create(image_path='/tmp/test.img',size=1000)
```

## Import
`import` has special meaning in Python, so we use `importcmd` instead.

```python
S.importcmd(image_path=image,input_source="docker://ubuntu:latest")

Docker image path: index.docker.io/library/ubuntu:latest
Cache folder set to /home/vanessa/.singularity/docker
Importing: base Singularity environment
Importing: /home/vanessa/.singularity/docker/sha256:c62795f78da9ad31d9669cb4feb4e8fba995a299a0b2bd0f05b10fdc05b1f35e.tar.gz
Importing: /home/vanessa/.singularity/docker/sha256:d4fceeeb758e5103c39daf44c73404bf476ef6fd6b7a9a11e2260fcc1797c806.tar.gz
Importing: /home/vanessa/.singularity/docker/sha256:5c9125a401ae0cf5a5b4128633e7a4e84230d3eb4c541c661618a70e5d29aeff.tar.gz
Importing: /home/vanessa/.singularity/docker/sha256:0062f774e9942f61d13928855ab8111adc27def6f41bd6f7902c329ec836882b.tar.gz
Importing: /home/vanessa/.singularity/docker/sha256:6b33fd031facf4d7dd97afeea8a93260c2f15c3e795eeccd8969198a3d52678d.tar.gz
Importing: /home/vanessa/.singularity/metadata/sha256:fe44851d529f465f9aa107b32351c8a0a722fc0619a2a7c22b058084fac068a4.tar.gz
```

## Bootstrap
Instead of importing, you might want to bootstrap. Note that this will require sudo, so if you didn't give it to the client originally, you will be asked for it. Here we are going to generate a build specification called `Singularity` and use it to bootstrap an empty image.

```python
runscript = '''Bootstrap:docker
From: ubuntu:latest

%runscript
exec echo "Hello World!"
'''

import tempfile
storage = tempfile.mkdtemp()
os.chdir(storage)
with open('Singularity','w') as filey:
    filey.writelines(runscript)

container_name = 'ubuntu-hello-world-1.img'
S = Singularity(sudopw='mysecretpass')
S.create(container_name)
S.bootstrap(container_name,'Singularity')
```
To see if it worked, we can run the image.

## Run
Using the image above, we can test run:

```python
S.run(container_name)
'Hello World!'
```

You can also try running a Docker or Singularity Hub image directly, but be careful here, because anything that doesn't produce a written or file output is going to try to call some other program from within python.


## Exec
This command will allow you to execute any program within the given container image.

```python
S.help(command='exec')

S.execute(image_path=image,command='ls')

b'LICENSE\nMANIFEST.in\nREADME.md\nSingularity.spec\nbuild\ndist\ndocs\nimg\nmake_video.sh\npaper.md\npypi.sh\nrequirements.txt\nsetup.py\nsingularity\nsingularity.egg-info\nvsoch-singularity-images-mongo.img\n'
$'docker2singularity.sh\nget_docker_container_id.sh\nget_docker_meta.py\nmakeBases.py\nsingularity

```
Execute assumes that you want the output, and by default returns it.


## Export

Here you can export an image. The default export_type="tar", and it must be a pipe.

```python
S.export(image_path=image)
```

This is going to pipe the image into your stdout, which you probably don't want to do. Instead, you might want an in memory tar to work with, and if this is the case, you want a function from the [reproduce.py](../../singularity/reproduce.py) module:

```python
from singularity.reproduce import get_memory_tar
file_obj,tar = get_memory_tar(image)

file_obj
<_io.BytesIO at 0x7f4c05a47678>

tar
<tarfile.TarFile at 0x7f4c05a457f0>

# make sure to close when you finish!
file_obj.close()
```

