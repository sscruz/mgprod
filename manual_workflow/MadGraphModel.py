import os
import subprocess
import shutil

class MadGraphModel(object):
    MODELS_DIR   = 'models'
    CARD_DEFAULT = 'param_card.dat'

    def __init__(self,tar_dir,tarball,np_block,param_card,cards_dir):
        self.tar_dir    = tar_dir       # Ex: models
        self.tb         = tarball       # Ex: HEL_UFO.third_gen.tar.gz
        self.np_block   = np_block      # Ex: NEWCOUP
        self.param_card = param_card    # Ex: restrict_no_b_mass.dat
        self.cards_dir  = cards_dir     # Ex: hel_cards

        self.m_name = self.tb.split('.')[0]

    def makeParamCard(self,mgbase_dir):
        orig_dir = os.getcwd()
        m_dir = os.path.join(mgbase_dir,self.MODELS_DIR,self.m_name)
        os.chdir(m_dir)
        subprocess.check_output(['python','write_param_card.py'])
        shutil.move(self.CARD_DEFAULT,self.param_card)
        os.chdir(orig_dir)
        return os.path.join(m_dir,self.param_card)

    # Gets the np parameters from a parameter card file
    def getParameters(self,fpath):
        # Returns a list of tuples e.g: [ (1,0.9,'cuW'), ... ]
        np_params = []
        in_block = False
        with open(fpath) as f:
            for l in f.readlines():
                if len(l) > 0 and l[0] == '#':
                    continue
                elif len(l.strip()) == 0:
                    continue
                l_chk = l.strip()
                if 'block' in l_chk.lower():
                    if in_block:
                        in_block = False
                        break
                    elif self.np_block.lower() in l_chk.lower():
                        in_block = True
                        continue
                if in_block:
                    arr = [x.strip() for x in l_chk.split('#')]
                    p_name = arr[1]
                    lha_code,p_val = arr[0].split()
                    np_params.append([int(lha_code),float(p_val),p_name])
        return np_params

    # Edit the Wilson coefficient strengths in the param_card.dat file
    def editParamCard(self,pts,fpath):
        # pts should be a list of tuples e.g: [ (1,0.9,'cuW'), ... ]
        print "Editing param card: %s" % (fpath)
        with open(fpath) as f:
            lines = f.readlines()
        in_block = False
        with open(fpath,'w') as f:
            for l in lines:
                if l.strip().lower() == 'block %s' % (self.np_block.lower()):
                    # Entering np block
                    in_block = True
                    f.write(l)
                    for lha_code,point,name in pts:
                        new_line = "%s %.6f # %s\n" % (str(lha_code).rjust(5),point,name)
                        f.write(new_line)
                if in_block:
                    if l.strip() == "":
                        # Exiting np block
                        in_block = False
                        f.write("\n")
                else:
                    f.write(l)
        return fpath