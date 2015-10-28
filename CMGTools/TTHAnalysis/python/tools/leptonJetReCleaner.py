from CMGTools.TTHAnalysis.treeReAnalyzer import *
from CMGTools.TTHAnalysis.tools.conept import conept

class LeptonJetReCleaner:
    def __init__(self,label,looseLeptonSel,cleaningLeptonSel,FOLeptonSel,tightLeptonSel,cleanJet,selectJet,isMC=True):
        self.label = "" if (label in ["",None]) else ("_"+label)
        self.looseLeptonSel = looseLeptonSel
        self.cleaningLeptonSel = cleaningLeptonSel # applied on top of looseLeptonSel
        self.FOLeptonSel = FOLeptonSel # applied on top of looseLeptonSel
        self.tightLeptonSel = tightLeptonSel # applied on top of looseLeptonSel
        self.cleanJet = cleanJet
        self.selectJet = selectJet
        self.isMC = isMC
    def listBranches(self):
        label = self.label
        biglist = [
            ("nLepGood","I"), ("LepGood_conePt","F",20,"nLepGood"), # calculate conept
            ("nLepLoose"+label, "I"), ("iL"+label,"I",20,"nLepLoose"+label), # passing loose
            ("nLepLooseVeto"+label, "I"), ("iLV"+label,"I",20,"nLepLooseVeto"+label), # passing loose + veto
            ("nLepCleaning"+label, "I"), ("iC"+label,"I",20,"nLepCleaning"+label), # passing cleaning
            ("nLepCleaningVeto"+label, "I"), ("iCV"+label,"I",20,"nLepCleaningVeto"+label), # passing cleaning + veto
            ("nLepFO"+label, "I"), ("iF"+label,"I",20,"nLepFO"+label), # passing FO
            ("nLepFOVeto"+label, "I"), ("iFV"+label,"I",20,"nLepFOVeto"+label), # passing FO + veto
            ("nLepTight"+label, "I"), ("iT"+label,"I",20,"nLepTight"+label), # passing tight
            ("nLepTightVeto"+label, "I"), ("iTV"+label,"I",20,"nLepTightVeto"+label), # passing tight + veto
            ("isLepLoose"+label,"I",20,"nLepGood"),("isLepLooseVeto"+label,"I",20,"nLepGood"),
            ("isLepCleaning"+label,"I",20,"nLepGood"),("isLepCleaningVeto"+label,"I",20,"nLepGood"),
            ("isLepFO"+label,"I",20,"nLepGood"),("isLepFOVeto"+label,"I",20,"nLepGood"),
            ("isLepTight"+label,"I",20,"nLepGood"),("isLepTightVeto"+label,"I",20,"nLepGood"),
            ("nJetSel"+label, "I"), ("iJ"+label,"I",20,"nJetSel"+label), # index >= 0 if in Jet; -1-index (<0) if in DiscJet
            ("nJet40"+label, "I"), "htJet40j"+label, ("nBJetLoose40"+label, "I"), ("nBJetMedium40"+label, "I"),
            ("nJet25"+label, "I"), "htJet25j"+label, ("nBJetLoose25"+label, "I"), ("nBJetMedium25"+label, "I"), 
            ]
        for jfloat in "pt eta phi mass btagCSV rawPt".split():
            biglist.append( ("JetSel"+label+"_"+jfloat,"F",20,"nJetSel"+label) )
        if self.isMC:
            biglist.append( ("JetSel"+label+"_mcPt",     "F",20,"nJetSel"+label) )
            biglist.append( ("JetSel"+label+"_mcFlavour","I",20,"nJetSel"+label) )
            biglist.append( ("JetSel"+label+"_mcMatchId","I",20,"nJetSel"+label) )
        return biglist

    def fillCollWithVeto(self,ret,refcollection,leps,lab,labext,selection,lepsforveto,ht=-1):
        ret['i'+lab] = [];
        ret['i'+lab+'V'] = [];
        for lep in leps:
            if (selection(lep) if ht<0 else selection(lep,ht)):
                    ret['i'+lab].append(refcollection.index(lep))
        ret['nLep'+labext] = len(ret['i'+lab])
        ret['isLep'+labext] = [(1 if i in ret['i'+lab] else 0) for i in xrange(len(refcollection))]
        lepspass = [ refcollection[il] for il in ret['i'+lab]  ]
        if lepsforveto==None: lepsforveto = lepspass # if lepsforveto==None, veto selected leptons among themselves
        for lep in lepspass:
            if passMllTLVeto(lep, lepsforveto, 76, 106, True) and passMllTLVeto(lep, lepsforveto, 0, 12, True):
                ret['i'+lab+'V'].append(refcollection.index(lep))
        ret['nLep'+labext+'Veto'] = len(ret['i'+lab+'V'])
        ret['isLep'+labext+'Veto'] = [(1 if i in ret['i'+lab+'V'] else 0) for i in xrange(len(refcollection))]
        lepspassveto = [ refcollection[il] for il in ret['i'+lab+'V']  ]
        return (ret,lepspass,lepspassveto)

    def __call__(self,event):
        leps = [l for l in Collection(event,"LepGood","nLepGood")]
        for lep in leps: lep.conept = conept(lep.pt,lep.miniRelIso,lep.jetPtRatiov2,lep.jetPtRelv2,lep.pdgId,2)
        jetsc = [j for j in Collection(event,"Jet","nJet")]
        jetsd = [j for j in Collection(event,"DiscJet","nDiscJet")]
        (met, metphi)  = event.met_pt, event.met_phi
        ret = {}; jetret = {}

        lepsl = []; lepslv = [];
        ret, lepsl, lepslv = self.fillCollWithVeto(ret,leps,leps,'L','Loose',self.looseLeptonSel,None)
        lepsc = []; lepscv = [];
        ret, lepsc, lepscv = self.fillCollWithVeto(ret,leps,lepsl,'C','Cleaning',self.cleaningLeptonSel,lepsl)

        ### Define jets
        ret["iJ"] = []
        # 0. mark each jet as clean
        for j in jetsc+jetsd: j._clean = True if self.selectJet(j) else False
        # 1. associate to each lepton passing the cleaning selection its nearest jet 
        for lep in lepsc:
            best = None; bestdr = 0.4
            for j in jetsc+jetsd:
                dr = deltaR(lep,j)
                if dr < bestdr:
                    best = j; bestdr = dr
            if best is not None and self.cleanJet(lep,best,bestdr):
                best._clean = False
        # 2. compute the jet list
        for ijc,j in enumerate(jetsc):
            if not j._clean: continue
            ret["iJ"].append(ijc)
        for ijd,j in enumerate(jetsd):
            if not j._clean: continue
            ret["iJ"].append(-1-ijd)
        # 3. sort the jets by pt
        ret["iJ"].sort(key = lambda idx : jetsc[idx].pt if idx >= 0 else jetsd[-1-idx].pt, reverse = True)
        ret["nJetSel"] = len(ret["iJ"])
        # 4. compute the variables
        for jfloat in "pt eta phi mass btagCSV rawPt".split():
            jetret[jfloat] = []
        if self.isMC:
            for jmc in "mcPt mcFlavour mcMatchId".split():
                jetret[jmc] = []
        for idx in ret["iJ"]:
            jet = jetsc[idx] if idx >= 0 else jetsd[-1-idx]
            for jfloat in "pt eta phi mass btagCSV rawPt".split():
                jetret[jfloat].append( getattr(jet,jfloat) )
            if self.isMC:
                for jmc in "mcPt mcFlavour mcMatchId".split():
                    jetret[jmc].append( getattr(jet,jmc) )
        # 5. compute the sums
        ret["nJet25"] = 0; ret["htJet25j"] = 0; ret["nBJetLoose25"] = 0; ret["nBJetMedium25"] = 0
        ret["nJet40"] = 0; ret["htJet40j"] = 0; ret["nBJetLoose40"] = 0; ret["nBJetMedium40"] = 0
        for j in jetsc+jetsd:
            if not j._clean: continue
            if j.pt > 25:
                ret["nJet25"] += 1; ret["htJet25j"] += j.pt; 
                if j.btagCSV>0.423: ret["nBJetLoose25"] += 1
                if j.btagCSV>0.814: ret["nBJetMedium25"] += 1
            if j.pt > 40:
                ret["nJet40"] += 1; ret["htJet40j"] += j.pt; 
                if j.btagCSV>0.423: ret["nBJetLoose40"] += 1
                if j.btagCSV>0.814: ret["nBJetMedium40"] += 1

        # calculate FOs and tight leptons using the cleaned HT
        lepsf = []; lepsfv = [];
        ret, lepsf, lepsfv = self.fillCollWithVeto(ret,leps,lepsl,'F','FO',self.FOLeptonSel,lepsl,ret["htJet40j"])
        lepst = []; lepstv = [];
        ret, lepst, lepstv = self.fillCollWithVeto(ret,leps,lepsl,'T','Tight',self.tightLeptonSel,lepsl,ret["htJet40j"])

        ### attach labels and return
        fullret = {}
        fullret["nLepGood"]=len(leps)
        fullret["LepGood_conePt"] = [lep.conept for lep in leps]
        for k,v in ret.iteritems(): 
            fullret[k+self.label] = v
        for k,v in jetret.iteritems(): 
            fullret["JetSel%s_%s" % (self.label,k)] = v
        return fullret

