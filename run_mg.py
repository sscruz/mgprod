import os

from utils import *
from MadGraphModel import MadGraphModel

HEL_MODEL = MadGraphModel(
    tar_dir='models',
    tarball='HEL_UFO.third_gen.tar.gz',
    np_block='NEWCOUP',
    param_card='restrict_no_b_mass.dat',
    cards_dir ='HEL_cards'
)

TOP_MODEL = MadGraphModel(
    tar_dir='models',
    tarball='dim6top_LO_UFO.tar.gz',
    np_block='DIM6',
    param_card='param_card.dat',
    cards_dir='TOP_cards'
)

MG_TARBALL = "MG5_aMC_v2_6_1.tar.gz"
SANDBOX    = 'test_2'
#PROC_CARD  = 'process_cards/ttZ.dat'
PROC_CARD  = 'process_cards/dim6_ttZ.dat'

def main(model,limits):    
    home_dir = os.getcwd()

    events  = 5000
    cores   = 1
    num_pts = 3

    if not os.path.exists(SANDBOX):
        os.makedirs(SANDBOX)
        os.chdir(SANDBOX)
        work_dir = setup_madgraph(home_dir,MG_TARBALL,model,PROC_CARD,limits.keys(),cores,events)
    else:
        os.chdir(SANDBOX)
        work_dir = os.path.join(os.getcwd(),'work')
    param_path = os.path.join(work_dir,'Cards','param_card.dat')
    np_params = model.getParameters(param_path)

    # Set the Wilson coeffs to starting values
    points = []
    for lha_code,val,c in np_params:
        if limits.has_key(c):
            points.append([lha_code,limits[c][0],c])
    model.editParamCard(points,param_path)
    # Create the reweight card
    rw_pts = create_reweight_points(limits,num_pts)
    print "rw pts:",rw_pts
    reweight_path = make_reweight_card(work_dir,model.np_block,rw_pts)

    os.chdir(work_dir)
    print "Generating %d events..." % (events)
    runProcess(['./bin/generate_events','-f'])

    #make_gridpack(os.path.join(home_dir,SANDBOX),work_dir)

if __name__ == "__main__":
    #model      = HEL_MODEL
    #target     = 'cuW'
    #target_pts = [0.0]
    #limits     = {
    #    'cuW': [0.0,-0.05,0.05],
    #    #'cuB': [0.0,-0.01,0.01],
    #}
    
    model      = TOP_MODEL
    target     = 'ctG'
    #target_pts = [-2.0,-1.0,0.0,1.0,2.0]
    target_pts = [0.0]
    limits     = {'ctG': [0.0,-2.0,2.0]}

    home_dir = os.getcwd()
    for start_pt in target_pts:
        print "Target: %.3f" % (start_pt)
        limits[target][0] = start_pt
        main(model,limits)
        os.chdir(home_dir)