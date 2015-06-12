import sys
doeff = ("eff" in sys.argv[1:])
dotable = ("table" in sys.argv[1:])
dodump = ("dump" in sys.argv[1:])
doplot = ("plot" in sys.argv[1:])

PATH="-P /data1/p/peruzzi/TREES_72X_070615_MiniIso -F sf/t {P}/3_QCDVarsSusy_FakeRateFO_v10/evVarFriend_{cname}.root %s --mcc susy-multilepton/fake_rate_ABC/susy_2lss_fake_rate_customchoices.txt "
FTREEQCD=""
FTREETT="-F sf/t {P}/1_lepJetReClean_Susy_v1/evVarFriend_{cname}.root"
OUTDIR='GOODFR/derive'

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


cuts["anylep"]="abs(LepGood_pdgId) > 0"
cuts["minireliso04"]="LepGood_miniRelIso<0.4"
cuts["dxy005"]="abs(LepGood_dxy)<0.05"
cuts["dz01"]="abs(LepGood_dz)<0.1"
cuts["sipLT4"]="LepGood_sip3d<4"
cuts["sipLT10"]="LepGood_sip3d<10"
cuts["sipGT4"]="LepGood_sip3d>4"
cuts["pt5"]="LepGood_ConePt > 5"
cuts["pt7"]="LepGood_ConePt > 7"
cuts["pt10"]="LepGood_ConePt > 10"
cuts["etaLT2p4"]="abs(LepGood_eta) < 2.4"
cuts["etaLT2p5"]="abs(LepGood_eta) < 2.5"
cuts["etagap"]="abs(LepGood_pdgId)!=11 || abs(LepGood_eta)<1.4442 || abs(LepGood_eta)>1.566"
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
cuts["ABCregion"]="LepGood_ABCRegion>-1"

LooseLepSel=["minireliso04","dxy005","dz01"]
LooseMuSel=LooseLepSel+["ismu","pt5","etaLT2p4"]
LooseElSel=LooseLepSel+["isel","pt7","pt10","etaLT2p5","etagap","elMVAloose","elConvVeto","losthitsLEQ1","losthitsEQ0"]

TightLepSel=["sipLT4","dz01","multiiso"]
TightMuSel=LooseMuSel+TightLepSel+["pt10","etaLT2p4","muMediumID","tightcharge"]
TightElSel=LooseElSel+TightLepSel+["pt10","etaLT2p5","elMVAtight","elConvVeto","tightcharge","losthitsEQ0"]

cuts["metLT20"]="met_pt<20"
cuts["mtLT20"]="mt_2(LepGood_pt,LepGood_phi,met_pt,met_phi)<20"
cuts["jetaway40"]="((LepGood_awayJet_pt>40) && (deltaR(LepGood_eta,LepGood_phi,LepGood_awayJet_eta,LepGood_awayJet_phi)>1.0))"
QCDmeasReg=["metLT20","mtLT20","jetaway40"]

cuts["jetawayCSVv2IVFL"]="LepGood_awayJet_btagCSV>0.423"
cuts["jetawayCSVv2IVFM"]="LepGood_awayJet_btagCSV>0.814"
cuts["jetawayCSVv2IVFT"]="LepGood_awayJet_btagCSV>0.941"


MuDsetsQCD='-p QCD_Mu'
ElDsetsQCD='-p QCD_El'

runs=[]
#[NAME,CUTS_TXT_FILE,SELECTION_CUTS,REMOVED_CUTS,REPLACED_CUTS,DATASETS,NUM_FOR_FR_STUDY(doeff==1 + define in sels.txt),XVAR_FOR_FR_STUDY(doeff==1 + define in xvars.txt)]

runs.append(["FO9Mu","susy-multilepton/fake_rate_ABC/derive/susy_2lss_fake_rate_perlep.txt",TightMuSel+QCDmeasReg+["ABCregion"],["sipLT4"],[("multiiso","minireliso04")],MuDsetsQCD])


if doplot:
    for run in runs:
        RUN="python mcPlots.py -f -e --print pdf --plotmode stack -l 0.01 --s2v --tree treeProducerSusyMultilepton"
        MYPATH=PATH
        MYPATH = MYPATH % (FTREEQCD if "QCD" in run[5] else FTREETT,)
        B0=' '.join(['echo',run[0],';',RUN,MYPATH,"susy-multilepton/fake_rate_ABC/susy_2lss_fake_rate_mca_sync.txt",run[1],"susy-multilepton/fake_rate_ABC/derive/susy_2lss_fake_rate_ABC_study.txt"])
        B0 += ' '.join([' ',add_cuts(prepare_cuts(run[2],run[3],run[4])),run[5],"--pdir "+OUTDIR+'_'+run[0]])
        print B0





#if (dotable or dodump):
#    for run in runs:
#        RUN="python %s -l 0.01 --s2v --tree treeProducerSusyMultilepton" % ("mcAnalysis.py" if dotable else "mcDump.py")
#        MYPATH=PATH
#        MYPATH = MYPATH % (FTREEQCD if "QCD" in run[5] else FTREETT,"--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_coneptchoice.txt" if "conept" in run[0] else "--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_defaultptchoice.txt")
#        B0=' '.join(['echo',run[0],';',RUN,MYPATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_mca_sync.txt",run[1]])
#        run[0]=run[6]+'_ON_'+run[0]
#        B0 += ' '.join([' ',add_cuts(prepare_cuts(run[2],run[3],run[4])),run[5]])
#        if dodump:
#            B0 += ' '+str(sys.argv[2])
#        print B0


#if doeff:
#    for run in runs:
#        RUN="python mcEfficiencies.py --s2v --tree treeProducerSusyMultilepton"
#        MYPATH=PATH
#        MYPATH = MYPATH % (FTREEQCD if "QCD" in run[5] else FTREETT,"--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_coneptchoice.txt" if "conept" in run[0] else "--mcc susy-multilepton/fake_rate/susy_2lss_fake_rate_defaultptchoice.txt")
#        B0=' '.join([RUN,MYPATH,"susy-multilepton/fake_rate/susy_2lss_fake_rate_mca_sync.txt",run[1],"susy-multilepton/fake_rate/derive/susy_2lss_fake_rate_sels_sync.txt","susy-multilepton/fake_rate/derive/susy_2lss_fake_rate_xvars_sync.txt"])
#        run[0]=run[6]+'_ON_'+run[0]
#        B0 += ' '.join([' ',"--legend=TL --ytitle 'Fake rate' --groupBy cut",'--sP '+run[6],"-o "+OUTDIR+'_'+run[0]+"/plots.root",' --sP '+run[7]])
#        B0 += ' '.join([' ',add_cuts(prepare_cuts(run[2],run[3],run[4])),run[5]])
#        print B0
#
