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

  HitFinder50
  HitFinder40
  HitFinder30
  HitFinder20
  HitFinder10

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
  set PileUpFile /atlas/data4/userdata/wfawcett/delphes/samples/pileup/MinBias_s10.pileup

  # average expected pile up
  set MeanPileUp 100

  # Set pileup distribution: 0 for poisson, 1 for uniform 
  set PileUpDistribution 0 

  # maximum spread in the beam direction in m
  set ZVertexSpread 0.25

  # maximum spread in time in s
  set TVertexSpread 800E-12

  # vertex smearing formula f(z,t) (z,t need to be respectively given in m,s) - {exp(-(t^2/160e-12^2/2))*exp(-(z^2/0.053^2/2))}
  set VertexDistributionFormula {exp(-(t^2/160e-12^2/2))*exp(-(z^2/0.053^2/2))}

}


module HitFinder HitFinder50 {
  set InputArray PileUpMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.532} {0.582} {0.632}
}

module HitFinder HitFinder40 {
  set InputArray PileUpMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.542} {0.582} {0.622}
}

module HitFinder HitFinder30 {
  set InputArray PileUpMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.552} {0.582} {0.612}
}

module HitFinder HitFinder20 {
  set InputArray PileUpMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.562} {0.582} {0.602}
}

module HitFinder HitFinder10 {
  set InputArray PileUpMerger/stableParticles
  set OutputArray hits
  set BarrelLength 2.250 
  set Bz 4.0
  add BarrelLayerRadii {0.572} {0.582} {0.592}
}


##################
# ROOT tree writer
##################

module TreeWriter TreeWriter {

  add Branch Delphes/allParticles Particle GenParticle
  add Branch PileUpMerger/vertices Vertex Vertex

  add Branch HitFinder50/hits Hits50 Hit
  add Branch HitFinder40/hits Hits40 Hit
  add Branch HitFinder30/hits Hits30 Hit
  add Branch HitFinder20/hits Hits20 Hit
  add Branch HitFinder10/hits Hits10 Hit

}
