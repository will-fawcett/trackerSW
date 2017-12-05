#
#  Delphes card for tripltet of tracking layers 
#
#  Main authors:  William Fawcett (Geneva)
#
#######################################
# Order of execution of various modules
#######################################

set ExecutionPath {
  PileUpMerger
  ParticlePropagator

  TrackMerger
  TrackMergerTruth
  TrackSmearing

  NeutrinoFilter

  TrackJetFinder
  TrackTruthJetFinder

  TreeWriter
}
## GenJetFinder

#################################
# PU merger
#################################

module PileUpMerger PileUpMerger {
  set InputArray Delphes/stableParticles

  set ParticleOutputArray stableParticles
  set VertexOutputArray vertices

  # pre-generated minbias input file
  #set PileUpFile /afs/cern.ch/work/w/wfawcett/private/geneva/delphes/samples/pileup/MinBias_s10.pileup 
  set PileupParticle /atlas/data4/userdata/wfawcett/delphes/samples/pileup/MinBias_s10.pileup
  #set PileUpFile MinBias.pileup

  # average expected pile up
  set MeanPileUp 200

  # Set pileup distribution: 0 for poisson, 1 for uniform 
  set PileUpDistribution 0 

  # maximum spread in the beam direction in m
  set ZVertexSpread 0.25

  # maximum spread in time in s
  set TVertexSpread 800E-12

  # vertex smearing formula f(z,t) (z,t need to be respectively given in m,s) - {exp(-(t^2/160e-12^2/2))*exp(-(z^2/0.053^2/2))}
  set VertexDistributionFormula {exp(-(t^2/160e-12^2/2))*exp(-(z^2/0.053^2/2))}

}


#################################
# Propagate particles in cylinder
#################################

module ParticlePropagator ParticlePropagator {
  set InputArray PileUpMerger/stableParticles

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

module Merger TrackMerger {
  add InputArray ParticlePropagator/chargedHadrons
  add InputArray ParticlePropagator/muons
  add InputArray ParticlePropagator/electrons
  set OutputArray tracks 
}


#################################
# Remove tracks with pT < 0.5 GeV and |eta| > 2.1 
#################################

module Efficiency TrackMergerTruth {
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
  set InputArray TrackMergerTruth/tracks
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
  set InputArray TrackMergerTruth/tracks

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

  add Branch PileUpMerger/vertices Vertex Vertex

  add Branch TrackMergerTruth/tracks TruthTrack Track
  add Branch TrackSmearing/tracks Track Track

  #add Branch GenJetFinder/jets GenJet Jet # WJF don't want GenJets? 
  add Branch TrackTruthJetFinder/jets TrackTruthJet Jet
  add Branch TrackJetFinder/jets TrackJet Jet


  #add Branch PileUpMerger/stableParticles PileupParticle GenParticle 
}

