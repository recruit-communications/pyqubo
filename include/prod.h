#pragma once
//#include <emmintrin.h>
#include <smmintrin.h>
#include <emmintrin.h>
using namespace std;

//typedef std::unordered_set<std::string> VarSet;
typedef std::set<std::string> VarSet;

class Prod2 {
    VarSet vars;
    size_t hash_value;
public:
    Prod2(VarSet vars) {
        this->vars = vars;
        set_hash(vars);
    }

    void set_hash(VarSet vars){
        size_t seed = 0;
        for (VarSet::iterator it = vars.begin(); it != vars.end(); it++) {
            seed = seed ^ std::hash<string>{}(*it);
        }
        this->hash_value = seed;
    }

    size_t hash() {
        return this->hash_value;
    }

    bool equal_to(Prod2 other) {
        if (this->hash() != other.hash()) {
            return false;
        } else {
            //todo: Comparison of two sets can be optimized.
            return this->vars == other.vars;
        }
    }

    string to_string() {
        string s = string() + "Prod2(";
        for (VarSet::iterator it = vars.begin(); it != vars.end(); it++) {
            s += *it + ",";
        }
        s += ")";
        return s;
    }

    void merge(Prod2 other){
        for (VarSet::iterator it = other.vars.begin(); it != other.vars.end(); it++) {
            this->vars.insert(*it);
        }
        set_hash(this->vars);
    }
};

class EncProd{
public:
    __m128i data;

    EncProd(uint32_t* p){
        data = _mm_set_epi32(p[0], p[1], p[2], p[3]);
    }

    EncProd(){
        data = _mm_set_epi32(0, 0, 0, 0);
    }

    EncProd(uint32_t p0){
        data = _mm_set_epi32(p0, 0, 0, 0);
    }

    EncProd(uint32_t p0, uint32_t p1){
        data = _mm_set_epi32(p0, p1, 0, 0);
    }

    EncProd(uint32_t p0, uint32_t p1, uint32_t p2){
        data = _mm_set_epi32(p0, p1, p2, 0);
    }

    EncProd(uint32_t p0, uint32_t p1, uint32_t p2, uint32_t p3){
        data = _mm_set_epi32(p0, p1, p2, p3);
    }

    bool equal_to(const EncProd& p) const {
        //return _mm_test_all_ones(_mm_cmpeq_epi8(this->data, p.data));
        //return _mm_movemask_ps(_mm_cmpeq_ps(this->data, p.data)) == 0xF;
        return _mm_movemask_epi8(_mm_cmpeq_epi16(this->data, p.data)) == 0xFFFF;
        //return true;
    }

    bool operator<(const EncProd &p) const{
        const int less = _mm_movemask_epi8(_mm_cmplt_epi8( this->data, p.data));
        const int greater = _mm_movemask_epi8(_mm_cmpgt_epi8(this->data, p.data));
        return less > greater;
    }

    uint32_t* load_values2() const {
        uint32_t* values = (uint32_t*)calloc(4, sizeof(uint32_t));
        //uint32_t values[4] = {0};
        _mm_store_si128((__m128i*)values, this->data);
        return values;
    }

    string to_string() const {
        //int values[4];
        uint32_t* values = this->load_values2();
        string ret = string();
        for(int i=0; i<4;i++){
          ret += std::to_string(values[3-i]);
          if(i!=3) ret += ",";
        }
        delete values;
        return ret;
    }
};

class Prod {
    
    /* 一次の項 */
    Prod(uint32_t p0):
        length(1),
        enc_prod(EncProd(p0+1)){
        sorted_indices[0] = p0+1;
        set_hash(sorted_indices, 1);
    }

    /* 二次の項 */
    Prod(uint32_t p0, uint32_t p1):
        length(2),
        enc_prod(EncProd(p0+1, p1+1)){
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
    EncProd enc_prod;
    size_t MAX_LENGTH = 4;
    size_t hash_value;

    Prod(const Prod& prod){
        this->length = prod.length;
        for(int i=0; i < prod.length; i++){
            this->sorted_indices[i] = prod.sorted_indices[i];
        }
        enc_prod = EncProd(sorted_indices);
        set_hash(sorted_indices, prod.length);
    }
    
    Prod(uint32_t* _sorted_indices, int _length):
        length(_length),
        enc_prod(EncProd(_sorted_indices)){
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

    /* 定数項 */
    Prod():
        length(0),
        enc_prod(EncProd()){
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

    bool operator<(const Prod &b) const{
        return this->enc_prod < b.enc_prod;
    }

    bool operator==(const Prod& other) const {
        return this->equal_to(other);
    }

    bool operator!=(const Prod& other) const {
        return !this->equal_to(other);
    }
    
    bool equal_to(const Prod& p) const {
        if(this->length != p.length) return false;
        return this->enc_prod.equal_to(p.enc_prod);

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
        uint32_t new_sorted_indices[4] = {0};
        uint32_t previous_index = -1;
        // ソート済みであるsorted_indicesのマージを行う
        while(i < this->length || j < other.length){
            if(k > MAX_LENGTH){
                throw std::runtime_error("Merge of OptProd failed. Length exceeded.");
            }
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

    /*struct ProdLess{
        bool operator()(const Prod &a, const Prod &b){
            const int less = _mm_movemask_epi8( _mm_cmplt_epi8( a.enc_prod.data, b.enc_prod.data ) );
            const int greater = _mm_movemask_epi8( _mm_cmpgt_epi8(a.enc_prod.data, b.enc_prod.data) );
            return less > greater;
        }
    };*/
}