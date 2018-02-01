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

#include "modules/Delphes.h"
#include "classes/DelphesClasses.h"
#include "classes/DelphesFactory.h"



bool DEBUG = false;
//bool DEBUG = true;

//bool calculateTrackParameters = false; 
bool calculateTrackParameters = true; 

std::string PrintTLorentz(TLorentzVector &v){
  std::ostringstream s;
  s <<  " (" << v.Pt() << ", " << v.Eta() << ", " << v.Phi() << ", " << v.M() << ")"; 
  return s.str();
}

// poor mans version of a container class to replace TLorentzVector
class threeVec
{
  private:
    float m_Pt;
    float m_Rapidity;
    float m_Phi;
  public:
    threeVec();
    void SetPtEtaPhi(float pt, float eta, float phi){
      m_Pt=pt;
      m_Rapidity=eta;
      m_Phi=phi;
    }
    float Pt(){return m_Pt;}
    float Rapidity(){return m_Rapidity;}
    float Eta(){return m_Rapidity;}
    float Phi(){return m_Phi;}
    ~threeVec();
};

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

inline float deltaPhi(float phi1, float phi2){
  return acos( cos( phi1 - phi2 ));
}

//------------------------------------------------------------------------------

void antiKt(const std::vector<TLorentzVector> i_inputs, std::vector<TLorentzVector>& outputJets )
{
  //////////////////////////////////////////////////
  // Manual implementation of the anti-kT algorithm 
  //////////////////////////////////////////////////

  float RADIUS_PARAMETER = 0.4; 
  std::vector<TLorentzVector> inputs;
  for(auto entity : i_inputs){
    inputs.push_back(entity);
  }


  // anti kt algorithm 
  int nInputs = inputs.size();
  while (nInputs>0){
    Double_t dRij  = 999999999.;
    Double_t dRi   = 999999999.;
    int dRiindex   = 0;
    int dRijindex1 = 0;
    int dRijindex2 = 0;

    // Calculate the beam distance ( 1/pT_i^2 ), find the entity with the smallest beam distance  
    for (Int_t i=0; i<nInputs; ++i){
      if (pow(1./(inputs.at(i)).Pt(),2)<dRi){
        dRi      = pow(1.0/(inputs.at(i)).Pt(),2);
        dRiindex = i;
        }
    }

    //if(DEBUG) std::cout << "beam distance: " << dRi << " index: " << dRiindex << std::endl;

    // Calculate the distance metric between all entities, find the smallest distance
    for (Int_t i=0; i<nInputs-1; ++i){
      float pT_i       = inputs.at(i).Pt();
      float rapidity_i = inputs.at(i).Rapidity();
      float phi_i      = inputs.at(i).Phi();

      for (Int_t j=i+1; j<nInputs; ++j){
        float pT_j       = inputs.at(j).Pt();
        float rapidity_j = inputs.at(j).Rapidity();
        float phi_j      = inputs.at(j).Phi();

        // distance metric calculation
        //Double_t tempdRij = std::min(pow(1.0/(inputs.at(i)).Pt(),2),pow(1.0/(inputs.at(j)).Pt(),2)) * (pow((inputs.at(i)).Rapidity()-(inputs.at(j)).Rapidity(),2)+pow(acos(cos(inputs.at(i).Phi()-inputs.at(j).Phi())),2));
        Double_t tempdRij = std::min( pow(1.0/pT_i,2), pow(1.0/pT_j,2) ) * ( pow(rapidity_i-rapidity_j,2) + pow(deltaPhi(phi_i, phi_j),2) ) / pow(RADIUS_PARAMETER,2);
        // find the smallest distance 
        if (tempdRij<dRij){
          dRij=tempdRij;
          dRijindex1 = i;
          dRijindex2 = j;
        }
      }
    }

    //if(DEBUG) std::cout << "smallest distance metric: " << dRij << " between: " << dRijindex1 << PrintTLorentz(inputs.at(dRijindex1)) << " and " << dRijindex2 << PrintTLorentz(inputs.at(dRijindex2)) << std::endl;

    int deleteIndex=0;
    if (dRi<dRij){ // label entity as a jet 
      deleteIndex=dRiindex;
      TLorentzVector aJet = inputs.at(dRiindex);
      outputJets.push_back( aJet ); 
    }else{ // cluster: add input entity j to entity i
      inputs.at(dRijindex1) += inputs.at(dRijindex2);
      deleteIndex=dRijindex2;
    }
    //remove the entity from the collection
    inputs.erase(inputs.begin()+deleteIndex);
    nInputs = nInputs-1;
  }
}


//------------------------------------------------------------------------------

struct TestPlots
{

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

  TH2 *track_eta_phi_pt; 
  TH2 *jet_eta_phi_pt; 

  TH1 *allJetPt; 
  TH1 *nJets;
  std::vector<TH1*> jetNPt;
  std::vector<TH1*> jetNEta;
  std::vector<TH1*> jetNPhi;


};

    


