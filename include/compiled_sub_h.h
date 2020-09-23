#pragma once
#include <poly.h>
#include <string>


class CompiledSubH{
public:
    CompiledQubo* compiled_qubo;
    string label;
    std::function<bool(double)> condition;
    CompiledSubH(std::string _label, Terms* terms, std::function<bool(double)> condition):
        label(_label),
        compiled_qubo(compile_coeff(terms)),
        condition(condition){}
    
    ~CompiledSubH(){}

    bool equal_to(const CompiledSubH& other){
        return compiled_qubo->equal_to(other.compiled_qubo) && label == other.label;
    }

    std::string to_string(){
        std::string s = std::string("SubH(") + label + "," + compiled_qubo->to_string() + ")";
        return s;
    }

private:
    CompiledQubo* compile_coeff(Terms* terms){
        CompiledTerms compiled_terms;
        for(auto it = terms->begin(); it != terms->end(); it++){
            PHPolyBase* compiled_coeff = it->second->expand();
            Prod prod = it->first;
            auto p = std::make_pair(prod, compiled_coeff);
            compiled_terms.push_back(p);
        }
        return new CompiledQubo(compiled_terms);
    }
};