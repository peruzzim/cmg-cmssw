from CMGTools.TTHAnalysis.treeReAnalyzer import *
from CMGTools.TTHAnalysis.tools.leptonJetReCleaner import passMllVeto
from ROOT import TFile,TH1F

class LeptonChoiceRA5:

    # enum
    style_TT_loopTF_2FF = 0
    style_sort_FO = 1

    # enum
    appl_Fakes = 0
    appl_Flips = 1

    def __init__(self,label,inputlabel,whichApplication,lepChoiceMethod,FRFileName=None):
        self.label = "" if (label in ["",None]) else ("_"+label)
        self.inputlabel = '_'+inputlabel
        if whichApplication=="Fakes": self.whichApplication = self.appl_Fakes
        elif whichApplication=="Flips": self.whichApplication = self.appl_Flips
        else: raise RuntimeError, 'Unknown whichApplication'
        if lepChoiceMethod=="TT_loopTF_2FF": self.lepChoiceMethod = self.style_TT_loopTF_2FF
        elif lepChoiceMethod=="sort_FO": self.lepChoiceMethod = self.style_sort_FO
        else: raise RuntimeError, 'Unknown lepChoiceMethod'
        if FRFileName:
            self.FRfile = ROOT.TFile(FRFileName,"read")
            self.initFRhistos()
    def listBranches(self):
        label = self.label
        biglist = [ 
            ("nPairs"+label,"I"),
            ("i1"+label,"I",20,"nPairs"+label),
            ("i2"+label,"I",20,"nPairs"+label),
            ("appWeight"+label,"F",20,"nPairs"+label),
            ("SR"+label,"I",20,"nPairs"+label),
            ("hasTT"+label, "I"), ("hasTF"+label, "I"), ("hasFF"+label, "I"),
#            "mZ1cut10TL"+label, "minMllAFASTL"+label,"minMllAFOSTL"+label,"minMllSFOSTL"+label,
#            "minMllAFASTT"+label,"minMllAFOSTT"+label,"minMllSFOSTT"+label,
#            "mZ1"+label, "minMllAFAS"+label,"minMllAFOS"+label,"minMllSFOS"+label
            ]
        return biglist

    def __call__(self,event):

        leps = [l for l in Collection(event,"LepGood","nLepGood")]
        lepsl = [leps[il] for il in getattr(event,"iL"+self.inputlabel)]
#        lepsc = [leps[il] for il in getattr(event,"iC"+self.inputlabel)]
#        lepsf = [leps[il] for il in getattr(event,"iF"+self.inputlabel)]
        lepst = [leps[il] for il in getattr(event,"iT"+self.inputlabel)]
#        lepslv = [leps[il] for il in getattr(event,"iLV"+self.inputlabel)]
#        lepscv = [leps[il] for il in getattr(event,"iCV"+self.inputlabel)]
        lepsfv = [leps[il] for il in getattr(event,"iFV"+self.inputlabel)]
        lepstv = [leps[il] for il in getattr(event,"iTV"+self.inputlabel)]
        (met, metphi)  = event.met_pt, event.met_phi

        ret = {};

