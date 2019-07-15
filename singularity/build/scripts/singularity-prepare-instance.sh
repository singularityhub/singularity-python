#!/bin/bash

################################################################################
# Instance Preparation
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#                   Generated ubuntu 18.04, 100MB disk, n1-standard-2
#
################################################################################

sudo apt-get update &&
sudo apt-get -y install git \
                   build-essential \
                   libtool \
                   squashfs-tools \
                   autotools-dev \
                   libarchive-dev \
                   automake \
                   autoconf \
                   debootstrap \
                   yum \
                   uuid-dev \
                   libssl-dev \
                   python3-pip


# Pip3 installs
sudo -H pip3 install --upgrade pip
sudo -H pip3 install pyasn1-modules -U
sudo -H pip3 install --upgrade google-api-python-client
sudo -H pip3 install --upgrade google 
sudo -H pip3 install oauth2client==3.0.0

# Install Singularity from Github

cd /tmp && git clone -b feature-squashbuild-secbuild-2.5 https://github.com/vsoch/singularity.git &&
cd /tmp/singularity && ./autogen.sh && ./configure --prefix=/usr/local && make && sudo make install && sudo make secbuildimg

# Singularity python development
cd /tmp && git clone -b v2.5-private https://www.github.com/singularityhub/singularity-python.git &&
cd /tmp/singularity-python && sudo python3 setup.py install
