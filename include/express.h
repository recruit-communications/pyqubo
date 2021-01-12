#pragma once
#include <vector>
#include <stdio.h>
#include <string.h>
#include <encoder.h>
#include <linkedlist.h>
#include <functional>


using namespace std;
class Add;
class PolyBase;
class Expanded;
class AddStop;
class Base;
class Mul;
class Num;
class Placeholder;
class Model;
class CompiledQubo;
class Coeff;

using BasePtr = std::shared_ptr<Base>;
using AddPtr = std::shared_ptr<Add>;
using NumPtr = std::shared_ptr<Num>;
using MulPtr = std::shared_ptr<Mul>;
using CoeffPtr = std::shared_ptr<Coeff>;
using PlaceholderPtr = std::shared_ptr<Placeholder>;

enum class ExpressType
{
    BINARY = 0,
    SPIN = 1,
    NUM = 2,
    ADD = 3,
    MUL = 4,
    PLACEHOLDER = 5,
    SUBH = 6,
    WITH_PENALTY = 7,
    UDE = 8,
    CONSTRAINT = 9,
    POW = 10
};

class Base: public enable_shared_from_this<Base>{
protected:
    size_t hash_value;


public:
    virtual BasePtr add(BasePtr other);

    virtual BasePtr add(double other);

    virtual BasePtr sub(BasePtr other);

    virtual BasePtr sub(double other);

    virtual BasePtr pow(int exponent);

    virtual BasePtr rsub(double other);

    virtual BasePtr mul(BasePtr other);

    virtual BasePtr mul(double other);

    virtual BasePtr div(double other);

    virtual BasePtr neg();

    Model compile(double strength=2.0);

    Model compile(string placeholder_label);
    
    Model compile(CoeffPtr strength);

    virtual std::string to_string(bool with_symbol) = 0;

    virtual bool equal_to(BasePtr other) = 0;

    size_t hash() {
        return hash_value;
    }

    virtual ExpressType get_type() const = 0;

    virtual Expanded* expand(Encoder& encoder) = 0;

    virtual ~Base(){};
};

namespace std {
    struct BaseHash {
        size_t operator()(BasePtr p) const { return p->hash(); }
    };

    struct BaseEqual {
        bool operator()(BasePtr left, BasePtr right) const { return left->equal_to(right); }
    };
}

using AddList = LinkedList<shared_ptr<Base>>;

class Add : public Base{
public:
    AddList* node;

    Add() = default;

    shared_ptr<Base> add(shared_ptr<Base> other) override;

    Add(shared_ptr<Add> add, shared_ptr<Base> child):
        node(create_node(add, child)){}
    
    AddList* create_node(shared_ptr<Add> add, shared_ptr<Base> new_child){
        AddList* new_node = new AddList(new_child, add->node);
        return new_node;
    }

    Add(shared_ptr<Add> add_left, shared_ptr<Add> add_right):
        node(create_node(add_left, add_right)){}
    
    Add(shared_ptr<Base> child){
        this->node = new AddList(child);
    }

    Add(shared_ptr<Base> left, shared_ptr<Base> right){
        this->node = new AddList(left);
        this->node->next = new AddList(right);
    }

    Add(shared_ptr<Base> left, double right_num){
        BasePtr right = static_pointer_cast<Base>(make_shared<Num>(right_num));
        Add(left, right);
    }

    Add(double left_num, shared_ptr<Base> right){
        BasePtr left = static_pointer_cast<Base>(make_shared<Num>(left_num));
        Add(left, right);
    }

    ~Add(){}

    virtual ExpressType get_type() const override {
        return ExpressType::ADD;
    }

    string to_string(bool with_symbol) override {
        string s;
        if(with_symbol){
            s += "(";
        }else{
            s += "Add(";
        }
        AddList* next_node = this->node;
        while(next_node != nullptr){
            s += next_node->value->to_string(with_symbol);
            if(with_symbol){
                s += "+";
            }else{
                s += ",";
            }
            next_node = next_node->next;
        }
        s.pop_back();
        s += ")";
        return s;
    }

