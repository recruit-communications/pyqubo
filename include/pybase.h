#include <express.h>
#include <model.h>
using namespace std;

class PyBase : public Base {
public:
    using Base::Base;
    //using Base::add;

    BasePtr add(BasePtr other) override{
        PYBIND11_OVERLOAD(
                BasePtr,
                Base,
                add,
                other
        );
    };

    BasePtr add(double other) override{
        PYBIND11_OVERLOAD(
                BasePtr,
                Base,
                add,
                other
        );
    };

    BasePtr mul(BasePtr other) override{
        PYBIND11_OVERLOAD(
                BasePtr,
                Base,
                mul,
                other
        );
    };

    BasePtr mul(double other) override{
        PYBIND11_OVERLOAD(
                BasePtr,
                Base,
                mul,
                other
        );
    };
    

    std::string to_string(bool with_string) override {
        PYBIND11_OVERLOAD_PURE(
                std::string,
                Base,
                to_string
        );
    }

    virtual ExpressType get_type() const override {
        PYBIND11_OVERLOAD_PURE(
                ExpressType,
                Base,
                get_type
        );
    }

    Expanded* expand(Encoder& encoder) override {return NULL;}

    bool equal_to(BasePtr other) override {
        PYBIND11_OVERLOAD_PURE(
                bool,
                Base,
                equal_to
        );
    };
};
