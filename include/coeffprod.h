#pragma once
#include <vector>
#include <map>
#include <math.h>
#include <string>

using namespace std;
//using Products = vector<std::pair<std::string, int>>;
using Products = std::map<string, int>;


class CoeffProd{

    void mul(const std::string& var, double coeff) {
        auto result = products.find(var);
        if(result != products.end()){
            products[var] = products[var] + coeff;
        }else{
            products[var] = coeff;
        }
    }

public:

    Products products;
    size_t hash_value;

    CoeffProd() = default;
    CoeffProd(string label, int order){
        mul(label, order);
        set_hash();
    }

    double evaluate(map<string, double>& feed_dict){
        double out = 1.0;
        for(auto it = products.begin(); it != products.end(); it++){
            out *= pow(feed_dict.at(it->first), it->second);
        }
        return out;
    }

    CoeffProd(Products& _products): products(_products){
        set_hash();
    }

    bool operator==(const CoeffProd& other) const {
        if(other.products.size() != this->products.size()){
            return false;
        }
        if(this->hash_value != other.hash_value){
            return false;
        }
        bool match = true;
        auto it_this = this->products.begin();
        auto it_other = other.products.begin();
        while(it_this != this->products.end()){
            match &= (it_this->first == it_other->first && it_this->second == it_other->second);
            it_this++;
            it_other++;
        }
        return match;
    }

    void set_hash(){
        size_t seed = 0;
        for(auto it = products.begin(); it != products.end(); it++){
            seed = seed ^ std::hash<string>{}(it->first) ^ std::hash<int>{}(it->second) * 13;
        }
        this->hash_value = seed;
    }

    bool operator!=(const CoeffProd& other) const {
        return !((*this)==(other));
    }

    int size(){
        return this->products.size();
    }

    CoeffProd mul(CoeffProd& other){
        CoeffProd new_coeff_prod = *this;
        for(auto it = other.products.begin(); it != other.products.end(); it++){
            new_coeff_prod.mul(it->first, it->second);
        }
        new_coeff_prod.set_hash();
        return new_coeff_prod;
    }

    string to_string() const {
        std::string out = std::string() + "CoeffProd(";
        int i = 0;
        for(auto it = products.begin(); it != products.end(); it++){
            out += it->first + ":" + std::to_string(it->second);
            if(i != products.size()-1){
                out += ",";
            }
            i++;
        }
        out += ")";
        return out;
    }
};

namespace std {
    struct CoeffProdHash {
        size_t operator()(const CoeffProd& p) const { return p.hash_value; }
    };
};
