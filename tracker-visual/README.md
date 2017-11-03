# tracker-visual
Scripts to visualise tracker layout

# Dependencies
These scripts require the FCCSW (FCC software) to be installed, see https://github.com/HEP-FCC/FCCSW as well as matplotlib.

# Bits ... 
To select a layer, one must use the hard-coded ID number from tkLayout. 
For example, to select the layer with ID=1 use the following logic.
```
(c.cellId() % 32) == 0 and (c.cellId() / 32) %32 == 1
```
Note the 32 is there because the ID is stored in a 5-bit number, 2^5=32. 
