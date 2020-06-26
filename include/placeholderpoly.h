#pragma once
#include <stdio.h>
#include <coeffprod.h>
#include <iostream>
#include <unordered_map>

using namespace std;


using CoeffTerms = std::unordered_map<CoeffProd, double, std::CoeffProdHash>;

class PHPolyBase;
class PHPoly;
class PHMono;

enum class PHPolyType{
    POLY = 0,
    MONO = 1
};

class PHPolyBase{
public:
    //virtual bool operator==(const PlPoly& other) const = 0;
    virtual double evaluate(map<string, double> feed_dict) = 0;
    virtual PHPolyType get_type() const = 0;
    virtual size_t size() const = 0;
    virtual string to_string() const = 0;
    virtual bool equal_to(PHPolyBase* other) const = 0;
    virtual ~PHPolyBase(){};
};

class PHPoly: public PHPolyBase{
public:
    CoeffTerms terms;

    PHPoly() = default;

    PHPoly(CoeffProd prod, double coeff){
        terms[prod] = coeff;
    }

    PHPolyType get_type() const override {
        return PHPolyType::POLY;
    }

    double evaluate(map<string, double> feed_dict) override {
        double sum = 0.0;
        for(auto it = terms.begin(); it != terms.end(); it++){
            CoeffProd prod = it->first;
            sum += prod.evaluate(feed_dict) * it->second;
        }
        return sum;
    }

    size_t size() const override{
        return terms.size();
    }

    bool equal_to(PHPolyBase* other) const override{
        if(other->get_type() == PHPolyType::MONO){
            return false;
        }else{
            PHPoly* casted(static_cast<PHPoly*>(other));
            if(casted->size() != this->size()){
                return false;
            }else{
                bool match = true;
                for(auto it = this->terms.begin(); it != this->terms.end(); it++){
                    auto found = casted->terms.find(it->first);
                    if(found != casted->terms.end()){
                        match &= (it->second == found->second);
                    }
                }
                return match;
            }
        }
    }

    string to_string() const override {
        string out = string() + "PlMultPoly(";
        for(auto it = terms.begin(); it != terms.end(); it++){
            out += it->first.to_string() + ":" + std::to_string(it->second) + ",";
        }
        out += ")";
        return out;
    }

    void add(CoeffProd prod, double coeff){
        auto match = terms.find(prod);
        if(match != terms.end()){
            terms[prod] += coeff;
        }else{
            terms[prod] = coeff;
        }
    }

    ~PHPoly(){};
};

class PHMono: public PHPolyBase{
public:
    CoeffProd coeff_prod;
    double coeff;

    PHMono(CoeffProd _coeff_prod, double _coeff):
        coeff_prod(_coeff_prod), coeff(_coeff){}

    PHPolyType get_type() const override {
        return PHPolyType::MONO;
    }

    size_t size() const override{
        return 1;
    }

    double evaluate(map<string, double> feed_dict) override {
        return coeff_prod.evaluate(feed_dict) * coeff;
    }

    bool equal_to(PHPolyBase* other) const override{
        if(other->get_type() == PHPolyType::POLY){
            return false;
        }else{
            PHMono* casted(static_cast<PHMono*>(other));
            return casted->coeff_prod == this->coeff_prod && casted->coeff == this->coeff;
        }
    }

    string to_string() const override {
        return string("PlMonoPoly(") + std::to_string(coeff) + "*" + coeff_prod.to_string() + ")";
    }
    ~PHMono(){};
};

namespace PlPolyOperation {
    PHPolyBase* mul(PHPolyBase* left, PHPolyBase* right);
    PHPolyBase* add(PHPolyBase* left, PHPolyBase* right);
}