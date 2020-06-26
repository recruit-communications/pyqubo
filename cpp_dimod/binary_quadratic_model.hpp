/**
 * @mainpage cpp_dimod
 * 
 * @section s_overview Overview
 * This library is a C++ implementation of dimod (https://github.com/dwavesystems/dimod). It provides a binary quadratic model class which contains an Ising model or a quadratic unconstrained binary optimization (QUBO) model.
 * It also provides utilities for constructing a model and transforming to some other interfaces.
 * 
 * @section s_bqm Binary quadratic model
 * A binary quadratic model class can contain an Ising model or a QUBO model.
 * 
 * @subsection ss_ising Ising model
 * An energy of an Ising model \f$E_{\mathrm{Ising}}\f$ is represented by
 * \f[
 * E_{\mathrm{Ising}} = \sum_{i} h_i s_i + \sum_{i \neq j} J_{ij} s_i s_j + \delta_{\mathrm{Ising}},
 * \f]
 * where \f$s_i \in \{+1, -1\}\f$ denotes a spin at the site \f$i\f$, \f$h_i\f$ denotes an external magnetic field parameter, \f$J_{ij}\f$ denotes an interaction parameter and \f$\delta_{\mathrm{Ising}}\f$ denotes an offset.
 * Note that this library assumes that the interaction is not symmetric, i.e., \f$J_{ij} \neq J_{ji}\f$.
 * 
 * @subsection ss_qubo QUBO model
 * An evaluation function of a QUBO model \f$E_{\mathrm{QUBO}}\f$ is represented by
 * \f[
 * E_{\mathrm{QUBO}} = \sum_{i, j} Q_{ij} x_i x_j + \delta_{\mathrm{QUBO}},
 * \f]
 * where \f$x_i \in \{0, 1\}\f$ denotes a decision variable, \f$Q_{ij}\f$ denotes a quadratic bias and \f$\delta_{\mathrm{QUBO}}\f$ denotes an offset.
 * Note that this library assumes that the quadratic bias is not symmetric, i.e., \f$Q_{ij} \neq Q_{ji}\f$ if \f$i \neq j\f$.
 * 
 */

/**
 * @file binary_quadratic_model.hpp
 * @author Fumiya Watanabe
 * @brief BinaryQuadraticModel class
 * @date 2020-03-13
 * 
 * @copyright Copyright (c) 2020
 * 
 */

#ifndef BINARY_QUADRATIC_MODEL_HPP__
#define BINARY_QUADRATIC_MODEL_HPP__

#include "vartypes.hpp"
#include "hash.hpp"

#include <algorithm>
#include <cstdint>
#include <iostream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

/**
 * @brief Type alias for linear bias
 * 
 * @tparam IndexType 
 */
template <typename IndexType>
using Linear = std::unordered_map<IndexType, double>;

/**
 * @brief Type alias for quadratic bias
 * 
 * @tparam IndexType 
 */
template <typename IndexType>
using Quadratic = std::unordered_map<std::pair<IndexType, IndexType>, double, pair_hash>;

/**
 * @brief Type alias for adjacency list
 * 
 * @tparam IndexType 
 */
template <typename IndexType>
using Adjacency = std::unordered_map<IndexType, std::unordered_map<IndexType, double>>;

/**
 * @brief Type alias for sample
 * 
 * @tparam IndexType 
 */
template <typename IndexType>
using Sample = std::unordered_map<IndexType, int32_t>;

/**
 * @brief Class for binary quadratic model.
 */
template <typename IndexType>
class BinaryQuadraticModel
{
protected:
    /**
     * @brief Linear biases as a dictionary.
     * 
     */
    Linear<IndexType> m_linear;

    /**
     * @brief Quadratic biases as a dictionary.
     * 
     */
    Quadratic<IndexType> m_quadratic;

    /**
     * @brief The energy offset associated with the model.
     * 
     */
    double m_offset;

    /**
     * @brief The model's type.
     * 
     */
    Vartype m_vartype = Vartype::NONE;

    /**
     * @brief A place to store miscellaneous data about the binary quadratic model as a whole.
     * 
     */
    std::string m_info;

