#include <placeholderpoly.h>
#include <memory>
#include <utility>

namespace PlPolyOperation {
    
    PHPolyBase* mul(PHPolyBase* left, PHPolyBase* right){
        PHPolyType left_type = left->get_type();
        PHPolyType right_type = right->get_type();
        
        if(left_type == PHPolyType::MONO && right_type == PHPolyType::MONO){

            PHMono* left_casted(static_cast<PHMono*>(left));
            PHMono* right_casted(static_cast<PHMono*>(right));
            CoeffProd new_prod = left_casted->coeff_prod.mul(right_casted->coeff_prod);
            double new_coeff = left_casted->coeff * right_casted->coeff;
            delete left_casted;
            delete right_casted;
            return new PHMono(new_prod, new_coeff);

        }else if((left_type == PHPolyType::POLY && right_type == PHPolyType::MONO)
            || (left_type == PHPolyType::MONO && right_type == PHPolyType::POLY)){

            PHPoly* multi_poly;
            PHMono* mono_poly;
            if(left_type == PHPolyType::POLY && right_type == PHPolyType::MONO){
                multi_poly = static_cast<PHPoly*>(left);
                mono_poly = static_cast<PHMono*>(right);
            }else{
                multi_poly = static_cast<PHPoly*>(right);
                mono_poly = static_cast<PHMono*>(left);
            }
            PHPoly* new_poly = new PHPoly();
            for(auto it_this = multi_poly->terms.begin(); it_this != multi_poly->terms.end(); it_this++){
                CoeffProd this_prod = it_this->first;
                CoeffProd new_prod = this_prod.mul(mono_poly->coeff_prod);
                double new_coeff = it_this->second * mono_poly->coeff;
                new_poly->add(new_prod, new_coeff);
            }
            delete multi_poly;
            delete mono_poly;
            return new_poly;

        }else if(left_type == PHPolyType::POLY && right_type == PHPolyType::POLY){

            PHPoly* left_casted(static_cast<PHPoly*>(left));
            PHPoly* right_casted(static_cast<PHPoly*>(right));
            PHPoly* new_poly = new PHPoly();
            for(auto it_this = left_casted->terms.begin(); it_this != left_casted->terms.end(); it_this++){
                for(auto it_other = right_casted->terms.begin(); it_other != right_casted->terms.end(); it_other++){
                    CoeffProd this_prod = it_this->first;
                    CoeffProd other_prod = it_other->first;
                    CoeffProd new_prod = this_prod.mul(other_prod);
                    double new_coeff = it_this->second * it_other->second;
                    new_poly->add(new_prod, new_coeff);
                }
            }
            delete left_casted;
            delete right_casted;
            return new_poly;

        }else{
            throw std::runtime_error("invalid poly_type.");
        }
    }

    PHPolyBase* add(PHPolyBase* left, PHPolyBase* right){
        PHPolyType left_type = left->get_type();
        PHPolyType right_type = right->get_type();

        if(left_type == PHPolyType::MONO && right_type == PHPolyType::MONO){
            PHMono* left_casted(static_cast<PHMono*>(left));
            PHMono* right_casted(static_cast<PHMono*>(right));
            auto new_poly = new PHPoly();
            new_poly->add(right_casted->coeff_prod, right_casted->coeff);
            new_poly->add(left_casted->coeff_prod, left_casted->coeff);
            delete left_casted;
            delete right_casted;
            return new_poly;

        }else if((left_type == PHPolyType::POLY && right_type == PHPolyType::MONO)
            || (left_type == PHPolyType::MONO && right_type == PHPolyType::POLY)){
            PHPoly* multi_poly;
            PHMono* mono_poly;
            if(left_type == PHPolyType::POLY && right_type == PHPolyType::MONO){
                multi_poly = static_cast<PHPoly*>(left);
                mono_poly = static_cast<PHMono*>(right);
            }else{
                multi_poly = static_cast<PHPoly*>(right);
                mono_poly = static_cast<PHMono*>(left);
            }
            multi_poly->add(mono_poly->coeff_prod, mono_poly->coeff);
            delete mono_poly;
            return multi_poly;

        }else if(left_type == PHPolyType::POLY && right_type == PHPolyType::POLY){
            PHPoly* left_casted(static_cast<PHPoly*>(left));
            PHPoly* right_casted(static_cast<PHPoly*>(right));
            for(auto it = left_casted->terms.begin(); it != left_casted->terms.end(); it++){
                right_casted->add(it->first, it->second);
            }
            delete left_casted;
            return right_casted;
        }else{
            throw std::runtime_error("invalid poly_type.");
        }
    }
};