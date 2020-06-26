#pragma once
#include <string>
#include <vector>


class ArrayIndex{
public:
    std::string var_label;
    std::string array_label;
    std::vector<uint32_t> size;
    std::vector<uint32_t> indices;

    ArrayIndex(
        std::string _var_label,
        std::string _array_label,
        std::vector<uint32_t> _size,
        std::vector<uint32_t> _indices
    ):
        var_label(_var_label),
        array_label(_array_label),
        size(_size),
        indices(_indices){}
    
    bool equal_to(ArrayIndex* other){
        bool label_equal = var_label == other->var_label;
        bool array_label_equal = array_label == other->array_label;
        bool size_equal = size == other->size;
        bool indices_equal = indices == other->indices;
        return label_equal && array_label_equal && size_equal && indices_equal;
    }
    
    std::string to_string(){
        std::string s = std::string("ArrayIndex(") + var_label + "," + array_label + ",size=(";
        for(auto& it: size){
            s += std::to_string(it) + ",";
        }
        if(size.size() > 0) s.pop_back();
        s += "),index=(";
        for(auto& it: indices){
            s += std::to_string(it) + ",";
        }
        if(indices.size() > 0) s.pop_back();
        s += "))";
        return s;
    }
};