def passMllVeto(l1, l2, mZmin, mZmax, isOSSF ):
    if  l1.pdgId == -l2.pdgId or not isOSSF:
        mz = (l1.p4() + l2.p4()).M()
        if mz > mZmin and  mz < mZmax:
            return False
    return True
def passMllTLVeto(lep, lepsl, mZmin, mZmax, isOSSF):
    for ll in lepsl:
        if ll == lep: continue
        if not passMllVeto(lep, ll, mZmin, mZmax, isOSSF):
            return False
    return True

def _tthlep_lepId(lep):
        #if lep.pt <= 10: return False
        if abs(lep.pdgId) == 13:
            if lep.pt <= 5: return False
            return True #lep.mediumMuonId > 0
        elif abs(lep.pdgId) == 11:
            if lep.pt <= 7: return False
            if not (lep.convVeto and lep.lostHits == 0): 
                return False
            return True #lep.mvaIdPhys14 > 0.73+(0.57-0.74)*(abs(lep.eta)>0.8)+(0.05-0.57)*(abs(lep.eta)>1.479)
        return False

def _susy2lss_lepId_CBloose(lep):
        if abs(lep.pdgId) == 13:
            if lep.pt <= 5: return False
            return True #lep.mediumMuonId > 0
        elif abs(lep.pdgId) == 11:
            if lep.pt <= 7: return False
            if not (lep.convVeto and lep.lostHits <= 1): 
                return False
            if not lep.mvaIdSpring15 > -0.70+(-0.83+0.70)*(abs(lep.eta)>0.8)+(-0.92+0.83)*(abs(lep.eta)>1.479):
                return False
            if not _susy2lss_idEmu_cuts(lep): return False
            return True
        return False

