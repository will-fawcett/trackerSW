#
#  Delphes card for tripltet of tracking layers 
#
#  Main authors:  William Fawcett (Geneva)
# 
#   Workflow as follows. Two track collections are created. 
#   1: NeutrinoFilter -- removes neutrinos from particle collection 
#
#   Then split into "normal" tracking (delphes default), and tracking with hit reconstruction
#
#   "Normal" tracking
#   -----------------
#   a1: ParticlePropagator -- moves particles in B field to the central layer of the triplet
#   a2: TrackMerger -- takes charged particles from ParticlePropagator (just collates the charged particles), labels them as tracks
#   a3: TrackEfficiency --  removes tracks with pT < 0.5 GeV and |eta| > 2.0 (save space, were not interested in these, and the triplet doesn't go beyond |eta|>2 anyway) 
#   > output "TrackEfficiency/tracks TruthTracks"
#   a4: TrackSmearing -- apply the smearing formulea from delphize, proxy for reconstructed tracks  
#   > output "TrackSmearing/tracks Tracks"  
#
#   Now tracking goes into finding primary bins 
#   a5: PrimaryBinFinder -- finds the primary bin (can also find multiple primary bins)
#   > output: a set of vertices (ordered by highest sum(pT))
#   a6: VertexTrackAssociator -- selects the tracks that match to the primary bin
#   
#   
#
#   Hit reconstruction tracking
#   ---------------------------
#   b1: HitFinder -- applies propagates particles N times to each of the N tracker layers. Generates N hits
#   > output "HitFinder/hits Hits"
#   b2: HitToTrack -- applies seeding to the HitFinder/hits and creates tracks out of these
#   > output "HitToTrack/tracks Tracks"  
#
#
#
#
#######################################
# Order of execution of various modules
#######################################

set ExecutionPath {

  NeutrinoFilter

  ParticlePropagator
  TrackMerger
  TrackEfficiency
  TrackSmearing

  PrimaryBinFinder
  VertexTrackAssociator

  TruthTrackJetFinder
  SmearedTrackJetFinder
  PBMatchedTrackJetFinder

  HitFinder30 
  HitToTrack
  FakeTrackRemover
  SmearedTracksFromHits

  PrimaryBinFinderHits
  VertexTrackAssociatorHits

  HitTrackJetFinder
  SmearedHitTrackJetFinder
  PBMatchedHitTrackJetFinder

  TreeWriter
}

#################
# Neutrino Filter
#################

module PdgCodeFilter NeutrinoFilter {

  set InputArray Delphes/stableParticles
  set OutputArray filteredParticles

  set PTMin 0.0

  add PdgCode {12}
  add PdgCode {14}
  add PdgCode {16}
  add PdgCode {-12}
  add PdgCode {-14}
  add PdgCode {-16}

}



#################################
# Propagate particles in cylinder
#################################

module ParticlePropagator ParticlePropagator {
  set InputArray NeutrinoFilter/filteredParticles

  set OutputArray stableParticles
  set ChargedHadronOutputArray chargedHadrons
  set ElectronOutputArray electrons
  set MuonOutputArray muons

  # radius of the magnetic field coverage, in m (want radius of the tracker)  ######## NOT THIS -> (radius of innermost tiplet layer in r) <- NOT THIS
  set Radius 0.582
  # half-length of the magnetic field coverage, in m (length of tracker in z)
  set HalfLength 2.250 

  # magnetic field
  set Bz 4.0
}


#################################
# Truth tracks full pT and Eta range 
#################################
# Creates truth tracks 
module Merger TrackMerger {
  add InputArray ParticlePropagator/chargedHadrons
  add InputArray ParticlePropagator/muons
  add InputArray ParticlePropagator/electrons
  set OutputArray tracks 
}



#################################
# Remove truth tracks with pT < 0.5 GeV and |eta| > 2.0 
#################################

module Efficiency TrackEfficiency {
  set InputArray TrackMerger/tracks
  set OutputArray tracks 
  set EfficiencyFormula { (pt <= 1.00) * (0.00) +
                        (abs(eta) <= 2.0) * (pt > 1.00) * (1.00) +
                        (abs(eta) > 2.0)  * (0.00)}
}


#################################
# Smear the tracks according to the resolution formula from tkLayout 
#################################

module TrackSmearing TrackSmearing {
  set InputArray TrackEfficiency/tracks
  #set BeamSpotInputArray BeamSpotFilter/beamSpotParticle
  set OutputArray tracks
  set ApplyToPileUp true 

  # magnetic field
  set Bz 4.0
  source tripletFCCresolutions_50mm.tcl 
}


#####################
# Vertex Finder (uses some seeding) 
#####################
module VertexFinder VertexFinder {
  set InputArray TrackSmearing/tracks

  set MaxEta 2.0
  set SeedMinPT 1.0 
  set MinNDF 1 

  set VertexOutputArray vertices
  set OutputArray tracks

}


