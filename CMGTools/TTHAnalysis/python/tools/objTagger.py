from CMGTools.TTHAnalysis.treeReAnalyzer import *

class ObjTagger:
    def __init__(self,label,coll,sel,sizelimit=20):
        self.label = "" if (label in ["",None]) else ("_"+label)
        self.coll = coll
        self.sel = sel
        self.sizelimit = sizelimit
    def listBranches(self):
        biglist = [ ("n"+self.coll+self.label, "I"), ("i"+self.coll+self.label,"I",self.sizelimit,"n"+self.coll+self.label) ]
        return biglist
    def __call__(self,event):
        objs = [l for l in Collection(event,self.coll,"n"+self.coll)]
        ret = {};
        ret["n"+self.coll+self.label]=0
        ret["i"+self.coll+self.label]=[]
        for i,ob in enumerate(objs):
            ispassing = True
            for selector in self.sel:
                if not selector(ob):
                    ispassing = False
                    break
            if ispassing:
                if ret["n"+self.coll+self.label] == self.sizelimit:
                    print 'WARNING: reached branch size limit for ObjTagger labeled '+self.label
                    break
                ret["n"+self.coll+self.label] += 1
                ret["i"+self.coll+self.label].append(i)
        return ret

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    tree.vectorTree = True
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf1 = ObjTagger("LepPt25","LepGood",[lambda ob : ob.pt >= 25])
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
            print self.sf1(ev)
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)

        
