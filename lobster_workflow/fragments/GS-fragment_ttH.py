import FWCore.ParameterSet.Config as cms

# link to cards:
# https://github.com/cms-sw/genproductions/tree/1dbb76303f4efe786c01d52dfd13d685aa412abb/bin/MadGraph5_aMCatNLO/cards/production/2017/13TeV/TTWJets/TTWJets_5f_LO_MLM

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/madgraph/V5_2.4.2/ttW012j_5f/v1/ttW012j_5f.tar.xz'),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8HadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'JetMatching:setMad = on', 
            'JetMatching:scheme = 1', 
            'JetMatching:merge = off',
            'JetMatching:jetAlgorithm = 2', 
            'JetMatching:etaJetMax = 999.', 
            'JetMatching:coneRadius = 1.', 
            'JetMatching:slowJetPower = 1', 
            'JetMatching:qCut = 60.', 
            'JetMatching:nQmatch = 5', 
            'JetMatching:doShowerKt = off',
            'JetMatching:nJetMax = 1',   # For ttHJet process
            'SLHA:useDecayTable = off',  # Use pythia8s own decay mode instead of decays defined in LH accord
            '25:m0 = 125.0',
            '23:mMin = 0.05',       # Solve problem with mZ cut
            '24:mMin = 0.05',       # Solve problem with mW cut
            '25:onMode = on',       # Allow all higgs decays 
            '25:offIfAny = 5 5',    # Switch decays of b quarks off
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'processParameters',
                                    )
    )
)