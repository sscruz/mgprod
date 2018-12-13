#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc630
if [ -r CMSSW_9_3_1/src ] ; then 
    echo release CMSSW_9_3_1 already exists
else
    scram p CMSSW CMSSW_9_3_1
fi
cd CMSSW_9_3_1/src
eval `scram runtime -sh`

scram b
cd ../../

if [ -r CMSSW_9_4_0_patch1/src ] ; then 
    echo release CMSSW_9_4_0_patch1 already exists
else
    scram p CMSSW CMSSW_9_4_0_patch1
fi
cd CMSSW_9_4_0_patch1/src
eval `scram runtime -sh`

scram b
cd ../../

