#ifndef JetPB_h
#define JetPB_h

#include "classes/DelphesClasses.h"

class JetPB
{
  private:
    Jet* theJet;
    int nConstituentsTotal;
    int nConstituentsInPB;

  public:

    // Constructor
    JetPB( Jet* i_jet,  int i_nConstituentsTotal,  int i_nConstituentsInPB){
       theJet = i_jet; 
       nConstituentsTotal = i_nConstituentsTotal;
       nConstituentsInPB = i_nConstituentsInPB;
    }

    /*void setParameters(TLorentzVector, int, int);*/
    float trackFraction();

    // Destructor
    ~JetPB();

};


#endif // JetPB_h
