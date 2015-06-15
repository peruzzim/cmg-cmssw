import sys
OUTDIR='GOODFR/closure'

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
cuts["isinclflav"]="((abs(LepGood1_pdgId) == 11 || abs(LepGood1_pdgId) == 13) && (abs(LepGood2_pdgId) == 11 || abs(LepGood2_pdgId) == 13))"
cuts["pt1LT25"]="LepGood1_pt<25"
cuts["pt1GT25"]="LepGood1_pt>=25"
cuts["pt2LT25"]="LepGood2_pt<25"
cuts["pt2GT25"]="LepGood2_pt>=25"
cuts["bas0"]="nBJetMedium25==0"
cuts["bas1"]="nBJetMedium25==1"
cuts["bas2"]="nBJetMedium25==2"
cuts["bas3"]="nBJetMedium25>=3"
cuts["pt_ll"]="LepGood1_pt<25 && LepGood2_pt<25"
cuts["pt_lh"]="(LepGood1_pt<25 && LepGood2_pt>=25) || (LepGood1_pt>=25 && LepGood2_pt<25)"
cuts["pt_hh"]="LepGood1_pt>=25 && LepGood2_pt>=25"
cuts["pt_inclpt"]="1"
cuts["isnotpromptprompt"]="(LepGood1_mcMatchId==0 || LepGood2_mcMatchId==0)"

# to be fixed for new closure test
cuts["fakeismu"] = "( (LepGood1_mcMatchId!=0 || abs(LepGood1_pdgId)==13) && (LepGood2_mcMatchId!=0 || abs(LepGood2_pdgId)==13) )"
cuts["fakeisel"] = "( (LepGood1_mcMatchId!=0 || abs(LepGood1_pdgId)==11) && (LepGood2_mcMatchId!=0 || abs(LepGood2_pdgId)==11) )"

runs=[]
#[NAME,CUTS_TXT_FILE,SELECTION_CUTS,REMOVED_CUTS,REPLACED_CUTS,DATASETS,NUM_FOR_FR_STUDY(doeff==1 + define in sels.txt),XVAR_FOR_FR_STUDY(doeff==1 + define in xvars.txt)]
for xvar in ["eta_pt"]:
#    for ptreg in ["inclpt","ll","lh","hh"]:
    for ptreg in ["inclpt"]:
        lepflav="inclflav"
        app=[]
        app.append("isnotpromptprompt")
        app.append("is"+lepflav)
        app.append("pt_"+ptreg)
        br="_incl"
        baselineregion = -1
        if baselineregion >= 0:
            app.append("bas%d" % (baselineregion,))
            br="_b%d" % (baselineregion,)
        runs.append(["Application_"+xvar+"_"+lepflav+"_"+ptreg+br,"susy-multilepton/fake_rate_ABC/apply/susy_2lss_fake_rate_applreg.txt",app,[],[],"-p TT,TT_red_FO9_%s" % (xvar,)])
#        runs.append(["Application_"+xvar+"_"+lepflav+"_"+ptreg+br,"susy-multilepton/fake_rate_ABC/apply/susy_2lss_fake_rate_applreg.txt",app,[],[],"-p TT,TT_red_FO1_%s,TT_red_FO9_%s" % (xvar,xvar)])

isplot = 'table' not in sys.argv[1:]

for run in runs:
    PATH="-P /data1/p/peruzzi/TREES_72X_070615_MiniIsoRelaxDxy -F sf/t {P}/1_lepJetReClean_Susy_v1/evVarFriend_{cname}.root -F sf/t {P}/3_QCDVarsSusy_FakeRateFO_v10_dxy/evVarFriend_{cname}.root --mcc susy-multilepton/fake_rate_ABC/susy_2lss_fake_rate_looseveto_lepchoice.txt --mcc susy-multilepton/fake_rate_ABC/susy_2lss_fake_rate_customchoices.txt"
    RUN="python %s --neg -j 8 -l 0.01 --s2v --tree treeProducerSusyMultilepton" % ("mcPlots.py -e -f --plotmode nostack --print 'pdf'" if isplot else "mcAnalysis.py ")
    B0=' '.join([RUN,PATH,"susy-multilepton/fake_rate_ABC/susy_2lss_fake_rate_mca_sync.txt",run[1],"susy-multilepton/fake_rate_ABC/apply/susy_2lss_fake_rate_plots.txt" if isplot else ""])
    B0 += ' '.join([' ',add_cuts(prepare_cuts(run[2],run[3],run[4])),"--pdir "+OUTDIR+'_'+run[0] if isplot else "",run[5]])
    print B0
