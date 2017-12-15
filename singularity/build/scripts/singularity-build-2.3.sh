#!/bin/bash

################################################################################
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

# This install script assumes using an image with Singularity installed
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

# Pip3 installs
sudo pip3 install --upgrade pip &&
sudo pip3 install --upgrade google-api-python-client &&
sudo pip3 install --upgrade google &&
sudo pip3 install singularity --upgrade &&
sudo pip3 install oauth2client==3.0.0

# Main running script
python3 -c "from singularity.build.google import run_build; run_build()" > /tmp/.shub-log 2>&1

# Finish by sending log
export command=$(echo "from singularity.build.google import finish_build; finish_build()") &&
python3 -c "$command"
