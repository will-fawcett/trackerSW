#
#  Delphes card for tripltet of tracking layers 
#
#  Main authors:  William Fawcett (Geneva)
#
#######################################
# Order of execution of various modules
#######################################

set ExecutionPath {
  NeutrinoFilter
  ParticlePropagator

  ParticlePropagator
  TrackMerger

  HitFinder30 
  HitToTrack
  
  

  TreeWriter
}

# Things removed from ExecutionPath
  #HitFinder50
  #HitFinder40
  #HitFinder30
  #HitFinder20
  #HitFinder10
  ##
  #TrackEfficiency
  #TrackSmearing
  #NeutrinoFilter
  #PrimaryBinFinder
  #VertexTrackAssociator
  #TrackJetFinder
  #TrackTruthJetFinder


#################################
# Propagate particles in cylinder
#################################

module ParticlePropagator ParticlePropagator {
  set InputArray Delphes/stableParticles

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
  set TrackPtMax 100
  set OutputArray tracks 
}

module HitFinder HitFinder50 {
  set InputArray Delphes/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.532} {0.582} {0.632}
}

module HitFinder HitFinder40 {
  set InputArray Delphes/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.542} {0.582} {0.622}
}


module HitFinder HitFinder20 {
  set InputArray Delphes/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.562} {0.582} {0.602}
}

module HitFinder HitFinder10 {
  set InputArray Delphes/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.572} {0.582} {0.592}
}


#################################
# HitToTrack (take delphes hits and reconstruct tracks)
################################
module HitToTrack HitToTrack {
  set InputArray HitFinder30/hits
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
# My track associator (unfinished?)
#####################
module VertexTrackAssociator VertexTrackAssociator { 
  set TrackInputArray TrackSmearing/tracks
  set VertexInputArray PrimaryBinFinder/vertices
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

module FastJetFinder TrackTruthJetFinder {
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

module FastJetFinder TrackJetFinder {
  set InputArray TrackSmearing/tracks

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

  #add Branch TrackEfficiency/tracks TruthTrack Track
  #add Branch TrackSmearing/tracks Track Track

  #add Branch PrimaryBinFinder/vertices PrimaryBin Vertex
  #add Branch VertexTrackAssociator/tracks AssociatedTracks Track

  #add Branch HitFinder50/hits Hits50 Hit
  #add Branch HitFinder40/hits Hits40 Hit
  add Branch HitFinder30/hits Hits30 Hit
  #add Branch HitFinder20/hits Hits20 Hit
  #add Branch HitFinder10/hits Hits10 Hit
  
  add Branch HitToTrack/tracks TracksFromHit30 Track

  # Then write a module to take the vertices and spit out the tracks from the highest pT vertex 
  # Need access to pointers inside vertex 
  # Then feed into Delphes JetFinder module 

  #add Branch GenJetFinder/jets GenJet Jet # WJF don't want GenJets? 

  #add Branch TrackTruthJetFinder/jets TrackTruthJet Jet
  #add Branch TrackJetFinder/jets TrackJet Jet

  # if you want to add the pileup particles to the particles -- collection will become huge
  #add Branch PileUpMerger/stableParticles PileupParticle GenParticle 
}

