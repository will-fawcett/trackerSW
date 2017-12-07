/*
Adapted from:
root -l examples/Example3.C'("delphes_output.root")'
This macro shows how to access the particle-level reference for reconstructed objects.
It is also shown how to loop over the jet constituents.

Re-tooled to make plots of track parameters 

*/


// Delphes classes
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootResult.h"
#include "modules/Delphes.h"
#include "classes/DelphesClasses.h"
#include "classes/DelphesFactory.h"
#include "modules/FastJetFinder.h"

// my classes

// c++ libs
#include <iostream>
#include <sstream>
#include <exception>

// stuff for ROOT
#include "TROOT.h"
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"
#include "TLegend.h"
#include "TPaveText.h"
#include "TClonesArray.h"

// fastjet (presumably the version inside Delphes)
#include "fastjet/PseudoJet.hh"
#include "fastjet/JetDefinition.hh"
#include "fastjet/ClusterSequence.hh"

using namespace fastjet;


std::string PrintTLorentz(TLorentzVector &v){
  std::ostringstream s;
  s <<  " (" << v.Pt() << ", " << v.Eta() << ", " << v.Phi() << ", " << v.M() << ")"; 
  return s.str();
}


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

inline float calculatDeltaPhi(float phi1, float phi2){
  return acos( cos( phi1 - phi2 ));
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
  TH1 *truthPt;
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

  TH1 *nAssociatedJets;
  std::vector<TH1*> associatedJetNPt;
  std::vector<TH1*> associatedJetNEta;
  std::vector<TH1*> associatedJetNPhi;

  TH1 *binnedZpT; 
  TH1 *binnedZnVertices; 


};

    


//------------------------------------------------------------------------------

