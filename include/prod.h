#pragma once
#include <unordered_set>
#include <set>
using namespace std;


typedef std::set<uint32_t> ProdSet;


class Prod {

    Prod(uint32_t p0){
        this->prodset.insert(p0+1);
        this->length = 1;
        set_hash();
    }

    Prod(uint32_t p0, uint32_t p1){
        this->prodset.insert(p0+1);
        this->prodset.insert(p1+1);
        this->length = 2;
        set_hash();
    }

public:
    ProdSet prodset;
    size_t length;
    size_t hash_value;

    Prod(ProdSet ps): prodset(ps), length(ps.size()){
        set_hash();
    };

    Prod():
        length(0){
            // Constant Prod doesn't allocate memory to sorted_indices.
            set_hash();
        };

    static Prod create(uint32_t p0, uint32_t p1){
        return Prod(p0, p1);
    }

    static Prod create(uint32_t p0){
        return Prod(p0);
    }

    Prod merge(Prod& other){
        ProdSet new_prodset;
        for(auto& it: this->prodset){
            new_prodset.insert(it);
        }
        for(auto& it: other.prodset){
            new_prodset.insert(it);
        }
        return Prod(new_prodset);
    }

    uint32_t get_raw_var(int index){
        if(index >= this->length){
            throw std::out_of_range("index out of bounds");
        }
        int i=0;
        for(auto& it: this->prodset){
            if(i==index){
                return it;
            }else{
                i++;
            }
        }
    }

    uint32_t get_var(int index){
        return get_raw_var(index)-1;
    }

    string to_string(){
        string s = string() + "Prod(";
        for (int i=0; i < this->length; i++) {
            s += std::to_string(this->get_raw_var(i));
            if(i != this->length-1) s+= string(",");
        }
        s += ")";
        return s;
    }

    bool equal_to(const Prod& p) const {
        if(this->length != p.length) return false;

        // when the both prods have length == 0, both prods are constant prod.
        if(this->length == 0 && p.length == 0) return true;

        return this->prodset == p.prodset;
    }

    bool operator==(const Prod& other) const {
        return this->equal_to(other);
    }

    bool operator!=(const Prod& other) const {
        return !this->equal_to(other);
    }

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
};


namespace std {

    struct ProdHash {
        size_t operator()(const Prod& p) const { return p.hash_value; }
    };

    struct ProdEqual {
        bool operator()(const Prod& left, const Prod& right) const { return left.equal_to(right); }
    };
}