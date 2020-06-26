#pragma once
#include <binary_quadratic_model.hpp>
#include <string>


namespace utils{
    template <class T>
    Sample<T> binary_to_spin(Sample<T> sample){
        Sample<T> new_sample;
        for(auto& it: sample){
            new_sample[it.first] = (int32_t)((it.second + 1)/2);
        }
        return new_sample;
    }
}