#include <gtest/gtest.h>
#include <express.h>
#include <prod.h>
#include <poly.h>
#include <model.h>
#include <coeffprod.h>
#include <placeholderpoly.h>
#include <coeff.h>
#include <expanded.h>

#include <binary_quadratic_model.hpp>
#include <vartypes.hpp>
#include <hash.hpp>

#include <unordered_map>
#include <utility>
#include <vector>
#include <cstdint>
#include <string>
#include <iostream>
#include <tuple>

using namespace std;

TEST(PROD, EQUALITY){
    Prod const_prod_1 = Prod();
    Prod const_prod_2 = Prod();
    Prod linear_prod_1 = Prod::create(1);
    Prod linear_prod_2 = Prod::create(1);
    Prod linear_prod_3 = Prod::create(2);
    Prod quad_prod_1 = Prod::create(1, 2);
    Prod quad_prod_2 = Prod::create(1, 2);
    Prod quad_prod_3 = Prod::create(2, 3);
    Prod c = Prod::create(1);
    EXPECT_EQ(const_prod_1, const_prod_2);
    EXPECT_EQ(linear_prod_1, linear_prod_2);
    EXPECT_NE(linear_prod_1, linear_prod_3);
    EXPECT_NE(const_prod_1, linear_prod_1);
    EXPECT_NE(const_prod_1, quad_prod_1);
    EXPECT_TRUE(std::ProdEqual()(quad_prod_1, quad_prod_2));
    EXPECT_NE(quad_prod_1, quad_prod_3);
    EXPECT_NE(std::ProdHash()(quad_prod_1), std::ProdHash()(quad_prod_3));
}

TEST(EXPRESS, COMPILE){
    BasePtr a(new Binary("a"));
    BasePtr b(new Binary("b"));
    BasePtr d(new Num(2.0));
    BasePtr e(new Placeholder("e"));

    typedef unordered_map<int, int> Map;
    typedef pair<int, int> MapPair;
    Map* m = new Map();
    m->insert(MapPair{1, 2});
    cout << to_string(m->at(1)) << endl;

    Encoder encoder = Encoder();
    auto a_b = a->add(b)->add(d);
    auto a_b_2 = a_b->mul(a_b);    
    auto a_b_2_e = a_b_2->mul(e);
    auto expanded = a_b_2_e->expand(encoder);
    auto mp = expanded->poly->to_multiple_poly();

    auto expected = new Poly();
    // original terms
    CoeffPtr coeff_e = make_shared<CoeffPlaceholder>("e");
    expected->add_term(Prod::create(1), coeff_e->mul(5.0));
    expected->add_term(Prod::create(0, 1), coeff_e->mul(2.0));
    expected->add_term(Prod::create(0), coeff_e->mul(5.0));
    expected->add_term(Prod(), coeff_e->mul(4.0));
    EXPECT_TRUE(mp->equal_to(expected));

    //compile
    map<std::string, double> feed_dict{{"e", 2.0}};
    auto model = a_b_2_e->compile();
    auto bqm = model.to_bqm_with_index(feed_dict);
    Linear<uint32_t> expected_linear{{1, 10.0}, {0, 10.0}};
    Quadratic<uint32_t> expected_quadratic{
        {std::make_pair(0, 1), 4.0},
    };
    EXPECT_EQ(bqm.get_linear(), expected_linear);
    EXPECT_EQ(bqm.get_quadratic(), expected_quadratic);
    EXPECT_EQ(bqm.get_offset(), 8.0);
}

TEST(EXPRESS, COMPILE2){
    BasePtr a(new Binary("a"));
    BasePtr b(new Binary("b"));
    BasePtr c(new Binary("c"));
    auto H = a->add(b);
    auto H2 = b->add(c);
    auto C1 = make_shared<SubH>(H, "const_1");
    auto C2 = make_shared<SubH>(H2, "const_2");
    auto H3 = C1->add(C2);
    Encoder encoder = Encoder();
    Expanded* expand = H3->expand(encoder);
    cout << expand->to_string() << "\n";
    auto model = H3->compile(1.0);
    cout << model.to_string() << "\n";
    vector<Sample<string>> samples = {
        {{"a", 1}, {"b", 1}, {"c", 0}}
    };
    auto dec_samples = model.decode_samples(samples, Vartype::BINARY);
    DecodedSolution sol = dec_samples[0];
    ASSERT_EQ(sol.subh_values["const_1"], 2.0);
    ASSERT_EQ(sol.subh_values["const_2"], 1.0);
    ASSERT_EQ(sol.energy, 3.0);
}

TEST(EXPRESS, COMPILE3){
    
    BasePtr a(new Binary("a"));
    BasePtr b(new Binary("b"));
    class MyWithPenalty: public WithPenalty{
    public:
        MyWithPenalty(){
            this->hamiltonian = make_shared<Binary>("a");
            this->penalty = make_shared<Binary>("b");
        }
    };
    auto p = make_shared<MyWithPenalty>();
    auto model = p->compile(1.0);
    cout << model.to_string() << "\n";
    auto qubo = model.to_qubo();
    auto quadratic = std::get<0>(qubo);
    Quadratic<string> expected_quadratic{
        {std::make_pair("a", "a"), 1.0},
        {std::make_pair("b", "b"), 1.0}
    };
    ASSERT_EQ(quadratic, expected_quadratic);
}

