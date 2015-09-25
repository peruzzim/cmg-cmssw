#include "TH2F.h"
#include <iostream>

TH2F *h_ele_neutral;
TH2F *h_ele_charged;
TH2F *h_mu_neutral;
TH2F *h_mu_charged;

void setEAhistos(TH2F *en, TH2F *ec, TH2F *mn, TH2F *mc){
  h_ele_neutral = en;
  h_ele_charged = ec;
  h_mu_neutral = mn;
  h_mu_charged = mc;
}

float getEA(int pid, int isocode, float eta, float R){

  TH2F *h = NULL;
  if (pid==11){
    if (isocode==0) h = h_ele_neutral;
    else h = h_ele_charged;
  }
  else if (pid==13){
    if (isocode==0) h = h_mu_neutral;
    else h = h_mu_charged;
  }

  float ea = h->GetBinContent(h->GetXaxis()->FindBin(fabs(eta)), h->GetYaxis()->FindBin(R));

  //  std::cout << pid << " " << isocode << " " << eta << " " << R << " " << ea << std::endl;
  return ea;

}
