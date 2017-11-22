'''
Script to plot bending radius as a function of particle energy, according to the formula
r = gamma.m.v / e B 
'''

lightSpeed = 299792458 # m.s^-1 

def gamma(v):
    '''Lorentz gamma factor
    '''
    g = 1.0 / math.sqrt(1 - (v**2 / lightSpeed**2) ) 
    return g 

import numpy as np  
import matplotlib.pyplot as plt  
def graph(formula, x_range, x_title='', y_title=''):  
    x = np.array(x_range)  
    y = eval(formula)
    plt.plot(x, y)  
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.show()

def main():

    #graph('x**3+2*x-4', range(-10, 11))

    #graph('( x**2 - 10**18 )**0.5 / ( 12 * 10**8)', range(10**9, 10* 10**9))
    graph('( x**2 - 1)**0.5 / (1.2)', range(2, 1000), 'E [GeV]', 'Bending Radius [m]')
    




if __name__ == "__main__":
    main()






