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
        poly_type _poly_type = poly_type::single_poly;
        pyqubo::polynomial* terms = nullptr;
        product* prd = nullptr;
        Coeff coeff;
        
        poly(pyqubo::polynomial* terms): terms(terms){
            _poly_type = poly_type::multi_poly;
        }

        poly(Coeff coeff): coeff(coeff){
            this->prd = new product({});
        }

        poly(){
            this->coeff = std::make_shared<const pyqubo::numeric_literal>(0);
            this->prd = new product({});
        }

        poly(Coeff coeff, product* prd): coeff(coeff), prd(prd){
        }

        poly copy() const {
            if(_poly_type == poly_type::single_poly){
                return poly(this->coeff, this->prd);
            }else{
                return poly(new pyqubo::polynomial(*terms));
            }
        }

        // polynomial is composed of only numeric constant or not
        bool is_numeric() const {
            return _poly_type == poly_type::single_poly && prd->indexes().size() == 0;
        }

        poly to_multi() const {
            if(_poly_type == poly_type::single_poly){
                return poly(new pyqubo::polynomial({{*prd, coeff}}));
            }else{
                return *this;
            }
        }

        pyqubo::polynomial* get_terms() const {
            if(_poly_type == poly_type::single_poly){
                return new pyqubo::polynomial({{*prd, coeff}});
            }else{
                return terms;
            }
        }

        size_t size() const {
            if(_poly_type == poly_type::single_poly){
                return 1;
            }else{
                return terms->size();
            }
        }

        std::string to_string() const {
            if(_poly_type == poly_type::single_poly){
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
        //std::cout << "add_multi_single: " << multi_poly.to_string() << " <= " << single_poly.to_string() << "\n";
        const auto [it, emplaced] = multi_poly.terms->emplace(*(single_poly.prd), single_poly.coeff);
        if(!emplaced){
            it->second = it->second + single_poly.coeff;
        }
        return multi_poly;
    }

    auto& add_multi_multi(const poly& multi_poly_1, const poly& multi_poly_2) {
        //printf("add_multi_multi");
        for (const auto& [product, coefficient] : *multi_poly_2.terms) {
            const auto [it, emplaced] = multi_poly_1.terms->emplace(product, coefficient);
            if (!emplaced) {
                it->second = it->second + coefficient;
            }
        }
        return multi_poly_1;
    }

    auto operator*(const poly& poly_1, const poly& poly_2) noexcept {
        if(poly_1._poly_type == poly_type::single_poly && poly_2._poly_type == poly_type::single_poly){
            /*if(poly_1.is_numeric() && poly_2.is_numeric()){
                return poly(poly_1.coeff * poly_2.coeff, new product({}));
            }else{
                return poly(poly_1.coeff * poly_2.coeff, multiply(poly_1.prd, poly_2.prd));
            }*/
            return poly(poly_1.coeff * poly_2.coeff, multiply(poly_1.prd, poly_2.prd));
        }else if(poly_1._poly_type == poly_type::multi_poly && poly_2._poly_type == poly_type::single_poly){
            return multiply_multi_multi(poly_1, poly_2.to_multi());
        }else if(poly_1._poly_type == poly_type::single_poly && poly_2._poly_type == poly_type::multi_poly){
            return multiply_multi_multi(poly_1.to_multi(), poly_2);
        }else{
            return multiply_multi_multi(poly_1, poly_2);
        }
    }

    auto operator+(poly& poly_1, poly& poly_2) noexcept {
        
        if(poly_1._poly_type == poly_type::single_poly && poly_2._poly_type == poly_type::single_poly){
            //printf("single poly %s + single poly %s\n", poly_1.coeff->to_string().c_str(), poly_2.coeff->to_string().c_str());
            if(poly_1.prd->equals(*poly_2.prd)){
                return poly(poly_1.coeff + poly_2.coeff, poly_1.prd);
            }else{
                auto terms = new pyqubo::polynomial({{*poly_1.prd, poly_1.coeff}, {*poly_2.prd, poly_2.coeff}});
                return poly(terms);
            }
        }else if(poly_1._poly_type == poly_type::multi_poly && poly_2._poly_type == poly_type::single_poly){
            //std::cout << "operator+ add_multi_single\n";
            return add_multi_single(poly_1, poly_2);

        }else if(poly_1._poly_type == poly_type::single_poly && poly_2._poly_type == poly_type::multi_poly){
            //std::cout << "operator+ add_multi_single\n";
            return add_multi_single(poly_2, poly_1);
        }else{
            //std::cout << "operator+ add_multi_multi\n";
            if(poly_1.size() > poly_2.size()){
                return add_multi_multi(poly_1, poly_2);
            }else{
                return add_multi_multi(poly_2, poly_1);
            }
        }
    }
}