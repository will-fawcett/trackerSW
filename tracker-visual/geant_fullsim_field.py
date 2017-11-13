# WJF add: parse args
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--geo', type=str, default=None, help='specify compact file for the geometry')
args, _ = parser.parse_known_args()




from Gaudi.Configuration import *

# Data service
from Configurables import FCCDataSvc
podioevent = FCCDataSvc("EventDataSvc")


from Configurables import GenAlg, MomentumRangeParticleGun
## Particle Gun using MomentumRangeParticleGun tool and FlatSmearVertex
# MomentumRangeParticleGun generates particles of given type(s) within given momentum, phi and theta range
# FlatSmearVertex smears the vertex with uniform distribution

pgun_tool = MomentumRangeParticleGun(PdgCodes=[13, -13])
pgun_tool.ThetaMin = 0.0
pgun_tool.ThetaMax = 2*3.14 
gen = GenAlg("ParticleGun", SignalProvider=pgun_tool, VertexSmearingTool="FlatSmearVertex")
gen.hepmc.Path = "hepmc"

from Configurables import Gaudi__ParticlePropertySvc
## Particle service
# list of possible particles is defined in ParticlePropertiesFile
ppservice = Gaudi__ParticlePropertySvc("ParticlePropertySvc", ParticlePropertiesFile="Generation/data/ParticleTable.txt")

# DD4hep geometry service
# Parses the given xml file
from Configurables import GeoSvc

# WJF edits
pathToXML = 'file:Detector/DetFCChhTrackerTkLayout/compact/'
myFile = "FCChh_triplet_layer2_4cm.xml"
myFile = "FCCtriplet_4barrel35mm.xml"
myFile = "FCCtriplet_1barrel30mm.xml"

myFilePath =pathToXML 
myFilePath = 'file:'+args.geo


geoservice = GeoSvc("GeoSvc", detectors=['file:Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
  myFilePath
  ],
                    OutputLevel = DEBUG)

from Configurables import HepMCToEDMConverter
## Reads an HepMC::GenEvent from the data service and writes a collection of EDM Particles
hepmc_converter = HepMCToEDMConverter("Converter")
hepmc_converter.hepmc.Path="hepmc"
hepmc_converter.genparticles.Path="allGenParticles"
hepmc_converter.genvertices.Path="allGenVertices"

# Geant4 service
# Configures the Geant simulation: geometry, physics list and user actions
from Configurables import SimG4Svc
# giving the names of tools will initialize the tools of that type
geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist="SimG4FtfpBert", actions="SimG4FullSimActions")

from Configurables import SimG4ConstantMagneticFieldTool
field = SimG4ConstantMagneticFieldTool("SimG4ConstantMagneticFieldTool", FieldOn=True, IntegratorStepper="ClassicalRK4")

# Geant4 algorithm
# Translates EDM to G4Event, passes the event to G4, writes out outputs via tools
from Configurables import SimG4Alg, SimG4SaveTrackerHits, SimG4PrimariesFromEdmTool
# first, create a tool that saves the tracker hits
# Name of that tool in GAUDI is "XX/YY" where XX is the tool class name ("SimG4SaveTrackerHits")
# and YY is the given name ("saveTrackerHits")
savetrackertool = SimG4SaveTrackerHits("saveTrackerHits", readoutNames = ["TrackerBarrelReadout", "TrackerEndcapReadout"])
savetrackertool.positionedTrackHits.Path = "positionedHits"
savetrackertool.trackHits.Path = "hits"
# next, create the G4 algorithm, giving the list of names of tools ("XX/YY")
particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
particle_converter.genParticles.Path = "allGenParticles"
geantsim = SimG4Alg("SimG4Alg",
                    outputs = ["SimG4SaveTrackerHits/saveTrackerHits"],
                    eventProvider=particle_converter)

# PODIO algorithm
from Configurables import PodioOutput
out = PodioOutput("out",
                   OutputLevel=DEBUG)
out.outputCommands = ["keep *"]
#out.filename = "tracker_with_field.root"
out.filename = myFilePath.split('/')[-1].replace('.xml','_hits.root') 

# ApplicationMgr
from Configurables import ApplicationMgr
ApplicationMgr( TopAlg = [gen, hepmc_converter, geantsim, out],
                EvtSel = 'NONE',
                EvtMax   = 5000,
                # order is important, as GeoSvc is needed by SimG4Svc
                ExtSvc = [ppservice, podioevent, geoservice, geantservice],
                OutputLevel=DEBUG
 )
