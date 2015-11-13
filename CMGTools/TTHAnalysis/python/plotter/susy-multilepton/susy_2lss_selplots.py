#!/usr/bin/env python

ODIR="test_ra5plots_nov13_allplots"

#lumi_unblinded = 0.13314
lumi_all = 1.28

def base(unbl=False):

    T="-P /data1/p/peruzzi/skimmed_nov12"
    CORE="%s --neg --s2v --tree treeProducerSusyMultilepton -F sf/t {P}/3_recleaner/evVarFriend_{cname}.root -F sf/t {P}/4_choice/evVarFriend_{cname}.root --mcc susy-multilepton/susy_2lssinc_triggerdefs.txt"%T
    GO="python mcPlots.py %s susy-multilepton/mca-Spring15-analysis-all.txt susy-multilepton/susy_2lss_multiiso.txt -f -j 8 --lspam '#bf{CMS} #it{Preliminary}' --legendWidth 0.35 --showRatio --maxRatioRange 0 2 susy-multilepton/susy_2lss_selplots.txt"%CORE
#    GO="%s -A alwaystrue trig_ll '(abs(LepGood1_pdgId) != 11 || abs(LepGood2_pdgId) != 11 || Triggers_ee) && (abs(LepGood1_pdgId) != 13 || abs(LepGood2_pdgId) != 13 || Triggers_mm) && (abs(LepGood1_pdgId)==abs(LepGood2_pdgId) || Triggers_em)'"%GO

#    PU_UNBL = " --FMC sf/t {P}/1_puWeights_v2_run2015D_unblindedjson/evVarFriend_{cname}.root -l %f -W 'vtxWeight*btagMediumSF_Mini' --xp '.*blinded.*'"%lumi_unblinded
#    mydata = []
#    PU_ALL = " --FMC sf/t {P}/1_puWeights_v3_run2015D_upto258750/evVarFriend_{cname}.root -W 'vtxWeight*btagMediumSF_Mini' -l %f "%lumi_all +" ".join(["--pgroup data:='data','_blinded_data'"]+["--pgroup %s:='%s','_blinded%s'"%(m,m,m) for m in mydata])

    PU_ALL = " --FMC sf/t {P}/1_pu_runD_258750/evVarFriend_{cname}.root -W 'vtxWeight*btagMediumSF_Mini' -l %f "%lumi_all

    if unbl: return GO+PU_ALL
    else: raise RuntimeError

def BRptreg(GO,LPt):
    if LPt=='hh': return GO
    elif LPt=='hl': return "%s -I lep2_pt25"%GO
    elif LPt=='ll': return "%s -I lep1_pt25 -X lep2_pt25"%GO
    elif LPt=='ii': return  "%s -X lep1_pt25 -X lep2_pt25"%GO
def SRptreg(GO,LPt):
    GO = BRptreg(GO,LPt)
    if LPt=='hh': return "%s -A alwaystrue SR_hh '(SR>0 && SR<=32)'"%GO
    elif LPt=='hl': return "%s -A alwaystrue SR_hl '(SR>32 && SR<=58)'"%GO
    elif LPt=='ll': return "%s -A alwaystrue SR_ll 'SR>58'"%GO
    elif LPt=='ii': return "%s -A alwaystrue SR_ii 'SR>0'"%GO

def procs(GO,mylist):
    return GO+' '+" ".join([ '-p %s'%l for l in mylist ])
def sigprocs(GO,mylist):
    return procs(GO,mylist)+' --showIndivSigs --noStackSig'
def runIt(GO,name,plots=[],noplots=[]):
#    print GO,' '.join(['--sP %s'%p for p in plots]),' '.join(['--xP %s'%p for p in noplots]),"--pdir /afs/cern.ch/user/p/peruzzi/%s/%s"%(ODIR,name) # no www
    print GO,' '.join(['--sP %s'%p for p in plots]),' '.join(['--xP %s'%p for p in noplots]),"--pdir /afs/cern.ch/user/p/peruzzi/www/%s/%s"%(ODIR,name)
def add(GO,opt):
    return '%s %s'%(GO,opt)
