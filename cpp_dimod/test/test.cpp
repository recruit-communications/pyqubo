#include "gtest/gtest.h"

#include "../binary_quadratic_model.hpp"
#include "../vartypes.hpp"
#include "../hash.hpp"

#include <unordered_map>
#include <utility>
#include <vector>
#include <cstdint>
#include <string>
#include <iostream>
#include <tuple>

namespace
{
    TEST(ConstructionTest, Construction)
    {
        Linear<uint32_t> linear{ {1, 1.0}, {2, 2.0}, {3, 3.0}, {4, 4.0} };
        Quadratic<uint32_t> quadratic
        {
            {std::make_pair(1, 2), 12.0}, {std::make_pair(1, 3), 13.0}, {std::make_pair(1, 4), 14.0},
            {std::make_pair(2, 3), 23.0}, {std::make_pair(2, 4), 24.0},
            {std::make_pair(3, 4), 34.0}
        };
        double offset = 0.0;
        Vartype vartype = Vartype::BINARY;

        BinaryQuadraticModel<uint32_t> bqm_k4(linear, quadratic, offset, vartype);

        Linear<uint32_t> bqm_linear = bqm_k4.get_linear();
        Quadratic<uint32_t> bqm_quadratic = bqm_k4.get_quadratic();
        double bqm_offset = bqm_k4.get_offset();
        Vartype bqm_vartype = bqm_k4.get_vartype();

        // check linear
        for(auto &it : bqm_linear)
        {
            EXPECT_EQ(it.second, linear[it.first]);
        }
        // check quadratic
        for(auto &it : bqm_quadratic)
        {
            EXPECT_EQ(it.second, quadratic[it.first]);
        }
        // check offset
        EXPECT_EQ(offset, bqm_offset);
        // check vartype
        EXPECT_EQ(vartype, bqm_vartype);
    }

    TEST(ConstructionTest, ConstructionString)
    {
        Linear<std::string> linear{ {"a", 1.0}, {"b", 2.0}, {"c", 3.0}, {"d", 4.0} };
        Quadratic<std::string> quadratic
        {
            {std::make_pair("a", "b"), 12.0}, {std::make_pair("a", "c"), 13.0}, {std::make_pair("a", "d"), 14.0},
            {std::make_pair("b", "c"), 23.0}, {std::make_pair("b", "d"), 24.0},
            {std::make_pair("c", "d"), 34.0}
        };
        double offset = 0.0;
        Vartype vartype = Vartype::BINARY;

        BinaryQuadraticModel<std::string> bqm_k4(linear, quadratic, offset, vartype, "BQM_Binary");

        bqm_k4.print();

        Linear<std::string> bqm_linear = bqm_k4.get_linear();
        Quadratic<std::string> bqm_quadratic = bqm_k4.get_quadratic();
        double bqm_offset = bqm_k4.get_offset();
        Vartype bqm_vartype = bqm_k4.get_vartype();

        // check linear
        for(auto &it : bqm_linear)
        {
            EXPECT_EQ(it.second, linear[it.first]);
        }
        // check quadratic
        for(auto &it : bqm_quadratic)
        {
            EXPECT_EQ(it.second, quadratic[it.first]);
        }
        // check offset
        EXPECT_EQ(offset, bqm_offset);
        // check vartype
        EXPECT_EQ(vartype, bqm_vartype);
    }

    TEST(FunctionTest, add_variable)
    {
        Linear<uint32_t> linear{ {0, 0.0}, {1, 1.0} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(0, 1), 0.5} };
        double offset = -0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        // check length
        EXPECT_EQ(bqm.length(), 2);

        bqm.add_variable(2, 2.0, Vartype::SPIN);
        bqm.add_variable(1, 0.33, Vartype::SPIN);
        bqm.add_variable(0, 0.33, Vartype::BINARY);

        Linear<uint32_t> bqm_linear = bqm.get_linear();

