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
#include "expand.hpp"
#include "product.hpp"
#include "variables.hpp"

namespace pyqubo {
    // Compile.
  inline auto compile(const std::shared_ptr<const expression>& express, const std::shared_ptr<const expression>& strength) noexcept {
    auto variables = pyqubo::variables();

    const auto [polynomial, sub_hamiltonians, constraints] = expand()(express, &variables);
    
    //std::cout << "compile" << polynomial.to_string() << std::endl;
    const auto quadratic_polynomial = convert_to_quadratic(*(polynomial.get_terms()), strength, &variables);
    
    
    /*for(auto [key, val]: quadratic_polynomial){
      std::cout << "quadratic_polynomial " << key.to_string() << ", " << val->to_string() << std::endl;
    }

    for(auto [key, val]: sub_hamiltonians){
      std::cout << "sub_hamiltonians " << key << ", " << val.to_string() << std::endl;
    }*/
    
    return model(quadratic_polynomial, sub_hamiltonians, constraints, variables);
  }
}