#IMPORTANT: The workers that are submitted to this lobster master, MUST come from T3 resources

import datetime
import os

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, MultiProductionDataset, StorageConfiguration, Workflow

input_path      = "/store/user/awightma/gridpack_scans/2018_04_17/"
input_path_full = "/hadoop" + input_path

# For running on gridpacks in a local directory
#input_path_full = "/afs/crc.nd.edu/user/a/awightma/Public/git_repos/mgprod/lobster_workflow/local_gridpacks/"
#input_path      = "/afs/crc.nd.edu/user/a/awightma/Public/git_repos/mgprod/lobster_workflow/local_gridpacks/"

version = "lobster_"+ datetime.datetime.now().strftime('%Y%m%d_%H%M')
output_path  = "/store/user/$USER/tests/"       + version
workdir_path = "/tmpscratch/users/$USER/tests/" + version
plotdir_path = "~/www/lobster/tests/"           + version

#version = "v1"
#grp_tag = "2018_04_17/sans_ttW"
#output_path  = "/store/user/$USER/LHE_step/%s/" % (grp_tag)       + version
#workdir_path = "/tmpscratch/users/$USER/LHE_step/%s/" % (grp_tag) + version
#plotdir_path = "~/www/lobster/LHE_step/%s/" % (grp_tag)           + version

storage = StorageConfiguration(
    input=[
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
        #"file://" + input_path,    # For running on gridpacks in a local directory
    ],
    output=[
        "hdfs://eddie.crc.nd.edu:19000"  + output_path,
        "file:///hadoop"                 + output_path,
        # ND is not in the XrootD redirector, thus hardcode server.
        "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + output_path,
        "srm://T3_US_NotreDame"          + output_path,
    ],
    disable_input_streaming=True,
)

# Only run over gridpacks from specific processes/coeffs/runs (i.e. MG starting points)
process_whitelist = ['ttH','ttZ','tZq']
coeff_whitelist   = []
runs_whitelist    = []
gridpacks = []
for f in os.listdir(input_path_full):
    arr = f.split('_')
    if len(arr) < 3:
        continue
    p,c,r = arr[0],arr[1],arr[2]
    if len(process_whitelist) > 0 and not p in process_whitelist:
        continue
    elif len(coeff_whitelist) > 0 and not c in coeff_whitelist:
        continue
    elif len(runs_whitelist) > 0 and not r in runs_whitelist:
        continue
    gridpacks.append(f)

lhe_resources = Category(
    name='lhe',
    cores=1,
    memory=1500,
    disk=2000
)

events_per_gridpack = 5000
events_per_lumi = 500

fragment_map = {
    'default': {
        'lhe': 'fragments/HIG-RunIIFall17wmLHE-00000_1_cfg.py',
    },
}

wf = []

print "Generating workflows:"
for idx,gridpack in enumerate(gridpacks):
    print "\t[%d/%d] Gridpack: %s" % (idx+1,len(gridpacks),gridpack)
    arr = gridpack.split('_')
    p,c,r = arr[0],arr[1],arr[2]

    lhe_fragment = fragment_map['default']['lhe']
    if fragment_map.has_key(p):
        lhe_fragment = fragment_map[p]['lhe']

    lhe = Workflow(
        label='lhe_step_%s_%s_%s' % (p,c,r),
        command='cmsRun %s' % (lhe_fragment),
        sandbox=cmssw.Sandbox(release='CMSSW_9_3_1'),
        merge_size=-1,  # Don't merge the output files, to keep individuals as small as possible
        cleanup_input=False,
        globaltag=False,
        outputs=['HIG-RunIIFall17wmLHE-00000ND.root'],
        dataset=MultiProductionDataset(
            gridpacks=gridpack,
            events_per_gridpack=events_per_gridpack,
            events_per_lumi=events_per_lumi,
            lumis_per_task=1,
            randomize_seeds=True
        ),
        category=lhe_resources
    )
    wf.extend([lhe])

config = Config(
    label='EFT_LHE',
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
