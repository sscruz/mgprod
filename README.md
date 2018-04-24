# mgprod
This code is meant to generate Monte Carlo events using [MadGraph](https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/ManualAndHelp) as generator and [Lobster](http://lobster.readthedocs.io/en/latest/) to manage the workflow steps: LHE,GEN-SIM,DIGI,RECO,MAOD.

## Setup
In order to setup your area, run the setup scripts located in the scripts directory.

    cd lobster_workflow
    source scripts/setup_cmssw.sh

This setup script is simply to make sure that the correct CMSSW releases are present when running lobster and should only have to be run once.

## Producing Samples
The production is split into two main steps, each with its own corresponding lobster configuration. It is assumed that the following commands are run in the `lobster_workflow` directory.

    source ~/.lobster/bin/activate

The first step produces LHE level events and uses [lobster_LHE_config.py](lobster_workflow/lobster_LHE_config.py). This step runs on a pre-made gridpack tarball, which were produced using the [CMSSW genproductions workflow](https://github.com/cms-sw/genproductions/tree/mg26x/bin/MadGraph5_aMCatNLO). The gridpacks directory can contain any number of gridpacks and can be filtered to only run over a certain sub-set of gridpacks using the whitelists in the lobster config. For the whitelists to work, it is assumed that the gridpacks are named with the following convention: `p_c_r_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz`, where `p`,`c`,`r` correspond respectively to process, coefficient tag, and run tag.

To start production of the LHE events run:

    lobster process lobster_LHE_config.py

Make sure to have a `work_queue_factory` running, otherwise lobster won't have any workers to process the tasks.

    nohup work_queue_factory -T condor -M "lobster_${USER}_EFT_LHE" -d all -o /tmp/${USER}_lobster_factory.debug -C REPLACEME >& /tmp/${USER}_lobster_factory.log &

Make sure to replace the `REPLACEME` with a path to your own `work_queue_factory` config file (e.g. `/afs/crc.nd.edu/user/a/awightma/Public/worker_factories/factory_T3_12c.json`). It is very important for this step that all the workers which are used by the lobster master are from the T3 resources, otherwise the tasks will take significantly longer to finish.

The second step runs on the output produced in the first step and uses [lobster_postLHE_config.py](lobster_workflow/lobster_postLHE_config.py). You will need to change the `input_path` and `input_path_full` variables to point to the output directory where you placed the LHE step root files. As before, run the following:

    lobster process lobster_postLHE_config.py

On the condorfe submit nodes run:

    nohup work_queue_factory -T condor -M "lobster_${USER}_EFT_postLHE" -d all -o /tmp/${USER}_lobster_factory.debug -C REPLACEME --runos=rhel6 >& /tmp/${USER}_lobster_factory.log &

Again replacing the `REPLACEME` string with a path to your own factory config file.