#!/bin/bash
# See: https://cms-pdmv.cern.ch/mcm/requests?prepid=TOP-RunIIFall17wmLHEGS-00031&page=0&shown=270339
# Sets up the CMSSW release needed for producing LHE+GEN level events with the central tZq gridpack
# NOTE: This should be run from the 'lobster_workflow' directory in order to ensure that the CMSSW
#   releases are created in the correct location.
export SCRAM_ARCH=slc7_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_9_3_6/src ] ; then 
 echo "release CMSSW_9_3_6 already exists"
else
scram p CMSSW CMSSW_9_3_6
fi
cd CMSSW_9_3_6/src
eval `scram runtime -sh`

curl -s --insecure https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/TOP-RunIIFall17wmLHEGS-00031 --retry 2 --create-dirs -o Configuration/GenProduction/python/TOP-RunIIFall17wmLHEGS-00031-fragment.py 
[ -s Configuration/GenProduction/python/TOP-RunIIFall17wmLHEGS-00031-fragment.py ] || exit $?;

scram b
cd ../../
nevts=42
fragment=TOP-RunIIFall17wmLHEGS-00031-fragment.py
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