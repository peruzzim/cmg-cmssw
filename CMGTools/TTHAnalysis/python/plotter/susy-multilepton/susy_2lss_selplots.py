#!/usr/bin/env python

ODIR="test_ra5plots_oct22_mytestsigs"

T="-P /data1/p/peruzzi/TREES_74X_161015_MiniIso"
CORE="%s --s2v --tree treeProducerSusyMultilepton -F sf/t {P}/0_allFriends_v1/evVarFriend_{cname}.root -X exclusive --mcc susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt --mcc susy-multilepton/susy_2lssinc_triggerdefs.txt"%T
GO="python mcPlots.py %s mca-Spring15-analysis-unblinded.txt susy-multilepton/susy_2lss_multiiso.txt -f -j 8 --legendWidth 0.30 --showRatio --maxRatioRange 0 2 susy-multilepton/susy_2lss_selplots.txt"%CORE
GO="%s -A alwaystrue trig_ll '(abs(LepGood1_pdgId) != 11 || abs(LepGood2_pdgId) != 11 || Triggers_ee) && (abs(LepGood1_pdgId) != 13 || abs(LepGood2_pdgId) != 13 || Triggers_mm) && (abs(LepGood1_pdgId)==abs(LepGood2_pdgId) || Triggers_em)'"%GO

PU_UNBL = "--FMC sf/t {P}/1_puWeights_v2_run2015D_unblindedjson/evVarFriend_{cname}.root -W vtxWeight -l 0.13314"
PU_ALL = "--FMC sf/t {P}/1_puWeights_v3_run2015D_upto258750/evVarFriend_{cname}.root -W vtxWeight -l 1.26388"

SAVE=GO

TIGHT="(multiIso_multiWP(LepGood_pdgId,LepGood_pt,LepGood_eta,LepGood_miniRelIso,LepGood_jetPtRatiov2,LepGood_jetPtRelv2,2) && (abs(LepGood_pdgId)!=11 || mvaIdSpring15(LepGood_pdgId,LepGood_eta,LepGood_mvaIdSpring15,3,0)))"

addsigs = True
SIG = "--showIndivSigs" if addsigs else "--xp 'T1.*','T5.*','T6.*'"

for LPt in ['hh','hl','ll']:
    for group in ["","--pgroup 'Fakes + flips':='.*fakes.*','.*flips.*'"]:
        GO=SAVE # BR and SR regions, all json (no data)
        if LPt=='hh': GO="%s"%GO
        elif LPt=='hl': GO="%s -I lep2_pt25"%GO
        elif LPt=='ll': GO="%s -I lep1_pt25 -X lep2_pt25"%GO
        print "%s %s %s --sP BR --xp data --pdir /afs/cern.ch/user/p/peruzzi/www/%s/%s%s %s"%(GO,SIG,PU_ALL,ODIR,LPt,'_group' if group!='' else '',group)
        GO2="%s -A alwaystrue TT '((%s) + (%s) == 2)'"%(GO,TIGHT.replace("LepGood","LepGood1"),TIGHT.replace("LepGood","LepGood2"))
        GO2=GO2.replace("susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt","susy-multilepton/susy_2lssinc_lepchoice_FO.txt")
        GO2=GO2.replace("0_allFriends_v1","2_leptonJetRecleanerFO_v1")
        print "%s %s %s --sP BR --xp data --pdir /afs/cern.ch/user/p/peruzzi/www/%s/%s%s_sortFO %s"%(GO2,SIG,PU_ALL,ODIR,LPt,'_group' if group!='' else '',group)
        if LPt=='hh': GO="%s -A alwaystrue SR_hh '(SR>0 && SR<=32)'"%GO
        elif LPt=='hl': GO="%s -A alwaystrue SR_hl '(SR>32 && SR<=58)'"%GO
        elif LPt=='ll': GO="%s -A alwaystrue SR_ll 'SR>58'"%GO
        print "%s %s %s --sP SR_%s --xp data --pdir /afs/cern.ch/user/p/peruzzi/www/%s/%s%s %s"%(GO,SIG,PU_ALL,ODIR,LPt,LPt,'_group' if group!='' else '',group)

GO=SAVE
GO="%s -R same-sign OS 'LepGood1_charge*LepGood2_charge<0' --xP 'SR.*' --xP BR -X lep1_pt25 -X lep2_pt25"%GO # OS, inclusive baseline, all json
GO=GO.replace("mca-Spring15-analysis-unblinded.txt","mca-Spring15-analysis-all.txt")
print "%s %s --pdir /afs/cern.ch/user/p/peruzzi/www/%s/OS_BR"%(GO,PU_ALL,ODIR)

GO=SAVE
GO="%s --xP 'SR.*' --xP BR -X lep1_pt25 -X lep2_pt25"%GO # SS, inclusive baseline, tight + FO non tight, all json
GO="%s -A alwaystrue TF '((%s) + (%s) == 1)'"%(GO,TIGHT.replace("LepGood","LepGood1"),TIGHT.replace("LepGood","LepGood2"))
GO=GO.replace("susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt","susy-multilepton/susy_2lssinc_lepchoice_FO.txt")
GO=GO.replace("0_allFriends_v1","2_leptonJetRecleanerFO_v1")
GO=GO.replace("mca-Spring15-analysis-unblinded.txt","mca-Spring15-analysis-all.txt")
print "%s %s --pdir /afs/cern.ch/user/p/peruzzi/www/%s/SS_TightFake_BR"%(GO,PU_ALL,ODIR)

GO=SAVE
GO="%s --xP 'SR.*' --xP BR -X lep1_pt25 -X lep2_pt25"%GO # SS, inclusive baseline, unblinded json
print "%s %s %s --pdir /afs/cern.ch/user/p/peruzzi/www/%s/SS_BR --pgroup 'Fakes + flips':='TT','DY','WJets','Single top'"%(GO,SIG,PU_UNBL,ODIR)

