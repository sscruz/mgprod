#IMPORTANT: The workers that are submitted to this lobster master, MUST come from T3 resources

import datetime
import os
import sys

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, MultiProductionDataset, StorageConfiguration, Workflow

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

events_per_gridpack = 50e3
events_per_lumi = 500

RUN_SETUP = 'lobster_test'
# RUN_SETUP = 'mg_studies'

# Where the gridpacks are located
input_path = "/store/user/"

version = "v1"
out_tag = "tzq_central"

master_label = 'EFT_T3_LHE_{tstamp}'.format(tstamp=timestamp_tag)

if RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/CentralProduction/{tag}/{ver}".format(tag=out_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/CentralProduction/{tag}/{ver}".format(tag=out_tag,ver=version)
    plotdir_path = "~/www/lobster/CentralProduction/{tag}/{ver}".format(tag=out_tag,ver=version)
elif RUN_SETUP == 'lobster_test':
    # For lobster workflow testing
    test_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/tests/{tag}".format(tag=test_tag)
    workdir_path = "/tmpscratch/users/$USER/tests/{tag}".format(tag=test_tag)
    plotdir_path = "~/www/lobster/tests/{tag}".format(tag=test_tag)
else:
    print "Unknown run setup, %s" % (RUN_SETUP)
    raise ValueError

inputs = [
    "hdfs://eddie.crc.nd.edu:19000"  + input_path,
    "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
    "gsiftp://T3_US_NotreDame"       + input_path,
    "srm://T3_US_NotreDame"          + input_path,
]

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

tzq_info = {
    'name': 'tzq_ll_4f_ckm_NLO',
    'location': os.path.join(input_path,"awightma/gridpack_scans/central_gridpacks"),
    'tarball': 'tzq_ll_4f_ckm_NLO_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz',
    'lhe_cfg': 'python_cfgs/central/tzq_ll_4f_ckm_NLO/LHE-00000_1_cfg.py',
    'gen_cfg': 'python_cfgs/central/tzq_ll_4f_ckm_NLO/GEN-00000_1_cfg.py',
    'lhe_release': 'CMSSW_9_3_6',
    'gen_release': 'CMSSW_9_3_6',
}

gridpacks = [
    tzq_info,
]

# Note: The tllq4fMatchedNoSchanW gridpacks seem to require ~2600 MB disk

lhe_resources = Category(
    name='lhe',
    mode='fixed',
    cores=1,
    memory=1200,
    disk=2900
)

gen_resources = Category(
    name='gen',
    mode='fixed',
    cores=1,
    memory=1200,
    disk=2900
)

wf = []

print "Generating workflows:"
for idx,gp_info in enumerate(gridpacks):
    nevents = events_per_gridpack
    name = gp_info['name']
    gp_loc = os.path.join(gp_info['location'],gp_info['tarball'])

    print "[{0}/{1}] Gridpack: {gp} (nevts {events})".format(idx+1,len(gridpacks),gp=name,events=nevents)
    print "\tGridpack: {path}".format(path=gp_loc)

    cmd = ['cmsRun']
    cmd.append(gp_info['lhe_cfg'])
    label = 'lhe_step_{tag}'.format(tag=name)

    print "\tLHE Step: {label}".format(label=label)
    print "\tLHE cfg: {cfg}".format(cfg=gp_info['lhe_cfg'])
    lhe = Workflow(
        label=label,
        command=' '.join(cmd),
        sandbox=cmssw.Sandbox(release=gp_info['lhe_release']),
        merge_size=-1,
        cleanup_input=False,
        globaltag=False,
        outputs=['LHE-00000.root'],
        dataset=MultiProductionDataset(
            gridpacks=gp_loc,
            events_per_gridpack=nevents,
            events_per_lumi=events_per_lumi,
            lumis_per_task=1,
            randomize_seeds=True
        ),
        category=lhe_resources
    )

    cmd = ['cmsRun']
    cmd.append(gp_info['gen_cfg'])
    label = 'gen_step_{tag}'.format(tag=name)

    print "\tGEN Step: {label}".format(label=label)
    print "\tGEN cfg: {cfg}".format(cfg=gp_info['gen_cfg'])
    gen = Workflow(
        label=label,
        command=' '.join(cmd),
        sandbox=cmssw.Sandbox(release=gp_info['gen_release']),
        merge_size=-1,
        cleanup_input=False,
        globaltag=False,
        outputs=['GEN-00000.root'],
        dataset=ParentDataset(
            parent=lhe,
            units_per_task=1
        )
        category=gen_resources
    )

    wf.extend([lhe,gen])

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
