BASE="python mcEfficiencies.py --s2v --tree treeProducerSusyMultilepton object-studies/lepton-mca.txt object-studies/lepton-perlep.txt --ytitle 'Fake rate' "
PATH="-P /afs/cern.ch/work/b/botta/TREES_72X_050515_MiniIso_QCD"
OUTDIR='plots_test/plots_test'

LowerCut="-R pt20 pt5 'LepGood_pt > 5'"

LooseLepSel="-A pt20 loose_mini_iso 'LepGood_miniRelIso<0.4'"
#ADD HERE THE OTHER CUTS OR CHECK PRESELECTION IN TREES

AnyLepSel="-A pt20 anylep 'abs(LepGood_pdgId) > 0'"
IsMu="-A pt20 ismu 'abs(LepGood_pdgId)==13'"
IsEle="-A pt20 isele 'abs(LepGood_pdgId)==11'"
MuQualCuts="-A pt20 muID 'LepGood_mediumMuonId > 0'"
EleQualCuts="-A pt20 eleID '(LepGood_mvaIdPhys14 >=0.73+(0.57-0.73)*(abs(LepGood_eta)>0.8)+(+0.05-0.57)*(abs(LepGood_eta)>1.479) || abs(LepGood_pdgId) == 13)'"
DxyCut="-A pt20 dxy_tight 'LepGood_sip3d < 4'"
EleAdditionalCuts="-A pt20 eleaddcuts '(abs(LepGood_pdgId) == 13 || (LepGood_convVeto && LepGood_lostHits == 0))'"
TightCharge="-A pt20 tightcharge '(LepGood_tightCharge > (abs(LepGood_pdgId) == 11))'"

JetSel="-A pt20 jet 'nJet40 >= 1 && minMllAFAS > 12'"
#CHECK THIS


LooseMuSel=' ' .join([LooseLepSel,AnyLepSel,IsMu])
LooseEleSel=' ' .join([LooseLepSel,AnyLepSel,IsEle])

MuIdOnly=' '.join([LooseLepSel,AnyLepSel,IsMu,MuQualCuts,DxyCut,TightCharge])
EleIdOnly=' '.join([LooseLepSel,AnyLepSel,IsEle,EleQualCuts,DxyCut,EleAdditionalCuts,TightCharge])

MultiIso="-A pt20 multiiso 'multiIso_multiWP(LepGood_pdgId,LepGood_pt,LepGood_eta,LepGood_miniRelIso,LepGood_jetPtRatio,LepGood_jetPtRel,2) > 0'"

#SipDen="-A pt20 siploose 'LepGood_sip3d < 4'"
#CommonDen="${SipDen} ${JetDen}"

runs=[]
runs.append(["multiIso_MuIdOnly",'multiIso',MuIdOnly])
runs.append(["multiIso_EleIdOnly",'multiIso',EleIdOnly])
runs.append(["multiIso_AND_MuonId_LooseMuSel",'multiIso_AND_MuonId',LooseMuSel])
runs.append(["multiIso_AND_EleId_LooseEleSel",'multiIso_AND_EleId',LooseEleSel])
runs.append(["MuonId_LooseMuSel",'MuonId',LooseMuSel])
runs.append(["EleId_LooseEleSel",'EleId',LooseEleSel])


for run in runs:
    run[2] += ' '+LowerCut
    B0=' '.join([BASE,PATH,"susy-multilepton/susy_2lss_fake_rate_sels.txt","susy-multilepton/susy_2lss_fake_rate_xvars.txt","--groupBy cut","-o "+OUTDIR+'_'+run[0]+'/plots.root'])
    B0 += " --legend=TL  --yrange 0 0.6 --showRatio --ratioRange 0.31 1.69 --xcut 10 999"
    B0 += ' -p QCDMu_red'
    B0 += ' --sP '+run[1]
    B0 += ' '+run[2]
    B0 += ' --sP pt_.*'
#    print '( '+B0+' ) &'
    print B0






