import operator 
import itertools
import copy
from math import *

from ROOT import std 
from ROOT import TLorentzVector, TVectorD

from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.HeppyCore.framework.event import Event
from PhysicsTools.HeppyCore.statistics.counter import Counter, Counters
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle

import ROOT
import os

class ttHhistoCounterAnalyzer( Analyzer ):
    def __init__(self, cfg_ana, cfg_comp, looperName ):
        super(ttHhistoCounterAnalyzer,self).__init__(cfg_ana,cfg_comp,looperName) 
        self.doLHE = getattr(cfg_ana, 'doLHE', True)

    def declareHandles(self):
        super(ttHhistoCounterAnalyzer, self).declareHandles()
        if self.doLHE: 
            self.mchandles['LHEweights'] = AutoHandle( 'externalLHEProducer', 'LHEEventProduct', mayFail = True, fallbackLabel = 'source', lazy = False )
        self.mchandles['GenInfo'] = AutoHandle( ('generator','',''), 'GenEventInfoProduct' )

    def beginLoop(self, setup):
        super(ttHhistoCounterAnalyzer,self).beginLoop(setup)
        self.counters.addCounter('pairs')
        count = self.counters.counter('pairs')
        count.register('all events')
        if "outputfile" in setup.services :
            setup.services["outputfile"].file.cd()
            self.inputCounter = ROOT.TH1D("Count","Count",1,0,2)
            if self.cfg_comp.isMC:
                self.inputCounterSMS = ROOT.TH3D("CountSMS","CountSMS",3001,-0.5,3000.5,3001,-0.5,3000.5,1,0,2)
                if self.doLHE:
                    self.inputLHE = ROOT.TH1D("CountLHE","CountLHE",10001,-0.5,10000.5)
#                    self.inputLHESMS = ROOT.TH3D("CountLHESMS","CountLHESMS",3001,-0.5,3000.5,3001,-0.5,3000.5,10001,-0.5,10000.5) ### too big!
                self.inputGenWeights = ROOT.TH1D("SumGenWeights","SumGenWeights",1,0,2)
                self.inputGenWeightsSMS = ROOT.TH3D("SumGenWeightsSMS","SumGenWeightsSMS",3001,-0.5,3000.5,3001,-0.5,3000.5,1,0,2)

    def process(self, event):
        self.readCollections( event.input )
        self.inputCounter.Fill(1)

        isSMS = self.cfg_comp.isMC and event.susyModel
        if isSMS:
            if max(event.genSusyMScan1,event.genSusyMScan2)>3000: raise RuntimeError, 'Histograms are not wide enough to contain this mass point: %f,%f'%(event.genSusyMScan1,event.genSusyMScan2)
            self.inputCounterSMS.Fill(event.genSusyMScan1,event.genSusyMScan2,1)

        if self.cfg_comp.isMC:
            if self.doLHE:
              if self.mchandles['LHEweights'].isValid():
                for w in self.mchandles['LHEweights'].product().weights():
                    id_ = float(w.id)
                    wgt_ = float(w.wgt)
                    self.inputLHE.Fill(id_, wgt_)
#                    if isSMS: self.inputLHESMS.Fill(event.genSusyMScan1,event.genSusyMScan2,id_, wgt_)

        if self.cfg_comp.isMC:
            genWeight_ = float(self.mchandles['GenInfo'].product().weight())
            self.inputGenWeights.Fill(1, genWeight_);
            if isSMS: self.inputGenWeightsSMS.Fill(event.genSusyMScan1,event.genSusyMScan2,1, genWeight_);

        return True
