#pragma once
#include <memory>
#include <placeholderpoly.h>

class Coeff;

using namespace std;
using CoeffPtr = std::shared_ptr<Coeff>;
using PlPolyPtr = PHPolyBase*;

enum class CoeffType
{
    PLACEHOLDER = 0,
    NUM = 1,
    ADD = 2,
    MUL = 3
};

class Coeff: public enable_shared_from_this<Coeff>{
public:
    virtual CoeffPtr add(CoeffPtr other);
    virtual CoeffPtr add(double num);
    virtual CoeffPtr mul(CoeffPtr other);
    virtual CoeffPtr mul(double num);
    virtual string to_string() = 0;
    virtual bool equal_to(CoeffPtr other) const = 0;
    virtual CoeffType get_type() const = 0;
    virtual PlPolyPtr expand() = 0;
};

class CoeffPlaceholder: public Coeff{
public:
    string label;
    CoeffPlaceholder(string label){
        this->label = label;
    }

    string to_string() override {
        return string() + "CPlaceholder(" + label + ")";
    }

    CoeffType get_type() const override{
        return CoeffType::PLACEHOLDER;
    }

    PlPolyPtr expand() override {
        auto prod = CoeffProd(label, 1);
        auto poly = new PHMono(prod, 1.0);
        return poly;
    }
    
    bool equal_to(CoeffPtr other) const override {
        if(this->get_type() != other->get_type()){
            return false;
        }else{
            return this->label == static_pointer_cast<CoeffPlaceholder>(other)->label;
        }
    }
};

class CoeffNum: public Coeff{
public:
    double value;
    CoeffNum(double value){
        this->value = value;
    }
    CoeffPtr add(CoeffPtr other) override;
    CoeffPtr add(double num) override;
    CoeffPtr mul(CoeffPtr other) override;
    CoeffPtr mul(double num) override;
    string to_string() override {
        return string() + "CNum(" + std::to_string(value) + ")";
    }

    CoeffType get_type() const override{
        return CoeffType::NUM;
    }

    bool equal_to(CoeffPtr other) const override {
        if(this->get_type() != other->get_type()){
            return false;
        }else{
            return this->value == static_pointer_cast<CoeffNum>(other)->value;
        }
    }

    PlPolyPtr expand() override {
        auto prod = CoeffProd();
        auto poly = new PHMono(prod, value);
        return poly;
    }
};

class CoeffMul: public Coeff{
public:
    CoeffPtr left;
    CoeffPtr right;
    CoeffMul(CoeffPtr left, CoeffPtr right){
        this->left = left;
        this->right = right;
    }
    string to_string() override {
        return string() + "CMul(" + this->left->to_string() + "," + this->right->to_string() + ")";
    }

    CoeffType get_type() const override{
        return CoeffType::MUL;
    }

    bool equal_to(CoeffPtr other) const override {
        if(this->get_type() != other->get_type()){
            return false;
        }else{
            auto other_mp = static_pointer_cast<CoeffMul>(other);
            bool left_equal = this->left->equal_to(other_mp->left);
            bool right_equal = this->right->equal_to(other_mp->right);
            if(left_equal && right_equal){
                return true;
            }
            left_equal = this->right->equal_to(other_mp->left);
            right_equal = this->left->equal_to(other_mp->right);
            if(left_equal && right_equal){
                return true;
            }else{
                return false;
            }
        }
    }

    PlPolyPtr expand() override {
        auto poly_right = right->expand();
        auto poly_left = left->expand();
        auto new_poly = PlPolyOperation::mul(poly_right, poly_left);
        return new_poly;
    }  
};

class CoeffAdd: public Coeff{
public:
    CoeffPtr left;
    CoeffPtr right;
    CoeffAdd(CoeffPtr left, CoeffPtr right){
        this->left = left;
        this->right = right;
    }
    string to_string() override {
        return string() + "CAdd(" + this->left->to_string() + "," + this->right->to_string() + ")";
    }

    CoeffType get_type() const override{
        return CoeffType::ADD;
    }

    bool equal_to(CoeffPtr other) const override {
        if(this->get_type() != other->get_type()){
            return false;
        }else{
            bool left_equal = this->left->equal_to(static_pointer_cast<CoeffAdd>(other)->left);
            bool right_equal = this->right->equal_to(static_pointer_cast<CoeffAdd>(other)->right);
            return left_equal && right_equal;
        }
    }

    PlPolyPtr expand() override {
        auto poly_right = right->expand();
        auto poly_left = left->expand();
        auto new_poly = PlPolyOperation::add(poly_right, poly_left);
        return new_poly;
    }
};
