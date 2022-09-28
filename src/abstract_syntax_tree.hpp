#pragma once

#include <algorithm>
#include <cstddef>
#include <functional>
#include <memory>
#include <string>
#include <vector>
#include <numeric>

#include <boost/functional/hash.hpp>
#include "linkedlist.hpp"


namespace pyqubo {
  enum class expression_type {
    add_operator,
    mul_operator,
    binary_variable,
    spin_variable,
    place_holder_variable,
    sub_hamiltonian,
    constraint,
    with_penalty,
    user_defined_expression,
    numeric_literal
  };

  class expression {
  public:
    virtual ~expression() {
      ;
    }

    virtual pyqubo::expression_type expression_type() const noexcept = 0;

    virtual std::string to_string() const noexcept = 0;

    virtual std::size_t hash() const noexcept = 0;

    virtual bool equals(const std::shared_ptr<const expression>& other) const noexcept {
      return expression_type() == other->expression_type();
    };

    friend std::hash<expression>;
  };
}

namespace std {
  template <>
  struct hash<pyqubo::expression> {
    auto operator()(const pyqubo::expression& expression) const noexcept {
      return expression.hash();
    }
  };
}

namespace pyqubo {

  using add_list = LinkedList<std::shared_ptr<const expression>>;

  class add_operator final : public expression {    

  public:
    pyqubo::add_list* node;

    add_operator(const std::shared_ptr<const expression>& lhs, const std::shared_ptr<const expression>& rhs) noexcept {
      this->node = new pyqubo::add_list(lhs);
      this->node->next = new pyqubo::add_list(rhs);
    }

    auto create_node(const std::shared_ptr<const add_operator> add, const std::shared_ptr<const expression> new_child){
        auto new_node = new pyqubo::add_list(new_child, add->node);
        return new_node;
    }

    add_operator(const std::shared_ptr<const add_operator> add, const std::shared_ptr<const expression> child):
        node(create_node(add, child)){}

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::add_operator;
    }

    std::string to_string() const noexcept override {
      std::string s;
      s += "(";
      pyqubo::add_list* next_node = this->node;
      int i = 0;
      std::string sep = " + ";
      while(next_node != nullptr){
          s += next_node->value->to_string();
          s += sep;
          next_node = next_node->next;
          i++;
      }
      for(int j=0;j<sep.size();j++) s.pop_back();
      s += ")";
      //printf("to_string cnt %d\n", i);
      return s;
    }

    std::size_t hash() const noexcept override {
      auto result = static_cast<std::size_t>(0);
      boost::hash_combine(result, "+");
      return result;
    }