    /**
     * @brief The model's interactions as nested dictionaries.
     * 
     */
    Adjacency<IndexType> m_adj;
    

public:
    /**
     * @brief BinaryQuadraticModel constructor.
     * 
     * @param linear
     * @param quadratic
     * @param offset
     * @param vartype
     * @param info
     */
    BinaryQuadraticModel
    (
        const Linear<IndexType> &linear,
        const Quadratic<IndexType> &quadratic,
        const double &offset,
        const Vartype vartype,
        const std::string info = ""
    ):
        m_offset(offset),
        m_vartype(vartype),
        m_info(info)
    {
        add_variables_from(linear);
        add_interactions_from(quadratic);
    };

    /**
     * @brief Copy constructor of BinaryQuadraticModel
     * 
     * @param bqm 
     */
    BinaryQuadraticModel
    (
        const BinaryQuadraticModel &bqm
    )
    {
        m_offset = bqm.get_offset();
        m_vartype = bqm.get_vartype();
        m_info = bqm.get_info();
        add_variables_from(bqm.get_linear());
        add_interactions_from(bqm.get_quadratic());
    };

    /**
     * @brief Return the number of variables.
     * 
     * @return The number of variables.
     */
    size_t length() const
    {
        return m_linear.size();
    };

    /**
     * @brief Return true if the variable contains v.
     * 
     * @return Return true if the variable contains v.
     * @param v
     */
    bool contains
    (
        const IndexType &v
    )
    {
        if(m_linear.count(v)!=0)
        {
            return true;
        }
        else
        {
            return false;
        }
        
    };
    
    /**
     * @brief Get the linear object
     * 
     * @return A linear bias.
     */
    Linear<IndexType> get_linear() const
    {
        return m_linear;
    };

    /**
     * @brief Get the quadratic object
     * 
     * @return A quadratic bias.
     */
    Quadratic<IndexType> get_quadratic() const
    {
        return m_quadratic;
    };

    /**
     * @brief Get the adjacency object
     * 
     * @return A adjacency list.
     */
    Adjacency<IndexType> get_adjacency() const
    {
        return m_adj;
    };

    /**
     * @brief Get the offset
     * 
     * @return An offset.
     */
    double get_offset() const
    {
        return m_offset;
    }

    /**
     * @brief Get the vartype object
     * 
     * @return Type of the model.
     */
    Vartype get_vartype() const
    {
        return m_vartype;
    }

    /**
     * @brief Get the info object
     * 
     * @return Information.
     */
    std::string get_info() const
    {
        return m_info;
    }

    /**
     * @brief Print informations of BinaryQuadraticModel
     * 
     */
    void print()
    {
        std::cout << "[BinaryQuadraticModel]" << std::endl;

        // Print linear
        std::cout << "linear = " << std::endl;
        for(auto &it : m_linear)
        {
            std::cout << "" << it.first << ": " << it.second << std::endl;
        }

        // Print quadratic
        std::cout << "quadratic = " << std::endl;
        for(auto &it : m_quadratic)
        {
            std::cout << "(" << it.first.first << ", " << it.first.second << "): " << it.second << ", ";
        }
        std::cout << std::endl;

        // Print adjacency
        std::cout << "adjacency = " << std::endl;
        for(auto &it_src : m_linear)
        {
            std::cout << it_src.first << ": {";
            for(auto &it_dst : m_adj[it_src.first])
            {
                std::cout << "(" << it_src.first << ", " << it_dst.first << "): " << it_dst.second << ", ";
            }
            std::cout << "}" << std::endl;
        }

        // Print vartype
        std::cout << "vartype = ";
        if(m_vartype == Vartype::SPIN)
        {
            std::cout << "Spin" << std::endl;
        }
        else if(m_vartype == Vartype::BINARY)
        {
            std::cout << "Binary" << std::endl;
        }

        // Print info
        std::cout << "info = ";
        std::cout << "\"" << m_info << "\"" << std::endl;
    }

    /* Update methods */

