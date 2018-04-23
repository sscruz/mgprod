#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc630
if [ -r CMSSW_9_4_0_patch1/src ] ; then 
 echo release CMSSW_9_4_0_patch1 already exists
else
scram p CMSSW CMSSW_9_4_0_patch1
fi
cd CMSSW_9_4_0_patch1/src
eval `scram runtime -sh`


scram b
cd ../../
cmsDriver.py step1 --filein file:HIG-RunIIFall17DRPremix-00823ND.root --fileout file:HIG-RunIIFall17MiniAOD-00821ND.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 94X_mc2017_realistic_v11 --step PAT --nThreads 8 --era Run2_2017 --python_filename HIG-RunIIFall17MiniAOD-00821_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 30 || exit $? ; 