    bool equal_to(BasePtr other) override {

        if (other->get_type() == ExpressType::ADD) {
            auto other_casted = static_pointer_cast<Add>(other);
            AddList* this_node = this->node;
            AddList* other_node = other_casted->node;
            bool result = true;
            while(true){
                if(this_node == nullptr && other_node == nullptr){
                    break;
                }else if((this_node != nullptr && other_node == nullptr)
                    || (this_node == nullptr && other_node != nullptr)){
                    return false;
                }else{
                    if(!this_node->value->equal_to(other_node->value)) return false;
                }
                this_node = this_node->next;
                other_node = other_node->next;
            }
            return true;
        }else{
            return false;
        }
    }
    Expanded* expand(Encoder& encoder) override;
};


class Mul : public Base{
public:
    BasePtr left;
    BasePtr right;

    ~Mul(){
        this->left.reset();
        this->right.reset();
    }

    virtual ExpressType get_type() const override {
        return ExpressType::MUL;
    }

    Mul(BasePtr left, BasePtr right) {
        this->left = left;
        this->right = right;
        this->hash_value = left->hash() ^ (right->hash() << 1);
    }

    string to_string(bool with_symbol) override {
        if(with_symbol){
            return this->left->to_string(with_symbol) + "*" + this->right->to_string(with_symbol);
        }else{
            return string("Mul(") + this->left->to_string(with_symbol) + "," + this->right->to_string(with_symbol) + ")";
        }
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::MUL) {
            auto other_casted = static_pointer_cast<Mul>(other);
            return left->equal_to(other_casted->left) && right->equal_to(other_casted->right);
        } else {
            return false;
        }
    }
    Expanded* expand(Encoder& encoder) override;
};


class Binary : public Base{
public:
    std::string label;

    ~Binary(){
        //cout << "~Binary\n";
    }

    virtual ExpressType get_type() const override {
        return ExpressType::BINARY;
    }

    Binary(const std::string s) {
        this->label = s;
        this->hash_value = std::hash<std::string>{}(s);
    }

    std::string to_string(bool with_symbol) override {
        string s = string("Binary(") + label + ")";
        return s;
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::BINARY) {
            return this->label == static_pointer_cast<Binary>(other)->label;
        } else {
            return false;
        }
    }

    Expanded* expand(Encoder& encoder) override;
};


class Spin : public Base{
public:
    std::string label;

    ~Spin(){}

    virtual ExpressType get_type() const override {
        return ExpressType::SPIN;
    }

    Spin(const std::string s) {
        this->label = s;
        this->hash_value = std::hash<std::string>{}(s);
    }

    std::string to_string(bool with_symbol) override {
        string s = string("Spin(") + label + ")";
        return s;
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::SPIN) {
            return this->label == static_pointer_cast<Spin>(other)->label;
        } else {
            return false;
        }
    }

    Expanded* expand(Encoder& encoder) override;
};

class Num : public Base{
public:
    double value;

    virtual ExpressType get_type() const override {
        return ExpressType::NUM;
    }

    Num(double value) {
        this->value = value;
        this->hash_value = std::hash <double> {}(value);
    }

    std::string to_string(bool with_symbol) override {
        return string() + "Num(" + std::to_string(this->value) + ")";
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::NUM) {
            return this->value == static_pointer_cast<Num>(other)->value;
        } else {
            return false;
        }
    }
    Expanded* expand(Encoder& encoder) override;
};

class Placeholder : public Base{
public:
    string label;

    virtual ExpressType get_type() const override {
        return ExpressType::PLACEHOLDER;
    }

    Placeholder(string label) {
        this->label = label;
        this->hash_value = std::hash <string>{}(label);
    }

    ~Placeholder(){}

    std::string to_string(bool with_symbol) override {
        return string("Placeholder(") + this->label + ")";
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::PLACEHOLDER) {
            return this->label == static_pointer_cast<Placeholder>(other)->label;
        } else {
            return false;
        }
    }
    Expanded* expand(Encoder& encoder) override;
};

class Pow : public Base{
public:
    BasePtr hamiltonian;
    int exponent;

    ~Pow(){}

    virtual ExpressType get_type() const override {
        return ExpressType::POW;
    }

    Pow(
        BasePtr hamiltonian,
        int exponent
    ):
        hamiltonian(hamiltonian),
        exponent(exponent){
        if(exponent <= 0){
            throw std::runtime_error("`exponent` should be positive");
        }
    }

