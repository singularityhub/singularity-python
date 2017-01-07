#!/usr/bin/env python

# This is an example of generating image packages from within python

import os
import shutil
from singularity.cli import get_image
from singularity.package import package

# Save packages here
output_folder = '/home/vanessa/Documents/Dropbox/Code/singularity/singularity-python/examples/package_image/packages'

# Here are my images. I'm lazy so I'm going to use all docker
# https://github.com/docker-library/official-images/tree/master/library
images = ['aerospike','alpine','amazonlinux','arangodb','backdrop','bash','bonita','buildpack-deps',
          'busybox','cassandra','celery','centos','chronograf','cirros','clearlinux','clojure','composer',
          'consul','couchbase','couchdb','crate','crux','debian','django','docker','drupal','eclipse-mosquitto',
          'eggdrop','elasticsearch','elixir','erlang','fedora','fsharp','gazebo','gcc','ghost','golang','haproxy',
          'haskell','hello-world','httpd','hylang','ibmjava','influxdb','iojs','irssi','java','jenkins','jetty',
          'joomla','jruby','julia','kaazing-gateway','kapacitor','kibana','known','kong','lightstreamer',
          'logstash','mageia','mariadb','maven','memcached','mongo','mongo-express','mono','mysql','nats',
          'nats-streaming','neo4j','neurodebian','nextcloud','nginx','node','notary','nuxeo','odoo','openjdk',
          'opensuse','oraclelinux','orientdb','owncloud','percona','perl','photon','php','php-zendserver',
          'piwik','plone','postgres','pypy','python','r-base','rabbitmq','rails','rakudo-star','redis',
          'redmine','registry','rethinkdb','rocket.chat','ros','ruby','sentry','solr','sonarqube','sourcemage',
          'spiped','storm','swarm','telegraf','thrift','tomcat','tomee','traefik','ubuntu','vault',
          'websphere-liberty','wordpress','zookeeper']

# You will need to export your sudopw to an environment variable called pancakes for it to not ask you :)
os.environ['pancakes'] = 'yoursecretpass'

for name in images:
    docker_image = "docker://%s:latest" %(name)
    image = get_image(docker_image)
    package_name = "%s/%s.zip" %(output_folder,os.path.basename(image))
    if not os.path.exists(package_name):
        image_package = package(image_path=image,
                                output_folder=output_folder,
                                remove_image=True,
                                runscript=True,
                                software=True)
    tmpfolder = os.path.dirname(image)