def setwide(x):
    x2 = add(x,'--wide')
    x2 = x2.replace('--legendWidth 0.35','--legendWidth 0.20')
    return x2

if __name__ == '__main__':


    for LPt in ['ii']:
        # BR/SR data/MC
        x = base(True)
        x = procs(x,['_standard_.*','data'])
        x1 = BRptreg(x,LPt)
        runIt(x1,'dataMC_nosig_baseline_'+LPt,['BR.*'])
        x2 = SRptreg(x,LPt)
        if LPt=='ii': x2 = setwide(x2)
        runIt(x2,'dataMC_nosig_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])

    for LPt in ['ii']:
        # BR/SR data/MC
        x = base(True)
        x = procs(x,['_standard_.*','data'])
        x = sigprocs(x,['_sig_.*'])
        x1 = BRptreg(x,LPt)
        runIt(x1,'dataMC_baseline_'+LPt,['BR.*'])
        x2 = SRptreg(x,LPt)
        if LPt=='ii': x2 = setwide(x2)
        runIt(x2,'dataMC_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])

    for LPt in ['ii']:
        # BR/SR data/MC
        x = base(True)
        x = procs(x,['_standard_.*'])
        x = sigprocs(x,['_sig_.*'])
        x1 = BRptreg(x,LPt)
        runIt(x1,'dataMC_signodata_baseline_'+LPt,['BR.*'])
        x2 = SRptreg(x,LPt)
        if LPt=='ii': x2 = setwide(x2)
        runIt(x2,'dataMC_signodata_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])


#    for LPt in ['ii','hh','hl','ll']:
    for LPt in ['ii']:
        # BR/SR data / fakes prediction - prompt rate + flips prediction + MC prompt
        x = base(True)
        x = procs(x,['data','_fakesappl_data','_promptratesub','_flipsappl_data','_standard_prompt_.*'])
        x = add(x,"--plotgroup _fakesappl_data+=_promptratesub --plotgroup _fakesappl_data_ewk_Up+=_promptratesub_ewk_Up --plotgroup _fakesappl_data_ewk_Dn+=_promptratesub_ewk_Dn")
        x = x.replace('susy_2lss_selplots.txt','susy_2lss_coarse_selplots.txt')
        x1 = BRptreg(x,LPt)
        runIt(x1,'dataPrediction_nosig_baseline_'+LPt,[],['SR_.*'])
#        x1b = add(x1,"-A alwaystrue 1b '(nBJetMedium25==1)'")
#        runIt(x1b,'dataPrediction_nosig_baseline_1b_'+LPt,[],['BR.*','SR_.*'])
#        x1nb = add(x1,"-A alwaystrue not1b '(nBJetMedium25!=1)'")
#        runIt(x1nb,'dataPrediction_nosig_baseline_not1b_'+LPt,[],['BR.*','SR_.*'])
#        x1np = add(x1,"-A alwaystrue lep6090_hh '(LepGood1_conePt>60 && LepGood1_conePt<90 && LepGood2_conePt>25)'")
#        runIt(x1np,'dataPrediction_nosig_baseline_HH_pt6090_'+LPt,[],['BR.*','SR_.*'])
        x2 = SRptreg(x,LPt)
        runIt(x2,'dataPrediction_nosig_SR_'+LPt,[],['BR.*','SR_.*'])
        if LPt=='ii':
            x2 = setwide(x2)
        runIt(x2,'dataPrediction_nosig_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])

#    for LPt in ['ii']:
#        x = base(True)
#        x = procs(x,['data','_fakesappl_data.*','_promptratesub.*','_flipsappl_data.*','_standard_prompt_.*'])
#        x = sigprocs(x,['_sig_.*'])
#        x = add(x,"--plotgroup _fakesappl_data+=_promptratesub --plotgroup _fakesappl_data_ewk_Up+=_promptratesub_ewk_Up --plotgroup _fakesappl_data_ewk_Dn+=_promptratesub_ewk_Dn")
#        x = SRptreg(x,LPt)
#        x = add(x,"--AP --doPrintOutNev 'SR'")
#        runIt(x,'dataPrediction_withsig_allprocesses_fordatacard_SR_'+LPt,['SR_%s'%LPt])


    for LPt in ['ii']:
        # BR/SR all json data full prediction / MC (no poisson)
        x = base(True)
        x = procs(x,['data','_promptratesub','_standard_.*'])
        x = add(x,"--plotgroup data+='_promptratesub'")
        x = add(x,'--no-poisson')
        x = x.replace('mca-Spring15-analysis-all.txt','mca-Spring15-analysis-dataPrediction.txt')
        x1 = BRptreg(x,LPt)
        runIt(x1,'MCvsDataDriven_baseline_'+LPt,[],['SR_.*'])
        x2 = SRptreg(x,LPt)
        if LPt=='ii':
            x2 = setwide(x2)
        runIt(x2,'MCvsDataDriven_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
        runIt(x2,'MCvsDataDriven_SR_'+LPt,[],['BR.*','SR_.*'])


    for LPt in ['ii']:
        # kin vars - all json data / MC fakes in application region
        x = base(True)
        x = procs(x,['data','_sideband_fakes_.*'])
        x = x.replace('mca-Spring15-analysis-all.txt','mca-Spring15-analysis-sideband.txt')
        x = x.replace('susy_2lss_selplots.txt','susy_2lss_coarse_selplots.txt')
        x = add(x,"-A alwaystrue safety '(!hasTT)'")
        x1 = BRptreg(x,LPt)
        runIt(x1,'kin_applicationFakes_baseline_'+LPt,[],['SR_.*'])
#        x2 = SRptreg(x,LPt)
#        runIt(x2,'kin_applicationFakes_SR_'+LPt,[],['BR.*','SR_.*'])
#        if LPt=='ii': x2 = setwide(x2)
#        runIt(x2,'kin_applicationFakes_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])


    for LPt in ['ii']:
        # kin vars - all json data / MC fakes in application region
        x = base(True)
        x = procs(x,['data','_sideband_fakes_.*'])
        x = x.replace('mca-Spring15-analysis-all.txt','mca-Spring15-analysis-sideband.txt')
        x = x.replace('susy_2lss_selplots.txt','susy_2lss_coarse_selplots.txt')
        x = add(x,"-A alwaystrue safety '(!hasTT)'")
        x = add(x,"-A alwaystrue only1fake '(hasTF)'")
        x1 = BRptreg(x,LPt)
        runIt(x1,'kin_T_FObnT_baseline_'+LPt,[],['SR_.*'])
#        x2 = SRptreg(x,LPt)
#        runIt(x2,'kin_T_FObnT_SR_'+LPt,[],['BR.*','SR_.*'])
#        if LPt=='ii': x2 = setwide(x2)
#        runIt(x2,'kin_T_FObnT_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])






#
#
#
#
#
##    for LPt in ['ii','hh','hl','ll']:
#    for LPt in ['ii']:
#        # kin vars - all json data / MC in flips application baseline region (OS)
#        x = base(True)
#        x = procs(x,['data','_OS_.*'])
#        x = x.replace('mca-Spring15-analysis-all.txt','mca-Spring15-analysis-OS.txt')
#        x = x.replace('/data1/p/peruzzi/skimmed_nov06_mix','/data1/p/peruzzi/skimmed_nov06_mix_forOS')
#        x = add(x,"-A alwaystrue safety '(!hasTT)'")
#        x1 = BRptreg(x,LPt)
#        runIt(x1,'kin_applicationFlips_OS_baseline_'+LPt,[],['SR_.*'])
##        x2 = SRptreg(x,LPt)
##        runIt(x2,'kin_applicationFlips_OS_SR_'+LPt,[],['BR.*','SR_.*'])
##        if LPt=='ii': x2 = setwide(x2)
##        runIt(x2,'kin_applicationFlips_OS_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
#
##    for LPt in ['ii','hh','hl','ll']:
#    for LPt in ['ii']:
#        # kin vars - all json data / MC in flips application baseline region (OS), Z/g* veto, 1b
#        x = base(True)
#        x = procs(x,['data','_OS_.*'])
#        x = x.replace('mca-Spring15-analysis-all.txt','mca-Spring15-analysis-OS.txt')
#        x = x.replace('/data1/p/peruzzi/skimmed_nov06_mix','/data1/p/peruzzi/skimmed_nov06_mix_forOS')
#        x = add(x,"-A alwaystrue safety '(!hasTT)'")
##        x = add(x,"-A alwaystrue mllZgVeto '(mass_2(LepGood1_pt,LepGood1_eta,LepGood1_phi,LepGood1_mass, LepGood2_pt,LepGood2_eta,LepGood2_phi,LepGood2_mass)>12 && ((mass_2(LepGood1_pt,LepGood1_eta,LepGood1_phi,LepGood1_mass, LepGood2_pt,LepGood2_eta,LepGood2_phi,LepGood2_mass)<76)||(mass_2(LepGood1_pt,LepGood1_eta,LepGood1_phi,LepGood1_mass, LepGood2_pt,LepGood2_eta,LepGood2_phi,LepGood2_mass)>106)))'")
#        x = BRptreg(x,LPt)
# #       x1 = add(x,"-A alwaystrue 1b '(nBJetMedium25>0)'")
# #       runIt(x1,'kin_OS_baseline_1b_'+LPt,[],['BR.*','SR_.*'])
#        x1 = add(x,"-A alwaystrue OF '(abs(LepGood1_pdgId)!=abs(LepGood2_pdgId))'")
##        runIt(x1,'kin_OS_baseline_OF_'+LPt,[],['BR.*','SR_.*'])
#        runIt(x1,'kin_OS_baseline_OF_'+LPt,['BR.*'],[])
#
#
#
#
#
#
#
#    for LPt in ['ii']:
#        # BR/SR data / fakes prediction - prompt rate + flips prediction + MC prompt
#        x = base(True)
#        x = procs(x,['data','_fakesappl_data','_promptratesub','_flipsappl_data','_standard_prompt_.*'])
#        x = sigprocs(x,['_sig_.*'])
#        x = x.replace('susy_2lss_selplots.txt','susy_2lss_coarse_selplots.txt')
#        x2 = SRptreg(x,LPt)
#        if LPt=='ii':
#            x2 = setwide(x2)
#            x2 = add(x2,"--doPrintOutNev 'SR'")
#        runIt(x2,'dataPrediction_noPromptRateSub_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
#
#
#    for LPt in ['ii']:
#        # BR/SR data / fakes prediction - prompt rate + flips prediction + MC prompt
#        x = base(True)
#        x = procs(x,['data','_fakesappl_data','_promptratesub','_flipsappl_data','_standard_prompt_.*'])
#        x = sigprocs(x,['_sig_.*'])
#        x = add(x,"--plotgroup _fakesappl_data+='_promptratesub'")
#        x = x.replace('susy_2lss_selplots.txt','susy_2lss_coarse_selplots.txt')
#        x = SRptreg(x,LPt)
#        x1 = add(x,"-A alwaystrue SR10 'SR==10'")
#        runIt(x1,'dataPrediction_SR10_'+LPt,[],['BR.*','SR_.*'])
#        x2 = add(x,"-A alwaystrue mll250 'mass_2(LepGood1_conePt,LepGood1_eta,LepGood1_phi,LepGood1_mass, LepGood2_conePt,LepGood2_eta,LepGood2_phi,LepGood2_mass)>250'")
#        runIt(x2,'dataPrediction_SR_mll250_'+LPt,[],['BR.*','SR_.*'])
#        x2 = add(x2,"--wide")
#        runIt(x2,'dataPrediction_SR_mll250_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
#        x3 = add(x,"-A alwaystrue exactly1b nBJetMedium25==1")
#        runIt(x3,'dataPrediction_SR_1b_'+LPt,[],['BR.*','SR_.*'])
#        x3 = add(x3,"--wide")
#        runIt(x3,'dataPrediction_SR_1b_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
#
#
#
#    for LPt in ['ii','hh','hl','ll']:
#        # BR/SR unblinded data / fakes prediction - prompt rate + flips prediction + MC prompt
#        x = base(True)
#        x = procs(x,['_fakesappl_data','_promptratesub','_flipsappl_data','_standard_prompt_.*'])
#        x = x.replace("-l %f"%lumi_all,"-l %f"%3.)
#        x = add(x,"--scaleplot _fakesappl_data*=%f"%(3./lumi_all))
#        x = add(x,"--scaleplot _flipsappl_data*=%f"%(3./lumi_all))
#        x = add(x,"--plotgroup _fakesappl_data+='_promptratesub'")
#        x1 = BRptreg(x,LPt)
#        runIt(x1,'dataPrediction_scaled3fb_nodata_baseline_'+LPt,['BR.*'])
#        x2 = SRptreg(x,LPt)
#        if LPt=='ii': x2 = setwide(x2)
#        runIt(x2,'dataPrediction_scaled3fb_nodata_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
#
#    for LPt in ['ii']:
#        # BR/SR unblinded data / fakes prediction - prompt rate + flips prediction + MC prompt
#        x = base(True)
#        x = procs(x,['_fakesappl_data','_promptratesub'])
#        x2 = SRptreg(x,LPt)
#        if LPt=='ii': x2 = setwide(x2)
#        runIt(x2,'dataPrediction_nodata_splittedpromptsub_debug_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
#        
#
#    for LPt in ['ii']:
#        # BR/SR all json data full prediction / MC (no poisson)
#        x = base(True)
#        x = procs(x,['data','_sideband_.*'])
#        x = x.replace('mca-Spring15-analysis-all.txt','mca-Spring15-analysis-sideband.txt')
#        x2 = SRptreg(x,LPt)
#        if LPt=='ii':
#            x2 = setwide(x2)
#            x2 = add(x2,"--doPrintOutNev 'SR'")
#        runIt(x2,'DataApplFakesCount_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
#
#
#
#
#
#
#
#
#
#
#    for LPt in ['ii','hh','hl','ll']:
#        if LPt=='ii': # kin vars - all json data / full prediction in specific SR, merged (LPt selection relaxed)
#            x = base(True)
#            x = x.replace('susy_2lss_selplots.txt','susy_2lss_coarse_selplots.txt')
#            x = procs(x,['data','_fakesappl_data','_promptratesub','_flipsappl_data','_standard_prompt_.*'])
#            x = add(x,"--plotgroup _fakesappl_data+='_promptratesub'")
#            x = add(x,"-A alwaystrue specialSR 'SR==9 || SR==33 || SR==39'")
#            x = SRptreg(x,LPt)
#            runIt(x,'fullSpecialSR_kinonly_'+LPt,[],['BR.*','SR_.*'])
#    for LPt in ['ii','hh','hl','ll']:
#        if LPt=='ii': # kin vars - all json data / full prediction in specific SR, merged (LPt selection relaxed)
#            x = base(True)
#            x = x.replace('susy_2lss_selplots.txt','susy_2lss_coarse_selplots.txt')
#            x = procs(x,['data','_standard_prompt_.*','_standard_fakes_.*'])
#            x = add(x,"-A alwaystrue specialSR 'SR==9 || SR==33 || SR==39'")
#            x = SRptreg(x,LPt)
#            runIt(x,'fullSpecialSR_MCfakes_kinonly_'+LPt,[],['BR.*','SR_.*'])
#
#    for LPt in ['ii']:
#        # signal b-tag uncertainty
#        x = base(True)
#        x = x.replace('mca-Spring15-analysis-all.txt','mca-Spring15-analysis-btagSF.txt')
##        x = add(x,"--pgroup _standard_prompt_all:='_standard_prompt_.*'")
##        x = add(x,"--pgroup _btagUp_standard_prompt_all:='_btagUp_standard_prompt_.*'")
##        x = add(x,"--pgroup _btagDown_standard_prompt_all:='_btagDown_standard_prompt_.*'")
#        if LPt=='ii': x = setwide(x)
#        x = add(x,'--plotmode nostack')
#        x = SRptreg(x,LPt)
#        runIt(x,'sig_prompt_bTag_variations_SR_'+LPt,['SR_%s'%LPt,'SR_%s_log'%LPt])
