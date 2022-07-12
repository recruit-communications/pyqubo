#include <algorithm>
#include <iostream>
#include <map>
#include <vector>
#include <time.h>
#include <vartypes.hpp>

#include "abstract_syntax_tree.hpp"
#include "compiler.hpp"
#include "compiler2.hpp"
#include "poly.hpp"
#include "product.hpp"


std::shared_ptr<const pyqubo::expression> create_binary(std::string s){
    return std::make_shared<const pyqubo::binary_variable>(s);
}

std::shared_ptr<const pyqubo::expression> create_numeric(double a){
    return std::make_shared<const pyqubo::numeric_literal>(a);
}

void test_poly(){
    auto sp1 = new pyqubo::single_poly(2.0);
    auto sp2 = new pyqubo::single_poly(3.0);
    auto sp3 = pyqubo::merge(sp1, sp2);
    std::cout << sp3->to_string() << std::endl;
}

void test_poly2(){
    auto sp1 = pyqubo::poly(create_numeric(2), new pyqubo::product({1}));
    auto sp2 = pyqubo::poly(create_numeric(3), new pyqubo::product({2}));
    auto sp3 = pyqubo::poly(create_numeric(4), new pyqubo::product({3}));
    auto sp4 = sp1 * sp2;
    auto sp5 = sp1 + sp2;
    auto sp6 = sp1 + sp3;
    auto sp7 = sp5 * sp6;
    
    std::cout << sp3.to_string() << std::endl;
    std::cout << sp4.to_string() << std::endl;
    std::cout << sp7.to_string() << std::endl;

    auto sp8 = sp7 + sp5;
    std::cout << sp8.to_string() << std::endl;
}

void test_express(int n){
    clock_t t0 = clock();
    auto a = create_binary("a");
    auto b = create_binary("b");
    auto c = std::make_shared<pyqubo::add_operator>(a, b);
    for(int i=0; i < n; i++){
        auto bi = create_binary("bi_" + std::to_string(i));
        auto bj = create_binary("bj_" + std::to_string(i));
        auto coeff = std::make_shared<const pyqubo::numeric_literal>(2);
        //c->add_child(coeff*bi*bj);
        c->add_child(coeff*bi);
    }
    //std::cout << a->to_string() << std::endl;
    
    clock_t t1 = clock();

    auto model = pyqubo::compile(c, 5);

    clock_t t2 = clock();
    const double expression_time = static_cast<double>(t1 - t0) / CLOCKS_PER_SEC * 1000.0;
    const double compile_time = static_cast<double>(t2 - t1) / CLOCKS_PER_SEC * 1000.0;
    printf("express time: %f, compile time %f\n", expression_time, compile_time);
    //auto qubo = model.to_qubo();
}


int main(int argc, char* argv[]){
    if(argc > 1){
        int n = atoi(argv[1]);
        printf("hello world\n");
        test_express(n);
    }

    test_poly2();
    return 0;
}