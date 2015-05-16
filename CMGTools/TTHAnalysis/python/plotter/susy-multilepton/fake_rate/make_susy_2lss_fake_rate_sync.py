#PATH="-P /afs/cern.ch/work/b/botta/TREES_72X_050515_MiniIso"
PATH="-P /data1/p/peruzzi/TREES_72X_050515_MiniIso -F sf/t {P}/1_lepJetReClean_Susy_v1/evVarFriend_{cname}.root --mcc susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt"
FTREEQCD="-F sf/t {P}/2_leptonFakeRateQCDVars_Susy_v1/evVarFriend_{cname}.root"
OUTDIR='FRplots_test/plots_test'

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


cuts["anylep"]="abs(LepGood_pdgId) > 0"
cuts["minireliso04"]="LepGood_miniRelIso<0.4"
cuts["dxy005"]="LepGood_dxy<0.05"
cuts["dz01"]="LepGood_dz<0.1"
cuts["sipLT4"]="LepGood_sip3d<4"
cuts["sipGT4"]="LepGood_sip3d>4"
cuts["pt5"]="LepGood_pt > 5"
cuts["pt7"]="LepGood_pt > 7"
cuts["pt10"]="LepGood_pt > 10"
cuts["etaLT2p4"]="abs(LepGood_eta) < 2.4"
cuts["etaLT2p5"]="abs(LepGood_eta) < 2.5"
cuts["ismu"]="abs(LepGood_pdgId)==13"
cuts["isel"]="abs(LepGood_pdgId)==11"
cuts["muMediumID"]="LepGood_mediumMuonId > 0"
cuts["elMVAloose"]="LepGood_mvaIdPhys14 > -0.11+(-0.35+0.11)*(abs(LepGood_eta)>0.8)+(-0.55+0.35)*(abs(LepGood_eta)>1.479)"
cuts["elMVAtight"]="LepGood_mvaIdPhys14 > 0.73+(0.57-0.73)*(abs(LepGood_eta)>0.8)+(+0.05-0.57)*(abs(LepGood_eta)>1.479)"
cuts["losthitsLEQ1"]="LepGood_lostHits<=1"
cuts["losthitsEQ0"]="LepGood_lostHits==0"
cuts["elConvVeto"]="LepGood_convVeto"
cuts["tightcharge"]="LepGood_tightCharge > (abs(LepGood_pdgId) == 11)"
cuts["multiiso"]="multiIso_multiWP(LepGood_pdgId,LepGood_pt,LepGood_eta,LepGood_miniRelIso,LepGood_jetPtRatio,LepGood_jetPtRel,2) > 0"
cuts["mutrackpterr"]="blablabla"


LooseLepSel=["minireliso04","dxy005","dz01"]
LooseMuSel=LooseLepSel+["pt5","etaLT2p4"]
LooseElSel=LooseLepSel+["pt7","etaLT2p5","elMVAloose","elConvVeto","losthitsLEQ1"]

TightLepSel=["sipLT4","dz01","multiiso"]
TightMuSel=LooseMuSel+TightLepSel+["pt10","etaLT2p4","muMediumID","tightcharge"]
TightElSel=LooseElSel+TightLepSel+["pt10","etaLT2p5","elMVAtight","elConvVeto","tightcharge","losthitsEQ0"]


cuts["metLT20"]="met_pt<20"
cuts["mtLT20"]="mt_2(LepGood_pt,LepGood_phi,met_pt,met_phi)<20"
cuts["jetaway40"]="((LepGood_awayJet_pt>40) && (deltaR(LepGood_eta,LepGood_phi,LepGood_awayJet_eta,LepGood_awayJet_phi)>1.0))"
QCDmeasReg=["metLT20","mtLT20","jetaway40"]


MuDsetsQCD=FTREEQCD+' -p QCDMu_red'
ElDsetsQCD=FTREEQCD+' -p QCDEl_red'
MuDsetsInSitu='-p TT_red '
ElDsetsInSitu='-p TT_red '

runs=[]
#[NAME,CUTS_TXT_FILE,SELECTION_CUTS,REMOVED_CUTS,REPLACED_CUTS,DATASETS,NUM_FOR_FR_STUDY(doeff==1 + define in sels.txt),XVAR_FOR_FR_STUDY(doeff==1 + define in xvars.txt)]
for xvar in ["eta_pt","eta_conept","eta_jetpt"]:
    runs.append(["FO1Mu"+"_"+xvar,"susy-multilepton/fake_rate/susy_2lss_fake_rate_perlep.txt",TightMuSel+QCDmeasReg,[],[("multiiso","minireliso04")],MuDsetsQCD,"multiiso",xvar])
    runs.append(["FO1El"+"_"+xvar,"susy-multilepton/fake_rate/susy_2lss_fake_rate_perlep.txt",TightElSel+QCDmeasReg,[],[("multiiso","minireliso04")],ElDsetsQCD,"multiiso",xvar])
    runs.append(["FO2El"+"_"+xvar,"susy-multilepton/fake_rate/susy_2lss_fake_rate_perlep.txt",TightElSel+QCDmeasReg,[],[("multiiso","minireliso04"),("elMVAtight","elMVAloose")],ElDsetsQCD,"multiiso_AND_elMVAtight",xvar])
    runs.append(["FO1MuInSitu"+"_"+xvar,"susy-multilepton/fake_rate/susy_2lss_fake_rate_insitu_sync.txt",TightMuSel,["dxy005","dz01"],[("sipLT4","sipGT4"),("multiiso","minireliso04")],MuDsetsInSitu,"multiiso",xvar])
    runs.append(["FO1ElInSitu"+"_"+xvar,"susy-multilepton/fake_rate/susy_2lss_fake_rate_insitu_sync.txt",TightElSel,["dxy005","dz01"],[("sipLT4","sipGT4"),("multiiso","minireliso04")],ElDsetsInSitu,"multiiso",xvar])
    runs.append(["FO2ElInSitu"+"_"+xvar,"susy-multilepton/fake_rate/susy_2lss_fake_rate_insitu_sync.txt",TightElSel,["dxy005","dz01"],[("sipLT4","sipGT4"),("multiiso","minireliso04"),("elMVAtight","elMVAloose")],ElDsetsInSitu,"multiiso_AND_elMVAtight",xvar])

for run in runs:
    doeff = (len(run)>6)
    RUN="python mcEfficiencies.py --s2v --tree treeProducerSusyMultilepton susy-multilepton/fake_rate/susy_2lss_fake_rate_mca_sync.txt "+run[1]
    run[0]=run[6]+'_ON_'+run[0]
    B0=' '.join([RUN,PATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_sels_sync.txt","susy-multilepton/fake_rate/susy_2lss_fake_rate_xvars_sync.txt"])
#    B0 += " --legend=TL  --yrange -1 2 --showRatio --ratioRange 0 3 --xcut 10 999 --ytitle 'Fake rate' --groupBy cut"
    B0 += " --legend=TL --ytitle 'Fake rate' --groupBy cut"
    B0 += ' --sP '+run[6]
    B0 += " -o "+OUTDIR+'_'+run[0]+"/plots.root"
    B0 += ' --sP '+run[7]
    B0 += ' '+add_cuts(prepare_cuts(run[2],run[3],run[4]))
    B0 += ' '+str(run[5])
    print B0

