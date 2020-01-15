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

#events_per_gridpack = 10e6
#events_per_gridpack = 3e6
#events_per_gridpack = 5e6
events_per_gridpack = 100e3
#events_per_gridpack = 500e3
events_per_lumi = 500

#RUN_SETUP = 'local'
#RUN_SETUP = 'full_production'
RUN_SETUP = 'mg_studies'
#RUN_SETUP = 'lobster_test'

# Where the gridpacks are located
#input_path      = "/store/user/awightma/gridpack_scans/2019_04_19/"
#input_path      = "/store/user/kmohrman/gridpack_scans/2019_04_19/"
#input_path_full = "/hadoop" + input_path

version = "v1"
grp_tag = "2019_04_19/ttHJet_HanV4xqcutTests" # Out tag for mg_studies
prod_tag = "Round6/Batch9"

# Only run over gridpacks from specific processes/coeffs/runs
#process_whitelist = ['^ttlnu$']
#coeff_whitelist   = ['^NoDim6$']
#runs_whitelist    = ['^run0$']    # (i.e. MG starting points)
#process_whitelist = ['^ttllNuNuNoHiggs$','^ttH$','^ttlnu$']
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []    # (i.e. MG starting points)

master_label = 'EFT_T3_{tstamp}'.format(tstamp=timestamp_tag)

#if RUN_SETUP == 'local':
#    # Overwrite the input path to point to a local AFS file directory with the desired gridpacks
#    input_path      = "/afs/crc.nd.edu/user/a/awightma/Public/git_repos/mgprod/lobster_workflow/local_gridpacks/"
#    input_path_full = input_path
#    test_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
#    output_path  = "/store/user/$USER/tests/{tag}".format(tag=test_tag)
#    workdir_path = "/tmpscratch/users/$USER/tests/{tag}".format(tag=test_tag)
#    plotdir_path = "~/www/lobster/tests/{tag}".format(tag=test_tag)
#    inputs = [
#        "file://" + input_path,    # For running on gridpacks in a local directory
#    ]
#elif RUN_SETUP == 'mg_studies':
if RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    plotdir_path = "~/www/lobster/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    #inputs = [
    #    "hdfs://eddie.crc.nd.edu:19000"  + input_path,
    #    "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
    #    "gsiftp://T3_US_NotreDame"       + input_path,
    #    "srm://T3_US_NotreDame"          + input_path,
    #]
elif RUN_SETUP == 'full_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/{tag}/LHE_step/{ver}".format(tag=prod_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/{tag}/LHE_step/{ver}".format(tag=prod_tag,ver=version)
    plotdir_path = "~/www/lobster/FullProduction/{tag}/LHE_step/{ver}".format(tag=prod_tag,ver=version)
    #inputs = [
    #    "hdfs://eddie.crc.nd.edu:19000"  + input_path,
    #    "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
    #    "gsiftp://T3_US_NotreDame"       + input_path,
    #    "srm://T3_US_NotreDame"          + input_path,
    #    #"file://" + input_path,    # For running on gridpacks in a local directory
    #]
elif RUN_SETUP == 'lobster_test':
    # For lobster workflow tests
    grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    plotdir_path = "~/www/lobster/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    #inputs = [
    #    "hdfs://eddie.crc.nd.edu:19000"  + input_path,
    #    "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
    #    "gsiftp://T3_US_NotreDame"       + input_path,
    #    "srm://T3_US_NotreDame"          + input_path,
    #]
else:
    print "Unknown run setup, %s" % (RUN_SETUP)
    raise ValueError

input_path = "/store/user/"
input_path_full = "/hadoop" + input_path

storage = StorageConfiguration(
    #input=inputs,
    input = [
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
    ],
    output=[
        "hdfs://eddie.crc.nd.edu:19000"  + output_path,
         #ND is not in the XrootD redirector, thus hardcode server.
        "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + output_path,
        "srm://T3_US_NotreDame"          + output_path,
        "file:///hadoop"                 + output_path,
    ],
    disable_input_streaming=True,
)

