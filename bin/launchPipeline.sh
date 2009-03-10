#! /bin/bash
#
# set -x
bindir=""
if echo $0 | grep -q /; then
    bindir=`dirname $0`
fi

if [ -z "$DC3PIPE_DIR" ]; then

    # make sure we load the dc3pipe environment
    version=`dirname "$bindir"`         # dc3pipe version directory
    if [ "$version" = "."  ]; then
        echo "Unable to load dc3pipe: unable to determin version from $bindir"
        exit 1
    fi

    if [ -z "$LSST_HOME" ]; then
        home=`dirname "$version"`           # dc2ipe directory
        home=`dirname "$home"`              # flavor directory
        export LSST_HOME=`dirname "$home"`  # LSST_HOME directory

    fi
    version=`basename $version`

    if [ ! -f "$LSST_HOME/loadLSST.sh" ]; then
        echo "Unable to load LSST stack; " \
             "can't find $LSST_HOME/loadLSST.sh"
        exit 1
    fi

    SHELL=/bin/bash
    source  $LSST_HOME/loadLSST.sh
    setup dc3pipe $version
fi

eups list 2> /dev/null | grep Setup > eups-env.txt
pipeline=`echo ${1} | sed -e 's/\..*$//'`
nohup $bindir/launchPipeline.py $* > ${pipeline}-${2}.log 2>&1  &
