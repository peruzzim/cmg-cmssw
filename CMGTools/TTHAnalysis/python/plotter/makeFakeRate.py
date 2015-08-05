from math import *
from os.path import basename

import sys
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')

from CMGTools.TTHAnalysis.plotter.mcEfficiencies import *

class METBinnedFakeRate:
    def __init__(self,effplots):
        self.effplots = effplots
        self.pmap = (self.effplots)[0][2]
        self.myprocs = ['data','mcmixture','ewk','qcd']
        self.myprocs = [i for i in self.myprocs if i in self.pmap.keys()]
    def binfinder(self,h,dim,b):
        bx,by,bz = ROOT.Long(), ROOT.Long(), ROOT.Long()
        h.GetBinXYZ(b,bx,by,bz)
        if dim in [1,'x']   :return h.GetXaxis().GetBinCenter(bx)
        elif dim in [2,'y'] : 
            if h.GetDimension()<2: raise RuntimeError('Invalid dimension choice')
            return h.GetYaxis().GetBinCenter(by)
        elif dim in [3,'z'] :
            if h.GetDimension()<3: raise RuntimeError('Invalid dimension choice')
            return h.GetZaxis().GetBinCenter(bz)
        else: raise RuntimeError('Called binfinder with invalid dimension identifier')
    def sliceintegral(self,h,cuts):
        n, n2 = 0, 0
        if not ("TH" in h.ClassName()): raise RuntimeError('Called integral function on an object that is not an histogram')
        bins = h.GetNbinsX() * (h.GetNbinsY() if ("TH2" in h.ClassName()) else 1) * (h.GetNbinsZ() if ("TH3" in h.ClassName()) else 1)
        for b in xrange(1,bins+1):
            failed = False
            for cut in cuts:
                x = self.binfinder(h,cut[0],b)
                if (x<cut[1] or x>cut[2]):
                    failed = True
                    break
            if failed: continue
            n  += h.GetBinContent(b)
            n2 += h.GetBinError(b)**2
        return [n, sqrt(n2)]

#    def frFromRangePF(self,h,xmin,xmax):
#        p,dp = self.integral(h[0],xmin,xmax)
#        f,df = self.integral(h[1],xmin,xmax)
#        r = p/float(p+f) if p+f > 0 else 0
#        dr = sqrt(((p*df)**2)+((f*dp)**2))/((p+f)**2) if p+f > 0 else 0
#        return (r,dr,p,dp,f,df) 

    def get_fake_qcd(self,hdata,hewk,met_l,met_h):

#  Pass    ^
#          | B   D
#          |
#          | A   C
#          |_________>
#                  MET
#  
#   fake rates do not depend on MET: f_{QCD}, f_{EWK}
#   ratio low/high MET for EWK is known: R_{EWK}
#   then: f_{QCD} = (B-R_{EWK}D)/(A-R_{EWK}C)

# pass 3d histos (pt,met,pass(0/1)) to this function

        res = hdata.ProjectionX()
        res.Reset()
        res.SetName(hdata.GetName()+"qcd_fakerate")
        res.SetTitle(hdata.GetTitle()+"qcd_fakerate")
        for b in xrange(1,hdata.GetNbinsX()+1):
            A = self.sliceintegral(hdata,[['y',met_l[0],met_l[1]],['z',-0.5,0.5]])
            B = self.sliceintegral(hdata,[['y',met_l[0],met_l[1]],['z',0.5,1.5]])
            C = self.sliceintegral(hdata,[['y',met_h[0],met_h[1]],['z',-0.5,0.5]])
            D = self.sliceintegral(hdata,[['y',met_h[0],met_h[1]],['z',0.5,1.5]])
            rewk = self.sliceintegral(hewk,[['y',met_l[0],met_l[1]]])/self.sliceintegral(hewk,[['y',met_h[0],met_h[1]]]) if hewk else 0
            if not hewk: raise RunTimeError('EWKMISSING','The histogram for EWK subtraction is missing')
            elif rewk==0: print 'Warning: EWK low/high MET ratio is zero in bin',b
            res.SetBinContent(b,(B-rewk*D)/(A-rewk*C))
            res.SetBinError(b,0) # TODO
        return res

    def makePlotsBySource(self):
        met_l = (0,20)
        met_h = (50,200)
        print self.myprocs
        meas_sample = 'data' if ('data' in self.myprocs) else 'QCD_Mu'
        hdata = self.pmap[meas_sample]['passfail']
        hewk = self.pmap['ewk']['passfail'] if 'ewk' in self.myprocs else None
        print self.get_fake_qcd(hdata,hewk,met_l,met_h)


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] mc.txt cuts.txt plotfile.txt")
    addROCMakerOptions(parser)
    addMCEfficienciesOptions(parser)
    (options, args) = parser.parse_args()
    options.globalRebin = 1
    options.allowNegative = True # with the fine bins used in ROCs, one otherwise gets nonsensical results
    options.outputNumDenHistos = True # necessary, forced True
    mca  = MCAnalysis(args[0],options)
    procs = mca.listProcesses()
    cut = CutsFile(args[1],options).allCuts()
    ids   = PlotFile(args[2],options).plots()
    xvars = PlotFile(args[3],options).plots()
    effplots = runEffPlots(mca,procs,cut,ids,xvars,options)
    fr = METBinnedFakeRate(effplots)
    fr.makePlotsBySource()