def _susy2lss_lepConePt1015(lep):
    if lep.conept <= (10 if abs(lep.pdgId)==13 else 15): return False
    return True

def _susy2lss_lepId_loosestFO(lep):
    if not _susy2lss_lepId_CBloose(lep): return False
    if abs(lep.pdgId) == 13:
        return lep.mediumMuonId > 0 and lep.tightCharge > 0
    elif abs(lep.pdgId) == 11:
        return (lep.convVeto and lep.tightCharge > 1 and lep.lostHits == 0)
    return False

def _susy2lss_lepId_tighterFO(lep):
    if not _susy2lss_lepId_loosestFO(lep): return False
    if abs(lep.pdgId)==11:
        if not lep.mvaIdSpring15 > -0.155+(-0.56+0.155)*(abs(lep.eta)>0.8)+(-0.76+0.56)*(abs(lep.eta)>1.479):
            return False
        if not _susy2lss_idIsoEmu_cuts(lep): return False
    return True

def _susy2lss_lepId_IPcuts(lep):
    if not lep.sip3d<4: return False
    if not (abs(lep.dxy)<0.05): return False
    if not (abs(lep.dz)<0.1): return False
    return True

def _susy2lss_lepId_CB(lep):
    if not _susy2lss_lepId_CBloose(lep): return False
    if not _susy2lss_lepId_IPcuts(lep): return False
    if abs(lep.pdgId) == 13:
        return lep.mediumMuonId > 0 and lep.tightCharge > 0
    elif abs(lep.pdgId) == 11:
        if not (lep.convVeto and lep.tightCharge > 1 and lep.lostHits == 0): 
            return False
        return lep.mvaIdSpring15 > 0.87+(0.60-0.87)*(abs(lep.eta)>0.8)+(0.17-0.60)*(abs(lep.eta)>1.479)
    return False

