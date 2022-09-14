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

#include <binary_quadratic_model.hpp>
#include <boost/container/small_vector.hpp>
#include <boost/functional/hash.hpp>
#include <robin_hood.h>

namespace std {
  template <>
  struct hash<pyqubo::product> {
    auto operator()(const pyqubo::product& product) const noexcept {
      return product._hash;
    }
  };
}

namespace pyqubo {
  using polynomial = robin_hood::unordered_map<product, std::shared_ptr<const expression>>;
  //using polynomial = std::unordered_map<product, std::shared_ptr<const expression>>;

  class variables final {
    robin_hood::unordered_map<std::string, int> _indexes;
    robin_hood::unordered_map<int, std::string> _names;

  public:
    variables() noexcept : _indexes{}, _names{} {
      ;
    }

    std::string to_string() const {
      std::string s = "variables(";
      for(auto [name, index]: _indexes){
        s += name + "->" + std::to_string(index) + "\n";
      }
      s += ")";
      return s;
    }

    auto index(const std::string& variable_name) noexcept {
      const auto [it, emplaced] = _indexes.emplace(variable_name, std::size(_indexes));

      if (emplaced) {
        _names.emplace(it->second, variable_name);
      }

      return it->second;
    }

    const auto& name(int index) const noexcept {
      return _names.find(index)->second;
    }

    auto names() const noexcept {
      auto result = std::vector<std::string>(std::size(_names));

      for (const auto& [index, name] : _names) {
        result[index] = name;
      }

      return result;
    }
  };

  inline auto multiply(const product* product_1, const product* product_2) noexcept {
    return new product([&] {
      auto result = indexes{};

      std::set_union(std::begin(product_1->indexes()), std::end(product_1->indexes()),
                     std::begin(product_2->indexes()), std::end(product_2->indexes()),
                     std::back_inserter(result));

      return result;
    }());
  }

  inline auto operator*(const product& product_1, const product& product_2) noexcept {
    return product([&] {
      auto result = indexes{};

      std::set_union(std::begin(product_1.indexes()), std::end(product_1.indexes()),
                     std::begin(product_2.indexes()), std::end(product_2.indexes()),
                     std::back_inserter(result));

      return result;
    }());
  }

  inline bool operator==(const product& product_1, const product& product_2) noexcept {
    return product_1.indexes() == product_2.indexes();
  }

  inline auto operator+(const polynomial& polynomial_1, const polynomial& polynomial_2) noexcept {
    auto result = polynomial_1;

    for (const auto& [product, coefficient] : polynomial_2) {
      const auto [it, emplaced] = result.emplace(product, coefficient);

      if (!emplaced) {
        it->second = it->second + coefficient;
      }
    }

    return result;
  }

  inline auto operator*(const polynomial& polynomial_1, const polynomial& polynomial_2) noexcept {
    auto result = polynomial{};

    for (const auto& [product_1, coefficient_1] : polynomial_1) {
      for (const auto& [product_2, coefficient_2] : polynomial_2) {
        const auto [it, emplaced] = result.emplace(product_1 * product_2, coefficient_1 * coefficient_2);

        if (!emplaced) {
          it->second = it->second + coefficient_1 * coefficient_2;
        }
      }
    }

    return result;
  }

}

