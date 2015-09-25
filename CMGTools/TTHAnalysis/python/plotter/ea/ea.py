from ROOT import *
from math import *

if "/getEA_cc.so" not in gSystem.GetLibraries(): 
    gROOT.ProcessLine(".L getEA.cc+O")

gROOT.SetBatch(True)
gStyle.SetOptStat(0)

f = TFile("/data1/p/peruzzi/TREES_74X_250915_7_4_12_noIso_slimForEA/DYJetsToLL_M50/treeProducerSusyMultilepton/tree.root")
t = f.Get("tree")

printfits = False
nevents = int(1e4)
evcuts = "(rho>5 && rho<25 && LepGood_mcMatchId==23 && LepGood_pt>20 && (abs(LepGood_pdgId)!=11 || abs(LepGood_etaSc)<1.4442 || abs(LepGood_etaSc)>1.566))"

results = {}

class myres:
    def __init__(self):
        pass
    def printme(self):
        print "%d_%s_%.1f_%.1f_%s: %.3f +/- %.3f, scaled to R^2: %.3f +/- %.3f"%(self.pid,self.iso,self.etamin,self.etamax,self.Rlabel,self.slope,self.slopeError,self.slopeOverR2,self.slopeOverR2Error)

def getkey(particle,iso,etamin,etamax,text):
    return "%d_%s_%.1f_%.1f_%s"%(particle,iso,etamin,etamax,text)

def isomean(particle,etamin=0,etamax=999,R=0.4,EAsub="raw",eff=None):
    for text,x in points:
        if x!=R: continue
        cutstring = "abs(LepGood_pdgId)==%d && abs(LepGood_etaSc)>%f && abs(LepGood_etaSc)<%f %s"%(particle,etamin,etamax,'&& '+evcuts if evcuts!="" else "")
        if particle!=11: cutstring = cutstring.replace('LepGood_etaSc','LepGood_eta')
        if EAsub=="raw":
            if eff==None: t.Draw("LepGood_scanAbsIsoCharged%s+LepGood_scanAbsIsoNeutral%s:rho>>htempraw(25,0,25)"%(text,text),cutstring,"prof",nevents)
            else: t.Draw("(LepGood_scanAbsIsoCharged%s+LepGood_scanAbsIsoNeutral%s)/LepGood_pt<%f:rho>>htempraw(25,0,25)"%(text,text,eff),cutstring,"prof",nevents)
            htemp = gDirectory.Get("htempraw")
        elif EAsub=="defScaled":
            if eff==None: t.Draw("LepGood_scanAbsIsoCharged%s+TMath::Max(0,LepGood_scanAbsIsoNeutral%s-LepGood_rhoForEA*LepGood_effArea*%f*%f/0.3/0.3):rho>>htempdefScaled(25,0,25)"%(text,text,R,R),cutstring,"prof",nevents)
            else: t.Draw("(LepGood_scanAbsIsoCharged%s+TMath::Max(0,LepGood_scanAbsIsoNeutral%s-LepGood_rhoForEA*LepGood_effArea*%f*%f/0.3/0.3))/LepGood_pt<%f:rho>>htempdefScaled(25,0,25)"%(text,text,R,R,eff),cutstring,"prof",nevents)
            htemp = gDirectory.Get("htempdefScaled")
        elif EAsub=="new":
            if eff==None: t.Draw("LepGood_scanAbsIsoCharged%s+TMath::Max(0,LepGood_scanAbsIsoNeutral%s-rho*getEA(%d,%d,LepGood_etaSc,%f)):rho>>htempnew(25,0,25)"%(text,text,particle,0,R),cutstring,"prof",nevents)
            else: t.Draw("(LepGood_scanAbsIsoCharged%s+TMath::Max(0,LepGood_scanAbsIsoNeutral%s-rho*getEA(%d,%d,LepGood_etaSc,%f)))/LepGood_pt<%f:rho>>htempnew(25,0,25)"%(text,text,particle,0,R,eff),cutstring,"prof",nevents)
            htemp = gDirectory.Get("htempnew")
        return htemp

def fit(particle,iso,etamin=0,etamax=999):
    for text,x in points:
        newkey = getkey(particle,iso,etamin,etamax,text)
        print 'Fitting %s'%newkey
        if newkey in results.keys(): print 'Warning: updating key %s'%newkey
        title = "LepGood_scanAbsIso%s%s_%s_%s_%s"%(iso,text,particle,etamin,etamax)
        c1 = TCanvas(title,title)
        c1.cd()
        cutstring = "abs(LepGood_pdgId)==%d && abs(LepGood_etaSc)>%f && abs(LepGood_etaSc)<%f %s"%(particle,etamin,etamax,'&& '+evcuts if evcuts!="" else "")
        if particle!=11: cutstring = cutstring.replace('LepGood_etaSc','LepGood_eta')
        t.Draw("LepGood_scanAbsIso%s%s:rho>>htemp(10,5,25)"%(iso,text),cutstring,"prof",nevents)
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

from array import array

