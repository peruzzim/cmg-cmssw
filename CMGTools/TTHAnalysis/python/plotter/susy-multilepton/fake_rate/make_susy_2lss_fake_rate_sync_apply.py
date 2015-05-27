OUTDIR='FRAPPLYplots_test/plots_test'

cuts={}
def add_cuts(mylist):
    my = [x for (i,x) in enumerate(mylist) if x not in mylist[:i]]
    return ' '.join("-A alwaystrue "+cut+" '"+cuts[cut]+"'" for cut in my)
def remove_cuts(mylist):
    my = [x for (i,x) in enumerate(mylist) if x not in mylist[:i]]
    return ' '.join("-X "+cut for cut in my)
def replace_cuts(mylist):
    my = [x for (i,x) in enumerate(mylist) if x not in mylist[:i]]
    return ' '.join("-R "+cut+" "+newcut+" '"+cuts[newcut]+"'" for cut,newcut in mylist)
def prepare_cuts(add,remove,replace):
    my = [x for (i,x) in enumerate(add) if x not in add[:i]]
    my = [i for i in my if i not in remove]
    for k,l in replace:
        my = [l if k==x else x for x in my]
        my = [x for (i,x) in enumerate(my) if x not in my[:i]]
    return my


cuts["isee"]="abs(LepGood1_pdgId) == 11 && abs(LepGood2_pdgId) == 11"
cuts["ismm"]="abs(LepGood1_pdgId) == 13 && abs(LepGood2_pdgId) == 13"
cuts["isem"]="(abs(LepGood1_pdgId) == 11 || abs(LepGood1_pdgId) == 13) && (abs(LepGood2_pdgId) == 11 || abs(LepGood2_pdgId) == 13)"
cuts["pt1LT25"]="LepGood1_ConePt<25"
cuts["pt1GT25"]="LepGood1_ConePt>=25"
cuts["pt2LT25"]="LepGood2_ConePt<25"
cuts["pt2GT25"]="LepGood2_ConePt>=25"
cuts["bas0"]="nBJetMedium25==0"
cuts["bas1"]="nBJetMedium25==1"
cuts["bas2"]="nBJetMedium25==2"
cuts["bas3"]="nBJetMedium25>=3"
cuts["pt_ll"]="LepGood1_ConePt<25 && LepGood2_ConePt<25"
cuts["pt_lh"]="(LepGood1_ConePt<25 && LepGood2_ConePt>=25) || (LepGood1_ConePt>=25 && LepGood2_ConePt<25)"
cuts["pt_hh"]="LepGood1_ConePt>=25 && LepGood2_ConePt>=25"

runs=[]
#[NAME,CUTS_TXT_FILE,SELECTION_CUTS,REMOVED_CUTS,REPLACED_CUTS,DATASETS,NUM_FOR_FR_STUDY(doeff==1 + define in sels.txt),XVAR_FOR_FR_STUDY(doeff==1 + define in xvars.txt)]
for xvar in ["eta_pt","eta_conept","eta_jetpt"]:
    for ptreg in ["ll","lh","hh"]:
        for lepflav in ["ee","em","mm"]:
#            for baselineregion in [-1,0,1,2,3]:
            for baselineregion in [-1]:
                app=[]
                app.append("is"+lepflav)
                app.append("pt_"+ptreg)
                br="_incl"
                if baselineregion >= 0:
                    app.append("bas%d" % (baselineregion,))
                    br="_b%d" % (baselineregion,)
                runs.append(["Application_"+xvar+"_"+lepflav+"_"+ptreg+br,"susy-multilepton/fake_rate/susy_2lss_fake_rate_multiiso.txt",app,[],[],"-p TT_red,TT_red_FO1_%s,TT_red_FO2_%s,TT_red_FO1_%s_insitu,TT_red_FO2_%s_insitu" % (xvar,xvar,xvar,xvar)])
#                runs.append(["Application_"+xvar+"_"+lepflav+"_"+ptreg+br,"susy-multilepton/fake_rate/susy_2lss_fake_rate_multiiso.txt",app,[],[],"-p TT_red,TT_red_FO1_%s,TT_red_FO2_%s,TT_red_FO3_%s,TT_red_FO1_%s_insitu,TT_red_FO2_%s_insitu,TT_red_FO3_%s_insitu" % (xvar,xvar,xvar,xvar,xvar,xvar)])
                    

for run in runs:
    PATH="-P /data1/p/peruzzi/TREES_72X_210515_MiniIsoRelaxDxy -F sf/t {P}/1_lepJetReClean_Susy_v4/evVarFriend_{cname}.root %s --mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_insitu_lepchoice_sync.txt"
    MYPATH = PATH % ("--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_coneptchoice.txt" if "conept" in run[0] else "--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_defaultptchoice.txt")
    RUN="python mcPlots.py -e -j 8 -l 0.01 -f --plotmode nostack --print 'pdf' --s2v --tree treeProducerSusyMultilepton"
    B0=' '.join([RUN,MYPATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_mca_sync.txt",run[1],"susy-multilepton/fake_rate/susy_2lss_fake_rate_plots.txt"])
    B0 += ' '.join([' ',add_cuts(prepare_cuts(run[2],run[3],run[4])),"--pdir "+OUTDIR+'_'+run[0],run[5]])
    print B0

#for run in runs:
#    PATH="-P /data1/p/peruzzi/TREES_72X_210515_MiniIsoRelaxDxy -F sf/t {P}/1_lepJetReClean_Susy_v4/evVarFriend_{cname}.root %s --mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_insitu_lepchoice_sync.txt"
#    MYPATH = PATH % ("--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_coneptchoice.txt" if "conept" in run[0] else "--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_defaultptchoice.txt")
#    RUN="python mcAnalysis.py -j 8 -l 0.01 --s2v --tree treeProducerSusyMultilepton"
#    B0=' '.join([RUN,MYPATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_mca_sync.txt",run[1]])
#    B0 += ' '.join([' ',add_cuts(prepare_cuts(run[2],run[3],run[4])),run[5]])
#    print B0




