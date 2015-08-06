from CMGTools.TTHAnalysis.treeReAnalyzer import *

class ObjTagger:
    def __init__(self,coll,sels,sizelimit=10):
        self.coll = coll
        self.sels = sels
        self.sizelimit = sizelimit
    def listBranches(self):
        biglist = [ ("n"+self.coll,"I") ]
        for lab in self.sels.iterkeys():
            biglist.extend([ ("n"+self.coll+"_"+lab, "I"), (self.coll+"_is"+lab,"I",100,"n"+self.coll) ])
        return biglist
    def __call__(self,event):
        try :
            assert (getattr(event,"n"+self.coll) <= self.sizelimit)
        except AssertionError:
            print 'ERROR in ObjTagger: branch size limit is '+str(self.sizelimit)+' while n'+self.coll+'=='+str(getattr(event,"n"+self.coll))
            raise
        objs = [l for l in Collection(event,self.coll,"n"+self.coll)]
        ret = {"n"+self.coll : getattr(event,"n"+self.coll) }
        for lab,sel in self.sels.iteritems():
	        ret["n"+self.coll+"_"+lab]=0
	        ret[self.coll+"_is"+lab]=[0] * getattr(event,"n"+self.coll)
	        for i,ob in enumerate(objs):
	            ispassing = True
	            for selector in sel:
	                if not selector(ob):
	                    ispassing = False
	                    break
	            if ispassing:
	                ret["n"+self.coll+"_"+lab] += 1
	                ret[self.coll+"_is"+lab][i] = 1
        return ret

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    tree.vectorTree = True
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf1 = ObjTagger("LepGood",{"LepPt25": [lambda ob : ob.pt >= 25], "LepPt10_EB": [lambda ob: ob.pt >= 10, lambda ob: abs(ob.eta)<1.4442]})
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
            print self.sf1(ev)
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)

        
