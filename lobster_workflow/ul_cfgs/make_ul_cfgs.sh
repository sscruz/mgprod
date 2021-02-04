#!/bin/bash

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

MAKE_UL16_CFGS=false
MAKE_UL16APV_CFGS=false
MAKE_UL17_CFGS=false
MAKE_UL18_CFGS=false

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

###################### UL16 ######################

if $MAKE_UL16_CFGS ; then

    # UL16 SIM
    (
        CFG_NAME=UL16_SIM_cfg.py
        FIN=GEN-00000.root
        FOUT=SIM-00000.root
        REL=CMSSW_10_6_17_patch1

        # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16SIM
        # cmsDriver from url: cmsDriver.py step1 --mc --eventcontent RAWSIM --runUnscheduled --datatier GEN-SIM --conditions 106X_mcRun2_asymptotic_v13 --beamspot Realistic25ns13TeV2016Collision --step SIM --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:step-1.root --fileout file:step0.root

        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        cmsDriver.py step1 --mc --eventcontent RAWSIM --runUnscheduled --datatier GEN-SIM --conditions 106X_mcRun2_asymptotic_v13 --beamspot Realistic25ns13TeV2016Collision --step SIM --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16 DIGI
    (
        CFG_NAME=UL16_DIGI_cfg.py
        FIN=SIM-00000.root
        FOUT=DIGI-00000.root
        REL=CMSSW_10_6_17_patch1

        # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16DIGIPremix
        # cmsDriver from url: cmsDriver.py step1 --mc --eventcontent PREMIXRAW --runUnscheduled --datatier GEN-SIM-DIGI --conditions 106X_mcRun2_asymptotic_v13 --step DIGI,DATAMIX,L1,DIGI2RAW --procModifiers premix_stage2 --nThreads 8 --geometry DB:Extended --datamix PreMix --era Run2_2016  --filein file:step-1.root --fileout file:step0.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL16_106X_mcRun2_asymptotic_v13-v1/PREMIX"

        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        cmsDriver.py step1 --mc --eventcontent PREMIXRAW --runUnscheduled --datatier GEN-SIM-DIGI --conditions 106X_mcRun2_asymptotic_v13 --step DIGI,DATAMIX,L1,DIGI2RAW --procModifiers premix_stage2 --nThreads 8 --geometry DB:Extended --datamix PreMix --era Run2_2016  --filein file:$FIN --fileout file:$FOUT --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL16_106X_mcRun2_asymptotic_v13-v1/PREMIX" --python_filename $CFG_NAME --no_exec
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16 HLT
    (
        CFG_NAME=UL16_HLT_cfg.py
        FIN=DIGI-00000.root
        FOUT=HLT-00000.root
        REL=CMSSW_8_0_33_UL

        # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16HLT
        # cmsDriver from url: cmsDriver.py step1 --mc --eventcontent RAWSIM --outputCommand "keep *_mix_*_*,keep *_genPUProtons_*_*" --datatier GEN-SIM-RAW --inputCommands "keep *","drop *_*_BMTF_*","drop *PixelFEDChannel*_*_*_*" --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 --customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' --step HLT:25ns15e33_v4 --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:step-1.root --fileout file:step0.root

        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        cmsDriver.py step1 --mc --eventcontent RAWSIM --outputCommand "keep *_mix_*_*,keep *_genPUProtons_*_*" --datatier GEN-SIM-RAW --inputCommands "keep *","drop *_*_BMTF_*","drop *PixelFEDChannel*_*_*_*" --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 --customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' --step HLT:25ns15e33_v4 --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16 RECO
    (
        CFG_NAME=UL16_RECO_cfg.py
        FIN=HLT-00000.root
        FOUT=RECO-00000.root
        REL=CMSSW_10_6_17_patch1

        # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16RECO
        # cmsDriver from url: cmsDriver.py step1 --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 106X_mcRun2_asymptotic_v13 --step RAW2DIGI,L1Reco,RECO,RECOSIM --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:step-1.root --fileout file:step0.root

        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        cmsDriver.py step1 --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 106X_mcRun2_asymptotic_v13 --step RAW2DIGI,L1Reco,RECO,RECOSIM --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16 MAOD
    (
        CFG_NAME=UL16_MAOD_cfg.py
        FIN=RECO-00000.root
        FOUT=MAOD-00000.root
        REL=CMSSW_10_6_20

        # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16MiniAODv2
        # cmsDriver from url: cmsDriver.py step1 --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 106X_mcRun2_asymptotic_v13 --step PAT --procModifiers run2_miniAOD_UL --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:step-1.root --fileout file:step0.root

        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        cmsDriver.py step1 --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions 106X_mcRun2_asymptotic_v13 --step PAT --procModifiers run2_miniAOD_UL --nThreads 8 --geometry DB:Extended --era Run2_2016  --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16 NAOD
    (
        CFG_NAME=UL16_NAOD_cfg.py
        FIN=MAOD-00000.root
        FOUT=NAOD-00000.root
        REL=CMSSW_10_6_19_patch2

        # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16NanoAODv2
        # cmsDriver from url: cmsDriver.py step1 --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 106X_mcRun2_asymptotic_v15 --step NANO --nThreads 8 --era Run2_2016,run2_nanoAOD_106Xv1  --filein file:step-1.root --fileout file:step0.root

        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        cmsDriver.py step1 --mc --eventcontent NANOEDMAODSIM --datatier NANOAODSIM --conditions 106X_mcRun2_asymptotic_v15 --step NANO --nThreads 8 --era Run2_2016,run2_nanoAOD_106Xv1  --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

fi

###################### UL16APV ######################

if $MAKE_UL16APV_CFGS ; then
    # UL16APV SIM
    (
        CFG_NAME=UL16APV_SIM_cfg.py
        FIN=GEN-00000.root
        FOUT=SIM-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16APV DIGI
    (
        CFG_NAME=UL16APV_DIGI_cfg.py
        FIN=SIM-00000.root
        FOUT=DIGI-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16APV HLT
    (
        CFG_NAME=UL16APV_HLT_cfg.py
        FIN=DIGI-00000.root
        FOUT=HLT-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16APV RECO
    (
        CFG_NAME=UL16APV_RECO_cfg.py
        FIN=HLT-00000.root
        FOUT=RECO-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16APV MAOD
    (
        CFG_NAME=UL16APV_MAOD_cfg.py
        FIN=RECO-00000.root
        FOUT=MAOD-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL16APV NAOD
    (
        CFG_NAME=UL16APV_NAOD_cfg.py
        FIN=MAOD-00000.root
        FOUT=NAOD-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )
fi

###################### UL17 ######################

if $MAKE_UL17_CFGS ; then
    # UL17 SIM
    (
        CFG_NAME=UL17_SIM_cfg.py
        FIN=GEN-00000.root
        FOUT=SIM-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL17 DIGI
    (
        CFG_NAME=UL17_DIGI_cfg.py
        FIN=SIM-00000.root
        FOUT=DIGI-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL17 HLT
    (
        CFG_NAME=UL17_HLT_cfg.py
        FIN=DIGI-00000.root
        FOUT=HLT-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL17 RECO
    (
        CFG_NAME=UL17_RECO_cfg.py
        FIN=HLT-00000.root
        FOUT=RECO-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL17 MAOD
    (
        CFG_NAME=UL17_MAOD_cfg.py
        FIN=RECO-00000.root
        FOUT=MAOD-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL17 NAOD
    (
        CFG_NAME=UL17_NAOD_cfg.py
        FIN=MAOD-00000.root
        FOUT=NAOD-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )
fi

###################### UL18 ######################

if $MAKE_UL18_CFGS ; then
    # UL18 SIM
    (
        CFG_NAME=UL18_SIM_cfg.py
        FIN=GEN-00000.root
        FOUT=SIM-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL18 DIGI
    (
        CFG_NAME=UL18_DIGI_cfg.py
        FIN=SIM-00000.root
        FOUT=DIGI-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL18 HLT
    (
        CFG_NAME=UL18_HLT_cfg.py
        FIN=DIGI-00000.root
        FOUT=HLT-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL18 RECO
    (
        CFG_NAME=UL18_RECO_cfg.py
        FIN=HLT-00000.root
        FOUT=RECO-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL18 MAOD
    (
        CFG_NAME=UL18_MAOD_cfg.py
        FIN=RECO-00000.root
        FOUT=MAOD-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )

    # UL18 NAOD
    (
        CFG_NAME=UL18_NAOD_cfg.py
        FIN=MAOD-00000.root
        FOUT=NAOD-00000.root
        REL=

        # cfg url:
        # cmsDriver from url:
        printf "\n --- START cfg $CFG_NAME ---\n"
        setup_rel $REL
        printf "\n --- END cfg $CFG_NAME ---\n"
    )
fi
