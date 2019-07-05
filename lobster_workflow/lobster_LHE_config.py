#IMPORTANT: The workers that are submitted to this lobster master, MUST come from T3 resources

import datetime
import os
import sys

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, MultiProductionDataset, StorageConfiguration, Workflow

#sys.path.append(os.getcwd())
sys.path.append('/afs/crc.nd.edu/user/a/awightma/Public/git_repos/mgprod/lobster_workflow')
from helpers.utils import regex_match

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

events_per_gridpack = 50e3
events_per_lumi = 500

#RUN_SETUP = 'local'
#RUN_SETUP = 'full_production'
RUN_SETUP = 'mg_studies'
#RUN_SETUP = 'lobster_test'

# Where the gridpacks are located
input_path      = "/store/user/awightma/gridpack_scans/2019_04_19/"
input_path_full = "/hadoop" + input_path

version = "v1"
grp_tag = "2019_04_19/ttlnu-TestExample"
prod_tag = "Round4/Batch5"

# Only run over gridpacks from specific processes/coeffs/runs
process_whitelist = ['^ttlnu$']
coeff_whitelist   = ['^NoDim6$']
runs_whitelist    = ['^run0$']    # (i.e. MG starting points)

master_label = 'EFT_LHE_%s' % (timestamp_tag)
#master_label = 'EFT_T3_LHE_%s' % (timestamp_tag)

if RUN_SETUP == 'local':
    # Overwrite the input path to point to a local AFS file directory with the desired gridpacks
    input_path      = "/afs/crc.nd.edu/user/a/awightma/Public/git_repos/mgprod/lobster_workflow/local_gridpacks/"
    input_path_full = input_path
    test_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/tests/{tag}".format(tag=test_tag)
    workdir_path = "/tmpscratch/users/$USER/tests/{tag}".format(tag=test_tag)
    plotdir_path = "~/www/lobster/tests/{tag}".format(tag=test_tag)
    inputs = [
        "file://" + input_path,    # For running on gridpacks in a local directory
    ]
elif RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    plotdir_path = "~/www/lobster/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    inputs = [
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
    ]
elif RUN_SETUP == 'full_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/{tag}/LHE_step/{ver}".format(tag=prod_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/{tag}/LHE_step/{ver}".format(tag=prod_tag,ver=version)
    plotdir_path = "~/www/lobster/FullProduction/{tag}/LHE_step/{ver}".format(tag=prod_tag,ver=version)
    inputs = [
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
        #"file://" + input_path,    # For running on gridpacks in a local directory
    ]
elif RUN_SETUP == 'lobster_test':
    # For lobster workflow tests
    grp_tag = "lobster_{tstamp}".format(timestamp_tag)
    output_path  = "/store/user/$USER/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    plotdir_path = "~/www/lobster/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    inputs = [
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
    ]
else:
    print "Unknown run setup, %s" % (RUN_SETUP)
    raise ValueError

storage = StorageConfiguration(
    input=inputs,
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

gridpacks = []
for f in os.listdir(input_path_full):
    arr = f.split('_')
    if len(arr) < 3:
        continue
    p,c,r = arr[0],arr[1],arr[2]
    if len(regex_match([p],process_whitelist)) == 0:
        continue
    elif len(regex_match([c],coeff_whitelist)) == 0:
        continue
    elif len(regex_match([r],runs_whitelist)) == 0:
        continue
    gridpacks.append(f)

lhe_resources = Category(
    name='lhe',
    cores=1,
    memory=1200,
    disk=1000,
    tasks_min=12
)

wf_steps = ['lhe']
fragment_map = {
    'default': {
        'lhe': 'python_cfgs/LHE/HIG-RunIIFall17wmLHE-00000_1_cfg.py',
    },
}

event_multiplier = {
    'default': 1,
    'ttHJet': 4,
    'ttlnuJet': 2,
    'tHq4fMatched': 1.2,
    'tllq4fMatchedNoHiggs': 1.2,
    'ttllNuNuJetNoHiggs': 4
}

wf = []

print "Generating workflows:"
for idx,gridpack in enumerate(gridpacks):
    arr = gridpack.split('_')
    p,c,r = arr[0],arr[1],arr[2]
    c = c.replace('-','')   # Lobster doesn't like labels with dashes in them
    wf_fragments = {}
    for step in wf_steps:
        if fragment_map.has_key(p) and fragment_map[p].has_key(step):
            wf_fragments[step] = fragment_map[p][step]
        else:
            wf_fragments[step] = fragment_map['default'][step]
    multiplier = event_multiplier['default']
    if event_multiplier.has_key(p):
        multiplier = event_multiplier[p]
    nevents = int(multiplier*events_per_gridpack)
    print "\t[{0}/{1}] Gridpack: {gp} (nevts {events})".format(idx+1,len(gridpacks),gp=gridpack,events=nevents)
    lhe = Workflow(
        label='lhe_step_{p}_{c}_{r}'.format(p=p,c=c,r=r),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['lhe']),
        sandbox=cmssw.Sandbox(release='CMSSW_9_3_1'),
        merge_size=-1,  # Don't merge the output files, to keep individuals as small as possible
        cleanup_input=False,
        globaltag=False,
        outputs=['HIG-RunIIFall17wmLHE-00000ND.root'],
        dataset=MultiProductionDataset(
            gridpacks=gridpack,
            events_per_gridpack=nevents,
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
        payload=10,
        xrootd_servers=['ndcms.crc.nd.edu',
                       'cmsxrootd.fnal.gov',
                       'deepthought.crc.nd.edu']
    )
)
