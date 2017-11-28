/*
Adapted from:
root -l examples/Example3.C'("delphes_output.root")'
This macro shows how to access the particle-level reference for reconstructed objects.
It is also shown how to loop over the jet constituents.

Re-tooled to make plots of track parameters 

*/

#ifdef __CLING__
R__LOAD_LIBRARY(libDelphes)
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootResult.h"
#else
class ExRootTreeReader;
class ExRootResult;
#endif

#include "TROOT.h"

//------------------------------------------------------------------------------

void PrintTrack(Track *track)
{
  std::cout << "pT "       << track->PT       << std::endl;
  std::cout << "eta "      << track->Eta      << std::endl;
  std::cout << "phi "      << track->Phi      << std::endl;
  std::cout << "CotTheta " << track->CtgTheta << std::endl;
  std::cout << "Charge "   << track->Charge   << std::endl;
  std::cout << "D0 "       << track->DZ       << std::endl;
  std::cout << "DZ "       << track->D0       << std::endl;
}

//------------------------------------------------------------------------------

struct TestPlots
{

  //TH1 *fElectronDeltaPT;
  //TH1 *fElectronDeltaEta;
  //TH1 *fPhotonDeltaPT;
  //TH1 *fPhotonDeltaEta;
  //TH1 *fPhotonDeltaE;
  //TH1 *fMuonDeltaPT;
  //TH1 *fMuonDeltaEta;
  //TH1 *fJetDeltaPT;

  TH1 *z0Res; 
  TH2 *z0Res_pt;
  TH2 *z0Res_eta;

  TH1 *d0Res;
  TH2 *d0Res_pt;
  TH2 *d0Res_eta;

  TH1 *CtgThetaRes;
  TH2 *CtgThetaRes_pt;
  TH2 *CtgThetaRes_eta;

  TH1 *pt;
  TH1 *ptRes;
  TH2 *ptRes_pt;

  TH1 *eta;
  TH1 *etaRes;
  TH2 *etaRes_eta;

};


//------------------------------------------------------------------------------

