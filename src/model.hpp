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

#include "abstract_syntax_tree.hpp"

namespace pyqubo {
  class variables final {
    robin_hood::unordered_map<std::string, int> _indexes;
    robin_hood::unordered_map<int, std::string> _names;

  public:
    variables() noexcept : _indexes{}, _names{} {
      ;
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
}

namespace std {
  template <>
  struct hash<pyqubo::product> {
    auto operator()(const pyqubo::product& product) const noexcept {
      return product._hash;
    }
  };
}

namespace pyqubo {
  // std::variantを使用してzeroやmonomialな場合の処理削減をやってみたのですが、パフォーマンスは向上しませんでした。なので、unordered_map一本でやります。
  // よく考えれば、要素数が0の場合の処理とかはunordered_mapの中でやっていそうですし。。。

  using polynomial = robin_hood::unordered_map<product, std::shared_ptr<const expression>>;

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

  class evaluate final {
    std::unordered_map<std::string, double> _feed_dict;

  public:
    evaluate(const std::unordered_map<std::string, double>& feed_dict) noexcept : _feed_dict(feed_dict) {
      ;
    }

    auto operator()(const std::shared_ptr<const expression>& expression) const noexcept {
      return visit<double>(*this, expression);
    }

    auto operator()(const std::shared_ptr<const add_operator>& add_operator) const noexcept {
      return std::accumulate(std::begin(add_operator->children()), std::end(add_operator->children()), 0.0, [&](const auto& acc, const auto& child) {
        return acc + visit<double>(*this, child);
      });
    }

    auto operator()(const std::shared_ptr<const mul_operator>& mul_operator) const noexcept {
      return visit<double>(*this, mul_operator->lhs()) * visit<double>(*this, mul_operator->rhs());
    }

    auto operator()(const std::shared_ptr<const placeholder_variable>& place_holder_variable) const noexcept {
      return _feed_dict.at(place_holder_variable->name());
    }

    auto operator()(const std::shared_ptr<const user_defined_expression>& user_defined_expression) const noexcept {
      return visit<double>(*this, user_defined_expression->expression());
    }

    auto operator()(const std::shared_ptr<const numeric_literal>& numeric_literal) const noexcept {
      return numeric_literal->value();
    }
  };

  class solution final {
    std::unordered_map<std::string, int> _sample;
    double _energy;
    std::unordered_map<std::string, double> _sub_hamiltonians;
    std::unordered_map<std::string, std::pair<bool, double>> _constraints;

  public:
    solution(const std::unordered_map<std::string, int> sample, double energy, const std::unordered_map<std::string, double>& sub_hamiltonians, const std::unordered_map<std::string, std::pair<bool, double>>& constraints) noexcept : _sample(sample), _energy(energy), _sub_hamiltonians(sub_hamiltonians), _constraints(constraints) {
      ;
    }

    const auto& sample() const noexcept {
      return _sample;
    }

    auto energy() const noexcept {
      return _energy;
    }

    const auto& sub_hamiltonians() const noexcept {
      return _sub_hamiltonians;
    }

    const auto& constraints() const noexcept {
      return _constraints;
    }
  };

  class model final {
    polynomial _quadratic_polynomial;
    robin_hood::unordered_map<std::string, polynomial> _sub_hamiltonians;
    robin_hood::unordered_map<std::string, std::pair<polynomial, std::function<bool(double)>>> _constraints;
    variables _variables;

    static auto to_cimod_vartype(const std::string vartype) noexcept {
      return vartype == "BINARY" ? cimod::Vartype::BINARY : cimod::Vartype::SPIN;
    }

  public:
    model(const polynomial& quadratic_polynomial, const robin_hood::unordered_map<std::string, polynomial>& sub_hamiltonians, const robin_hood::unordered_map<std::string, std::pair<polynomial, std::function<bool(double)>>>& constraints, const variables& variables) noexcept : _quadratic_polynomial(quadratic_polynomial), _sub_hamiltonians(sub_hamiltonians), _constraints(constraints), _variables(variables) {
      ;
    }

    std::vector<std::string> variable_names() const noexcept {
      return _variables.names();
    }

    template <typename T = std::string>
    auto to_bqm_parameters(const std::unordered_map<std::string, double>& feed_dict) const noexcept { // 不格好でごめんなさい。PythonのBinaryQuadraticModelを作成可能にするために、このメンバ関数でBinaryQuadraticModelの引数を生成します。
      const auto evaluate = pyqubo::evaluate(feed_dict);

      auto linear = cimod::Linear<T, double>{};
      auto quadratic = cimod::Quadratic<T, double>{};
      auto offset = 0.0;

      for (const auto& [product, coefficient] : _quadratic_polynomial) {
        const auto coefficient_value = evaluate(coefficient);

        switch (std::size(product.indexes())) {
        case 0: {
          offset = coefficient_value; // 次数が0の項は1つにまとめられるので、この処理は最大で1回しか実行されません。なので、+=ではなくて=を使用しています。
          break;
        }
        case 1: {
          linear.emplace(_variables.name(product.indexes()[0]), coefficient_value);
          break;
        }
        case 2: {
          quadratic.emplace(std::pair{_variables.name(product.indexes()[0]), _variables.name(product.indexes()[1])}, coefficient_value);
          break;
        }
        default:
          throw std::runtime_error("invalid term."); // ここには絶対にこないはず。
        }
      }

      return std::tuple{linear, quadratic, offset};
    }

