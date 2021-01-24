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

#username = "awightma"
username = "kmohrman"

#RUN_SETUP = 'local'
#RUN_SETUP = 'full_production'
RUN_SETUP = 'mg_studies'
#RUN_SETUP = 'lobster_test'

in_ver  = ""   # The version index for the INPUT directory
out_ver = "v1"   # The version index for the OUTPUT directory

#grp_tag  = "2019_04_19/ttHJet-xqcutStudies"   # For 'local' and 'mg_studies' setups
#grp_tag  = "2019_04_19/HanModelNoctG16DttllScanpointsxqcutscan"
grp_tag  = ""
#out_tag  = "2019_04_19/ttHJet-HanV4cptAxisScan-withPSweights"
#out_tag  = "2019_04_19/ttXJet_HanV4_semftComp_QED1_QCD2_DIM62"
#out_tag  = "2019_04_19/ttH-ttHJet_dim6Top-vMay2020-normChromoTrue"
#out_tag  = "2019_04_19/ttW-ttWJet-ttZ-ttZJet_QED-QCD-order-tests"
#out_tag  = "2019_04_19/tllqJet5f_SMmodel-xqcut10-nJetMax-Tests"
#out_tag  = "2019_04_19/ttX-NLO_SMEFT_QED1_QCD2_NP2"
#out_tag  = "2019_04_19/ttX-ttXJet_HanV4-QED2-startPtChecks"
#out_tag  = "2019_04_19/ttH_HanV4ttH0pStartPtDoubleCheck"
#out_tag  = "2019_04_19/test"
#out_tag  = "2019_04_19/ttHJet_HanV4-5M"
#out_tag  = "FullR2Studies/PreliminaryStudies/ttHJet_dim6TopMay20_testing-old-genprod-updated-model"
#out_tag  = "FullR2Studies/PreliminaryStudies/ttXJet-tXq_testUpdateGenproddim6TopMay20GST-testAllProcs"
out_tag  = "FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprod-HanV4"
#out_tag = "test/lobster_test_{tstamp}".format(tstamp=timestamp_tag)
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
elif RUN_SETUP == 'lobster_test':
    # For lobster workflow tests
    grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/genOnly_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/genOnly_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/genOnly_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
else:
    print "Unknown run setup, {setup}".format(setup=RUN_SETUP)
    raise ValueError

input_path = "/store/user/"
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

dir_list = [
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttHJet_HanV4cptAxisScan/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttW-ttWJet-ttZ-ttZJet_QED-QCD-order-tests/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttXJet_HanV4-QED1-noQCDconstraints/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/tllqJet5f_HanV4-xqcut10/v1"),
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/tllqJet5f_SMmodel-xqcut10/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttX-NLO_SMEFT_QED1_QCD2_NP2/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttX-ttXJet_HanV4-QED2-startPtChecks/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttH_HanV4ttH0pStartPtDoubleCheck/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/PreliminaryStudies/ttHJet_testUpdateGenprod-testModels/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/PreliminaryStudies/ttHJet_testOldGenprod-testModels/v1")
    os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprod-HanV4/v1")
]

lhe_dirs = []
for path in dir_list:
    for fd in os.listdir(path):
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

#lhe_dirs = [
    #"kmohrman/LHE_step/2019_04_19/ttHJet-ttWJet_HanV4ttXJetStartPtChecks/v1/lhe_step_ttHJet_HanV4ttXJetStartPtChecks_run2"
    #"kmohrman/LHE_step/2019_04_19/ttHJet-ttWJet_HanV4ttXJetStartPtChecks/v1/lhe_step_ttlnuJet_HanV4ttXJetStartPtChecks_run1",
    #"kmohrman/LHE_step/2019_04_19/ttZJet_HanV4ttXJetStartPtChecks-run2run3/v1/lhe_step_ttllNuNuJetNoHiggs_HanV4ttXJetStartPtChecks_run2",
    #"kmohrman/LHE_step/2019_04_19/ttX-NLO_SMEFT_QED1_QCD2_NP2/v1/lhe_step_ttH_SMEFTNLO_slc7"
    #"kmohrman/LHE_step/2019_04_19/ttW-ttWJet-HanV4cpQ3AxisScan/v1/lhe_step_ttWJet_cpQ3HanV4AxisScan_run0",
    #"kmohrman/LHE_step/2019_04_19/ttW-ttWJet-HanV4cpQ3AxisScan/v1/lhe_step_ttWJet_cpQ3HanV4AxisScan_run1",
    #"kmohrman/LHE_step/2019_04_19/ttW-ttWJet-HanV4cpQ3AxisScan/v1/lhe_step_ttWJet_cpQ3HanV4AxisScan_run2",
    #"kmohrman/LHE_step/2019_04_19/ttW-ttWJet-HanV4cpQ3AxisScan/v1/lhe_step_ttWJet_cpQ3HanV4AxisScan_run3",
    #"kmohrman/LHE_step/2019_04_19/ttW-ttWJet-HanV4cpQ3AxisScan/v1/lhe_step_ttWJet_cpQ3HanV4AxisScan_run4",
    #"kmohrman/FullProduction/Round6/Batch8/LHE_step/v1/lhe_step_ttHJet_HanV4ttXJetStartPtChecks_run0",
