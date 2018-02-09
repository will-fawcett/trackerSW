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


//------------------------------------------------------------------------------

struct TestPlots
{


  // Number of true tracks
  TH1* nDelphesTracks;
  TH1* nDelphesTracks1GeV;
  TH1* nDelphesTracks10GeV;
  std::vector<TH1*> nDelphesHits; 
  
  // number of reconstructed tracks
  std::vector<TH1*> nRecoTracks; 
  std::vector<TH1*> nRecoTracksMatched;
  TH1* fractionOfFakeTracks;

  TH1* trueParticlePt_numParticles;
  TH1* trueParticlePt_numRecoTracks;


  // Fake rate as a function of pT, eta
  std::vector<TH1*> recoTrackPt;
  std::vector<TH1*> recoTrackPt_fake; 
  std::vector<TH1*> recoTrackEta;
  std::vector<TH1*> recoTrackEta_fake; 

};

//------------------------------------------------------------------------------

void BookHistograms(ExRootResult *result, TestPlots *plots)
{

  int hitMultiplicity = 5000;

  for(int i=0; i<6; ++i ){
    std::string trackerID = std::to_string((i+1)*10);

    plots->nDelphesHits.push_back(
        result->AddHist1D("nDelphesHits_"+trackerID, "Number of hits in outermost layer", "", "", hitMultiplicity, 0, hitMultiplicity,0,0)
        );
    plots->nRecoTracks.push_back(
        result->AddHist1D("nRecoTracks_"+trackerID, "Tracks+fakes", "Number of tracks", "Number of events", hitMultiplicity, 0, hitMultiplicity,0,0)
        );
    plots->nRecoTracksMatched.push_back(
        result->AddHist1D("nRecoTracksMatched_"+trackerID, "Matched tracks", "Number of tracks", "Number of events", hitMultiplicity, 0, hitMultiplicity,0,0)
        );

    plots->recoTrackPt.push_back(
        result->AddHist1D("recoTrackPt_"+trackerID, "Reco track pT", "", "", 1000, 0, 1000, 0, 0)
        );
    plots->recoTrackPt_fake.push_back(
        result->AddHist1D("recoTrackPt_fake_"+trackerID, "Fake Reco track pT", "", "", 1000, 0, 1000, 0, 0)
        );
    plots->recoTrackEta.push_back(
        result->AddHist1D("recoTrackEta_"+trackerID, "Reco track eta", "", "", 100, -5, 5, 0, 0)
        );
    plots->recoTrackEta_fake.push_back(
        result->AddHist1D("recoTrackEta_fake_"+trackerID, "Fake Reco track eta", "", "", 100, -5, 5, 0, 0)
        );


  }

    plots->nDelphesTracks = result->AddHist1D("nDelphesTracks", "TrueTracks", "Number of tracks", "Number of events", hitMultiplicity, 0, hitMultiplicity,0,0);
    plots->nDelphesTracks1GeV = result->AddHist1D("nDelphesTracks1GeV", "TrueTracks > 1 GeV", "Number of tracks", "Number of events", hitMultiplicity, 0, hitMultiplicity,0,0);
    plots->nDelphesTracks10GeV = result->AddHist1D("nDelphesTracks10GeV", "TrueTracks > 10 GeV", "Number of tracks", "Number of events", hitMultiplicity, 0, hitMultiplicity,0,0);


  plots->fractionOfFakeTracks = result->AddHist1D("fractionOfFakeTracks", "", "", "", 100, 0, 1, 0, 0);

  plots->trueParticlePt_numParticles = result->AddHist1D("trueParticlePt_numParticles", "", "", "", 100, 0, 100, 0, 0);
  plots->trueParticlePt_numRecoTracks = result->AddHist1D("trueParticlePt_numRecoTracks", "", "", "", 100, 0, 100, 0, 0);

}

//------------------------------------------------------------------------------

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
      if(! track.isNotFake() ) nFakes++;
    }
    return nFakes;
}

//------------------------------------------------------------------------------

void AnalyseEvents(const int nEvents, ExRootTreeReader *treeReader, TestPlots *plots, float vertexDistSigma, int nVertexSigma)
{

  // Define branches
  TClonesArray *branchParticle   = treeReader->UseBranch("Particle");
  TClonesArray *branchTruthTrack = treeReader->UseBranch("TruthTrack");
  TClonesArray *branchTrack      = treeReader->UseBranch("Track");

  // Different hit branches, corresponding to the different geometry 
  TClonesArray *branchHit50        = treeReader->UseBranch("Hits50");
  TClonesArray *branchHit40        = treeReader->UseBranch("Hits40");
  TClonesArray *branchHit30        = treeReader->UseBranch("Hits30");
  TClonesArray *branchHit20        = treeReader->UseBranch("Hits20");
  TClonesArray *branchHit10        = treeReader->UseBranch("Hits10");

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
    hitContainer hc50 = fillHitContainer(branchHit50); 
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
    for(hitContainer hc : theHitContainers){

      TrackFitter tf(fitTypes::simpleLinear, parameters, layerIDs); 
      if( tf.AssociateHits(hc) ){
        std::vector< myTrack > theTracks = tf.GetTracks(); 
        int nFakes = countFakes(theTracks);
        std::vector<Hit*> outerHits = hc[2];
        plots->nDelphesHits.at(counter)->Fill( outerHits.size(), eventWeight); // number of hits in outer layer
        plots->nRecoTracks.at(counter)->Fill(theTracks.size(), eventWeight);
        plots->nRecoTracksMatched.at(counter)->Fill(theTracks.size() - nFakes, eventWeight);

        // loop over tracks to fill fake rate plots
        for(const auto& track : theTracks){
          plots->recoTrackPt.at(counter)->Fill(track.Pt());
          plots->recoTrackEta.at(counter)->Fill(track.Eta()); // might want to check theta calculation
          if(track.isFake()){
            plots->recoTrackPt_fake.at(counter)->Fill(track.Pt());
            plots->recoTrackEta_fake.at(counter)->Fill(track.Eta()); // might want to check theta calculation
          }
        }

      }
      //std::cout << "i: " << counter << std::endl;
      ++counter;
    }



    TrackFitter tf2(fitTypes::simpleLinear, parameters, layerIDs); 
    if( tf2.AssociateHits(hc50) ){
      std::vector< myTrack > theTracks50 = tf2.GetTracks(); 
      int nFakes50 = countFakes(theTracks50);
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

  ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
  ExRootResult *result = new ExRootResult();

  TestPlots *plots = new TestPlots;
  BookHistograms(result, plots);
  AnalyseEvents(nEvents, treeReader, plots, vertexDistSigma, nVertexSigma);

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
