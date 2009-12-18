#include <string>
#include <vector>
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

  vector<Bus> buses;

  vector<Branch> branches;

  vector<Generator> generators;

  public:
    vector<Bus> connected_buses (void) {
      return buses;
    }
};
