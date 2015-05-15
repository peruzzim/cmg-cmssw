doeff=0
plotmode='norm'
pyfile=["mcPlots.py -f --plotmode "+plotmode+" --print 'pdf'",'mcEfficiencies.py']

RUN="python "+pyfile[doeff]+" --s2v --tree treeProducerSusyMultilepton susy-multilepton/susy_2lss_fake_rate_mca.txt susy-multilepton/susy_2lss_fake_rate_perlep.txt"

#PATH="-P /afs/cern.ch/work/b/botta/TREES_72X_050515_MiniIso"
PATH="-P /data1/p/peruzzi/TREES_72X_050515_MiniIso"
OUTDIR='plots_test/plots_test'

LooseLepSel="-A alwaystrue loose_mini_iso 'LepGood_miniRelIso<0.4' -A alwaystrue anylep 'abs(LepGood_pdgId) > 0'"
SipCut="-A alwaystrue dxy 'LepGood_sip3d < 20'"

IsMu="-A alwaystrue ismu 'abs(LepGood_pdgId)==13'"
PtMu="-A alwaystrue pt5 'LepGood_pt > 5'"
MuQualCuts="-A alwaystrue muID 'LepGood_mediumMuonId > 0'"

IsEle="-A alwaystrue isele 'abs(LepGood_pdgId)==11'"
PtEle="-A alwaystrue pt7 'LepGood_pt > 7'"
VLEleSel="-A alwaystrue elemvaloose 'LepGood_mvaIdPhys14 > -0.11+(-0.35+0.11)*(abs(LepGood_eta)>0.8)+(-0.55+0.35)*(abs(LepGood_eta)>1.479)' -A alwaystrue lhits 'LepGood_lostHits<=1' -A alwaystrue convveto 'LepGood_convVeto'"
EleQualCuts="-A alwaystrue eleID '(LepGood_mvaIdPhys14 >=0.73+(0.57-0.73)*(abs(LepGood_eta)>0.8)+(+0.05-0.57)*(abs(LepGood_eta)>1.479) || abs(LepGood_pdgId) == 13)'"
EleAdditionalCuts="-A alwaystrue eleaddcuts '(abs(LepGood_pdgId) == 13 || (LepGood_convVeto && LepGood_lostHits == 0))'"
TightCharge="-A alwaystrue tightcharge '(LepGood_tightCharge > (abs(LepGood_pdgId) == 11))'"

LooseMuSel=' ' .join([LooseLepSel,IsMu,PtMu,SipCut])
LooseEleSel=' ' .join([LooseLepSel,IsEle,PtEle,VLEleSel,SipCut])

MuIdOnly=' '.join([LooseMuSel,MuQualCuts,TightCharge])
EleIdOnly=' '.join([LooseEleSel,EleQualCuts,EleAdditionalCuts,TightCharge])

#CHECK THESE
#MultiIso="-A alwaystrue multiiso 'multiIso_multiWP(LepGood_pdgId,LepGood_pt,LepGood_eta,LepGood_miniRelIso,LepGood_jetPtRatio,LepGood_jetPtRel,2) > 0'"
#JetSel="-A alwaystrue jet 'nJet40 >= 1 && minMllAFAS > 12'"
#CommonDen="${SipDen} ${JetDen}"

MuDsets='-p TT_.* --xp TT_red'
EleDsets='-p TT_.* --xp TT_red'
if doeff==1:
    MuDsets+=' --sp TT_red'
    EleDsets+=' --sp TT_red'

runs=[]
#runs.append(["LooseMuSel",'MuonId',LooseMuSel,MuDsets])
#runs.append(["LooseEleSel",'EleId',LooseEleSel,EleDsets])
#runs.append(["MuIdOnly",'multiIso',MuIdOnly,MuDsets])
#runs.append(["EleIdOnly",'multiIso',EleIdOnly,EleDsets])
runs.append(["MuIdOnlyRelaxSip",'multiIso',MuIdOnly,MuDsets])
runs.append(["EleIdOnlyRelaxSip",'multiIso',EleIdOnly,EleDsets])
runs.append(["MuIdOnlyRevertSip",'multiIso',MuIdOnly+" -A alwaystrue siprev 'LepGood_sip3d > 4'",MuDsets])
runs.append(["EleIdOnlyRevertSip",'multiIso',EleIdOnly+" -A alwaystrue siprev 'LepGood_sip3d > 4'",EleDsets])
runs.append(["MuIdOnlyTightSip",'multiIso',MuIdOnly+" -A alwaystrue sipcut 'LepGood_sip3d < 4'",MuDsets])
runs.append(["EleIdOnlyTightSip",'multiIso',EleIdOnly+" -A alwaystrue sipcut 'LepGood_sip3d < 4'",EleDsets])
#runs.append(["MuIdOnly",'miniRelIsoM',MuIdOnly,MuDsets])
#runs.append(["EleIdOnly",'miniRelIsoT',EleIdOnly,EleDsets])
#runs.append(["LooseMuSel",'multiIso_AND_MuonId',LooseMuSel,MuDsets])
#runs.append(["LooseEleSel",'multiIso_AND_EleId',LooseEleSel,EleDsets])


for run in runs:
    if doeff==1:
        run[0]=run[1]+'_ON_'+run[0]
        B0=' '.join([RUN,PATH,"susy-multilepton/susy_2lss_fake_rate_sels.txt","susy-multilepton/susy_2lss_fake_rate_xvars.txt"])
        B0 += " --legend=TL  --yrange -1 2 --showRatio --ratioRange 0 3 --xcut 10 999 --ytitle 'Fake rate' --groupBy cut"
        B0 += ' --sP '+run[1]
        B0 += " -o "+OUTDIR+'_'+run[0]+"/plots.root"
        B0 += ' --sP pt_.*'
    else:
        B0=' '.join([RUN,PATH,"susy-multilepton/susy_2lss_fake_rate_plots.txt"])
        B0 += " --pdir "+OUTDIR+'_'+run[0]
        if 'ismu' in run[2]:
            B0 += " --xP ele_MVAid,losthits,multiIso_AND_EleId,EleId,sieie_EB,sieie_EE"
        elif 'isele' in run[2]:
            B0 += " --xP mu_mediumid,multiIso_AND_MuonId,MuonId"
    B0 += ' '+run[2]
    B0 += ' '+run[3]
    print B0





