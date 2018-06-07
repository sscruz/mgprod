#IMPORTANT: The workers that are submitted to this lobster master, MUST come from T3 resources

import datetime
import os

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, MultiProductionDataset, StorageConfiguration, Workflow

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

events_per_gridpack = 50000
events_per_lumi = 500

#RUN_SETUP = 'local'
#RUN_SETUP = 'full_production'
RUN_SETUP = 'mg_studies'

# Where the gridpacks are located
input_path      = "/store/user/awightma/gridpack_scans/2018_05_06/"
input_path_full = "/hadoop" + input_path

version = "v1"
grp_tag = "2018_05_06/2HeavyScan1dim"
production_tag = "Round1/Batch1"

# Only run over gridpacks from specific processes/coeffs/runs
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []    # (i.e. MG starting points)

#master_label = 'EFT_LHE_%s' % (timestamp_tag)
master_label = 'EFT_T3_LHE_%s' % (timestamp_tag)

if RUN_SETUP == 'local':
    # Overwrite the input path to point to a local AFS file directory with the desired gridpacks
    input_path      = "/afs/crc.nd.edu/user/a/awightma/Public/git_repos/mgprod/lobster_workflow/local_gridpacks/"
    input_path_full = input_path

    version = "lobster_" + timestamp_tag
    output_path  = "/store/user/$USER/tests/"       + version
    workdir_path = "/tmpscratch/users/$USER/tests/" + version
    plotdir_path = "~/www/lobster/tests/"           + version

    storage = StorageConfiguration(
        input=[
            "file://" + input_path,    # For running on gridpacks in a local directory
        ],
        output=[
            "hdfs://eddie.crc.nd.edu:19000"  + output_path,
            # ND is not in the XrootD redirector, thus hardcode server.
            "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
            "gsiftp://T3_US_NotreDame"       + output_path,
            "srm://T3_US_NotreDame"          + output_path,
            "file:///hadoop"                 + output_path,
        ],
        disable_input_streaming=True,
    )
elif RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/LHE_step/%s/" % (grp_tag)       + version
    workdir_path = "/tmpscratch/users/$USER/LHE_step/%s/" % (grp_tag) + version
    plotdir_path = "~/www/lobster/LHE_step/%s/" % (grp_tag)           + version

    storage = StorageConfiguration(
        input=[
            "hdfs://eddie.crc.nd.edu:19000"  + input_path,
            "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
            "gsiftp://T3_US_NotreDame"       + input_path,
            "srm://T3_US_NotreDame"          + input_path,
        ],
        output=[
            "hdfs://eddie.crc.nd.edu:19000"  + output_path,
            # ND is not in the XrootD redirector, thus hardcode server.
            "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
            "gsiftp://T3_US_NotreDame"       + output_path,
            "srm://T3_US_NotreDame"          + output_path,
            "file:///hadoop"                 + output_path,
        ],
        disable_input_streaming=True,
    )
elif RUN_SETUP == 'full_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/%s/LHE_step/%s" % (production_tag,version)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/%s/LHE_step/%s" % (production_tag,version)
    plotdir_path = "~/www/lobster/FullProduction/%s/LHE_step/%s" % (production_tag,version)

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
            # ND is not in the XrootD redirector, thus hardcode server.
            "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
            "gsiftp://T3_US_NotreDame"       + output_path,
            "srm://T3_US_NotreDame"          + output_path,
            "file:///hadoop"                 + output_path,
        ],
        disable_input_streaming=True,
    )
else:
    print "Unknown run setup, %s" % (RUN_SETUP)
    raise ValueError

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
    memory=1200,
    disk=1000
)

wf_steps = ['lhe']
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

    wf_fragments = {}
    for step in wf_steps:
        if fragment_map.has_key(p) and fragment_map[p].has_key(step):
            wf_fragments[step] = fragment_map[p][step]
        else:
            wf_fragments[step] = fragment_map['default'][step]

    lhe = Workflow(
        label='lhe_step_%s_%s_%s' % (p,c,r),
        #command='cmsRun %s' % (lhe_fragment),
        command='cmsRun %s' % (wf_fragments['lhe']),
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
    label=master_label,
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