TEST(EXPRESS, MAKE_QUADRATIC){
    BasePtr a(new Binary("a"));
    BasePtr b(new Binary("b"));
    BasePtr c(new Binary("c"));
    BasePtr d(new Binary("d"));
    BasePtr e(new Placeholder("e"));
    auto abc = a->mul(b)->mul(c);
    auto bcd = b->mul(c)->mul(d);
    Encoder encoder = Encoder();
    auto H = abc->add(bcd);
    auto expanded = H->expand(encoder);
    double strength = 2.0;
    CoeffPtr strength_coeff = make_shared<CoeffNum>(strength);
    Poly* quad_poly = expanded->poly->make_quadratic(encoder, strength_coeff);
    cout << "quad_poly" << quad_poly->to_string() << " \n";

    auto expected = new Poly();
    // original terms
    expected->add_term(Prod::create(3, 4), 1.0);
    expected->add_term(Prod::create(0, 4), 1.0);
    // contraint terms
    expected->add_term(Prod::create(1, 4), -2.0 * strength);
    expected->add_term(Prod::create(2, 4), -2.0 * strength);
    expected->add_term(Prod::create(4), 3.0 * strength);
    expected->add_term(Prod::create(1, 2), strength);
    EXPECT_TRUE(quad_poly->equal_to(expected));

    // check to_bqm_with_index()
    auto model = H->compile();
    map<std::string, double> feed_dict{{"e", 2.0}};
    auto bqm = model.to_bqm_with_index(feed_dict);
    Linear<uint32_t> expected_linear{{0, 0.0}, {1, 0.0}, {2, 0.0}, {3, 0.0}, {4, 6.0}};
    Quadratic<uint32_t> expected_quadratic{
        {std::make_pair(0, 4), 1.0}, {std::make_pair(3, 4), 1.0}, {std::make_pair(2, 4), -4.0},
        {std::make_pair(1, 2), 2.0}, {std::make_pair(1, 4), -4.0},
    };
    EXPECT_EQ(bqm.get_linear(), expected_linear);
    EXPECT_EQ(bqm.get_quadratic(), expected_quadratic);
    EXPECT_EQ(bqm.get_offset(), 0.0);
    
    // check to_bqm()
    model.to_bqm(feed_dict);
}

TEST(COEFF_POLY, EQUALITY){
    CoeffProd a = CoeffProd("x", 1);
    CoeffProd b = CoeffProd("y", 2);
    CoeffProd c = CoeffProd("x", 2);
    CoeffProd d = CoeffProd("x", 3);
    auto abc = a.mul(b).mul(c);
    auto bd = d.mul(b);
    EXPECT_EQ(abc, bd);
    EXPECT_NE(a, b);
    
    // c, d = constant
    CoeffProd e = CoeffProd();
    CoeffProd f = CoeffProd();
    EXPECT_EQ(e, f);
    
    auto poly1 = new PHMono(a, 2.0); // 2 x
    auto poly2 = new PHMono(bd, 3.0); // 3 x^3 y^2
    auto poly3 = new PHMono(abc, 3.0); // 3 x^3 y^2
    auto poly4 = new PHMono(abc, 2.0); // 2 x^3 y^2
    EXPECT_TRUE(poly2->equal_to(poly3));
    EXPECT_FALSE(poly3->equal_to(poly4));
    auto poly1_2 = (PHPoly*)PlPolyOperation::add(poly1, poly2); // poly1 = 2 x + 3 x^3 y^2

    auto poly5 = new PHPoly(); // poly5 = 2 x + 3 x^3 y^2
    poly5->add(a, 1.0);
    poly5->add(a, 1.0);
    poly5->add(abc, 3.0);
    EXPECT_TRUE(poly1_2->equal_to(poly5));

    poly1_2->add(e, 3.0);
    auto poly6 = PlPolyOperation::mul(poly1_2, poly5);
    auto poly7 = new PHPoly(); // = 4 x^2 + 12 x^4 y^2 + 9 x^6 y^4 + 6x + 9x^3y^2
    poly7->add(a.mul(a), 4.0);
    poly7->add(a.mul(abc), 12.0);
    poly7->add(abc.mul(abc), 9.0);
    poly7->add(a, 6.0);
    poly7->add(abc, 9.0);
    EXPECT_TRUE(poly6->equal_to(poly7));
    
    // test evaluation
    map<string, double> feed_dict;
    feed_dict["x"] = 3.0;
    feed_dict["y"] = 4.0;
    EXPECT_EQ(a.evaluate(feed_dict), 3.0);
    EXPECT_EQ(b.evaluate(feed_dict), 16.0);
    EXPECT_EQ(abc.evaluate(feed_dict), 432.0);
}

TEST(COEFF, EXPAND){
    CoeffPtr a = make_shared<CoeffNum>(2.0);
    CoeffPtr b = make_shared<CoeffNum>(3.0);
    CoeffPtr ab = a->mul(b);
    CoeffPtr expect = make_shared<CoeffNum>(6.0);
    EXPECT_TRUE(ab->equal_to(expect));

    CoeffPtr x = make_shared<CoeffPlaceholder>("x");
    CoeffPtr ax_b = x->mul(a)->add(b);

    auto expand_ax_b = ax_b->expand();
    auto expect_poly1 = new PHPoly();
    CoeffProd x_prod = CoeffProd("x", 1);
    expect_poly1->add(x_prod, 2.0);
    expect_poly1->add(CoeffProd(), 3.0);
    EXPECT_TRUE(expand_ax_b->equal_to(expect_poly1));

    CoeffPtr ax_b_2 = ax_b->mul(ax_b);
    auto expand_ax_b_2 = ax_b_2->expand();
    auto expect_poly2 = new PHPoly(); 
    expect_poly2->add(x_prod, 12.0);
    expect_poly2->add(x_prod.mul(x_prod), 4.0);
    expect_poly2->add(CoeffProd(), 9.0);
    EXPECT_TRUE(expand_ax_b_2->equal_to(expect_poly2));
}
