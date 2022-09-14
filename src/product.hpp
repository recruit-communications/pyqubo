#pragma once

#include <algorithm>
#include <cstddef>
#include <functional>
#include <initializer_list>
#include <iterator>
#include <map>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <boost/container/small_vector.hpp>
#include <boost/functional/hash.hpp>
#include <robin_hood.h>

namespace pyqubo {
    using indexes = boost::container::small_vector<int, 2>;
    class product final {
        pyqubo::indexes _indexes;
        std::size_t _hash;

    public:
        product(const pyqubo::indexes& indexes) noexcept : _indexes(indexes), _hash(create_hash(indexes)) {
        ;
        }

        std::size_t create_hash(const pyqubo::indexes& indexes){
            std::size_t seed = robin_hood::hash_int(4711);
            for(int v: indexes){
                // Combine algorithm is same as boost::hash_conbine except hash function.
                // We use robin_hood::hash_int since boost::hash doesn't work well. 
                seed ^= robin_hood::hash_int(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
            }
            return seed;
        }

        product(std::initializer_list<int> init) noexcept : product(pyqubo::indexes(init)) {
        ;
        }

        std::string to_string() const {
            std::stringstream ss;
            ss << "[";
            for(size_t i = 0; i < _indexes.size(); ++i){
                if(i != 0) ss << ",";
                ss << _indexes[i];
            }
            ss << "]";
            std::string s = ss.str();
            return s;
        }

        const auto& indexes() const noexcept {
        return _indexes;
        }

        bool equals(pyqubo::product other){
            return this->indexes() == other.indexes();
        }

        friend std::hash<product>;
    };


}