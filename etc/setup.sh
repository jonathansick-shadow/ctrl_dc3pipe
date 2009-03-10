source /lsst/DC3/stacks/default/loadLSST.sh
HERE=$PWD
cd  /lsst/home/srp/temp_merge/dc3pipe/trunk/;setup -r .
#cd  /lsst/home/srp/temp_merge/pex_harness/trunk/;setup -r .
#setup pex_logging 3.3.2
#cd  /lsst/home/srp/temp_merge/pex_policy/trunk/;setup -r .
cd $HERE
eups list