    template <typename T = std::string>
    auto to_bqm(const std::unordered_map<std::string, double>& feed_dict, cimod::Vartype vartype) const noexcept {
      const auto [linear, quadratic, offset] = to_bqm_parameters<T>(feed_dict);

      return cimod::BinaryQuadraticModel<T, double, cimod::Dense>(linear, quadratic, offset, vartype);
    }

    template <typename T = std::string>
    auto energy(const std::unordered_map<T, int>& sample, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) const noexcept {
      return to_bqm<T>(feed_dict, to_cimod_vartype(vartype)).energy([&] {
        // BinaryQuadraticModelの引数でvartypeを設定しても、energyでは使われないみたい。。。Determine the energy of the specified sample of a binary quadratic modelって書いてある。
        // しょうがないので、spinからbinaryに変換します。

        auto result = sample;

        if (vartype == "SPIN") {
          for (const auto& [name, value] : sample) {
            result[name] = (value + 1) / 2;
          }
        }

        return result;
      }());
    }

    template <typename T = std::string>
    auto decode_sample(const std::unordered_map<T, int>& sample, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) const noexcept {
      const auto evaluate = pyqubo::evaluate(feed_dict);
      const auto evaluate_polynomial = [&](const auto& polynomial, const auto& sample) {
        return std::accumulate(std::begin(polynomial), std::end(polynomial), 0.0, [&](const auto acc, const auto& term) {
          return acc +
                 std::accumulate(std::begin(term.first.indexes()), std::end(term.first.indexes()), 1, [&](const auto acc, const auto& index) {
                   const auto value = sample.at(_variables.name(index));

                   return acc * (vartype == "BINARY" ? value : (value + 1) / 2);
                 }) * evaluate(term.second);
        });
      };

      return solution(
          sample,
          energy<T>(sample, vartype, feed_dict),
          [&] {
            auto result = std::unordered_map<std::string, double>{};

            for (const auto& [name, polynomial] : _sub_hamiltonians) {
              result.emplace(name, evaluate_polynomial(polynomial, sample));
            }

            return result;
          }(),
          [&] {
            auto result = std::unordered_map<std::string, std::pair<bool, double>>{};

            for (const auto& [name, pair] : _constraints) {
              const auto& [polynomial, condition] = pair;
              const auto energy = evaluate_polynomial(polynomial, sample);

              result.emplace(name, std::pair{condition(energy), energy});
            }

            return result;
          }());
    }

    template <typename T = std::string>
    auto decode_samples(const std::vector<std::unordered_map<T, int>>& samples, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) const noexcept {
      auto result = std::vector<solution>{};

      std::transform(std::begin(samples), std::end(samples), std::back_inserter(result), [&](const auto& sample) {
        return decode_sample(sample, vartype, feed_dict);
      });

      return result;
    }
  };

  template <>
  inline auto model::to_bqm_parameters<int>(const std::unordered_map<std::string, double>& feed_dict) const noexcept { // メンバ関数を特殊化するときは、クラスの外に書かなければなりません。。。
    const auto evaluate = pyqubo::evaluate(feed_dict);

    auto linear = cimod::Linear<int, double>{};
    auto quadratic = cimod::Quadratic<int, double>{};
    auto offset = 0.0;

    for (const auto& [product, coefficient] : _quadratic_polynomial) {
      const auto coefficient_value = evaluate(coefficient);

      switch (std::size(product.indexes())) {
      case 0: {
        offset = coefficient_value; // 次数が0の項は1つにまとめられるので、この処理は最大で1回しか実行されません。なので、+=ではなくて=を使用しています。
        break;
      }
      case 1: {
        linear.emplace(product.indexes()[0], coefficient_value);
        break;
      }
      case 2: {
        quadratic.emplace(std::pair{product.indexes()[0], product.indexes()[1]}, coefficient_value);
        break;
      }
      default:
        throw std::runtime_error("invalid term."); // ここには絶対にこないはず。
      }
    }

    return std::tuple{linear, quadratic, offset};
  }

  template <>
  inline auto model::decode_sample<int>(const std::unordered_map<int, int>& sample, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) const noexcept {
    const auto evaluate = pyqubo::evaluate(feed_dict);
    const auto evaluate_polynomial = [&](const auto& polynomial, const auto& sample) {
      return std::accumulate(std::begin(polynomial), std::end(polynomial), 0.0, [&](const auto acc, const auto& term) {
        return acc +
               std::accumulate(std::begin(term.first.indexes()), std::end(term.first.indexes()), 1, [&](const auto acc, const auto& index) {
                 const auto value = sample.at(index);

                 return acc * (vartype == "BINARY" ? value : (value + 1) / 2);
               }) * evaluate(term.second);
      });
    };

    return solution(
        [&] {
          auto result = std::unordered_map<std::string, int>{};

          std::transform(std::begin(sample), std::end(sample), std::inserter(result, std::begin(result)), [&](const auto& index_and_value) {
            return std::pair{_variables.name(index_and_value.first), index_and_value.second};
          });

          return result;
        }(),
        energy<int>(sample, vartype, feed_dict),
        [&] {
          auto result = std::unordered_map<std::string, double>{};

          for (const auto& [name, polynomial] : _sub_hamiltonians) {
            result.emplace(name, evaluate_polynomial(polynomial, sample));
          }

          return result;
        }(),
        [&] {
          auto result = std::unordered_map<std::string, std::pair<bool, double>>{};

          for (const auto& [name, pair] : _constraints) {
            const auto& [polynomial, condition] = pair;
            const auto energy = evaluate_polynomial(polynomial, sample);

            result.emplace(name, std::pair{condition(energy), energy});
          }

          return result;
        }());
  }
}
