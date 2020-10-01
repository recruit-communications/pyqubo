#pragma once
#include <poly.h>
#include <linkedlist.h>
#include <compiled_sub_h.h>
#include <compiled_penalty.h>



class Expanded{
public:
    LinkedList<CompiledSubH>* first_sub_hs = nullptr;
    LinkedList<CompiledSubH>* last_sub_hs = nullptr;

    LinkedList<CompiledPenalty>* first_penalties = nullptr;
    LinkedList<CompiledPenalty>* last_penalties = nullptr;

    PolyBase* poly;

    Expanded(PolyBase* poly):
        poly(poly){}

    ~Expanded(){
        // we delete linkedlist by calling `delete_linked_list` at expanding finished.
        delete poly;
    }

    void delete_linked_list(){
        if(this->first_sub_hs != nullptr){
            delete this->first_sub_hs;
        }
        if(this->first_penalties != nullptr){
            delete this->first_penalties;
        }
    }

    string to_string(){
        string s = string("Expanded(poly=") + poly->to_string() + ",sub_h=[";
        auto it = first_sub_hs;
        while(it != nullptr){
            s += it->value.to_string() + ",";
            it = it->next;
        }
        s += "])";
        return s;
    }

    CompiledQubo* get_compiled_qubo(Encoder& encoder, CoeffPtr strength){
        Poly* mp = this->poly->to_multiple_poly();

        // add penalties to the Hamiltonian
        auto it = this->first_penalties;
        std::set<string> penalties;
        while(it != nullptr){
            auto result = penalties.find(it->value.label);
            if(result == penalties.end()){
                poly::merge_poly(mp, it->value.poly);
                penalties.insert(it->value.label);
            }
            it = it->next;
        }

        // make polynomial to QUBO
        Poly* quadratic_poly = mp->make_quadratic(encoder, strength);

        // compile the coefficients of QUBO
        CompiledQubo* compiled_qubo = quadratic_poly->compile_coeff();
        return compiled_qubo;
    }

    void add_sub_h(string label, Terms* terms, std::function<bool(double)> condition){
        if(first_sub_hs == nullptr){
            first_sub_hs = new LinkedList<CompiledSubH>(CompiledSubH(label, terms, condition));
            last_sub_hs = first_sub_hs;
        }else{
            last_sub_hs->next = new LinkedList<CompiledSubH>(CompiledSubH(label, terms, condition));
            last_sub_hs = last_sub_hs->next;
        }
    }

    void add_penalty(string label, Expanded* expanded){
        // add poly of penalty
        if(first_penalties == nullptr){
            first_penalties = new LinkedList<CompiledPenalty>(CompiledPenalty(label, expanded->poly));
            last_penalties = first_penalties;
        }else{
            last_penalties->next = new LinkedList<CompiledPenalty>(CompiledPenalty(label, expanded->poly));
            last_penalties = last_penalties->next;
        }

        // add subhs of penalty from expanded
        if(first_sub_hs == nullptr){
            first_sub_hs = expanded->first_sub_hs;
            last_sub_hs = expanded->last_sub_hs;
        }else{
            last_sub_hs->next = expanded->first_sub_hs;
            last_sub_hs = expanded->last_sub_hs;
        }
    }
};

namespace expanded{
    Expanded* mul(Expanded* left_exp, Expanded* right_exp);
    Expanded* add(Expanded* left_exp, Expanded* right_exp);
    Expanded* pow(Expanded* expanded, int exponent);
}