def _susy2lss_idEmu_cuts(lep):
    if (abs(lep.pdgId)!=11): return True
    if (lep.sigmaIEtaIEta>=(0.011 if abs(lep.etaSc)<1.479 else 0.031)): return False
    if (lep.hadronicOverEm>=0.08): return False
    if (abs(lep.dEtaScTrkIn)>=0.01): return False
    if (abs(lep.dPhiScTrkIn)>=(0.04 if abs(lep.etaSc)<1.479 else 0.08)): return False
    if (abs(lep.eInvMinusPInv)>=0.01): return False
    return True

def _susy2lss_idIsoEmu_cuts(lep):
    if (abs(lep.pdgId)!=11): return True
    if not _susy2lss_idEmu_cuts(lep): return False
    if (lep.ecalPFClusterIso>=0.45*lep.pt): return False
    if (lep.hcalPFClusterIso>=0.25*lep.pt): return False
    if (lep.dr03TkSumPt>=0.2*lep.pt): return False
    return True

def _susy2lss_multiIso(lep):
        if abs(lep.pdgId) == 13: A,B,C = (0.16,0.76,7.2)
        else:                    A,B,C = (0.12,0.80,7.2)
        return lep.miniRelIso < A and (lep.jetPtRatiov2 > B or lep.jetPtRelv2 > C)

#def _susy2lss_multiIso_withMiniIsoRelaxed_ConePtJetPtRatiov2(lep):
#        if abs(lep.pdgId) == 13: A,B,C = (0.4,0.76,7.2)
#        else:                    A,B,C = (0.4,0.80,7.2)
#        return lep.miniRelIso < A and (conept(lep.pt,lep.miniRelIso,lep.jetPtRatiov2,lep.jetPtRelv2,lep.pdgId,2)/lep.pt*lep.jetPtRatiov2 > B or lep.jetPtRelv2 > C)
#def _susy2lss_multiIso_withMiniIsoRelaxed_CutForFO4(lep):
#        if abs(lep.pdgId) == 13: A,B,C = (0.4,0.76,7.2)
#        else:                    A,B,C = (0.4,0.80,7.2)
#        return lep.miniRelIso < A and (1/lep.jetPtRatiov2 < (1/B + lep.miniRelIso))

#def _susy2lss_lepId_CBOld(lep):
#        if lep.pt <= 10: return False
#        if abs(lep.pdgId) == 13:
#            return lep.tightId > 0
#        elif abs(lep.pdgId) == 11:
#            return lep.tightId >= 2 and lep.convVeto and lep.tightCharge > 1 and lep.lostHits == 0
#        return False

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    tree.vectorTree = True
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf1 = LeptonJetReCleaner("Old", 
                lambda lep : lep.relIso03 < 0.5, 
                lambda lep : lep.relIso03 < 0.1 and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4))
            self.sf2 = LeptonJetReCleaner("PtRel", 
                lambda lep : lep.relIso03 < 0.4 or lep.jetPtRel > 5, 
                lambda lep : (lep.relIso03 < 0.1 or lep.jetPtRel > 14) and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4))
            self.sf3 = LeptonJetReCleaner("MiniIso", 
                lambda lep : lep.miniRelIso < 0.4, 
                lambda lep : lep.miniRelIso < 0.05 and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4))
            self.sf4 = LeptonJetReCleaner("PtRelJC", 
                lambda lep : lep.relIso03 < 0.4 or lep.jetPtRel > 5, 
                lambda lep : (lep.relIso03 < 0.1 or lep.jetPtRel > 14) and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4 and not (lep.jetPtRel > 5 and lep.pt*(1/lep.jetPtRatio-1) > 25)))
            self.sf5 = LeptonJetReCleaner("MiniIsoJC", 
                lambda lep : lep.miniRelIso < 0.4, 
                lambda lep : lep.miniRelIso < 0.05 and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4 and not (lep.jetDR > 0.5*10/min(50,max(lep.pt,200)) and lep.pt*(1/lep.jetPtRatio-1) > 25)))
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
            print self.sf1(ev)
            print self.sf2(ev)
            print self.sf3(ev)
            print self.sf4(ev)
            print self.sf5(ev)
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)

        
