# Run Singularity

These functions are a wrapper for the bash command line tool, singularity, to make functions programatically accessible from Python! (under development)

First, we need to import the Class in python

      from singularity.cli import Singularity
      S = Singularity()

      # These are the defaults, which can be specified
      S = Singularity(sudo=True,verbose=False)


The default will ask for your sudo password, and then not ask again to run commands. It is not stored anywhere on the system other than in the class variable, so you should not save/pickle the class variable for later use, unless you want others to have access to your password.


To get general help, there is a wrapper for the help command. When you run it without any arguments, you see the general `singularity --help`

      S.help()

You can also run with a command to get details for that command:

      S.help(command='run')

      # or return as string
      help = S.help(command="exec",stdout=False)


If you need an image, you can get it from:

      wget http://www.vbmis.com/bmi/project/singularity/package_image/ubuntu:latest-2016-04-06.img


Let's define the path to this in python:

      image_path = 'ubuntu:latest-2016-04-06.img'

## Singularity exec
This command will allow you to execute any program within the given container image.

      S.execute(image_path=image_path,command='ls')
      $'docker2singularity.sh\nget_docker_container_id.sh\nget_docker_meta.py\nmakeBases.py\nsingularity\nubuntu:latest-2016-04-06.img\n'

      S.help(command='exec')

## Singularity export

Here you can export an image. The default export_type="tar", pipe=False, and output_file = None. Not specifying an output file will produce file in a temporary directory.

      tmptar = S.export(image_path=image_path)

## Singularity create

Here is how to create a simple empty image.

      S.create(image_path='test.img')

## Singularity import

This is still under development - the image seems to create but there is a bug where I need to specify --debug! Likely the new version of singularity needs to come out so I can reinstall and test this again.

      docker_image = S.docker2singularity("ubuntu:latest")

This doesn't use the native singularity `import` command, as this would require the docker image specification. Look for an update to this after the new singularity is released.
