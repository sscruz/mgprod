#!/bin/bash
# See: https://cms-pdmv.cern.ch/mcm/requests?member_of_chain=HIG-chain_RunIIFall17wmLHEGS_flowRunIIFall17DRPremixPU2017_flowRunIIFall17MiniAOD-00031&page=0&shown=4115
# Sets up the CMSSW releases and creates the python configs for the various processing steps. These
#   python configs are all built using the 'HIG-RunIIFall17wmLHEGS-00040' McM request as an example.
#   Additional python configs can then be made by copying these baseline configs and modifying them
#   accordingly (e.g. for ttH parton showering).
# NOTE: This should be run from the 'lobster_workflow' directory in order to ensure that the CMSSW
#   releases are created in the correct location.
export SCRAM_ARCH=slc6_amd64_gcc630
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

# Based on 'HIG-RunIIFall17wmLHEGS-00040'

# LHE Only
fout=LHE-00000.root
cfgname=LHE-00000_1_cfg.py
cmsDriver.py Configuration/GenProduction/python/${fragment} --fileout file:${fout} --mc --eventcontent LHE --datatier LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE --nThreads 8 --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

# GEN Only
fin=LHE-00000.root
fout=GEN-00000.root
cfgname=GEN-00000_1_cfg.py
cmsDriver.py Configuration/GenProduction/python/${fragment} --filein file:${fin} --fileout file:${fout} --mc --eventcontent RAWSIM --datatier GEN --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN --nThreads 8 --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

# SIM Only
fin=GEN-00000.root
fout=LHEGS-00040.root
cfgname=SIM-00000_1_cfg.py
cmsDriver.py Configuration/GenProduction/python/${fragment} --filein file:${fin} --fileout file:${fout} --mc --eventcontent RAWSIM --datatier SIM --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step SIM --nThreads 8 --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

# GEN-SIM Only
fin=LHE-00000.root
fout=LHEGS-00040.root
cfgname=GS-00000_1_cfg.py
cmsDriver.py Configuration/GenProduction/python/${fragment} --filein file:${fin} --fileout file:${fout} --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN,SIM --nThreads 8 --geometry DB:Extended --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

# LHE+GEN-SIM
fout=LHEGS-00040.root
cfgname=LHEGS-00040_1_cfg.py
cmsDriver.py Configuration/GenProduction/python/${fragment} --fileout file:${fout} --mc --eventcontent RAWSIM,LHE --datatier GEN-SIM,LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE,GEN,SIM --nThreads 8 --geometry DB:Extended --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

if [ -r CMSSW_9_4_0_patch1/src ] ; then 
 echo release CMSSW_9_4_0_patch1 already exists
else
 scram p CMSSW CMSSW_9_4_0_patch1
fi
cd CMSSW_9_4_0_patch1/src
eval `scram runtime -sh`

scram b
cd ../../

# DRPremix Step1
fin=LHEGS-00040.root
fout=DRPremix-00823_step1.root
cfgname=DRPremix-00823_1_cfg.py
cmsDriver.py step1 --filein file:${fin} --fileout file:${fout} --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --nThreads 8 --datamix PreMix --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

# DRPremix Step2
fin=DRPremix-00823_step1.root
fout=DRPremix-00823.root
cfgname=DRPremix-00823_2_cfg.py
cmsDriver.py step2 --filein file:${fin} --fileout file:${fout} --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 94X_mc2017_realistic_v11 --step RAW2DIGI,RECO,RECOSIM,EI --nThreads 8 --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

# mAOD Step
fin=DRPremix-00823.root
fout=MiniAOD-00821.root
cfgname=MiniAOD-00821_1_cfg.py
cmsDriver.py step1 --filein file:${fin} --fileout file:${fout} --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 94X_mc2017_realistic_v11 --step PAT --nThreads 8 --era Run2_2017 --python_filename ${cfgname} --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n ${nevts} || exit $? ;

