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
#include "expand.hpp"
#include "product.hpp"
#include "variables.hpp"


namespace pyqubo {


  class evaluate final {
    std::unordered_map<std::string, double> _feed_dict;

  public:
    evaluate(const std::unordered_map<std::string, double>& feed_dict) : _feed_dict(feed_dict) {
      ;
    }

    auto operator()(const std::shared_ptr<const expression>& expression) const {
      return visit<double>(*this, expression);
    }

    auto operator()(const std::shared_ptr<const add_operator>& add_operator) const {
      double acc = 0.0;
      add_list* next_node = add_operator->node;
      while(next_node != nullptr){
        acc = acc + visit<double>(*this, next_node->value);
        next_node = next_node->next;
      }
      return acc;
      /*return std::accumulate(std::begin(add_operator->children()), std::end(add_operator->children()), 0.0, [&](const auto& acc, const auto& child) {
        return acc + visit<double>(*this, child);
      });*/
    }

    auto operator()(const std::shared_ptr<const mul_operator>& mul_operator) const {
      return visit<double>(*this, mul_operator->lhs()) * visit<double>(*this, mul_operator->rhs());
    }

    auto operator()(const std::shared_ptr<const placeholder_variable>& place_holder_variable) const {
      
      auto found = _feed_dict.find(place_holder_variable->name());
      if(found != _feed_dict.end()){
        return found->second;
      }else{
        std::string err_msg = "the value of " + place_holder_variable->name() + " is not provided in feed_dict.";
        throw std::invalid_argument(err_msg);
        return 0.0;
      }
    }

    auto operator()(const std::shared_ptr<const user_defined_expression>& user_defined_expression) const {
      return visit<double>(*this, user_defined_expression->expression());
    }

    auto operator()(const std::shared_ptr<const numeric_literal>& numeric_literal) const {
      return numeric_literal->value();
    }
  };


  class solution final {
    std::unordered_map<std::string, int> _sample;
    double _energy;
    std::unordered_map<std::string, double> _sub_hamiltonians;
    std::unordered_map<std::string, std::pair<bool, double>> _constraints;
    const std::unordered_map<std::string, double> _feed_dict;
    const std::string _vartype;
    variables _variables;

  public:
    solution(
      const std::unordered_map<std::string, int> sample,
      double energy,
      const std::unordered_map<std::string, double>& sub_hamiltonians,
      const std::unordered_map<std::string, std::pair<bool, double>>& constraints,
      const std::unordered_map<std::string, double> feed_dict,
      const std::string vartype,
      variables variables
    ) noexcept :
      _sample(sample),
      _energy(energy),
      _sub_hamiltonians(sub_hamiltonians),
      _constraints(constraints),
      _feed_dict(feed_dict),
      _vartype(vartype),
      _variables(variables) {
      ;
    }

    std::string to_string(){
      std::string s = "DecodedSolution({";
      int counter = 0;
      for(auto [k, v]: _sample){
        s += k + ":" + std::to_string(v);
        if(counter != _sample.size() - 1){
          s += ", ";
        }
        counter ++;
      }
      s += "}, energy=" + std::to_string(_energy) + ")";
      return s;
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

    auto evaluate(const std::shared_ptr<const expression>& expression) {

      const auto [polynomial, sub_hamiltonians, constraints] = pyqubo::expand()(expression, &_variables);
      //std::cout << _variables.to_string();
      //std::cout << "compile" << polynomial.to_string() << std::endl;
      auto& poly_terms = *polynomial.terms;

      const auto evaluate = pyqubo::evaluate(_feed_dict);
      const auto evaluate_polynomial = [&](const auto& poly_terms) {
        return std::accumulate(std::begin(poly_terms), std::end(poly_terms), 0.0, [&](const auto acc, const auto& term) {
          return acc +
                 std::accumulate(std::begin(term.first.indexes()), std::end(term.first.indexes()), 1, [&](const auto acc, const auto& index) {
                   const auto value = _sample.at(_variables.name(index));
                   return acc * (_vartype == "BINARY" ? value : (value + 1) / 2);
                 }) * evaluate(term.second);
        });
      };
      const auto energy = evaluate_polynomial(poly_terms);

      // check constraints
      for (const auto& [name, pair] : constraints) {
        const auto& [polynomial, condition] = pair;
        auto& const_poly_terms = *polynomial.terms;
        const auto const_energy = evaluate_polynomial(const_poly_terms);
        if(const_energy > 0){
          throw std::runtime_error("constraint: " + name + " is broken.");
        }
      }
      return energy;
    }
  };

  class model final {
    const polynomial _quadratic_polynomial;
    robin_hood::unordered_map<std::string, poly> _sub_hamiltonians; // コンパイル中にpolyのコピーをしたかチェック
    robin_hood::unordered_map<std::string, std::pair<poly, std::function<bool(double)>>> _constraints;
    variables _variables;

    static auto to_cimod_vartype(const std::string vartype) noexcept {
      return vartype == "BINARY" ? cimod::Vartype::BINARY : cimod::Vartype::SPIN;
    }