    bool equals(const std::shared_ptr<const expression>& other) const noexcept override {
      if(expression::equals(other)){
        pyqubo::add_list* other_next_node = std::static_pointer_cast<const add_operator>(other)->node;
        pyqubo::add_list* next_node = this->node;
        while(next_node != nullptr && other_next_node != nullptr){
            if(!next_node->value->equals(other_next_node->value)){
              return false;
            }
            next_node = next_node->next;
            other_next_node = other_next_node->next;
        }
        if(next_node == nullptr && other_next_node == nullptr){
          return true;
        }else{
          return false;
        }
      }else{
        return false;
      }
    }
  };

  class mul_operator final : public expression {
    std::shared_ptr<const expression> _lhs;
    std::shared_ptr<const expression> _rhs;

  public:
    mul_operator(const std::shared_ptr<const expression>& lhs, const std::shared_ptr<const expression>& rhs) noexcept : _lhs(lhs), _rhs(rhs) {
      ;
    }

    const auto& lhs() const noexcept {
      return _lhs;
    }

    const auto& rhs() const noexcept {
      return _rhs;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::mul_operator;
    }

    std::string to_string() const noexcept override {
      return "(" + lhs()->to_string() + " * " + rhs()->to_string() + ")";
    }

    std::size_t hash() const noexcept override {
      auto result = static_cast<std::size_t>(0);

      boost::hash_combine(result, "*");
      boost::hash_combine(result, std::hash<expression>()(*_lhs));
      boost::hash_combine(result, std::hash<expression>()(*_rhs));

      return result;
    }

    bool equals(const std::shared_ptr<const expression>& other) const noexcept override {
      return expression::equals(other) && _lhs->equals(std::static_pointer_cast<const mul_operator>(other)->_lhs) && _rhs->equals(std::static_pointer_cast<const mul_operator>(other)->_rhs);
    }
  };

  class variable : public expression {
    std::string _name;

  protected:
    variable(const std::string& name) noexcept : _name(name) {
      ;
    }

  public:
    const auto& name() const noexcept {
      return _name;
    }

    std::size_t hash() const noexcept override {
      return std::hash<std::string>()(_name);
    }

    bool equals(const std::shared_ptr<const expression>& other) const noexcept override {
      return expression::equals(other) && _name == std::static_pointer_cast<const variable>(other)->_name;
    }
  };

  class binary_variable final : public variable {
  public:
    binary_variable(const std::string& name) noexcept : variable(name) {
      ;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::binary_variable;
    }

    std::string to_string() const noexcept override {
      return "Binary('" + name() + "')";
    }

    std::size_t hash() const noexcept override {
      auto result = variable::hash();

      boost::hash_combine(result, "binary_variable");

      return result;
    }
  };

  class spin_variable final : public variable {
  public:
    spin_variable(const std::string& name) noexcept : variable(name) {
      ;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::spin_variable;
    }

    std::string to_string() const noexcept override {
      return "Spin('" + name() + "')";
    }

    std::size_t hash() const noexcept override {
      auto result = variable::hash();

      boost::hash_combine(result, "spin_variable");

      return result;
    }
  };

  class placeholder_variable final : public variable {
  public:
    placeholder_variable(const std::string& name) noexcept : variable(name) {
      ;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::place_holder_variable;
    }

    std::string to_string() const noexcept override {
      return "Placeholder('" + name() + "')";
    }

    std::size_t hash() const noexcept override {
      auto result = variable::hash();

      boost::hash_combine(result, "placeholder_variable");

      return result;
    }
  };

  class sub_hamiltonian : public variable {
    

  public:
    sub_hamiltonian(const std::shared_ptr<const pyqubo::expression>& expression, const std::string& name) noexcept : variable(name), _expression(expression) {
      ;
    }

    const auto& expression() const noexcept {
      return _expression;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::sub_hamiltonian;
    }

    std::string to_string() const noexcept override {
      return "SubH(" + _expression->to_string() + ", '" + name() + "')";
    }

    std::size_t hash() const noexcept override {
      auto result = variable::hash();
      boost::hash_combine(result, "sub_hamiltonian");
      boost::hash_combine(result, std::hash<pyqubo::expression>()(*_expression));
      return result;
    }

    bool equals(const std::shared_ptr<const pyqubo::expression>& other) const noexcept override {
      return variable::equals(other) && _expression->equals(std::static_pointer_cast<const sub_hamiltonian>(other)->_expression);
    }

  protected:
    std::shared_ptr<const pyqubo::expression> _expression;
  };

  class constraint final : public sub_hamiltonian {
    std::function<bool(double)> _condition;

  public:
    constraint(
        const std::shared_ptr<const pyqubo::expression>& expression, const std::string& name, const std::function<bool(double)>& condition) noexcept : sub_hamiltonian(expression, name), _condition(condition) {
      ;
    }

    const auto& condition() const noexcept {
      return _condition;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::constraint;
    }

    std::string to_string() const noexcept override {
      return "Constraint(" + expression()->to_string() + ", '" + name() + "')";
    }

    std::size_t hash() const noexcept override {
      auto result = variable::hash();

      boost::hash_combine(result, "constraint");

      return result;
    }
  };

  class with_penalty : public sub_hamiltonian {
    std::shared_ptr<const pyqubo::expression> _penalty;

  public:
    with_penalty(const std::shared_ptr<const pyqubo::expression>& expression, const std::shared_ptr<const pyqubo::expression>& penalty, const std::string& name) noexcept : sub_hamiltonian(expression, name), _penalty(penalty) {
      ;
    }

    const auto& penalty() const noexcept {
      return _penalty;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::with_penalty;
    }

    std::string to_string() const noexcept override {
      return "WithPenalty(" + expression()->to_string() + ", " + _penalty->to_string() + ", '" + name() + "')";
    }

    std::size_t hash() const noexcept override {
      auto result = sub_hamiltonian::hash();

      boost::hash_combine(result, "with_penalty");
      boost::hash_combine(result, std::hash<pyqubo::expression>()(*_penalty));

      return result;
    }

    bool equals(const std::shared_ptr<const pyqubo::expression>& other) const noexcept override {
      return sub_hamiltonian::equals(other) && _penalty->equals(std::static_pointer_cast<const with_penalty>(other)->_penalty);
    }
  };

  class user_defined_expression : public expression {
    std::shared_ptr<const expression> _expression;

  public:
    user_defined_expression(const std::shared_ptr<const pyqubo::expression>& expression) noexcept : _expression(expression) {
      ;
    }

    auto expression() const noexcept {
      return _expression;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::user_defined_expression;
    }

    std::string to_string() const noexcept override {
      return _expression->to_string();
    }

    std::size_t hash() const noexcept override {
      return std::hash<pyqubo::expression>()(*_expression);
    }

    bool equals(const std::shared_ptr<const pyqubo::expression>& other) const noexcept override {
      return expression::equals(other) && _expression->equals(std::static_pointer_cast<const user_defined_expression>(other)->_expression);
    }
  };

  class numeric_literal final : public expression {
    double _value;

  public:
    numeric_literal(double value) noexcept : _value(value) {
      ;
    }

    auto value() const noexcept {
      return _value;
    }

    pyqubo::expression_type expression_type() const noexcept override {
      return expression_type::numeric_literal;
    }

    std::string to_string() const noexcept override {
      return std::to_string(_value);
    }

    std::size_t hash() const noexcept override {
      return std::hash<double>()(_value);
    }

    bool equals(const std::shared_ptr<const expression>& other) const noexcept override {
      return expression::equals(other) && _value == std::static_pointer_cast<const numeric_literal>(other)->_value;
    }
  };

  inline std::shared_ptr<const expression> operator+(const std::shared_ptr<const expression>& lhs, const std::shared_ptr<const expression>& rhs) noexcept {
    if (lhs->expression_type() == expression_type::numeric_literal && rhs->expression_type() == expression_type::numeric_literal) {
      double left_value = std::static_pointer_cast<const numeric_literal>(lhs)->value();
      double right_value = std::static_pointer_cast<const numeric_literal>(rhs)->value();
      return std::make_shared<numeric_literal>(left_value + right_value);
    }

    
    /*if (lhs->expression_type() == expression_type::numeric_literal && std::static_pointer_cast<const numeric_literal>(lhs)->value() == 0) {
      return rhs;
    }

    if (rhs->expression_type() == expression_type::numeric_literal && std::static_pointer_cast<const numeric_literal>(rhs)->value() == 0) {
      return lhs;
    }*/
    

    return std::make_shared<const add_operator>(lhs, rhs);
  }

  inline std::shared_ptr<const expression> operator*(const std::shared_ptr<const expression>& lhs, const std::shared_ptr<const expression>& rhs) noexcept {
    /*if(lhs->expression_type() != expression_type::numeric_literal && rhs->expression_type() != expression_type::numeric_literal){
      return std::make_shared<const mul_operator>(lhs, rhs);
    }else if (lhs->expression_type() == expression_type::numeric_literal){
      if (rhs->expression_type() == expression_type::numeric_literal) {
        return std::make_shared<numeric_literal>(std::static_pointer_cast<const numeric_literal>(lhs)->value() * std::static_pointer_cast<const numeric_literal>(rhs)->value());
      }else if (std::static_pointer_cast<const numeric_literal>(lhs)->value() == 1) {
        return rhs;
      }else{
        return std::make_shared<const mul_operator>(lhs, rhs);
      }
    } else if (rhs->expression_type() == expression_type::numeric_literal){
      if (std::static_pointer_cast<const numeric_literal>(rhs)->value() == 1) {
        return lhs;
      }else{
        return std::make_shared<const mul_operator>(lhs, rhs);
      }
    }*/
    // constant times constant
    if (lhs->expression_type() == expression_type::numeric_literal && rhs->expression_type() == expression_type::numeric_literal) {
      return std::make_shared<numeric_literal>(
        std::static_pointer_cast<const numeric_literal>(lhs)->value() * std::static_pointer_cast<const numeric_literal>(rhs)->value());
    }else{
      return std::make_shared<const mul_operator>(lhs, rhs);
    }
    
    //return std::make_shared<const mul_operator>(lhs, rhs);
  }

  inline std::shared_ptr<const expression> multiply_express(const std::shared_ptr<const expression>& lhs, const std::shared_ptr<const expression>& rhs) noexcept {
    return std::make_shared<const mul_operator>(lhs, rhs);
  }

  template <typename Result, typename Functor>
  Result visit(Functor& functor, const std::shared_ptr<const expression>& expression) {
    switch (expression->expression_type()) {
    case expression_type::add_operator:
      return functor(std::static_pointer_cast<const add_operator>(expression));

    case expression_type::mul_operator:
      return functor(std::static_pointer_cast<const mul_operator>(expression));

    case expression_type::binary_variable:
      return functor(std::static_pointer_cast<const binary_variable>(expression));

    case expression_type::spin_variable:
      return functor(std::static_pointer_cast<const spin_variable>(expression));

    case expression_type::place_holder_variable:
      return functor(std::static_pointer_cast<const placeholder_variable>(expression));

    case expression_type::sub_hamiltonian:
      return functor(std::static_pointer_cast<const sub_hamiltonian>(expression));

    case expression_type::constraint:
      return functor(std::static_pointer_cast<const constraint>(expression));

    case expression_type::with_penalty:
      return functor(std::static_pointer_cast<const with_penalty>(expression));

    case expression_type::user_defined_expression:
      return functor(std::static_pointer_cast<const user_defined_expression>(expression));

    case expression_type::numeric_literal:
      return functor(std::static_pointer_cast<const numeric_literal>(expression));

    default:
      throw std::runtime_error("invalid expression type."); // ここには絶対に来ないはず。
    }
  }
}