    /**
     * @brief Add variable v and/or its bias to a binary quadratic model.
     * 
     * @param v
     * @param bias
     * @param vartype
     */
    void add_variable
    (
        const IndexType &v,
        const double &bias,
        const Vartype vartype = Vartype::NONE
    )
    {
        double b = bias;

        // handle the case that a different vartype is provided
        if((vartype!=Vartype::NONE)&&(vartype!=m_vartype))
        {
            if((m_vartype == Vartype::SPIN)&&(vartype == Vartype::BINARY))
            {
                b /= 2;
                m_offset += b;
            }
            else if((m_vartype == Vartype::BINARY)&&(vartype == Vartype::SPIN))
            {
                m_offset -= b;
                b *= 2;
            }
            else
            {
                std::cerr << "Unknown vartype" << std::endl;
            }
        }

        // Insert or assign the bias
        double value = 0;
        if(m_linear.count(v) != 0)
        {
            value = m_linear[v];
        }
        m_linear[v] = value + b;
    };

    /**
     * @brief Add variables and/or linear biases to a binary quadratic model.
     * 
     * @param linear
     * @param vartype
     */
    void add_variables_from
    (
        const Linear<IndexType> &linear,
        const Vartype vartype = Vartype::NONE
    )
    {
        for(auto &it : linear)
        {
            add_variable(it.first, it.second, vartype);
        }
    };

    /**
     * @brief Add an interaction and/or quadratic bias to a binary quadratic model.
     * 
     * @param u
     * @param v
     * @param bias
     * @param vartype
     */
    void add_interaction
    (
        const IndexType &u,
        const IndexType &v,
        const double &bias,
        const Vartype vartype = Vartype::NONE
    )
    {
        if(u == v)
        {
            std::cerr << "No self-loops allowed, therefore (" << u << ", " << v << ") is not an allowed interaction." << std::endl;
        }
        else
        {
            double b = bias;
            if((vartype!=Vartype::NONE)&&(vartype!=m_vartype))
            {
                if((m_vartype == Vartype::SPIN)&&(vartype == Vartype::BINARY))
                {
                    //convert from binary to spin
                    b /= 4;
                    add_offset(b);
                    add_variable(u, b);
                    add_variable(v, b);
                }
                else if((m_vartype == Vartype::BINARY)&&(vartype == Vartype::SPIN))
                {
                    //convert from spin to binary
                    add_offset(b);
                    add_variable(u, -2 * b);
                    add_variable(v, -2 * b);
                    b *= 4;
                }
                else
                {
                    std::cerr << "Unknown vartype" << std::endl;
                }
            }
            else
            {
                if(m_linear.count(u) == 0)
                {
                    add_variable(u, 0);
                }
                if(m_linear.count(v) == 0)
                {
                    add_variable(v, 0);
                }
            }
            
            double value = 0;
            std::pair<IndexType, IndexType> p1 = std::make_pair(u, v);
            if(m_quadratic.count(p1) != 0)
            {
                value = m_quadratic[p1];
            }
            m_quadratic[p1] = value + b;
            update_adjacency(u, v);
        }
    };

    /**
     * @brief Add interactions and/or quadratic biases to a binary quadratic model.
     * 
     * @param quadratic
     * @param vartype
     */
    void add_interactions_from
    (
        const Quadratic<IndexType> &quadratic,
        const Vartype vartype = Vartype::NONE
    )
    {
        for(auto &it : quadratic)
        {
            add_interaction(it.first.first, it.first.second, it.second, vartype);
        }
    }

    /**
     * @brief Add the adjacency to the adjacency list
     * 
     */
    void update_adjacency
    (
        const IndexType &u,
        const IndexType &v
    )
    {
        std::pair<IndexType, IndexType> p = std::make_pair(u, v);
        if(m_quadratic.count(p)!=0)
        {
            m_adj[u][v] = m_quadratic[p];
        }
    }

    /**
     * @brief Remove variable v and all its interactions from a binary quadratic model.
     * 
     * @param v
     */
    void remove_variable
    (
        const IndexType &v
    )
    {
        std::vector<std::pair<IndexType, IndexType>> interactions;
        for(auto &it : m_quadratic)
        {
            if(it.first.first == v || it.first.second == v)
            {
                interactions.push_back(it.first);
            }         
        }
        remove_interactions_from(interactions);
        m_linear.erase(v);
        m_adj.erase(v);
    }

    /**
     * @brief Remove specified variables and all of their interactions from a binary quadratic model.
     * 
     * @param variables
     */
    void remove_variables_from
    (
        const std::vector<IndexType> &variables
    )
    {
        for(auto &it : variables)
        {
            remove_variable(it);
        }
    };