#####################
# My vertex finder
#####################
module PrimaryBinFinder PrimaryBinFinder {
  set InputArray TrackSmearing/tracks
  set NumPrimaryBins 1
  set BeamWidth 600
  set OutputArray vertices 
}


#####################
# My track associator : associates the tracks 
#####################
module VertexTrackAssociator VertexTrackAssociator { 
  set TrackInputArray TrackSmearing/tracks
  set VertexInputArray PrimaryBinFinder/vertices
  set OutputArray tracks
}

#####################
# MC truth jet finder
#####################

module FastJetFinder GenJetFinder {
  set InputArray Delphes/stableParticles
  set OutputArray jets
  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4
  set JetPTMin 5.0
}

#####################
# track truth jet finder
#####################

module FastJetFinder TruthTrackJetFinder {
  set InputArray TrackEfficiency/tracks
  set OutputArray jets
  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4
  set JetPTMin 5.0
}

#####################
# Track jet finder
#####################

module FastJetFinder SmearedTrackJetFinder {
  set InputArray TrackSmearing/tracks
  set OutputArray jets
  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4
  set JetPTMin 5.0
}

module FastJetFinder PBMatchedTrackJetFinder { 
  set InputArray VertexTrackAssociator/tracks
  set OutputArray jets
  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4
  set JetPTMin 5.0

}



# HitFinder (create delphes hits)
module HitFinder HitFinder30 {
  set InputArray NeutrinoFilter/filteredParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.552} {0.582} {0.612}
}

# HitToTrack (take delphes hits and reconstruct tracks)
module HitToTrack HitToTrack {
  set InputArray HitFinder30/hits
  set OutputArray tracks
}

# remove fake tracks with some pre-defined cuts 
module FakeTrackRemover FakeTrackRemover {
  set InputArray HitToTrack/tracks
  set OutputArray tracks 
}

# Smear the reconstructed tracks 
module TrackSmearing SmearedTracksFromHits {
  set InputArray FakeTrackRemover/tracks
  set OutputArray tracks
  set ApplyToPileUp true 
  set Bz 4.0
  source tripletFCCresolutions_50mm.tcl 
}

# find the primary bin from the reconstructed tracks
module PrimaryBinFinder PrimaryBinFinderHits {
  set InputArray SmearedTracksFromHits/tracks
  set NumPrimaryBins 1
  set BeamWidth 600
  set OutputArray vertices 
}

# associate tracks to the primary bin
module VertexTrackAssociator VertexTrackAssociatorHits { 
  set TrackInputArray SmearedTracksFromHits/tracks
  set VertexInputArray PrimaryBinFinderHits/vertices
  set OutputArray tracks
}

# cluster the (raw) hit-tracks into jets 
module FastJetFinder HitTrackJetFinder {
  set InputArray FakeTrackRemover/tracks
  set OutputArray jets
  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4
  set JetPTMin 5.0
}

# cluster the smeered hit-tracks into jets
module FastJetFinder SmearedHitTrackJetFinder {
  set InputArray SmearedTracksFromHits/tracks
  set OutputArray jets
  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4
  set JetPTMin 5.0
}

# cluster the hit-tracks that were associated to the PB into jets
module FastJetFinder PBMatchedHitTrackJetFinder {
  set InputArray VertexTrackAssociatorHits/tracks
  set OutputArray jets
  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4
  set JetPTMin 5.0
}


##################
# ROOT tree writer
##################

module TreeWriter TreeWriter {

  add Branch Delphes/allParticles Particle GenParticle
  #add Branch PileUpMerger/vertices Vertex Vertex

  # Stage A "normal" tracking
  add Branch TrackEfficiency/tracks TruthTrack Track
  add Branch TrackSmearing/tracks Track Track
  add Branch PrimaryBinFinder/vertices PrimaryBin Vertex
  add Branch VertexTrackAssociator/tracks PBMatchedTracks Track

  add Branch TruthTrackJetFinder/jets TruthTrackJets Jet
  add Branch SmearedTrackJetFinder/jets SmearedTrackJets Jet
  add Branch PBMatchedTrackJetFinder/jets PBMatchedTrackJets Jet

  # Stage B "tracking from hits"
  add Branch HitFinder30/hits Hits Hit
  add Branch FakeTrackRemover/tracks TracksFromHit30 Track
  add Branch SmearedTracksFromHits/tracks SmearedTracksFromHits Track

  add Branch PrimaryBinFinderHits/vertices PrimaryBinHits Vertex
  add Branch VertexTrackAssociatorHits/tracks PBMatchedHitTracks Track

  # jets from the tracks (from hits)
  add Branch HitTrackJetFinder/jets TruthHitTrackJets Jet
  add Branch SmearedHitTrackJetFinder/jets SmearedHitTrackJets Jet
  add Branch PBMatchedHitTrackJetFinder/jets PBMatchedHitTrackJets Jet 


  # if you want to add the pileup particles to the particles -- collection will become huge
  #add Branch PileUpMerger/stableParticles PileupParticle GenParticle 
}

