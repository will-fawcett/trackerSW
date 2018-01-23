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

using namespace fastjet;

// typedef for hit container 
//using hitContainer = std::map<int, std::vector<myHit*> >; 
using hitContainer = std::map<int, std::vector<Hit*> >; 

// object to store track parameters (TO DO)! 
class myTrack{
  public:
    float coord;
};

// enum for different fit types (can add more later) 
enum fitTypes{
  linear,
  MAX
};

// class to 
class TrackFitter{

  private:
    std::vector< myTrack > tracks; 
    fitTypes fitType;
    std::vector<float> parameters;

    std::vector< std::vector< Hit* >> associatedHitCollection; 

    bool associateHitsLinearOutToIn(hitContainer hc, float minZ, float maxZ){
      /***********************************************
       * Hit association algorithm
       * - Assumes concentric barrel layers, no endcaps
       * - Innermost layer labelled with 0, incremented as layers increase
       *
       * The algorithm:
       * - Starts from a hit in the outer layer, calculates a window in the layer benieth in which to search for other hits
       * - Loops over hits in the next innermost layer, if within the search window, then this hit is assigned the hit in the above layer
       *   -- repeat untill the last layer
       * *********************************************/

      // Get layer IDs from hitContainer
      std::vector<int> layers;
      for(auto const& key : hc){
        layers.push_back(key.first);
      }
      std::reverse(layers.begin(), layers.end()); // should count from 3 .. 2 .. 1 

      // start from outermost barrel layer, and work inwards
      for(int layerID : layers){
        if(layerID == layers.back()) continue; // don't execute algorithm for innermost layer

        // get the r coordinate of the next-innermost layer
        float rInner = hc[layerID-1].at(0)->Perp(); // should be able to optimize this away? 

        // loop over all hits in layer
        for(Hit* hit : hc[layerID]){

          // find window for hits in the next layer to be assigned to this one
          float r = hit->Perp();
          float z = hit->Z;
          float zLeft  = calculateZWindowForNextLevel(r, z, rInner, minZ); 
          float zRight = calculateZWindowForNextLevel(r, z, rInner, maxZ); 

          // loop over all hits in next layer
          for(Hit* innerHit : hitMap[layerID - 1]){
            float innerHitZ = innerHit.Z; 

            // if hit within window, assign to the bit above 
            if(zLeft < innerHitZ && innerHitZ < zRight){
              hit->addHit(&innerHit); 
            }
          }
          
        } // loop over hits in layer
      }
      return true;
    } // end associateHitsLinearOutToIn


  public:
    
    // constructor 
    TrackFitter(const fitTypes ftIn, std::vector<float> paramIn){
      fitType=ftIn;
      parameters=paramIn;
    };

    bool FitFromHits(hitContainer hc){

      switch (fitType) { 
        case linear:
          float minZ = parameters.at(0);
          float maxZ = parameters.at(1);
          return this->associateHitsLinearOutToIn(hc, minZ, maxZ);
      }

      return true; 
    }


    std::vector <myTrack> GetTracks(){
      std::vector<myTrack> temp; 
      return temp;
    }

    // select the algorithm to associate hits to one another 
    /***
    switch (fitType) {
      case linear:
        return this->associateHitsLinear(hc);
      default:
        std::cout << "default" << std::endl;
        break;
    }
    ***/


};



// possibly now obsolete class to store hits (and relationships between hits) 
class myHit{
  private:
    TLorentzVector position;
    int SurfaceID;
    int UniqueHitID; 

    //std::map<int, std::vector<int> > assignedHits;
    std::map<int, std::vector<myHit*> > assignedHits; // maybe const myHit* .... to think about 

  public:

    // constructor 
    myHit(const Hit *hitIn, const int ID){
      position.SetXYZT(hitIn->X, hitIn->Y, hitIn->Z, hitIn->T);
      SurfaceID = hitIn->SurfaceID;
      UniqueHitID = ID; 
      //assignedHits = 0;
    };


    void printHit(){
      std::cout << "position: (" << position.X() << ", " << position.Y() << ", " << position.Z() << ")" 
        << "\t surface: " << SurfaceID 
        << "\t UID: " << UniqueHitID 
        << std::endl;
    }

    // other hits matched to this hit 
    void addHit(myHit * hitIn){
      assignedHits[hitIn->SurfaceID].push_back(hitIn);
    }

    int countAssignedHitsInLayer(const int layerID){
      return assignedHits[layerID].size();
    }

    void printAssignedHits(){
      std::cout << "Hit has: " << std::endl;
      for(const auto &surface : assignedHits){ // returns a pair
          std::cout << "\t" << surface.second.size() << " hits in layer " << surface.first << std::endl;
      }
    }

    // access some of the TLorentzVector functions
    float X() {return position.X();}
    float Y() {return position.Y();}
    float Z() {return position.Z();}
    float T() {return position.T();}
    float Perp() {return position.Perp();}

};

//------------------------------------------------------------------------------

