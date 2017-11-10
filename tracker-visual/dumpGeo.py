import os
from Gaudi.Configuration import *
import sys

from Configurables import GeoSvc


myFileDir = "Detector/DetFCChhTrackerTkLayout/compact/"

if len(sys.argv) > 2:
    myFilePath = sys.argv[-1]
else:
    myFileName = "FCChh_v3.03_triplet.xml"
    myFileName = "FCChh_triplet_layer2_4cm.xml"
    myFileName = "FCCtriplet_1barrel20mm.xml"
    myFilePath = myFileDir+myFileName
print 'Will execute for ', myFilePath 

#geoservice = GeoSvc("GeoSvc", detectors=['file:../Detector/DetSensitive/tests/compact/Box_simpleTrackerSD.xml'], OutputLevel = DEBUG)
geoservice = GeoSvc("GeoSvc", detectors=['file:Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml','file:'+myFilePath], OutputLevel = DEBUG)

from Configurables import SimG4Svc
geantservice = SimG4Svc("SimG4Svc",
                        detector='SimG4DD4hepDetector',
                        physicslist="SimG4FtfpBert",
                        actions="SimG4FullSimActions")

#export_fname = "TestBox.gdml"
export_fname = myFilePath.split('/')[-1].replace('xml', 'gdml') 

# check if file exists and delete it:
if os.path.isfile(export_fname):
    os.remove(export_fname)

from Configurables import GeoToGdmlDumpSvc
geodumpservice = GeoToGdmlDumpSvc("GeoDump", gdml=export_fname)

from Configurables import ApplicationMgr
ApplicationMgr( TopAlg = [],
                EvtSel = 'NONE',
                EvtMax   = 1,
                # order is important, as GeoSvc is needed by SimG4Svc
                ExtSvc = [geoservice, geantservice, geodumpservice],
                OutputLevel=DEBUG
 )
