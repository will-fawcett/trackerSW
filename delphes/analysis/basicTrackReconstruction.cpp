//#include "modules/TestClass.h"
//#include "modules/ClusteredJet.h"

// Delphes classes
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/ExRootAnalysis/ExRootResult.h"
#include "modules/Delphes.h"
#include "classes/DelphesClasses.h"
#include "classes/DelphesFactory.h"
#include "modules/FastJetFinder.h"

// my analysis classes
#include "classes/TrackFitter.h"

// c++ libs
#include <iostream>
#include <sstream>
#include <exception>
#include <map>

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

// attempt with eigen
//#include <Eigen/Core>
//#include "tricktrack/RiemannFit.h"
//

#include <ctime>


void printTime(clock_t begin, clock_t end, std::string message){
  std::cout << message << ": time elapsed: " << double(end - begin) / CLOCKS_PER_SEC << std::endl;
}

struct trackStruct
{
  Float_t pT;
  Float_t d0;
  Float_t z0;
  Float_t eta;
  Float_t phi;
  Float_t kappa_013;
  Float_t kappa_123;
  Int_t isFake; 
};

//------------------------------------------------------------------------------

struct TestPlots
{


  // Number of true tracks
  TH1* nDelphesTracks;
  TH1* nDelphesTracks1GeV;
  TH1* nDelphesTracks10GeV;
  std::vector<TH1*> nDelphesHits; 
  std::vector<TH1*> nDelphesHitsPt2; 
  
  // number of reconstructed tracks
  std::vector<TH1*> nRecoTracks; 
  std::vector<TH1*> nRecoTracksPt2; 
  std::vector<TH1*> nRecoTracksMatched;
  std::vector<TH1*> nRecoTracksMatchedPt2;
  TH1* fractionOfFakeTracks;

  TH1* trueParticlePt_numParticles;
  TH1* trueParticlePt_numRecoTracks;


  // Fake rate as a function of pT, eta
  std::vector<TH1*> recoTrackPt;
  std::vector<TH1*> recoTrackEta;

  std::vector<TH1*> recoTrackPt_fake;
  std::vector<TH1*> recoTrackEta_fake; 

  std::vector<TH1*> recoTrackPt_true;
  std::vector<TH1*> recoTrackEta_true; 

  std::vector<TH1*> recoTrackHitPt_true;
  std::vector<TH1*> recoTrackHitEta_true;
  std::vector<TH1*> recoTrackHitEtaPt2_true;
  
  std::vector<TH1*> nHitsPt; 
  std::vector<TH1*> nHitsEta;  
  std::vector<TH1*> nHitsEtaPt2;  
  std::vector<TH1*> recoTrackPtResolution;

  // Simple histogram of curvature difference 
  TH1* curvatureDifference_true;
  TH1* curvatureDifference_fake;

  TGraph* curvatureDifference_curvature_true;
  TGraph* curvatureDifference_curvature_fake;



};

//------------------------------------------------------------------------------