  public:
    model(const polynomial &quadratic_polynomial, const robin_hood::unordered_map<std::string, poly>& sub_hamiltonians, const robin_hood::unordered_map<std::string, std::pair<poly, std::function<bool(double)>>>& constraints, const variables& variables) noexcept : _quadratic_polynomial(quadratic_polynomial), _sub_hamiltonians(sub_hamiltonians), _constraints(constraints), _variables(variables) {
      ;
    }

    std::vector<std::string> variable_names() const noexcept {
      return _variables.names();
    }

    template <typename T = std::string>
    auto to_bqm_parameters(const std::unordered_map<std::string, double>& feed_dict) const { // 不格好でごめんなさい。PythonのBinaryQuadraticModelを作成可能にするために、このメンバ関数でBinaryQuadraticModelの引数を生成します。
      //throw std::runtime_error("test to_qubo.");
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
    auto to_bqm(const std::unordered_map<std::string, double>& feed_dict, cimod::Vartype vartype) const {
      const auto [linear, quadratic, offset] = to_bqm_parameters<T>(feed_dict);

      return cimod::BinaryQuadraticModel<T, double, cimod::Dense>(linear, quadratic, offset, vartype);
    }

    auto to_qubo_int(const std::unordered_map<std::string, double>& feed_dict) const {

      const auto evaluate = pyqubo::evaluate(feed_dict);
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
          if(coefficient_value != 0.0){
            quadratic.emplace(std::pair{product.indexes()[0], product.indexes()[0]}, coefficient_value);
          }
          break;
        }
        case 2: {
          if(coefficient_value != 0.0){
            quadratic.emplace(std::pair{product.indexes()[0], product.indexes()[1]}, coefficient_value);
          }
          break;
        }
        default:
          throw std::runtime_error("invalid term.");
        }
      }

      return std::make_tuple(quadratic, offset);
    }

    auto to_qubo_string(const std::unordered_map<std::string, double>& feed_dict) const {

      const auto evaluate = pyqubo::evaluate(feed_dict);

      auto quadratic = cimod::Quadratic<std::string, double>{};
      auto offset = 0.0;

      for (const auto& [product, coefficient] : _quadratic_polynomial) {
        const auto coefficient_value = evaluate(coefficient);

        switch (std::size(product.indexes())) {
        case 0: {
          offset = coefficient_value; // 次数が0の項は1つにまとめられるので、この処理は最大で1回しか実行されません。なので、+=ではなくて=を使用しています。
          break;
        }
        case 1: {
          if(coefficient_value != 0.0){
            quadratic.emplace(std::pair{_variables.name(product.indexes()[0]), _variables.name(product.indexes()[0])}, coefficient_value);
          }
          break;
        }
        case 2: {
          if(coefficient_value != 0.0){
            quadratic.emplace(std::pair{_variables.name(product.indexes()[0]), _variables.name(product.indexes()[1])}, coefficient_value);
          }
          break;
        }
        default:
          throw std::runtime_error("invalid term."); // ここには絶対にこないはず。
        }
      }

      return std::make_tuple(quadratic, offset);
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
    auto decode_sample(const std::unordered_map<T, int>& sample, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) const {
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
              result.emplace(name, evaluate_polynomial(*polynomial.get_terms(), sample));
            }

            return result;
          }(),
          [&] {
            auto result = std::unordered_map<std::string, std::pair<bool, double>>{};

            for (const auto& [name, pair] : _constraints) {
              const auto& [polynomial, condition] = pair;
              const auto energy = evaluate_polynomial(*polynomial.get_terms(), sample);

              result.emplace(name, std::pair{condition(energy), energy});
            }

            return result;
          }(),
          feed_dict,
          vartype,
          _variables);
    }

    template <typename T = std::string>
    auto decode_samples(const std::vector<std::unordered_map<T, int>>& samples, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) const {
      auto result = std::vector<solution>{};

      std::transform(std::begin(samples), std::end(samples), std::back_inserter(result), [&](const auto& sample) {
        return decode_sample(sample, vartype, feed_dict);
      });

      return result;
    }
  };

  template <>
  inline auto model::to_bqm_parameters<int>(const std::unordered_map<std::string, double>& feed_dict) const { // メンバ関数を特殊化するときは、クラスの外に書かなければなりません。。。
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
  inline auto model::decode_sample<int>(const std::unordered_map<int, int>& sample, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) const {
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
            result.emplace(name, evaluate_polynomial(*polynomial.get_terms(), sample));
          }

          return result;
        }(),
        [&] {
          auto result = std::unordered_map<std::string, std::pair<bool, double>>{};

          for (const auto& [name, pair] : _constraints) {
            const auto& [polynomial, condition] = pair;
            const auto energy = evaluate_polynomial(*polynomial.get_terms(), sample);

            result.emplace(name, std::pair{condition(energy), energy});
          }

          return result;
        }(),
        feed_dict,
        vartype,
        _variables);
  }
}
