###########################################################################################
################### This script is not done yet!!! Do not use it yet!!! ###################
###########################################################################################

import datetime
import os
import sys
import shutil

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, Dataset,ParentDataset, StorageConfiguration, Workflow

sys.path.append(os.getcwd())
from helpers.utils import regex_match, run_process

MODIFIED_CFG_DIR = "python_cfgs/modified"

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

input_path = "/store/user/"
input_path_full = "/hadoop" + input_path

#RUN_SETUP = 'full_production'
#RUN_SETUP = 'mg_studies'
RUN_SETUP = 'testing'

UL_YEAR = 'UL16'
#UL_YEAR = 'UL16APV'
#UL_YEAR = 'UL17'
#UL_YEAR = 'UL18'

# Note: The workflows in each of the input directories should all be uniquely named w.r.t each other
input_dirs = [
    os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttXJetTests-HanV4Model-xqcut10/v1")
]

out_ver = "v1"   # The version index for the OUTPUT directory

#out_tag = "Round6/Batch9"                               # For 'full_production' setup
out_tag = "2019_04_19/TEST"

# Only run over lhe steps from specific processes/coeffs/runs
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []  # (i.e. MG starting points)

master_label = 'EFT_ALL_postLHE_{tstamp}'.format(tstamp=timestamp_tag)

if RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
elif RUN_SETUP == 'full_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/{tag}/postLHE_step/{ver}".format(tag=out_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/{tag}/postLHE_step/{ver}".format(tag=out_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/FullProduction/{tag}/postLHE_step/{ver}".format(tag=out_tag,ver=out_ver)
elif RUN_SETUP == 'testing':
    grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
else:
    print "Unknown run setup, {setup}".format(setup=RUN_SETUP)
    raise ValueError

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
for path in input_dirs:
    for fd in os.listdir(path):
        print ("FD!!!",fd)
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
        relpath = os.path.relpath(path,input_path_full)
        lhe_dirs.append(os.path.join(relpath,fd))

lhe_dirs = [
    "kmohrman/LHE_step/FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprod-HanV4/v1/lhe_step_tHq4f_testOldGenprodHanV4_run2"
]

#################################################################
# Worker Res.:
#   Cores:  12    | 4
#   Memory: 16000 | 8000
#   Disk:   13000 | 6500
#################################################################
# Need to be careful with using 'runtime' setting, as it can cause us to exceed the workers resources

gen_resources = Category(
    name='gen',
    cores=1,
    memory=1200,
    disk=1000,
    tasks_min=12,
    tasks_max=3000,
    mode='fixed'
)

sim_resources = Category(
    name='sim',
    #cores=12,
    cores=6,
    memory=3000,
    disk=3000,
    tasks_min=12,
    mode='fixed'
)

digi_resources = Category(
    name='digi',
    cores=6,
    memory=7800,
    disk=6000,
    mode='fixed'
)

# Not sure what to put for this... same as digi???
hlt_resources = Category(
    name='hlt',
    cores=6,
    memory=7800,
    disk=6000,
    mode='fixed'
)

reco_resources = Category(
    name='reco',
    cores=3,
    memory=3500,
    disk=3000,
    mode='fixed'
)

maod_resources = Category(
    name='maod',
    cores=2,
    memory=2500,
    disk=2000,
    mode='fixed'
)
#################################################################

wf_steps = ['gen','sim','digi','hlt','reco','maod']

base = '/afs/crc.nd.edu/user/k/kmohrman/test/test_das_query/test_cmds/ttbar'
ul_16_base = 'UL16'
ul_16APV_base = 'UL16APV'
ul_17_base = 'UL17'
ul_18_base = 'UL18'

