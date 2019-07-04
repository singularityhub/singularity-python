#!/bin/bash

# The script takes the definition file as first argument. and
# desired final image page as second.
SINGULARITY_BUILDDEF="${1}"
SINGULARITY_FINAL="${2}"

if [ ! -f "${SINGULARITY_BUILDDEF}" ]; then
    echo "${SINGULARITY_BUILDDEF} does not exist";
    exit 1;
else
    echo "Build definition file found as ${SINGULARITY_BUILDDEF}"
fi

SINGULARITY_confdir="/usr/local/etc/singularity"
SINGULARITY_bindir="/usr/local/bin"
SINGULARITY_libexecdir="/usr/local/libexec/singularity"
SINGULARITY_PATH="/usr/local/bin"
SECBUILD_IMAGE="$SINGULARITY_libexecdir/secure-build/secbuild.sif"

# Set the isolated root
if [ -z "${SINGULARITY_ISOLATED_ROOT:-}" ]; then
    BUILDDEF_DIR_NAME=$(dirname ${SINGULARITY_BUILDDEF:-})
else
    BUILDDEF_DIR_NAME=$(readlink -f ${SINGULARITY_ISOLATED_ROOT:-})
fi
BUILDDEF_DIR=$(readlink -f ${BUILDDEF_DIR_NAME:-})

if [ -z "${BUILDDEF_DIR:-}" ]; then
   echo "Can't find parent directory of $SINGULARITY_BUILDDEF"
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

mkdir -p ${SINGULARITY_WORKDIR}${REPO_DIR}
mkdir -p ${SINGULARITY_WORKDIR}${STAGED_BUILD_IMAGE}

# Move the repo to be the REPO_DIR
cp -R $BUILDDEF_DIR/* ${SINGULARITY_WORKDIR}$REPO_DIR

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
config passwd = yes
config group = no
config resolv_conf = no
mount proc = no
mount sys = no
mount home = no
mount dev = minimal
mount devpts = no
mount tmp = no
mount slave = no
enable overlay = no
enable underlay = no
user bind control = no
bind path = $SINGULARITY_WORKDIR/root:/root
bind path = $SINGULARITY_WORKDIR/tmp:/tmp
bind path = $SINGULARITY_WORKDIR/var_tmp:/var/tmp
bind path = /tmp/sbuild/fs:$STAGED_BUILD_IMAGE
bind path = $FSTAB_FILE:/etc/fstab
bind path = $RESOLV_CONF:/etc/resolv.conf
bind path = $HOSTS_FILE:/etc/hosts
root default capabilities = full
allow user capabilities = no
allow setuid = yes
CONF

# We only use the builder once, make default config
cp "$TMP_CONF_FILE" "${SINGULARITY_confdir}/singularity.conf"

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
cd $REPO_DIR
singularity build $STAGED_BUILD_IMAGE/container.sif $BUILDDEF
exit \$?
SCRIPT

chmod +x $BUILD_SCRIPT

unset SINGULARITY_IMAGE
unset SINGULARITY_NO_PRIVS
unset SINGULARITY_KEEP_PRIVS
unset SINGULARITY_ADD_CAPS
unset SINGULARITY_DROP_CAPS

${SINGULARITY_bindir}/singularity exec -e -i -p $SECBUILD_IMAGE /tmp/build-script
if [ $? != 0 ]; then
    rm -rf $SINGULARITY_WORKDIR
    exit 1
fi

if [ ! -f "${SINGULARITY_WORKDIR}${STAGED_BUILD_IMAGE}/container.sif" ]; then
   echo "Container was not built.";
   exit 1;
fi

mv "${SINGULARITY_WORKDIR}${STAGED_BUILD_IMAGE}/container.sif" "$BUILDDEF_DIR/${SINGULARITY_FINAL}"
rm -rf $SINGULARITY_WORKDIR
