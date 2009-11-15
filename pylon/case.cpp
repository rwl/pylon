#include <string>
using namespace std;

struct Named {
  string name;
};

Named::Named () {
  name = "named";
}

Named::Named (string n) {
  name = n;
}

Named::~Named () {
  delete name;
}

struct Case: public Named {
  float base_mva;
  
  Bus buses [];
  
  Branch branches [];
  
  public:
    Bus [] connected_buses (void) {
      return buses;
    }
};