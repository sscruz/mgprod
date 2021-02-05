jobs=[
    # dict(
    #     name='ttHJets',
    #     process="ttHJets",
    #     nChunks=400,
    #     nEventsPerChunk=500,
    #     productionTag="EFT_Trees_jan8_newgridpacks_morestats_2",
    #     gridpack="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/gridpacks//ttHJet_ProductionWith4QuarkOps_run0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
    #     output="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/{tag}/LHE_GEN/{process}_chunk{chunk}.root",
    #     cfg="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/python_cfgs/LHE_GEN/HIG-RunIISummer19UL17wmLHEGEN-00538_1_cfg_forSubmission.py",
    # ),
    dict(
        name='ttlnuJet',
        process="ttlnuJet",
        nChunks=400,
        nEventsPerChunk=500,
        productionTag="EFT_Trees_jan8_newgridpacks_morestats_2",
        gridpack="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/gridpacks//ttlnuJet_ProductionWith4QuarkOps_2_run0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
        output="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/{tag}/LHE_GEN/{process}_chunk{chunk}.root",
        cfg="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/python_cfgs/LHE_GEN/HIG-RunIISummer19UL17wmLHEGEN-00538_1_cfg_forSubmission.py",
    ),
    dict(
        name='ttllNuNuJet',
        process="ttllNuNuJet",
        nChunks=400,
        nEventsPerChunk=500,
        productionTag="EFT_Trees_jan8_newgridpacks_morestats_2",
        gridpack="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/gridpacks//ttllNuNuJetNoHiggs_ProductionWith4QuarkOps_3_run0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
        output="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/{tag}/LHE_GEN/{process}_chunk{chunk}.root",
        cfg="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/python_cfgs/LHE_GEN/HIG-RunIISummer19UL17wmLHEGEN-00538_1_cfg_forSubmission.py",
    ),
    # dict(
    #     name='ttbar',
    #     process="ttbar",
    #     nChunks=400,
    #     nEventsPerChunk=500,
    #     productionTag="EFT_Trees_jan8_newgridpacks_morestats_2",
    #     gridpack="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/gridpacks//ttbar_ProductionWith4QuarkOps_3_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
    #     output="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/{tag}/LHE_GEN/{process}_chunk{chunk}.root",
    #     cfg="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/python_cfgs/LHE_GEN/HIG-RunIISummer19UL17wmLHEGEN-00538_tHq_1_cfg_forSubmission.py"
    # ),
    # dict(
    #     name='tHq_matched',
    #     process="tHq_matched",
    #     nChunks=400,
    #     nEventsPerChunk=500,
    #     productionTag="EFT_Trees_jan8_newgridpacks_morestats_2",
    #     gridpack="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/gridpacks//tHq4fMatched_ProductionWith4QuarkOps_7_run0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
    #     output="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/{tag}/LHE_GEN/{process}_chunk{chunk}.root",
    #     cfg="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/python_cfgs/LHE_GEN/HIG-RunIISummer19UL17wmLHEGEN-00538_tHq_1_cfg_forSubmission.py"
    # ),
    # dict(
    #      name='tZq_matched',
    #      process="tZq_matched",
    #      nChunks=400,
    #      nEventsPerChunk=500,
    #      productionTag="EFT_Trees_jan8_newgridpacks_morestats_2",
    #      gridpack="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/gridpacks//tllq4fNoSchanWNoHiggs0p_ProductionWith4QuarkOps_5_run0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
    #      output="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/{tag}/LHE_GEN/{process}_chunk{chunk}.root",
    #      cfg="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/python_cfgs/LHE_GEN/HIG-RunIISummer19UL17wmLHEGEN-00538_tHq_1_cfg_forSubmission.py"
    # ),
    ]

for job in jobs:
    template='sbatch  -p wn --wrap "bash lxbatch_runner.sh /work/sesanche/EFT_analysis/mgprod/slurm_workflow/sandbox/CMSSW_10_6_18/src/ /scratch/sesanche/{tag}_{{process}}_{{chunk}} {output} cmsRun {cfg} maxEvents={nEventsPerChunk}  inputFiles={gridpack} iChunk={{chunk}} "'.format(output=job['output'],nEventsPerChunk=job['nEventsPerChunk'],tag=job['productionTag'],gridpack=job['gridpack'], cfg=job['cfg'])
    
    for i in range(job['nChunks']):
        print template.format(chunk=i,process=job['process'],tag=job['productionTag'])