void BookHistograms(ExRootResult *result, TestPlots *plots)
{
  TLegend *legend;
  TPaveText *comment;
  
  // Basic kinematics
  // pt
  plots->pt = result->AddHist1D(
      "pt", "pt", "Track p_{T} [GeV]", "Number of Tracks",
      100, 0, 1000, 0, 1);
  plots->ptRes = result->AddHist1D(
      "ptRes", "pt resolution", "x", "y",
      100, -3, 3, 0, 0);
  plots->ptRes_pt = result->AddHist2D(
      "ptRes_pt", "pt resolution", "x", "y", 
      100, -1, 1, 100, 0, 100);
  //eta
  plots->eta = result->AddHist1D(
      "eta", "eta", "Track #eta", "Number of Tracks",
      100, -6, 6);
  plots->etaRes = result->AddHist1D(
      "etaRes", "eta resolution", "x", "y", 
      100, -6, 6);
  plots->etaRes_eta = result->AddHist2D(
      "etaRes_eta", "eta resolution", "#eta resolution", "Truth #eta", 
      100, -6, 6, 100, -6, 6);


  // z0
  float z0Min(-10), z0Max(10);
  plots->z0Res = result->AddHist1D(
      "z0_resolution", "z0 resolution", "#deltaz_{0} [mm]", "Number of Tracks", 
      100, z0Min, z0Max);

  plots->z0Res_pt = result->AddHist2D(
      "z0_resolution_pt", "z0 resolution", "#deltaz_{0} [mm]", "Truth p_{T} [GeV]", 
      100, z0Min, z0Max, 100, 0, 1000);

  plots->z0Res_eta = result->AddHist2D(
      "z0_resolution_eta", "z0 resolution", "#deltaz_{0} [mm]", "Truth #eta", 
      100, z0Min, z0Max, 100, -2, 2);

  // d0 
  float d0Min(-100), d0Max(100);
  plots->d0Res = result->AddHist1D(
      "d0_resolution", "d0 resolution", "#deltad_{0} [mm]", "Number of Tracks",
      100, d0Min, d0Max);

  plots->d0Res_pt = result->AddHist2D(
      "d0_resolution_pt", "d0 resolution", "#deltad_{0} [mm]", "Truth p_{T} [GeV]",
      100, d0Min, d0Max, 100, 0, 1000);

  plots->d0Res_eta = result->AddHist2D(
      "d0_resolution_eta", "d0 resolution", "#deltad_{0} [mm]", "Truth #eta",
      100, d0Min, d0Max, 100, -2, 2);

  // cot(theta)
  float CtgThMin(-0.001), CtgThMax(0.001);
  plots->CtgThetaRes = result->AddHist1D(
      "CtgThetaRes", "CtgThetaRes", "#deltacot(#theta)", "Number of Tracks",
      100, CtgThMin, CtgThMax);
  plots->CtgThetaRes_pt = result->AddHist2D(
      "CtgThetaRes_pt", "CtgThetaRes_pt", "#deltacot(#theta)", "Truth p_{T} [GeV]",
      100, CtgThMin, CtgThMax, 100, 0, 1000);
  plots->CtgThetaRes_eta = result->AddHist2D(
      "CtgThetaRes_eta", "CtgThetaRes_eta", "#deltacot(#theta)", "Truth #eta",
      100, CtgThMin, CtgThMax, 100, -2, 2);
  

    //TH2 *CtgThetaRes_eta;


  

  /***********
  plots->fElectronDeltaPT = result->AddHist1D(
    "electron_delta_pt", "(p_{T}^{particle} - p_{T}^{electron})/p_{T}^{particle}",
    "(p_{T}^{particle} - p_{T}^{electron})/p_{T}^{particle}", "number of electrons",
    100, -0.1, 0.1);

  plots->fElectronDeltaEta = result->AddHist1D(
    "electron_delta_eta", "(#eta^{particle} - #eta^{electron})/#eta^{particle}",
    "(#eta^{particle} - #eta^{electron})/#eta^{particle}", "number of electrons",
    100, -0.1, 0.1);

  plots->fPhotonDeltaPT = result->AddHist1D(
    "photon_delta_pt", "(p_{T}^{particle} - p_{T}^{photon})/p_{T}^{particle}",
    "(p_{T}^{particle} - p_{T}^{photon})/p_{T}^{particle}", "number of photons",
    100, -0.1, 0.1);

  plots->fPhotonDeltaEta = result->AddHist1D(
    "photon_delta_eta", "(#eta^{particle} - #eta^{photon})/#eta^{particle}",
    "(#eta^{particle} - #eta^{photon})/#eta^{particle}", "number of photons",
    100, -0.1, 0.1);

  plots->fPhotonDeltaE = result->AddHist1D(
    "photon_delta_energy", "(E^{particle} - E^{photon})/E^{particle}",
    "(E^{particle} - E^{photon})/E^{particle}", "number of photons",
    100, -0.1, 0.1);

  plots->fMuonDeltaPT = result->AddHist1D(
    "muon_delta_pt", "(p_{T}^{particle} - p_{T}^{muon})/p_{T}^{particle}",
    "(p_{T}^{particle} - p_{T}^{muon})/p_{T}^{particle}", "number of muons",
    100, -0.1, 0.1);

  plots->fMuonDeltaEta = result->AddHist1D(
    "muon_delta_eta", "(#eta^{particle} - #eta^{muon})/#eta^{particle}",
    "(#eta^{particle} - #eta^{muon})/#eta^{particle}", "number of muons",
    100, -0.1, 0.1);

  plots->fJetDeltaPT = result->AddHist1D(
    "jet_delta_pt", "(p_{T}^{jet} - p_{T}^{constituents})/p_{T}^{jet}",
    "(p_{T}^{jet} - p_{T}^{constituents})/p_{T}^{jet}", "number of jets",
    100, -1.0e-1, 1.0e-1);
    **********/

}

//------------------------------------------------------------------------------

