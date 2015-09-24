#!/bin/bash

export ODIR="~/www/25ns_run2015d_upto4396"
export MYTREEDIR="~/work/cmgtools/trees25"
export MYLUMI="0.151"

export EXE="python mcPlots.py"
export MYMCC="--mcc susy-multilepton/first-data/susy_jetPtRatioL1Corr.txt"
export WDIR="susy-multilepton/first-data-new"
export COMMOPT='--s2v --tree treeProducerSusyMultilepton --noErrorBandOnRatio  --rspam "%(lumi) (13 TeV)  " --lspam "#bf{CMS} #it{Preliminary}" --legendBorder=0 --legendFontSize 0.055 --legendWidth=0.35 --showRatio --maxRatioRange 0 2 --showRatio --poisson -j 8 -f --sp ".*"'

export SELECTIONS="ZtoMuMu"
#export SELECTIONS="ZtoEE ZtoMuMu ttbar Wl Zl ttbar_semiLeptonic"

for SEL in ${SELECTIONS}
do
    echo ${EXE} ${WDIR}/mca_13tev.txt ${WDIR}/cuts_${SEL}.txt ${WDIR}/plots_${SEL}.txt ${COMMOPT} -P ${MYTREEDIR} -l ${MYLUMI} ${MYMCC} --scaleSigToData --pdir ${ODIR}/${SEL}/ScaleSigToData
    echo ${EXE} ${WDIR}/mca_13tev.txt ${WDIR}/cuts_${SEL}.txt ${WDIR}/plots_${SEL}.txt ${COMMOPT} -P ${MYTREEDIR} -l ${MYLUMI} ${MYMCC} --pdir ${ODIR}/${SEL}/ScaleSigToLumi
done
