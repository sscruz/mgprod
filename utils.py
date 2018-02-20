import os
import subprocess
import re
import shutil
import numpy as np

def runProcess(inputs):
    p = subprocess.Popen(inputs,stdout=subprocess.PIPE)
    while True:
        l = p.stdout.readline()
        if l == '' and p.poll() is not None:
            break
        if l:
            print l.strip()
    return

def setup_madgraph(home_dir,mg_tarball,mdl,process_card,scan_coeffs,cores,events):
    work_dir = os.path.join(os.getcwd(),'work')

    print 'Unpacking MG tarball %s' % (mg_tarball)
    subprocess.call(['tar','xaf',os.path.join(home_dir,mg_tarball)])

    arr = os.listdir('.')
    mgbase_dir = os.path.join(os.getcwd(),arr[0])   # Doesn't work with MGv233 tarball!
    shutil.move(mgbase_dir,'mgbasedir')
    mgbase_dir = os.path.join(os.getcwd(),'mgbasedir')

    print 'Unpacking model tarball %s' % (os.path.join(mgbase_dir,mdl.tar_dir,mdl.tb))
    subprocess.call(['tar','xaf',os.path.join(home_dir,mdl.tar_dir,mdl.tb),'--directory=%s' % (os.path.join(mgbase_dir,'models'))])

    param_path = mdl.makeParamCard(mgbase_dir)
    np_params = mdl.getParameters(param_path)
    points = [[p[0],1.0*(idx+1),p[2]] if (p[2] in scan_coeffs) else [p[0],0.0,p[2]] for idx,p in enumerate(np_params)]
    mdl.editParamCard(points,param_path)

    os.chdir(mgbase_dir)

    print 'Running mg5_aMC...'
    #output = subprocess.check_output(['python',os.path.join('bin','mg5_aMC'),'-f',os.path.join(home_dir,process_card)])
    runProcess(['python',os.path.join('bin','mg5_aMC'),'-f',os.path.join(home_dir,process_card)])

    arr = os.listdir(mgbase_dir)
    if "processtmp" not in arr:
        print "ERROR: Missing processtmp directory!"
        return

    print "Moving process directory to %s" % (work_dir)
    shutil.move('processtmp',work_dir)

    os.chdir(work_dir)

    shutil.copy(os.path.join(home_dir,mdl.cards_dir,'run_card.dat'), 'Cards')
    shutil.copy(os.path.join(home_dir,mdl.cards_dir,'grid_card.dat'), 'Cards')
    shutil.copy(os.path.join(home_dir,mdl.cards_dir,'runcmsgrid.sh'), '../')

    with open('Cards/me5_configuration.txt','a') as f:
        f.write('\nnb_core = %d' % (cores))
        f.write('\nrun_mode = 0')
        #f.write('\nlhapdf = /cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/lhapdf/6.1.6/share/LHAPDF/../../bin/lhapdf-config')
        f.write('\nlhapdf = /cvmfs/cms.cern.ch/slc6_amd64_gcc630/external/lhapdf/6.1.6/share/LHAPDF/../../bin/lhapdf-config')
        f.write('\nautomatic_html_opening = False')

    with open('Cards/run_card.dat','a') as f:
        f.write('\n %d = nevents' % (events))
        f.write('\n.false. = gridpack')

    return work_dir

def make_gridpack(sandbox_dir,work_dir):
    os.chdir(work_dir)
    with open('Cards/run_card.dat','a') as f:
        f.write('\n.true. = gridpack')

    print "Generating gridpack events..."
    #output = subprocess.check_output(['./bin/generate_events','-f'])
    runProcess(['./bin/generate_events','-f'])
    shutil.move('run_01_gridpack.tar.gz',sandbox_dir)

    os.chdir(sandbox_dir)

    print "Unpacking run_01_gridpack..."
    subprocess.call(['tar','xzf','run_01_gridpack.tar.gz'])
    
    os.chdir('madevent')

    #print "Running reweighting..."
    #os.mkdir('Events/pilotrun')
    #shutil.copy(os.path.join(work_dir,'Events/run_01/unweighted_events.lhe.gz'),os.path.join('Events/pilotrun/unweighted_events.lhe.gz'))
    #with open('Cards/me5_configuration.txt.','a') as f:
    #    f.write('\nnb_core = 1')
    #runProcess(['./bin/madevent','reweight','-f','pilotrun'])

    print "Compiling madevent..."
    runProcess(['./bin/compile'])
    runProcess(['./bin/clean4grid'])

    os.chdir(sandbox_dir)

    os.mkdir('process')
    shutil.move('madevent','process')
    shutil.move('run.sh','process')

    print "Making gridpack..."
    subprocess.call(['tar', 'cJpsf', 'gridpack.tar.xz', 'mgbasedir', 'process', 'runcmsgrid.sh'])

    print "Finished..."

# Make the reweight_card.dat file
def make_reweight_card(work_dir,np_block,points):
    # points = [{c1: 1.0, c2: 1.0, ...}, {c1: 1.0, c2: 2.0, ...}, ...]
    orig_dir = os.getcwd()
    os.chdir(work_dir)
    with open('Cards/reweight_card.dat','w') as f:
        f.write('change rwgt_dir rwgt\n')
        for p in points:
            f.write('\nlaunch')
            for k,v in p.iteritems():
                f.write('\nset %s %s %.6f' % (np_block,k,v))
            f.write('\n')
    os.chdir(orig_dir)
    return os.path.join(work_dir,'Cards','reweight_card.dat')

# This works for multi-dim scans now
def create_reweight_points(limits,num_pts):
    sm_pt     = {k: 0.0 for k in limits.keys()}
    start_pt  = {k: arr[0] for k,arr in limits.iteritems()}
    has_sm_pt = check_point(sm_pt,start_pt)
    rwgt_pts  = []
    coeffs    = []
    arr       = []
    for k,(start,low,high) in limits.iteritems():
        coeffs.append(k)
        arr += [np.linspace(low,high,num_pts)]
    mesh_pts = cartesian_product(*arr)
    for rwgt_pt in mesh_pts:
        pt = {k: round(rwgt_pt[idx],6) for idx,k in enumerate(coeffs)}
        if check_point(pt,sm_pt):
            has_sm_pt = True
        if check_point(pt,start_pt):
            continue
        rwgt_pts.append(pt)
    if not has_sm_pt:
        rwgt_pts.append(sm_pt)
    return rwgt_pts

def check_point(pt1,pt2):
    for k,v in pt1.iteritems():
        if not pt2.has_key(k):
            pt2[k] = 0.0    # pt2 is missing the coeff, add it and set it to SM value
        if v != pt2[k]:
            return False
    return True

def cartesian_product(*arrays):
    # https://stackoverflow.com/questions/11144513
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[..., i] = a
    return arr.reshape(-1, la)
