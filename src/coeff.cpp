#include <coeff.h>

using namespace std;

CoeffPtr Coeff::add(CoeffPtr other) {
    CoeffPtr this_ptr = shared_from_this();
    auto added = make_shared<CoeffAdd>(this_ptr, other);
    return added;
}

CoeffPtr Coeff::add(double num) {
    CoeffPtr this_ptr = shared_from_this();
    CoeffPtr num_coeff = make_shared<CoeffNum>(num);
    auto added = make_shared<CoeffAdd>(this_ptr, num_coeff);
    return added;
}

CoeffPtr Coeff::mul(CoeffPtr other) {
    CoeffPtr this_ptr = shared_from_this();
    auto multiplied = make_shared<CoeffMul>(this_ptr, other);
    return multiplied;
}

CoeffPtr Coeff::mul(double num) {
    CoeffPtr this_ptr = shared_from_this();
    CoeffPtr num_coeff = make_shared<CoeffNum>(num);
    auto multiplied = make_shared<CoeffMul>(this_ptr, num_coeff);
    return multiplied;
}

CoeffPtr CoeffNum::add(CoeffPtr other) {
    if (other->get_type() == CoeffType::NUM) {
        return make_shared<CoeffNum>(static_pointer_cast<CoeffNum>(other)->value + this->value);
    } else {
        auto this_ptr = static_pointer_cast<CoeffNum>(shared_from_this());
        return make_shared<CoeffAdd>(this_ptr, other);
    }
}

CoeffPtr CoeffNum::add(double num) {
    return make_shared<CoeffNum>(this->value + num);
}

CoeffPtr CoeffNum::mul(CoeffPtr other) {
    if (other->get_type() == CoeffType::NUM) {
        return make_shared<CoeffNum>((static_pointer_cast<CoeffNum>(other))->value * this->value);
    } else {
        auto this_ptr = static_pointer_cast<CoeffNum>(shared_from_this());
        return make_shared<CoeffMul>(this_ptr, other);
    }
}

CoeffPtr CoeffNum::mul(double num) {
    return make_shared<CoeffNum>(this->value * num);
}