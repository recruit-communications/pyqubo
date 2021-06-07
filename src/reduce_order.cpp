#include <poly.h>
#include <time.h>

using QuboIndex = pair<uint32_t, uint32_t>;

namespace reduce_order{

    namespace {

        void add_term(Terms* terms, Prod prod, CoeffPtr coeff){
            auto result = terms->find(prod);
            if(result == terms->end()){
                terms->insert(TermsPair{prod, coeff});
            }else{
                result->second = coeff->add(result->second);
            }
        }

        bool has_higher_degree(Poly* mp){
            bool found = false;
            for(auto it = mp->terms->begin(); it != mp->terms->end(); it++){
                if(it->first.length > 2){
                    found = true;
                    break;
                }
            }
            return found;
        };

        QuboIndex find_most_common(Poly* mp){
            map<QuboIndex, uint32_t> counter;
            for(auto it = mp->terms->begin(); it != mp->terms->end(); it++){
                int degree = it->first.length;
                if(degree > 2){
                    // calc all combinations
                    for(int i=0; i < degree-1; i++){
                        for(int j=i+1; j < degree; j++){
                            Prod prod = it->first;
                            uint32_t index_i = prod.get_var(i);
                            uint32_t index_j = prod.get_var(j);
                            QuboIndex p;
                            // sort the order of index so that the key is identical
                            if(index_i < index_j){
                                p = make_pair(index_i, index_j);
                            }else{
                                p = make_pair(index_j, index_i);
                            }
                            auto result = counter.find(p);
                            if(result == counter.end()){
                                counter[p] = 1;
                            }else{
                                counter[p] = result->second + 1;
                            }
                        }
                    }
                }
            }
            // choose the most appeared index
            QuboIndex most_common;
            int best_count = 0;
            for(auto it = counter.begin(); it != counter.end(); it++){
                if(best_count < it->second){
                    best_count = it->second;
                    most_common = it->first;
                }
            }
            return most_common;
        }

        void replace_variable(Poly* mp, QuboIndex index_pair, int new_variable){
            for(auto it = mp->terms->begin(); it != mp->terms->end(); it++){
                Prod prod = it->first;
                CoeffPtr coeff = it->second;
                bool first_in = false, second_in = false;
                for(int i=0; i < it->first.length; i++){
                    if(prod.get_var(i) == index_pair.first) first_in = true;
                    if(prod.get_var(i) == index_pair.second) second_in = true;
                }
                if(first_in && second_in){
                    uint32_t* indices = new uint32_t[it->first.length+1];
                    int index = 0;
                    for(int i=0; i < it->first.length; i++){
                        if(prod.get_var(i) != index_pair.first && prod.get_var(i) != index_pair.second){
                            // increment the index when creating prod.indices
                            indices[index++] = prod.get_var(i) + 1;
                        }
                    }
                    mp->terms->erase(it);
                    // increment the index when creating prod.indices
                    indices[index++] = new_variable + 1;
                    Prod new_prod = Prod(indices, index);
                    mp->terms->insert(TermsPair{new_prod, coeff});
                    it = mp->terms->begin();
                }
            }
        }

        uint32_t create_new_var(QuboIndex index_pair, Encoder& encoder){
            string new_label = std::to_string(index_pair.first) + string("*") + std::to_string(index_pair.second);
            return encoder.encode(new_label);
        }

        void add_and_constraint(Poly* mp, QuboIndex index_pair, uint32_t new_var, CoeffPtr strength){
            add_term(mp->terms, Prod::create(new_var), strength->mul(3.0));
            add_term(mp->terms, Prod::create(index_pair.first, new_var), strength->mul(-2.0));
            add_term(mp->terms, Prod::create(index_pair.second, new_var), strength->mul(-2.0));
            add_term(mp->terms, Prod::create(index_pair.first, index_pair.second), strength);
        }
    }

    void make_quadratic(Poly* mp, Encoder& encoder, CoeffPtr strength){
        //clock_t time0 = clock();
        while(has_higher_degree(mp)){
            QuboIndex index_pair = find_most_common(mp);
            uint32_t new_var = create_new_var(index_pair, encoder);
            replace_variable(mp, index_pair, new_var);
            add_and_constraint(mp, index_pair, new_var, strength);
        }
        //clock_t time3 = clock();
        //printf("make_quadratic2 %lf[ms]\n", static_cast<double>(time3-time0) / CLOCKS_PER_SEC * 1000.0);
    }
}
