#include <iostream>
#include <express.h>
#include <poly.h>
#include <time.h>
#include <model.h>
#include <expanded.h>

using namespace::std;

BasePtr Base::add(BasePtr other){
    BasePtr this_ptr = shared_from_this();
    AddPtr new_base(new Add(this_ptr, other));
    return new_base;
}

BasePtr Base::add(double other){
    shared_ptr<Num> num(new Num(other));
    BasePtr this_ptr = shared_from_this();
    if(other == 0.0){
        return this_ptr;
    }else{
        AddPtr new_base(new Add(this_ptr, num));
        return new_base;
    }
}

BasePtr Base::mul(BasePtr other){
    BasePtr this_ptr = shared_from_this();
    shared_ptr<Mul> new_base(new Mul(this_ptr, other));
    return new_base;
}

BasePtr Base::mul(double other){
    BasePtr this_ptr = shared_from_this();
    if(other == 1.0){
        return this_ptr;
    }else if(other == 0.0){
        shared_ptr<Num> num(new Num(0.0));
        return num;
    }else{
        shared_ptr<Num> num(new Num(other));
        shared_ptr<Mul> new_base(new Mul(this_ptr, num));
        return new_base;
    }
}

BasePtr Base::div(double other){
    if(other == 0.0){
        throw std::runtime_error("zero devide error");
    }else{
        return Base::mul(1.0 / other);
    }
}

BasePtr Base::pow(int other){
    BasePtr result = shared_from_this();
    BasePtr this_ptr = shared_from_this(); 
    for(int i=0; i < other-1; i++){
        result = result->mul(this_ptr);
    }
    return result;
}

// we don't use Pow class since the advantage was not confirmed in benchmark.
/*BasePtr Base::pow(int exponent){
    BasePtr this_ptr = shared_from_this(); 
    shared_ptr<Pow> new_pow(new Pow(this_ptr, exponent));
    return new_pow;
}*/

BasePtr Base::neg(){
    return Base::mul(-1.0);
}

BasePtr Base::sub(BasePtr other){
    BasePtr this_ptr = shared_from_this();
    AddPtr new_base(new Add(this_ptr, other->mul(-1)));
    return new_base;
}

BasePtr Base::sub(double other){
    return Base::add(-other);
}

BasePtr Base::rsub(double other){
    BasePtr this_ptr = shared_from_this();
    shared_ptr<Num> num(new Num(other));
    AddPtr new_base(new Add(this_ptr->mul(-1), num));
    return new_base;
}

Model Base::compile(double strength){
    CoeffPtr strength_coeff = make_shared<CoeffNum>(strength);
    return Base::compile(strength_coeff);
}

Model Base::compile(string placeholder_label){
    CoeffPtr strength_coeff = make_shared<CoeffPlaceholder>(placeholder_label);
    return Base::compile(strength_coeff);
}

Model Base::compile(CoeffPtr strength){
    //clock_t start = clock();
    Encoder encoder = Encoder();
    Expanded* expanded = this->expand(encoder);
    //clock_t end = clock();
    //printf("compile0 %lf[ms]\n", static_cast<double>(end-start) / CLOCKS_PER_SEC * 1000.0);
    CompiledQubo* compiled_qubo = expanded->get_compiled_qubo(encoder, strength);
    //std::cout << compiled_qubo->to_string() << endl;
    //clock_t end2 = clock();
    //printf("compile1 %lf[ms]\n", static_cast<double>(end2-end) / CLOCKS_PER_SEC * 1000.0);
    
    auto model = Model(*compiled_qubo, encoder, expanded);
    
    expanded->delete_linked_list();
    delete expanded;
    return model;
}

BasePtr Add::add(BasePtr other){
    BasePtr this_ptr = shared_from_this();
    AddPtr new_base(new Add(static_pointer_cast<Add>(this_ptr), other));
    return new_base;
}

Expanded* Add::expand(Encoder& encoder){
    int i = 0;
    AddList* next_node = this->node;
    Expanded* new_expanded = next_node->value->expand(encoder);
    next_node = next_node->next;
    while(next_node != nullptr){
        Expanded* expanded_tmp = next_node->value->expand(encoder);
        expanded::add(new_expanded, expanded_tmp);
        next_node = next_node->next;
        i++;
    }
    return new_expanded;
};

Expanded* Mul::expand(Encoder& encoder){
    Expanded* left_expanded = this->left->expand(encoder);
    Expanded* right_expanded = this->right->expand(encoder);
    Expanded* new_expanded = expanded::mul(left_expanded, right_expanded);
    return new_expanded;
};

Expanded* Binary::expand(Encoder& encoder){
    BasePtr this_ptr = shared_from_this();
    Mono* poly = new Mono(static_pointer_cast<Binary>(this_ptr), encoder);
    auto new_expanded = new Expanded(poly);
    return new_expanded;
};

Expanded* Spin::expand(Encoder& encoder){
    BasePtr this_ptr = shared_from_this();
    Poly* poly = new Poly(static_pointer_cast<Spin>(this_ptr), encoder);
    auto new_expanded = new Expanded(poly);
    return new_expanded;
};

Expanded* Num::expand(Encoder& encoder){
    BasePtr this_ptr = shared_from_this();
    Mono* poly = new Mono(static_pointer_cast<Num>(this_ptr));
    return new Expanded(poly);
};

Expanded* Placeholder::expand(Encoder& encoder){
    BasePtr this_ptr = shared_from_this();
    Mono* poly = new Mono(static_pointer_cast<Placeholder>(this_ptr));
    return new Expanded(poly);
};

Expanded* Pow::expand(Encoder& encoder){
    Expanded* expanded = this->hamiltonian->expand(encoder);
    auto new_expanded = expanded::pow(expanded, this->exponent);
    return new_expanded;
};

Expanded* WithPenalty::expand(Encoder& encoder){
    Expanded* hamiltonian_expand = this->hamiltonian->expand(encoder);
    Expanded* penalty_expanded = penalty->expand(encoder);
    hamiltonian_expand->add_penalty(this->label, penalty_expanded);
    return hamiltonian_expand;
};

Expanded* UserDefinedExpress::expand(Encoder& encoder){
    Expanded* hamiltonian_expand = this->hamiltonian->expand(encoder);
    return hamiltonian_expand;
};

Expanded* SubH::expand(Encoder& encoder){
    Expanded* hamiltonian_exp = this->hamiltonian->expand(encoder);
    hamiltonian_exp->add_sub_h(this->label, hamiltonian_exp->poly->get_terms(), nullptr);
    return hamiltonian_exp;
};

Expanded* Constraint::expand(Encoder& encoder){
    Expanded* hamiltonian_exp = this->hamiltonian->expand(encoder);
    hamiltonian_exp->add_sub_h(this->label, hamiltonian_exp->poly->get_terms(), this->condition);
    return hamiltonian_exp;
};