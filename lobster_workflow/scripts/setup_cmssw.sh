#!/bin/bash

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

setup_rel(){

    printf "\nSet up CMSSW release for $1...\n"
    if [ -r $1/src ] ; then
        echo release $1 already exists
    else
        scram p CMSSW $1
    fi
    cd $1/src
    eval `scram runtime -sh`

    scram b
    cd ../..

    printf "CMSSW base: $CMSSW_BASE\n"
}

( setup_rel CMSSW_9_3_1 )
( setup_rel CMSSW_9_4_0_patch1 )
( setup_rel CMSSW_9_3_6 )

# For the UL16 samples
( setup_rel CMSSW_10_6_17_patch1 )
( setup_rel CMSSW_8_0_33_UL )
( setup_rel CMSSW_10_6_20 )
( setup_rel CMSSW_10_6_19_patch2 )
