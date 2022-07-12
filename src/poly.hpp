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
#include "product.hpp"


namespace pyqubo {
    
    enum class poly_type {
        multi_poly,
        single_poly
    };

    using Coeff = std::shared_ptr<const expression>;

    class poly {
    public:
        poly_type poly_type = poly_type::single_poly;
        pyqubo::polynomial* terms = nullptr;
        product* prd = nullptr;
        Coeff coeff;
        
        poly(pyqubo::polynomial* terms): terms(terms){
            poly_type = poly_type::multi_poly;
        }

        poly(Coeff coeff): coeff(coeff){
            this->prd = new product({});
        }

        poly(Coeff coeff, product* prd): coeff(coeff), prd(prd){
        }

        poly to_multi() const {
            if(poly_type == poly_type::single_poly){
                return poly(new pyqubo::polynomial({{*prd, coeff}}));
            }else{
                return *this;
            }
        }

        size_t size() const {
            if(poly_type == poly_type::single_poly){
                return 1;
            }else{
                return terms->size();
            }
        }

        std::string to_string() const {
            if(poly_type == poly_type::single_poly){
                return "single_poly(" + coeff->to_string() + "," + this->prd->to_string() + ")";
            }else{
                std::stringstream ss;
                ss << "multi_poly(";
                for(const auto& [name, value]: *terms){
                    ss << "[";
                    ss << name.to_string();
                    ss << ",";
                    ss << value->to_string();
                    ss << "],";
                }
                ss << ")";
                std::string s = ss.str();
                return s;
            }
        }
    };

    auto multiply_multi_multi(const poly& poly_1, const poly& poly_2){
        auto result = new polynomial{};
        for (const auto& [product_1, coefficient_1] : *poly_1.terms) {
            for (const auto& [product_2, coefficient_2] : *poly_2.terms) {
                const auto [it, emplaced] = result->emplace(product_1 * product_2, coefficient_1 * coefficient_2);
                if (!emplaced) {
                    it->second = it->second + coefficient_1 * coefficient_2;
                }
            }
        }
        return poly(result);
    }

    auto& add_multi_single(poly& multi_poly, poly& single_poly){
        const auto [it, emplaced] = multi_poly.terms->emplace(*(single_poly.prd), single_poly.coeff);
        if (!emplaced) {
            it->second = it->second + single_poly.coeff;
        }
        return multi_poly;
    }

    auto& add_multi_multi(const poly& multi_poly_1, const poly& multi_poly_2) {
        printf("add_multi_multi");
        for (const auto& [product, coefficient] : *multi_poly_2.terms) {
            const auto [it, emplaced] = multi_poly_1.terms->emplace(product, coefficient);
            if (!emplaced) {
                it->second = it->second + coefficient;
            }
        }
        return multi_poly_1;
    }

    auto operator*(const poly& poly_1, const poly& poly_2) noexcept {
        if(poly_1.poly_type == poly_type::single_poly && poly_2.poly_type == poly_type::single_poly){
            return poly(poly_1.coeff * poly_2.coeff, multiply(poly_1.prd, poly_2.prd));
        }else if(poly_1.poly_type == poly_type::multi_poly && poly_2.poly_type == poly_type::single_poly){
            return multiply_multi_multi(poly_1, poly_2.to_multi());
        }else if(poly_1.poly_type == poly_type::single_poly && poly_2.poly_type == poly_type::multi_poly){
            return multiply_multi_multi(poly_1.to_multi(), poly_2);
        }else{
            return multiply_multi_multi(poly_1, poly_2);
        }
    }

    auto operator+(poly& poly_1, poly& poly_2) noexcept {
        
        if(poly_1.poly_type == poly_type::single_poly && poly_2.poly_type == poly_type::single_poly){
            if(poly_1.prd == poly_2.prd){
                return poly(poly_1.coeff + poly_2.coeff, poly_1.prd);
            }else{
                auto terms = new pyqubo::polynomial({{*poly_1.prd, poly_1.coeff}, {*poly_2.prd, poly_2.coeff}});
                return poly(terms);
            }
        }else if(poly_1.poly_type == poly_type::multi_poly && poly_2.poly_type == poly_type::single_poly){
            printf("operator+ add_multi_single\n");
            return add_multi_single(poly_1, poly_2);

        }else if(poly_1.poly_type == poly_type::single_poly && poly_2.poly_type == poly_type::multi_poly){
            printf("operator+ add_multi_single\n");
            return add_multi_single(poly_2, poly_1);
        }else{
            printf("operator+ add_multi_multi\n");
            if(poly_1.size() > poly_2.size()){
                return add_multi_multi(poly_1, poly_2);
            }else{
                return add_multi_multi(poly_2, poly_1);
            }
        }
    }

    class poly_base {
    public:
        virtual pyqubo::poly_type poly_type() const noexcept = 0;
        virtual std::string to_string() const noexcept = 0;
    };

    class multi_poly: public poly_base {
        
    public:
    
        pyqubo::polynomial polynomial;

        pyqubo::poly_type poly_type() const noexcept override {
            return poly_type::multi_poly;
        }

        std::string to_string() const noexcept override {
            return "this is multi_poly";
        }
    };

    class single_poly: public poly_base {
    
    public:
        double coeff = 0.0;

        single_poly(double coeff): coeff(coeff){
        }
        
        pyqubo::poly_type poly_type() const noexcept override {
            return poly_type::single_poly;
        }

        std::string to_string() const noexcept override {
            return "single_poly(" + std::to_string(coeff) + ")";
        }
    };

    /*poly merge(multi_poly poly_left, multi_poly poly_right){

    }*/

    poly_base* merge(poly_base* poly_left, poly_base* poly_right){
        //single_poly(poly_left.coeff * poly_right.coeff)
        if(poly_left->poly_type() == poly_type::single_poly && poly_right->poly_type() == poly_type::single_poly){
            auto left = dynamic_cast<single_poly*>(poly_left);
            auto right = dynamic_cast<single_poly*>(poly_right);

        }
        return nullptr;
        //return poly_left;
    }

    single_poly* merge(single_poly* poly_left, single_poly* poly_right){
        return new single_poly(poly_left->coeff * poly_right->coeff);
    }
}