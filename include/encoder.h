#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <stdio.h>
#include <memory>

class Binary;

class Encoder{
    std::unordered_map<std::string, uint32_t> label_to_index;
    std::unordered_map<uint32_t, std::string> index_to_label;
    uint32_t current_index = 0;

public:
    Encoder(){};

    uint32_t encode(std::shared_ptr<Binary> exp);
    uint32_t encode(std::string label);
    std::string decode(uint32_t index);
    size_t size();
    std::vector<std::string> variables;
};