//------------------------------------------------------------------------------

void BookHistograms(ExRootResult *result, TestPlots *plots)
{
  TLegend *legend;
  TPaveText *comment;
  
  // jet histograms
  for(int i=0; i<7; ++i){
    plots->jetNPt.push_back(
        result->AddHist1D( ("jet"+to_string(i+1)+"Pt").c_str(), "", (to_string(i+1)+" Jet p_{T} [GeV]").c_str(), "",  100, 0, 1000, 0, 0) 
        );
    plots->jetNEta.push_back(
        result->AddHist1D( ("jet"+to_string(i+1)+"Eta").c_str(), "", (to_string(i+1)+" Jet #eta").c_str(), "",  100, -2.5, 2.5) 
        );
    plots->jetNPhi.push_back(
        result->AddHist1D( ("jet"+to_string(i+1)+"Phi").c_str(), "", (to_string(i+1)+" Jet #phi").c_str(), "",  100, -M_PI, M_PI) 
        );
  }
  plots->nJets = result->AddHist1D( "nJets", "nJets", "Number of Jets", "", 100, 0, 100, 0, 0 );
  plots->allJetPt = result->AddHist1D("allJetPt", "", "Jet p_{T} (all jets) [GeV]", "", 100, 0, 1000);

  // Plots only used if track parameters are calculated 
  if(calculateTrackParameters){

    // Basic kinematics
    // pt
    plots->pt = result->AddHist1D(
        "pt", "pt", "Track p_{T} [GeV]", "Number of Tracks",
        1000, 0, 2000, 0, 1);
    float ptMinRaw(-200), ptMaxRaw(200); // wont be able to calculate pT resolutions for tracks with > 200 GeV 
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
        4000, ptMinRaw, ptMaxRaw, 200, 0, 200, 40, -2, 2); // lots of bins needed since pT resolution degreades over many decades

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
    float z0Min(-20), z0Max(20); // large range for low pT tracks needed 
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
    float d0Min(-50), d0Max(50);
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
    float CtgThMin(-0.1), CtgThMax(0.1);
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

    // track
    plots->track_eta_phi_pt = result->AddHist2D(
        "track_eta_phi_pt", "", "#eta", "#phi",
        400, -2, 2, 100, -M_PI, M_PI);
    plots->jet_eta_phi_pt = result->AddHist2D(
        "jet_eta_phi_pt", "", "#eta", "#phi",
        400, -2, 2, 100, -M_PI, M_PI);
  } // end if calculateTrackParameters


}

void calculateResolutions(TClonesArray *branchTruthTrack, TClonesArray *branchTrack, TestPlots *plots){

  GenParticle *particle, *truthParticle;
  Track *track, *truthTrack;

  // loop over all truth tracks
  for(Int_t j=0; j<branchTruthTrack->GetEntriesFast(); ++j){
    if(DEBUG) std::cout << "track j " << j << std::endl;
    truthTrack      = (Track*) branchTruthTrack->At(j);
    truthParticle   = (GenParticle*) truthTrack->Particle.GetObject(); 
    if(DEBUG) std::cout << "Extract particle info" << std::endl;

    if( fabs(truthTrack->Eta) > 2.0 ) continue; // remove tracks with |eta| > 2.0 
    if( truthTrack->PT < 1.0) continue;


    UInt_t truthParticleUID = 0;
    //if(truthParticle->GetName() != "GenParticle") continue;
    //if( !strncmp(truthParticle->GetName(), "GenParticle", 11)){
    //std::cout << "Warning: found particle of type '" << truthParticle->GetName() << "'" << std::endl;
    if(truthParticle == NULL){
        continue;
      }
    truthParticleUID = truthParticle->GetUniqueID(); 


    std::cout << "truthID: "  << truthParticleUID << std::endl; 


    // Loop over all tracks in event
    for(Int_t i=0; i<branchTrack->GetEntriesFast(); ++i)
    {
      if(DEBUG) std::cout << "track i: " << i << " out of " << branchTrack->GetEntriesFast() << std::endl; 
      track = (Track*) branchTrack->At(i);
      particle = (GenParticle*) track->Particle.GetObject(); 
      if(DEBUG) std::cout << "extracted track and particle" << std::endl;
      if(DEBUG) std::cout << "particleID: "  << particle->GetUniqueID() << std::endl;
      if(DEBUG) std::cout << "truthParticleID: "  << truthParticle->GetUniqueID() << std::endl;


      //if (i==0) std::cout << gen->fUniqueID << std::endl;
      //if(particle == truthParticle){
      if(particle->GetUniqueID() == truthParticle->GetUniqueID()){
        if(DEBUG) std::cout << "Matched track to particle" << std::endl;
        double z0Resolution = track->DZ - truthTrack->DZ; 
        double ptResolution = track->PT - truthTrack->PT;
        double d0Resolution = track->D0 - truthTrack->D0;
        double etaResolution = track->Eta - truthTrack->Eta;
        double CtgThetaResolution = track->CtgTheta - truthTrack->CtgTheta;
        double phiResolution = track->Phi - truthTrack->Phi;

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
        if(DEBUG) std::cout << "Filled resolution histograms" << std::endl;
      }
    }
  }
}

