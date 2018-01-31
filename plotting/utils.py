
#____________________________________________________________________________
def checkDir(dir, CHECK=False):
    import os
    ''' Create a directory if it does not exist,
        overwrite it otherwise
    '''
    # if output directory does not exist, then create it
    if not os.path.isdir(dir):
        print 'Creating directory', dir
        os.mkdir(dir)
        os.system('chmod g+w '+dir)
    # If it already exists, check if one wants to overwrite
    elif CHECK:
        print dir, "already exists... are you sure you want to overwrite it?",
        yesno = raw_input("y/n? ")
        if yesno != "y": sys.exit("Exiting, try again with a new name")
    else:
        print dir, "already exists and will be overwritten"
        print 'Dir will be', dir


#___________________________________________________________________________
def prepareLegend(position):
    import ROOT

    bottomLeft  = [0.15, 0.1, 0.35, 0.3]
    bottomRight = [0.7, 0.1, 0.9, 0.3]
    topRight    = [0.7, 0.7, 0.9, 0.9]
    topLeft     = [0.15, 0.7, 0.35, 0.9]

    if (position == "topLeft"):
        myPosition = topLeft
    if (position == "topRight"):
        myPosition = topRight
    if (position == "bottomLeft"):
        myPosition = bottomLeft
    if (position == "bottomRight"):
        myPosition = bottomRight

    return ROOT.TLegend(myPosition[0], myPosition[1], myPosition[2], myPosition[3])
