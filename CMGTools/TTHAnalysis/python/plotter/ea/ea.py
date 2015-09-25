from ROOT import *
from math import *

gROOT.SetBatch(True)

f = TFile("/data1/p/peruzzi/TREES_74X_250915_7_4_12_noIso_slimForEA/DYJetsToLL_M50/treeProducerSusyMultilepton/tree.root")
t = f.Get("tree")

printfits = False
evcuts = "(rho>5 && rho<25 && LepGood_mcMatchId==23 && LepGood_pt>20 && (abs(LepGood_pdgId)!=11 || abs(LepGood_etaSc)<1.4442 || abs(LepGood_etaSc)>1.566))"

results = {}

class myres:
    def __init__(self):
        pass
    def printme(self):
        print "%d_%s_%.1f_%.1f_%s: %.3f +/- %.3f, scaled to R^2: %.3f +/- %.3f"%(self.pid,self.iso,self.etamin,self.etamax,self.Rlabel,self.slope,self.slopeError,self.slopeOverR2,self.slopeOverR2Error)

def getkey(particle,iso,etamin,etamax,text):
    return "%d_%s_%.1f_%.1f_%s"%(particle,iso,etamin,etamax,text)

def fit(particle,iso,etamin=0,etamax=999,tag='EA fit'):
    for text,x in points:
        newkey = getkey(particle,iso,etamin,etamax,text)
        print 'Fitting %s'%newkey
        if newkey in results.keys(): print 'Warning: updating key %s'%newkey
        title = "LepGood_scanAbsIso%s%s_%s_%s_%s"%(iso,text,particle,etamin,etamax)
        c1 = TCanvas(title,title)
        c1.cd()
        cutstring = "abs(LepGood_pdgId)==%d && abs(LepGood_etaSc)>%f && abs(LepGood_etaSc)<%f %s"%(particle,etamin,etamax,'&& '+evcuts if evcuts!="" else "")
        if particle!=11: cutstring = cutstring.replace('LepGood_etaSc','LepGood_eta')
        t.Draw("LepGood_scanAbsIso%s%s:rho>>htemp(10,5,25)"%(iso,text),cutstring,"prof",10000)
        htemp = gDirectory.Get("htemp")
        fit = htemp.Fit("pol1","SQ")
        if printfits: c1.Print(title+'.pdf')
        slope = fit.Get().GetParams()[1]
        error = fit.Get().ParError(1)
        a = myres()
        a.pid = particle
        a.iso = iso
        a.etamin = etamin
        a.etamax = etamax
        a.R = x
        a.Rlabel = text
        a.slope = slope
        a.slopeError = error
        a.slopeOverR2 = slope/(x*x)
        a.slopeOverR2Error = error/(x*x)
        results[newkey]=a

def getEA(particle,iso,eta,R):
    found = None
    for key,res in results.iteritems():
        if res.pid!=particle: continue
        if res.iso!=iso: continue
        if abs(eta)<res.etamin: continue
        if not (abs(eta)<res.etamax): continue
        if R!=res.R: continue
        found = res
        break
    if found==None:
        print 'EA not found'
        return 0
    return found.slope



if __name__=="__main__":

    components = ["Neutral","Charged"]
    eta_boundaries = [0,0.8,1.3,2.0,2.2,2.5]
    pids={"Electron": 11, "Muon": 13}
    points = [("005",0.05), ("01",0.1), ("02",0.2), ("03",0.3), ("04",0.4)]

    for particle,pid in pids.iteritems():
        for comp in components:
            for eta_bin in xrange(len(eta_boundaries)-1):
                etamin = eta_boundaries[eta_bin]
                etamax = eta_boundaries[eta_bin+1]
                label = particle+' %.1f-%.1f'%(etamin,etamax)
                fit(pid,comp,etamin,etamax,label)

    for key,res in results.iteritems(): res.printme()

    colors=[kBlue,kRed,kGreen,kYellow,kOrange,kBlack]
    for particle,pid in pids.iteritems():
        for comp in components:
            title = '%s: %s component'%(particle,comp)
            c2 = TCanvas(title,title,800,600)
            c2.cd()
            n = len(points)
            grs=[]
            for eta_bin in xrange(len(eta_boundaries)-1):
                gr = TGraphErrors(n)
                gr.SetName(title+'_%d'%eta_bin)
                gr.SetTitle(title+'_%d'%eta_bin)
                if eta_bin==0: gr.SetTitle(gr.GetTitle().split('_')[0])
                print gr.GetTitle()
                etamin = eta_boundaries[eta_bin]
                etamax = eta_boundaries[eta_bin+1]
                for i in xrange(n):
                    key = getkey(pid,comp,etamin,etamax,points[i][0])
                    gr.SetPoint(i,points[i][1],results[key].slopeOverR2)
                    gr.SetPointError(i,0,results[key].slopeOverR2Error)
                gr.SetMarkerStyle(21)
                gr.SetMarkerColor(colors[eta_bin])
                gr.SetLineColor(colors[eta_bin])
                gr.Draw("AP" if eta_bin==0 else "Psame")
                gr.GetXaxis().SetTitle("Cone radius")
                gr.GetYaxis().SetTitle("Effective area / Square cone radius")
                gr.GetXaxis().SetRangeUser(0,0.45)
                gr.GetYaxis().SetRangeUser(-0.2,1.6)
                grs.append(gr)
            c2.Update()

            leg = TLegend(0.12,0.58,0.42,0.88)
            leg.SetFillColor(kWhite)
            leg.SetFillStyle(0)
            leg.SetBorderSize(0)
            for i in xrange(len(grs)):
                leg.AddEntry(grs[i],"#eta=%.1f-%.1f"%(eta_boundaries[i],eta_boundaries[i+1]),"lp");
                print "#eta=%.1f-%.1f"%(eta_boundaries[i],eta_boundaries[i+1])
            leg.Draw()
            c2.Update()

            c2.Print('%s_%s.pdf'%(particle,comp))


#    results2= []
#    print '\n'+tag+' '+iso
#    for x,slope,error in results:
#        x2 = (x/results[-1][0])**2
#        slope2 = slope/results[-1][1]
#        error2 = slope2*sqrt((error/slope)**2+(results[-1][2]/results[-1][1])**2)
#        print '%f: %f +/- %f   -> ratio %f +/- %f'%(x,slope,error,slope2/x2,error2/x2)

#    c2 = TCanvas(title,title,800,600)
#    c2.cd()
#    n = len(points)
#    gr = TGraphErrors(n)
#    gr.SetTitle(title)
#    for i in xrange(n):
#        gr.SetPoint(i,results[i][0],results[i][1]/(results[i][0]**2))
#        gr.SetPointError(i,0,results[i][2]/(results[i][0]**2))



