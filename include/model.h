#pragma once
#include <compiled_qubo.h>
#include <poly.h>
#include <expanded.h>
#include <utils.h>
#include <compiled_sub_h.h>
#include <decoded_solution.h>
#include <binary_quadratic_model.hpp>
#include <string>



using QuboInt = std::tuple<Quadratic<uint32_t>, double>;
using QuboStr = std::tuple<Quadratic<std::string>, double>;
using IsingInt = std::tuple<Linear<uint32_t>, Quadratic<uint32_t>, double>;
using IsingStr = std::tuple<Linear<std::string>, Quadratic<std::string>, double>;
using FeedDict = map<string, double>;

class Model{
    CompiledQubo compiled_qubo;
    Encoder encoder;
    std::vector<CompiledSubH> compiled_sub_hs;

public:
    Model(
        CompiledQubo _compiled_qubo,
        Encoder encoder,
        Expanded* expanded
    ):
        compiled_qubo(_compiled_qubo),
        encoder(encoder),
        compiled_sub_hs(build_sub_hs_vector(expanded->first_sub_hs)){}
    
    ~Model(){}
    
    string to_string(){
        string s = string("Model(") + this->compiled_qubo.to_string() + ", SubHs=[";
        bool subhs_exists = false;
        for(auto& it: compiled_sub_hs){
            s += it.to_string() + ",";
            subhs_exists = true;
        }
        if(subhs_exists) s.pop_back();
        s += "])";
        return s;
    }

    vector<string> variables() const {
        return this->encoder.variables;
    }

    BinaryQuadraticModel<uint32_t> to_bqm_with_index(FeedDict feed_dict){
        return compiled_qubo.evaluate_with_index(feed_dict);
    }

    BinaryQuadraticModel<std::string> to_bqm(FeedDict feed_dict){
        return compiled_qubo.evaluate(feed_dict, this->encoder);
    }

    QuboInt to_qubo_with_index(FeedDict feed_dict = std::map<string, double>()){
        auto bqm = to_bqm_with_index(feed_dict);
        return bqm.to_qubo();
    }

    QuboStr to_qubo(FeedDict feed_dict = std::map<string, double>()){
        auto bqm = to_bqm(feed_dict);
        return bqm.to_qubo();
    }

    IsingInt to_ising_with_index(FeedDict feed_dict = std::map<string, double>()){
        auto bqm = to_bqm_with_index(feed_dict);
        return bqm.to_ising();
    }

    IsingStr to_ising(FeedDict feed_dict = std::map<string, double>()){
        auto bqm = to_bqm(feed_dict);
        return bqm.to_ising();
    }

    std::vector<CompiledSubH> build_sub_hs_vector(LinkedList<CompiledSubH>* compiled_sub_hs){
        std::vector<CompiledSubH> subhs_vector;
        std:set<string> labels;
        auto it = compiled_sub_hs;
        while(it != nullptr){
            auto found = labels.find(it->value.label);
            if(found == labels.end()){
                subhs_vector.push_back(it->value);
                labels.insert(it->value.label);
            }
            it = it->next;
        }
        return subhs_vector;
    }

    double energy(
        Sample<string>& sample,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        BinaryQuadraticModel<std::string> bqm = to_bqm(feed_dict);
        if(vartype == Vartype::BINARY){
            return bqm.energy(sample);
        }else{
            auto bin_sample = utils::binary_to_spin(sample);
            return bqm.energy(bin_sample);
        }
    }

    vector<double> energies(
        vector<Sample<string>>& samples,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        vector<double> energy_vector;
        for(auto& sample: samples){
            energy(sample, vartype, feed_dict);
        }
    }

    Sample<string> convert_sample_vector_to_label(
        vector<int32_t>& sample
    ){
        Sample<string> new_sample;
        int i = 0;
        for(auto & it: sample){
            string new_index = encoder.decode(i);
            new_sample[new_index] = it;
            i++;
        }
        return new_sample;
    }

    vector<Sample<string>> convert_samples_vector_to_label(
        vector<vector<int32_t>>& samples
    ){
        vector<Sample<string>> new_samples;
        for(auto &sample : samples){
            auto new_sample = convert_sample_vector_to_label(sample);
            new_samples.push_back(new_sample);
        }
        return new_samples;
    }