    std::string to_string(bool with_symbol) override {
        string s = string("Pow(") + this->hamiltonian->to_string(with_symbol)
            + "," + to_string(this->exponent) + ")";
        return s;
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::POW) {
            auto other_casted = static_pointer_cast<Pow>(other);
            return this->hamiltonian->equal_to(other_casted->hamiltonian) && this->exponent == other_casted->exponent;
        } else {
            return false;
        }
    }

    Expanded* expand(Encoder& encoder) override;
};



class WithPenalty: public Base{
public:
    BasePtr hamiltonian;
    BasePtr penalty;
    string label;
    WithPenalty(){}

    ~WithPenalty(){}

    WithPenalty(
        BasePtr hamiltonian,
        BasePtr penalty,
        string label
    ):
        hamiltonian(hamiltonian),
        penalty(penalty),
        label(label){}

    virtual ExpressType get_type() const override {
        return ExpressType::WITH_PENALTY;
    }

    std::string to_string(bool with_symbol) override {
        return string("WithPenalty(") + this->hamiltonian->to_string(with_symbol) + "," + penalty->to_string(with_symbol) + "," + label + ")";
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::WITH_PENALTY) {
            auto other_casted = static_pointer_cast<WithPenalty>(other);
            return hamiltonian->equal_to(other_casted->hamiltonian) && penalty->equal_to(other_casted->penalty);
        } else {
            return false;
        }
    }

    Expanded* expand(Encoder& encoder) override;
};

class UserDefinedExpress: public Base{
public:
    BasePtr hamiltonian;
    UserDefinedExpress(){}

    ~UserDefinedExpress(){}

    UserDefinedExpress(
        BasePtr hamiltonian
    ):
        hamiltonian(hamiltonian){}

    virtual ExpressType get_type() const override {
        return ExpressType::UDE;
    }

    std::string to_string(bool with_symbol) override {
        check_instance_variable();
        return "UserDefinedExpress(" + this->hamiltonian->to_string(with_symbol) + ")";
    }

    void check_instance_variable(){
        if(hamiltonian == nullptr){
            throw std::runtime_error("`hamiltonian` is not defined. Please define the `hamiltonian` in the constructor of your inherited class.");
        }
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::UDE) {
            auto other_casted = static_pointer_cast<UserDefinedExpress>(other);
            return hamiltonian->equal_to(other_casted->hamiltonian);
        } else {
            return false;
        }
    }

    Expanded* expand(Encoder& encoder) override;
};



class SubH: public Base{
public:
    string label;
    BasePtr hamiltonian;

    SubH(
        BasePtr hamiltonian,
        string label
    ):
        hamiltonian(hamiltonian),
        label(label){}

    ~SubH(){}

    virtual ExpressType get_type() const override {
        return ExpressType::SUBH;
    }

    std::string to_string(bool with_symbol) override {
        check_instance_variable();
        return string("SubH(") + this->hamiltonian->to_string(with_symbol) + ")";
    }

    void check_instance_variable(){
        if(hamiltonian == nullptr){
            throw std::runtime_error("`hamiltonian` is not defined. Please define the `hamiltonian` in the constructor of your inherited class.");
        }
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::SUBH) {
            auto other_casted = static_pointer_cast<SubH>(other);
            return label == other_casted->label && hamiltonian->equal_to(other_casted->hamiltonian);
        } else {
            return false;
        }
    }

    Expanded* expand(Encoder& encoder) override;
};

class Constraint: public Base{
public:
    string label;
    BasePtr hamiltonian;
    std::function<bool(double)> condition;

    Constraint(
        BasePtr hamiltonian,
        string label,
        std::function<bool(double)> _condition
    ):
        hamiltonian(hamiltonian),
        label(label),
        condition(_condition)
    {};

    ~Constraint(){}

    virtual ExpressType get_type() const override {
        return ExpressType::CONSTRAINT;
    }

    std::string to_string(bool with_symbol) override {
        return string("Constraint(label=") + label + "," + this->hamiltonian->to_string(with_symbol) + ")";
    }

    bool equal_to(BasePtr other) override {
        if (other->get_type() == ExpressType::CONSTRAINT) {
            auto other_casted = static_pointer_cast<Constraint>(other);
            return label == other_casted->label && hamiltonian->equal_to(other_casted->hamiltonian);
        } else {
            return false;
        }
    }
    
    Expanded* expand(Encoder& encoder) override;
};