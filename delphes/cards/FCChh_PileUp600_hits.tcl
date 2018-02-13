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
  HitFinder50
  HitFinder40
  HitFinder30
  HitFinder20
  HitFinder10
  TrackEfficiency
  TrackSmearing

  NeutrinoFilter

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
  set MeanPileUp 600

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
  set InputArray PileupMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.532} {0.582} {0.632}
}

module HitFinder HitFinder40 {
  set InputArray PileupMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.542} {0.582} {0.622}
}

module HitFinder HitFinder30 {
  set InputArray PileupMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.552} {0.582} {0.612}
}

module HitFinder HitFinder20 {
  set InputArray PileupMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.562} {0.582} {0.602}
}

module HitFinder HitFinder10 {
  set InputArray PileupMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.572} {0.582} {0.592}
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


##################
# ROOT tree writer
##################

module TreeWriter TreeWriter {
  add Branch Delphes/allParticles Particle GenParticle

  add Branch PileUpMerger/vertices Vertex Vertex

  add Branch TrackEfficiency/tracks TruthTrack Track
  add Branch TrackSmearing/tracks Track Track

  add Branch HitFinder50/hits Hits50 Hit
  add Branch HitFinder40/hits Hits40 Hit
  add Branch HitFinder30/hits Hits30 Hit
  add Branch HitFinder20/hits Hits20 Hit
  add Branch HitFinder10/hits Hits10 Hit

}