std::string PrintTLorentz(TLorentzVector &v){
  std::ostringstream s;
  s <<  " (" << v.Pt() << ", " << v.Eta() << ", " << v.Phi() << ", " << v.M() << ")";
  return s.str();
}

//------------------------------------------------------------------------------

// Rule for sorting vector of tracks 
bool reverse(const Track* i, const Track* j){
  return i->PT > j->PT; 
}

//------------------------------------------------------------------------------

inline float calculatDeltaPhi(float phi1, float phi2){
  return acos( cos( phi1 - phi2 ));
}

//------------------------------------------------------------------------------

struct TestPlots
{

  TH1 *nJets;
  TH1 *allJetPt;

};

//------------------------------------------------------------------------------

void BookHistograms(ExRootResult *result, TestPlots *plots)
{

  plots->nJets           = result->AddHist1D( "nJets", "nJets", "Number of Jets", "", 100, 0, 100, 0, 0 );
  plots->allJetPt        = result->AddHist1D("allJetPt", "", "Jet p_{T} (all jets) [GeV]", "", 100, 0, 1000);

}

//------------------------------------------------------------------------------


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

  bool debug = true; 


  // Loop over all events
  Long64_t allEntries = treeReader->GetEntries();
  int nEventsCorrectlyIdentifiedVertex(0);
  std::cout << "** Chain contains " << allEntries << " events" << std::endl;
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

    /////////////////////
    // Marco's suggestion 
    /////////////////////
    
    // Fill the hitContainer with all the hits in the event (geometry defined by the surfaces) 
    std::map<int, std::vector<Hit*> > event; 
    hitContainer hc; 
    for(auto itHit = branchHit->begin(); itHit != branchHit->end(); ++itHit){
      Hit * hit = dynamic_cast<Hit*>(*itHit);
      int SurfaceID = hit->SurfaceID; 
      hc[SurfaceID].push_back(hit); 
    }

    TrackFitter tf(linear, parameters); // contains the rules to associate hits together, and then the collection of hits into tracks 
    bool success = tf.FitFromHits( hc ); 
    std::vector< myTrack > theTracks = tf.GetTracks(); 

    /////////////////////
    // WJF original code
    /////////////////////

    // sort hits into layers
    /************************************
    std::map<int, std::vector<myHit> > hitMap; 
    int uniqueHitID = 0;
    for(auto itHit = branchHit->begin(); itHit != branchHit->end(); ++itHit){
      Hit * hit = dynamic_cast<Hit*>(*itHit);
      TLorentzVector position;
      position.SetXYZT(hit->X, hit->Y, hit->Z, hit->T);
      int SurfaceID = hit->SurfaceID; 
      hitMap[SurfaceID].push_back( myHit(hit, uniqueHitID ) );
      uniqueHitID++; 
    }

    // extract the unique keys in the hit map (should correspond to the number of layers)
    std::vector<int> layers;
    for(auto const& key: hitMap){
      layers.push_back(key.first);
    }
    std::reverse(layers.begin(), layers.end()); // should count from 3 .. 2 .. 1 
    if(debug){
      std::cout << "Event has: " << layers.size() << " layers" << std::endl;
      for(auto l : layers){
        std::cout << "\tLayer " << l << " has " << hitMap[l].size() << " hits." << std::endl;
      }
    }


    // start from outermost barrel layer, and work inwards
    for(int layerID : layers){
      if(layerID == layers.back()) continue; // don't execute algorithm for innermost layer

      // loop over all hits in layer
      //for(auto hit : hitMap[layerID]){
      for(int hitID=0; hitID < hitMap[layerID].size(); ++hitID){

        myHit *hit = &hitMap[layerID].at(hitID); // get pointer to the hit inside the map

        // get the r coordinate of the next layer
        float rInner = hitMap[layerID-1].at(0)->Position.Perp(); 

        // find window for hits in the next layer to be assigned to this one
        float r = hit->Perp();
        float z = hit->Z();
        float zLeft  = calculateZWindowForNextLevel(r, z, rInner, minZ); 
        float zRight = calculateZWindowForNextLevel(r, z, rInner, maxZ); 

        // loop over all hits in next layer
        for(auto innerHit : hitMap[layerID - 1]){
          float innerHitZ = innerHit.Z(); 
          //std::cout << "inner hit Z " << innerHitZ << std::endl;

          // if hit within window, assign to the bit above 
          if(zLeft < innerHitZ && innerHitZ < zRight){
            hit->addHit(&innerHit); 
          }
        }

        //hit->printHit();
        //hit->printAssignedHits();
        
      } // loop over hits in layer
    } // end loop over layers 

    // now investigate the hits
    for(auto & hit : hitMap[2]){
      hit.printHit();
      hit.printAssignedHits();
    //std::cout << "has " << hit.countAssignedHitsInLayer(1) << " assigned hits in layer 1" << std::endl;
    }
    ****************************************/


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

  gROOT->SetBatch(1);
  bool DEBUG = false;

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