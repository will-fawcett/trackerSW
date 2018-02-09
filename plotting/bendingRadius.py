'''
Script to plot bending radius as a function of particle energy, according to the formula
r = gamma.m.v / e B 
  = p / e B 
  = sqrt(E^2 - m^2 c^4) / c e B 
  
  Note, bending radius in [m] is given by (approximately) 
  r = (5/6) p
  for p in [GeV/c] 
'''
import numpy as np  
import matplotlib.pyplot as plt  
import math
from math import sqrt

lightSpeed = 299792458 # m.s^-1 

elementaryCharge = 1.602 * 10**(-19) # C 
eV = 1.602 * 10**(-19) # J
GeV = eV * 10**9 # J 
GeVoc2 = GeV / lightSpeed**2

muon = 0.105 * (GeV / lightSpeed**2)
proton = 1 * (GeV / lightSpeed**2)

# length conversions (defined other way around?)
mm = 10**(-3)
um = 10**(-6) 

pt = '$p_{\mathrm{T}}$'
ptGeV = '$p_{\mathrm{T}}$ [GeV]'

def main():

    # Bending radius versus energy 
    #graph('( x**2 - 1)**0.5 / (1.2)', range(2, 1000), 'bendingRvE', 'E [GeV]', 'Bending Radius [m]')

    # bending radius versus transverse momentum (with nice lines)   (multiply by 100 for m->cm )
    #graph2('( 500.0*x / 6.0 ) ', range(0, 3), 'bendingRvP', 'pT [GeV]', 'Bending Radius [cm]') 

    # deviation as a function of bending radius  
    #graph('(x - np.sqrt(x*x - 0.25))', range(1, 10), 'deviation', 'Bending radius [m]', 'deviaton[$\mu$m]')

    # deviation as a function of momentum, triplet spacing 0.05 m (so total distance 0.1m) 
    #graph3('(x*(5.0/6.0) - np.sqrt( (x*(5.0/6.0))**2 - (0.1)**2 ))*10**6', range(40, 201), 'deviation100mm', ptGeV, 'Perpendicular Deviaton [$\mu$m]', 'Perpendicular deviation as a function of '+pt+' for longitudinal spacing of 100mm')
    
    #graph3('(x*(5.0/6.0) - np.sqrt( (x*(5.0/6.0))**2 - (0.05)**2 ))*10**6', range(1, 11), 'deviation50mm', ptGeV, 'Perpendicular Deviaton [$\mu$m]', 'Perpendicular deviation as a function of '+pt+' for longitudinal spacing of 50mm')
    # (above) previous range (1, 61)
    
    # spacing required for deviation of 40 um as a function of pT
    #graph( 'np.sqrt( (x*5.0/6.0)**2 - (x*5.0/6.0 - 40*10**(-6))**2 )*1000', range(1, 101), 'spacing', '$p_{\mathrm{T}}$ [GeV]', 'Spacing [mm]', 'Tracker layer spacing required for 40 $\mu$m track deviation as a function of $p_{\mathrm{T}}$')
    #graph( 'np.sqrt( (x*5.0/6.0)**2 - (x*5.0/6.0 - 40*10**(-6))**2 )*1000', range(1, 101), 'spacingInverse', 'Spacing [mm]', ptGeV, 'Tracker layer spacing required for 40 $\mu$m track deviation as a function of $p_{\mathrm{T}}$', True)

    # phi deviation of a particle emination from the origin and and intersecting barrel layers at 
    # radii r1 and r2 for the cases, as a function of transverse momentum [GeV]
    # Factor of 57.296 to convert radians to degrees
    # r1 = 0.532, r2 = 0.632 m (100 mm spacing) 
    # r1 = 0.532, r2 = 0.582 m (50 mm spacing)
    # r1 = 0.532, r2 = 0.542 m (10 mm spacing)
    plotRange = [float(x)/10 for x in range(6,60)]
    
    graph('(np.arccos( 0.532 / (2.0 * 1.199*x) ) - np.arccos( 0.632 / (2.0 * 1.199*x) ))*57.296', plotRange, 'phiDeviation', 'pT [GeV]', '$\Delta \phi$ [degrees]')
    graph('(np.arccos( 0.532 / (2.0 * 1.199*x) ) - np.arccos( 0.582 / (2.0 * 1.199*x) ))*57.296', plotRange, 'phiDeviation', 'pT [GeV]', '$\Delta \phi$ [degrees]')
    graph('(np.arccos( 0.532 / (2.0 * 1.199*x) ) - np.arccos( 0.542 / (2.0 * 1.199*x) ))*57.296', plotRange, 'phiDeviation', 'pT [GeV]', '$\Delta \phi$ [degrees]')


    #printRad(1*GeV/lightSpeed,  4.0)
    #printRad(2*GeV/lightSpeed,  4.0)
    #printRad(5*GeV/lightSpeed,  4.0)

    ##printDev(1*GeV/lightSpeed, 0.05)
    ##printDev(2*GeV/lightSpeed, 0.05)
    ##printDev(5*GeV/lightSpeed, 0.05)
    ##printDev(100*GeV/lightSpeed, 0.05)

    '''
    for i in range(140, 160):
        #printDev(i*GeV/lightSpeed, 0.05)
        printDev(i*GeV/lightSpeed, 0.10)
    '''