void BookHistograms(ExRootResult *result, TestPlots *plots)
{

  int hitMultiplicity = 12000;
  int hitMultiplicityBins = hitMultiplicity/10; 

  for(int i=0; i<5; ++i ){
    std::string trackerID = std::to_string((i+1)*10);

    plots->nDelphesHits.push_back(
        result->AddHist1D("nDelphesHits_"+trackerID, "Number of hits in outermost layer", "", "", hitMultiplicityBins, 0, hitMultiplicity,0,0)
        );
    plots->nDelphesHitsPt2.push_back(
        result->AddHist1D("nDelphesHitsPt2_"+trackerID, "Number of hits in outermost layer with pT>2", "", "", hitMultiplicityBins, 0, hitMultiplicity,0,0)
        );
    plots->nRecoTracks.push_back(
        result->AddHist1D("nRecoTracks_"+trackerID, "Tracks+fakes", "Number of tracks", "Number of events", hitMultiplicityBins, 0, hitMultiplicity,0,0)
        );
    plots->nRecoTracksMatched.push_back(
        result->AddHist1D("nRecoTracksMatched_"+trackerID, "Matched tracks", "Number of tracks", "Number of events", hitMultiplicityBins, 0, hitMultiplicity,0,0)
        );
    plots->nRecoTracksPt2.push_back(
        result->AddHist1D("nRecoTracksPt2_"+trackerID, "Tracks+fakes", "Number of tracks pT>2", "Number of events", hitMultiplicityBins, 0, hitMultiplicity,0,0)
        );
    plots->nRecoTracksMatchedPt2.push_back(
        result->AddHist1D("nRecoTracksMatchedPt2_"+trackerID, "Matched tracks pT>2GeV", "Number of tracks", "Number of events", hitMultiplicityBins, 0, hitMultiplicity,0,0)
        );

    int nBinsPt = 1000;
    int pTMax = 500;
    plots->recoTrackPt.push_back(
        result->AddHist1D("recoTrackPt_"+trackerID, "Reco track pT", "", "", nBinsPt, 0, pTMax, 0, 0)
        );
    plots->recoTrackPt_fake.push_back(
        result->AddHist1D("recoTrackPt_fake_"+trackerID, "Fake Reco track pT", "", "", nBinsPt, 0, pTMax, 0, 0)
        );
    plots->recoTrackPt_true.push_back(
        result->AddHist1D("recoTrackPt_true_"+trackerID, "True Reco track pT", "", "", nBinsPt, 0, pTMax, 0, 0)
        );
    plots->recoTrackHitPt_true.push_back(
        result->AddHist1D("recoTrackHitPt_true_"+trackerID, "True Reco track, pT of hit", "", "", nBinsPt, 0, pTMax, 0, 0)
        );
    plots->recoTrackHitEta_true.push_back(
        result->AddHist1D("recoTrackHitEta_true_"+trackerID, "True Reco track, Eta of hit", "", "", 100, -5, 5, 0, 0)
        );
    plots->recoTrackHitEtaPt2_true.push_back(
        result->AddHist1D("recoTrackHitEtaPt2_true_"+trackerID, "True Reco track, Eta of hit, hit pT > 2 GeV", "", "", 100, -5, 5, 0, 0)
        );
    plots->nHitsPt.push_back(
        result->AddHist1D("nHitsPt_"+trackerID, "Hit Pt", "", "", nBinsPt, 0, pTMax, 0, 0)
        );
    plots->nHitsEta.push_back(
        result->AddHist1D("nHitsEta_"+trackerID, "Hit Eta", "", "", 100, -5, 5, 0, 0)
        );
    plots->nHitsEtaPt2.push_back(
        result->AddHist1D("nHitsEtaPt2_"+trackerID, "Hit Eta, hit pT > 2 GeV", "", "", 100, -5, 5, 0, 0)
        );

    plots->recoTrackEta.push_back(
        result->AddHist1D("recoTrackEta_"+trackerID, "Reco track eta", "", "", 100, -5, 5, 0, 0)
        );
    plots->recoTrackEta_fake.push_back(
        result->AddHist1D("recoTrackEta_fake_"+trackerID, "Fake Reco track eta", "", "", 100, -5, 5, 0, 0)
        );
    plots->recoTrackEta_true.push_back(
        result->AddHist1D("recoTrackEta_true_"+trackerID, "true Reco track eta", "", "", 100, -5, 5, 0, 0)
        );

    plots->recoTrackPtResolution.push_back(
        result->AddHist1D("recoTrackPtResolution_"+trackerID, "Reconstructed track pT resolution", "", "", 400, -10, 10, 0, 0)
        );

  }

  plots->nDelphesTracks = result->AddHist1D("nDelphesTracks", "TrueTracks", "Number of tracks", "Number of events", hitMultiplicityBins, 0, hitMultiplicity,0,0);
  plots->nDelphesTracks1GeV = result->AddHist1D("nDelphesTracks1GeV", "TrueTracks > 1 GeV", "Number of tracks", "Number of events", hitMultiplicityBins, 0, hitMultiplicity,0,0);
  plots->nDelphesTracks10GeV = result->AddHist1D("nDelphesTracks10GeV", "TrueTracks > 10 GeV", "Number of tracks", "Number of events", hitMultiplicityBins, 0, hitMultiplicity,0,0);

  plots->curvatureDifference_true = result->AddHist1D("curvatureDifference_true", "", "Curvature difference", "Number of tracks", 100, -0.1, 0.1, 0, 0);
  plots->curvatureDifference_fake = result->AddHist1D("curvatureDifference_fake", "", "Curvature difference", "Number of tracks", 100, -0.1, 0.1, 0, 0);

  //plots->curvatureDifference_curvature_true = new TGraph();
  plots->curvatureDifference_curvature_true = result->AddTGraph("curvatureDifference_curvature_true");
  plots->curvatureDifference_curvature_fake = result->AddTGraph("curvatureDifference_curvature_fake");


  plots->fractionOfFakeTracks = result->AddHist1D("fractionOfFakeTracks", "", "", "", 100, 0, 1, 0, 0);

  plots->trueParticlePt_numParticles = result->AddHist1D("trueParticlePt_numParticles", "", "", "", 100, 0, 100, 0, 0);
  plots->trueParticlePt_numRecoTracks = result->AddHist1D("trueParticlePt_numRecoTracks", "", "", "", 100, 0, 100, 0, 0);

}

