#!/bin/bash
export SCRAM_ARCH=slc7_amd64_gcc630
(
echo "Setting up CMSSW_9_3_1"
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_3_1/src ] ; then 
    echo release CMSSW_9_3_1 already exists
else
    scram p CMSSW CMSSW_9_3_1
fi
cd CMSSW_9_3_1/src
eval `scram runtime -sh`

scram b
cd ../../
)

(
echo "Setting up CMSSW_9_4_0_patch1"
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_4_0_patch1/src ] ; then 
    echo release CMSSW_9_4_0_patch1 already exists
else
    scram p CMSSW CMSSW_9_4_0_patch1
fi
cd CMSSW_9_4_0_patch1/src
eval `scram runtime -sh`

scram b
cd ../../
)

echo "Finished setup!"