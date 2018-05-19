#!/bin/bash

################################################################################
# Instance Preparation
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
#
# Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
# University.
# Copyright (C) 2016-2017 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
