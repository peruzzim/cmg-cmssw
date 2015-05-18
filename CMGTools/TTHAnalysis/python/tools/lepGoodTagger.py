from CMGTools.TTHAnalysis.treeReAnalyzer import *

class LepGoodTagger:
    def __init__(self,label,LeptonSel):
        self.label = "" if (label in ["",None]) else ("_"+label)
        self.LeptonSel = LeptonSel
        self.sizelimit = 20
    def listBranches(self):
        label = self.label
        biglist = [ ("nLepGoodTagger"+label, "I"), ("iLepGoodTagger"+label,"I",self.sizelimit,"nLepGoodTagger"+label) ]
        return biglist
    def __call__(self,event):
        leps = [l for l in Collection(event,"LepGood","nLepGood")]
        ret = {};
        ret["nLepGoodTagger"+self.label]=0
        ret["iLepGoodTagger"+self.label]=[]
        for il,lep in enumerate(leps):
            ispassing = True
            for selector in self.LeptonSel:
                if not selector(lep):
                    ispassing = False
                    break
            if ispassing:
                if ret["nLepGoodTagger"+self.label] == self.sizelimit:
                    print 'WARNING: reached branch size limit for LepGoodTagger labeled '+self.label
                    break
                ret["nLepGoodTagger"+self.label] += 1
                ret["iLepGoodTagger"+self.label].append(il)
        return ret

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    tree.vectorTree = True
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf1 = LepGoodTagger("LepGoodPt25", 
                [lambda lep : lep.pt >= 25])
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
            print self.sf1(ev)
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)

        
