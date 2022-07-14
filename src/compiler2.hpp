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
#include "model.hpp"
#include "compiler.hpp"
#include "product.hpp"
#include "variables.hpp"

namespace pyqubo {
    // Compile.
  inline auto compile(const std::shared_ptr<const expression>& expression, double strength) noexcept {
    auto variables = pyqubo::variables();

    const auto [polynomial, sub_hamiltonians, constraints] = expand()(expression, &variables);
    
    //std::cout << "compile" << polynomial.to_string() << std::endl;
    //const auto quadratic_polynomial = convert_to_quadratic(*polynomial.to_multi().terms, strength, &variables);
    return model(polynomial.get_terms(), sub_hamiltonians, constraints, variables);
  }
}