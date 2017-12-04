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

  ChargedHadronTrackingEfficiency
  ElectronTrackingEfficiency
  MuonTrackingEfficiency

  ChargedHadronMomentumSmearing
  ElectronMomentumSmearing
  MuonMomentumSmearing

  TrackMergerTruth
  TrackMerger
  TrackSmearing

  NeutrinoFilter

  GenMissingET

  GenJetFinder
  TrackJets

  TreeWriter
}


module PileUpMerger PileUpMerger {
  set InputArray Delphes/stableParticles

  set ParticleOutputArray stableParticles
  set VertexOutputArray vertices

  # pre-generated minbias input file
  set PileUpFile /afs/cern.ch/work/w/wfawcett/private/geneva/delphes/samples/pileup/MinBias_s10.pileup 

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

####################################
# Charged hadron tracking efficiency
####################################

module Efficiency ChargedHadronTrackingEfficiency {
  set InputArray ParticlePropagator/chargedHadrons
  set OutputArray chargedHadrons

 # TBC (which eta_max ? which pT min?)

 # tracking efficiency formula for charged hadrons

  # Set tracking efficiency to 100 % 
  #set EfficiencyFormula { (pt <= 0.5) * (0.00) + \
(abs(eta) <= 2.5) * (pt > 0.5 && pt <= 1) * (0.90) + \
(abs(eta) <= 2.5) * (pt > 1) * (0.95) + \
(abs(eta) > 2.5 && abs(eta) <= 4) * (pt > 0.5 && pt <= 1) * (0.85) + \
(abs(eta) > 2.5 && abs(eta) <= 4) * (pt > 1) * (0.90) + \
(abs(eta) > 4 && abs(eta) <= 6) * (pt > 0.5 && pt <= 1) * (0.80) + \
(abs(eta) > 4 && abs(eta) <= 6) * (pt > 1.0) * (0.85) + \
(abs(eta) > 6.0) * (0.00)}

  # WJF: set tracking efficiency to 100% (on advice from Michele)
  set EfficiencyFormula { 1.00 } 


}

##############################
# Electron tracking efficiency
##############################

module Efficiency ElectronTrackingEfficiency {
  set InputArray ParticlePropagator/electrons
  set OutputArray electrons

# TBC (which eta_max ?)
# putting same as charged hadrons for now...

  # WJF: set tracking efficiency to 100% (on advice from Michele)
  set EfficiencyFormula { 1.00 }
  #set EfficiencyFormula { (pt <= 0.5) * (0.00) + \
  (abs(eta) <= 2.5) * (pt > 0.5 && pt <= 1) * (0.90) + \
  (abs(eta) <= 2.5) * (pt > 1) * (0.95) + \
  (abs(eta) > 2.5 && abs(eta) <= 4) * (pt > 0.5 && pt <= 1) * (0.85) + \
  (abs(eta) > 2.5 && abs(eta) <= 4) * (pt > 1) * (0.90) + \
  (abs(eta) > 4 && abs(eta) <= 6) * (pt > 0.5 && pt <= 1) * (0.80) + \
  (abs(eta) > 4 && abs(eta) <= 6) * (pt > 1.0) * (0.85) + \
  (abs(eta) > 6.0) * (0.00)}

}
##########################
# Muon tracking efficiency
##########################

module Efficiency MuonTrackingEfficiency {
  set InputArray ParticlePropagator/muons
  set OutputArray muons

# TBC (which eta_max ? why eff = 0 for 4 < eta < 6 ? for now put the same as central)
# what about high pT ?
 # tracking efficiency formula for muons

  # WJF: set tracking efficiency to 100% (on advice from Michele)
  set EfficiencyFormula { 1.00 }
  #set EfficiencyFormula { (pt <= 0.5) * (0.00) + \
  (abs(eta) <= 6.0) * (pt > 0.5 && pt <= 1) * (0.90) + \
  (abs(eta) <= 6.0) * (pt > 1) * (0.99) + \
  (abs(eta) > 6.0) * (0.00)}

}

