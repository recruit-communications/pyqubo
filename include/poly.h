#pragma once
#include <vector>
#include <csignal>
#include "coeff.h"
#include "prod.h"
#include "express.h"
#include "encoder.h"
#include "compiled_qubo.h"

using namespace std;

//typedef std::unordered_set<Base *, std::BaseHash, std::BaseEqual> BaseSet;
typedef std::unordered_map<Prod, CoeffPtr, std::ProdHash, std::ProdEqual> Terms;
//typedef std::unordered_set<string> VarSet;
typedef std::set<string> VarSet;
class Poly;

enum class PolyType
{
    POLY = 0,
    MONO = 1
};

class PolyBase {
public:
    virtual Terms get_terms() = 0;

    //virtual Poly *mul(Poly *other) = 0;
    //virtual unique_ptr<Poly> mul(unique_ptr<Poly>& other) = 0;

    virtual string to_string() = 0;

    virtual int size() const = 0;
    virtual PolyBase* copy() = 0;

    virtual PolyType get_poly_type() const = 0;

    //~Poly();
    virtual Poly* to_multiple_poly() = 0;

    CompiledQubo* compile_coeff();
    Poly* make_quadratic(Encoder* encoder, CoeffPtr strength);
    virtual ~PolyBase(){};
};


class Poly : public PolyBase {
public:
    Terms terms;

    virtual PolyType get_poly_type() const override {
        return PolyType::POLY;
    }

    Poly(){}

    Poly(Terms& _terms): terms(_terms){};

    Poly(shared_ptr<Spin> spin, Encoder* encoder){
        Prod spin_prod = Prod::create(encoder->encode(spin->label));
        Prod const_prod = Prod();
        terms[spin_prod] = make_shared<CoeffNum>(2.0);
        terms[const_prod] = make_shared<CoeffNum>(-1.0);
    }

    PolyBase* copy() override{
        return new Poly(this->terms);
    }

    bool operator==(const Poly mp) const{
        if(this->size() != mp.size()){
            return false;
        }else{
            bool match = true;
            for(auto it = mp.terms.begin(); it != mp.terms.end(); it++){
                auto result = this->terms.find(it->first);
                if(result == this->terms.end()){
                    return false;
                }else{
                    match &= result->second->equal_to(it->second);
                }
            }
            return match;
        }
    }

    void add_term(Prod prod, double coeff){
        CoeffPtr coeff_ptr = make_shared<CoeffNum>(coeff);
        add_term(prod, coeff_ptr);
    }

    void add_term(Prod prod, CoeffPtr coeff){
        auto result = terms.find(prod);
        if(result == terms.end()){
            terms[prod] = coeff;
        }else{
            terms[prod] = coeff->add(result->second);
        }
    }

    int size() const override {
        return this->terms.size();
    }

    Terms get_terms() override {
        return this->terms;
    }

    string to_string() override {
        string s = string() + "MultiplePoly(";
        int i = 0;
        for (Terms::iterator it = this->terms.begin(); it != this->terms.end(); it++) {
            Prod p = it->first;
            s += it->second->to_string() + "*" + p.to_string();
            if(this->terms.size()-1 != i) s += "+";
            i++;
        }
        s += ")";
        return s;
    }

    //unique_ptr<Poly> mul(unique_ptr<Poly>& other) override;

    Poly* to_multiple_poly() override {
        return this;
    }

    ~Poly(){};
};


class Mono : public PolyBase {
public:
    Prod prod = Prod();
    CoeffPtr coeff;

    int size() const override {
        return 1;
    }

    virtual PolyType get_poly_type() const override {
        return PolyType::MONO;
    }

    PolyBase* copy() override{
        CoeffPtr coeff = make_shared<CoeffNum>(1.0);
        return new Mono(prod, coeff);
    }

    Mono(Prod _prod, CoeffPtr _coeff):
        prod(_prod),
        coeff(_coeff){}

    Mono(shared_ptr<Num> exp) {
        this-> coeff = make_shared<CoeffNum>(exp->value);
    }

    Mono(shared_ptr<Placeholder> exp) {
        this-> coeff = make_shared<CoeffPlaceholder>(exp->label);
    }

    Mono(shared_ptr<Binary> exp, Encoder* encoder) {
        this-> prod = Prod::create(encoder->encode(exp));
        this-> coeff = make_shared<CoeffNum>(1.0);
    }

    Poly* to_multiple_poly() override {
        auto terms = get_terms();
        auto mp = new Poly(terms);
        return mp;
    }

    bool operator==(const Mono sp) const{
        return sp.prod == this->prod && sp.coeff->equal_to(this->coeff);
    }

    //unique_ptr<Poly> mul(unique_ptr<Poly>& other) override;

    string to_string() override {
        string s = string() + "SinglePoly([";
        s += this->prod.to_string();
        s += "], coeff=" + this->coeff->to_string() + ")";
        return s;
    }

    Terms get_terms() override {
        Terms terms;
        terms[this->get_prod()] = this->coeff;
        return terms;
    }

    Prod get_prod() {
        return this->prod;
    }

    CoeffPtr get_coeff() {
        return this->coeff;
    }
};

namespace poly{
    PolyBase* mul(PolyBase* left, PolyBase* right);
    void merge_poly(Poly* org_poly, PolyBase* poly);
}