#PATH="-P /afs/cern.ch/work/b/botta/TREES_72X_050515_MiniIso"
#PATH="-P /data1/p/peruzzi/TREES_72X_050515_MiniIso -F sf/t {P}/1_lepJetReClean_Susy_v1/evVarFriend_{cname}.root --mcc susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt"
PATH="-P /dev/shm/TREES_72X_050515_MiniIso_TTJets -F sf/t {P}/1_lepJetReClean_Susy_v1/evVarFriend_{cname}.root --mcc susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt"
OUTDIR='FRAPPLYplots_test/plots_test'

cuts={}
def add_cuts(mylist):
    my = list(set(mylist))
    return ' '.join("-A alwaystrue "+cut+" '"+cuts[cut]+"'" for cut in my)
def remove_cuts(mylist):
    my = list(set(mylist))
    return ' '.join("-X "+cut for cut in my)
def replace_cuts(mylist):
    my = list(set(mylist))
    return ' '.join("-R "+cut+" "+newcut+" '"+cuts[newcut]+"'" for cut,newcut in mylist)
def prepare_cuts(add,remove,replace):
    my = list(set(add))
    my = [i for i in my if i not in remove]
    for k,l in replace:
        my = [l if k==x else x for x in my]
        my=list(set(my))
    return my

cuts["isee"]="abs(LepGood1_pdgId) == 11 && abs(LepGood2_pdgId) == 11"
cuts["ismm"]="abs(LepGood1_pdgId) == 13 && abs(LepGood2_pdgId) == 13"
cuts["isem"]="(abs(LepGood1_pdgId) == 11 || abs(LepGood1_pdgId) == 13) && (abs(LepGood2_pdgId) == 11 || abs(LepGood2_pdgId) == 13)"
cuts["pt1LT25"]="LepGood1_pt<25"
cuts["pt1GT25"]="LepGood1_pt>=25"
cuts["pt2LT25"]="LepGood2_pt<25"
cuts["pt2GT25"]="LepGood2_pt>=25"
cuts["bas0"]="nBJetMedium25==0"
cuts["bas1"]="nBJetMedium25==2"
cuts["bas2"]="nBJetMedium25==2"
cuts["bas3"]="nBJetMedium25>=3"

runs=[]
#[NAME,CUTS_TXT_FILE,SELECTION_CUTS,REMOVED_CUTS,REPLACED_CUTS,DATASETS,NUM_FOR_FR_STUDY(doeff==1 + define in sels.txt),XVAR_FOR_FR_STUDY(doeff==1 + define in xvars.txt)]
for xvar in ["eta_pt","eta_conept","eta_jetpt"]:
    for ptreg in ["ll","lh","hh"]:
        for lepflav in ["ee","em","mm"]:
            for baselineregion in [-1,0,1,2,3]:
                app=[]
                app.append("is"+lepflav)
                app.append("pt1LT25" if ptreg[0]=="l" else "pt1GT25")
                app.append("pt2LT25" if ptreg[1]=="l" else "pt2GT25")
                br="_incl"
                if baselineregion >= 0:
                    app.append("bas%d" % (baselineregion,))
                    br="_b%d" % (baselineregion,)
                runs.append(["Application_"+xvar+"_"+lepflav+"_"+ptreg+br,"susy-multilepton/fake_rate/susy_2lss_fake_rate_multiiso.txt",app,[],[],"-p TT_red,TT_red_FO1_%s,TT_red_FO2_%s,TT_red_FO1_%s_insitu,TT_red_FO2_%s_insitu" % (xvar,xvar,xvar,xvar)])
                    

for run in runs:
    RUN="python mcPlots.py -j 8 -f --plotmode nostack --print 'pdf' --s2v --tree treeProducerSusyMultilepton susy-multilepton/fake_rate/susy_2lss_fake_rate_mca_sync.txt "+run[1]
    B0=' '.join([RUN,PATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_plots.txt"])
    B0 += " --pdir "+OUTDIR+'_'+run[0]
    B0 += ' '+add_cuts(prepare_cuts(run[2],run[3],run[4]))
    B0 += ' '+str(run[5])
    print B0

