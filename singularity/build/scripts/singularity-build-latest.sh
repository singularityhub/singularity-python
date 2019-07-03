#!/bin/bash

################################################################################
# Build Latest, only runs build without updating software
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
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

SINGULARITY_libexecdir="/usr/local/libexec/singularity"
SINGULARITY_PATH="/usr/local/bin"
SECBUILD_IMAGE="$SINGULARITY_libexecdir/singularity/secure-build/secbuild.sif"

# Set the isolated root
if [ -z "${SINGULARITY_ISOLATED_ROOT:-}" ]; then
    BUILDDEF_DIR_NAME=$(dirname ${SINGULARITY_BUILDDEF:-})
else
    BUILDDEF_DIR_NAME=$(readlink -f ${SINGULARITY_ISOLATED_ROOT:-})
fi
BUILDDEF_DIR=$(readlink -f ${BUILDDEF_DIR_NAME:-})

if [ -z "${BUILDDEF_DIR:-}" ]; then
    message ERROR "Can't find parent directory of $SINGULARITY_BUILDDEF\n"
    exit 1
fi

BUILDDEF=$(basename ${SINGULARITY_BUILDDEF:-})

# create a temporary dir per build instance
export SINGULARITY_WORKDIR=$(mktemp -d)

# create /tmp and /var/tmp into WORKDIR
mkdir -p $SINGULARITY_WORKDIR/tmp $SINGULARITY_WORKDIR/var_tmp

# set sticky bit for these directories
chmod 1777 $SINGULARITY_WORKDIR/tmp
chmod 1777 $SINGULARITY_WORKDIR/var_tmp

# setup a fake root directory
cp -a /etc/skel $SINGULARITY_WORKDIR/root

cat > "$SINGULARITY_WORKDIR/root/.rpmmacros" << RPMMAC
%_var /var
%_dbpath %{_var}/lib/rpm
RPMMAC

REPO_DIR="/root/repo"
STAGED_BUILD_IMAGE="/root/build"

mkdir ${SINGULARITY_WORKDIR}${REPO_DIR}
mkdir ${SINGULARITY_WORKDIR}${STAGED_BUILD_IMAGE}

BUILD_SCRIPT="$SINGULARITY_WORKDIR/tmp/build-script"
TMP_CONF_FILE="$SINGULARITY_WORKDIR/tmp.conf"
FSTAB_FILE="$SINGULARITY_WORKDIR/fstab"
RESOLV_CONF="$SINGULARITY_WORKDIR/resolv.conf"
HOSTS_FILE="$SINGULARITY_WORKDIR/hosts"

cp /etc/resolv.conf $RESOLV_CONF
cp /etc/hosts $HOSTS_FILE

cat > "$FSTAB_FILE" << FSTAB
none $STAGED_BUILD_IMAGE      bind    dev     0 0
FSTAB

cat > "$TMP_CONF_FILE" << CONF
config passwd = no
config group = no
config resolv_conf = no
mount proc = no
mount sys = no
mount home = no
mount dev = minimal
mount devpts = no
mount tmp = no
enable overlay = no
user bind control = no
bind path = $SINGULARITY_WORKDIR/root:/root
bind path = $SINGULARITY_WORKDIR/tmp:/tmp
bind path = $SINGULARITY_WORKDIR/var_tmp:/var/tmp
bind path = $SINGULARITY_ROOTFS:$STAGED_BUILD_IMAGE
bind path = $BUILDDEF_DIR:$REPO_DIR
bind path = $FSTAB_FILE:/etc/fstab
bind path = $RESOLV_CONF:/etc/resolv.conf
bind path = $HOSTS_FILE:/etc/hosts
root default capabilities = default
allow user capabilities = no
CONF

# here build pre-stage
cat > "$BUILD_SCRIPT" << SCRIPT
#!/bin/sh
mount -r --no-mtab -t proc proc /proc
if [ \$? != 0 ]; then
    echo "Can't mount /proc directory"
    exit 1
fi
mount -r --no-mtab -t sysfs sysfs /sys
if [ \$? != 0 ]; then
    echo "Can't mount /sys directory"
    exit 1
fi
mount -o remount,dev $STAGED_BUILD_IMAGE
if [ \$? != 0 ]; then
    echo "Can't remount $STAGED_BUILD_IMAGE"
    exit 1
fi
cd $REPO_DIR
singularity build --sandbox $STAGED_BUILD_IMAGE $BUILDDEF
exit \$?
SCRIPT

chmod +x $BUILD_SCRIPT

unset SINGULARITY_IMAGE
unset SINGULARITY_NO_PRIVS
unset SINGULARITY_KEEP_PRIVS
unset SINGULARITY_ADD_CAPS
unset SINGULARITY_DROP_CAPS

${SINGULARITY_bindir}/singularity -c $TMP_CONF_FILE exec -e -i -p $SECBUILD_IMAGE /tmp/build-script
if [ $? != 0 ]; then
    rm -rf $SINGULARITY_WORKDIR
    exit 1
fi

rm -rf $SINGULARITY_WORKDIR










echo "Start Time: $(date)." > /tmp/.shub-log 2>&1
timeout -s KILL 2h sudo python3 -c "from singularity.build.google import run_build; run_build()" >> /tmp/.shub-log 2>&1
ret=$?

echo "Return value of ${ret}." >> /tmp/.shub-log 2>&1

if [ $ret -eq 137 ]
then
    echo "Killed: $(date)." >> /tmp/.shub-log 2>&1
else
    echo "End Time: $(date)." >> /tmp/.shub-log 2>&1
fi

# Finish by sending log
sudo python3 -c "from singularity.build.google import finish_build; finish_build()"
