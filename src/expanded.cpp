#include <expanded.h>
#include <poly.h>
#include <compiled_sub_h.h>


namespace expanded{
    
    template<class T>
    void merge_linked_list(LinkedList<T>*& main_first, LinkedList<T>*& main_last,
        LinkedList<T>*& append_first, LinkedList<T>*& append_last){
        if(append_first==nullptr) return;
        if(main_first != nullptr){
            main_last->next = append_first;
            main_last = append_last;
        }else{
            main_first = append_first;
            main_last = append_last;
        } 
    }

    void merge_info(Expanded* main, Expanded* append){
        merge_linked_list(main->first_sub_hs, main->last_sub_hs, append->first_sub_hs, append->last_sub_hs);
        merge_linked_list(main->first_penalties, main->last_penalties, append->first_penalties, append->last_penalties);
    }

    Expanded* mul(Expanded* left_exp, Expanded* right_exp){
        //printf("expanded::mul -0\n");
        PolyBase* new_poly = poly::mul(left_exp->poly, right_exp->poly);
        //printf("expanded::mul -1\n");
        auto new_expand = new Expanded(new_poly);
        merge_info(new_expand, left_exp);
        merge_info(new_expand, right_exp);
        return new_expand;
    }

    Expanded* add(Expanded* main, Expanded* append){
        //printf("expanded::add\n");
        if(main->poly->get_poly_type()==PolyType::POLY){
            //printf("expanded::add2\n");
            poly::merge_poly((Poly*)(main->poly), append->poly);
        }else{
            //printf("expanded::add3\n");
            //cout << string("add3") << main->poly->to_string() << endl;
            main->poly = main->poly->to_multiple_poly();
            poly::merge_poly((Poly*)(main->poly), append->poly);
        }
        //cout << string("expanded::add poly") << main->poly->to_string() << endl;
        merge_info(main, append);
        return main;
    }
}