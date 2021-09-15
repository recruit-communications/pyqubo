#include <algorithm>
#include <iostream>
#include <map>
#include <vector>

#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vartypes.hpp>

#include "abstract_syntax_tree.hpp"
#include "compiler.hpp"

namespace py = pybind11;
using namespace py::literals;

PYBIND11_MODULE(cpp_pyqubo, m) {
  m.doc() = "pyqubo C++ binding";

  py::class_<pyqubo::expression, std::shared_ptr<pyqubo::expression>>(m, "Base")
      .def("__add__", [](const std::shared_ptr<const pyqubo::expression>& expression, const std::shared_ptr<const pyqubo::expression>& other) {
        return expression + other;
      })
      .def("__add__", [](const std::shared_ptr<const pyqubo::expression>& expression, double other) {
        return expression + std::make_shared<const pyqubo::numeric_literal>(other);
      })
      .def("__radd__", [](const std::shared_ptr<const pyqubo::expression>& expression, double other) {
        return std::make_shared<const pyqubo::numeric_literal>(other) + expression;
      })
      .def("__sub__", [](const std::shared_ptr<const pyqubo::expression>& expression, const std::shared_ptr<const pyqubo::expression>& other) {
        return expression + std::make_shared<const pyqubo::numeric_literal>(-1) * other;
      })
      .def("__sub__", [](const std::shared_ptr<const pyqubo::expression>& expression, double other) {
        return expression + std::make_shared<const pyqubo::numeric_literal>(-other);
      })
      .def("__rsub__", [](const std::shared_ptr<const pyqubo::expression>& expression, double other) {
        return std::make_shared<const pyqubo::numeric_literal>(other) + std::make_shared<const pyqubo::numeric_literal>(-1) * expression;
      })
      .def("__mul__", [](const std::shared_ptr<const pyqubo::expression>& expression, const std::shared_ptr<const pyqubo::expression>& other) {
        return expression * other;
      })
      .def("__mul__", [](const std::shared_ptr<const pyqubo::expression>& expression, double other) {
        return expression * std::make_shared<const pyqubo::numeric_literal>(other);
      })
      .def("__rmul__", [](const std::shared_ptr<const pyqubo::expression>& expression, double other) {
        return std::make_shared<const pyqubo::numeric_literal>(other) * expression;
      })
      .def("__truediv__", [](const std::shared_ptr<const pyqubo::expression>& expression, double other) {
        if (other == 0) {
          throw std::runtime_error("zero divide error.");
        }

        return expression * std::make_shared<const pyqubo::numeric_literal>(1 / other);
      })
      .def("__pow__", [](const std::shared_ptr<const pyqubo::expression>& expression, int expotent) {
        if (expotent <= 0) {
          throw std::runtime_error("`exponent` should be positive.");
        }

        auto result = expression;

        for (auto i = 1; i < expotent; ++i) {
          result = result * expression;
        }

        return result;
      })
      .def("__neg__", [](const std::shared_ptr<const pyqubo::expression>& expression) {
        return std::make_shared<const pyqubo::numeric_literal>(-1) * expression;
      })
      .def(
          "compile", [](const std::shared_ptr<const pyqubo::expression>& expression, double strength) {
            return pyqubo::compile(expression, strength);
          },
          py::arg("strength") = 5)
      .def("__hash__", [](const pyqubo::expression& expression) { // 必要？
        return std::hash<pyqubo::expression>()(expression);
      })
      .def("__eq__", &pyqubo::expression::equals) // 必要？
      .def("__str__", &pyqubo::expression::to_string)
      .def("__repr__", &pyqubo::expression::to_string);

  py::class_<pyqubo::add_operator, std::shared_ptr<pyqubo::add_operator>, pyqubo::expression>(m, "Add")
      .def("__iadd__", [](std::shared_ptr<pyqubo::add_operator>& add_operator, const std::shared_ptr<const pyqubo::expression>& other) {
        add_operator->add_child(other);

        return add_operator;
      })
      .def("__iadd__", [](std::shared_ptr<pyqubo::add_operator>& add_operator, double other) {
        add_operator->add_child(std::make_shared<const pyqubo::numeric_literal>(other));

        return add_operator;
      });

  py::class_<pyqubo::binary_variable, std::shared_ptr<pyqubo::binary_variable>, pyqubo::expression>(m, "Binary")
      .def(py::init<const std::string&>());

  py::class_<pyqubo::spin_variable, std::shared_ptr<pyqubo::spin_variable>, pyqubo::expression>(m, "Spin")
      .def(py::init<const std::string&>());

  py::class_<pyqubo::placeholder_variable, std::shared_ptr<pyqubo::placeholder_variable>, pyqubo::expression>(m, "Placeholder")
      .def(py::init<const std::string&>());

  py::class_<pyqubo::sub_hamiltonian, std::shared_ptr<pyqubo::sub_hamiltonian>, pyqubo::expression>(m, "SubH")
      .def(py::init<const std::shared_ptr<const pyqubo::expression>&, const std::string&>(), py::arg("hamiltonian"), py::arg("label"));

  py::class_<pyqubo::constraint, std::shared_ptr<pyqubo::constraint>, pyqubo::expression>(m, "Constraint")
      .def(py::init<const std::shared_ptr<const pyqubo::expression>&, const std::string&, const std::function<bool(double)>&>(), py::arg("hamiltonian"), py::arg("label"), py::arg("condition") = py::cpp_function([](double x) { return x == 0; }));

  py::class_<pyqubo::with_penalty, std::shared_ptr<pyqubo::with_penalty>, pyqubo::expression>(m, "WithPenalty")
      .def(py::init<const std::shared_ptr<const pyqubo::expression>&, const std::shared_ptr<const pyqubo::expression>&, const std::string&>());

  py::class_<pyqubo::user_defined_expression, std::shared_ptr<pyqubo::user_defined_expression>, pyqubo::expression>(m, "UserDefinedExpress")
      .def(py::init<const std::shared_ptr<const pyqubo::expression>&>());

  py::class_<pyqubo::numeric_literal, std::shared_ptr<pyqubo::numeric_literal>, pyqubo::expression>(m, "Num")
      .def(py::init<double>());

  py::class_<pyqubo::solution>(m, "DecodedSample")
      .def_property_readonly("sample", &pyqubo::solution::sample)
      .def_property_readonly("energy", &pyqubo::solution::energy)
      .def_property_readonly("subh", [](const pyqubo::solution& solution) {
        auto result = solution.sub_hamiltonians();

        std::transform(std::begin(solution.constraints()), std::end(solution.constraints()), std::inserter(result, std::begin(result)), [](const auto& constraint) {
          return std::pair{constraint.first, constraint.second.second};
        });

        return result;
      })
      .def(
          "constraints", [](const pyqubo::solution& solution, bool only_broken) {
            auto constraints = solution.constraints();

            if (only_broken) {
              return [&] {
                auto result = std::unordered_map<std::string, std::pair<bool, double>>{};

                for (const auto& [name, value] : constraints) {
                  const auto& [not_broken, energy] = value;

                  if (not_broken) {
                    continue;
                  }

                  result.emplace(name, value);
                }

                return result;
              }();
            }

            return constraints;
          },
          py::arg("only_broken")=false)
      .def("array", [](const pyqubo::solution& solution, const std::string& name, int index) {
        return solution.sample().at(name + "[" + std::to_string(index) + "]");
      })
      .def("array", [](const pyqubo::solution& solution, const std::string& name, const py::tuple& indexes) {
        const auto name_and_indexes = [&] {
          auto result = name;

          for (const auto& index : indexes.cast<std::vector<int>>()) {
            result += "[" + std::to_string(index) + "]";
          }

          return result;
        }();

        return solution.sample().at(name_and_indexes);
      });
  py::class_<pyqubo::model>(m, "Model")
      .def_property_readonly("variables", &pyqubo::model::variable_names)
      .def(
          "to_bqm", [](const pyqubo::model& model, bool index_label, const std::unordered_map<std::string, double>& feed_dict) {
            const auto binary_quadratic_model = py::module::import("dimod").attr("BinaryQuadraticModel"); // dimodのPythonのBinaryQuadraticModelを作成します。cimodのPythonのBinaryQuadraticModelだと、dwave-nealで通らなかった……。
            const auto binary = py::module::import("dimod").attr("Vartype").attr("BINARY");

            if (!index_label) {
              const auto [linear, quadratic, offset] = model.to_bqm_parameters<std::string>(feed_dict);
              return binary_quadratic_model(linear, quadratic, offset, binary);
            } else {
              const auto [linear, quadratic, offset] = model.to_bqm_parameters<int>(feed_dict);
              return binary_quadratic_model(linear, quadratic, offset, binary);
            }
          },
          py::arg("index_label") = false, py::arg("feed_dict") = std::unordered_map<std::string, double>{})
      .def(
          "to_qubo", [](const pyqubo::model& model, bool index_label, const std::unordered_map<std::string, double>& feed_dict) {
            if (!index_label) {
              return py::cast(model.to_bqm<std::string>(feed_dict, cimod::Vartype::BINARY).to_qubo());
            } else {
              return py::cast(model.to_bqm<int>(feed_dict, cimod::Vartype::BINARY).to_qubo());
            }
          },
          py::arg("index_label") = false, py::arg("feed_dict") = std::unordered_map<std::string, double>{})
      .def(
          "to_ising", [](const pyqubo::model& model, bool index_label, const std::unordered_map<std::string, double>& feed_dict) {
            if (!index_label) {
              return py::cast(model.to_bqm<std::string>(feed_dict, cimod::Vartype::BINARY).to_ising());
            } else {
              return py::cast(model.to_bqm<int>(feed_dict, cimod::Vartype::BINARY).to_ising());
            }
          },
          py::arg("index_label") = false, py::arg("feed_dict") = std::unordered_map<std::string, double>{})
      .def(
          "energy", [](const pyqubo::model& model, const py::object& sample, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) {
            try {
              return model.energy(sample.cast<std::unordered_map<std::string, int>>(), vartype, feed_dict);
            } catch (...) {
              ;
            }

            try {
              return model.energy(sample.cast<std::unordered_map<int, int>>(), vartype, feed_dict);
            } catch (...) {
              ;
            }

            throw std::runtime_error("invalid sample");
          },
          py::arg("sample"), py::arg("vartype"), py::arg("feed_dict") = std::unordered_map<std::string, double>{})
      .def(
          "decode_sample", [](const pyqubo::model& model, const py::object& sample, const std::string& vartype, const std::unordered_map<std::string, double>& feed_dict) {
            try {
              return model.decode_sample(sample.cast<std::unordered_map<std::string, int>>(), vartype, feed_dict);
            } catch (...) {
              ;
            }

            try {
              return model.decode_sample(sample.cast<std::unordered_map<int, int>>(), vartype, feed_dict);
            } catch (...) {
              ;
            }

            try {
              return model.decode_sample([&] {
                auto result = std::unordered_map<int, int>{};

                const auto v = sample.cast<std::vector<int>>();
                for (auto i = 0; i < static_cast<int>(std::size(v)); ++i) {
                  result.emplace(i, v[i]);
                }

                return result;
              }(), vartype, feed_dict);
            } catch (...) {
              ;
            }

            throw std::runtime_error("invalid sample");
          },
          py::arg("sample"), py::arg("vartype"), py::arg("feed_dict") = std::unordered_map<std::string, double>{})
      .def(
          "decode_sampleset", [](const pyqubo::model& model, const py::object& sampleset, const std::unordered_map<std::string, double>& feed_dict) {
            sampleset.attr("record").attr("sort")("order"_a = "energy");

            const auto array = sampleset.attr("record")["sample"].cast<py::array_t<std::int8_t>>();
            const auto info = array.request();

            if (info.format != py::format_descriptor<int8_t>::format() || info.ndim != 2) {
              throw std::runtime_error("Incompatible buffer format!");
            }

            try {
              const auto variables = sampleset.attr("variables").cast<std::vector<std::string>>();

              const auto samples = [&] {
                auto result = std::vector<std::unordered_map<std::string, int>>(info.shape[0]);

                for (auto i = 0; i < info.shape[0]; ++i) {
                  for (auto j = 0; j < info.shape[1]; ++j) {
                    result[i].emplace(variables[j], *array.data(i, j));
                  }
                }

                return result;
              }();

              return model.decode_samples(samples, sampleset.attr("vartype").attr("name").cast<std::string>(), feed_dict);
            } catch (...) {
              ;
            }

            try {
              const auto samples = [&] {
                auto result = std::vector<std::unordered_map<int, int>>(info.shape[0]);

                for (auto i = 0; i < info.shape[0]; ++i) {
                  for (auto j = 0; j < info.shape[1]; ++j) {
                    result[i].emplace(j, *array.data(i, j));
                  }
                }

                return result;
              }();

              return model.decode_samples(samples, sampleset.attr("vartype").attr("name").cast<std::string>(), feed_dict);
            } catch (...) {
              ;
            }

            throw std::runtime_error("invalid sample");
          },
          py::arg("sampleset"), py::arg("feed_dict") = std::unordered_map<std::string, double>{});
}
