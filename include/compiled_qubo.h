#pragma once
#include <vector>
#include <poly.h>
#include <prod.h>
#include <binary_quadratic_model.hpp>


using namespace std;
using CompiledTerms = vector<std::pair<Prod, PHPolyBase*>>;

class CompiledQubo{
public:
    CompiledTerms terms;
    CompiledQubo() = default;
    CompiledQubo(CompiledTerms terms): terms(terms){};

    ~CompiledQubo(){}

    string to_string() {
        string s = string() + "CompiledQubo(";
        int i = 0;
        for (auto it = this->terms.begin(); it != this->terms.end(); it++) {
            auto p = it->first;
            s += it->second->to_string() + "*" + p.to_string();
            if(this->terms.size()-1 != i) s += "+";
            i++;
        }
        s += ")";
        return s;
    }

    bool equal_to(CompiledQubo* other){
        if(this->terms.size() != other->terms.size()){
            return false;
        }else{
            for(int i=0; i < terms.size(); i++){
                Prod& this_prod = this->terms[i].first;
                Prod& other_prod = other->terms[i].first;
                PHPolyBase* this_pl_poly = this->terms[i].second;
                PHPolyBase* other_pl_poly = other->terms[i].second;
                if(!this_prod.equal_to(other_prod) && this_pl_poly->equal_to(other_pl_poly)){
                    return false;
                }
            }
            return true;
        }
    }


    BinaryQuadraticModel<string> evaluate(map<string, double> feed_dict, Encoder& encoder){
        Linear<string> linear;
        Quadratic<string> quadratic;
        double offset = 0.0;
        for (auto it = this->terms.begin(); it != this->terms.end(); it++) {
            if(it->first.length == 2){
                auto var_it = it->first.prodset.begin();
                string i = encoder.decode(*var_it-1);
                var_it++;
                string j = encoder.decode(*var_it-1);
                quadratic[std::make_pair(i, j)] = it->second->evaluate(feed_dict);
            }else if(it->first.length == 1){
                auto var_it = it->first.prodset.begin();
                string i = encoder.decode(*var_it-1);
                linear[i] = it->second->evaluate(feed_dict);
            }else if(it->first.length == 0){
                offset = it->second->evaluate(feed_dict);
            }else{
                throw std::runtime_error("QUBO was not created correctly. Please report the bug to the developer.");
            }
        }
        Vartype vartype = Vartype::BINARY;
        BinaryQuadraticModel<string> bqm(linear, quadratic, offset, vartype);
        return bqm;
    }


    BinaryQuadraticModel<uint32_t> evaluate_with_index(map<string, double> feed_dict){
        Linear<uint32_t> linear;
        Quadratic<uint32_t> quadratic;
        double offset = 0.0;
        for (auto it = this->terms.begin(); it != this->terms.end(); it++) {
            if(it->first.length == 2){
                auto var_it = it->first.prodset.begin();
                uint32_t i = *var_it - 1;
                var_it++;
                uint32_t j = *var_it - 1;
                quadratic[std::make_pair(i, j)] = it->second->evaluate(feed_dict);
            }else if(it->first.length == 1){
                auto var_it = it->first.prodset.begin();
                uint32_t i = *var_it-1;
                linear[i] = it->second->evaluate(feed_dict);
            }else if(it->first.length == 0){
                offset = it->second->evaluate(feed_dict);
            }else{
                throw std::runtime_error("QUBO was not created correctly. Please report the bug to the developer.");
            }
        }
        Vartype vartype = Vartype::BINARY;
        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);
        return bqm;
    }

    double evaluate_energy(Sample<string> sample, map<string, double> feed_dict, Encoder& encoder){
        double energy = 0.0;
        for (auto it = this->terms.begin(); it != this->terms.end(); it++) {
            int prod_value = 1;
            for(auto& it_var: it->first.prodset){
                string label = encoder.decode(it_var-1);
                auto result = sample.find(label);
                if(result != sample.end()){
                    prod_value *= result->second;
                }else{
                    throw std::runtime_error("The value of " + label + " was not contained in sample.");
                }
            }
            energy += prod_value * it->second->evaluate(feed_dict);
        }
        return energy;
    }
};