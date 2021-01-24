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
events_per_gridpack = 200e3
#events_per_gridpack = 250e3
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
#grp_tag = "2019_04_19/ttHJet_HanV4xqcutTests" # Out tag for mg_studies
#grp_tag = "2019_04_19/ttXJet_HanV4_semftComp_QED1_QCD2_DIM62" # Out tag for mg_studies
#grp_tag = "2019_04_19/ttX-NLO_SMEFT_QED1_QCD2_NP2" # Out tag for mg_studies
#grp_tag = "2019_04_19/ttHJet_HanV4_withRwgt_smeftComp_QED1_QCD2_DIM61" # Out tag for mg_studies
#grp_tag = "2019_04_19/ttX-ttXJet_HanV4-QED1-QCD3"
#grp_tag = "2019_04_19/tllqJet5f_HanV4-xqcut10"
#grp_tag = "2019_04_19/ttV-ttVJet_HanV4_QED1-and-noConstraints_startPtChecks"
#grp_tag = "2019_04_19/ttHNLO_SMmodel-NLO-test"
#grp_tag = "2019_04_19/ttHjet-NLO_SM-SMEFTNLO-fromReza"
#grp_tag = "2019_04_19/ttX-ttXJet_HanV4-QED2-startPtChecks"
#grp_tag = "2019_04_19/ttW-ttWJet-HanV4cpQ3AxisScan"
#grp_tag = "FullR2Studies/ttHJet_dim6TopMay20_testing-old-genprod-updated-model"
#grp_tag = "FullR2Studies/PreliminaryStudies/ttHJet_testUpdateGenprod-testModels"
#grp_tag = "FullR2Studies/PreliminaryStudies/ttHJet_testOldGenprod-testModels"
grp_tag = "FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprod-HanV4"
prod_tag = ""

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
    #"awightma/gridpack_scans/central_gridpacks/tth01j_5f_ckm_NLO_FXFX_MH125_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz", # A central ttH
    #"awightma/gridpack_scans/central_gridpacks/TTWJetsToLNu_5f_NLO_FXFX_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz",     # A central ttlnu
    #"awightma/gridpack_scans/central_gridpacks/TTZJetsToLLNuNu_5f_NLO_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz",       # A central ttll
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
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXjetxqcut5_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXjetxqcut10_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4ttXjetxqcut15_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",
    #"kmohrman/gridpack_scans/2019_04_19/ttHJetSMEFTcomp_ttXJetSMEFTcomp_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Comp with SMEFT NLO
    #"kmohrman/gridpack_scans/2019_04_19/ttWJetSMEFTcomp_ttXJetSMEFTcomp_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Comp with SMEFT NLO
    #"kmohrman/gridpack_scans/2019_04_19/ttZJetSMEFTcomp_ttXJetSMEFTcomp_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Comp with SMEFT NLO
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttH_SMEFTNLO_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza NLO
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttW_SMEFTNLO_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza NLO
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttZ_SMEFTNLO_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza NLO
    #"kmohrman/gridpack_scans/2019_04_19/ttH_dim6Top-vMay2020-normChromoTrue_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Updated dim6Top ttH check
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_dim6Top-vMay2020-normChromoTrue_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Updated dim6Top ttHJet check
    #"kmohrman/gridpack_scans/2019_04_19/ttW_HanV4-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",              # ttW (not ttlnu!) (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttZ_HanV4-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",              # ttZ (not ttll!) (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_HanV4-0plus1p-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",   # This is (or at least should be) 0+1p (not just +1p) (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttZJet_HanV4-0plus1p-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",   # This is (or at least should be) 0+1p (not just +1p) (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttW_HanV4-QED1QCD2-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",     # ttW QED1,QD2
    #"kmohrman/gridpack_scans/2019_04_19/ttZ_HanV4-QED1QCD2-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",     # ttZ QED1,QCD2
    #"kmohrman/gridpack_scans/2019_04_19/ttH_HanV4-0p-QED1QCD2-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",   # ttH QED1, QCD1
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4-0plus1p-noMatching-QED1QCD2-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttHJet QED1, QCD2, matching off (since no extr jet)!
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_HanV4-0plus1p-noMatching-QED1QCD2-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet QED1, QCD2, matching off (since no extr jet)!
    #"kmohrman/gridpack_scans/2019_04_19/ttZJet_HanV4-0plus1p-noMatching-QED1QCD2-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttZJet QED1, QCD2, matching off (since no extr jet)!
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4-DIM61QED1noQEDconstraint-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttHJet QED=1, no QCD constraints
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_HanV4-DIM61QED1noQEDconstraint-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet QED=1, no QCD constraints
    #"kmohrman/gridpack_scans/2019_04_19/ttZJet_HanV4-DIM61QED1noQEDconstraint-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttZJet QED=1, no QCD constraints
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4-DIM61QED1QCD3-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttHJet, QED=1, QCD=3 (turns out the NLO QED=1, QCD=2 [QCD] mean that we should have QCD=3 to compare at LO
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_HanV4-DIM61QED1QCD3-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet, QED=1, QCD=3 (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttZJet_HanV4-DIM61QED1QCD3-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttZJet, QED=1, QCD=3 (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttH_HanV4-DIM61QED1QCD3-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttHJet, QED=1, QCD=3
    #"kmohrman/gridpack_scans/2019_04_19/ttW_HanV4-DIM61QED1QCD3-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet, QED=1, QCD=3 (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/ttZ_HanV4-DIM61QED1QCD3-withRwgt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttZJet, QED=1, QCD=3 (bad start pt)
    #"kmohrman/gridpack_scans/2019_04_19/tllqJet5fNoSchanWNoHiggs_HanV4-tllqJet5f-Test_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Atempt at making tllqJet 5f gridpack (HanV4)
    #"kmohrman/gridpack_scans/2019_04_19/tllqJet5fNoSchanWNoHiggs_SMmodel-tllqJet5f-Test_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Attempt at making a tllqJet 5f matched gridpack (SM model)
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttH_SM-SMEFTNLO_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza SM NLO gridpack
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttW_SM-SMEFTNLO_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza SM NLO gridpack
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttZ_SM-SMEFTNLO_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza SM NLO gridpack
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttHjet_SMEFTNLO_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza SM ttHJet test (not actualy plus jet!!!)
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttHjet_SMEFTNLO_NP0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza SM ttHJet test, with NP=0 (not actually plus jet!!!)
    #"kmohrman/gridpack_scans/2020_05_11_fromReza/ttHjet_SM-SMEFTNLO-plusJ_NP0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Reza SM ttHJet, should actually be plus jet
    #"kmohrman/gridpack_scans/2019_04_19/ttHJet_HanV4lModel16DttllScanpoints_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",   # Normal HanV4 ttHJet
    #"kmohrman/gridpack_scans/2019_04_19/ttH_HanV4ModelNoJets16DttllScanpoints_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Normal VanV4 ttH
    #"kmohrman/gridpack_scans/2019_04_19/ttW_HanV4-QED1QCD3-goodStartPt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",    # ttW QED1QCD3 good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_HanV4-QED1QCD3-goodStartPt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWjet QED1QCD3 good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttZ_HanV4-QED1QCD3-goodStartPt_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",    # ttZ QED1QCD3 good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttZJet_HanV4-QED1QCD3-goodStartPt_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttZjet QED1QCD3 good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttW_HanV4-goodStartPt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",    # ttW good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_HanV4-goodStartPt_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWjet good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttZ_HanV4-goodStartPt_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",    # ttZ good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttZJet_HanV4-goodStartPt_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttZjet good start pt
    #"kmohrman/gridpack_scans/2019_04_19/ttH_cptHanV4AxisScan_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH cpt axis scan (-15 to 15)
    #"kmohrman/gridpack_scans/2019_04_19/ttH_cptHanV4-batch2AxisScan_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH cpt axis scan (-15 to 15) REDO, issue with first one
    #"kmohrman/gridpack_scans/2019_04_19/ttH_cptHanV4AxisScan_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH cpt axis scan (-15 to 15)
    #"kmohrman/gridpack_scans/2019_04_19/ttH_cptHanV4AxisScan_run3_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH cpt axis scan (-15 to 15)
    #"kmohrman/gridpack_scans/2019_04_19/ttH_cptHanV4AxisScan_run4_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH cpt axis scan (-15 to 15)
    #"kmohrman/gridpack_scans/2019_04_19/ttW_cpQ3HanV4AxisScan_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttW cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttW_cpQ3HanV4AxisScan_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttW cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttW_cpQ3HanV4AxisScan_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttW cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttW_cpQ3HanV4AxisScan_run3_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttW cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttW_cpQ3HanV4AxisScan_run4_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttW cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_cpQ3HanV4AxisScan_run0_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_cpQ3HanV4AxisScan_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_cpQ3HanV4AxisScan_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_cpQ3HanV4AxisScan_run3_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttWJet_cpQ3HanV4AxisScan_run4_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttWJet cpQ3 axis scan (-4 to 4)
    #"kmohrman/gridpack_scans/2019_04_19/ttH_HanV4ttH0pStartPtDoubleCheck_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH 0p start point check (or double check? Have we really not checked this before?)
    #"kmohrman/gridpack_scans/2019_04_19/ttH_HanV4ttH0pStartPtDoubleCheck_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH 0p start point check (or double check? Have we really not checked this before?)
    #"kmohrman/gridpack_scans/2019_04_19/ttH_HanV4ttH0pStartPtDoubleCheck_run3_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # ttH 0p start point check (or double check? Have we really not checked this before?)
    ###
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_TESTdim6TopGST_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # First test gridpack with updated genproductions framework, updated dim6Top model
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_dim6TopMay20GSTtestWithOldGenprod_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Test gridpack, old genprodudictions framework, new (May 2020) dim6Top model, with gs norm true
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_dim6TopMay20GSFtestWithOldGenprod_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz", # Test gridpack, old genprodudictions framework, new (May 2020) dim6Top model, with gs norm false
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_testUpdateGenproddim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Test new updated genprod framework
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_testUpdateGenproddim6TopMay20GSF_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Test new updated genprod framework
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_testUpdateGenprodHanV4_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Test new updated genprod framework
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_testOldGenproddim6TopMay20GST_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",  # Test old framework
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_testOldGenproddim6TopMay20GSF_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",  # Test old framework
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_testOldGenprodHanV4_run1_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",            # Test old framework
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttllNuNuJetNoHiggs_testUpdateGenproddim6TopMay20GST_run2_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",      # Test rest of processes with new framework (and new dim6Top)
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttlnuJet_testUpdateGenproddim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",                # Test rest of processes with new framework (and new dim6Top)
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/tllq4fNoSchanWNoHiggs0p_testUpdateGenproddim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Test rest of processes with new framework (and new dim6Top)
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/tHq4f_testUpdateGenproddim6TopMay20GST_run2_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",                   # Test rest of processes with new framework (and new dim6Top)
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttbar_newGenProdCheckTTBARv6dim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Check for bkg dependence on WCs
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttbar_newGenProdCheckTTBARv6dim6TopMay20GST_run2_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Check for bkg dependence on WCs
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttbar_newGenProdCheckTTBARv6dim6TopMay20GST_run3_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Check for bkg dependence on WCs
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttbarJet_newGenProdCheckTTBARv5dim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Check ttbar for bkg dependence on WCs
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttbarJet_newGenProdCheckTTBARv5dim6TopMay20GST_run2_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Check ttbar for bkg dependence on WCs
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttbarJet_newGenProdCheckTTBARv5dim6TopMay20GST_run3_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Check ttbar for bkg dependence on WCs
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/tHq4f_testUpdateGenprodMG260dim6TopMay20GST_run2_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",                   # Check new model and new genprod framework BUT with MG 260
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/tllq4fNoSchanWNoHiggs0p_testUpdateGenprodMG260dim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz", # Check new model and new genprod framework BUT with MG 260
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttHJet_testUpdateGenprodMG260dim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",                  # Check new model and new genprod framework BUT with MG 260
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttlnuJet_testUpdateGenprodMG260dim6TopMay20GST_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",                # Check new model and new genprod framework BUT with MG 260
    #"kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/ttllNuNuJetNoHiggs_testUpdateGenprodMG260dim6TopMay20GST_run2_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",      # Check new model and new genprod framework BUT with MG 260
    "kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprodHanV4_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",                             # tHq check with old genprod and HanV4 (Has issue with FCNC=0 twice in proc card)
    "kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprodHanV4WithoutExtraFCNC0InProcCard_run2_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz",  # tHq check with old genprod and HanV4


]

## This block is usually comented:
##hardcoded_dir = "/hadoop/store/user/kmohrman/gridpack_scans/2020_08_05_ttV_startPtChecks"
##hardcoded_base_dir = "kmohrman/gridpack_scans/2020_08_05_ttV_startPtChecks/"
#hardcoded_dir = "/hadoop/store/user/kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies"
#hardcoded_base_dir = "kmohrman/gridpack_scans/FullR2Studies/PreliminaryStudies/"
#gridpacks = []
##for f in os.listdir(input_path_full):
##for gp_dir in gridpack_list:
#for gp_dir in os.listdir(hardcoded_dir):
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
#    gridpacks.append(hardcoded_base_dir+gp)
#gridpack_list = gridpacks

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
    'ttHjet': 4,
    'ttlnuJet': 2,
    'ttWJet': 2,
    'tHq4fMatched': 1.2,
    'tllq4fMatchedNoHiggs': 1.2,
    'tllqJet5fNoSchanWNoHiggs':4,
    'ttllNuNuJetNoHiggs': 4,
    'ttZJet': 4,
    'ttbarJet':3.5,
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
    print "Label and cat name:", label,cat_name
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
        dashboard = False,
        bad_exit_codes=[127, 160],
        log_level=1,
        payload=10,
        xrootd_servers=['ndcms.crc.nd.edu',
                       'cmsxrootd.fnal.gov',
                       'deepthought.crc.nd.edu']
    )
)
