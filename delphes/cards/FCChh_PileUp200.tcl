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
  TrackEfficiency
  TrackSmearing

  NeutrinoFilter

  VertexFinder
  PrimaryBinFinder
  VertexTrackAssociator

  TrackJetFinder
  TrackTruthJetFinder

  Calorimeter

  TreeWriter
}

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

  # radius of the magnetic field coverage, in m (radius of innermost tiplet layer in r)
  set Radius 0.532
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
# My track associator
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


module SimpleCalorimeter Calorimeter {
  set ParticleInputArray TrackMerger/tracks 
  set TrackInputArray TrackMerger/tracks

  set TowerOutputArray towers
  set EFlowTrackOutputArray eflowTracks
  set EFlowTowerOutputArray eflowPhotons

  set IsEcal true

  set PixelSize 400  

  set EnergyMin 0
  set EnergySignificanceMin 0.0

  set SmearTowerCenter false

  ########################
  # TODO: Adapt granularity to one given by pixel detector
  # (in eta-phi)
  ########################
  set pi [expr {acos(-1)}]

  # lists of the edges of each tower in eta and phi
  # each list starts with the lower edge of the first tower
  # the list ends with the higher edged of the last tower

  # 0.012 rad towers up to eta = 2.5 (barrel)
  set PhiBins {}
  for {set i -256} {$i <= 256} {incr i} {
    add PhiBins [expr {$i * $pi/256.0}]
  } 

  # 0.01 unit in eta up to eta = 2.5 (barrel)
  for {set i -249} {$i <= 250} {incr i} {
    set eta [expr {$i * 0.01}]
    add EtaPhiBins $eta $PhiBins
  }

  # 0.025 rad between 2.5 and 6.0
  set PhiBins {}
  for {set i -128} {$i <= 128} {incr i} {
    add PhiBins [expr {$i * $pi/128.0}]
  }

  # 0.025 unit in eta between 2.5 and 6.0
  for {set i 0} {$i <= 140} {incr i} {
    set eta [expr { -6.00 + $i * 0.025}]
    add EtaPhiBins $eta $PhiBins
  }

  for {set i 0} {$i <= 139} {incr i} {
    set eta [expr { 2.525 + $i * 0.025}]
    add EtaPhiBins $eta $PhiBins
  }

  # default energy fractions {abs(PDG code)} {fraction of energy deposited in ECAL}

  add EnergyFraction {0} {1.0}
  # energy fractions for e, gamma and pi0
  add EnergyFraction {11} {1.0}
  add EnergyFraction {22} {1.0}
  add EnergyFraction {111} {1.0}
  # energy fractions for muon, neutrinos and neutralinos
  add EnergyFraction {12} {0.0}
  add EnergyFraction {13} {0.0}
  add EnergyFraction {14} {0.0}
  add EnergyFraction {16} {0.0}
  add EnergyFraction {1000022} {0.0}
  add EnergyFraction {1000023} {0.0}
  add EnergyFraction {1000025} {0.0}
  add EnergyFraction {1000035} {0.0}
  add EnergyFraction {1000045} {0.0}
  # energy fractions for K0short and Lambda
  # add EnergyFraction {310} {0.3}
  # add EnergyFraction {3122} {0.3}

  # set ECalResolutionFormula {resolution formula as a function of eta and energy}
  set ResolutionFormula {                     (abs(eta) <= 4.0) * sqrt(0.001) + \
                            (abs(eta) > 4.0 && abs(eta) <= 6.0) * sqrt(0.001)}


}

##################
# ROOT tree writer
##################

module TreeWriter TreeWriter {
  add Branch Delphes/allParticles Particle GenParticle

  add Branch PileUpMerger/vertices Vertex Vertex

  add Branch TrackEfficiency/tracks TruthTrack Track
  add Branch TrackSmearing/tracks Track Track

  # Something to play with 
  add Branch VertexFinder/vertices ClusteredVertices Vertex
  add Branch VertexFinder/tracks ClusteredTracks Track

  add Branch PrimaryBinFinder/vertices PrimaryBin Vertex
  add Branch VertexTrackAssociator/tracks AssociatedTracks Track

  # Then write a module to take the vertices and spit out the tracks from the highest pT vertex 
  # Need access to pointers inside vertex 
  # Then feed into Delphes JetFinder module 

  #add Branch GenJetFinder/jets GenJet Jet # WJF don't want GenJets? 

  add Branch TrackTruthJetFinder/jets TrackTruthJet Jet
  add Branch TrackJetFinder/jets TrackJet Jet

  # Idea to get density of tracks in the first layer of the tracker 
  add Branch Calorimeter/towers Tower Tower

  # if you want to add the pileup particles to the particles -- collection will become huge
  #add Branch PileUpMerger/stableParticles PileupParticle GenParticle 
}