        // check length
        EXPECT_EQ(bqm.length(), 3);
        // check linear
        EXPECT_EQ(bqm_linear[1], 1.33);
    }

    TEST(FunctionTest, add_variables_from)
    {
        Linear<uint32_t> linear;
        Quadratic<uint32_t> quadratic;
        double offset = 0.0;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        // check length
        EXPECT_EQ(bqm.length(), 0);

        Linear<uint32_t> linear2 = { {0, 0.5}, {1, -1.0} };
        Linear<uint32_t> linear3 = { {1, -1.0}, {2, 2.0} };

        bqm.add_variables_from(linear2, Vartype::SPIN);
        // check variable
        EXPECT_EQ(bqm.contains(1), true);

        bqm.add_variables_from(linear3);

        // check bias
        Linear<uint32_t> bqm_linear = bqm.get_linear();
        EXPECT_EQ(bqm_linear[1], -2.0);
    }

    TEST(FunctionTest, add_interaction)
    {
        Linear<uint32_t> linear{ {0, 0.0}, {1, 1.0} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(0, 1), 0.5} };
        double offset = -0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        bqm.print();

        bqm.add_interaction(0, 2, 2);
        bqm.add_interaction(0, 1, 0.25);
        bqm.add_interaction(1, 2, 0.25, Vartype::BINARY);

        // check bias
        Quadratic<uint32_t> bqm_quadratic = bqm.get_quadratic();
        EXPECT_EQ(bqm_quadratic[std::make_pair(0, 1)], 0.75);

        bqm.print();
    }

    TEST(FunctionTest, add_interactions_from)
    {
        Linear<uint32_t> linear;
        Quadratic<uint32_t> quadratic;
        double offset = 0.0;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        Quadratic<uint32_t> quadratic1{ {std::make_pair(0, 1), -0.5} };
        bqm.add_interactions_from(quadratic1);

        // check bias
        Quadratic<uint32_t> bqm_quadratic = bqm.get_quadratic();
        EXPECT_EQ(bqm_quadratic[std::make_pair(0, 1)], -0.5);

        Quadratic<uint32_t> quadratic2{ {std::make_pair(0, 1), -0.5}, {std::make_pair(0, 2), 2.0} };
        Quadratic<uint32_t> quadratic3{ {std::make_pair(1, 2), 2.0} };
        bqm.add_interactions_from(quadratic2);
        bqm.add_interactions_from(quadratic3, Vartype::BINARY);

        // check length
        EXPECT_EQ(bqm.length(), 3);

        // check bias
        bqm_quadratic = bqm.get_quadratic();
        EXPECT_EQ(bqm_quadratic[std::make_pair(0, 1)], -1.0);
    }

    TEST(FunctionTest, add_offset)
    {
        Linear<uint32_t> linear{ {0, 0.0}, {1, 1.0} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(0, 1), 0.5} };
        double offset = -0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        bqm.add_offset(1.0);
        
        // check offset
        EXPECT_EQ(bqm.get_offset(), 0.5);
    }

    TEST(FunctionTest, energy)
    {
        Linear<uint32_t> linear{ {1, 1.0}, {2, 1.0} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(1, 2), 1.0} };
        double offset = 0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        // check energy
        Sample<uint32_t> sample1{ {1, -1}, {2, -1} };
        EXPECT_EQ(bqm.energy(sample1), -0.5);
        Sample<uint32_t> sample2{ {1, 1}, {2, 1} };
        EXPECT_EQ(bqm.energy(sample2), 3.5);
    }

    TEST(FunctionTest, energies)
    {
        Linear<uint32_t> linear{ {1, 1.0}, {2, 1.0} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(1, 2), 1.0} };
        double offset = 0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        Sample<uint32_t> sample1{ {1, -1}, {2, -1} };
        Sample<uint32_t> sample2{ {1, 1}, {2, 1} };
        std::vector<Sample<uint32_t>> samples{sample1, sample2};
        std::vector<double> en_vec = bqm.energies(samples);

        // check energies
        EXPECT_EQ(en_vec[0], -0.5);
        EXPECT_EQ(en_vec[1], 3.5);
    }

    TEST(FunctionTest, to_qubo)
    {
        Linear<uint32_t> linear{{0, 1.0}, {1, -1.0}, {2, 0.5} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(0, 1), 0.5}, {std::make_pair(1, 2), 1.5} };
        double offset = 1.4;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        auto t_qubo = bqm.to_qubo();
        Quadratic<uint32_t> Q = std::get<0>(t_qubo);
        double offset_qubo = std::get<1>(t_qubo);

        // check quadratic matrix and offset
        EXPECT_EQ(Q[std::make_pair(0, 0)], 1.0);
        EXPECT_EQ(Q[std::make_pair(0, 1)], 2.0);
        EXPECT_EQ(Q[std::make_pair(1, 1)], -6.0);
        EXPECT_EQ(Q[std::make_pair(1, 2)], 6.0);
        EXPECT_EQ(Q[std::make_pair(2, 2)], -2.0);
        EXPECT_EQ(offset_qubo, 2.9);
    }

    TEST(FunctionTest, to_ising)
    {
        Linear<uint32_t> linear{{0, 1.0}, {1, -1.0}, {2, 0.5} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(0, 1), 0.5}, {std::make_pair(1, 2), 1.5} };
        double offset = 1.4;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);

        auto t_ising = bqm.to_ising();
        Linear<uint32_t> h = std::get<0>(t_ising);
        Quadratic<uint32_t> J = std::get<1>(t_ising);
        double offset_ising = std::get<2>(t_ising);

        // check biases
        EXPECT_EQ(h[0], 1.0);
        EXPECT_EQ(J[std::make_pair(0, 1)], 0.5);
        EXPECT_EQ(h[1], -1.0);
        EXPECT_EQ(J[std::make_pair(1, 2)], 1.5);
        EXPECT_EQ(h[2], 0.5);
        EXPECT_EQ(offset_ising, 1.4);
    }

    TEST(FunctionTest, remove_interaction)
    {
        Linear<std::string> linear;
        Quadratic<std::string> quadratic{ {std::make_pair("a", "b"), -1.0}, {std::make_pair("b", "c"), 1.0} };
        double offset = 0.0;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<std::string> bqm(linear, quadratic, offset, vartype);
        bqm.print();
        bqm.remove_interaction("b", "c");
        bqm.print();
    }

    TEST(FunctionTest, remove_variable)
    {
        Linear<std::string> linear{ {"a", 0.0}, {"b", 1.0}, {"c", 2.0} };
        Quadratic<std::string> quadratic{ {std::make_pair("a", "b"), 0.25}, {std::make_pair("a", "c"), 0.5}, {std::make_pair("b", "c"), 0.75} };
        double offset = -0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<std::string> bqm(linear, quadratic, offset, vartype);
        bqm.print();
        bqm.remove_variable("a");
        bqm.print();

        // check variables
        EXPECT_EQ(bqm.contains("a"), false);
        EXPECT_EQ(bqm.contains("b"), true);
        EXPECT_EQ(bqm.contains("c"), true);
    }

    TEST(FunctionTest, remove_variables_from)
    {
        Linear<uint32_t> linear{ {0, 0.0}, {1, 1.0}, {2, 2.0} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(0, 1), 0.25}, {std::make_pair(0, 2), 0.5}, {std::make_pair(1, 2), 0.75} };
        double offset = -0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);
        bqm.print();

        std::vector<uint32_t> variables = {0, 1};

        bqm.remove_variables_from(variables);
        bqm.print();

        // check variables
        EXPECT_EQ(bqm.contains(0), false);
        EXPECT_EQ(bqm.contains(1), false);
        EXPECT_EQ(bqm.contains(2), true);
    }

    TEST(FunctionTest, scale)
    {
        Linear<std::string> linear{{"a", -2.0}, {"b", 2.0} };
        Quadratic<std::string> quadratic{ {std::make_pair("a", "b"), -1.0}};
        double offset = 1.0;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<std::string> bqm(linear, quadratic, offset, vartype);

        bqm.scale(0.5);
        auto bqm_linear = bqm.get_linear();
        auto bqm_quadratic = bqm.get_quadratic();
        double bqm_offset = bqm.get_offset();

        // check biases and offset
        EXPECT_EQ(bqm_linear["a"], -1.0);
        EXPECT_EQ(bqm_quadratic[std::make_pair("a", "b")], -0.5);
        EXPECT_EQ(bqm_offset, 0.5);
    }

    TEST(FunctionTest, normalize)
    {
        Linear<std::string> linear{ {"a", -2.0}, {"b", 1.5} };
        Quadratic<std::string> quadratic{ {std::make_pair("a", "b"), -1.0} };
        double offset = 1.0;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<std::string> bqm(linear, quadratic, offset, vartype);

        bqm.normalize(std::make_pair(-1.0, 1.0));
        auto bqm_linear = bqm.get_linear();
        auto bqm_quadratic = bqm.get_quadratic();
        double bqm_offset = bqm.get_offset();

        auto comp = [](const auto &a, const auto &b) { return std::abs(a.second) < std::abs(b.second); };
        auto lin_max = std::max_element(bqm_linear.begin(), bqm_linear.end(), comp);
        auto quad_max = std::max_element(bqm_quadratic.begin(), bqm_quadratic.end(), comp);

        // check maximum biases
        EXPECT_EQ(lin_max->second, -1.0);
        EXPECT_EQ(quad_max->second, -0.5);
    }

    TEST(FunctionTest, fix_variable)
    {
        Linear<std::string> linear{ {"a", -0.5}, {"b", 0.0} };
        Quadratic<std::string> quadratic{ {std::make_pair("a", "b"), -1.0} };
        double offset = 0.0;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<std::string> bqm(linear, quadratic, offset, vartype);
        
        bqm.fix_variable("a", -1);
        auto bqm_linear = bqm.get_linear();
        double bqm_offset = bqm.get_offset();

        // check offset, linear bias and variable
        EXPECT_EQ(bqm_offset, 0.5);
        EXPECT_EQ(bqm_linear["b"], 1.0);
        EXPECT_EQ(bqm.contains("a"), false);
    }

    TEST(FunctionTest, flip_variable)
    {
        Linear<uint32_t> linear{{1, 1.0}, {2, 2.0} };
        Quadratic<uint32_t> quadratic{ {std::make_pair(1, 2), 0.5} };
        double offset = 0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);
        
        bqm.flip_variable(1);
        auto bqm_linear = bqm.get_linear();
        auto bqm_quadratic = bqm.get_quadratic();

        // check biases
        EXPECT_EQ(bqm_linear[1], -1.0);
        EXPECT_EQ(bqm_linear[2], 2.0);
        EXPECT_EQ(bqm_quadratic[std::make_pair(1, 2)], -0.5);
    }
    TEST(FunctionTest, contract_variables)
    {
        Linear<uint32_t> linear{ {1, 1.0}, {2, 2.0}, {3, 3.0}, {4, 4.0} };
        Quadratic<uint32_t> quadratic
        {
            {std::make_pair(1, 2), 12.0}, {std::make_pair(1, 3), 13.0}, {std::make_pair(1, 4), 14.0},
            {std::make_pair(2, 3), 23.0}, {std::make_pair(2, 4), 24.0},
            {std::make_pair(3, 4), 34.0}
        };
        double offset = 0.5;
        Vartype vartype = Vartype::SPIN;

        BinaryQuadraticModel<uint32_t> bqm(linear, quadratic, offset, vartype);
        bqm.contract_variables(2, 3);

        auto bqm_quadratic = bqm.get_quadratic();

        // check variable and quadratic bias
        EXPECT_EQ(bqm.contains(3), false);
        EXPECT_EQ(bqm_quadratic[std::make_pair(1, 2)], 25.0);
    }
}