    /**
     * @brief Remove interaction of variables u, v from a binary quadratic model.
     * 
     * @param u
     * @param v
     */
    void remove_interaction
    (
        const IndexType &u,
        const IndexType &v      
    )
    {
        auto p = std::make_pair(u, v);
        if(m_quadratic.count(p)!=0)
        {
            auto k = m_quadratic.erase(p);
            remove_adjacency(u, v);
        }
    };

    /**
     * @brief Remove all specified interactions from the binary quadratic model.
     * 
     * @param interactions
     */
    void remove_interactions_from
    (
        const std::vector<std::pair<IndexType, IndexType>> &interactions
    )
    {
        for(auto &it : interactions)
        {
            remove_interaction(it.first, it.second);
        }
    };

    /**
     * @brief Remove adjacency from the adjacency list
     * 
     * @param u 
     * @param v 
     */
    void remove_adjacency
    (
        const IndexType &u,
        const IndexType &v
    )
    {
        auto k = m_adj[u].erase(v);
    };

    /**
     * @brief Add specified value to the offset of a binary quadratic model.
     * 
     * @param offset
     */
    void add_offset
    (
        const double &offset
    )
    {
        m_offset += offset;
    };

    /**
     * @brief Set the binary quadratic model's offset to zero.
     */
    void remove_offset()
    {
        add_offset(-m_offset);
    };

    /**
     * @brief Multiply by the specified scalar all the biases and offset of a binary quadratic model.
     * 
     * @param scalar
     * @param ignored_variables
     * @param ignored_interactions
     * @param ignored_offset
     */
    void scale
    (
        const double &scalar,
        const std::vector<IndexType> &ignored_variables = {},
        const std::vector<std::pair<IndexType, IndexType>> &ignored_interactions = {},
        const bool ignored_offset = false
    )
    {
        // scaling linear
        for(auto &it : m_linear)
        {
            if(std::find(ignored_variables.begin(), ignored_variables.end(), it.first) != ignored_variables.end() || ignored_variables.empty())
            {
                it.second *= scalar;
            }
        }

        // scaling quadratic
        for(auto &it : m_quadratic)
        {
            if(std::find(ignored_interactions.begin(), ignored_interactions.end(), it.first) != ignored_interactions.end() || ignored_variables.empty())
            {
                it.second *= scalar;
            }
        }

        // scaling offset
        if(!ignored_offset)
        {
            m_offset *= scalar;
        }
    };


    /**
     * @brief Fix the value of a variable and remove it from a binary quadratic model.
     * 
     * @param v
     * @param value
     */
    void fix_variable
    (
        const IndexType &v,
        const int32_t &value
    )
    {
        std::vector<std::pair<IndexType, IndexType>> interactions;
        for(auto &it : m_quadratic)
        {
            if(it.first.first == v)
            {
                add_variable(it.first.second, value*it.second);
                interactions.push_back(it.first);
            }
            else if(it.first.second == v)
            {
                add_variable(it.first.first, value*it.second);
                interactions.push_back(it.first);
            }
        }
        remove_interactions_from(interactions);
        add_offset(m_linear[v]*value);
        remove_variable(v);
    };

    /**
     * @brief Fix the value of the variables and remove it from a binary quadratic model.
     * 
     * @param fixed
     */
    void fix_variables
    (
        const std::vector<std::pair<IndexType, int32_t>> &fixed
    )
    {
        for(auto &it : fixed)
        {
            fix_variable(it.first, it.second);
        }
    };

    /**
     * @brief Flip variable v in a binary quadratic model.
     * 
     * @param v
     */
    void flip_variable
    (
        const IndexType &v
    )
    {
        // check variable
        if(m_linear.count(v)==0)
        {
           std::cout << v << " is not a variable in the binary quadratic model." << std::endl;
           return;
        }

        if(m_vartype == Vartype::SPIN)
        {
            m_linear[v] *= -1.0;
            for(auto &it : m_quadratic)
            {
                if(it.first.first == v || it.first.second == v)
                {
                    it.second *= -1.0;
                    update_adjacency(it.first.first, it.first.second);
                }
            }
        }
        else if(m_vartype == Vartype::BINARY)
        {
            add_offset(m_linear[v]);
            m_linear[v] *= -1.0;

            for(auto &it : m_quadratic)
            {
                if(it.first.first == v)
                {
                    m_linear[it.first.second] += it.second;
                    it.second *= -1.0;
                    update_adjacency(it.first.first, it.first.second);
                }
                else if(it.first.second == v)
                {
                    m_linear[it.first.first] += it.second;
                    it.second *= -1.0;
                    update_adjacency(it.first.first, it.first.second);
                }
            }
        }
    };

