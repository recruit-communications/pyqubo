#pragma once
#include <string>
#include <map>
#include <linkedlist.h>
#include <compiled_sub_h.h>
#include <utils.h>
#include <binary_quadratic_model.hpp>


using FeedDict = map<string, double>;

class DecodedSubH{
public:
    string label;
    double energy;
    bool is_constraint;
    bool satisfied;

    DecodedSubH(
        CompiledSubH compiled_sub_h,
        Sample<string> sample,
        FeedDict feed_dict,
        Encoder& encoder,
        Vartype vartype
    ){
        Sample<string> binary_sample;
        if(vartype == Vartype::BINARY){
            binary_sample = sample;
        }else{
            binary_sample = utils::binary_to_spin(sample);
        }
        this->energy = compiled_sub_h.compiled_qubo->evaluate_energy(binary_sample, feed_dict, encoder);
        this->label = compiled_sub_h.label;
        if(compiled_sub_h.condition != nullptr){
            this->is_constraint = true;
            this->satisfied = compiled_sub_h.condition(this->energy);
        }else{
            this->is_constraint = false;
            this->satisfied = false;
        }
    }

    string to_string(){
        return string("Constraint(") + label + ",energy=" + std::to_string(energy) + ")";
    }
};


class DecodedSolution{
public:
    vector<DecodedSubH> decoded_subhs;
    map<string, double> subh_values;
    map<string, std::pair<bool, double>> constraints;
    Sample<string> sample;
    double energy;

    DecodedSolution(
        vector<CompiledSubH> compiled_sub_hs,
        Sample<string> _sample,
        double _energy,
        FeedDict feed_dict,
        Encoder& encoder,
        Vartype vartype
    ):
        sample(_sample),
        energy(_energy)
    {
        for(auto& sub_h: compiled_sub_hs){
            auto decoded_subh = DecodedSubH(sub_h, sample, feed_dict, encoder, vartype);
            this->decoded_subhs.push_back(decoded_subh);
        }
        subh_values = build_subh_values(this->decoded_subhs);
        constraints = build_constraints(this->decoded_subhs);
    }

    map<string, std::pair<bool, double>> get_constraints(bool only_broken){
        if(only_broken){
            map<string, std::pair<bool, double>> broken;
            for(auto& c: this->constraints){
                if(!c.second.first){
                    broken[c.first] = c.second;
                }
            }
            return broken;
        }else{
            return this->constraints;
        }
    }

    string to_string(){
        string s = string("DecodedSample(decoded_subhs=[");
        for(auto& constraint: decoded_subhs){
            s += constraint.to_string() + ",";
        }
        if(constraints.size()>0) s.pop_back();
        s += "],sample={";
        for(auto& it: sample){
            s += it.first + ":" + std::to_string(it.second) + ",";
        }
        if(sample.size()>0) s.pop_back();
        s += "})";
        return s;
    }

private:
    map<string, std::pair<bool, double>> build_constraints(vector<DecodedSubH> &decoded_subhs){
        std::map<string, std::pair<bool, double>> constraints;
        for(auto& subh: decoded_subhs){
            if(subh.is_constraint){
                constraints[subh.label] = std::make_pair(subh.satisfied, subh.energy);
            }
        }
        return constraints;
    }

    map<string, double> build_subh_values(vector<DecodedSubH> &decoded_subhs){
        std::map<string, double> subh_values;
        for(auto& subh: decoded_subhs){
            subh_values[subh.label] = subh.energy;
        }
        return subh_values;
    }
};
