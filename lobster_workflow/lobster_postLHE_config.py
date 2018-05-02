import datetime
import os

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, Dataset,ParentDataset, StorageConfiguration, Workflow

input_path_full = "/hadoop/store/user/awightma/LHE_step/2018_04_17/500k_events/v2/"
input_path      = "/store/user/awightma/LHE_step/2018_04_17/500k_events/v2/"

version = "lobster_"+ datetime.datetime.now().strftime('%Y%m%d_%H%M')
output_path  = "/store/user/$USER/tests/"       + version
workdir_path = "/tmpscratch/users/$USER/tests/" + version
plotdir_path = "~/www/lobster/tests/"           + version

#version = "v1"
#output_path  = "/store/user/$USER/postLHE_step/2018_04_17/500k_events/"       + version
#workdir_path = "/tmpscratch/users/$USER/postLHE_step/2018_04_17/500k_events/" + version
#plotdir_path = "~/www/lobster/postLHE_step/2018_04_17/500k_events/"           + version

storage = StorageConfiguration(
    input=[
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
    ],
    output=[
        "hdfs://eddie.crc.nd.edu:19000"  + output_path,
        "file:///hadoop"                 + output_path,
        # ND is not in the XrootD redirector, thus hardcode server.
        "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + output_path,
        "srm://T3_US_NotreDame"          + output_path,
    ],
    disable_input_streaming=False,
)

# Only run over lhe steps from specific processes/coeffs/runs (i.e. MG starting points)
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []
lhe_dirs = []
for fd in os.listdir(input_path_full):
    if fd.find('lhe_step_') < 0:
        continue
    arr = fd.split('_')
    p,c,r = arr[2],arr[3],arr[4]
    if len(process_whitelist) > 0 and not p in process_whitelist:
        continue
    elif len(coeff_whitelist) > 0 and not c in coeff_whitelist:
        continue
    elif len(runs_whitelist) > 0 and not r in runs_whitelist:
        continue
    lhe_dirs.append(fd)

gs_resources = Category(
    name='gs',
    cores=12,
    memory=22000,
    disk=22000,
)

digi_resources = Category(
    name='digi',
    cores=12,
    memory=22000,
    disk=22000,
    tasks_min=1
)

reco_resources = Category(
    name='reco',
    cores=12,
    memory=22000,
    disk=22000,
    tasks_min=1
)

maod_resources = Category(
    name='maod',
    cores=12,
    memory=22000,
    disk=22000,
    tasks_min=1
)

fragment_map = {
    'default': {
        'gs':   'fragments/HIG-RunIIFall17wmGS-00000_1_cfg.py',
        'digi': 'fragments/HIG-RunIIFall17DRPremix-00823_1_cfg.py',
        'reco': 'fragments/HIG-RunIIFall17DRPremix-00823_2_cfg.py',
        'maod': 'fragments/HIG-RunIIFall17MiniAOD-00821_1_cfg.py',
    },
    'ttH': {
        'gs':   'fragments/HIG-RunIIFall17wmGS-00000-ttH_1_cfg.py',
        'digi': 'fragments/HIG-RunIIFall17DRPremix-00823_1_cfg.py',
        'reco': 'fragments/HIG-RunIIFall17DRPremix-00823_2_cfg.py',
        'maod': 'fragments/HIG-RunIIFall17MiniAOD-00821_1_cfg.py',
    }
}

wf = []

print "Generating workflows:"
for idx,lhe_dir in enumerate(lhe_dirs):
    print "\t[%d/%d] LHE Input: %s" % (idx+1,len(lhe_dirs),lhe_dir)
    arr = lhe_dir.split('_')
    p,c,r = arr[2],arr[3],arr[4]

    gs_fragment   = fragment_map['default']['gs']
    digi_fragment = fragment_map['default']['digi']
    reco_fragment = fragment_map['default']['reco']
    maod_fragment = fragment_map['default']['maod']
    if fragment_map.has_key(p):
        gs_fragment   = fragment_map[p]['gs']
        digi_fragment = fragment_map[p]['digi']
        reco_fragment = fragment_map[p]['reco']
        maod_fragment = fragment_map[p]['maod']

    gs = Workflow(
        label='gs_step_%s_%s_%s' % (p,c,r),
        command='cmsRun %s' % (gs_fragment),
        sandbox=cmssw.Sandbox(release='CMSSW_9_3_1'),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=False,
        globaltag=False,
        outputs=['HIG-RunIIFall17wmLHEGS-00040ND.root'],
        dataset=Dataset(
            files=lhe_dir,
            files_per_task=1,
            patterns=["*.root"]
        ),
        category=gs_resources
    )

    digi = Workflow(
        label='digi_step_%s_%s_%s' % (p,c,r),
        command='cmsRun %s' (digi_fragment),
        sandbox=cmssw.Sandbox(release='CMSSW_9_4_0_patch1'),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=False,    # Save the GEN-SIM step
        outputs=['HIG-RunIIFall17DRPremix-00823ND_step1.root'],
        dataset=ParentDataset(
            parent=gs,
            units_per_task=1
        ),
        category=digi_resources
    )

    reco = Workflow(
        label='reco_step_%s_%s_%s' % (p,c,r),
        command='cmsRun %s' % (reco_fragment),
        sandbox=cmssw.Sandbox(release='CMSSW_9_4_0_patch1'),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=True,
        outputs=['HIG-RunIIFall17DRPremix-00823ND.root'],
        dataset=ParentDataset(
            parent=digi,
            units_per_task=1
        ),
        category=reco_resources
    )

    maod = Workflow(
        label='mAOD_step_%s_%s_%s' % (p,c,r),
        command='cmsRun %s' % (maod_fragment),
        sandbox=cmssw.Sandbox(release='CMSSW_9_4_0_patch1'),
        merge_size='512M',
        cleanup_input=True,
        outputs=['HIG-RunIIFall17MiniAOD-00821ND.root'],
        dataset=ParentDataset(
            parent=reco,
            units_per_task=5
        ),
        category=maod_resources
    )

    wf.extend([gs,digi,reco,maod])

config = Config(
    label='EFT_postLHE',
    workdir=workdir_path,
    plotdir=plotdir_path,
    storage=storage,
    workflows=wf,
    advanced=AdvancedOptions(
        bad_exit_codes=[127, 160],
        log_level=1,
        payload=10
    )
)
