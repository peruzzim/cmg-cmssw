import ROOT
import os, sys

# usage: python verifyFTree BIGTREE_DIR FTREE_DIR DATASET_NAME ...

dsets = sys.argv[3:]
if len(sys.argv)<4:
    dsets = [d.replace('evVarFriend_','').replace('.root','') for d in os.listdir(sys.argv[2]) if 'evVarFriend' in d]

for dset in dsets:
    f_t = ROOT.TFile.Open(sys.argv[1]+'/'+dset+'/treeProducerSusyMultilepton/tree.root')
    t_t = f_t.Get("tree")
    n_t = t_t.GetEntries()
    f_t.Close()
    f_f = ROOT.TFile.Open(sys.argv[2]+'/evVarFriend_'+dset+'.root')
    t_f = f_f.Get("sf/t")
    n_f = t_f.GetEntries()
    f_f.Close()
    print '%s: %d - %d : %s'%(dset,n_t,n_f,'OK' if n_t==n_f else 'ERROR '*5+' !!!')
