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
        product(const pyqubo::indexes& indexes) noexcept : _indexes(indexes), _hash(boost::hash_range(std::begin(indexes), std::end(indexes))) {
        ;
        }

        product(std::initializer_list<int> init) noexcept : product(pyqubo::indexes(init)) {
        ;
        }

        const auto& indexes() const noexcept {
        return _indexes;
        }

        friend std::hash<product>;
    };
}