def printDev(p, spacing, B=4.0):
    bendingRadius = radius(p , B)
    dev = deviation(bendingRadius, spacing)/um
    print '{0} GeV/c track will deviate by {1} um in {2} m triplet (bending radius {3} m)'.format(p/(GeV/lightSpeed), dev, spacing, bendingRadius)

def deviation(r, d):
    '''Calculate the deviation of a particle according to 
    r - sqrt(r^2 - d^2) 
    Note that r and d must be in the same units
    Args:
        r: bending radius of the particle 
        d: transverse distance travelled by the partiel (in r direction)
    Returns:
        perpendicular deviation from original trajectory after travelling d
    '''
    return r - math.sqrt(r**2 - d**2) 


def printRad(p, B):
    bendingRadius = radius(p, B)
    print 'Particle with momentum {0:.3g} kg m/s ({1} GeV/c) has bending radius {2:.3g} m in field {3} T'.format(p, p/(GeV/lightSpeed), bendingRadius, B)



def radius(p, B):
    '''Calculate bending radius of particle with the following parameters, according to 
    r = p / cB 
    Args:
        p: momentum [kg m/s]
        B: magnetic field [T]
    Returns:
        bending radius [m] 
    '''
    radius = p / (elementaryCharge * B)
    return radius


def printRadiusEnergy(E, m, B):
    print 'Particle of mass {0} kg ({3} GeV/c^2) with energy {1} J ({4} GeV) has bending radius {2} m'.format(m, E, radiusEnergy(E, m, B), m/GeVoc2, E/GeV)



def radiusEnergy(E, m, B):
    # Bending radius of particle with charge e
    # Energy in J
    # Mass in kg
    # B field in Tesla

    r = math.sqrt( E**2 - m**2 * lightSpeed**4)  /  ( lightSpeed * elementaryCharge * B)
    return r



def gamma(v):
    '''Lorentz gamma factor
    '''
    g = 1.0 / math.sqrt(1 - (v**2 / lightSpeed**2) ) 
    return g 

def graph(formula, x_range, save, x_title='', y_title='', title='', inverse=False):  
    x = np.array(x_range)  
    y = eval(formula)
    if inverse:
        plt.plot(y, x)  
    else:
        plt.plot(x, y)  
    plt.title(title)
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    maxy = plt.gca().grid()
    plt.savefig(save+'.pdf')
    plt.savefig(save+'.eps')

def graph3(formula, x_range, save, x_title='', y_title='', title='', inverse=False):
    x = np.array(x_range)  
    y = eval(formula)
    if inverse:
        plt.plot(y, x) 
    else:
        plt.plot(x, y)  
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(title)
    maxy = plt.gca().grid()
    plt.axhline(y=40, ls='--')
    plt.savefig(save+'.pdf')
    

def graph2(formula, x_range, save, x_title='', y_title=''):  
    x = np.array(x_range)  
    y = eval(formula)
    plt.plot(x, y)  
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    maxy = plt.gca().get_ylim()[-1]
    miny = plt.gca().get_ylim()[0]
    maxx = plt.gca().get_xlim()[-1]
    minx = plt.gca().get_xlim()[0]
    print plt.gca().get_ylim()
    for i_yval in [0.52, 0.72, 0.93, 1.13, 1.34, 1.54]:
        yval = 0.5*i_yval * 100 # m -> cm
        xval = 6.0 * yval / 500.0 
        fracy = (yval+abs(miny)) / (maxy + abs(miny))
        fracx = (xval+abs(minx)) / (maxx + abs(minx))
        #print maxy, yval, fracy
        print yval, xval 
        plt.axvline(x=xval, ymax=fracy, ls='--')
        plt.axhline(y=yval, xmax=fracx, ls='--')
    plt.savefig(save+'.pdf')
    #plt.clear()


if __name__ == "__main__":
    main()
