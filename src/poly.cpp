#include <poly.h>
#include <string.h>
#include <compiled_qubo.h>
#include "reduce_order.cpp"

using namespace std;
using QuboIndex = pair<uint32_t, uint32_t>;

namespace poly {
    
    namespace{
        Poly* mul_mp_sp(Poly* mp, Mono* sp) {
            Terms* terms = mp->terms;
            Terms* new_terms = new Terms();
            Prod prod_sp = sp->prod;
            auto coeff_sp = sp->coeff;

            for(auto it = terms->begin(); it != terms->end(); it++){
                Prod prod_mp = it->first;
                auto p = Prod();
                prod_mp = prod_mp.merge(prod_sp);
                auto coeff_mp = it->second;

                auto result = new_terms->find(prod_mp);
                if (result != new_terms->end()) {
                    //new_terms->at(prod_mp) = new_terms->at(prod_mp)->add(coeff_mp->mul(coeff_sp));
                    //new_terms->insert(TermsPair{prod_mp, new_terms->at(prod_mp)->add(coeff_mp->mul(coeff_sp))});
                    result->second = new_terms->at(prod_mp)->add(coeff_mp->mul(coeff_sp));
                } else {
                    //new_terms->at(prod_mp) = coeff_mp->mul(coeff_sp);
                    new_terms->insert(TermsPair{prod_mp, coeff_mp->mul(coeff_sp)});
                }
            }
            Poly* new_poly = new Poly(new_terms);
            return new_poly;
        }

        Poly* mul_mp_mp(Poly* left, Poly* right) {
            Terms* left_terms = left->terms;
            Terms* right_terms = right->terms;
            Terms* new_terms = new Terms();
            for(Terms::iterator it_left = left_terms->begin(); it_left != left_terms->end(); it_left++){
                for(Terms::iterator it_right = right_terms->begin(); it_right != right_terms->end(); it_right++){
                    
                    // 文字列の掛け算
                    Prod prod_left = it_left->first;
                    Prod prod_right = it_right->first;
                    prod_left = prod_left.merge(prod_right);

                    // 係数の掛け算
                    auto coeff_left = it_left->second;
                    auto coeff_right = it_right->second;
                    
                    auto result = new_terms->find(prod_left);
                    if(result != new_terms->end()){
                        //new_terms->at(prod_left) = new_terms->at(prod_left)->add(coeff_left->mul(coeff_right));
                        //new_terms->insert(TermsPair{prod_left, new_terms->at(prod_left)->add(coeff_left->mul(coeff_right))});
                        result->second = new_terms->at(prod_left)->add(coeff_left->mul(coeff_right));
                    }else{
                        //new_terms->at(prod_left) = coeff_left->mul(coeff_right);
                        new_terms->insert(TermsPair{prod_left, coeff_left->mul(coeff_right)});
                    }
                }
            }
            delete left;
            delete right;
            return new Poly(new_terms);
        }

        PolyBase* mul_sp_sp(Mono* left, Mono* right){
            Prod new_prod = left->prod.merge(right->prod);
            auto new_coeff = left->coeff->mul(right->coeff);
            Mono* sp = new Mono(new_prod, new_coeff);
            return sp;
        }
    }

    PolyBase* mul(PolyBase* left, PolyBase* right){
        //printf("poly::mul-1\n");
        //printf("left %s\n", left->to_string().c_str());
        //printf("right %s\n", right->to_string().c_str());
        PolyType left_type = left->get_poly_type();
        PolyType right_type = right->get_poly_type();
        if(left_type == PolyType::MONO && right_type == PolyType::MONO){
            //printf("poly::mul-2\n");
            return mul_sp_sp((Mono*)left, (Mono*)right);
        }else if((left_type == PolyType::MONO && right_type == PolyType::POLY)
            || (left_type == PolyType::POLY && right_type == PolyType::MONO)){
            //printf("poly::mul-3\n");
            Poly* mp;
            Mono* sp;
            if(left_type == PolyType::MONO && right_type == PolyType::POLY){
                mp = (Poly*)right;
                sp = (Mono*)left;
            }else{
                mp = (Poly*)left;
                sp = (Mono*)right;
            }
            return mul_mp_sp(mp, sp);
        }else if(left_type == PolyType::POLY && right_type == PolyType::POLY){
            //printf("poly::mul-4\n");
            return mul_mp_mp((Poly*)left, (Poly*)right);
        }else{

        }
    }

