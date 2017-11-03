from rootpy.io import root_open
import ROOT
from ROOT import gStyle

ROOT.gROOT.SetBatch(1)

# Optional Style, using FCCStyle from FCCSW
#from plotstyle import FCCStyle
#FCCStyle.initialize()
gStyle.SetOptStat(11)
gStyle.SetNdivisions(405)

import sys

f = root_open(sys.argv[1])

nEvents = f.events.GetEntries()
nEventStr = "NEvents: " + str(f.events.GetEntries())

cv = ROOT.TCanvas()

##########################################################################################################################

h = f.events.Draw("positionedHits.position.z:sqrt(pow(positionedHits.position.x,2) + pow(positionedHits.position.y,2))")
h.SetLineWidth(0)
h.GetXaxis().SetTitle("Z")
h.GetYaxis().SetTitle("R")

cv.Print("Hits_RZ.png")

print type(h)

#h2 = f.events.Draw("positionedHits.position.x:positionedHits.position.y", "0 < abs(positionedHits.position.z) < 5")
h2 = f.events.Draw("positionedHits.position.x:positionedHits.position.y")
print type(h2)

#h2.SetLineWidth(0)
h2.GetXaxis().SetTitle("X")
h2.GetYaxis().SetTitle("Y")
h2.SetMarkerSize(0.01)

cv.Print("Hits_XY.png")