//------------------------------------------------------------------------------

// using hitContainer = std::map<int, std::vector<Hit*> >; 
hitContainer fillHitContainer(TClonesArray* hitBranch){
  // Fill a  hitContainer object with the hits form a particular branch

    hitContainer hc; 
    for(auto itHit = hitBranch->begin(); itHit != hitBranch->end(); ++itHit){
      Hit * hit = dynamic_cast<Hit*>(*itHit);
      int SurfaceID = hit->SurfaceID; 
      hc[SurfaceID].push_back(hit); 
    }
    return hc;
}

//------------------------------------------------------------------------------

int countFakes(std::vector<myTrack>& theTracks){

    // count number of fake tracks 
    int nFakes(0);
    for(const auto& track : theTracks){
      if(track.isFake()) nFakes++;
    }
    return nFakes;
}

//------------------------------------------------------------------------------

void AnalyseEvents(const int nEvents, ExRootTreeReader *treeReader, TestPlots *plots, float vertexDistSigma, int nVertexSigma, TTree* tree)
{

  // Define branches
  TClonesArray *branchParticle   = treeReader->UseBranch("Particle");
  //TClonesArray *branchTruthTrack = treeReader->UseBranch("TruthTrack");
  TClonesArray *branchTrack      = treeReader->UseBranch("Track");

  // Different hit branches, corresponding to the different geometry 
  TClonesArray *branchHit50        = treeReader->UseBranch("Hits50");
  TClonesArray *branchHit40        = treeReader->UseBranch("Hits40");
  TClonesArray *branchHit30        = treeReader->UseBranch("Hits30");
  TClonesArray *branchHit20        = treeReader->UseBranch("Hits20");
  TClonesArray *branchHit10        = treeReader->UseBranch("Hits10");

  // Declare track structs 
  trackStruct tracks50;
  trackStruct tracks40;
  trackStruct tracks30;
  trackStruct tracks20;
  trackStruct tracks10;

  // Create the branches
  TBranch* branchTrack50 = tree->Branch("tracks50", &tracks50, "pT/F:d0/F:z0/F:eta/F:phi/F:kappa_013/F:kappa_123/F:isFake/I");
  TBranch* branchTrack40 = tree->Branch("tracks40", &tracks40, "pT/F:d0/F:z0/F:eta/F:phi/F:kappa_013/F:kappa_123/F:isFake/I");
  TBranch* branchTrack30 = tree->Branch("tracks30", &tracks30, "pT/F:d0/F:z0/F:eta/F:phi/F:kappa_013/F:kappa_123/F:isFake/I");
  TBranch* branchTrack20 = tree->Branch("tracks20", &tracks20, "pT/F:d0/F:z0/F:eta/F:phi/F:kappa_013/F:kappa_123/F:isFake/I");
  TBranch* branchTrack10 = tree->Branch("tracks10", &tracks10, "pT/F:d0/F:z0/F:eta/F:phi/F:kappa_013/F:kappa_123/F:isFake/I");


  // based on the spread of vertices, calculate the maximum tolerance along the beam line to which a track can point
  float maxZ = nVertexSigma*vertexDistSigma;
  float minZ = -1*maxZ; 
  std::vector<float> parameters;
  parameters.push_back(minZ);
  parameters.push_back(maxZ);

  // Loop over all events
  Long64_t allEntries = treeReader->GetEntries();
  int nEventsCorrectlyIdentifiedVertex(0);
  std::cout << "** Chain contains " << allEntries << " events" << std::endl;
  // an event weight for normalising histograms
  std::vector<int> layerIDs;
  float eventWeight = 1.0/allEntries; 
  for(Long64_t entry = 0; entry < allEntries; ++entry)
  {

    // limit number of events looped over
    if(nEvents != -1){
      if(entry > nEvents-1) break; // -1 because humans will count from 1 event
    }
    // Load selected branches with data from specified event
    treeReader->ReadEntry(entry);
    // print every 10% complete
    if( entry % int(allEntries/10)==0 ) std::cout << "Event " << entry << " out of " << allEntries << std::endl;
    if( entry % 100==0 ) std::cout << "Event " << entry << " out of " << allEntries << std::endl;



    //////////////////////////////////////////
    // Count the number of tracks from Delphes
    //////////////////////////////////////////
    
    int nTracks(0);
    int nTracks1GeV(0);
    int nTracks10GeV(0);
    for(auto itTrack=branchTrack->begin(); itTrack != branchTrack->end(); ++itTrack){
      Track* track = dynamic_cast<Track*>(*itTrack);
      nTracks++;
      if(track->PT < 1.0) continue;
      nTracks1GeV++;
      if(track->PT < 10) continue;
      nTracks10GeV++;
    }
    plots->nDelphesTracks->Fill(nTracks, eventWeight);
    plots->nDelphesTracks1GeV->Fill(nTracks1GeV, eventWeight);
    plots->nDelphesTracks10GeV->Fill(nTracks10GeV, eventWeight);

    
    // Fill the hitContainer with all the hits in the event (geometry defined by the surfaces) 
    //clock_t begin_fillHitContainer = clock();
    hitContainer hc50 = fillHitContainer(branchHit50); 
    //clock_t end_fillHitContainer = clock();
    //printTime(begin_fillHitContainer, end_fillHitContainer, "Fill hit container");
    hitContainer hc40 = fillHitContainer(branchHit40); 
    hitContainer hc30 = fillHitContainer(branchHit30); 
    hitContainer hc20 = fillHitContainer(branchHit20); 
    hitContainer hc10 = fillHitContainer(branchHit10); 


    // get list of unique layer IDs (only need filling once)
    if(entry == 0){
      for(auto const& key : hc50){
        layerIDs.push_back(key.first);
      }
      std::sort(layerIDs.begin(), layerIDs.end()); // layers should be ascengin 
      std::cout << "Sorted Layer IDs: " << std::endl;
      for(auto l : layerIDs) std::cout << "\t" << l << std::endl;
    }


    // contains the rules to associate hits together, and then the collection of hits into tracks 
    //tf.debug();
    
    std::vector<hitContainer> theHitContainers = {hc10, hc20, hc30, hc40, hc50};
    int counter(0);
    for(auto& hc : theHitContainers){

      // fill histogram with the pT of hits in the outermost layer
      int nHitsPt2(0);
      for(auto& hit : hc[ layerIDs.back() ]){
        plots->nHitsPt.at(counter)->Fill(hit->PT);
        plots->nHitsEta.at(counter)->Fill(hit->Eta);
        if(hit->PT > 2.0){
          nHitsPt2++;
          plots->nHitsEtaPt2.at(counter)->Fill(hit->Eta);
        }
      }

      // number of hits with pT > 2 GeV
      plots->nDelphesHitsPt2.at(counter)->Fill(nHitsPt2); 

      TrackFitter tf(fitTypes::simpleLinear, parameters, layerIDs); 
      bool associated = tf.AssociateHits(hc);

      if(associated){
        /**********
        std::vector< myTrack > baseTracks = tf.GetTracks();
        std::cout << "Number of base tracks: " << baseTracks.size() << std::endl;
        int nBaseFakes = countFakes(baseTracks);
        std::cout << "\tOf which " << nBaseFakes << " are fake." << std::endl;
        ***********/

        std::vector< myTrack > tracksNoCurvature = tf.GetTracks();
        if(counter==0){
          for(const myTrack& track : tracksNoCurvature){
            tracks10.pT = track.Pt();
            tracks10.d0 = track.D0();
            tracks10.z0 = track.Z0();
            tracks10.eta = track.Eta();
            tracks10.phi = track.Phi();
            tracks10.kappa_013 = track.kappa_bc();
            tracks10.kappa_123 = track.kappa_nbc();
            tracks10.isFake = track.isFake(); 
            tree->Fill();
          }

        }

        //tf.ApplyCurvatureCut( 0.01 ); // reject tracks with curvature difference greater than this number [mm^-1]
        tf.ApplyCurvatureCut( 0.005 ); // reject tracks with curvature difference greater than this number [mm^-1]

        std::vector< myTrack > theTracks = tf.GetTracks(); 
        int nFakes = countFakes(theTracks);

        /***************
        std::cout << "Number of tacks after cut: " << theTracks.size() << std::endl;
        std::cout << "\tOf which " << nFakes << " are fake." << std::endl;
        std::cout << "Removed " << baseTracks.size()-theTracks.size() << " tracks" << std::endl;
        std::cout << "Removed " << nBaseFakes - nFakes << " fakes" << std::endl;
        std::cout << "" << std::endl;
        ********************/

        std::vector<Hit*> outerHits = hc[2];
        plots->nDelphesHits.at(counter)->Fill( outerHits.size(), eventWeight); // number of hits in outer layer
        plots->nRecoTracks.at(counter)->Fill(theTracks.size(), eventWeight);
        plots->nRecoTracksMatched.at(counter)->Fill(theTracks.size() - nFakes, eventWeight);

        int nTracksPt2(0);
        int nMatchedTracksPt2(0);

        // loop over tracks to fill fake rate plots
        for(const auto& track : theTracks){

          //track.printHitInfo();

          plots->recoTrackPt.at(counter)->Fill(track.Pt());
          plots->recoTrackEta.at(counter)->Fill(track.Eta()); // might want to check theta calculation
          //if(track.Pt()>2) nTracksPt2++;
          float outerHitPt = track.GetHitPtAtLayer(2);
          float outerHitEta = track.GetHitAtLayer(2)->Eta; 
          if(outerHitPt > 2) nTracksPt2++;

          float curvatureDifference =  track.kappa_bc() - track.kappa_nbc();
          if(track.isFake()){
            // FAKE tracks 
            plots->recoTrackPt_fake.at(counter)->Fill(track.Pt());
            plots->recoTrackEta_fake.at(counter)->Fill(track.Eta()); 
            if(counter == 1){
              plots->curvatureDifference_fake->Fill(curvatureDifference); 
              static int fakePointCounter = 0;
              plots->curvatureDifference_curvature_fake->SetPoint(fakePointCounter,curvatureDifference , track.kappa_bc());
              //std::cout << "fakePointCounter: " << fakePointCounter << std::endl;
              fakePointCounter++;
            }
          }
          else{
            // TRUE tracks 
            plots->recoTrackPtResolution.at(counter)->Fill(track.Pt() - outerHitPt); 
            plots->recoTrackPt_true.at(counter)->Fill(track.Pt());
            plots->recoTrackHitPt_true.at(counter)->Fill(outerHitPt);
            plots->recoTrackHitEta_true.at(counter)->Fill(outerHitEta);
            plots->recoTrackEta_true.at(counter)->Fill(track.Eta()); 
            //if(track.Pt()>2) nMatchedTracksPt2++;
            if(track.GetHitPtAtLayer(2) > 2){
              nMatchedTracksPt2++; 
              plots->recoTrackHitEtaPt2_true.at(counter)->Fill(outerHitEta);
            }

            if(counter == 1){
              plots->curvatureDifference_true->Fill(curvatureDifference); 
              static int truePointCounter = 0;
              plots->curvatureDifference_curvature_true->SetPoint(truePointCounter, curvatureDifference, track.kappa_bc());
              truePointCounter++;
            }
          }
        }
        plots->nRecoTracksPt2.at(counter)->Fill(nTracksPt2);
        plots->nRecoTracksMatchedPt2.at(counter)->Fill(nMatchedTracksPt2);

      }
      //std::cout << "i: " << counter << std::endl;
      ++counter;
    }



    /***************
    // count how many of the reconstructed tracks are not fakes
    int numRealTracks(0);
    for(const auto& track : theTracks){
      if(track.isNotFake()) numRealTracks++;
    }
    int numFakeTracks = theTracks.size() - numRealTracks;
    if(!(theTracks.size() == 0)){
      float f_fractionOfFakeTracks = numFakeTracks/theTracks.size();
      //plots->fractionOfFakeTracks->Fill(f_fractionOfFakeTracks);
    }
    //std::cout << "There are " << numFakeTracks << " fakes out of " << theTracks.size() << " reco tracks, from a possible " << hc[0].size() << " hits in the inner layer" << std::endl;
    //std::cout << "event has: " << theTracks.size() << " reconstructed tracks" << std::endl;
    //plots->nRecoTracks->Fill(theTracks.size(), eventWeight);
    **************/

    //////////////////////////////////////////
    // have another quick go at finding tracks
    // Simplest possible algorithm 
    //////////////////////////////////////////

    //plots->nDelphesHits->Fill(hc[2].size(), eventWeight);
    
    /****************************
    int nNewMatchedTracks(0);
    int nNewMatchedTracksNotFake(0);
    std::vector<myTrack> newMatchedTracks;
    for(auto innerHit : hc[0]){
      float rInner = 532.0; //innerHit.Perp();
      float rOuter = 632.0; //outerHit->Perp();
      float zInner = innerHit->Z;
      float phiInner = innerHit->Phi();
      GenParticle * particleInner = dynamic_cast<GenParticle*>(innerHit->Particle.GetObject());


      for(auto outerHit : hc[2]){

        plots->trueParticlePt_numParticles->Fill( outerHit->PT, eventWeight );
        

        // must be in same hemesphere 
        float deltaPhi = acos(cos( phiInner - outerHit->Phi() )); 
        if(fabs(deltaPhi) > M_PI) continue; 

        // calculate line parameters 
        float zOuter = outerHit->Z;
        lineParameters params = calculateLineParameters(zInner, rInner, zOuter, rOuter);

        // recect if not within 3 sigma of the luminous region
        float beamlineIntersect = (0 - params.intercept)/params.gradient;
        if(fabs(beamlineIntersect) > maxZ) continue;

        float intersect = (582.0 - params.intercept)/params.gradient;

        for(auto intermediateHit : hc[1]){
          float zInter = intermediateHit->Z;
          // 
          if(fabs( zInter - intersect) < 1.0){

            // match
            std::vector<Hit*> matchedHits;
            matchedHits.push_back(innerHit);
            matchedHits.push_back(intermediateHit);
            matchedHits.push_back(outerHit);
            myTrack aTrack  = simpleLinearLeastSquaresFit(matchedHits);
            nNewMatchedTracks++;
            newMatchedTracks.push_back(aTrack);

            plots->trueParticlePt_numRecoTracks->Fill(outerHit->PT, eventWeight);

            if(aTrack.isNotFake()) nNewMatchedTracksNotFake++;
          }
        }
      }
    }
    //std::cout << "Number of inner hits: " << hc[0].size() << std::endl;
    //std::cout << "Number of new tracks: " << nNewMatchedTracks << " of which " << nNewMatchedTracksNotFake << " were real." << std::endl;

  plots->nRecoTracks->Fill(nNewMatchedTracks, eventWeight);
  plots->nRecoTracksMatched->Fill(nNewMatchedTracksNotFake, eventWeight);
  *******************************/

    
    //std::cout << "event has: " << nTracks << " delphes tracks" << std::endl;

  } // end loop over entries
  tree->Write();
} // end AnalyseEvents