ul_cfg_map = {
    'UL16' : {
        'all_procs' : {
            #'sim'  : base+"/"+ul_16_base+"/"+'SIM' +"/"+'TRK-RunIISummer19UL16SIM-00003_1_cfg.py',
            'sim'  : 'TRK-RunIISummer19UL16SIM-00003_1_cfg.py',
            'digi' : base+"/"+ul_16_base+"/"+'DIGI'+"/"+'TRK-RunIISummer19UL16DIGI-00003_1_cfg.py',
            'hlt'  : base+"/"+ul_16_base+"/"+'HLT' +"/"+'TRK-RunIISummer19UL16HLT-00003_1_cfg.py',
            'reco' : base+"/"+ul_16_base+"/"+'RECO'+"/"+'TRK-RunIISummer19UL16RECO-00003_1_cfg.py',
            'maod' : base+"/"+ul_16_base+"/"+'MAOD'+"/"+'TRK-RunIISummer19UL16MiniAOD-00003_1_cfg.py',
        }
    },
    'UL16APV' : {
        'all_procs' : {
            'sim'  : base+"/"+ul_16APV_base+"/"+'SIM' +"/"+'TRK-RunIISummer19UL16SIMAPV-00003_1_cfg.py',
            'digi' : base+"/"+ul_16APV_base+"/"+'DIGI'+"/"+'TRK-RunIISummer19UL16DIGIAPV-00001_1_cfg.py',
            'hlt'  : base+"/"+ul_16APV_base+"/"+'HLT' +"/"+'TRK-RunIISummer19UL16HLTAPV-00003_1_cfg.py',
            'reco' : base+"/"+ul_16APV_base+"/"+'RECO'+"/"+'TRK-RunIISummer19UL16RECOAPV-00003_1_cfg.py',
            'maod' : base+"/"+ul_16APV_base+"/"+'MAOD'+"/"+'TRK-RunIISummer19UL16MiniAODAPV-00003_1_cfg.py',
        }
    },
    'UL17' : {
        'all_procs' : {
            'sim'  : base+"/"+ul_17_base+"/"+'SIM' +"/"+'TRK-RunIISummer19UL17SIM-00003_1_cfg.py',
            'digi' : base+"/"+ul_17_base+"/"+'DIGI'+"/"+'TRK-RunIISummer19UL17DIGI-00003_1_cfg.py',
            'hlt'  : base+"/"+ul_17_base+"/"+'HLT' +"/"+'TRK-RunIISummer19UL17HLT-00003_1_cfg.py',
            'reco' : base+"/"+ul_17_base+"/"+'RECO'+"/"+'TRK-RunIISummer19UL17RECO-00003_1_cfg.py',
            'maod' : base+"/"+ul_17_base+"/"+'MAOD'+"/"+'TRK-RunIISummer19UL17MiniAOD-00003_1_cfg.py',
        }
    },
    'UL18' : {
        'all_procs' : {
            'sim'  : base+"/"+ul_18_base+"/"+'SIM' +"/"+'TRK-RunIISummer19UL18SIM-00003_1_cfg.py',
            'digi' : base+"/"+ul_18_base+"/"+'DIGI'+"/"+'TRK-RunIISummer19UL18DIGI-00003_1_cfg.py',
            'hlt'  : base+"/"+ul_18_base+"/"+'HLT' +"/"+'TRK-RunIISummer19UL18HLT-00003_1_cfg.py',
            'reco' : base+"/"+ul_18_base+"/"+'RECO'+"/"+'TRK-RunIISummer19UL18RECO-00003_1_cfg.py',
            'maod' : base+"/"+ul_18_base+"/"+'MAOD'+"/"+'TRK-RunIISummer19UL18MiniAOD-00003_1_cfg.py',
        }
    }

}
gen_cfg_map = {
    'ttHJet' : {
        #'gen' : 'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-ttHJets_1_cfg.py'
        'gen': 'python_cfgs/GEN/GEN-00000-ttHJets_1_cfg.py',
    },
    'ttlnuJet' : {
        #'gen' : 'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-ttlnuJets_1_cfg.py',
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttllNuNuJetNoHiggs' : {
        #'gen' : 'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-ttlnuJets_1_cfg.py',
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py'
    },
    'tllq4fNoSchanWNoHiggs0p' : {
        #'gen' : 'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-tllq4f_1_cfg.py',
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tHq4f' : {
        #'gen' : 'python_cfgs/GS/HIG-RunIIFall17wmGS-00000-tllq4f_1_cfg.py',
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    }
}

