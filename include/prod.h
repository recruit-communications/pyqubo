#pragma once
#include <set>
using namespace std;



class Prod {
    
    /* First order Prod */
    Prod(uint32_t p0):
        length(1){
        sorted_indices = new uint32_t[1];
        sorted_indices[0] = p0+1;
        set_hash(sorted_indices, 1);
    }

    /* Second order Prod */
    Prod(uint32_t p0, uint32_t p1):
        length(2){
            if(p0 >= p1){
                throw std::runtime_error("input indedices should be sorted.");
            }
            sorted_indices = new uint32_t[2];
            sorted_indices[0] = p0+1;
            sorted_indices[1] = p1+1;
            set_hash(sorted_indices, 2);
    }

public:
    uint32_t* sorted_indices;
    size_t length;
    size_t hash_value;

    Prod(const Prod& prod){
        this->length = prod.length;
        this->sorted_indices = new uint32_t[prod.length];
        for(int i=0; i < prod.length; i++){
            this->sorted_indices[i] = prod.sorted_indices[i];
        }
        this->set_hash(sorted_indices, prod.length);
    }

    Prod &operator=(const Prod& prod){
        if(this != &prod){
            this->sorted_indices = new uint32_t[prod.length];
            this->length = prod.length;
            for(int i=0; i < prod.length; i++){
                this->sorted_indices[i] = prod.sorted_indices[i];
            }
            this->set_hash(sorted_indices, prod.length);
        }
        return(*this);
    }

    ~Prod(){
        if(length > 0){
            delete[] sorted_indices;
        }
    }
    
    Prod(uint32_t* _sorted_indices, int _length):
        length(_length){
            sorted_indices = new uint32_t[_length];
            for(int i=0; i<_length; i++){
                sorted_indices[i] = _sorted_indices[i];
            }
            set_hash(sorted_indices, _length);
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
            set_hash(0);
        };
    
    void set_hash(uint32_t p0){
        this->hash_value = std::hash<uint32_t>{}(p0);
    }

    void set_hash(uint32_t* sorted_indices, int length){
        size_t seed = 0;
        uint32_t curr = 0;
        for(int i=0; i<length; i++){
            int shift = 7*(i%4);
            curr = sorted_indices[i] << shift;
            /*if(i==0){
                curr = sorted_indices[0];
            }else if(i==1){
                curr = sorted_indices[1] << 7;
            }else if(i==2){
                curr = sorted_indices[2] << 14;
            }else{
                curr = sorted_indices[3] << 21;
            }*/
            seed = seed ^ std::hash<uint32_t>{}(curr);
        }
        this->hash_value = seed;
    }

    uint32_t get_var(int index){
        if(index > this->length){
            throw std::runtime_error("index out of bounds in get_var().");
        }
        return this->sorted_indices[index]-1;
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
        for(int i=0;i<this->length;i++){
            bool match = p.sorted_indices[i] == this->sorted_indices[i];
            ret = ret && match;
        }
        return ret;
    }

    size_t hash() const {
        return this-> hash_value;
    }

    string to_string() const {
        string s = string() + "Prod(";
        for (int i=0; i < this->length; i++) {
            s += std::to_string(sorted_indices[i]);
            if(i != this->length-1) s+= string(",");
        }
        s += ")";
        return s;
    }

    Prod merge(Prod& other){
        int i = 0; // index for this->sorted_indices
        int j = 0; // index for other.sorted_indices
        int k = 0; // index for new_sorted_indices
        uint32_t* new_sorted_indices = new uint32_t[std::max(this->length, other.length)];
        uint32_t previous_index = -1;
        // merge sorted_indices
        while(i < this->length || j < other.length){
            if(j == other.length || (i < this->length && this->sorted_indices[i] < other.sorted_indices[j])){
                uint32_t new_index = this->sorted_indices[i];
                if(previous_index != new_index){
                    new_sorted_indices[k++] = new_index;
                    previous_index = new_index;
                }
                i++;
            }else{
                uint32_t new_index = other.sorted_indices[j];
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


class Prod3 {
    
    /* 一次の項 */
    Prod3(uint32_t p0):
        length(1){
        sorted_indices[0] = p0+1;
        set_hash(sorted_indices, 1);
    }

    /* 二次の項 */
    Prod3(uint32_t p0, uint32_t p1):
        length(2){
            if(p0 >= p1){
                throw std::runtime_error("input indedices should be sorted.");
            }
            sorted_indices[0] = p0+1;
            sorted_indices[1] = p1+1;
            set_hash(sorted_indices, 2);
    }

public:
    uint32_t sorted_indices[4] = {0};
    size_t length;
    size_t MAX_LENGTH = 4;
    size_t hash_value;

    Prod3(const Prod3& prod){
        this->length = prod.length;
        for(int i=0; i < prod.length; i++){
            this->sorted_indices[i] = prod.sorted_indices[i];
        }
        set_hash(sorted_indices, prod.length);
    }

    ~Prod3(){}
    
    Prod3(uint32_t* _sorted_indices, int _length):
        length(_length){
            for(int i=0; i<_length; i++){
                sorted_indices[i] = _sorted_indices[i];
            }
            set_hash(sorted_indices, _length);
        }

    static Prod3 create(uint32_t p0, uint32_t p1){
        return Prod3(p0, p1);
    }

    static Prod3 create(uint32_t p0){
        return Prod3(p0);
    }

    /* 定数項 */
    Prod3():
        length(0){
            set_hash(0);
        };
    
    void set_hash(uint32_t p0){
        this->hash_value = std::hash<uint32_t>{}(p0);
    }

    void set_hash(uint32_t* sorted_indices, int length){
        size_t seed = 0;
        uint32_t curr = 0;
        for(int i=0; i<length; i++){
            if(i==0){
                curr = sorted_indices[0];
            }else if(i==1){
                curr = sorted_indices[1] << 7;
            }else if(i==2){
                curr = sorted_indices[2] << 14;
            }else{
                curr = sorted_indices[3] << 21;
            }
            seed = seed ^ std::hash<uint32_t>{}(curr);
        }
        this->hash_value = seed;
    }

    uint32_t get_var(int index){
        if(index > this->length){
            throw std::runtime_error("index out of bounds in get_var().");
        }
        return this->sorted_indices[index]-1;
    }
    
    bool equal_to(const Prod3& p) const {
        if(this->length != p.length) return false;
        //return this->enc_prod.equal_to(p.enc_prod);

        bool ret = true;
        for(int i=0;i<this->length;i++){
            bool match = p.sorted_indices[i] == this->sorted_indices[i];
            ret = ret && match;
        }
        return ret;
    }

    size_t hash() const {
        return this-> hash_value;
    }

    string to_string() const {
        string s = string() + "Prod3(";
        for (int i=0; i < this->length; i++) {
            s += std::to_string(sorted_indices[i]);
            if(i != this->length-1) s+= string(",");
        }
        s += ")";
        return s;
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