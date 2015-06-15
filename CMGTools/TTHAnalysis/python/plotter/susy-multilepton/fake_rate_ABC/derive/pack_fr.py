#!/usr/bin/env python

#this has to be in sync with what is defined in bin2Dto1Dlib.cc

debug = False

bins_pt=(10,25,35,70)
bins_eta=(0,1,2,2.5)
binning_code=0

import os,sys
sys.argv.append('-b-')
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.remove('-b-')
from array import *
ROOT.gStyle.SetPaintTextFormat(".2f")
ROOT.gStyle.SetOptStat(0)

NEWDIR="."

if "/bin2Dto1Dlib_cc.so" not in ROOT.gSystem.GetLibraries():
    ROOT.gROOT.ProcessLine(".L %s/src/CMGTools/TTHAnalysis/python/plotter/bin2Dto1Dlib.cc+" % os.environ['CMSSW_BASE']);

def makeH2D(name,xedges,yedges):
    return ROOT.TH2F(name,name,len(xedges)-1,array('f',xedges),len(yedges)-1,array('f',yedges))

def fillPlot2D(th2,plot1d):
    for xbin in xrange(1,th2.GetNbinsX()+1):
        for ybin in xrange(1,th2.GetNbinsY()+1):
            xval = th2.GetXaxis().GetBinCenter(xbin)
            yval = th2.GetYaxis().GetBinCenter(ybin)
            xbin1d = int(ROOT.gROOT.ProcessLine("bin2Dto1D(%f,%f,%d);" % (xval,yval,binning_code)))
            th2.SetBinContent(xbin,ybin,plot1d.GetBinContent(xbin1d))
            th2.SetBinError(xbin,ybin,plot1d.GetBinError(xbin1d))

def readPlot1D(alpha2d,beta2d,filename,plotnameL,plotnameT):
    slicefile = ROOT.TFile.Open(filename)
    if not slicefile: raise RuntimeError, "Cannot open "+filename
    plotL = slicefile.Get(plotnameL)
    plotT = slicefile.Get(plotnameT)
    if (not plotL) or (not plotT): 
        slicefile.ls()
        raise RuntimeError, "Cannot find plots "+plotnameL+","+plotnameT+" in "+filename    
    a,b = calculateABC(plotL,plotT)
    fillPlot2D(alpha2d,a)
    fillPlot2D(beta2d,b)
    slicefile.Close()

def calculateABC(plotL,plotT):
    if debug:
        plotL.Print()
        plotT.Print()
    thLA=plotL.ProjectionY(plotL.GetName()+'_pyA',2,2)
    thLB=plotL.ProjectionY(plotL.GetName()+'_pyB',3,3)
    thLC=plotL.ProjectionY(plotL.GetName()+'_pyC',4,4)
    thTA=plotT.ProjectionY(plotT.GetName()+'_pyA',2,2)
    thTB=plotT.ProjectionY(plotT.GetName()+'_pyB',3,3)
    thTC=plotT.ProjectionY(plotT.GetName()+'_pyC',4,4)
    alpha = plotL.ProjectionY('res_alpha')
    beta = plotL.ProjectionY('res_beta')
    alpha.Reset()
    beta.Reset()
    for i in xrange(thLA.GetNbinsX()):
        bin = i+1
        m = ROOT.TMatrix()
        m.ResizeTo(2,2)
        m[0][0]=thLB.GetBinContent(bin)
        m[0][1]=thLC.GetBinContent(bin)
        m[1][0]=thTB.GetBinContent(bin)
        m[1][1]=thTC.GetBinContent(bin)
        a = ROOT.TMatrix()
        a.ResizeTo(2,1)
        a[0][0]=thLA.GetBinContent(bin)
        a[1][0]=thTA.GetBinContent(bin)
        if debug:
            m.Print()
            a.Print()
        m.Invert()
        b = m*a
        alpha.SetBinContent(bin,b[0][0])
        beta.SetBinContent(bin,b[1][0])
        if debug:
            print 'alpha, beta =',alpha,beta
    return (alpha,beta)

def assemble2D(name,filename,plotnameL,plotnameT):
    out = ROOT.TFile.Open(NEWDIR+"/"+name+".root","RECREATE")
    out.cd()
    th2a = makeH2D(name+"_alpha",bins_pt,bins_eta)
    th2b = makeH2D(name+"_beta",bins_pt,bins_eta)
    try:
        readPlot1D(th2a,th2b,filename,plotnameL,plotnameT)
    except RuntimeError:
        print "Impossible to open file "+filename+", skipping..."
        return
    c = ROOT.TCanvas("canv_"+name,"canv_"+name)
    c.Divide(2)
    c.cd(1)
    th2a.Draw("TEXT")
    c.cd(2)
    th2b.Draw("TEXT")
    c.cd()
    c.SaveAs(NEWDIR+"/"+name+".pdf")
    out.WriteTObject(th2a)
    out.WriteTObject(th2b)
    out.ls()
    out.Close()
    
if __name__ == "__main__":
    PLOTSPATH="GOODFR"
    PLOTSPREFIX="derive"
    NEWDIR=PLOTSPATH+"_packed"
    os.mkdir(NEWDIR)
    for ob in ["Mu","El"]:
        assemble2D("FR_FO9_%s_antitight" % (ob,),"%s/%s_FO9%s/susy_2lss_fake_rate_ABC_study.root" % (PLOTSPATH,PLOTSPREFIX,ob),"reg_eta_mypt_antiBaway_background","reg_eta_mypt_tightaway_background")
        assemble2D("FR_FO9_%s_alltight" % (ob,),"%s/%s_FO9%s/susy_2lss_fake_rate_ABC_study.root" % (PLOTSPATH,PLOTSPREFIX,ob),"reg_eta_mypt_allaway_background","reg_eta_mypt_tightaway_background")
