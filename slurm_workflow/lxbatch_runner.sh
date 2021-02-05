#!/bin/bash
if [[ "$VO_CMS_SW_DIR" != "" ]] && test -f $VO_CMS_SW_DIR/cmsset_default.sh; then 
  source $VO_CMS_SW_DIR/cmsset_default.sh
fi;
RELEASEPATH=$1; shift
SRC=$1; shift
OUTPUT=$1; shift

rm -rf $SRC # cleanup leftovers
mkdir -p $SRC

echo "Getting ENV from $RELEASEPATH"
cd $RELEASEPATH
eval $(scramv1 runtime -sh);
echo "Running in $SRC"
cd $SRC; 

echo "Creating scratch dir for madgraph"
mkdir -p _CONDOR_SCRATCH_DIR
export _CONDOR_SCRATCH_DIR="$PWD/CONDOR_SCRATCH_DIR"

echo "Will execute $*"
$* &> thelog_$SLURM_JOB_ID

echo "Transferring output" 
xrdcp -f output.root root://t3dcachedb.psi.ch:1094/$OUTPUT
xrdcp -f output_LHE.root root://t3dcachedb.psi.ch:1094/${OUTPUT/.root/_LHE.root}
xrdcp -f output_tree.root root://t3dcachedb.psi.ch:1094/${OUTPUT/.root/_histos.root}

echo "copying log"
xrdcp -f thelog_$SLURM_JOB_ID root://t3dcachedb.psi.ch:1094/${OUTPUT/.root/$SLURM_JOB_ID}
    
rm -rf $SRC
