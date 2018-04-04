#!/usr/bin/python
'''
Script to parse the data rate HTML files
'''
import json
from glob import glob


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def main(verbose):

    #layer = {
            #1 : [532.0, 

    files = glob("*.html")
    print files

    for fName in files: 

        ifile = open(fName, 'r')
        dataDict = {}
        for line in ifile:
            if line[0]=='>':

                info = line.split(':')

                what = info[0].strip()
                data = info[1].replace('</td> <td>', ',').replace('</td> </tr><tr><td',',').replace('</th> <th>', ',').split(',')
                data = [float(x) for x in data if is_number(x)]

                print what, '\t', data
                dataDict[what.replace('>','').replace('</b','')] = data

        print dataDict

        with open(fName.replace('html','json'), 'w') as fp:
            json.dump(dataDict, fp, sort_keys=True, indent=2)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Turn on verbose messages", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    main(verbose)