gridpack_list = [
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXJetStartPtChecks_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # FP R5 start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXJetStartPtChecks_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", #FP (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttlnuJet_HanV4ttXJetStartPtChecks_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", #FP
    #"kmohrman/gridpack_scans/2019_04_19/ttllNuNuJetNoHiggs_HanV4ttXJetStartPtChecks_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", #FP
    #"kmohrman/gridpack_scans/2019_04_19/tHq4f_HanV4tHqStartPtChecks_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tHq4f_HanV4tHqStartPtChecks_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tHq4f_HanV4tHqStartPtChecks_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tHq4f_HanV4tHqStartPtChecks_run3_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"awightma/gridpack_scans/2019_04_19/tllq4fNoSchanWNoHiggs0p_HanV4Model16DttllScanpointsXQCUT0_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", #FP
    #"kmohrman/gridpack_scans/2019_04_19/tllq4fNoSchanWNoHiggs0p_HanV4tZqStartPtCheck_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tllq4fNoSchanWNoHiggs0p_HanV4tZqStartPtCheck_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tllq4fNoSchanWNoHiggs0p_HanV4tZqStartPtCheck_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tllq4fNoSchanWNoHiggs0p_HanV4tZqStartPtCheck_run3_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tHq4f_HanV4tXqSMCheck_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/tllq4fNoSchanWNoHiggs0p_HanV4tXqSMCheck_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXSMCheck_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/ttllNuNuJetNoHiggs_HanV4ttXSMCheck_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/ttlnuJet_HanV4ttXSMCheck_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"awightma/gridpack_scans/2019_04_19/ttllNuNuJetNoHiggs_HanModelNoDim6_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"awightma/gridpack_scans/2019_04_19/ttHJet_HanModelNoDim6_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"awightma/gridpack_scans/2019_04_19/ttlnuJet_HanModelNoDim6_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    "kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXjetxqcut5_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    "kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXjetxqcut10_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    "kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXjetxqcut15_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
]

#gridpacks = []
##for f in os.listdir(input_path_full):
#for gp_dir in gridpack_list:
#    path_to_gp, gp = os.path.split(gp_dir)
#    #arr = f.split('_')
#    arr = gp.split('_')
#    if len(arr) < 3:
#        continue
#    p,c,r = arr[0],arr[1],arr[2]
#    if len(regex_match([p],process_whitelist)) == 0:
#        continue
#    elif len(regex_match([c],coeff_whitelist)) == 0:
#        continue
#    elif len(regex_match([r],runs_whitelist)) == 0:
#        continue
#    #gridpacks.append(f)
#    gridpacks.append(gp)

# Note: The tllq4fMatchedNoSchanW gridpacks seem to require ~2600 MB disk

#lhe_resources = Category(
#    name='lhe',
#    mode='fixed',
#    cores=1,
#    memory=1200,
#    disk=2900
#)

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

cat_dict = {}

wf = []

print "Generating workflows:"
#for idx,gridpack in enumerate(gridpacks):
for idx,gridpack in enumerate(gridpack_list):
    #arr = gridpack.split('_')
    head,tail = os.path.split(gridpack)
    arr = tail.split('_')
    p,c,r = arr[0],arr[1],arr[2]
    c = c.replace('-','')   # Lobster doesn't like labels with dashes in them

    label='lhe_step_{p}_{c}_{r}'.format(p=p,c=c,r=r)
    cat_name = 'lhe_{p}'.format(p=p)
    if not cat_name in cat_dict:
        cat_dict[cat_name] = Category(
            name=cat_name,
            #mode='fixed',
            cores=1,
            memory=1200,
            disk=2900
        )
    cat = cat_dict[cat_name]

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
    #print "\t[{0}/{1}] Gridpack: {gp} (nevts {events})".format(idx+1,len(gridpacks),gp=gridpack,events=nevents)
    print "\t[{0}/{1}] Gridpack: {gp} (nevts {events})".format(idx+1,len(gridpack_list),gp=gridpack,events=nevents)
    lhe = Workflow(
        #label='lhe_step_{p}_{c}_{r}'.format(p=p,c=c,r=r),
        label=label,
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
        #category=lhe_resources
        category=cat
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
