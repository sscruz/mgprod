import datetime
import os
import sys

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, Dataset,ParentDataset, StorageConfiguration, Workflow

sys.path.append(os.getcwd())
from helpers.utils import regex_match

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

username = "awightma"

#RUN_SETUP = 'local'
#RUN_SETUP = 'full_production'
RUN_SETUP = 'mg_studies'

in_ver  = "v1"   # The version index for the INPUT directory
out_ver = "v1"   # The version index for the OUTPUT directory

grp_tag  = "2019_04_19/ttZRunCard"      # For 'local' and 'mg_studies' setups
prod_tag = "Round1/Batch1"              # For 'full_production' setup

# Only run over lhe steps from specific processes/coeffs/runs
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []  # (i.e. MG starting points)

master_label = 'EFT_ALL_postLHE_{tstamp}'.format(tstamp=timestamp_tag)

if RUN_SETUP == 'local':
    # For quick generic lobster workflow testing
    test_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    input_path   = "/store/user/{user}/LHE_step/{tag}/{ver}/".format(user=username,tag=grp_tag,ver=in_ver)
    output_path  = "/store/user/$USER/tests/{tag}".format(tag=test_tag)
    workdir_path = "/tmpscratch/users/$USER/tests/{tag}".format(tag=test_tag)
    plotdir_path = "~/www/lobster/tests/{tag}".format(tag=test_tag)
elif RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    input_path   = "/store/user/{user}/LHE_step/{tag}/{ver}/".format(user=username,tag=grp_tag,ver=in_ver)
    output_path  = "/store/user/$USER/postLHE_step/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/postLHE_step/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/postLHE_step/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
elif RUN_SETUP == 'full_production':
    # For Large MC production
    input_path   = "/store/user/{user}/FullProduction/{tag}/LHE_step/{ver}".format(user=username,tag=prod_tag,ver=in_ver)
    output_path  = "/store/user/$USER/FullProduction/{tag}/postLHE_step/{ver}".format(tag=prod_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/{tag}/postLHE_step/{ver}".format(tag=prod_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/FullProduction/{tag}/postLHE_step/{ver}".format(tag=prod_tag,ver=out_ver)
else:
    print "Unknown run setup, {setup}".format(setup=RUN_SETUP)
    raise ValueError

input_path_full = "/hadoop" + input_path

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
    disable_input_streaming=False,
)

lhe_dirs = []
for fd in os.listdir(input_path_full):
    if fd.find('lhe_step_') < 0:
        continue
    arr = fd.split('_')
    p,c,r = arr[2],arr[3],arr[4]
    if len(regex_match([p],process_whitelist)) == 0:
        continue
    elif len(regex_match([c],coeff_whitelist)) == 0:
        continue
    elif len(regex_match([r],runs_whitelist)) == 0:
        continue
    lhe_dirs.append(fd)


# Old setup
#gs_resources = Category(
#    name='gs',
#    cores=12,
#    memory=22000,
#    disk=22000
#)
#
#digi_resources = Category(
#    name='digi',
#    cores=12,
#    memory=22000,
#    disk=22000,
#    tasks_min=1
#)
#
#reco_resources = Category(
#    name='reco',
#    cores=12,
#    memory=22000,
#    disk=22000,
#    tasks_min=1
#)
#
#maod_resources = Category(
#    name='maod',
#    cores=12,
#    memory=22000,
#    disk=22000,
#    tasks_min=1
#)


#################################################################
# Worker Res.:
#   Cores:  12    | 4
#   Memory: 16000 | 8000
#   Disk:   13000 | 6500
#################################################################
# Need to be careful with using 'runetime' setting, as it can cause us to exceed the workers resources
gs_resources = Category(
    name='gs',
    cores=6,
    memory=3000,
    disk=3000,
    tasks_min=12,
    #runtime=3600,
    mode='fixed'
)

digi_resources = Category(
    name='digi',
    cores=6,
    memory=7000,
    disk=4000,
    #runtime=3600,
    mode='fixed'
)

reco_resources = Category(
    name='reco',
    cores=3,
    memory=3500,
    disk=2000,
    #runtime=3600,
    mode='fixed'
)

maod_resources = Category(
    name='maod',
    cores=2,
    memory=2500,
    disk=2000,
    #runtime=3600,
    mode='fixed'
)
#################################################################

wf_steps = ['gs','digi','reco','maod']
fragment_map = {
    'default': {
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000_1_cfg.py',
        'digi': 'python_cfgs/DR/HIG-RunIIFall17DRPremix-00823_1_cfg.py',
        'reco': 'python_cfgs/DR/HIG-RunIIFall17DRPremix-00823_2_cfg.py',
        'maod': 'python_cfgs/MAOD/HIG-RunIIFall17MiniAOD-00821_1_cfg.py',
    },
    'ttH': {
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-ttH_1_cfg.py',
    },
    'tllq4f': {
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-tllq4f_1_cfg.py',
    },
    'tllq4fNoHiggs': {
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-tllq4f_1_cfg.py',
    },
    'tllq4fMatched': {
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-tllq4f_1_cfg.py',
    },
    'ttHJet': {
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-ttHJets_1_cfg.py'
    },
    'ttlnuJet': {
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-ttlnuJets_1_cfg.py',
    },
    'tllq4fMatchedNoHiggs': {# Uses same fragment as tllq4f
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-tllq4f_1_cfg.py',
    },
    'ttllNuNuJetNoHiggs': {# Uses same fragment as ttlnuJet
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-ttlnuJets_1_cfg.py',
    },
    'tHq4fMatched': {# Uses same fragment as tllq4f
        'gs':   'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-tllq4f_1_cfg.py',

    }

}

wf = []

print "Generating workflows:"
for idx,lhe_dir in enumerate(lhe_dirs):
    print "\t[{0}/{1}] LHE Input: {dir}".format(idx+1,len(lhe_dirs),dir=lhe_dir)
    arr = lhe_dir.split('_')
    p,c,r = arr[2],arr[3],arr[4]

    wf_fragments = {}
    for step in wf_steps:
        if fragment_map.has_key(p) and fragment_map[p].has_key(step):
            wf_fragments[step] = fragment_map[p][step]
        else:
            wf_fragments[step] = fragment_map['default'][step]

    gs = Workflow(
        label='gs_step_{p}_{c}_{r}'.format(p=p,c=c,r=r),
        command='cmsRun {cfg}'.format(wf_fragments['gs']),
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
        label='digi_step_{p}_{c}_{r}'.format(p=p,c=c,r=r),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['gs']),
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
        label='reco_step_{p}_{c}_{r}'.format(p=p,c=c,r=r),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['reco']),
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
        label='mAOD_step_{p}_{c}_{r}'.format(p=p,c=c,r=r),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['maod']),
        sandbox=cmssw.Sandbox(release='CMSSW_9_4_0_patch1'),
        merge_size='512M',
        cleanup_input=True,
        outputs=['HIG-RunIIFall17MiniAOD-00821ND.root'],
        dataset=ParentDataset(
            parent=reco,
            units_per_task=2
        ),
        category=maod_resources
    )

    wf.extend([gs,digi,reco,maod])

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
