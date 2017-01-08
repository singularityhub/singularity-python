#!/usr/bin/env python

# This is an example of generating image packages from within python. The docker image packages (top) will
# retrieve all of docker official library (as of 1/2017), and the os specific images (bottom) will 
# retrieve base os (both included with singularity-python)

import os
import shutil
from singularity.cli import get_image
from singularity.package import package

# Save packages here
output_base = '/home/vanessa/Documents/Dropbox/Code/singularity/singularity-python/examples/package_image/packages'

## DOCKER LIBBRARY IMAGES
# https://github.com/docker-library/official-images/tree/master/library
images = ['aerospike:3.10.1.1','alpine:3.5','amazonlinux:2016.09','arangodb:3.1.7','backdrop:1.5.2',
          'bash:4.4.5','bonita:7.3.3','buildpack-deps:jessie',
          'busybox:1.26.1-glibc','cassandra:3.9','celery:3.1.3','centos:7',
          'chronograf:0.13.0','cirros:0.3.4','clearlinux:base','clojure:lein-2.7.1',
          'composer:1.3.0','consul:0.7.2','couchbase:enterprise-4.5.1','couchdb:1.6.1','crate:1.0.1',
          'debian:8.6','docker:1.13.0-rc5','drupal:8.2.5-apache','eclipse-mosquitto:1.4.10','eggdrop:1.8.0',
          'elasticsearch:5.1.1','elixir:1.4.0','erlang:19.2','fedora:25','fsharp:4.0.0.4','gazebo:libgazebo7',
          'gcc:4.9.4','ghost:0.11.3','golang:1.6.4','haproxy:1.7.1','haskell:8.0.1','hello-world:latest',
          'httpd:2.2.31','hylang:0.11.1','ibmjava:8-jre','influxdb:1.1.1','iojs:3.3.0','irssi:1.0.0',
          'jenkins:2.32.1','jetty:9.3.15','joomla:3.6.5','jruby:9.1.6.0-jre','julia:0.5.0',
          'kaazing-gateway:5.3.2','kapacitor:1.1.1','kibana:5.1.1','known:0.9.2','kong:0.9.7','lightstreamer:6.0.3',
          'logstash:5.1.1','mageia:5','mariadb:10.1.20','maven:3.3.9-jdk-8','memcached:1.4.33','mongo:3.4.1',
          'mongo-express:0.34.0','mono:4.6.2.16','mysql:5.7.17','nats:0.9.6',
          'nats-streaming:0.3.6','neo4j:3.1.0','neurodebian:nd70','nextcloud:10.0.0','nginx:1.11.8',
          'node:7.4.0','notary:server-0.5.0','notary:signer-0.5.0','nuxeo-LTS-2016','odoo:10.0','openjdk:8u111-jdk',
          'opensuse:42.2','oraclelinux:7.3','orientdb:2.2.14','owncloud:9.1.3-apache','percona:5.7.16',
          'perl:5.24.0','photon:1.0','php:7.1.0-cli','php-zendserver:9.0.1-php7',
          'piwik:3.0.0','plone:5.0.6','postgres:9.6.1','pypy:3-5.5.0-alpha','python:3.6.0',
          'r-base:3.3.2','rabbitmq:3.6.6','rakudo-star:2016.11','redis:3.0.7','redmine:3.1.7','registry:2.5.1',
          'rethinkdb:2.3.5','rocket.chat:0.48.2','ros:kinetic-ros-base','ruby:2.4.0','sentry:8.12.0',
          'solr:6.3.0','sonarqube:6.2','sourcemage:0.62','spiped:1.5.0','storm:1.0.2','swarm:1.2.5',
          'telegraf:1.1.2','thrift:0.9.3','tomcat:8.0.39-jre7',
          'tomee:8-jdk-7.0.1-webprofile','traefik:v1.1.2','ubuntu:16.04','vault:0.6.4',
          'websphere-liberty:javaee7','wordpress:4.7.0','zookeeper:3.4.9']

image_type = 'docker'


## OS IMAGES (provided via official docker library)
images = ['alpine:3.1','alpine:3.2','alpine:3.3','alpine:3.4','alpine:3.5',
          'busybox:1.26.1-glibc','busybox:1.26.1-musl','busybox:1.26.1-uclibc',
          'amazonlinux:2016:09',
          'centos:7','centos:6','centos:5',
          'cirros:0.3,4','cirros:0.3,3',
          'clearlinux:latest',
          'crux:3.1',
          'debian:8.6','debian:sid','debian:stretch','debian:7.11', # 8.6 is jessie, 7.11 is wheezy
          'fedora:25','fedora:24','fedora:23','fedora:22','fedora:21','fedora:20',
          'mageia:5',
          'opensuse:42.2','opensuse:42.1','opensuse:13.2','opensuse:tumbleweed' #  42.2 is leap, 13.2 harlequin
          'oraclelinux:7.3','oraclelinux:7.2','oraclelinux:7.1','oraclelinux:7.0','oraclelinux:6.8',
          'oraclelinux:6.7','oraclelinux:6.6','oraclelinux:5.11',
          'photon:1.0',
          'sourcemage:0.62',
          'swarm:1.2.6-rc1',
          'ubuntu:12.04.5','ubuntu:14.04.5','ubuntu:16.04','ubuntu:16.10','ubuntu:17.04']

image_type = 'os'

# You will need to export your sudopw to an environment variable called pancakes for it to not ask you :)
os.environ['pancakes'] = 'yoursecretpass'

# We will make subdirectories in package folder
output_folder = "%s/%s" %(output_base,image_type)

if not os.path.exists(output_folder):
   os.mkdir(output_folder)

for name in images:
    docker_image = "docker://%s" %(name)
    image = get_image(docker_image)
    package_name = "%s/%s.zip" %(output_folder,os.path.basename(image))
    if not os.path.exists(package_name):
        image_package = package(image_path=image,
                                output_folder=output_folder,
                                remove_image=True,
                                runscript=True,
                                software=True)
    tmpfolder = os.path.dirname(image)
    shutil.rmtree(tmpfolder)

