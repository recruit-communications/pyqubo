#pragma once

#include <algorithm>
#include <functional>
#include <iterator>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <tuple>
#include <utility>

#include <robin_hood.h>

#include "abstract_syntax_tree.hpp"
#include "product.hpp"
#include "variables.hpp"
#include "poly.hpp"

namespace pyqubo {
  // Expand to polynomial.

  // TODO: ペナルティを最後ではなく途中で足し合わせられるか検討する。もし途中で足し合わせられるなら、戻り値が一つになって嬉しい。

  class expand final {
    robin_hood::unordered_map<std::string, poly> _sub_hamiltonians;
    robin_hood::unordered_map<std::string, std::pair<poly, std::function<bool(double)>>> _constraints;
    variables* _variables;

  public:
    auto operator()(const std::shared_ptr<const expression>& expression, variables* variables) noexcept {
      _sub_hamiltonians = {};
      _constraints = {};
      _variables = variables;

      auto [polynomial, penalty] = visit<std::tuple<poly, poly>>(*this, expression);
      //polynomial = polynomial + penalty;
      //std::cout << polynomial.to_string() << std::endl;

      return std::tuple{polynomial, _sub_hamiltonians, _constraints};
    }

    auto operator()(const std::shared_ptr<const add_operator>& add_operator) noexcept {
      /*const auto& merge = [](auto& polyominal, const auto& other) {
        for (const auto& [product, coefficient] : other) {
          const auto [it, emplaced] = polyominal.emplace(product, coefficient);

          if (!emplaced) {
            it->second = it->second + coefficient;
          }
        }
      };*/

      auto polynomial = pyqubo::poly();
      auto penalty = pyqubo::poly();

      for (const auto& child: add_operator->children()) {
        auto [child_polynomial, child_penalty] = visit<std::tuple<pyqubo::poly, pyqubo::poly>>(*this, child);
        //std::cout << "add loop" << child_polynomial.to_string() << "\n";
        polynomial = polynomial + child_polynomial;
        penalty = penalty + child_penalty;
      }

      return std::tuple{polynomial, penalty};
    }

    auto operator()(const std::shared_ptr<const mul_operator>& mul_operator) noexcept {
      auto [l_polynomial, l_penalty] = visit<std::tuple<poly, poly>>(*this, mul_operator->lhs());
      auto [r_polynomial, r_penalty] = visit<std::tuple<poly, poly>>(*this, mul_operator->rhs());

      return std::tuple{l_polynomial * r_polynomial, l_penalty + r_penalty};
    }

    auto operator()(const std::shared_ptr<const binary_variable>& binary_variable) noexcept {
      auto p1 = poly(std::make_shared<numeric_literal>(1), new product({_variables->index(binary_variable->name())}));
      //std::cout << p1.to_string() << std::endl;
      return std::tuple{
        p1,
        poly()
      };
      //return std::tuple{polynomial{{{_variables->index(binary_variable->name())}, std::make_shared<numeric_literal>(1)}}, polynomial{}};
    }

    auto operator()(const std::shared_ptr<const spin_variable>& spin_variable) noexcept {
      polynomial* p = new polynomial{{
        {{_variables->index(spin_variable->name())}, std::make_shared<numeric_literal>(2)},
        {{}, std::make_shared<numeric_literal>(-1)}
      }};
      return std::tuple{poly(p), poly()};
    }

    auto operator()(const std::shared_ptr<const placeholder_variable>& place_holder_variable) noexcept {
      return std::tuple{
        poly(place_holder_variable, new product({})),
        //polynomial{{{}, place_holder_variable}},
        poly()
      };
    }

    auto operator()(const std::shared_ptr<const sub_hamiltonian>& sub_hamiltonian) noexcept {
      const auto [polynomial, penalty] = visit<std::tuple<pyqubo::poly, pyqubo::poly>>(*this, sub_hamiltonian->expression());
      //_sub_hamiltonians.emplace(sub_hamiltonian->name(), polynomial);
      return std::tuple{polynomial, penalty};
    }

    auto operator()(const std::shared_ptr<const constraint>& constraint) noexcept {
      const auto [polynomial, penalty] = visit<std::tuple<pyqubo::poly, pyqubo::poly>>(*this, constraint->expression());
      //_constraints.emplace(constraint->name(), std::pair{polynomial, constraint->condition()});
      return std::tuple{polynomial, penalty};
    }