def setEAs():
    myhs={}
    for particle,pid in pids.iteritems():
        for comp in components:
            rs = [0]
            rs.extend([x for text,x in points])
            rs.append(10)
            n = len(rs)
            rs2 = []
            for i in xrange(n):
                if i==0: rs2.append(rs[i])
                elif i!=n-1: rs2.append((rs[i]+rs[i+1])/2)
                else: pass
            name = 'EA_%s_%s'%(pid,comp)
            myhs[name] = TH2F(name,name,len(eta_boundaries)-1,array('f',eta_boundaries),len(rs2)-1,array('f',rs2))
    for key,res in results.iteritems():    
        h=myhs['EA_%s_%s'%(res.pid,res.iso)]
        h.SetBinContent(h.GetXaxis().FindBin((res.etamin+res.etamax)/2),h.GetYaxis().FindBin(res.R),res.slope)
    setEAhistos(myhs['EA_11_Neutral'],myhs['EA_11_Charged'],myhs['EA_13_Neutral'],myhs['EA_13_Charged'])


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
                fit(pid,comp,etamin,etamax)

    for key,res in results.iteritems(): res.printme()

    colors=[kBlue,kRed,kGreen,kOrange,kMagenta]
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

            leg = TLegend(0.12,0.68,0.42,0.88)
            leg.SetFillColor(kWhite)
            leg.SetFillStyle(0)
            leg.SetBorderSize(0)
            for i in xrange(len(grs)):
                leg.AddEntry(grs[i],"#eta=%.1f-%.1f"%(eta_boundaries[i],eta_boundaries[i+1]),"lp");
            leg.Draw()
            c2.Update()

            c2.Print('%s_%s.pdf'%(particle,comp))

    setEAs()

    for particle,pid in pids.iteritems():
        for text,x in points:
            title = '%s: isolation in R=%.1f cone'%(particle,x)
            c2 = TCanvas(title,title,800,600)
            c2.cd()
            hraw = isomean(pid,etamin=0,etamax=2.5,R=x,EAsub="raw")
            hdefScaled = isomean(pid,etamin=0,etamax=2.5,R=x,EAsub="defScaled")
            hnew = isomean(pid,etamin=0,etamax=2.5,R=x,EAsub="new")
            hs=[hraw,hdefScaled,hnew]
            for i in xrange(len(hs)):
                hs[i].SetMarkerStyle(21+i)
                hs[i].SetMarkerColor(colors[i])
                hs[i].SetLineColor(colors[i])
                if i==0: hs[i].SetTitle("%s isolation in R=%s cone"%(particle,str(x).rstrip('0')))
                hs[i].Draw("E1" if i==0 else "E1same")
                if i==0: hs[i].GetYaxis().SetRangeUser(0,5)
                hs[i].GetXaxis().SetTitle("#rho")
                hs[i].GetYaxis().SetTitle("<Isolation> (GeV)")
            c2.Update()

            leg = TLegend(0.12,0.73,0.42,0.88)
            leg.SetFillColor(kWhite)
            leg.SetFillStyle(0)
            leg.SetBorderSize(0)
            leg.AddEntry(hraw,"Raw","lp")
            leg.AddEntry(hdefScaled,"Scaled EA","lp")
            leg.Draw()
            c2.Update()

            c2.Print('Iso_%s_%s.pdf'%(particle,text))

    effcut = 0.05
    for particle,pid in pids.iteritems():
        for text,x in points:
            title = '%s: efficiency for isolation in R=%.1f cone < %s'%(particle,x,str(effcut).rstrip('0'))
            c2 = TCanvas(title,title,800,600)
            c2.cd()
            hraw = isomean(pid,etamin=0,etamax=2.5,R=x,EAsub="raw",eff=effcut)
            hdefScaled = isomean(pid,etamin=0,etamax=2.5,R=x,EAsub="defScaled",eff=effcut)
            hnew = isomean(pid,etamin=0,etamax=2.5,R=x,EAsub="new",eff=effcut)
            hs = [hraw,hdefScaled,hnew]
            for i in xrange(len(hs)):
                hs[i].SetMarkerStyle(21+i)
                hs[i].SetMarkerColor(colors[i])
                hs[i].SetLineColor(colors[i])
                if i==0: hs[i].SetTitle('%s: efficiency for isolation in R=%s cone < %s'%(particle,str(x).rstrip('0'),str(effcut).rstrip('0')))
                hs[i].Draw("E1" if i==0 else "E1same")
                if i==0: hs[i].GetYaxis().SetRangeUser(0.6,1.2)
                hs[i].GetXaxis().SetTitle("#rho")
                hs[i].GetYaxis().SetTitle("Efficiency")
            c2.Update()

            leg = TLegend(0.12,0.68,0.42,0.88)
            leg.SetFillColor(kWhite)
            leg.SetFillStyle(0)
            leg.SetBorderSize(0)
            leg.AddEntry(hraw,"Raw","lp")
            leg.AddEntry(hdefScaled,"Scaled EA","lp")
            leg.Draw()
            c2.Update()

            c2.Print('Eff_%s_%s.pdf'%(particle,text))

