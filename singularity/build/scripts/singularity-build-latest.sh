#!/bin/bash
# This install script assumes using an image with Singularity software installed
sudo apt-get update > /tmp/.install-log
sudo apt-get -y install git \
                   build-essential \
                   libtool \
                   autotools-dev \
                   squashfs-tools \
                   debootstrap \
                   automake \
                   autoconf \
                   python3-pip >> /tmp/.install-log


# Singularity python development
cd /tmp && git clone -b development https://www.github.com/vsoch/singularity-python.git &&
cd /tmp/singularity-python && sudo python3 setup.py install

# Pip3 installs
sudo pip3 install --upgrade pip &&
sudo pip3 install --upgrade google-api-python-client &&
sudo pip3 install --upgrade google &&
#sudo pip3 install singularity --upgrade &&
sudo pip3 install oauth2client==3.0.0

# Main running script
sudo python3 -c "from singularity.build.google import run_build; run_build()" > /tmp/.shub-log 2>&1 &&

# Finish by sending log
export command=$(echo "from singularity.build.google import finish_build; finish_build()") &&
sudo python3 -c "$command"