    auto operator()(const std::shared_ptr<const with_penalty>& with_penalty) noexcept {
      auto [e_polynomial, e_penalty] = visit<std::tuple<poly, poly>>(*this, with_penalty->expression());
      auto [p_polynomial, p_penalty] = visit<std::tuple<poly, poly>>(*this, with_penalty->penalty());
      e_penalty = e_penalty + p_polynomial;
      e_penalty = e_penalty + p_penalty;
      //return std::tuple{e_polynomial, e_penalty + p_penalty + p_polynomial};
      return std::tuple{e_polynomial, e_penalty};
    }

    auto operator()(const std::shared_ptr<const user_defined_expression>& user_defined_expression) noexcept {
      return visit<std::tuple<poly, poly>>(*this, user_defined_expression->expression());
    }

    auto operator()(const std::shared_ptr<const numeric_literal>& numeric_literal) noexcept {
      return std::tuple{
        //polynomial{{{}, numeric_literal}},
        poly(numeric_literal, new product({})),
        poly()
      };
    }
  };

  // Convert to quadratic polynomial.

  inline std::optional<std::pair<int, int>> find_replacing_pair(const pyqubo::polynomial& polynomial) noexcept {
    auto counts = [&] {
      auto result = std::map<std::pair<int, int>, int>{};

      for (const auto& [product, _] : polynomial) {
        if (std::size(product.indexes()) <= 2) {
          continue;
        }

        for (auto it_1 = std::begin(product.indexes()); it_1 != std::prev(std::end(product.indexes())); ++it_1) {
          for (auto it_2 = std::next(it_1); it_2 != std::end(product.indexes()); ++it_2) {
            const auto [it, emplaced] = result.emplace(std::pair{*it_1, *it_2}, 1);

            if (!emplaced) {
              it->second++;
            }
          }
        }
      }

      return result;
    }();

    if (std::size(counts) == 0) {
      return std::nullopt;
    }

    const auto it = std::max_element(std::begin(counts), std::end(counts), [](const auto& count_1, const auto& count_2) {
      return count_1.second < count_2.second;
    });

    return it->first;
  }

  inline auto convert_to_quadratic(const pyqubo::polynomial& polynomial, double strength, variables* variables) noexcept {
    auto result = polynomial;

    for (;;) {
      const auto replacing_pair = find_replacing_pair(result);

      if (!replacing_pair) {
        break;
      }

      const auto replacing_pair_index = variables->index(variables->name(replacing_pair->first) + " * " + variables->name(replacing_pair->second));

      // replace.

      for (;;) {
        auto it = std::find_if(std::begin(result), std::end(result), [&](const auto& term) {
          return std::binary_search(std::begin(term.first.indexes()), std::end(term.first.indexes()), replacing_pair->first) && std::binary_search(std::begin(term.first.indexes()), std::end(term.first.indexes()), replacing_pair->second);
        });

        if (it == std::end(result)) {
          break;
        }

        const auto indexes = [&] {
          auto result = pyqubo::indexes{};

          std::copy_if(std::begin(it->first.indexes()), std::end(it->first.indexes()), std::back_inserter(result), [&](const auto& index) {
            return index != replacing_pair->first && index != replacing_pair->second;
          });

          result.emplace_back(replacing_pair_index);

          return result;
        }();
        const auto expression = it->second;

        result.erase(it);
        result.emplace(product(indexes), expression);
      }

      // insert.

      const auto emplace_term = [](pyqubo::polynomial& polynomial, const pyqubo::product& product, const std::shared_ptr<const expression>& coefficient) {
        const auto [it, emplaced] = polynomial.emplace(product, coefficient);

        if (!emplaced) {
          it->second = it->second + coefficient;
        }
      };

      // clang-format off
      emplace_term(result, product{replacing_pair_index                          }, std::make_shared<numeric_literal>(strength *  3));
      emplace_term(result, product{replacing_pair->first,  replacing_pair_index  }, std::make_shared<numeric_literal>(strength * -2));
      emplace_term(result, product{replacing_pair->second, replacing_pair_index  }, std::make_shared<numeric_literal>(strength * -2));
      emplace_term(result, product{replacing_pair->first,  replacing_pair->second}, std::make_shared<numeric_literal>(strength *  1));
      // clang-format on
    }

    return result;
  }
}
