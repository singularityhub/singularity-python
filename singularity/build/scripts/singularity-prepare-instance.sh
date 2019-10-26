#!/bin/bash

################################################################################
# Instance Preparation (version 3.4*)
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#                   Ubuntu 18.04 LTS
#      
# Copyright (C) 2016-2019 Vanessa Sochat.
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
                   cryptsetup \
                   libssl-dev \
                   uuid-dev \
                   libgpgme-dev \
                   libseccomp-dev \
                   pkg-config \
                   squashfs-tools \
                   debootstrap \
                   yum \
                   python3-pip

# Pip3 installs
sudo -H python3 -m pip install --upgrade pip
sudo -H python3 -m pip install pyasn1-modules -U
sudo -H python3 -m pip install --upgrade google-api-python-client
sudo -H python3 -m pip install --upgrade google
sudo -H python3 -m pip install oauth2client==3.0.0
sudo -H python3 -m pip install ipython

# Install GoLang
export VERSION=1.13 OS=linux ARCH=amd64

wget -O /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz https://dl.google.com/go/go${VERSION}.${OS}-${ARCH}.tar.gz && \
    sudo tar -C /usr/local -xzf /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz

# Install Singularity from Github

mkdir -p /tmp/go
export GOPATH=/tmp/go SINGULARITY_VERSION=3.4.2
export PATH=/usr/local/go/bin:$PATH
echo 'Defaults env_keep += "GOPATH"' | sudo tee --append /etc/sudoers.d/env_keep

mkdir -p ${GOPATH}/src/github.com/sylabs && \
    cd ${GOPATH}/src/github.com/sylabs && \
    wget https://github.com/sylabs/singularity/archive/v${SINGULARITY_VERSION}.tar.gz && \
    tar -xzvf v${SINGULARITY_VERSION}.tar.gz && \
    mv singularity-${SINGULARITY_VERSION} singularity && \
    cd singularity && \
    echo "v${SINGULARITY_VERSION}" > VERSION

# https://github.com/sylabs/singularity/blob/release-3.4/internal/pkg/build/build.go is 3.4.2 at build time
cd ${GOPATH}/src/github.com/sylabs/singularity && \
    wget https://raw.githubusercontent.com/singularityhub/singularity-python/v$SINGULARITY_VERSION/singularity/build/scripts/bundle.go && \
    wget https://raw.githubusercontent.com/singularityhub/singularity-python/v$SINGULARITY_VERSION/singularity/build/scripts/build.go && \
    mv bundle.go pkg/build/types/ && \
    mv build.go internal/pkg/build/build.go
    ./mconfig && \
    cd ./builddir && \
    make && \
    sudo make install

# Prepare Secure Build

SINGULARITY_libexecdir="/usr/local/libexec/singularity"
SINGULARITY_PATH="/usr/local/bin"

sudo mkdir -p "$SINGULARITY_libexecdir/secure-build"
SECBUILD_IMAGE="$SINGULARITY_libexecdir/secure-build/secbuild.sif"

BUILDTMP=$(mktemp -d)
SECBUILD_SINGULARITY="$BUILDTMP/singularity"
SECBUILD_DEFFILE="$BUILDTMP/secbuild.def"

cat > "$SECBUILD_DEFFILE" << DEFFILE
Bootstrap: docker
From: ubuntu:18.04
%post 
    export LC_LANG=C
    export VERSION=1.12.6 OS=linux ARCH=amd64
    export SINGULARITY_VERSION=3.2.1
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get -y install git build-essential libssl-dev uuid-dev pkg-config curl gcc cryptsetup
    apt-get -y install libgpgme11-dev libseccomp-dev squashfs-tools libc6-dev-i386
    apt-get install -y debootstrap yum pacman
    apt-get clean
    apt-get autoclean
    rm -rf /usr/local/libexec/singularity
    rm -rf /usr/local/lib/singularity
    wget -O /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz https://dl.google.com/go/go${VERSION}.${OS}-${ARCH}.tar.gz && \
    tar -C /usr/local -xzf /tmp/go${VERSION}.${OS}-${ARCH}.tar.gz

    mkdir -p /tmp/go
    export GOPATH=/tmp/go
    export PATH=/usr/local/go/bin:$PATH
    export HOME=/root

    mkdir -p ${GOPATH}/src/github.com/sylabs && \
        cd ${GOPATH}/src/github.com/sylabs && \
        wget https://github.com/sylabs/singularity/archive/v${SINGULARITY_VERSION}.tar.gz && \
        tar -xzvf v${SINGULARITY_VERSION}.tar.gz && \
        mv singularity-${SINGULARITY_VERSION} singularity && \
        cd singularity && \
        echo "v${SINGULARITY_VERSION}" > VERSION

    cd ${GOPATH}/src/github.com/sylabs/singularity && \
        ./mconfig && \
        cd ./builddir && \
        make && \
        make install

    sed -i 's/^.*allow-setuid.*$/allow setuid = no/' /usr/local/etc/singularity/singularity.conf
DEFFILE

sudo $SINGULARITY_PATH/singularity build --sandbox $SECBUILD_IMAGE $SECBUILD_DEFFILE

# Singularity python
cd /tmp && git clone -b v${SINGULARITY_VERSION} https://www.github.com/singularityhub/singularity-python.git &&
cd /tmp/singularity-python && sudo python3 setup.py install