void BookHistograms(ExRootResult *result, TestPlots *plots, bool calculateTrackParameters)
{

  //TLegend *legend;
  //TPaveText *comment;
  

  // jet histograms
  for(int i=0; i<7; ++i){
    plots->jetNPt.push_back(
        result->AddHist1D( ("jet"+std::to_string(i+1)+"Pt").c_str(), "", (std::to_string(i+1)+" Jet p_{T} [GeV]").c_str(), "",  1000, 0, 1000, 0, 0) 
        );
    plots->jetNEta.push_back(
        result->AddHist1D( ("jet"+std::to_string(i+1)+"Eta").c_str(), "", (std::to_string(i+1)+" Jet #eta").c_str(), "",  100, -2.5, 2.5) 
        );
    plots->jetNPhi.push_back(
        result->AddHist1D( ("jet"+std::to_string(i+1)+"Phi").c_str(), "", (std::to_string(i+1)+" Jet #phi").c_str(), "",  100, -M_PI, M_PI) 
        );
    // Jets associated to PV
    plots->associatedJetNPt.push_back(
        result->AddHist1D( ("associatedJet"+std::to_string(i+1)+"Pt").c_str(), "", (std::to_string(i+1)+" Jet p_{T} [GeV]").c_str(), "",  1000, 0, 1000, 0, 0) 
        );
    plots->associatedJetNEta.push_back(
        result->AddHist1D( ("associatedJet"+std::to_string(i+1)+"Eta").c_str(), "", (std::to_string(i+1)+" Jet #eta").c_str(), "",  100, -2.5, 2.5) 
        );
    plots->associatedJetNPhi.push_back(
        result->AddHist1D( ("associatedJet"+std::to_string(i+1)+"Phi").c_str(), "", (std::to_string(i+1)+" Jet #phi").c_str(), "",  100, -M_PI, M_PI) 
        );

  }
  plots->nJets = result->AddHist1D( "nJets", "nJets", "Number of Jets", "", 100, 0, 100, 0, 0 );
  plots->nAssociatedJets = result->AddHist1D( "nAssociatedJets", "nAssociatedJets", "Number of Jets", "", 100, 0, 100, 0, 0 );
  plots->allJetPt = result->AddHist1D("allJetPt", "", "Jet p_{T} (all jets) [GeV]", "", 100, 0, 1000);

  // z pt
  plots->binnedZpT = result->AddHist1D( "binnedZpT", "", "z position [mm]", "Sum(p_{T}) [GeV]", 600, -300, 300);

  // Plots only used if track parameters are calculated 
  if(calculateTrackParameters){

    // Basic kinematics
    // pt
    plots->pt = result->AddHist1D(
        "pt", "pt", "Track p_{T} [GeV]", "Number of Tracks",
        1000, 0, 2000, 0, 1);
    plots->truthPt = result->AddHist1D(
        "truthPt", "pt", "Truth Track p_{T} [GeV]", "Number of Tracks",
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

void calculateResolutions(TClonesArray *branchTruthTrack, TClonesArray *branchTrack, TestPlots *plots, bool DEBUG){

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

    // Check is the truth track is from pileup
    if(truthParticle == NULL) continue; 

    // Extract the UID of the particle
    UInt_t truthParticleUID = truthParticle->GetUniqueID();

    // Loop over all tracks in event
    for(Int_t i=0; i<branchTrack->GetEntriesFast(); ++i)
    {
      if(DEBUG) std::cout << "track i: " << i << " out of " << branchTrack->GetEntriesFast() << std::endl; 
      track = (Track*) branchTrack->At(i);
      particle = (GenParticle*) track->Particle.GetObject(); 
      if(DEBUG) std::cout << "extracted track and particle" << std::endl;

      // Check is the reco track is from pileup
      if(particle == NULL) continue;

      UInt_t particleUID = particle->GetUniqueID();

      if(DEBUG) std::cout << "truthParticleID: "  << truthParticle->GetUniqueID() << std::endl;
      if(DEBUG) std::cout << "particleID: "  << particle->GetUniqueID() << std::endl;

      // Match the track with the corresponding truth track 
      if(truthParticleUID == particleUID){
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
        plots->truthPt->Fill(truthTrack->PT);
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
} // end of calculate resolutions

//------------------------------------------------------------------------------

void AnalyseEvents(ExRootTreeReader *treeReader, TestPlots *plots, bool DEBUG, bool calculateTrackParameters)
{


  // Define branches 
  TClonesArray *branchParticle   = treeReader->UseBranch("Particle");
  TClonesArray *branchTruthTrack = treeReader->UseBranch("TruthTrack");
  TClonesArray *branchTrack      = treeReader->UseBranch("Track");
  TClonesArray *branchTrackJet   = treeReader->UseBranch("TrackJet");
  TClonesArray *branchVertex     = treeReader->UseBranch("Vertex");
  //TClonesArray *branchPileupParticle = treeReader->UseBranch("PileupParticle");

  // Setup FastJet
  JetDefinition *definition = 0;
  definition = new JetDefinition(antikt_algorithm, 0.4);


  // Loop over all events
  Long64_t allEntries = treeReader->GetEntries();
  int nEventsCorrectlyIdentifiedVertex(0);
  std::cout << "** Chain contains " << allEntries << " events" << std::endl;
  for(Long64_t entry = 0; entry < allEntries; ++entry)
  {
    // Load selected branches with data from specified event
    treeReader->ReadEntry(entry);

    // print every 10% complete
    if( entry % 100==0 ) std::cout << "Event " << entry << " out of " << allEntries << std::endl;

    /////////////////////////////////////////
    // Calculate track parameter resolutions  
    /////////////////////////////////////////
    
    if(calculateTrackParameters){ // turn off if pileup is ON (too many tracks!) 
      calculateResolutions(branchTruthTrack, branchTrack, plots, DEBUG);
    }


    // Fill plots with track jet properties
    int nJets = branchTrackJet->GetEntriesFast();
    plots->nJets->Fill( nJets ); 
    for(int i=0; i<nJets && i<7; ++i){
      Jet * jet = (Jet*) branchTrackJet->At(i);
      plots->jetNPt.at(i)->Fill( jet->PT );
      plots->jetNEta.at(i)->Fill( jet->Eta );
      plots->jetNPhi.at(i)->Fill( jet->Phi );
    }

    ///////////////////////////////////
    // loop over all reco tracks, and find the "primary bin"
    //////////////////////////////////

    // let bin width be 1 mm ?
    TH1F * eventBinnedZpT = new TH1F("eventBinnedZpT", "", 600, -300, 300); // for 5mm use 120 bins 
    for(auto itTrack = branchTrack->begin(); itTrack != branchTrack->end(); ++itTrack){
      float trackPt = static_cast<Track*>(*itTrack)->PT;
      float zPosition = static_cast<Track*>(*itTrack)->DZ;
      plots->binnedZpT->Fill(zPosition, trackPt);
      eventBinnedZpT->Fill(zPosition, trackPt); 
    } // end iteration over tracks 

    // get bin with largest sum(pT) 
    Int_t binWithPtMax = eventBinnedZpT->GetMaximumBin();

    // get z range of bin with largest sum(pT)
    TAxis * xaxis = static_cast<TAxis*>(eventBinnedZpT->GetXaxis());
    float zMin = xaxis->GetBinLowEdge(binWithPtMax);
    float zMax = xaxis->GetBinUpEdge(binWithPtMax);
    float zWidth = xaxis->GetBinWidth(binWithPtMax);
    delete eventBinnedZpT;


    ///////////////////////////////////
    // Find the location of the real PV
    ///////////////////////////////////
    float vertexZ(0.0); 
    for(int i=0; i<branchVertex->GetEntriesFast(); ++i){
      Vertex * vertex = (Vertex*) branchVertex->At(i);
      if(vertex->IsPU) continue;
      else{
        vertexZ = vertex->Z;
        //std::cout << "Event: " << entry << " vertex z: " << vertexZ << std::endl;
      }
    }
    
    // Check to see that real PV is in the PB
    if(vertexZ > zMin && vertexZ < zMax){
      nEventsCorrectlyIdentifiedVertex++;
      //std::cout << "Vertex is inside PB" << std::endl; 
      //std::cout << "vertex z: " << vertexZ << " PB range: [" << zMin << ", " << zMax << "]" << std::endl;
    }
    else{
      //std::cout << "Vertex isn't inside PB" << std::endl;
      //std::cout << "vertex z: " << vertexZ << " PB range: [" << zMin << ", " << zMax << "]" << std::endl;
    }
    
    ///////////////////////////////////
    // Select tracks which belong to the PB
    ///////////////////////////////////
    std::vector<Track*> tracksAssociatedToPB;
    std::vector<TLorentzVector> vectorsAssociatedToPB;
    for(auto itTrack = branchTrack->begin(); itTrack != branchTrack->end(); ++itTrack){
      float zPosition = static_cast<Track*>(*itTrack)->DZ;
      if(zPosition > zMin && zPosition < zMax){
        tracksAssociatedToPB.push_back( static_cast<Track*>(*itTrack) );
        vectorsAssociatedToPB.push_back( static_cast<Track*>(*itTrack)->P4());
      }
    }

    // Use FastJetFinder inside delphes to cluster jets 
    std::vector<PseudoJet> inputList, outputList;
    for(auto track : tracksAssociatedToPB){
      TLorentzVector momentum = track->P4();
      PseudoJet jet = PseudoJet(momentum.Px(), momentum.Py(), momentum.Pz(), momentum.E());
      inputList.push_back(jet);
    }
    // run clustering 
    ClusterSequence sequence(inputList, *definition);
    outputList.clear();
    outputList = sorted_by_pt(sequence.inclusive_jets(0.0));

    // plots for associated jets
    for(int i=0; i<outputList.size() && i<7; ++i){
      plots->associatedJetNPt.at(i)->Fill( outputList.at(i).pt() );
      plots->associatedJetNEta.at(i)->Fill( outputList.at(i).eta() );
      plots->associatedJetNPhi.at(i)->Fill( outputList.at(i).phi() );
    }
    plots->nAssociatedJets->Fill( outputList.size() );





    /*********************
    ///////////////////////////////////
    // Loop over all jets and find which tracks are associated to the PB 
    // WJF: idea was to find the jets with tracks that came from the PB
    // This was almost all jets, as there is no "directional" information"
    ///////////////////////////////////

    std::vector<Jet*> jetsFromPV;
    std::vector<std::pair<int, int>> jetsFromPVProperties ; 
    // Loop over jets (or tracks), select tracks with dz inside the window with the largets pT
    for(int i = 0; i < branchTrackJet->GetEntriesFast(); ++i){
      jet = (Jet*) branchTrackJet->At(i);
      int nConstituents = jet->Constituents.GetEntriesFast();
      int nConstituentsInPV(0);

      for(int j = 0; j < nConstituents; ++j){

        TLorentzVector momentum;
        momentum.SetPtEtaPhiM(0.0, 0.0, 0.0, 0.0);
        TObject *object = jet->Constituents.At(j);

        if(object == 0) continue; // Check if the constituent is accessible
        if(object->IsA() == Track::Class()){
          track = (Track*) object;
          if(track->DZ > zMin && track->DZ < zMax){
            nConstituentsInPV++;
          }
          //std::cout << "    Track pt: " << track->PT << ", eta: " << track->Eta << ", phi: " << track->Phi << std::endl;
        }
        else{
          // add exception handling if this ever happens?
          std::cerr << "Unidentified object in jet collection (not a track): " << object->GetName() << std::endl;
        }
      }
      if(nConstituentsInPV > 0){
        jetsFromPV.push_back( jet );
        jetsFromPVProperties.push_back( std::make_pair(nConstituents, nConstituentsInPV));
      }
    } // end of loop over jets
    // Loop over jets that are associated to the PV
    plots->nAssociatedJets->Fill(jetsFromPV.size() );
    for(int i=0; i<jetsFromPV.size() && i<7; ++i){
      //std::cout << "jet with " << jetsFromPVProperties.at(i).first << " constituents, and " << jetsFromPVProperties.at(i).second << " associated to PV. Fraction: " << static_cast<float>(jetsFromPVProperties.at(i).second)/static_cast<float>(jetsFromPVProperties.at(i).first) << std::endl;
      plots->associatedJetNPt.at(i)->Fill(jetsFromPV.at(i)->PT);
      
    }
    *******************************/


  } // end loop over entries

  std::cout << "Of " << allEntries << " events, " << nEventsCorrectlyIdentifiedVertex << " had the vertex correctly identified, i.e. " << static_cast<float>(nEventsCorrectlyIdentifiedVertex)/static_cast<float>(allEntries) << " of events."  << std::endl;
} // end AnalyseEvents 



//------------------------------------------------------------------------------

void PrintHistograms(ExRootResult *result, TestPlots *plots)
{
  result->Print("pdf");
}


//------------------------------------------------------------------------------



//------------------------------------------------------------------------------

int main(int argc, char *argv[])
{

  gROOT->SetBatch(1);
  bool DEBUG = false;
  bool calculateTrackParameters = true; 
  //bool calculateTrackParameters = false; 

  std::string appName = "trackParameters";
  std::string inputFile = argv[1]; // doesn't complain about cast? Maybe compiler can deal with it :p 
  std::string outputFile = argv[2];

  if(argc < 3)
  {
    std::cout << " Usage: " << appName << " input_file" << " output_file" << std::endl;
    std::cout << " config_file - configuration file in Tcl format,"       << std::endl;
    std::cout << " output_file - output file in ROOT format,"             << std::endl;
    std::cout << " input_file(s) - input file(s) in STDHEP format,"       << std::endl;
    std::cout << " with no input_file, or when input_file is -, read standard input." << std::endl;
    return 1;
  }

  // control analysis 
  TChain *chain = new TChain("Delphes");
  std::cout << "Adding " << inputFile << " to chain" << std::endl;
  chain->Add(inputFile.c_str());

  ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
  ExRootResult *result = new ExRootResult();

  TestPlots *plots = new TestPlots;
  BookHistograms(result, plots, calculateTrackParameters);
  AnalyseEvents(treeReader, plots, DEBUG, calculateTrackParameters);
  PrintHistograms(result, plots);

  std::cout << "Writing to file: " << outputFile << std::endl;
  result->Write(outputFile.c_str());

  std::cout << "** Exiting..." << std::endl;

  delete plots;
  delete result;
  delete treeReader;
  delete chain;

  return 0;
}

    /////////////////////////////////////////
    // Manually create track jets  
    /////////////////////////////////////////

    /*******************************8
    std::cout << "Number of tracks: " << branchTrack->GetEntriesFast() << std::endl; 
    std::vector<TLorentzVector> goodTracks;
    for(Int_t i=0; i<branchTrack->GetEntriesFast(); ++i)
    {
      track = (Track*) branchTrack->At(i);
      particle = (GenParticle*) track->Particle.GetObject(); 

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
    for(unsigned int i=0; i<trackJets.size() && i<7; ++i){
      plots->jetNPt.at(i)->Fill( trackJets.at(i).Pt() );
      plots->jetNEta.at(i)->Fill( trackJets.at(i).Eta() );
      plots->jetNPhi.at(i)->Fill( trackJets.at(i).Phi() );
    }
    ******************/
