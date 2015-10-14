#!/bin/bash

T="/afs/cern.ch/work/p/peruzzi/ra5trees/ra5sync_131015"
CORE="-P $T --s2v --tree treeProducerSusyMultilepton"
CORE="${CORE} -F sf/t {P}/0_allFriends_v1/evVarFriend_{cname}.root"
CORE="${CORE} -X exclusive --mcc susy-multilepton/susy_2lssinc_lepchoice_multiiso.txt --mcc susy-multilepton/susy_2lssinc_triggerdefs.txt"

POST="";
WHAT="$1"; shift;
if [[ "$WHAT" == "mccounts" ]]; then
    GO="python mcAnalysis.py $CORE mca-Spring15-sync.txt susy-multilepton/susy_2lss_multiiso.txt -p TTWv2_RA5_sync -f -G -u "
    POST="| awk '/all/{print \$2}' "
elif [[ "$WHAT" == "mcyields" ]]; then
    GO="python mcAnalysis.py $CORE mca-Spring15-sync.txt susy-multilepton/susy_2lss_multiiso.txt -p TTWv2_RA5_sync  -f -G"
elif [[ "$WHAT" == "mcplots" ]]; then
    GO="python mcPlots.py $CORE mca-Spring15-sync.txt susy-multilepton/susy_2lss_multiiso.txt -f -G -p TTWv2_RA5_sync -j 8 -f --legendWidth 0.30 susy-multilepton/susy_2lss_plots.txt"
elif [[ "$WHAT" == "mcdumps" ]]; then
    FMT='"{run:1d} {lumi:9d} {evt:12d}\t{nLepGood_Mini:2d}\t{LepGood1_pdgId:+2d} {LepGood1_pt:5.1f}\t{LepGood2_pdgId:+2d} {LepGood2_pt:5.1f}\t{nJet40}\t{nBJetMedium25:2d}\t{met_pt:5.1f}\t{htJet40j:6.1f}\t{SRTV_Mini:2d}"'
    GO="python mcDump.py $CORE mca-Spring15-sync.txt susy-multilepton/susy_2lss_multiiso.txt -p TTWv2_RA5_sync  $FMT"
    POST="| sort -n -k1 -k2"
else
    echo "I don't know what you want"
    exit;
fi

SAVE="${GO}"
for LL  in ee em mm ll; do 
for SR  in 0 10 20 30; do # 0X 1X 2X 3X; do 
for LPt in hh hl; do
#for LL  in ll; do 
#for SR  in 0; do # 0X 1X 2X 3X; do 
#for LPt in hh; do
for MOD in multiiso; do #oldpresel ptrel miniiso; do

GO="${SAVE}"
case $SR in
0)   GO="${GO} -R nBjet nBjet0 'nBJetMedium25 >= 0' " ;;
00)  GO="${GO} -R nBjet nBjet0 'nBJetMedium25 == 0' " ;;
10)  GO="${GO} -R nBjet nBjet1 'nBJetMedium25 == 1' " ;;
20)  GO="${GO} -R nBjet nBjet2 'nBJetMedium25 == 2' " ;;
20+)  GO="${GO} -R nBjet nBjet2 'nBJetMedium25 >= 2' " ;;
30)  GO="${GO} -R nBjet nBjet3 'nBJetMedium25 >= 3' " ;;
esac;

case $LL in
ee)  GO="${GO} -R anyll ee 'abs(LepGood1_pdgId) == 11 && abs(LepGood2_pdgId) == 11' -A alwaystrue trig_ee Triggers_ee" ;;
em)  GO="${GO} -R anyll em 'abs(LepGood1_pdgId) != abs(LepGood2_pdgId)' -A alwaystrue trig_em Triggers_em" ;;
mm)  GO="${GO} -R anyll mm 'abs(LepGood1_pdgId) == 13 && abs(LepGood2_pdgId) == 13' -A alwaystrue trig_mm Triggers_mm" ;;
ll)  GO="${GO} -A alwaystrue trig_ll '(abs(LepGood1_pdgId) != 11 || abs(LepGood2_pdgId) != 11 || Triggers_ee) && (abs(LepGood1_pdgId) != 13 || abs(LepGood2_pdgId) != 13 || Triggers_mm) && (abs(LepGood1_pdgId)==abs(LepGood2_pdgId) || Triggers_em)'" ;;
esac;
case $LPt in
hl)  GO="${GO} -I lep2_pt25" ;;
ll)  GO="${GO} -I lep1_pt25 -X lep2_pt25" ;;
ii)  GO="${GO} -X lep1_pt25 -X lep2_pt25" ;;
esac;
case $MOD in
oldpresel) GO="${GO//multiiso/oldpresel} " ;;
miniiso)   GO="${GO//multiiso/miniiso} "   ;;
ptrel)     GO="${GO//multiiso/ptrel} "     ;;
esac;

if [[ "${WHAT}" == "mcplots" || "${WHAT}" == "mcrocs" ]]; then
    if [[ "${WHAT}" == "mcplots" ]]; then
        echo "$GO --pdir /afs/cern.ch/user/p/peruzzi/www/ra5sync//2lss_${MOD}/${LL}_pt_${LPt}/${SR}${PF}/"
    else
        echo "$GO -o plots/72X/v2/4fb/vars/2lss_${MOD}/${LL}_pt_${LPt}/${SR}${PF}/rocs.root"
    fi
else
    echo "echo; echo \" ===== SR $SR${PF} $LL $LPt $MOD $LId ===== \"; $GO $POST"
fi

done
done
done
done
