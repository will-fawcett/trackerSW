class fourVec
{
  private:
    float m_Pt;
    float m_Rapidity;
    float m_Phi;
  public:
    threeVec();
    void SetPtEtaPhi(float pt, float eta, float phi){
      m_Pt=pt;
      m_Rapidity=eta;
      m_Phi=phi;
    }
    float Pt(){return m_Pt;}
    float Rapidity(){return m_Rapidity;}
    float Eta(){return m_Rapidity;}
    float Phi(){return m_Phi;}
    ~threeVec();
};


class vector4 : public vector3
{
  protected: //might need to override << operator here to printout 4-vector.
      double ct, x, y, z; // x,y,z already inherited?

  public:
      // Default constructor
      vector4(){ct=x=y=z=0;}
      //paramitarised constructor(s)
      vector4(double ctin, double xin, double yin, double zin){ct=ctin; x=xin; y=yin; z=zin;}
      vector4(double ctin, vector3 &vec3){ct=ctin;} //SOMETHING!!!! }
      // Destructor
      ~vector4(){}

      //Function to print out 4-vector (again overriding may be needed)
      void show() const {cout<<"("<<ct<<","<<x<<","<<y<<","<<z<<")"<<endl;}
      };

class vector3
{
  friend ostream & operator<<(ostream &os, const vector3 &vec3)
  {
    os<<"("<<vec3.x<<","<<vec3.y<<","<<vec3.z<<")"<<endl;
    return os;

  }

  protected:
  double x,y,z;

  public:
  //Default constructor
  vector3(){x=y=z=0;}
  // Paramitarised constructor
  vector3(double xin, double yin, double zin){x=xin; y=yin= z=zin;}
  // Destructor
  ~vector3(){cout<<"Destroying 3 vector object"<<endl;}

  // Access functions
  void setx(double xin) {x=xin;}
  void sety(double yin) {y=yin;}
  void setz(double zin) {z=zin;}

  double getx() const {return x;}
  double gety() const {return y;}
  double getz() const {return z;}

  // Function to print out vector (redundant with friend)
  void show() const {cout<<"("<<x<<","<<y<<","<<z<<")"<<endl;}

  // Function to add scalar to each component
  void addscalar(double s) {x+=s; y=+s; z+=s;}

  // Function to overload + for vector sum
  vector3 operator+(const vector3 &vec3)
  {
    vector3 temp(x+vec3.getx(), y+vec3.gety(), z+vec3.getz());
    return temp;
  }

  // Function to overload * for dot product
  double operator*(vector3 &vec3)
  {
    double dot(x*vec3.getx() + y*vec3.gety() + z*vec3.getz());
    return dot;
  }

};