//------------------------------------------------------------------------------

void PrintHistograms(ExRootResult *result, TestPlots *plots)
{
  result->Print("pdf");
}

//------------------------------------------------------------------------------

int main(int argc, char *argv[])
{

  //Matrix3xNd hits = Matrix3xNd::Random(3,3);
  //Matrix3Nd hits_cov = Matrix3Nd::Random(9,9);

  gROOT->SetBatch(1);

  // configurable(>) parameters
  float vertexDistSigma = 53.0; // standard deviation (1 sigma) of the distribution of vertices along z
  int nVertexSigma = 3;

  std::string appName = "basicTrackReconstructon";
  std::cout << "Will execute " << appName << std::endl;
  std::string inputFile = argv[1]; // doesn't complain about cast? Maybe compiler can deal with it :p
  std::string outputFile = argv[2];
  int doPrintHistograms = atoi(argv[3]);
  int nEvents(-1);
  if(argc > 4){
    nEvents = atoi(argv[4]);
    std::cout << "INFO: Will run over " << nEvents << std::endl;
  }
  // 
  if(argc < 4)
  {
    std::cout << " Usage: " << appName << " input_file output_file [optional: nEvents]" << std::endl;
    std::cout << " 1) input_file: ROOT file containing delphes output,"       << std::endl;
    std::cout << " 2) output_file: ROOT file name that will contain output histograms" << std::endl;
    std::cout << " 3) bool: write files to .pdf" << std::endl;
    std::cout << " 4) nEvents (optional): number of events to be processed (for testing, default is all events)." << std::endl;
    return 1;
  }

  // control analysis
  TChain *chain = new TChain("Delphes");
  std::cout << "Adding " << inputFile << " to chain" << std::endl;
  chain->Add(inputFile.c_str());


  // Try to add a new ROOT file
  TFile* oFile = new TFile("newFile.root", "RECREATE");
  TTree* tree = new TTree("Tracks", "A tree with tracks");

  /*************
  // test with a struct
  TestStruct track;
  track.pT = 5.0;
  track.z0 = 10;
  track.kappa = 0.001; 

  tree->Branch("track", &track, "pT/F:z0/F:kappa/F");
  tree->Fill();
  track.pT = 10.0;
  track.z0 = 11.0;
  track.kappa = 0.02;
  tree->Fill(); 
  tree->Write();
  oFile->Close();
  delete oFile;
  *************/


  ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
  ExRootResult *result = new ExRootResult();

  TestPlots *plots = new TestPlots;
  BookHistograms(result, plots);
  AnalyseEvents(nEvents, treeReader, plots, vertexDistSigma, nVertexSigma, tree);

  if(doPrintHistograms) PrintHistograms(result, plots);

  std::cout << "Writing to file: " << outputFile << std::endl;
  result->Write(outputFile.c_str());

  std::cout << "** Exiting..." << std::endl;

  delete plots;
  delete result;
  delete treeReader;
  delete chain;

  return 0;
}
