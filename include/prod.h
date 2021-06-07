#pragma once
#include <set>
using namespace std;




class Prod {
    
    /* First order Prod */
    Prod(uint32_t _p0):
        length(1){
        this->p0 = _p0+1;
        set_hash();
    }

    /* Second order Prod */
    Prod(uint32_t _p0, uint32_t _p1):
        length(2){
            if(_p0 >= _p1){
                throw std::runtime_error("input indedices should be sorted.");
            }
            this->p0 = _p0+1;
            this->p1 = _p1+1;
            set_hash();
    }

public:

    uint32_t p0;
    uint32_t p1;
    uint32_t* sorted_indices;
    size_t length;
    size_t hash_value;
    size_t OFFSET = 2;

    Prod(const Prod& prod){
        this->copy_to_this(prod);
    }

    void copy_to_this(const Prod& from){
        this->length = from.length;
        if(from.length > 0){
            this->p0 = from.p0;
        }
        if(from.length > 1){
            this->p1 = from.p1;
        }
        if(from.length > OFFSET){
            size_t indice_size = from.length - OFFSET;
            this->sorted_indices = new uint32_t[indice_size+1];
            for(int i=0; i < indice_size; i++){
                this->sorted_indices[i] = from.sorted_indices[i];
            }
        }
        this->hash_value = from.hash_value;
    }

    Prod &operator=(const Prod& prod){
        if(this != &prod){
            this->copy_to_this(prod);
        }
        return(*this);
    }

    ~Prod(){
        if(length > OFFSET){
            delete[] sorted_indices;
        }
    }
    
    Prod(uint32_t* _sorted_indices, int _length):
        length(_length){
            if(_length > 0){
                this->p0 = _sorted_indices[0];
            }
            if(_length > 1){
                this->p1 = _sorted_indices[1];
            }
            if(_length > OFFSET){
                size_t indice_size = _length - OFFSET;
                this->sorted_indices = new uint32_t[indice_size+1];
                for(int i=0; i<indice_size; i++){
                    this->sorted_indices[i] = _sorted_indices[i+OFFSET];
                }
            }
            this->set_hash();
        }

    static Prod create(uint32_t p0, uint32_t p1){
        return Prod(p0, p1);
    }

    static Prod create(uint32_t p0){
        return Prod(p0);
    }

    /* Constant Prod*/
    Prod():
        length(0){
            // Constant Prod doesn't allocate memory to sorted_indices.
            set_hash();
        };

    void set_hash(){
        if(this->length == 0){
            this->hash_value = std::hash<uint32_t>{}(0);
        }else{
            size_t seed = 0;
            for(int i=0; i < this->length; i++){
                int shift = 7 * (i % 4);
                uint32_t raw_var = this->get_raw_var(i);
                seed = seed ^ std::hash<uint32_t>{}(raw_var << shift);
            }
            this->hash_value = seed;
        }
    }

    uint32_t get_raw_var(int index) const {
        if(index >= this->length){
            throw std::out_of_range("index out of bounds");
        }
        if(index == 0){
            return this->p0;
        }else if(index == 1){
            return this->p1;
        }else{
            return this->sorted_indices[index-OFFSET];
        }
    }

    uint32_t get_var(int index){
        return get_raw_var(index)-1;
    }

    bool operator==(const Prod& other) const {
        return this->equal_to(other);
    }

    bool operator!=(const Prod& other) const {
        return !this->equal_to(other);
    }
    
    bool equal_to(const Prod& p) const {
        if(this->length != p.length) return false;

        /* when the both prods have length == 0, both prods are constant prod. */
        if(this->length == 0 && p.length == 0) return true;

        bool ret = true;
        for(int i=0; i < this->length; i++){
            bool match = this->get_raw_var(i) == p.get_raw_var(i);
            ret = ret & match;
        }
        return ret;
    }

    size_t hash() const {
        return this-> hash_value;
    }

    string to_string() const {
        string s = string() + "Prod(";
        for (int i=0; i < this->length; i++) {
            s += std::to_string(this->get_raw_var(i));
            if(i != this->length-1) s+= string(",");
        }
        s += ")";
        return s;
    }

    Prod merge(Prod& other){
        int i = 0;
        int j = 0;
        int k = 0;
        size_t max_size = this->length + other.length;
        uint32_t* new_sorted_indices = new uint32_t[max_size];
        
        uint32_t previous_index = -1;
        // merge sorted_indices
        while(i < this->length || j < other.length){
            if(j == other.length || (i < this->length && this->get_raw_var(i) < other.get_raw_var(j))){
                uint32_t new_index = this->get_raw_var(i);
                if(previous_index != new_index){
                    new_sorted_indices[k++] = new_index;
                    previous_index = new_index;
                }
                i++;
            }else{
                uint32_t new_index = other.get_raw_var(j);
                if(new_index != previous_index){
                    new_sorted_indices[k++] = new_index;
                    previous_index = new_index;
                }
                j++;
            }
        };
        Prod newOptProd = Prod(new_sorted_indices, k);
        delete[] new_sorted_indices;
        return newOptProd;
    }
};


namespace std {
    struct ProdHash {
        size_t operator()(const Prod& p) const { return p.hash(); }
    };

    struct ProdEqual {
        bool operator()(const Prod& left, const Prod& right) const { return left.equal_to(right); }
    };
}
