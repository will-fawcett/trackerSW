#!/usr/bin/env python

'''
Script to generate config files for tkLayout, but including a triplet layer at a variable location in the outer tracker. 
Variables include
    - Layer of triplet in barrel
    - Spacing of triplet layer in barrel
    - Position of triplet in end-cap
    - Spacing of triplet in end-cap
'''

def main(tripletLayer):
    print 'hello world'
    print tripletLayer




from optparse import OptionParser
import sys
if __name__ == "__main__":
  parser = OptionParser()
  #parser.add_option("-j", "--jsonFile", action="store", type="string", help="Input JSON file")
  #parser.add_option("-o", "--outputDir", action="store", type="string", default=os.getcwd(), help="Output directory for plots")
  parser.add_option("-l", "--tripletLayer", action="store", type="int", help="Triplet layer in barrel, choose 1--6")
  #parser.add_option("-W", "--chartWidth", action="store", type="int", default = 300, help="width of each chart plot")
  #parser.add_option("-H", "--chartHeight", action="store", type="int", default = 300, help="height of each chart plot")
  #parser.add_option("-l", "--labelFormat", action="store", type="string", default="%perc", help="label format: %val for numbers, %perc for percentages")
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

  options, args = parser.parse_args()
  option_dict = dict( (k, v) for k, v in vars(options).iteritems() if v is not None)
  main(**option_dict)
