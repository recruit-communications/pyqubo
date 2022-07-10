#include <algorithm>
#include <iostream>
#include <map>
#include <vector>
#include <time.h>
#include <vartypes.hpp>

#include "abstract_syntax_tree.hpp"
#include "compiler.hpp"
#include "compiler2.hpp"


std::shared_ptr<const pyqubo::expression> create_binary(std::string s){
    return std::make_shared<const pyqubo::binary_variable>(s);
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
    int n = atoi(argv[1]);
    printf("hello world\n");
    test_express(n);
    return 0;
}