rel_map = {
    'UL16' : {
        #'gen' : 'CMSSW_10_6_12',
        'sim' : 'CMSSW_10_6_12',
        'digi': 'CMSSW_10_6_12',
        'hlt' : 'CMSSW_8_0_33_UL',
        'reco': 'CMSSW_10_6_12',
        'maod': 'CMSSW_10_6_12',
    },
    'UL16APV' : {
        #'gen' : 'CMSSW_10_6_12',
        'sim' : 'CMSSW_10_6_12',
        'digi': 'CMSSW_10_6_12',
        'hlt' : 'CMSSW_8_0_33_UL',
        'reco': 'CMSSW_10_6_12',
        'maod': 'CMSSW_10_6_12',
    },
    'UL17' : {
        #'gen' : 'CMSSW_10_6_12',
        'sim' : 'CMSSW_10_6_2',
        'digi': 'CMSSW_10_6_2',
        'hlt' : 'CMSSW_9_4_14_UL_patch1',
        'reco': 'CMSSW_10_6_2',
        'maod': 'CMSSW_10_6_2',
    },
    'UL18' : {
        #'gen' : 'CMSSW_10_6_12',
        'sim' : 'CMSSW_10_6_4_patch1',
        'digi': 'CMSSW_10_6_4_patch1',
        'hlt' : 'CMSSW_10_2_16_UL',
        'reco': 'CMSSW_10_6_4_patch1',
        'maod': 'CMSSW_10_6_4_patch1',
    },

}

fragment_map = ul_cfg_map[UL_YEAR]
for k,v in gen_cfg_map.iteritems():
    fragment_map[k] = v

print("Fragement map!")
for k,v in fragment_map.iteritems():
    print k,":",v

# Note: These changes will be applied to every process in the run

gs_mods_dict = {}

gs_mods_dict["base"] = {}
gs_mods_dict["base"]["base"] = []
#gs_mods_dict["ttHJet"] = {}
#gs_mods_dict["ttHJet"]['qCut15'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 15|g']
#gs_mods_dict["ttHJet"]['qCut19'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 19|g']
#gs_mods_dict["ttHJet"]['qCut25'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 25|g']

gs_mods_dict["tllq4fNoSchanWNoHiggs0p"] = {}
gs_mods_dict["tllq4fNoSchanWNoHiggs0p"]['MatchOff'] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']

gs_mods_dict["tHq4f"] = {}
gs_mods_dict["tHq4f"]['MatchOff'] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']

wf = []

