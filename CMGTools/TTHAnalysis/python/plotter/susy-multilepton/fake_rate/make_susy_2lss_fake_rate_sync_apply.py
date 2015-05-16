plotmode='norm'
pyfile=["mcPlots.py -f --plotmode "+plotmode+" --print 'pdf'",'mcEfficiencies.py']

#PATH="-P /afs/cern.ch/work/b/botta/TREES_72X_050515_MiniIso"
PATH="-P /data1/p/peruzzi/TREES_72X_050515_MiniIso -F sf/t {P}/1_lepJetReClean_Susy_v1/evVarFriend_{cname}.root -F sf/t {P}/2_leptonFakeRateQCDVars_Susy_v1/evVarFriend_{cname}.root --mcc susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt"
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


MuDsetsQCD='-p QCDMu_red'
ElDsetsQCD='-p QCDEl_red'
MuDsetsInSitu='-p TTJets_red'
ElDsetsInSitu='-p TTJets_red'

runs=[]
#[NAME,CUTS_TXT_FILE,SELECTION_CUTS,REMOVED_CUTS,REPLACED_CUTS,DATASETS,NUM_FOR_FR_STUDY(doeff==1 + define in sels.txt),XVAR_FOR_FR_STUDY(doeff==1 + define in xvars.txt)]
for xvar in ["eta_pt","eta_conept","eta_jetpt"]:
    for ptreg in ["ll","lh","hh"]:
        for lepflav in ["ee","em","mm"]:
                app=[]
                app.append("is"+lepflav)
                app.append("pt1LT25" if ptreg[0]=="l" else "pt1GT25")
                app.append("pt2LT25" if ptreg[1]=="l" else "pt2GT25")
                runs.append(["MuApplication_"+xvar,"susy_2lss_fake_rate_multiiso.txt",app,[],[],MuDsetsQCD])
                runs.append(["ElApplication_"+xvar,"susy_2lss_fake_rate_multiiso.txt",app,[],[],MuDsetsQCD])
                runs.append(["MuApplicationInSitu_"+xvar,"susy_2lss_fake_rate_multiiso.txt",app,[],[],MuDsetsInSitu])
                runs.append(["ElApplicationInSitu_"+xvar,"susy_2lss_fake_rate_multiiso.txt",app,[],[],ElDsetsInSitu])


runs=runs[:1]

for run in runs:
    doeff = (len(run)>6)
    RUN="python "+pyfile[doeff]+" --s2v --tree treeProducerSusyMultilepton susy-multilepton/fake_rate/susy_2lss_fake_rate_mca_sync.txt "+run[1]
    if doeff:
        run[0]=run[6]+'_ON_'+run[0]
        B0=' '.join([RUN,PATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_sels_sync.txt","susy-multilepton/fake_rate/susy_2lss_fake_rate_xvars_sync.txt"])
#        B0 += " --legend=TL  --yrange -1 2 --showRatio --ratioRange 0 3 --xcut 10 999 --ytitle 'Fake rate' --groupBy cut"
        B0 += " --legend=TL --ytitle 'Fake rate' --groupBy cut"
        B0 += ' --sP '+run[6]
        B0 += " -o "+OUTDIR+'_'+run[0]+"/plots.root"
        B0 += ' --sP '+run[7]
    else:
        B0=' '.join([RUN,PATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_plots.txt"])
        B0 += " --pdir "+OUTDIR+'_'+run[0]
        if 'ismu' in run[2]:
            B0 += " --xP ele_MVAid,losthits,multiIso_AND_EleId,EleId,sieie_EB,sieie_EE"
        elif 'isel' in run[2]:
            B0 += " --xP mu_mediumid,multiIso_AND_MuonId,MuonId"
    B0 += ' '+add_cuts(prepare_cuts(run[2],run[3],run[4]))
    B0 += ' '+str(run[5])
    print B0

