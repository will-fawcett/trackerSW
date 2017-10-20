"""
Quick script to dump FCCSW tracker validation data to plaintext spacepoints.
Requires podio, fcc-edm in pythonpath and ld-library-path.
"""


from EventStore import EventStore
import numpy as np
import sys

filename = sys.argv[1]
basefilename = filename.replace(".root", "")
events = EventStore([filename])
print 'number of events: ', len(events)
pos_b = []
ids_b = []
pos_e = []
ids_e = []
barrel_ids = []
for i, store in enumerate(events):
      if i > 100000:
        break
      clusters = store.get('positionedHits')
      #print clusters    
      for c in clusters:
          cor = c.position()
          if (c.cellId() % 32) == 0 and (c.cellId() / 32) %32 == 1 :
            
              pos_b.append([cor.x, cor.y, cor.z])
              ids_b.append([c.bits(), c.cellId()])
          print c.cellId() % 32, np.sqrt(cor.x**2 + cor.y**2)
          #else:
          #  pos_e.append([cor.x, cor.y, cor.z])
          #  ids_e.append([c.bits(), c.cellId()])
pos_e = np.array(pos_e)
ids_e = np.array(ids_e)
pos_b = np.array(pos_b)
ids_b = np.array(ids_b)
print "number of endcap hits: ", len(pos_e)
print "number of barrel hits: ", len(pos_b)
np.savetxt(basefilename + 'hit_positions_e.dat', pos_e)
np.savetxt(basefilename + 'hit_ids_e.dat', ids_e, fmt="%i")
np.savetxt(basefilename + 'hit_positions_b.dat', pos_b)
np.savetxt(basefilename + 'hit_ids_b.dat', ids_b, fmt="%i")