print "Generating workflows:"
for idx,lhe_dir in enumerate(lhe_dirs):
    print "\t[{0}/{1}] LHE Input: {dir}".format(idx+1,len(lhe_dirs),dir=lhe_dir)
    head,tail = os.path.split(lhe_dir)
    arr = tail.split('_')
    p,c,r = arr[2],arr[3],arr[4]
    print("p c r:",p,c,r)
    if p in gs_mods_dict:
        gs_mods = gs_mods_dict[p]
    else:
        gs_mods = gs_mods_dict["base"]
    for mod_tag,sed_str_list in gs_mods.iteritems():
        wf_fragments = {}
        for step in wf_steps:
            if step == 'gen':
                template_loc = fragment_map[p][step]
            else:
                template_loc = fragment_map["all_procs"][step]
            print "template loc !!", template_loc
            # Only the GEN-SIM step can be modified
            if step == 'gen':
                head,tail = os.path.split(template_loc)
                # This should be a unique identifier within a single lobster master to ensure we dont overwrite a cfg file too early
                cfg_tag = '{tag}-{idx}'.format(tag=mod_tag,idx=idx)
                tail = tail.replace("cfg.py","{tag}_cfg.py".format(tag=cfg_tag))
                mod_loc = os.path.join(MODIFIED_CFG_DIR,tail)
                shutil.copy(template_loc,mod_loc)
                for sed_str in sed_str_list:
                    if sed_str:
                        run_process(['sed','-i','-e',sed_str,mod_loc])
            else:
                mod_loc = template_loc
            wf_fragments[step] = mod_loc
        if mod_tag == 'base': mod_tag = ''
        label_tag = "{p}_{c}{mod}_{r}".format(p=p,c=c,r=r,mod=mod_tag)
        print "\t\tLabel: {label}".format(label=label_tag)

        print "\nThis is the wf_fragments:",wf_fragments,"\n"

        gen = Workflow(
            label='gen_step_{tag}'.format(tag=label_tag),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['gen']),
            sandbox=cmssw.Sandbox(release='CMSSW_9_3_6'),
            merge_size=-1,  # Don't merge files we don't plan to keep
            cleanup_input=False,
            globaltag=False,
            outputs=['GEN-00000.root'],
            dataset=Dataset(
                files=lhe_dir,
                #files_per_task=2,
                files_per_task=1,
                patterns=["*.root"]
            ),
            category=gen_resources
        )

        sim = Workflow(
            label='sim_step_{tag}'.format(tag=label_tag),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['sim']),
            sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['sim']),
            merge_size=-1,  # Don't merge files we don't plan to keep
            cleanup_input=False,
            globaltag=False,
            outputs=['SIM-00000.root'],
            dataset=ParentDataset(
                parent=gen,
                units_per_task=1
            ),
            category=sim_resources
        )

        digi = Workflow(
            label='digi_step_{tag}'.format(tag=label_tag),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['digi']),
            sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['digi']),
            merge_size=-1,  # Don't merge files we don't plan to keep
            cleanup_input=True,    # Save the GEN-SIM step
            outputs=['DIGI-00000.root'],
            dataset=ParentDataset(
                parent=sim,
                units_per_task=1
            ),
            category=digi_resources
        )

        hlt = Workflow(
            label='hlt_step_{tag}'.format(tag=label_tag),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['hlt']),
            sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['hlt']),
            merge_size=-1, # Don't merge files we don't plan to keep
            cleanup_input=False, # ???
            outputs=['HLT-00000'],
            dataset=ParentDataset(
                parent=digi,
                units_per_task=1
            ),
            category=hlt_resources
        )

        reco = Workflow(
            label='reco_step_{tag}'.format(tag=label_tag),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['reco']),
            sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['reco']),
            merge_size=-1,  # Don't merge files we don't plan to keep
            cleanup_input=True,
            outputs=['RECO-00000.root'],
            dataset=ParentDataset(
                parent=hlt,
                units_per_task=2
            ),
            category=reco_resources
        )

        maod = Workflow(
            label='mAOD_step_{tag}'.format(tag=label_tag),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['maod']),
            sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['maod']),
            merge_size='256M',
            cleanup_input=True,
            outputs=['MAOD-00000.root'],
            dataset=ParentDataset(
                parent=reco,
                units_per_task=3
            ),
            category=maod_resources
        )

        wf.extend([gen,sim,digi,hlt,reco,maod])
        #wf.extend([gen])

config = Config(
    label=master_label,
    workdir=workdir_path,
    plotdir=plotdir_path,
    storage=storage,
    workflows=wf,
    advanced=AdvancedOptions(
        dashboard = False,
        bad_exit_codes=[127, 160],
        log_level=1,
        payload=10,
        xrootd_servers=['ndcms.crc.nd.edu',
                       'cmsxrootd.fnal.gov',
                       'deepthought.crc.nd.edu']
    )
)