    vector<Sample<string>> convert_samples_index_to_label(vector<Sample<uint32_t>> &samples){
        vector<Sample<string>> new_samples;
        for(auto &sample : samples){
            auto new_sample = convert_sample_index_to_label(sample);
            new_samples.push_back(new_sample);
        }
        return new_samples;
    }

    Sample<string> convert_sample_index_to_label(Sample<uint32_t>& sample){
        Sample<string> new_sample;
        for(auto& it: sample){
            string new_index = encoder.decode(it.first);
            new_sample[new_index] = it.second;
        }
        return new_sample;
    }

    vector<DecodedSolution> decode_samples_vector
    (
        vector<vector<int32_t>>& samples,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        auto new_samples = convert_samples_vector_to_label(samples);
        return decode_samples(new_samples, vartype, feed_dict);
    }

    DecodedSolution decode_sample_vector
    (
        vector<int32_t>& sample,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        auto new_sample = convert_sample_vector_to_label(sample);
        return decode_sample(new_sample, vartype, feed_dict);
    }

    vector<DecodedSolution> decode_samples_with_index
    (
        vector<Sample<uint32_t>>& samples,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        auto new_samples = convert_samples_index_to_label(samples);
        return decode_samples(new_samples, vartype, feed_dict);
    }

    DecodedSolution decode_sample_with_index
    (
        Sample<uint32_t>& sample,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        check_variable(sample);
        auto new_sample = convert_sample_index_to_label(sample);
        return decode_sample(new_sample, vartype, feed_dict);
    }

    template <class T, class Dummy=int>
    vector<DecodedSolution> decode_samples_general(
        vector<Sample<T>>& samples,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        throw std::runtime_error("Incompatible type. Please contact developers.");
    }

    template <class Dummy=int>
    vector<DecodedSolution> decode_samples_general(
        vector<Sample<uint32_t>>& samples,
        Vartype vartype,
        FeedDict feed_dict
    ){ 
        return decode_samples_with_index(samples, vartype, feed_dict);
    }

    template <class Dummy=int>
    vector<DecodedSolution> decode_samples_general(
        vector<Sample<string>>& samples,
        Vartype vartype,
        FeedDict feed_dict
    ){ 
        return decode_samples(samples, vartype, feed_dict);
    }


    vector<DecodedSolution> decode_samples(
        vector<Sample<string>>& samples,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        vector<DecodedSolution> decoded_solutions;
        BinaryQuadraticModel<std::string> bqm = to_bqm(feed_dict);

        for(auto& sample: samples){
            Sample<string> binary_sample;
            if(vartype == Vartype::BINARY){
                binary_sample = sample;
            }else{
                binary_sample = utils::binary_to_spin(sample);
            }
            double energy = bqm.energy(binary_sample);
            auto sol = DecodedSolution(this->compiled_sub_hs, sample, energy, feed_dict, this->encoder, vartype);
            decoded_solutions.push_back(sol);
        }
        return decoded_solutions;
    }

    

    DecodedSolution decode_sample(
        Sample<string>& sample,
        Vartype vartype,
        FeedDict feed_dict = std::map<string, double>()
    ){
        BinaryQuadraticModel<std::string> bqm = to_bqm(feed_dict);
        Sample<string> binary_sample;
        if(vartype == Vartype::BINARY){
            binary_sample = sample;
        }else{
            binary_sample = utils::binary_to_spin(sample);
        }
        check_variable(sample);
        double energy = bqm.energy(binary_sample);
        return DecodedSolution(this->compiled_sub_hs, sample, energy, feed_dict, this->encoder, vartype);
    }

    void check_variable(Sample<uint32_t>& sample){
        int model_size = variables().size();
        for(auto& it: sample){
            if(it.first < 0 || it.first >= model_size){
                string err_msg = string("given sample contains index: ") + std::to_string(it.first) + " which is ouf of range.";
                throw std::out_of_range(err_msg);
            }
        }
    }

    void check_variable(Sample<string>& sample){
        for(auto& var: variables()){
            auto result = sample.find(var);
            if(result == sample.end()){
                string err_msg = string("key: ") + var + " was not found in the given sample";
                throw std::invalid_argument(err_msg);
            }
        }
    }
};

