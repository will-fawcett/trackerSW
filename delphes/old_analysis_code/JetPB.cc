#include "classes/JetPB.h"


//JetPB::JetPB(const Jet* i_Jet, const int i_nConstituentsTotal, const int i_nConstituentsInPB){
//theJet = i_jet; 
//nConstituentsTotal = i_nConstituentsTotal;
//nConstituentsInPB = i_nConstituentsInPB;
//}

float JetPB::trackFraction()
{
  return static_cast<float>(nConstituentsInPB)/static_cast<float>(nConstituentsTotal);
}

//JetPB::~JetPB(){
//};