    void update
    (
        const BinaryQuadraticModel &bqm,
        const bool ignore_info = true
    )
    {
        add_variables_from(bqm.get_linear(), bqm.get_vartype());
        add_interactions_from(bqm.get_quadratic(), bqm.get_vartype());
        add_offset(bqm.get_offset());
        if(!ignore_info)
        {
            m_info = bqm.get_info();
        }
    };

    /**
     * @brief Enforce u, v being the same variable in a binary quadratic model.
     * 
     * @param u
     * @param v
     */
    void contract_variables
    (
        const IndexType &u,
        const IndexType &v
    )
    {
        // check variable
        if(m_linear.count(v)==0)
        {
            std::cerr << v << " is not a variable in the binary quadratic model." << std::endl;
            return;
        }
        if(m_linear.count(u)==0)
        {
            std::cerr << u << " is not a variable in the binary quadratic model." << std::endl;
            return;
        }

        auto p1 = std::make_pair(u, v);
        auto p2 = std::make_pair(v, u);
        if(m_quadratic.count(p1) != 0)
        {
            if(m_vartype == Vartype::BINARY)
            {
                add_variable(u, m_quadratic[p1]);
            }
            else if(m_vartype == Vartype::SPIN)
            {
                add_offset(m_quadratic[p1]);
            }
            remove_interaction(u, v);
        }
        if(m_quadratic.count(p2) != 0)
        {
            if(m_vartype == Vartype::BINARY)
            {
                add_variable(u, m_quadratic[p2]);
            }
            else if(m_vartype == Vartype::SPIN)
            {
                add_offset(m_quadratic[p2]);
            }
            remove_interaction(v, u);
        }

        std::vector<std::pair<IndexType, IndexType>> interactions;
        for(auto &it : m_quadratic)
        {
            if(it.first.first == v)
            {
                add_interaction(u, it.first.second, it.second);
                update_adjacency(u, it.first.second);
                interactions.push_back(it.first);
            }
            else if(it.first.second == v)
            {
                add_interaction(it.first.first, u, it.second);
                update_adjacency(it.first.first, u);
                interactions.push_back(it.first);
            }
        }
        remove_interactions_from(interactions);

        add_variable(u, m_linear[v]);
        remove_variable(v);
    };

    /* Transformations */

    /**
     * @brief Create a binary quadratic model with the specified vartype.
     * 
     * @param vartype
     * @return A new instance of the BinaryQuadraticModel class.
     */
    BinaryQuadraticModel change_vartype
    (
        const Vartype &vartype
    )
    {
        // same vartype
        if(vartype == m_vartype)
        {
            BinaryQuadraticModel bqm(m_linear, m_quadratic, m_offset, m_vartype, m_info);
            return bqm;
        }
        // different vartype
        else
        {
            std::tuple<Linear<IndexType>, Quadratic<IndexType>, double> t;
            if(m_vartype == Vartype::BINARY && vartype == Vartype::SPIN) // binary -> spin
            {
                t = binary_to_spin(m_linear, m_quadratic, m_offset);                
            }
            else if(m_vartype == Vartype::SPIN && vartype == Vartype::BINARY) // spin -> binary
            {
                t = spin_to_binary(m_linear, m_quadratic, m_offset);
            }
            else
            {
                std::cerr << "Invalid vartype." << std::endl;
            }
            BinaryQuadraticModel bqm(std::get<0>(t), std::get<1>(t), std::get<2>(t), vartype, m_info);
            return bqm;
        }
    };
    
