#!/bin/bash

################################################################################
# Instance Preparation
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
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
                   zypper \
                   libssl-dev \
                   python3-pip


# Pip3 installs
sudo pip3 install --upgrade pip &&
sudo pip3 install pyasn1-modules -U &&
sudo pip3 install --upgrade google-api-python-client &&
sudo pip3 install --upgrade google &&
sudo pip3 install oauth2client==3.0.0

# Install Singularity from Github

cd /tmp && git clone -b feature-squashbuild-secbuild-2.5.0 https://github.com/cclerget/singularity.git &&
cd /tmp/singularity && ./autogen.sh && ./configure --prefix=/usr/local && make && sudo make install && sudo make secbuildimg

# Singularity python development
cd /tmp && git clone -b v2.5 https://www.github.com/vsoch/singularity-python.git &&
cd /tmp/singularity-python && sudo python3 setup.py install