    void merge_poly(Poly* org_poly, PolyBase* poly){
        //cout << "merge_poly -0" << org_poly->to_string() << endl;

        Terms* terms = org_poly->terms;
        if(poly->get_poly_type() == PolyType::MONO){
            Mono* sp = (Mono*)poly;
            const Prod& prod = sp->prod;

            auto result = terms->find(prod);
            if(result != (terms->end())){
                //terms->at(prod) = terms->at(prod)->add(sp->get_coeff());
                //cout << "merge_poly -1" << terms->at(prod)->to_string() << endl;
                //cout << "merge_poly -2" << sp->get_coeff()->to_string() << endl;
                //terms->insert(TermsPair{prod, terms->at(prod)->add(sp->get_coeff())});
                result->second = terms->at(prod)->add(sp->get_coeff());
                //cout << "merge_poly -3" << terms->at(prod)->to_string() << endl;
            }else{
                //terms->at(prod) = sp->get_coeff();
                //cout << "merge_poly -4" << prod.to_string() << endl;
                terms->insert(TermsPair{prod, sp->get_coeff()});
                //cout << "merge_poly -4.5" << terms->at(prod)->to_string() << endl;
            }
        }else{
            Poly* mp = (Poly*)poly;
            Terms* adding_terms = mp->get_terms();
            for(Terms::iterator it = adding_terms->begin(); it != adding_terms->end(); it++){
                const Prod& prod = it->first;
                auto coeff = it->second;

                //cout << "merge_poly -6" << prod.to_string() << endl;
                //cout << "merge_poly -7" << coeff->to_string() << endl;

                auto result = terms->find(prod);
                if(result != (terms->end())){
                    //terms->at(prod) = terms->at(prod)->add(coeff);
                    //terms->insert(TermsPair{prod, added});
                    result->second = terms->at(prod)->add(coeff);
                }else{
                    //terms->at(prod) = coeff;
                    //cout << "merge_poly -9" << prod.to_string() << endl;
                    terms->insert(TermsPair{prod, coeff});
                }
                //cout << "merge_poly -10" << terms->at(prod)->to_string() << endl;
            }
        }
    }
}

CompiledQubo* PolyBase::compile_coeff(){
    clock_t time0 = clock();
    CompiledTerms compiled_terms;
    Poly* mp = this->to_multiple_poly();
    clock_t time1 = clock();
    printf("compile_coeff %lf[ms]\n", static_cast<double>(time1-time0) / CLOCKS_PER_SEC * 1000.0);
    for(auto it = mp->terms->begin(); it != mp->terms->end(); it++){
        PHPolyBase* compiled_coeff = it->second->expand();
        Prod prod = it->first;
        auto p = std::make_pair(prod, compiled_coeff);
        compiled_terms.push_back(p);
    }
    clock_t time2 = clock();
    printf("compile_coeff 1 %lf[ms]\n", static_cast<double>(time2-time1) / CLOCKS_PER_SEC * 1000.0);
    auto cq = new CompiledQubo(compiled_terms);
    clock_t time3 = clock();
    printf("compile_coeff 2 %lf[ms]\n", static_cast<double>(time3-time2) / CLOCKS_PER_SEC * 1000.0);
    return cq;
}

Poly* PolyBase::make_quadratic(Encoder* encoder, CoeffPtr strength){
    Poly* mp = this->to_multiple_poly();
    reduce_order::make_quadratic(mp, encoder, strength);
    return mp;
}
