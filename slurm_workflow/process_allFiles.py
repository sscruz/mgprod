import os 
path="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/EFT_Trees_feb4_tocheckdecays/LHE_GEN/"
outpath="/pnfs/psi.ch/cms/trivcat/store/user/sesanche/EFT/EFT_Trees_feb4_tocheckdecays/histos/"
jobname="histos"
cfg="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/sandbox2/CMSSW_10_6_18/src/EFTGenReader/GenReader/test/EFTGenHistsWithCuts_slurmized_cfg.py"
sandbox="/work/sesanche/EFT_analysis/mgprod/slurm_workflow/sandbox2/CMSSW_10_6_18/src/"
scratch="/scratch/sesanche/{jobname}_{file}/"

for fil in os.listdir(path):
    thescratch = scratch.format(jobname=jobname, file=fil)
    if '_LHE.root' in fil: continue
    if '.root' not in fil: continue
    print "sbatch  -p wn lxbatch_runner.sh {sandbox} {scratch} {outpath}/{fil} cmsRun {cfg} inputFiles=file:{path}/{fil}".format(sandbox=sandbox, scratch=thescratch, outpath=outpath, fil=fil, cfg=cfg, path=path)