void AnalyseEvents(ExRootTreeReader *treeReader, TestPlots *plots)
{
  //TClonesArray *branchElectron = treeReader->UseBranch("Electron");
  //TClonesArray *branchPhoton = treeReader->UseBranch("Photon");
  //TClonesArray *branchMuon = treeReader->UseBranch("Muon");
  //TClonesArray *branchEFlowTrack = treeReader->UseBranch("EFlowTrack");
  //TClonesArray *branchEFlowPhoton = treeReader->UseBranch("EFlowPhoton");
  //TClonesArray *branchEFlowNeutralHadron = treeReader->UseBranch("EFlowNeutralHadron");
  //TClonesArray *branchJet = treeReader->UseBranch("Jet");

  // can we have track jets?

  TClonesArray *branchParticle = treeReader->UseBranch("Particle");
  TClonesArray *branchTruthTrack = treeReader->UseBranch("TruthTrack");
  TClonesArray *branchTrack = treeReader->UseBranch("Track");

  Long64_t allEntries = treeReader->GetEntries();

  cout << "** Chain contains " << allEntries << " events" << endl;

  GenParticle *particle, *truthParticle;
  Electron *electron;
  Photon *photon;
  Muon *muon;

  Track *track, *truthTrack;
  Tower *tower;

  Jet *jet;
  TObject *object;

  TLorentzVector momentum;

  Float_t Eem, Ehad;
  Bool_t skip;

  Long64_t entry;

  Int_t i, j, pdgCode;

  // Loop over all events
  for(entry = 0; entry < allEntries; ++entry)
  {
    // Load selected branches with data from specified event
    treeReader->ReadEntry(entry);

    

    //std::cout << "ntracks: " << branchTrack->GetEntriesFast()  << std::endl;
      

    // loop over all truth tracks
    for(j=0; j<branchTruthTrack->GetEntriesFast(); ++j){
      truthTrack      = (Track*) branchTruthTrack->At(j);
      truthParticle   = (GenParticle*) truthTrack->Particle.GetObject(); 
      if( fabs(truthTrack->Eta) > 2.0 ) continue; // remove tracks with |eta| > 2.0 
      if(truthTrack->PT < 0.5) continue;

      // Loop over all tracks in event
      for(i=0; i<branchTrack->GetEntriesFast(); ++i)
      {
        track = (Track*) branchTrack->At(i);
        particle = (GenParticle*) track->Particle.GetObject(); 

        //if (i==0) std::cout << gen->fUniqueID << std::endl;
        //if(particle == truthParticle){
        if(particle->GetUniqueID() == truthParticle->GetUniqueID()){
          double z0Resolution = track->DZ - truthTrack->DZ; 
          double ptResolution = track->PT - truthTrack->PT;
          double d0Resolution = track->D0 - truthTrack->D0;
          double etaResolution = track->Eta - truthTrack->Eta;
          double CtgThetaResolution = track->CtgTheta - truthTrack->CtgTheta;

          //std::cout << "ptRes: " << ptResolution << std::endl;
          //std::cout << "etaRes: " << etaResolution << std::endl;

          //std::cout << track->DZ << std::endl;
          //std::cout << truthTrack->DZ << std::endl;
          
          //std::cout << "\tsmeered" << std::endl; 
          //PrintTrack(track);
          //std::cout << "\ttruth" << std::endl; 
          //PrintTrack(truthTrack);

          //std::cout << "Match found for i " << i << "\tj " << j << std::endl;
          //std::cout << "z0 res: " << z0resolution << std::endl;
          
          plots->pt->Fill(track->PT);
          plots->ptRes->Fill(ptResolution);
          plots->ptRes_pt->Fill(ptResolution, truthTrack->PT);

          plots->eta->Fill(track->Eta);
          plots->etaRes->Fill(etaResolution);
          plots->etaRes_eta->Fill(etaResolution, truthTrack->Eta);

          plots->z0Res->Fill(z0Resolution);
          plots->z0Res_pt->Fill(z0Resolution, truthTrack->PT);
          plots->z0Res_eta->Fill(z0Resolution, truthTrack->Eta);

          plots->d0Res->Fill(d0Resolution);
          plots->d0Res_pt->Fill(d0Resolution, truthTrack->PT);
          plots->d0Res_eta->Fill(d0Resolution, truthTrack->Eta);

          plots->CtgThetaRes->Fill(CtgThetaResolution);
          plots->CtgThetaRes_pt->Fill(CtgThetaResolution, truthTrack->PT);
          plots->CtgThetaRes_eta->Fill(CtgThetaResolution, truthTrack->Eta);
        }


        
      }

      //plots->fz0Res->Fill(track->DZ);
    }

    /*******************
    // Loop over all electrons in event
    for(i = 0; i < branchElectron->GetEntriesFast(); ++i)
    {
      electron = (Electron*) branchElectron->At(i);
      particle = (GenParticle*) electron->Particle.GetObject();

      plots->fElectronDeltaPT->Fill((particle->PT - electron->PT)/particle->PT);
      plots->fElectronDeltaEta->Fill((particle->Eta - electron->Eta)/particle->Eta);
    }

    // Loop over all photons in event
    for(i = 0; i < branchPhoton->GetEntriesFast(); ++i)
    {
      photon = (Photon*) branchPhoton->At(i);

      // skip photons with references to multiple particles
      if(photon->Particles.GetEntriesFast() != 1) continue;

      particle = (GenParticle*) photon->Particles.At(0);
      plots->fPhotonDeltaPT->Fill((particle->PT - photon->PT)/particle->PT);
      plots->fPhotonDeltaEta->Fill((particle->Eta - photon->Eta)/particle->Eta);
      plots->fPhotonDeltaE->Fill((particle->E - photon->E)/particle->E);
          
    }

    // Loop over all muons in event
    for(i = 0; i < branchMuon->GetEntriesFast(); ++i)
    {
      muon = (Muon*) branchMuon->At(i);
      particle = (GenParticle*) muon->Particle.GetObject();

      plots->fMuonDeltaPT->Fill((particle->PT - muon->PT)/particle->PT);
      plots->fMuonDeltaEta->Fill((particle->Eta - muon->Eta)/particle->Eta);
    }

    // cout << "--  New event -- " << endl;

    // Loop over all jets in event
    for(i = 0; i < branchJet->GetEntriesFast(); ++i)
    {
      jet = (Jet*) branchJet->At(i);

      momentum.SetPxPyPzE(0.0, 0.0, 0.0, 0.0);

      // cout<<"Looping over jet constituents. Jet pt: "<<jet->PT<<", eta: "<<jet->Eta<<", phi: "<<jet->Phi<<endl;

      // Loop over all jet's constituents
      for(j = 0; j < jet->Constituents.GetEntriesFast(); ++j)
      {
        object = jet->Constituents.At(j);

        // Check if the constituent is accessible
        if(object == 0) continue;

        if(object->IsA() == GenParticle::Class())
        {
          particle = (GenParticle*) object;
          // cout << "    GenPart pt: " << particle->PT << ", eta: " << particle->Eta << ", phi: " << particle->Phi << endl;
          momentum += particle->P4();
        }
        else if(object->IsA() == Track::Class())
        {
          track = (Track*) object;
          // cout << "    Track pt: " << track->PT << ", eta: " << track->Eta << ", phi: " << track->Phi << endl;
          momentum += track->P4();
        }
        else if(object->IsA() == Tower::Class())
        {
          tower = (Tower*) object;
          // cout << "    Tower pt: " << tower->ET << ", eta: " << tower->Eta << ", phi: " << tower->Phi << endl;
          momentum += tower->P4();
        }
      }
      plots->fJetDeltaPT->Fill((jet->PT - momentum.Pt())/jet->PT);
    }
  *********************/

  } // end loop over entries
} // end AnalyseEvents 



//------------------------------------------------------------------------------

void PrintHistograms(ExRootResult *result, TestPlots *plots)
{
  result->Print("pdf");
}


//------------------------------------------------------------------------------

void trackParameters(const char *inputFile)
{
  gSystem->Load("libDelphes");
  gROOT->SetBatch(1);

  TChain *chain = new TChain("Delphes");
  chain->Add(inputFile);

  ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
  ExRootResult *result = new ExRootResult();

  TestPlots *plots = new TestPlots;
  BookHistograms(result, plots);
  AnalyseEvents(treeReader, plots);
  PrintHistograms(result, plots);
  result->Write("results.root");

  cout << "** Exiting..." << endl;

  delete plots;
  delete result;
  delete treeReader;
  delete chain;
}

//------------------------------------------------------------------------------
