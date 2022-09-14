#include <algorithm>
#include <iostream>
#include <map>
#include <vector>
#include <time.h>
#include <vartypes.hpp>
#include <functional>

#include "abstract_syntax_tree.hpp"
#include "expand.hpp"
#include "compiler.hpp"
#include "poly.hpp"
#include "product.hpp"
#include "variables.hpp"


std::shared_ptr<const pyqubo::expression> create_binary(std::string s){
    return std::make_shared<const pyqubo::binary_variable>(s);
}

std::shared_ptr<const pyqubo::expression> create_numeric(double a){
    return std::make_shared<const pyqubo::numeric_literal>(a);
}

namespace pyqubo {

void test_poly1(){
    auto variables = pyqubo::variables();
    int index1 = variables.index("x_1");
    int index2 = variables.index("x_1");
    auto p1 = new pyqubo::product({index1});
    auto p2 = new pyqubo::product({index2});
    auto sp1 = pyqubo::poly(create_numeric(2), p1);
    auto sp2 = pyqubo::poly(create_numeric(3), p2);
    auto sp3 = sp1 + sp2;

    const product cp1 = *p1;
    const product cp2 = *p2;
    //auto h = std::hash<product>()(cp1);
    std::cout << "p1: " << std::to_string(std::hash<product>()(cp1)) << ", p2: " << std::to_string(std::hash<product>()(cp2)) << std::endl;
    if(cp1 == cp2){
        std::cout << "p1==p2" << std::endl;
    }else{
        std::cout << "p1!=p2" << std::endl;
    }
    std::cout << sp3.to_string() << std::endl;
    
}

void test_poly2(){
    auto sp1 = pyqubo::poly(create_numeric(2), new pyqubo::product({1}));
    auto sp2 = pyqubo::poly(create_numeric(3), new pyqubo::product({2}));
    auto sp3 = pyqubo::poly(create_numeric(4), new pyqubo::product({3}));
    auto sp0 = pyqubo::poly();
    
    auto sp4 = sp1 * sp2;
    auto sp5 = sp1 + sp2;
    auto sp6 = sp1 + sp3;
    auto sp7 = sp5 * sp6;
    
    std::cout << sp3.to_string() << std::endl;
    std::cout << sp4.to_string() << std::endl;
    std::cout << sp7.to_string() << std::endl;

    auto sp8 = sp7 + sp5;
    std::cout << sp8.to_string() << std::endl;

    auto sp9 = sp0 + sp8;
    std::cout << sp9.to_string() << std::endl;
}

void test_poly3(int n){
    auto variables = pyqubo::variables();
    clock_t t0 = clock();
    auto sp0 = pyqubo::poly();
    for(int i=0; i < n; i++){
        for(int j=0; j < n; j++){
            for(int k=0; k < n; k++){
                int index1 = variables.index("xxx_" + std::to_string(i) + "_" + std::to_string(j));
                int index2 = variables.index("xxx_" + std::to_string(j) + "_" + std::to_string(k));
                auto sp1 = pyqubo::poly(create_numeric(2), new pyqubo::product({index1}));
                auto sp2 = pyqubo::poly(create_numeric(2), new pyqubo::product({index2}));
                auto sp3 = sp1 * sp2;
                sp0 = sp0 + sp3;
            }
        }
    }
    std::cout << sp0.to_string() << std::endl;
    printf("size: %zu\n", sp0.size());
    clock_t t1 = clock();
    const double expression_time = static_cast<double>(t1 - t0) / CLOCKS_PER_SEC * 1000.0;
    printf("time %f\n", expression_time);
}


void test_express(int n){
    clock_t t0 = clock();
    auto a = create_binary("a");
    auto b = create_binary("b");
    std::shared_ptr<const pyqubo::add_operator> c = std::make_shared<const pyqubo::add_operator>(a, b);

    for(int i=0; i < n; i++){
        for(int j=0; j < n; j++){
            for(int k=0; k < n; k++){
                auto bi = create_binary("xxx_" + std::to_string(i) + "_" + std::to_string(j));
                auto bj = create_binary("xxx_" + std::to_string(j) + "_" + std::to_string(k));
                auto coeff = std::make_shared<const pyqubo::numeric_literal>(2);
                auto p = coeff*bi*bj;
                c = std::make_shared<const pyqubo::add_operator>(c, p);
                //c->add_child(coeff*bi);
            }
        }
    }
    //std::cout << c->to_string() << std::endl;
    std::cout << "express done\n";
    clock_t t1 = clock();

    auto model = pyqubo::compile(c, create_numeric(5));
    std::cout << "compile done\n";

    clock_t t2 = clock();
    const double expression_time = static_cast<double>(t1 - t0) / CLOCKS_PER_SEC * 1000.0;
    const double compile_time = static_cast<double>(t2 - t1) / CLOCKS_PER_SEC * 1000.0;
    printf("express time: %f, compile time %f\n", expression_time, compile_time);
    const auto [qubo, offset] = model.to_qubo_string({});
    std::cout << "size:" << qubo.size() << "\n"; 
    for(const auto& [key, value]: qubo){
        //std::cout << std::get<0>(key) << "," << std::get<1>(key) << "," << value << std::endl;
    }
}

void test_express2(int n){
    clock_t t0 = clock();
    
    for(int i=0; i < n; i++){
        auto a = create_binary("a");
        pyqubo::compile(a, create_numeric(5));
    }
    //std::cout << a->to_string() << std::endl;
    
    clock_t t1 = clock();

    clock_t t2 = clock();
    const double expression_time = static_cast<double>(t1 - t0) / CLOCKS_PER_SEC * 1000.0;
    const double compile_time = static_cast<double>(t2 - t1) / CLOCKS_PER_SEC * 1000.0;
    printf("express time: %f, compile time %f\n", expression_time, compile_time);
    //auto qubo = model.to_qubo();
}

void test_express3(){
    
    auto a = create_binary("a");
    auto b = create_binary("b");
    auto c = create_binary("c");

    auto H = a * b * c;
    auto m = pyqubo::compile(H, create_numeric(5));
    //std::cout << ->to_string() << std::endl;
    auto qubo = m.to_qubo_string({});
}

void test_express4(){
    
    auto a = create_binary("a");
    auto b = create_binary("b");
    auto c = create_binary("c");
    auto n2 = create_numeric(2);
    auto n1 = create_numeric(-1);
    auto cc = (a + b + n1);
    auto subh_var = std::make_shared<const pyqubo::sub_hamiltonian>(a + n2 * b, "my_subh");
    auto with_p = std::make_shared<const pyqubo::with_penalty>(subh_var, cc * cc, "my_with_penalty");

    auto H = subh_var + create_numeric(-3);
    auto m = pyqubo::compile(H, create_numeric(5));
    //std::cout << ->to_string() << std::endl;
    auto qubo = m.to_qubo_string({});
}

}

int main(int argc, char* argv[]){
    if(argc > 1){
        int n = atoi(argv[1]);
        printf("hello world\n");
        pyqubo::test_express(n);
    }

    //pyqubo::test_poly1();
    //pyqubo::test_poly2();
    //pyqubo::test_express3();
    pyqubo::test_express4();

    return 0;
}
