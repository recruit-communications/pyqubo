/**
 * @file hash.hpp
 * @author Fumiya Watanabe
 * @brief Hash function for std::pair
 * @version 0.1
 * @date 2020-03-13
 * 
 * @copyright Copyright (c) 2020
 * 
 */

#ifndef HASH_HPP__
#define HASH_HPP__

#include <utility>
#include <cstdint>
#include <iostream>

/**
 * @brief Hash function for std::unordered_map
 * 
 */
struct pair_hash {
    template <class T1, class T2>
    unsigned int operator() (const std::pair<T1, T2>& p) const {
        unsigned int lhs = std::hash<T1>()(p.first), rhs = std::hash<T2>()(p.second);
        return lhs^(rhs+0x9e3779b9+(lhs<<6)+(lhs>>2));
    }
};

#endif