//------------------------------------------------------------------------------

void AnalyseEvents(ExRootTreeReader *treeReader, TestPlots *plots)
{

  // Define branches 
  TClonesArray *branchParticle       = treeReader->UseBranch("Particle");
  TClonesArray *branchTruthTrack     = treeReader->UseBranch("TruthTrack");
  TClonesArray *branchTrack          = treeReader->UseBranch("Track");
  //TClonesArray *branchPileupParticle = treeReader->UseBranch("PileupParticle");

  // Declare delphes physics objects 
  GenParticle *particle, *truthParticle;
  Track *track, *truthTrack;

  Long64_t allEntries = treeReader->GetEntries();
  cout << "** Chain contains " << allEntries << " events" << endl;

  // Loop over all events
  Long64_t entry;
  for(entry = 0; entry < allEntries; ++entry)
  {
    //if (entry>0)break;
    // Load selected branches with data from specified event
    treeReader->ReadEntry(entry);

    // print every 10% complete
    if( entry % 100==0 ) std::cout << "Event " << entry << " out of " << allEntries << std::endl;
    if(entry > 1) break;

    /////////////////////////////////////////
    // Calculate track parameter resolutions  
    /////////////////////////////////////////
    
    if(calculateTrackParameters){ // turn off if pileup is ON (too many tracks!) 
      calculateResolutions(branchTruthTrack, branchTrack, plots);
    }

    /////////////////////////////////////////
    // Create track jets  
    /////////////////////////////////////////

    // collect tracks
    std::vector<TLorentzVector> goodTracks;
    std::cout << "Number of tracks" << branchTrack->GetEntries() << std::endl;
    for(Int_t i=0; i<branchTrack->GetEntriesFast(); ++i)
    {
      if(DEBUG) std::cout << "about to get tracks" << std::endl; 
      track = (Track*) branchTrack->At(i);
      if(DEBUG) std::cout << "about to get particles" << std::endl; 
      particle = (GenParticle*) track->Particle.GetObject(); 
      if(DEBUG) std::cout << "Extracted tracks and particles"  << std::endl; 

      if( track->PT > 1 && fabs(track->Eta) < 2.0)
      {
      
        // It is impossible for the tracker to measure the pT if it's greater than 100 GeV
        auto trackPt = track->PT;
        if (trackPt > 100){
          trackPt = 100;
        }

        if(DEBUG) plots->track_eta_phi_pt->Fill(track->Eta, track->Phi, trackPt); 
        TLorentzVector vec;
        vec.SetPtEtaPhiM( trackPt, track->Eta, track->Phi, 0.14); // pion mass in GeV 
        goodTracks.push_back(vec);
        if(DEBUG) std::cout << "Filled track vector" << std::endl;
      }
    }

    if(DEBUG) std::cout << "n tracks " << goodTracks.size() << std::endl;


    // recluster tracks into jets 
    std::vector<TLorentzVector> trackJets;
    antiKt(goodTracks, trackJets); 

    if(DEBUG) std::cout << "Found " << trackJets.size() << " jets" << std::endl;

    if(DEBUG){
      for(auto jet : trackJets){
        plots->jet_eta_phi_pt->Fill(jet.Eta(), jet.Phi(), jet.Pt());
      }
    }

    for(auto jet : trackJets) plots->allJetPt->Fill(jet.Pt());
    plots->nJets->Fill(trackJets.size());

    // nth jet plots 
    for(int i=0; i<trackJets.size() && i<7; ++i){
      plots->jetNPt.at(i)->Fill( trackJets.at(i).Pt() );
      plots->jetNEta.at(i)->Fill( trackJets.at(i).Eta() );
      plots->jetNPhi.at(i)->Fill( trackJets.at(i).Phi() );
    }




  } // end loop over entries
} // end AnalyseEvents 



//------------------------------------------------------------------------------

void PrintHistograms(ExRootResult *result, TestPlots *plots)
{
  result->Print("pdf");
}


//------------------------------------------------------------------------------

void trackParameters(std::string inputFile, std::string outputFile)
{
  gSystem->Load("libDelphes");
  gROOT->SetBatch(1);

  TChain *chain = new TChain("Delphes");
  chain->Add(inputFile.c_str());

  ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
  ExRootResult *result = new ExRootResult();

  TestPlots *plots = new TestPlots;
  BookHistograms(result, plots);
  AnalyseEvents(treeReader, plots);
  PrintHistograms(result, plots);
  result->Write(outputFile.c_str());

  cout << "** Exiting..." << endl;

  delete plots;
  delete result;
  delete treeReader;
  delete chain;
}

//------------------------------------------------------------------------------
