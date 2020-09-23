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
typedef std::pair<Prod, CoeffPtr> TermsPair;
class Poly;

enum class PolyType
{
    POLY = 0,
    MONO = 1
};

class PolyBase {
public:
    virtual Terms* get_terms() = 0;

    virtual string to_string() = 0;

    virtual bool equal_to(PolyBase* poly) = 0;

    virtual int size() const = 0;

    virtual PolyBase* copy() = 0;

    virtual PolyType get_poly_type() const = 0;

    virtual Poly* to_multiple_poly() = 0;

    CompiledQubo* compile_coeff();
    Poly* make_quadratic(Encoder& encoder, CoeffPtr strength);
    virtual ~PolyBase(){};
};


class Poly : public PolyBase {
private:
    Poly(const Poly &poly);
    Poly &operator=(const Poly &poly);

public:
    Terms* terms = new Terms();

    virtual PolyType get_poly_type() const override {
        return PolyType::POLY;
    }

    ~Poly(){
        delete terms;
    };

    Poly(){}

    Poly(Terms* _terms): terms(_terms){};

    Poly(shared_ptr<Spin> spin, Encoder& encoder){
        Prod spin_prod = Prod::create(encoder.encode(spin->label));
        Prod const_prod = Prod();
        terms->insert(TermsPair{spin_prod, make_shared<CoeffNum>(2.0)});
        terms->insert(TermsPair{const_prod, make_shared<CoeffNum>(-1.0)});
    }

    PolyBase* copy() override{
        Terms* new_terms = new Terms();
        for (Terms::iterator it = this->terms->begin(); it != this->terms->end(); it++) {
            Prod p = it->first;
            new_terms->insert(TermsPair{it->first, it->second});
        }
        return new Poly(new_terms);
    }

    bool equal_to(PolyBase* poly_base) override {
        if(poly_base->get_poly_type() != PolyType::POLY){
            return false;
        }else{
            auto poly = (Poly*)poly_base;
            if(this->size() != poly->size()){
                return false;
            }else{
                bool match = true;
                for(auto it = poly->terms->begin(); it != poly->terms->end(); it++){
                    auto result = this->terms->find(it->first);
                    if(result == this->terms->end()){
                        return false;
                    }else{
                        match &= result->second->equal_to(it->second);
                    }
                }
                return match;
            }
        }
    }

    void add_term(Prod prod, double coeff){
        CoeffPtr coeff_ptr = make_shared<CoeffNum>(coeff);
        add_term(prod, coeff_ptr);
    }

    void add_term(Prod prod, CoeffPtr coeff){
        auto result = terms->find(prod);
        if(result == terms->end()){
            terms->insert(TermsPair{prod, coeff});
        }else{
            result->second = coeff->add(result->second);
        }
    }

    int size() const override {
        return this->terms->size();
    }

    Terms* get_terms() override {
        return this->terms;
    }

    string to_string() override {
        string s = string() + "MultiplePoly(";
        int i = 0;
        for (Terms::iterator it = this->terms->begin(); it != this->terms->end(); it++) {
            Prod p = it->first;
            s += it->second->to_string() + "*" + p.to_string();
            if(this->terms->size()-1 != i) s += "+";
            i++;
        }
        s += ")";
        return s;
    }

    Poly* to_multiple_poly() override {
        return this;
    }
};


class Mono : public PolyBase {
private:
    Mono(const Mono &poly);
    Mono &operator=(const Mono &poly);

public:
    Prod prod = Prod();
    CoeffPtr coeff;

    int size() const override {
        return 1;
    }

    ~Mono(){}

    virtual PolyType get_poly_type() const override {
        return PolyType::MONO;
    }

    PolyBase* copy() override{
        CoeffPtr coeff = make_shared<CoeffNum>(1.0);
        Prod new_prod = Prod();
        return new Mono(new_prod, coeff);
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

    Mono(shared_ptr<Binary> exp, Encoder& encoder) {
        this-> prod = Prod::create(encoder.encode(exp));
        this-> coeff = make_shared<CoeffNum>(1.0);
    }

    Poly* to_multiple_poly() override {
        auto terms = get_terms();
        auto mp = new Poly(terms);
        return mp;
    }

    bool equal_to(PolyBase* poly_base) override {
        if(poly_base->get_poly_type() != PolyType::MONO){
            return false;
        }else{
            auto mono = (Mono*)poly_base;
            return mono->prod == this->prod && mono->coeff->equal_to(this->coeff);
        }
    }

    string to_string() override {
        string s = string() + "SinglePoly([";
        s += this->prod.to_string();
        s += "], coeff=" + this->coeff->to_string() + ")";
        return s;
    }

    Terms* get_terms() override {
        Terms* terms = new Terms();
        terms->insert(TermsPair{this->get_prod(), this->coeff});
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
    PolyBase* pow(PolyBase* poly, int exponent);
    void merge_poly(Poly* org_poly, PolyBase* poly);
}
