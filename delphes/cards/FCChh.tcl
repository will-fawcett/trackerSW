#
#  Delphes card for tripltet of tracking layers 
#
#  Main authors:  William Fawcett (Geneva)
#
#######################################
# Order of execution of various modules
#######################################

set ExecutionPath {
  ParticlePropagator

  TrackMerger
  TrackEfficiency
  TrackSmearing

  NeutrinoFilter

  TrackJetFinder
  TrackTruthJetFinder

  TreeWriter
}
## GenJetFinder


#################################
# Propagate particles in cylinder
#################################

module ParticlePropagator ParticlePropagator {
  set InputArray Delphes/stableParticles

  set OutputArray stableParticles
  set ChargedHadronOutputArray chargedHadrons
  set ElectronOutputArray electrons
  set MuonOutputArray muons

  # radius of the magnetic field coverage, in m
  set Radius 1.5
  # half-length of the magnetic field coverage, in m
  set HalfLength 5

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


#################################
# Remove tracks with pT < 0.5 GeV and |eta| > 2.1 
#################################

module Efficiency TrackEfficiency {
  set InputArray TrackMerger/tracks
  set OutputArray tracks 
  set EfficiencyFormula { (pt <= 0.5) * (0.00) +
                        (abs(eta) <= 2.1) * (pt > 0.5) * (1.00) +
                        (abs(eta) > 2.1)  * (0.00)}
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

  source tripletFCCresolutions.tcl 
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

  #add Branch PileUpMerger/vertices Vertex Vertex

  add Branch TrackEfficiency/tracks TruthTrack Track
  add Branch TrackSmearing/tracks Track Track

  add Branch TrackSmearing/vertices Vertex Vertex

  #add Branch GenJetFinder/jets GenJet Jet # WJF don't want GenJets? 
  add Branch TrackTruthJetFinder/jets TrackTruthJet Jet
  add Branch TrackJetFinder/jets TrackJet Jet


  #add Branch PileUpMerger/stableParticles PileupParticle GenParticle 
}

