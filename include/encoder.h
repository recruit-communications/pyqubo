#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <stdio.h>
#include <memory>

class Binary;

typedef std::unordered_map<std::string, uint32_t> LabelToIndex;
typedef std::unordered_map<uint32_t, std::string> IndexToLabel;

class Encoder{
    LabelToIndex label_to_index;
    IndexToLabel index_to_label;
    uint32_t current_index = 0;

public:
    std::vector<std::string> variables;

    Encoder(){};

    Encoder(const Encoder& encoder){
        this->label_to_index = LabelToIndex(encoder.label_to_index);
        this->index_to_label = IndexToLabel(encoder.index_to_label);
        this->variables = std::vector<std::string>(encoder.variables);
        this -> current_index = current_index;
    }

    uint32_t encode(std::shared_ptr<Binary> exp);
    uint32_t encode(std::string label);
    std::string decode(uint32_t index);
    size_t size();
};