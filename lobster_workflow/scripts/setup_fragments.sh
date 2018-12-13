#!/bin/bash
# Sets up the CMSSW releases and creates the python configs for the LHE, GS, DIGIRECO, and mAOD
#   processing steps. It should produce *_cfg.py files identical (or similar) to those already saved
#   in the fragments directory.
# NOTE: The script assumes that it gets run from the 'lobster_workflow' directory in order to find
#       the fragments directory
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc630
if [ -r CMSSW_9_3_1/src ] ; then 
 echo release CMSSW_9_3_1 already exists
else
 scram p CMSSW CMSSW_9_3_1
fi
cd CMSSW_9_3_1/src
eval `scram runtime -sh`

mkdir -p Configuration/GenProduction/python

fragment=GS-fragment_default ; cfgsuffix=""
#fragment=GS-fragment_ttH ; cfgsuffix="-ttH"

cp ../../fragments/${fragment} Configuration/GenProduction/python/${fragment}

scram b
cd ../../

# LHE Step
cmsDriver.py Configuration/GenProduction/python/${fragment} --fileout file:HIG-RunIIFall17wmLHE-00000ND.root --mc --eventcontent LHE --datatier LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step LHE --nThreads 8 --geometry DB:Extended --era Run2_2017 --python_filename HIG-RunIIFall17wmLHE-00000_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 30
# GS Step
cmsDriver.py Configuration/GenProduction/python/${fragment} --filein file:HIG-RunIIFall17wmLHE-00000ND.root --fileout file:HIG-RunIIFall17wmLHEGS-00040ND.root --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN,SIM --nThreads 8 --geometry DB:Extended --era Run2_2017 --python_filename HIG-RunIIFall17wmGS-00000${cfgsuffix}_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 30

if [ -r CMSSW_9_4_0_patch1/src ] ; then 
 echo release CMSSW_9_4_0_patch1 already exists
else
 scram p CMSSW CMSSW_9_4_0_patch1
fi
cd CMSSW_9_4_0_patch1/src
eval `scram runtime -sh`

scram b
cd ../../

# drPremix Step1
cmsDriver.py step1 --filein file:HIG-RunIIFall17wmLHEGS-00040ND.root --fileout file:HIG-RunIIFall17DRPremix-00823ND_step1.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --nThreads 8 --datamix PreMix --era Run2_2017 --python_filename HIG-RunIIFall17DRPremix-00823_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 30
# drPremix Step2
cmsDriver.py step2 --filein file:HIG-RunIIFall17DRPremix-00823ND_step1.root --fileout file:HIG-RunIIFall17DRPremix-00823ND.root --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 94X_mc2017_realistic_v11 --step RAW2DIGI,RECO,RECOSIM,EI --nThreads 8 --era Run2_2017 --python_filename HIG-RunIIFall17DRPremix-00823_2_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 30
# mAOD Step
cmsDriver.py step1 --filein file:HIG-RunIIFall17DRPremix-00823ND.root --fileout file:HIG-RunIIFall17MiniAOD-00821ND.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 94X_mc2017_realistic_v11 --step PAT --nThreads 8 --era Run2_2017 --python_filename HIG-RunIIFall17MiniAOD-00821_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 30