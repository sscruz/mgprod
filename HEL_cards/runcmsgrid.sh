#!/bin/bash

nevt=${1}
echo "%MSG-MG5 number of events requested = $nevt"

rnum=${2}
echo "%MSG-MG5 random seed used for the run = $rnum"

ncpu=${3}
echo "%MSG-MG5 number of cpus = $ncpu"

LHEWORKDIR=`pwd`

use_gridpack_env=true
if [ -n "$4" ]
  then
  use_gridpack_env=$4
fi

if [ "$use_gridpack_env" = true ]
  then
    if [ -n "$5" ]
      then
        scram_arch_version=${5}
      else
        scram_arch_version=slc6_amd64_gcc481
    fi
    echo "%MSG-MG5 SCRAM_ARCH version = $scram_arch_version"

    if [ -n "$6" ]
      then
        cmssw_version=${6}
      else
        cmssw_version=CMSSW_7_1_30
    fi
    echo "%MSG-MG5 CMSSW version = $cmssw_version"
    export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
    source $VO_CMS_SW_DIR/cmsset_default.sh
    export SCRAM_ARCH=${scram_arch_version}
    scramv1 project CMSSW ${cmssw_version}
    cd ${cmssw_version}/src
    eval `scramv1 runtime -sh`
fi

cd $LHEWORKDIR

cd process

#make sure lhapdf points to local cmssw installation area
LHAPDFCONFIG=`echo "$LHAPDF_DATA_PATH/../../bin/lhapdf-config"`

echo "lhapdf = $LHAPDFCONFIG" >> ./madevent/Cards/me5_configuration.txt
# echo "cluster_local_path = `${LHAPDFCONFIG} --datadir`" >> ./madevent/Cards/me5_configuration.txt

if [ "$ncpu" -gt "1" ]; then
  echo "run_mode = 2" >> ./madevent/Cards/me5_configuration.txt
  echo "nb_core = $ncpu" >> ./madevent/Cards/me5_configuration.txt
fi

#generate events
./run.sh $nevt $rnum

domadspin=0
if [ -f ./madspin_card.dat ] ;then
    domadspin=1
    echo "import events.lhe.gz" > madspinrun.dat
    rnum2=$(($rnum+1000000))
    echo `echo "set seed $rnum2"` >> madspinrun.dat
    cat ./madspin_card.dat >> madspinrun.dat
    cat madspinrun.dat | $LHEWORKDIR/mgbasedir/MadSpin/madspin
fi

cd $LHEWORKDIR

runlabel=GridRun_${rnum}
event_file=events.lhe.gz
if [ "$domadspin" -gt "0" ] ; then 
    event_file=events_decayed.lhe.gz
fi
mv process/$event_file process/madevent/Events/${runlabel}/events.lhe.gz

# Add scale and PDF weights using systematics module
#
pushd process/madevent
pdfsets="306000,322500@0,322700@0,322900@0,323100@0,323300@0,323500@0,323700@0,323900@0,305800,13000,13065@0,13069@0,13100,13163@0,13167@0,13200@0,25200,25300,25000@0,42780,90200,91200,90400,91400,61100,61130,61200,61230,13400,82200,292200,292600@0,315000@0,315200@0,262000@0,263000@0"
scalevars="--mur=1,2,0.5 --muf=1,2,0.5 --together=muf,mur,dyn --dyn=-1,1,2,3,4"

echo "systematics $runlabel --pdf=$pdfsets $scalevars" | ./bin/madevent
popd

mv process/madevent/Events/${runlabel}/events.lhe.gz cmsgrid_final.lhe.gz
gzip -d cmsgrid_final.lhe.gz


#reweight if necessary
if [ -e process/madevent/Cards/reweight_card.dat ]; then
    echo "reweighting events"
    mv cmsgrid_final.lhe process/madevent/Events/GridRun_${rnum}/unweighted_events.lhe
    cd process/madevent
    ./bin/madevent reweight -f GridRun_${rnum}
    cd ../..
    #mv process/madevent/Events/GridRun_${rnum}/unweighted_events.lhe cmsgrid_final.lhe
    mv process/madevent/Events/GridRun_${rnum}/unweighted_events.lhe.gz cmsgrid_final.lhe.gz
    gzip -d  cmsgrid_final.lhe.gz
fi


ls -l
echo

exit 0
