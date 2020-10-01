#include <encoder.h>
#include <express.h>


using namespace std;

uint32_t Encoder::encode(shared_ptr<Binary> exp){
    return this->encode(exp->label);
}

uint32_t Encoder::encode(string label){
    auto it = label_to_index.find(label);
    if (it == label_to_index.end()){
        label_to_index[label] = current_index;
        index_to_label[current_index] = label;

        // register label to variables
        variables.push_back(label);

        current_index++;
        return current_index - 1;
    }else{
        return it->second;
    }
}

std::string Encoder::decode(uint32_t index){
    auto it = index_to_label.find(index);
    if (it == index_to_label.end()){
        throw std::runtime_error("Decode failed. index " + std::to_string(index) + " is out of bounds.");
    }else{
        return it->second;
    }
}

size_t Encoder::size(){
    return this->label_to_index.size();
}
