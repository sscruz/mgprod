import datetime
import os
import sys
import shutil

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, Dataset,ParentDataset, StorageConfiguration, Workflow

sys.path.append(os.getcwd())
from helpers.utils import regex_match

MODIFIED_CFG_DIR = "python_cfgs/modified"

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

username = "awightma"

#RUN_SETUP = 'local'
#RUN_SETUP = 'full_production'
RUN_SETUP = 'mg_studies'

in_ver  = "v1"   # The version index for the INPUT directory
out_ver = "v1"   # The version index for the OUTPUT directory

grp_tag  = "2019_04_19/ttZRunCard"   # For 'local' and 'mg_studies' setups
out_tag  = "2019_04_19/ttZRunCard"
prod_tag = "Round1/Batch1"            # For 'full_production' setup

# Only run over lhe steps from specific processes/coeffs/runs
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []  # (i.e. MG starting points)

master_label = 'EFT_ALL_genOnly_{tstamp}'.format(tstamp=timestamp_tag)

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
    output_path  = "/store/user/$USER/genOnly_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/genOnly_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/genOnly_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
elif RUN_SETUP == 'full_production':
    # For Large MC production
    input_path   = "/store/user/{user}/FullProduction/{tag}/{ver}".format(user=username,tag=prod_tag,ver=in_ver)
    output_path  = "/store/user/$USER/genOnly_step/FP/{tag}/{ver}".format(tag=prod_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/genOnly_step/FP/{tag}/{ver}".format(tag=prod_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/genOnly_step/FP/{tag}/{ver}".format(tag=prod_tag,ver=out_ver)
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


#################################################################
# Worker Res.:
#   Cores:  12    | 4
#   Memory: 16000 | 8000
#   Disk:   13000 | 6500
#################################################################
# Need to be careful with using 'runetime' setting, as it can cause us to exceed the workers resources
gen_resources = Category(
    name='gen',
    cores=1,
    memory=1200,
    disk=1000,
    tasks_min=12,
    tasks_max=3000,
    mode='fixed'
)
#################################################################

wf_steps = ['gen']
fragment_map = {
    'default': {
        'gen': 'python_cfgs/GEN/GEN-00000_1_cfg.py',
    },
    'ttH': {
        'gen': 'python_cfgs/GEN/GEN-00000-ttH_1_cfg.py',
    },
    'ttHJet': {
        'gen': 'python_cfgs/GEN/GEN-00000-ttHJets_1_cfg.py',
    },
    'ttlnuJet': {
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttllNuNuJetNoHiggs': {# Uses same fragment as ttlnuJet
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'tllq4f': {
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tllq4fNoHiggs': {
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tllq4fMatched': {
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tllq4fMatchedNoHiggs': {# Uses same fragment as tllq4f
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tHq4fMatched': {# Uses same fragment as tllq4f
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    }
}

wf = []

print "Generating workflows:"
for idx,lhe_dir in enumerate(lhe_dirs):
    print "\t[{n}/{tot}] LHE Input: {dir}".format(n=idx+1,tot=len(lhe_dirs),dir=lhe_dir)
    arr = lhe_dir.split('_')
    p,c,r = arr[2],arr[3],arr[4]

    wf_fragments = {}
    for step in wf_steps:
        #if fragment_map.has_key(p) and fragment_map[p].has_key(step):
        #    wf_fragments[step] = fragment_map[p][step]
        #else:
        #    wf_fragments[step] = fragment_map['default'][step]
        if fragment_map.has_key(p) and fragment_map[p].has_key(step):
            template_loc = fragment_map[p][step]
        else:
            template_loc = fragment_map['default'][step]
        head,tail = os.path.split(template_loc)
        # This should be a unique identifier within a single lobster master to ensure we dont overwrite a cfg file to early
        mod_tag = 'idx{0}'.format(idx)
        tail = tail.replace("cfg.py","{tag}_cfg.py".format(tag=mod_tag)
        mod_loc = os.path.join(MODIFIED_CFG_DIR,tail)
        shutil.copy(template_loc,mod_loc)

        wf_fragments[step] = mod_loc
    gen = Workflow(
        label='gen_step_{p}_{c}_{r}'.format(p=p,c=c,r=r),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['gen']),
        sandbox=cmssw.Sandbox(release='CMSSW_9_3_1'),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=False,
        globaltag=False,
        outputs=['GEN-00000.root'],
        dataset=Dataset(
            files=lhe_dir,
            files_per_task=10,
            patterns=["*.root"]
        ),
        category=gen_resources
    )

    wf.extend([gen])

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
