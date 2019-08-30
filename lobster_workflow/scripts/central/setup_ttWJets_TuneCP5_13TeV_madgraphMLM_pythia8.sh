#!/bin/bash
# See: https://cms-pdmv.cern.ch/mcm/requests?prepid=HIG-RunIIFall17wmLHEGS-00040&page=0&shown=270339
# Sets up the CMSSW release needed for producing LHE+GEN level events with a central ttW gridpack
# NOTE: This should be run from the 'lobster_workflow' directory in order to ensure that the CMSSW
#   releases are created in the correct location.
export SCRAM_ARCH=slc7_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_3_1/src ] ; then 
 echo release CMSSW_9_3_1 already exists
else
scram p CMSSW CMSSW_9_3_1
fi
cd CMSSW_9_3_1/src
eval `scram runtime -sh`

curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/HIG-RunIIFall17wmLHEGS-00040 --retry 2 --create-dirs -o Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-00040-fragment.py 
[ -s Configuration/GenProduction/python/HIG-RunIIFall17wmLHEGS-00040-fragment.py ] || exit $?;

scram b
cd ../../
nevts=42
fragment=HIG-RunIIFall17wmLHEGS-00040-fragment.py
seed=$(date +%s)

# LHE Only
fout=LHE-00000.root
cfgname=LHE-00000_1_cfg.py
cmsDriver.py Configuration/GenProduction/python/${fragment} --fileout file:${fout} --mc --eventcontent LHE --datatier LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE --nThreads 8 --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${seed}%100)" -n ${nevts} || exit $? ;

# GEN Only
fin=LHE-00000.root
fout=GEN-00000.root
cfgname=GEN-00000_1_cfg.py
cmsDriver.py Configuration/GenProduction/python/${fragment} --filein file:${fin} --fileout file:${fout} --mc --eventcontent RAWSIM --datatier GEN --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN --nThreads 8 --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;