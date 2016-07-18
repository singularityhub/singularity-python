#! /bin/bash
#
# docker2singularity.sh will convert a docker image into a singularity
# Must be run with sudo to use docker commands (eg aufs)
#
# USAGE: docker2singularity.sh ubuntu:14.04
set -o errexit
set -o nounset

usage="$0 ubuntu:14.04"
if [ -z $1 ]; then
    echo $usage;
    exit 0;
else
    image=$1
fi

MY_GROUPS=`groups`

permission=false
for group in $MY_GROUPS; do
    if [[ "$group" == "sudo" ]]; then
        SUDOCMD="sudo"
        permission=true
        break
    elif [[ "$group" == "root" ]]; then
        SUDOCMD=""
        permission=true
        break
    fi
done

if [[ $permission == false ]]; then
    echo "Sorry you need to be at least sudoer to run this script. Bye."
    exit 1
fi


################################################################################
### CONTAINER RUNNING ID #######################################################
################################################################################

runningid=`$SUDOCMD docker run -d $image tail -f /dev/null`

# Full id looks like
# sha256:d59bdb51bb5c4fb7b2c8d90ae445e0720c169c553bcf553f67cb9dd208a4ec15

# Take the first 12 characters to get id of container
container_id=`echo ${runningid} | cut -c1-12`

# Network address, if needed
network_address=`$SUDOCMD docker inspect --format="{{.NetworkSettings.IPAddress}}" $container_id`


################################################################################
### IMAGE NAME #################################################################
################################################################################

image_name=`$SUDOCMD docker inspect --format="{{.Config.Image}}" $container_id`

# using bash substitution
# removing special chars [perhaps echo + sed would be better for other chars]
image_name=${image_name/\//_}

# following is the date of the container, not the docker image.
#creation_date=`$SUDOCMD docker inspect --format="{{.Created}}" $container_id`
creation_date=`$SUDOCMD docker inspect --format="{{.Created}}" $image`


################################################################################
### IMAGE SIZE #################################################################
################################################################################

size=`$SUDOCMD docker inspect --format="{{.Size}}" $image`
# convert size in MB (it seems too small for singularity containers ...?). Add 1MB to round up (minimum).
size=`echo $(($size/1000000+1))`
# adding half of the container size seems to work (do not know why exactly...?)
# I think it would be Ok by adding 1/3 of the size.
size=`echo $(($size+$size/2))`

echo "Size: $size MB for the singularity container"




################################################################################
### IMAGE CREATION #############################################################
################################################################################
TMPDIR=$(mktemp -u -d)
mkdir -p $TMPDIR

creation_date=`echo ${creation_date} | cut -c1-10`
new_container_name=$image_name-$creation_date.img
$SUDOCMD singularity create -s $size $new_container_name
$SUDOCMD docker export $container_id | $SUDOCMD singularity import $new_container_name
$SUDOCMD docker inspect $container_id >> $TMPDIR/singularity.json
sudo singularity copy $new_container_name $TMPDIR/singularity.json /

# Merge the /etc/group file
$SUDOCMD docker cp $container_id:/etc/group $TMPDIR/grouphost
sort /etc/group $TMPDIR/grouphost | uniq -u > $TMPDIR/group
$SUDOCMD singularity copy $new_container_name $TMPDIR/group /etc/group
$SUDOCMD singularity bootstrap $new_container_name
$SUDOCMD chmod a+rw -R $TMPDIR

################################################################################
### SINGULARITY RUN SCRIPT #####################################################
################################################################################

CMD=$($SUDOCMD docker inspect --format='{{json .Config.Cmd}}' $image)
if [[ $CMD != [* ]]; then
	CMD="/bin/sh -c "$CMD
fi
# Remove quotes and braces
CMD=`echo "${CMD//\"/}" | sed 's/\[/\//g' | sed 's/\]//g' | sed 's/,//g'`

ENTRYPOINT=$($SUDOCMD docker inspect --format='{{json .Config.Entrypoint}}' $image)
if [[ $ENTRYPOINT != [* ]]; then
	ENTRYPOINT="/bin/sh -c "$ENTRYPOINT
fi
# Remove quotes and braces
ENTRYPOINT=`echo "${ENTRYPOINT//\"/}" | sed 's/\[//g' | sed 's/\]//g' | sed 's/,//g'`

echo '#!/bin/sh' > $TMPDIR/singularity
if [[ $ENTRYPOINT != "null" ]]; then
    echo $ENTRYPOINT >> $TMPDIR/singularity;
else
    echo $CMD >> $TMPDIR/singularity;
fi

chmod +x $TMPDIR/singularity
$SUDOCMD singularity copy $new_container_name $TMPDIR/singularity /

################################################################################
### SINGULARITY ENVIRONMENT ####################################################
################################################################################

docker run --rm --entrypoint="/usr/bin/env" $image > $TMPDIR/docker_environment
# don't include HOME and HOSTNAME - they mess with local config
sed -i '/^HOME/d' $TMPDIR/docker_environment
sed -i '/^HOSTNAME/d' $TMPDIR/docker_environment
$SUDOCMD singularity copy $new_container_name $TMPDIR/docker_environment /
$SUDOCMD singularity exec --writable $new_container_name /bin/sh -c "echo '. /docker_environment' >> /environment"
rm -rf $TMPDIR

################################################################################
### Permissions ################################################################
################################################################################

# making sure that any user can read and execute everything in the container
echo "Fixing permissions"
$SUDOCMD singularity exec --writable --contain $new_container_name /bin/sh -c "find /* -maxdepth 0 -not -path '/dev*' -not -path '/proc*' -exec chmod a+r -R '{}' \;"
$SUDOCMD singularity exec --writable --contain $new_container_name /bin/sh -c "find / -executable -perm -u+x,o-x -not -path '/dev*' -not -path '/proc*' -exec chmod a+x '{}' \;"

echo "Stopping container, please wait."
$SUDOCMD docker stop $container_id