#        ### 2lss specific things - still useful?
#        ret['mZ1'] = self.bestZ1TL(lepsl, lepsl)
#        ret['mZ1cut10TL'] = self.bestZ1TL(lepsl, lepst, cut=lambda l:l.conePt>(10 if abs(l.pdgId)==13 else 15))
#        ret['minMllAFAS'] = self.minMllTL(lepsl, lepsl) 
#        ret['minMllAFOS'] = self.minMllTL(lepsl, lepsl, paircut = lambda l1,l2 : l1.charge !=  l2.charge) 
#        ret['minMllSFOS'] = self.minMllTL(lepsl, lepsl, paircut = lambda l1,l2 : l1.pdgId  == -l2.pdgId) 
#        ret['minMllAFASTL'] = self.minMllTL(lepsl, lepst) 
#        ret['minMllAFOSTL'] = self.minMllTL(lepsl, lepst, paircut = lambda l1,l2 : l1.charge !=  l2.charge) 
#        ret['minMllSFOSTL'] = self.minMllTL(lepsl, lepst, paircut = lambda l1,l2 : l1.pdgId  == -l2.pdgId) 
#        ret['minMllAFASTT'] = self.minMllTL(lepst, lepst)
#        ret['minMllAFOSTT'] = self.minMllTL(lepst, lepst, paircut = lambda l1,l2 : l1.charge !=  l2.charge) 
#        ret['minMllSFOSTT'] = self.minMllTL(lepst, lepst, paircut = lambda l1,l2 : l1.pdgId  == -l2.pdgId) 

        ret["nPairs"]=0
        ret["i1"] = [0]*20
        ret["i2"] = [0]*20
        ret["appWeight"] = [0]*20
        ret["SR"] = [0]*20
        ret["hasTT"]=False
        ret["hasTF"]=False
        ret["hasFF"]=False

        if self.whichApplication == self.appl_Fakes:
            if self.lepChoiceMethod==self.style_TT_loopTF_2FF:
                choice = self.findPairs(lepstv,lepstv,byflav=True,bypassMV=False,choose_SS_else_OS=True)
                if choice:
                    ret["hasTT"]=True
                    choice=choice[:1]
                else:
                    choice = self.findPairs(lepstv,lepsfv,byflav=True,bypassMV=False,choose_SS_else_OS=True)
                    if choice:
                        ret["hasTF"]=True
                        _probs = []
                    else:
                        choice = self.findPairs(lepsfv,lepsfv,byflav=True,bypassMV=False,choose_SS_else_OS=True)
                        if choice:
                            ret["hasFF"]=True
            if self.lepChoiceMethod==self.style_sort_FO:
                choice = self.findPairs(lepsfv,lepsfv,byflav=True,bypassMV=False,choose_SS_else_OS=True)
                if choice:
                    choice = choice[:1]
                    tt_sort_FO = [False]*2
                    if choice[0][0] in lepstv: tt_sort_FO[0]=True
                    if choice[0][1] in lepstv: tt_sort_FO[1]=True
                    if tt_sort_FO==[True,True]: ret["hasTT"]=True
                    elif tt_sort_FO==[False,False]: ret["hasFF"]=True
                    else: ret["hasTF"] = True
        elif self.whichApplication == self.appl_Flips:
            choice = self.findPairs(lepstv,lepstv,byflav=True,bypassMV=False,choose_SS_else_OS=True)
            if choice:
                ret["hasTT"]=True
                choice=choice[:1]
            else:
                choice = self.findPairs(lepst,lepst,byflav=True,bypassMV=False,choose_SS_else_OS=False)
                if choice:
                    ret["hasTF"]=True
                    choice=choice[:1]
            
        if choice:
            ret["nPairs"] = len(choice)
            for npair in xrange(len(choice)):
                i1 = leps.index(choice[npair][0])
                i2 = leps.index(choice[npair][1])
                ret["i1"][npair]=i1
                ret["i2"][npair]=i2
                mtwmin = min(sqrt(2*leps[i1].conePt*met*(1-cos(leps[i1].phi-metphi))),sqrt(2*leps[i2].conePt*met*(1-cos(leps[i2].phi-metphi))))
                ht = getattr(event,"htJet40j"+self.inputlabel)
                ret["SR"][npair]=self.SR(leps[i1].conePt,leps[i2].conePt,ht,met,getattr(event,"nJet40"+self.inputlabel),getattr(event,"nBJetMedium25"+self.inputlabel),mtwmin)
                if self.whichApplication == self.appl_Fakes:
                    if self.lepChoiceMethod==self.style_TT_loopTF_2FF:
                        if ret["hasTT"]:
                            ret["appWeight"][npair] = 0.0
                        elif ret["hasTF"]:
                            prev = 1.0
                            for x in _probs:
                                prev *= (1-x)
                            prob = self.FRprob(leps[i2],ht)
                            transf = self.FRtransfer_fromprob(prob)
                            _probs.append(prob)
                            ret["appWeight"][npair] = prev * transf
                        elif ret["hasFF"]:
                            ret["appWeight"][npair] = -self.FRtransfer(leps[i1],ht)*self.FRtransfer(leps[i2],ht) if len(choice)<2 else 0.0 # throw away events with three FO non Tight
                    elif self.lepChoiceMethod==self.style_sort_FO:
                        if ret["hasTT"]:
                            ret["appWeight"][npair] = 0.0
                        elif ret["hasTF"]:
                            ret["appWeight"][npair] = self.FRtransfer(leps[i2 if tt_sort_FO[0] else i1],ht)
                        elif ret["hasFF"]:
                            ret["appWeight"][npair] = -self.FRtransfer(leps[i1],ht)*self.FRtransfer(leps[i2],ht)
                elif self.whichApplication == self.appl_Flips:
                    print 'TODO'

        ### attach labels and return
        fullret = {}
        for k,v in ret.iteritems(): 
            fullret[k+self.label] = v
        return fullret

    def initFRhistos(self):
        self.FR_mu = (self.FRfile.Get("FRMuPtCorr_ETH_non"),self.FRfile.Get("FRMuPtCorr_ETH_iso"))
        self.FR_el = (self.FRfile.Get("FRElPtCorr_ETH_non"),self.FRfile.Get("FRElPtCorr_ETH_iso"))

    def FRprob(self,lep,ht):
        isiso = (ht<=300)
        h = self.FR_el[isiso] if abs(lep.pdgId)==11 else self.FR_mu[isiso]
        ptbin = max(1,min(h.GetNbinsX(),h.GetXaxis().FindBin(lep.conePt)))
        etabin = max(1,min(h.GetNbinsY(),h.GetYaxis().FindBin(abs(lep.eta))))
        return h.GetBinContent(ptbin,etabin)
    def FRtransfer_fromprob(self,prob):
        return prob/(1-prob)
    def FRtransfer(self,lep,ht):
        return self.FRtransfer_fromprob(self.FRprob(lep,ht))

    def bestZ1TL(self,lepsl,lepst,cut=lambda lep:True):
          pairs = []
          for l1 in lepst:
            if not cut(l1): continue
            for l2 in lepsl:
                if not cut(l2): continue
                if l1.pdgId == -l2.pdgId:
                   mz = (l1.p4() + l2.p4()).M()
                   diff = abs(mz-91.2)
                   pairs.append( (diff,mz) )
          if len(pairs):
              pairs.sort()
              return pairs[0][1]
          return 0.
    def minMllTL(self, lepsl, lepst, bothcut=lambda lep:True, onecut=lambda lep:True, paircut=lambda lep1,lep2:True):
            pairs = []
            for l1 in lepst:
                if not bothcut(l1): continue
                for l2 in lepsl:
                    if l2 == l1 or not bothcut(l2): continue
                    if not onecut(l1) and not onecut(l2): continue
                    if not paircut(l1,l2): continue
                    mll = (l1.p4() + l2.p4()).M()
                    pairs.append(mll)
            if len(pairs):
                return min(pairs)
            return -1
    def findPairs(self,leps1,leps2,byflav,bypassMV,choose_SS_else_OS=True):
        ret = None
        pairs = []
        _p = []
        for p in [(l1,l2) for l1 in leps1 for l2 in leps2 if l1!=l2]:
            if (p[1],p[0]) not in _p:
                _p.append(p)
        for (l1,l2) in _p:
                if not passMllVeto(l1, l2, 0, 8, False) and not bypassMV: continue
                flav = abs(l1.pdgId) + abs(l2.pdgId) if byflav else 0
                ht   = l1.conePt + l2.conePt
                if ((l1.charge == l2.charge) if choose_SS_else_OS else (l1.charge != l2.charge)):
                    pairs.append( (-flav,-ht,l1,l2) )
        if len(pairs):
            pairs.sort()
            ret = [(pair[2],pair[3]) for pair in pairs]
        return ret
    def SR(self, l1pt, l2pt, ht, met, nj, nb, mtw):
        if l1pt > 25 and l2pt > 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 0 and mtw < 120 : SR = 1
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 0 and mtw < 120  : SR = 2
        elif l1pt > 25 and l2pt > 25 and ht < 300 and nb == 0 and ((met > 50 and met < 200 and nj >= 5 and mtw < 120) or (met > 200 and met < 300 and nj >= 2 and mtw < 120) or (met > 50 and met < 300 and nj >= 2 and mtw > 120))   : SR = 3
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 5 and nb == 0 and mtw < 120  : SR = 4
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nj <= 4 and nb == 0 and mtw < 120  : SR = 5
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 5 and nb == 0 and mtw < 120  : SR = 6
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 0 and mtw > 120  : SR = 7
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and nb == 0 and ((met > 50 and met < 200 and nj >= 5 and mtw > 120) or (met > 200 and met < 300 and nj >= 2 and mtw > 120)) : SR = 8
        elif l1pt > 25 and l2pt > 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 1 and mtw < 120 : SR = 9
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 1 and mtw < 120  : SR = 10
        elif l1pt > 25 and l2pt > 25 and ht < 300 and nb == 1 and ((met > 50 and met < 200 and nj >= 5 and mtw < 120) or (met > 200 and met < 300 and nj >= 2 and mtw < 120) or (met > 50 and met < 300 and nj >= 2 and mtw > 120))   : SR = 11
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 5 and nb == 1 and mtw < 120  : SR = 12
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nj <= 4 and nb == 1 and mtw < 120  : SR = 13
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 5 and nb == 1 and mtw < 120  : SR = 14
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 1 and mtw > 120  : SR = 15
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and nb == 1 and ((met > 50 and met < 200 and nj >= 5 and mtw > 120) or (met > 200 and met < 300 and nj >= 2 and mtw > 120)) : SR = 16
        elif l1pt > 25 and l2pt > 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 2 and mtw < 120 : SR = 17
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 2 and mtw < 120  : SR = 18
        elif l1pt > 25 and l2pt > 25 and ht < 300 and nb == 2 and ((met > 50 and met < 200 and nj >= 5 and mtw < 120) or (met > 200 and met < 300 and nj >= 2 and mtw < 120) or (met > 50 and met < 300 and nj >= 2 and mtw > 120))   : SR = 19
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 5 and nb == 2 and mtw < 120  : SR = 20
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nj <= 4 and nb == 2 and mtw < 120  : SR = 21
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 5 and nb == 2 and mtw < 120  : SR = 22
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 2 and mtw > 120  : SR = 23
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and nb == 2 and ((met > 50 and met < 200 and nj >= 5 and mtw > 120) or (met > 200 and met < 300 and nj >= 2 and mtw > 120)) : SR = 24
        elif l1pt > 25 and l2pt > 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 25
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 26
        elif l1pt > 25 and l2pt > 25 and ht < 300 and met > 200 and met < 300 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 27
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 28
        elif l1pt > 25 and l2pt > 25 and ht < 300 and met > 50 and met < 300 and nj >= 2 and nb >= 3 and mtw > 120 : SR = 29
        elif l1pt > 25 and l2pt > 25 and ht > 300 and ht < 1125 and met > 50 and met < 300 and nj >= 2 and nb >= 3 and mtw > 120 : SR = 30
        elif l1pt > 25 and l2pt > 25 and ht > 300 and met > 300 and nj >= 2 : SR = 31
        elif l1pt > 25 and l2pt > 25 and ht > 1125 and met > 50 and met < 300 and nj >= 2 : SR = 32
        ####
        elif l1pt > 25 and l2pt < 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 0 and mtw < 120 : SR = 33 #1B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 0 and mtw < 120 : SR = 34 #2B
        elif l1pt > 25 and l2pt < 25 and ht < 300  and ((met > 50 and met < 200 and nj >= 5) or (met > 200 and met < 300 and nj >= 2)) and nb == 0 and mtw < 120 : SR = 35 #3B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 5 and nb == 0 and mtw < 120 : SR = 36  #4B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nj <= 4 and nb == 0 and mtw < 120 : SR = 37 #5B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 5 and nb == 0 and mtw < 120 : SR = 38 #6B
        elif l1pt > 25 and l2pt < 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 1 and mtw < 120 : SR = 39 #7B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 1 and mtw < 120 : SR = 40 #8B
        elif l1pt > 25 and l2pt < 25 and ht < 300  and ((met > 50 and met < 200 and nj >= 5) or (met > 200 and met < 300 and nj >= 2)) and nb == 1 and mtw < 120 : SR = 41 #9B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 5 and nb == 1 and mtw < 120 : SR = 42 #10B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nj <= 4 and nb == 1 and mtw < 120 : SR = 43 #11B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 5 and nb == 1 and mtw < 120 : SR = 44 #12B
        elif l1pt > 25 and l2pt < 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 2 and mtw < 120 : SR = 45 #13B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nj <= 4 and nb == 2 and mtw < 120 : SR = 46 #14B
        elif l1pt > 25 and l2pt < 25 and ht < 300  and ((met > 50 and met < 200 and nj >= 5) or (met > 200 and met < 300 and nj >= 2)) and nb == 2 and mtw < 120 : SR = 47 #15B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 5 and nb == 2 and mtw < 120 : SR = 48 #16B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nj <= 4 and nb == 2 and mtw < 120 : SR = 49 #17B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 5 and nb == 2 and mtw < 120 : SR = 50 #18B
       
        elif l1pt > 25 and l2pt < 25 and ht < 300 and met > 50 and met < 200 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 51 #19B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 200 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 52 #20B
        elif l1pt > 25 and l2pt < 25 and ht < 300 and met > 200 and met < 300 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 53 #21B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 200 and met < 300 and nj >= 2 and nb >= 3 and mtw < 120 : SR = 54 #21B       
        elif l1pt > 25 and l2pt < 25 and ht < 300 and met > 50 and met < 300 and nj >= 2 and mtw > 120 : SR = 55 #23B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and ht < 1125 and met > 50 and met < 300 and nj >= 2 and mtw > 120 : SR = 56 #24B
        elif l1pt > 25 and l2pt < 25 and ht > 300 and met > 300 and nj >= 2 : SR = 57 #25B
        elif l1pt > 25 and l2pt < 25 and ht > 1125 and met > 50 and met < 300 and nj >= 2 : SR = 58 #26B
        ####
        elif l1pt < 25 and l2pt < 25 and  met > 50 and met < 200 and nb == 0 and mtw < 120 : SR = 59 #C1 
        elif l1pt < 25 and l2pt < 25 and  met > 200 and nb == 0 and mtw < 120 : SR = 60 #C2 
        elif l1pt < 25 and l2pt < 25 and  met > 50 and met < 200 and nb == 1 and mtw < 120 : SR = 61 #C3 
        elif l1pt < 25 and l2pt < 25 and  met > 200 and nb == 1 and mtw < 120 : SR = 62 #C4 
        elif l1pt < 25 and l2pt < 25 and  met > 50 and met < 200 and nb == 2 and mtw < 120 : SR = 63 #C5 
        elif l1pt < 25 and l2pt < 25 and  met > 200 and nb == 2 and mtw < 120 : SR = 64 #C6 
        elif l1pt < 25 and l2pt < 25 and  nb >= 3 and mtw < 120 : SR = 65 #C7 
        elif l1pt < 25 and l2pt < 25 and  mtw > 120 : SR = 66 #C8 
        else : SR = 0 
        return SR

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    tree.vectorTree = True
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf1 = LeptonChoiceRA5("Old", 
                lambda lep : lep.relIso03 < 0.5, 
                lambda lep : lep.relIso03 < 0.1 and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4))
            self.sf2 = LeptonChoiceRA5("PtRel", 
                lambda lep : lep.relIso03 < 0.4 or lep.jetPtRel > 5, 
                lambda lep : (lep.relIso03 < 0.1 or lep.jetPtRel > 14) and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4))
            self.sf3 = LeptonChoiceRA5("MiniIso", 
                lambda lep : lep.miniRelIso < 0.4, 
                lambda lep : lep.miniRelIso < 0.05 and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4))
            self.sf4 = LeptonChoiceRA5("PtRelJC", 
                lambda lep : lep.relIso03 < 0.4 or lep.jetPtRel > 5, 
                lambda lep : (lep.relIso03 < 0.1 or lep.jetPtRel > 14) and lep.sip3d < 4 and _susy2lss_lepId_CB(lep),
                cleanJet = lambda lep,jet,dr : (lep.pt > 10 and dr < 0.4 and not (lep.jetPtRel > 5 and lep.pt*(1/lep.jetPtRatio-1) > 25)))
            self.sf5 = LeptonChoiceRA5("MiniIsoJC", 
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

        