########################################
# Momentum resolution for charged tracks
########################################

module MomentumSmearing ChargedHadronMomentumSmearing {
  set InputArray ChargedHadronTrackingEfficiency/chargedHadrons
  set OutputArray chargedHadrons

  #source momentumResolutionVsP.tcl 
  #source triplet_1barrel50mm_pRes_Delphes.tcl
  #source tripletFCCresolutions.tcl
  set ResolutionFormula { 0.0 } 
}


###################################
# Momentum resolution for electrons
###################################

module MomentumSmearing ElectronMomentumSmearing {
  set InputArray ElectronTrackingEfficiency/electrons
  set OutputArray electrons

  #source momentumResolutionVsP.tcl 
  #source triplet_1barrel50mm_pRes_Delphes.tcl
  #source tripletFCCresolutions.tcl
  set ResolutionFormula { 0.0 } 

}


###############################
# Momentum resolution for muons
###############################

module MomentumSmearing MuonMomentumSmearing {
  set InputArray MuonTrackingEfficiency/muons
  set OutputArray muons

  # TBC for just putting tracker resolution/ need to add improvement at high pT

  #source muonMomentumResolutionVsP.tcl 
  #source triplet_1barrel50mm_pRes_Delphes.tcl
  #source tripletFCCresolutions.tcl 
  set ResolutionFormula { 0.0 } 
   
}

##############
# Track merger
##############

module Merger TrackMerger {
  add InputArray ChargedHadronMomentumSmearing/chargedHadrons
  add InputArray ElectronMomentumSmearing/electrons
  add InputArray MuonMomentumSmearing/muons
  set OutputArray tracks
}

module TrackSmearing TrackSmearing {
  set InputArray TrackMerger/tracks
  #set BeamSpotInputArray BeamSpotFilter/beamSpotParticle
  set OutputArray tracks
  #set ApplyToPileUp true

  # magnetic field
  set Bz 4.0

  source tripletFCCresolutions.tcl 
}



# WJF attempt: truth tracks
module Merger TrackMergerTruth {

  #add InputArray ChargedHadronTrackingEfficiency/chargedHadrons
  #add InputArray ElectronTrackingEfficiency/electrons
  #add InputArray MuonTrackingEfficiency/muons
  add InputArray ParticlePropagator/chargedHadrons
  add InputArray ParticlePropagator/muons
  add InputArray ParticlePropagator/electrons
  set OutputArray tracks 

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

# TBC: is jet radius fine?

module FastJetFinder GenJetFinder {
#  set InputArray NeutrinoFilter/filteredParticles
  set InputArray Delphes/stableParticles

  set OutputArray jets

  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4

  set JetPTMin 5.0
}

module FastJetFinder TrackJets {
#  set InputArray NeutrinoFilter/filteredParticles
  set InputArray TrackMerger/tracks

  set OutputArray jets

  # algorithm: 1 CDFJetClu, 2 MidPoint, 3 SIScone, 4 kt, 5 Cambridge/Aachen, 6 antikt
  set JetAlgorithm 6
  set ParameterR 0.4

  set JetPTMin 5.0
}

#########################
# Gen Missing ET merger
########################

module Merger GenMissingET {

# add InputArray InputArray
  add InputArray NeutrinoFilter/filteredParticles
  set MomentumOutputArray momentum
}



##################
# ROOT tree writer
##################

module TreeWriter TreeWriter {
# add Branch InputArray BranchName BranchClass
  add Branch Delphes/allParticles Particle GenParticle

  add Branch GenJetFinder/jets GenJet Jet
  add Branch TrackJets/jets TrackJet Jet
  add Branch GenMissingET/momentum GenMissingET MissingET

  #add Branch TrackMerger/tracks Track Track
  add Branch TrackSmearing/tracks Track Track
  add Branch TrackMergerTruth/tracks TruthTrack Track

  #add Branch PileUpMerger/stableParticles PileupParticle GenParticle 
  
}

