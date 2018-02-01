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
#include "classes/anaClasses.h"

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
#include "tricktrack/RiemannFit.h"


//------------------------------------------------------------------------------

struct TestPlots
{

  TH1 *nJets;
  TH1 *allJetPt;
  TH1* nDelphesTracks;
  TH1* nDelphesTracks1GeV;
  TH1* nRecoTracks; 

};

//------------------------------------------------------------------------------

void BookHistograms(ExRootResult *result, TestPlots *plots)
{

  plots->nJets          = result->AddHist1D("nJets", "nJets", "Number of Jets", "", 100, 0, 100, 0, 0 );
  plots->allJetPt       = result->AddHist1D("allJetPt", "", "Jet p_{T} (all jets) [GeV]", "", 100, 0, 1000);
  plots->nDelphesTracks = result->AddHist1D("nDelphesTracks", "TrueTracks", "Number of tracks", "Number of events", 10000, 0, 10000,0,0);
  plots->nDelphesTracks1GeV = result->AddHist1D("nDelphesTracks1GeV", "TrueTracks > 1 GeV", "Number of tracks", "Number of events", 10000, 0, 10000,0,0);
  plots->nRecoTracks    = result->AddHist1D("nRecoTracks", "Tracks+fakes", "Number of tracks", "Number of events", 10000, 0, 10000,0,0);

}

//------------------------------------------------------------------------------

void AnalyseEvents(const int nEvents, ExRootTreeReader *treeReader, TestPlots *plots, float vertexDistSigma, int nVertexSigma)
{

  // Define branches
  TClonesArray *branchParticle   = treeReader->UseBranch("Particle");
  TClonesArray *branchTruthTrack = treeReader->UseBranch("TruthTrack");
  TClonesArray *branchTrack      = treeReader->UseBranch("Track");
  TClonesArray *branchHit        = treeReader->UseBranch("Hits");

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

    
    // Fill the hitContainer with all the hits in the event (geometry defined by the surfaces) 
    std::map<int, std::vector<Hit*> > event; 
    hitContainer hc; 
    for(auto itHit = branchHit->begin(); itHit != branchHit->end(); ++itHit){
      Hit * hit = dynamic_cast<Hit*>(*itHit);
      int SurfaceID = hit->SurfaceID; 
      hc[SurfaceID].push_back(hit); 
    }

    // contains the rules to associate hits together, and then the collection of hits into tracks 
    TrackFitter tf(fitTypes::linearInToOut, parameters); 
    bool success = tf.AssociateHits( hc ); 
    std::vector< myTrack > theTracks = tf.GetTracks(); 

    //std::cout << "event has: " << theTracks.size() << " reconstructed tracks" << std::endl;
    plots->nRecoTracks->Fill(theTracks.size(), eventWeight);

    int nTracks(0);
    int nTracks1GeV(0);
    for(auto itTrack=branchTrack->begin(); itTrack != branchTrack->end(); ++itTrack){
      Track* track = dynamic_cast<Track*>(*itTrack);
      nTracks++;
      if(track->PT < 1.0) continue;
      nTracks1GeV++;
    }
    plots->nDelphesTracks->Fill(nTracks, eventWeight);
    plots->nDelphesTracks1GeV->Fill(nTracks1GeV, eventWeight);
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