#]

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
fragment_map_NLO = {
    'ttH': { # Reza's sample with this name does not have an extra jet explicitly
        'gen': 'python_cfgs/GEN/NLO/HIG-RunIIFall17wmLHEGS-00054_1_cfg.py',
    },
    'ttW': { # Reza's sample with this name does not have an extra jet explicitly
        'gen': 'python_cfgs/GEN/NLO/TOP-RunIIFall17wmLHEGS-00076_1_cfg.py', # No matching
    },
    'ttZ': { # Reza's sample with this name does not have an extra jet explicitly
        'gen': 'python_cfgs/GEN/NLO/TOP-RunIIFall17wmLHEGS-00076_1_cfg.py', # No matching
    },
    'ttHjet':{ # Reza ttH + j sample
        'gen': 'python_cfgs/GEN/NLO/HIG-RunIIFall17wmLHEGS-00054_1_matchON_cfg.py',
        #'gen': 'python_cfgs/GEN/NLO/HIG-RunIIFall17wmLHEGS-00054_1_cfg.py',
    },
    'tth01j':{ # Central ttH (with extra jet explicitly)
        'gen': 'python_cfgs/GEN/NLO/HIG-RunIIFall17wmLHEGS-00054_1_matchON_cfg.py',
     },
    'TTWJetsToLNu':{ # Central ttlnu (with extra jet explicitly)
        'gen': 'python_cfgs/GEN/NLO/TOP-RunIIFall17wmLHEGS-00075_1_cfg.py',
     },
    'TTZJetsToLLNuNu':{ # Central ttll (WITHOUT extra jet explicitly)
        'gen': 'python_cfgs/GEN/NLO/TOP-RunIIFall17wmLHEGS-00076_1_cfg.py',
     },
}
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
    'ttHJetqq': {
        'gen': 'python_cfgs/GEN/GEN-00000-ttHJets_1_cfg.py',
    },
    'ttHJetgg': {
        'gen': 'python_cfgs/GEN/GEN-00000-ttHJets_1_cfg.py',
    },  
    'ttHJetgq': {
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
    'tllq4fMatchedNoSchanW':{
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tllq4fMatchedNoHiggs': {# Uses same fragment as tllq4f
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tllq4fNoSchanWNoHiggs0p': {# Uses same fragment as tllq4f (but remember to turn off matching!!!)
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tHq4fMatched': {# Uses same fragment as tllq4f
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'tHq4f': {# Uses same fragment as tllq4f (but remember to turn off matching!!!)
        'gen': 'python_cfgs/GEN/GEN-00000-tllq4f_1_cfg.py',
    },
    'ttbarJetgg': {
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttHJetSMEFTcomp': { # Use same as ttHJet
        'gen': 'python_cfgs/GEN/GEN-00000-ttHJets_1_cfg.py',
    },
    'ttWJetSMEFTcomp': { # Use same as ttlnuJet
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttZJetSMEFTcomp': { # USe same as ttlnuJet
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttWJet': { # Use same as ttlnuJet? Should check with Andrew.
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttZJet': { # Use same as ttlnuJet? Should check with Andrew.
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'tllqJet5fNoSchanWNoHiggs': { # Use same as ttlnuJet ### Note! Hard coded nJet = 1 into cfg for this run
        'gen': 'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttbar' :{ # Remember to turn off matching!!!
        'gen':'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
    'ttbarJet' :{
        'gen':'python_cfgs/GEN/GEN-00000-ttlnuJets_1_cfg.py',
    },
}

# For each input, create multiple output workflows modifying a single GEN config attribute
#gen_mods = {}
#gen_mods['base'] = ''
#gen_mods['qCut10'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 10|g']
#gen_mods['qCut15'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 15|g']
#gen_mods['qCut19'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 19|g']
#gen_mods['qCut25'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 25|g']
#gen_mods['MatchOff'] = ['s|JetMatching:merge = on|JetMatching:merge = off|g' , 's|TimeShower:mMaxGamma = 4.0|TimeShower:mMaxGamma = 10|g'] # Also set mMaxGamma to default to match 2017 analysis
#gen_mods['qCut19_nJetMax1'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 19|g' , 's|JetMatching:nJetMax = 1|JetMatching:nJetMax = 1|g']
#gen_mods['qCut19_nJet1_nJetMax2'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 19|g' , 's|JetMatching:nJetMax = 1|JetMatching:nJetMax = 2|g']
#gen_mods['qCut50_nJetMax1'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 50|g' , 's|JetMatching:nJetMax = 1|JetMatching:nJetMax = 1|g']
#gen_mods['qCut50_nJetMax2'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 50|g' , 's|JetMatching:nJetMax = 1|JetMatching:nJetMax = 2|g']

gen_mods_dict = {}

gen_mods_dict["base"] = {}
gen_mods_dict["base"]["base"] = []
# gen_mods_dict["base"]["qCutUp"] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 25|g']
# gen_mods_dict["base"]["qCutDown"] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 15|g']
#gen_mods_dict["ttHJet"] = {}
#gen_mods_dict["ttHJet"]['qCut15'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 15|g']
#gen_mods_dict["ttHJet"]['qCut19'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 19|g']
#gen_mods_dict["ttHJet"]['qCut25'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 25|g']

gen_mods_dict["tllq4fNoSchanWNoHiggs0p"] = {}
gen_mods_dict["tllq4fNoSchanWNoHiggs0p"]['MatchOff'] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']

gen_mods_dict["tHq4f"] = {}
gen_mods_dict["tHq4f"]['MatchOff'] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']

gen_mods_dict["ttbar"] = {}
gen_mods_dict["ttbar"]["MatchOff"] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']

wf = []

print "Generating workflows:"
for idx,lhe_dir in enumerate(lhe_dirs):
    print "\t[{n}/{tot}] LHE Input: {dir}".format(n=idx+1,tot=len(lhe_dirs),dir=lhe_dir)
    #arr = lhe_dir.split('_')
    head,tail = os.path.split(lhe_dir)
    arr = tail.split('_')
    p,c,r = arr[2],arr[3],arr[4]
    if p in gen_mods_dict:
        gen_mods = gen_mods_dict[p]
    else:
        gen_mods = gen_mods_dict["base"]
    for mod_tag,sed_str_list in gen_mods.iteritems():
        wf_fragments = {}
        for step in wf_steps:
            if fragment_map.has_key(p) and fragment_map[p].has_key(step):
                template_loc = fragment_map[p][step]
            else:
                print "\nNo fragment specified! Using default for this step."
                template_loc = fragment_map['default'][step]
            #template_loc = fragment_map_NLO[p][step] # For NLO
            head,tail = os.path.split(template_loc)
            # This should be a unique identifier within a single lobster master to ensure we dont overwrite a cfg file too early
            cfg_tag = '{tag}-{idx}'.format(tag=mod_tag,idx=idx)
            tail = tail.replace("cfg.py","{tag}_cfg.py".format(tag=cfg_tag))
            mod_loc = os.path.join(MODIFIED_CFG_DIR,tail)
            shutil.copy(template_loc,mod_loc)
            for sed_str in sed_str_list:
                if sed_str:
                    run_process(['sed','-i','-e',sed_str,mod_loc])
            wf_fragments[step] = mod_loc
        if mod_tag == 'base': mod_tag = ''
        gen = Workflow(
            label='gen_step_{p}_{c}{mod}_{r}'.format(p=p,c=c,mod=mod_tag,r=r),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['gen']),
            #sandbox=cmssw.Sandbox(release='CMSSW_9_3_1'),
            sandbox=cmssw.Sandbox(release='CMSSW_9_3_6'),
            merge_size=-1,  # Don't merge files we don't plan to keep
            cleanup_input=False,
            globaltag=False,
            outputs=['GEN-00000.root'],
            dataset=Dataset(
                files=lhe_dir,
                files_per_task=5,
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
        dashboard = False,
        bad_exit_codes=[127, 160],
        log_level=1,
        payload=10,
        xrootd_servers=['ndcms.crc.nd.edu',
                       'cmsxrootd.fnal.gov',
                       'deepthought.crc.nd.edu']
    )
)
