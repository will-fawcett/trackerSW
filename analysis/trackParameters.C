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
  TH3 *z0Res_pt_eta;

  TH1 *d0Res;
  TH2 *d0Res_pt;
  TH2 *d0Res_eta;
  TH3 *d0Res_pt_eta;

  TH1 *CtgThetaRes;
  TH2 *CtgThetaRes_pt;
  TH2 *CtgThetaRes_eta;
  TH3 *CtgThetaRes_pt_eta;

  TH1 *phiRes;
  TH2 *phiRes_pt;
  TH2 *phiRes_eta;
  TH3 *phiRes_pt_eta;

  TH1 *pt;
  TH1 *ptRes;
  TH2 *ptRes_pt;
  TH2 *ptRes_eta;
  TH3 *ptRes_pt_eta;

  TH1 *ptResRaw;
  TH2 *ptResRaw_pt;
  TH2 *ptResRaw_eta;
  TH3 *ptResRaw_pt_eta;

  TH1 *eta;
  TH1 *etaRes;
  TH2 *etaRes_eta;
  TH3 *etaRes_pt_eta;

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
      1000, 0, 2000, 0, 1);
  float ptMinRaw(-100), ptMaxRaw(100);
  plots->ptResRaw = result->AddHist1D(
      "ptResRaw", "pt resolution", "#deltap_{T} [GeV]", "Number of Tracks",
      1000, ptMinRaw, ptMaxRaw, 0, 0);
  plots->ptResRaw_pt = result->AddHist2D(
      "ptResRaw_pt", "pt resolution", "#deltap_{T} [GeV]", "Truth p_{T} [GeV]", 
      1000, ptMinRaw, ptMaxRaw, 200, 0, 2000);
  plots->ptResRaw_eta = result->AddHist2D(
      "ptResRaw_eta", "pt resolution", "#deltap_{T} [GeV]", "Truth #eta", 
      1000, ptMinRaw, ptMaxRaw, 200, -2, 2);
  plots->ptResRaw_pt_eta = result->AddHist3D(
      "ptResRaw_pt_eta", "pt resolution", "#deltap_{T} [GeV]", "Truth p_{T} [GeV]", "Truth #eta", 
      1000, ptMinRaw, ptMaxRaw, 200, 0, 200, 100, -2, 2);

  float ptMin(-10), ptMax(10);
  plots->ptRes = result->AddHist1D(
      "ptRes", "pt resolution", "#deltap_{T}/p_{T}", "Number of Tracks",
      1000, ptMin, ptMax, 0, 0);
  plots->ptRes_pt = result->AddHist2D(
      "ptRes_pt", "pt resolution", "#deltap_{T}/p_{T}", "Truth p_{T} [GeV]", 
      1000, ptMin, ptMax, 200, 0, 1000);
  plots->ptRes_eta = result->AddHist2D(
      "ptRes_eta", "eta resolution", "#deltap_{T}/p_{T}", "Truth #eta", 
      1000, ptMin, ptMax, 200, -2, 2);
  plots->ptRes_pt_eta = result->AddHist3D(
      "ptRes_pt_eta", "pt resolution", "#deltap_{T}/p_{T}", "Truth p_{T} [GeV]", "Truth #eta", 
      1000, ptMin, ptMax, 200, 0, 200, 100, -2, 2);


  //eta
  plots->eta = result->AddHist1D(
      "eta", "eta", "Track #eta", "Number of Tracks",
      100, -4, 4);
  float etaMin(-0.001), etaMax(0.001);
  plots->etaRes = result->AddHist1D(
      "etaRes", "eta resolution", "#delta#eta", "Number of Tracks", 
      1000, etaMin, etaMax);
  plots->etaRes_eta = result->AddHist2D(
      "etaRes_eta", "eta resolution", "#delta#eta", "Truth #eta", 
      1000, etaMin, etaMax, 100, -2, 2);
  plots->etaRes_pt_eta = result->AddHist3D(
      "etaRes_pt_eta", "pt resolution", "#deltap_{T}/p_{T}", "Truth p_{T} [GeV]", "Truth #eta", 
      1000, etaMin, etaMax, 200, 0, 200, 100, -2, 2);

  // z0
  float z0Min(-200), z0Max(200); // large range for low pT tracks needed 
  plots->z0Res = result->AddHist1D(
      "z0Res", "z0 resolution", "#deltaz_{0} [mm]", "Number of Tracks", 
      1000, z0Min, z0Max);
  plots->z0Res_pt = result->AddHist2D(
      "z0Res_pt", "z0 resolution", "#deltaz_{0} [mm]", "Truth p_{T} [GeV]", 
      1000, z0Min, z0Max, 200, 0, 2000);
  plots->z0Res_eta = result->AddHist2D(
      "z0Res_eta", "z0 resolution", "#deltaz_{0} [mm]", "Truth #eta", 
      1000, z0Min, z0Max, 200, -2, 2);
  plots->z0Res_pt_eta = result->AddHist3D(
      "z0Res_pt_eta", "z0 resolution", "#deltaz_{0} [mm]", "Truth p_{T} [GeV]", "Truth #eta", 
      2000, z0Min, z0Max, 200, 0, 200, 100, -2, 2); // particularly tricky, lots of bins


  // d0 
  float d0Min(-1000), d0Max(1000);
  plots->d0Res = result->AddHist1D(
      "d0Res", "d0 resolution", "#deltad_{0} [mm]", "Number of Tracks",
      1000, d0Min, d0Max);
  plots->d0Res_pt = result->AddHist2D(
      "d0Res_pt", "d0 resolution", "#deltad_{0} [mm]", "Truth p_{T} [GeV]",
      1000, d0Min, d0Max, 200, 0, 2000);
  plots->d0Res_eta = result->AddHist2D(
      "d0Res_eta", "d0 resolution", "#deltad_{0} [mm]", "Truth #eta",
      1000, d0Min, d0Max, 200, -2, 2);
  plots->d0Res_pt_eta = result->AddHist3D(
      "d0Res_pt_eta", "d0 resolution", "#deltad_{0} [mm]", "Truth p_{T} [GeV]", "Truth #eta", 
      1000, d0Min, d0Max, 200, 0, 200, 100, -2, 2);

  // cot(theta)
  float CtgThMin(-0.001), CtgThMax(0.001);
  plots->CtgThetaRes = result->AddHist1D(
      "CtgThetaRes", "CtgThetaRes", "#deltacot(#theta)", "Number of Tracks",
      1000, CtgThMin, CtgThMax);
  plots->CtgThetaRes_pt = result->AddHist2D(
      "CtgThetaRes_pt", "CtgThetaRes_pt", "#deltacot(#theta)", "Truth p_{T} [GeV]",
      1000, CtgThMin, CtgThMax, 200, 0, 2000);
  plots->CtgThetaRes_eta = result->AddHist2D(
      "CtgThetaRes_eta", "CtgThetaRes_eta", "#deltacot(#theta)", "Truth #eta",
      1000, CtgThMin, CtgThMax, 200, -2, 2);
  plots->CtgThetaRes_pt_eta = result->AddHist3D(
      "CtgThetaRes_pt_eta", "CtgTheta resolution", "#deltacot(#theta)", "Truth p_{T} [GeV]", "Truth #eta", 
      1000, CtgThMin, CtgThMax, 200, 0, 200, 100, -2, 2);

  // phi
  float phiMin(-0.1), phiMax(0.1);
  plots->phiRes = result->AddHist1D(
      "phiRes", "phi resolution", "#delta#phi", "Number of Tracks",
      1000, phiMin, phiMax);
  plots->phiRes_pt = result->AddHist2D(
      "phiRes_pt", "phi resolution", "#delta#phi", "Truth p_{T} [GeV]",
      1000, phiMin, phiMax, 200, 0, 2000);
  plots->phiRes_eta = result->AddHist2D(
      "phiRes_eta", "phi resolution", "#delta#phi", "Truth #eta",
      1000, phiMin, phiMax, 200, -2, 2);
  plots->phiRes_pt_eta = result->AddHist3D(
      "phiRes_pt_eta", "phi resolution", "#delta#phi", "Truth p_{T} [GeV]", "Truth #eta", 
      1000, phiMin, phiMax, 200, 0, 200, 100, -2, 2);

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

    // print every 10% complete
    if( entry % 100==0 ) std::cout << "Event " << entry << " out of " << allEntries << std::endl;

    

    //std::cout << "ntracks: " << branchTrack->GetEntriesFast()  << std::endl;
      

    // loop over all truth tracks
    for(j=0; j<branchTruthTrack->GetEntriesFast(); ++j){
      truthTrack      = (Track*) branchTruthTrack->At(j);
      truthParticle   = (GenParticle*) truthTrack->Particle.GetObject(); 
      if( fabs(truthTrack->Eta) > 2.0 ) continue; // remove tracks with |eta| > 2.0 
      if(truthTrack->PT < 1.0) continue;

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
          double phiResolution = track->Phi - truthTrack->Phi;

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
          //
          float truthPt = truthTrack->PT;
          float truthEta = truthTrack->Eta;
          
          plots->pt->Fill(track->PT);
          plots->ptResRaw->Fill(ptResolution);
          plots->ptResRaw_pt->Fill(ptResolution, truthPt);
          plots->ptResRaw_eta->Fill(ptResolution, truthEta);
          plots->ptResRaw_pt_eta->Fill(ptResolution, truthPt, truthEta);

          plots->ptRes->Fill(ptResolution/truthPt);
          plots->ptRes_pt->Fill(ptResolution/truthPt, truthPt);
          plots->ptRes_eta->Fill(ptResolution/truthPt, truthEta);
          plots->ptRes_pt_eta->Fill(ptResolution/truthPt, truthPt, truthEta);

          plots->eta->Fill(track->Eta);
          plots->etaRes->Fill(etaResolution);
          plots->etaRes_eta->Fill(etaResolution, truthEta);
          plots->etaRes_pt_eta->Fill(etaResolution, truthPt, truthEta);

          plots->z0Res->Fill(z0Resolution);
          plots->z0Res_pt->Fill(z0Resolution, truthPt);
          plots->z0Res_eta->Fill(z0Resolution, truthEta);
          plots->z0Res_pt_eta->Fill(z0Resolution, truthPt, truthEta);

          plots->d0Res->Fill(d0Resolution);
          plots->d0Res_pt->Fill(d0Resolution, truthPt);
          plots->d0Res_eta->Fill(d0Resolution, truthEta);
          plots->d0Res_pt_eta->Fill(d0Resolution, truthPt, truthEta);

          plots->CtgThetaRes->Fill(CtgThetaResolution);
          plots->CtgThetaRes_pt->Fill(CtgThetaResolution, truthPt);
          plots->CtgThetaRes_eta->Fill(CtgThetaResolution, truthEta);
          plots->CtgThetaRes_pt_eta->Fill(CtgThetaResolution, truthPt, truthEta);

          plots->phiRes->Fill(phiResolution);
          plots->phiRes_pt->Fill(phiResolution, truthPt);
          plots->phiRes_eta->Fill(phiResolution, truthEta);
          plots->phiRes_pt_eta->Fill(phiResolution, truthPt, truthEta);
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
