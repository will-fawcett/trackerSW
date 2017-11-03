from ROOT import * 
#import ROOT


def printPrimitiveNames(tobject):

    primList = tobject.GetListOfPrimitives()
    print 'TObject of type: {0}, and name: {1}, has {2} primitives'.format(type(tobject), tobject.GetName(), len(primList))
    for x in primList:
        print '\t', x


def main():
    

    # open root file
    f = TFile.Open("run/results_FCCtriplet_1barrel20mm_1EC20mm/ctauRes_triplet_noMS_P000.root")
    f.ls()
    #printPrimitiveNames(f)

    can = f.Get("ctauRes_triplet_noMS_P000")
    printPrimitiveNames(can)


if __name__ == "__main__":
  main()
