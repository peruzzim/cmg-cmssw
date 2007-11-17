// -*-C++-*-
#ifndef L1TRCT_H
#define L1TRCT_H

/*
 * \file L1TRCT.h
 *
 * $Date: 2007/02/19 22:49:53 $
 * $Revision: 1.1 $
 * \author P. Wittich
 * $Id: L1TRCT.h,v 1.1 2007/02/19 22:49:53 wittich Exp $
 * $Log: L1TRCT.h,v $
 * Revision 1.1  2007/02/19 22:49:53  wittich
 * - Add RCT monitor
 *
 *
 *
*/

// system include files
#include <memory>
#include <unistd.h>


#include <iostream>
#include <fstream>
#include <vector>


// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

// DQM
#include "DQMServices/Core/interface/DaqMonitorBEInterface.h"
#include "DQMServices/Daemon/interface/MonitorDaemon.h"


// Trigger Headers



//
// class declaration
//

class L1TRCT : public edm::EDAnalyzer {

public:

// Constructor
  L1TRCT(const edm::ParameterSet& ps);

// Destructor
 virtual ~L1TRCT();

protected:
// Analyze
 void analyze(const edm::Event& e, const edm::EventSetup& c);

// BeginJob
 void beginJob(const edm::EventSetup& c);

// EndJob
void endJob(void);

private:
  // ----------member data ---------------------------
  DaqMonitorBEInterface * dbe;

  // RCT stuff
  MonitorElement* rctRegionsEtEtaPhi_;
  MonitorElement* rctRegionsOccEtaPhi_;
  MonitorElement* rctTauVetoEtaPhi_;
  MonitorElement* rctIsoEmEtEtaPhi_;
  MonitorElement* rctIsoEmOccEtaPhi_;
  MonitorElement* rctNonIsoEmEtEtaPhi_;
  MonitorElement* rctNonIsoEmOccEtaPhi_;
  MonitorElement* rctRegionRank_;
  MonitorElement* rctIsoEmRank_;
  MonitorElement* rctNonIsoEmRank_;


  int nev_; // Number of events processed
  std::string outputFile_; //file name for ROOT ouput
  bool verbose_;
  bool monitorDaemon_;
  ofstream logFile_;

  edm::InputTag rctSource_;


};

#endif