    /* Static methods */
    /**
     * @brief Convert linear, quadratic, and offset from spin to binary. Does no checking of vartype. Copies all of the values into new objects.
     * 
     * @param linear
     * @param quadratic
     * @param offset
     * 
     * @return A tuple including a linear bias, a quadratic bias and an offset.
     */
    static std::tuple<Linear<IndexType>, Quadratic<IndexType>, double> spin_to_binary
    (
        const Linear<IndexType> &linear,
        const Quadratic<IndexType> &quadratic,
        const double &offset
    )
    {
        Linear<IndexType> new_linear;
        Quadratic<IndexType> new_quadratic;
        double new_offset = offset;
        double linear_offset = 0.0;
        double quadratic_offset = 0.0;

        for(auto &it : linear)
        {
            new_linear[it.first] = 2.0 * it.second;
            linear_offset += it.second;
        }

        for(auto &it : quadratic)
        {
            new_quadratic[it.first] = 4.0 * it.second;
            new_linear[it.first.first] -= 2.0 * it.second;
            new_linear[it.first.second] -= 2.0 * it.second;
            quadratic_offset += it.second; 
        }

        new_offset += quadratic_offset - linear_offset;

        return std::make_tuple(new_linear, new_quadratic, new_offset);
    };

    /**
     * @brief Convert linear, quadratic and offset from binary to spin. Does no checking of vartype. Copies all of the values into new objects.
     * 
     * @param linear
     * @param quadratic
     * @param offset
     * 
     * @return A tuple including a linear bias, a quadratic bias and an offset.
     */
    static std::tuple<Linear<IndexType>, Quadratic<IndexType>, double> binary_to_spin
    (
        const Linear<IndexType> &linear,
        const Quadratic<IndexType> &quadratic,
        const double &offset
    )
    {
        Linear<IndexType> h;
        Quadratic<IndexType> J;
        double new_offset = offset;
        double linear_offset = 0.0;
        double quadratic_offset = 0.0;

        for(auto &it : linear)
        {
            h[it.first] = 0.5 * it.second;
            linear_offset += it.second;
        }

        for(auto &it : quadratic)
        {
            J[it.first] = 0.25 * it.second;
            h[it.first.first] += 0.25 * it.second;
            h[it.first.second] += 0.25 * it.second;
            quadratic_offset += it.second;
        }

        new_offset += 0.5 * linear_offset + 0.25 * quadratic_offset;

        return std::make_tuple(h, J, new_offset);
    };

    /* Methods */

    /**
     * @brief Determine the energy of the specified sample of a binary quadratic model.
     * 
     * @param sample
     * @return An energy with respect to the sample.
     */
    double energy
    (
        Sample<IndexType> &sample
    )
    {
        double en = m_offset;
        for(auto &it : m_linear)
        {
            en += static_cast<double>(sample[it.first]) * it.second;
        }
        for(auto &it : m_quadratic)
        {
            en += static_cast<double>(sample[it.first.first]) * static_cast<double>(sample[it.first.second]) * it.second;
        }
        return en;
    };
    
    /**
     * @brief Determine the energies of the given samples.
     * 
     * @param samples_like
     * @return A vector including energies with respect to the samples.
     */
    std::vector<double> energies
    (
        std::vector<Sample<IndexType>> &samples_like
    )
    {
        std::vector<double> en_vec;
        for(auto &it : samples_like)
        {
            en_vec.push_back(energy(it));
        }
        return en_vec;
    };
    
    /* Conversions */
    /**
     * @brief Convert a binary quadratic model to QUBO format.
     * 
     * @return A tuple including a quadratic bias and an offset.
     */
    std::tuple<Quadratic<IndexType>, double> to_qubo()
    {
        // change vartype to binary
        BinaryQuadraticModel bqm = change_vartype(Vartype::BINARY);

        Linear<IndexType> linear = bqm.get_linear();
        Quadratic<IndexType> Q = bqm.get_quadratic();
        double offset = bqm.get_offset();
        for(auto &it : linear)
        {
            Q[std::make_pair(it.first, it.first)] = it.second;
        }
        return std::make_tuple(Q, offset);
    };

    /**
     * @brief Convert a binary quadratic model to Ising format.
     * 
     * @return A tuple including a linear bias, a quadratic bias and an offset.
     */
    std::tuple<Linear<IndexType>, Quadratic<IndexType>, double> to_ising()
    {
        // change vartype to spin
        BinaryQuadraticModel bqm = change_vartype(Vartype::SPIN);

        Linear<IndexType> linear = bqm.get_linear();
        Quadratic<IndexType> quadratic = bqm.get_quadratic();
        double offset = bqm.get_offset();
        return std::make_tuple(linear, quadratic, offset);
    };

};

#endif